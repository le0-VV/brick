from __future__ import annotations

import io
import json
import sqlite3
import unittest
import urllib.error
from contextlib import closing
from unittest import mock

from test_phase4_index_search import index, make_repo, memory, write_memory


class EmbeddingGemmaProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = make_repo(self)
        self.config_path = self.repo / index.LOCAL_CONFIG_RELATIVE_PATH
        self.config_path.parent.mkdir(parents=True)
        self.paths = [
            write_memory(
                self.repo,
                memory_id=memory_id,
                title=title,
                body=body,
                tags=["retrieval"],
            )
            for memory_id, title, body in (
                (
                    "01JX3Y1Y8H6TR4Y3Q38K1W9P2A",
                    "Alpha: API Configuration",
                    "## Keep Case\nUse `API_KEY` and [Docs](https://example.test/API).\n",
                ),
                (
                    "01JX3Y2D8S6Q7M4K2B9P0V1W3T",
                    "Bravo: 中文 Notes",
                    "Preserve **Markdown**, punctuation, and 中文.\n",
                ),
            )
        ]
        self.configure()

    def configure(self, **overrides: object) -> None:
        settings = {
            "url": "http://embedding.example/v1",
            "model": "embeddinggemma-2",
            "profile": "embeddinggemma-2",
            **overrides,
        }
        self.config_path.write_text(json.dumps({"embedding": settings}), encoding="utf-8")

    @staticmethod
    def response(vector: list[float] | None = None) -> mock.MagicMock:
        payload = {"data": [{"index": 0, "embedding": vector or [1.0] + [0.0] * 767}]}
        response = mock.MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps(payload).encode()
        return response

    def test_profile_config_defaults_and_rejects_unknown_values(self) -> None:
        self.assertEqual(index.configured_embedding(self.repo, {}).profile, "embeddinggemma-2")
        self.configure(profile="generic")
        self.assertEqual(index.configured_embedding(self.repo, {}).profile, "generic")
        settings = json.loads(self.config_path.read_text())
        del settings["embedding"]["profile"]
        self.config_path.write_text(json.dumps(settings))
        self.assertEqual(index.configured_embedding(self.repo, {}).profile, "generic")
        for invalid in ("other", "", None, 1):
            with self.subTest(profile=invalid):
                self.configure(profile=invalid)
                with self.assertRaises(index.BrickIndexError) as raised:
                    index.configured_embedding(self.repo, {})
                self.assertEqual(raised.exception.code, "invalid_local_config")

    def test_rebuild_and_query_preserve_text_and_use_task_prefixes(self) -> None:
        documents = [memory.load_memory(path) for path in self.paths]
        inputs = []

        def respond(request, *, timeout):
            self.assertEqual(timeout, 30)
            self.assertEqual(request.full_url, "http://embedding.example/v1/embeddings")
            payload = json.loads(request.data)
            self.assertEqual(payload["model"], "embeddinggemma-2")
            self.assertEqual(len(payload["input"]), 1)
            inputs.extend(payload["input"])
            return self.response([float(len(inputs))] + [0.0] * 767)

        with mock.patch.object(index.urllib.request, "urlopen", side_effect=respond):
            rebuilt = index.rebuild_index(self.repo, env={}).to_dict(self.repo)
            result = index.search_index(self.repo, "API_KEY 中文: Which **Setting**?", env={})

        self.assertEqual(
            inputs,
            [f"title: {doc.frontmatter['title']} | text: {doc.body}" for doc in documents]
            + ["task: search result | query: API_KEY 中文: Which **Setting**?"],
        )
        self.assertEqual(result["retrieval"]["mode"], "hybrid")
        self.assertEqual(rebuilt["index"]["embedding_profile"], "embeddinggemma-2")
        self.assertEqual(rebuilt["index"]["embedding_profile_version"], 1)
        self.assertEqual(result["index"]["embedding_profile"], "embeddinggemma-2")
        with closing(sqlite3.connect(index.index_path(self.repo))) as connection, connection:
            vectors = connection.execute(
                "SELECT memories.title, embeddings.vector_json FROM memories JOIN embeddings "
                "ON memories.id = embeddings.memory_id ORDER BY memories.path"
            ).fetchall()
        self.assertEqual([json.loads(row[1])[0] for row in vectors], [1.0, 2.0])

    def test_generic_profile_keeps_batched_normalised_document_input(self) -> None:
        self.configure(profile="generic")
        expected = [
            index.memory_row(self.repo, memory.load_memory(path))["search_text"]
            for path in self.paths
        ]
        with mock.patch.object(index, "request_embeddings", return_value=[[1.0], [2.0]]) as request:
            index.rebuild_index(self.repo, env={})
        self.assertEqual(request.call_count, 1)
        self.assertEqual(request.call_args.args[1], expected)
        with closing(sqlite3.connect(index.index_path(self.repo))) as connection, connection:
            connection.execute("DELETE FROM metadata WHERE key LIKE 'embedding_profile%'")
        with mock.patch.object(index, "request_embeddings", return_value=[[1.0]]) as request:
            result = index.search_index(self.repo, "API_KEY", env={})
        self.assertEqual(result["retrieval"]["mode"], "hybrid")
        self.assertEqual(request.call_args.args[1], ["API_KEY"])

    def test_profile_model_and_version_mismatch_use_visible_keyword_fallback(self) -> None:
        with mock.patch.object(index.urllib.request, "urlopen", return_value=self.response()):
            index.rebuild_index(self.repo, env={})
        mutations = (
            ("embedding_profile", "generic", "embedding_profile_mismatch"),
            ("embedding_profile", None, "embedding_profile_mismatch"),
            ("embedding_profile_version", "2", "embedding_profile_mismatch"),
            ("embedding_profile_version", "unknown", "embedding_profile_mismatch"),
            ("embedding_profile_version", None, "embedding_profile_mismatch"),
            ("embedding_model", "another-model", "embedding_model_mismatch"),
        )
        for key, value, reason in mutations:
            with self.subTest(key=key, value=value):
                with closing(sqlite3.connect(index.index_path(self.repo))) as connection, connection:
                    original = connection.execute("SELECT value FROM metadata WHERE key = ?", (key,)).fetchone()[0]
                    if value is None:
                        connection.execute("DELETE FROM metadata WHERE key = ?", (key,))
                    else:
                        connection.execute("UPDATE metadata SET value = ? WHERE key = ?", (value, key))
                with mock.patch.object(index, "request_embeddings") as request:
                    result = index.search_index(self.repo, "API_KEY", env={})
                request.assert_not_called()
                self.assertEqual(result["retrieval"]["mode"], "keyword")
                self.assertEqual(result["retrieval"]["semantic"]["reason"], reason)
                self.assertEqual(result["retrieval"]["semantic"]["action"], "run brick rebuild")
                self.assertTrue(result["results"])
                with closing(sqlite3.connect(index.index_path(self.repo))) as connection, connection:
                    connection.execute("INSERT OR REPLACE INTO metadata VALUES (?, ?)", (key, original))

    def test_response_order_and_strict_vector_validation(self) -> None:
        first = [1.0] + [0.0] * 767
        second = [0.0, 1.0] + [0.0] * 766
        response = {"data": [{"index": 1, "embedding": second}, {"index": 0, "embedding": first}]}
        self.assertEqual(
            index.parse_embedding_response(response, 2, profile="embeddinggemma-2"),
            [first, second],
        )
        invalid_vectors = [[], [1.0] * 767, [1.0] * 769] + [
            [value] + [0.0] * 767
            for value in (True, "1", None, float("nan"), float("inf"), -float("inf"), 10**400)
        ]
        invalid_payloads = [None, {}, {"data": []}, {"data": [None]}]
        invalid_payloads += [{"data": [{"index": 0, "embedding": vector}]} for vector in invalid_vectors]
        invalid_payloads += [
            {"data": [{"index": invalid, "embedding": first}]}
            for invalid in (-1, 1, False, "0", None)
        ]
        invalid_payloads.append({"data": [{"embedding": first}]})
        for payload in invalid_payloads:
            with self.subTest(payload=str(payload)[:100]):
                with self.assertRaises(index.EmbeddingError) as raised:
                    index.parse_embedding_response(payload, 1, profile="embeddinggemma-2")
                self.assertEqual(raised.exception.reason, "embedding_response_invalid")
        with self.assertRaises(index.EmbeddingError):
            index.parse_embedding_response(
                {"data": [{"index": 0, "embedding": first}] * 2},
                2,
                profile="embeddinggemma-2",
            )

    def test_failed_mid_rebuild_preserves_previous_index(self) -> None:
        with mock.patch.object(index.urllib.request, "urlopen", return_value=self.response()):
            index.rebuild_index(self.repo, env={})
        old_index = index.index_path(self.repo).read_bytes()
        oversized = urllib.error.HTTPError(
            "http://embedding.example/v1/embeddings", 400, "Bad Request", {},
            io.BytesIO(b'{"error":"input exceeds 2048 tokens"}'),
        )
        self.addCleanup(oversized.close)
        for failure in (oversized, self.response([1.0, 2.0])):
            with self.subTest(failure=failure):
                with (
                    mock.patch.object(index.urllib.request, "urlopen", side_effect=[self.response(), failure]) as request,
                    self.assertRaises(index.BrickIndexError) as raised,
                ):
                    index.rebuild_index(self.repo, env={})
                self.assertEqual(request.call_count, 2)
                self.assertIn(raised.exception.code, {"embedding_request_failed", "embedding_response_invalid"})
                if failure is oversized:
                    self.assertIn("2048", str(raised.exception))
                self.assertEqual(index.index_path(self.repo).read_bytes(), old_index)

    def test_invalid_query_vector_reports_keyword_fallback(self) -> None:
        with mock.patch.object(index.urllib.request, "urlopen", return_value=self.response()):
            index.rebuild_index(self.repo, env={})
        with mock.patch.object(index.urllib.request, "urlopen", return_value=self.response([1.0])):
            result = index.search_index(self.repo, "API_KEY", env={})
        self.assertEqual(result["retrieval"]["mode"], "keyword")
        self.assertEqual(result["retrieval"]["semantic"]["reason"], "embedding_response_invalid")
        self.assertIn("768", result["retrieval"]["semantic"]["message"])


if __name__ == "__main__":
    unittest.main()
