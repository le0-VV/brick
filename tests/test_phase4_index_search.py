from __future__ import annotations

import http.client
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / ".agents/brick/src"
sys.path.insert(0, str(SRC))

from brick import index
from brick import memory


def make_repo(test_case: unittest.TestCase) -> Path:
    temp_dir = tempfile.TemporaryDirectory()
    test_case.addCleanup(temp_dir.cleanup)
    repo = Path(temp_dir.name)
    subprocess.run(["git", "init"], cwd=repo, check=True, stdout=subprocess.PIPE)
    return repo


def write_memory(
    repo: Path,
    *,
    memory_id: str,
    title: str,
    body: str,
    tags: list[str],
    status: str = "active",
    memory_type: str = "decision",
    source: dict[str, Any] | None = None,
    evidence: list[Any] | None = None,
    hash_override: str | None = None,
) -> Path:
    frontmatter: dict[str, Any] = {
        "id": memory_id,
        "title": title,
        "type": memory_type,
        "status": status,
        "tags": tags,
        "created_at": "2026-05-24T00:00:00Z",
        "updated_at": "2026-05-24T00:00:00Z",
        "source": source or {"kind": "test", "ref": title},
        "evidence": evidence or [{"kind": "test", "text": f"{title} fixture"}],
        "supersedes": [],
        "related": [],
    }
    frontmatter["content_hash"] = hash_override or memory.compute_content_hash(frontmatter, body)
    target = repo / ".agents/memory" / memory_type / f"{memory_id}-{memory.slugify(title)}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(memory.render_memory_text(frontmatter, body), encoding="utf-8")
    return target


def run_rebuild(
    repo: Path,
    *args: str,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    return subprocess.run(
        [sys.executable, str(ROOT / ".agents/brick/bin/brick"), "rebuild", "--json", *args],
        cwd=repo,
        env=run_env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def run_search(
    repo: Path,
    query: str,
    *args: str,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    return subprocess.run(
        [sys.executable, str(ROOT / ".agents/brick/bin/brick"), "memory", "search", query, *args],
        cwd=repo,
        env=run_env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def fake_embedding_vector(text: str) -> list[float]:
    lowered = text.lower()
    if "alpha" in lowered or "semantic-only" in lowered:
        return [1.0, 0.0, 0.0]
    if "bravo" in lowered:
        return [0.0, 1.0, 0.0]
    return [0.0, 0.0, 1.0]


class Phase4IndexSearchTests(unittest.TestCase):
    def test_rebuild_creates_sqlite_index_and_json_contract(self) -> None:
        repo = make_repo(self)
        write_memory(
            repo,
            memory_id="01JX3Y1Y8H6TR4Y3Q38K1W9P2A",
            title="Hybrid retrieval decision",
            tags=["retrieval", "architecture"],
            body="Use keyword fallback search before semantic retrieval is configured.",
        )
        write_memory(
            repo,
            memory_id="01JX3Y2D8S6Q7M4K2B9P0V1W3T",
            title="Run unit tests",
            tags=["tests"],
            body="Run Python unittest discovery before committing CLI changes.",
            memory_type="command",
        )

        completed = run_rebuild(repo)

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["index"]["path"], ".agents/brick/index/brick.sqlite3")
        self.assertEqual(payload["index"]["schema_version"], 2)
        self.assertEqual(payload["index"]["memory_count"], 2)
        self.assertEqual(payload["checked"], 2)

        database = repo / payload["index"]["path"]
        self.assertTrue(database.is_file())
        with sqlite3.connect(database) as connection:
            count = connection.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        self.assertEqual(count, 2)

    def test_rebuild_fails_on_invalid_memory_without_writing_index(self) -> None:
        repo = make_repo(self)
        write_memory(
            repo,
            memory_id="01JX3Y1Y8H6TR4Y3Q38K1W9P2A",
            title="Bad hash memory",
            tags=["validation"],
            body="This memory has a bad content hash.",
            hash_override="sha256:" + "0" * 64,
        )

        completed = run_rebuild(repo)

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(payload["status"], "invalid")
        self.assertEqual(payload["reason"], "memory_validation_failed")
        self.assertFalse((repo / ".agents/brick/index/brick.sqlite3").exists())

    def test_search_requires_built_index(self) -> None:
        repo = make_repo(self)

        completed = run_search(repo, "retrieval")

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["reason"], "index_missing")
        self.assertEqual(payload["action"], "run brick rebuild")

    def test_search_ranks_keyword_results_and_reports_semantic_missing(self) -> None:
        repo = make_repo(self)
        write_memory(
            repo,
            memory_id="01JX3Y1Y8H6TR4Y3Q38K1W9P2A",
            title="Hybrid retrieval decision",
            tags=["retrieval", "architecture"],
            body="Use keyword fallback search before semantic retrieval is configured.",
            evidence=[{"kind": "quote", "text": "Hybrid retrieval lgtm."}],
        )
        write_memory(
            repo,
            memory_id="01JX3Y2D8S6Q7M4K2B9P0V1W3T",
            title="Run unit tests",
            tags=["tests"],
            body="Run Python unittest discovery before committing CLI changes.",
            memory_type="command",
        )
        rebuild = run_rebuild(repo)
        self.assertEqual(rebuild.returncode, 0, rebuild.stdout + rebuild.stderr)

        completed = run_search(repo, "hybrid retrieval")

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["retrieval"]["mode"], "keyword")
        self.assertFalse(payload["retrieval"]["semantic"]["available"])
        self.assertEqual(
            payload["retrieval"]["semantic"]["reason"],
            "BRICK_EMBEDDING_URL_not_configured",
        )
        self.assertEqual(payload["results"][0]["id"], "01JX3Y1Y8H6TR4Y3Q38K1W9P2A")
        first = payload["results"][0]
        self.assertEqual(first["confidence"], "high")
        self.assertEqual(
            first["source_path"],
            ".agents/memory/decision/01JX3Y1Y8H6TR4Y3Q38K1W9P2A-hybrid-retrieval-decision.md",
        )
        self.assertEqual(first["source"]["kind"], "test")
        self.assertEqual(first["matched_terms"], ["hybrid", "retrieval"])
        self.assertIn("summary", first)
        self.assertIn("content_hash", first)
        self.assertIn("evidence", first)
        self.assertIn("full_text_path", first)

    def test_search_filters_superseded_by_default_and_can_include_it(self) -> None:
        repo = make_repo(self)
        write_memory(
            repo,
            memory_id="01JX3Y1Y8H6TR4Y3Q38K1W9P2A",
            title="Legacy retrieval decision",
            tags=["legacy", "retrieval"],
            body="Legacy retrieval used a previous design.",
            status="superseded",
        )
        write_memory(
            repo,
            memory_id="01JX3Y2D8S6Q7M4K2B9P0V1W3T",
            title="Current search decision",
            tags=["search"],
            body="Current search uses the active design.",
        )
        rebuild = run_rebuild(repo)
        self.assertEqual(rebuild.returncode, 0, rebuild.stdout + rebuild.stderr)

        default_search = run_search(repo, "legacy")
        default_payload = json.loads(default_search.stdout)
        self.assertEqual(default_search.returncode, 0)
        self.assertEqual(default_payload["results"], [])

        included_search = run_search(repo, "legacy", "--include-superseded")
        included_payload = json.loads(included_search.stdout)
        self.assertEqual(included_search.returncode, 0)
        self.assertEqual(included_payload["results"][0]["status"], "superseded")

    def test_rebuild_and_search_use_openai_compatible_embedding_endpoint(self) -> None:
        repo = make_repo(self)
        write_memory(
            repo,
            memory_id="01JX3Y1Y8H6TR4Y3Q38K1W9P2A",
            title="Alpha vector memory",
            tags=["vectors"],
            body="Alpha content is retrievable through semantic search.",
        )
        write_memory(
            repo,
            memory_id="01JX3Y2D8S6Q7M4K2B9P0V1W3T",
            title="Bravo vector memory",
            tags=["vectors"],
            body="Bravo content points in a different embedding direction.",
        )

        env = {
            "BRICK_EMBEDDING_URL": "http://embedding.example/v1",
            "BRICK_EMBEDDING_MODEL": "fake-embedding-model",
            "BRICK_EMBEDDING_API_KEY": "test-key",
        }
        embedding_calls: list[tuple[index.EmbeddingConfig, list[str]]] = []

        def fake_request_embeddings(
            config: index.EmbeddingConfig,
            inputs: list[str],
        ) -> list[list[float]]:
            embedding_calls.append((config, inputs))
            return [fake_embedding_vector(text) for text in inputs]

        with mock.patch.object(index, "request_embeddings", side_effect=fake_request_embeddings):
            rebuild_result = index.rebuild_index(repo, env=env)
            rebuild_payload = rebuild_result.to_dict(repo)
            search_payload = index.search_index(repo, "semantic-only", env=env)

        self.assertEqual(rebuild_payload["index"]["schema_version"], 2)
        self.assertEqual(rebuild_payload["index"]["embedding_count"], 2)
        self.assertEqual(rebuild_payload["index"]["embedding_model"], "fake-embedding-model")
        self.assertEqual(rebuild_payload["index"]["embedding_dimensions"], 3)
        self.assertEqual(search_payload["retrieval"]["mode"], "hybrid")
        self.assertTrue(search_payload["retrieval"]["semantic"]["available"])
        self.assertEqual(search_payload["retrieval"]["semantic"]["model"], "fake-embedding-model")
        self.assertEqual(search_payload["results"][0]["id"], "01JX3Y1Y8H6TR4Y3Q38K1W9P2A")
        self.assertEqual(search_payload["results"][0]["keyword_score"], 0)
        self.assertEqual(search_payload["results"][0]["semantic_score"], 1.0)
        self.assertEqual(len(embedding_calls), 2)
        self.assertEqual(embedding_calls[0][0].endpoint_url, "http://embedding.example/v1/embeddings")
        self.assertEqual(embedding_calls[0][0].model, "fake-embedding-model")
        self.assertEqual(embedding_calls[0][0].api_key, "test-key")
        self.assertEqual(len(embedding_calls[0][1]), 2)
        self.assertEqual(embedding_calls[1][1], ["semantic-only"])

    def test_embedding_remote_disconnect_returns_embedding_error(self) -> None:
        config = index.EmbeddingConfig(
            endpoint_url="http://embedding.example/v1/embeddings",
            model="fake-embedding-model",
        )

        with (
            mock.patch.object(
                index.urllib.request,
                "urlopen",
                side_effect=http.client.RemoteDisconnected(
                    "Remote end closed connection without response"
                ),
            ),
            self.assertRaises(index.EmbeddingError) as raised,
        ):
            index.request_embeddings(config, ["hello"])

        self.assertEqual(raised.exception.reason, "embedding_request_failed")
        self.assertIn("Remote end closed connection", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
