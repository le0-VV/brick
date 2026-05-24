from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / ".agents/brick/src"
sys.path.insert(0, str(SRC))

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
    body: str,
    evidence: list[Any] | None = None,
) -> Path:
    memory_id = "01JX3Y1Y8H6TR4Y3Q38K1W9P2A"
    frontmatter: dict[str, Any] = {
        "id": memory_id,
        "title": "Redaction fixture",
        "type": "decision",
        "status": "active",
        "tags": ["safety"],
        "created_at": "2026-05-24T00:00:00Z",
        "updated_at": "2026-05-24T00:00:00Z",
        "source": {"kind": "test", "ref": "redaction"},
        "evidence": evidence or [{"kind": "test", "text": "Redaction fixture"}],
        "supersedes": [],
        "related": [],
    }
    frontmatter["content_hash"] = memory.compute_content_hash(frontmatter, body)
    path = repo / ".agents/memory/decision/01JX3Y1Y8H6TR4Y3Q38K1W9P2A-redaction-fixture.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(memory.render_memory_text(frontmatter, body), encoding="utf-8")
    return path


def run_redact(repo: Path, payload: object | str) -> subprocess.CompletedProcess[str]:
    input_text = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(
        [sys.executable, str(ROOT / ".agents/brick/bin/brick"), "memory", "redact"],
        cwd=repo,
        input=input_text,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def run_search(repo: Path, query: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / ".agents/brick/bin/brick"), "memory", "search", query],
        cwd=repo,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class Phase7RedactionTests(unittest.TestCase):
    def test_memory_redact_replaces_secret_marks_redacted_and_rebuilds_index(self) -> None:
        repo = make_repo(self)
        path = write_memory(
            repo,
            body="Use api_key = sk_test_1234567890abcdef for examples.\n",
        )

        completed = run_redact(
            repo,
            {
                "path": str(path.relative_to(repo)),
                "redactions": ["api_key = sk_test_1234567890abcdef"],
                "reason": "Removed leaked test credential.",
            },
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["index_rebuilt"])
        self.assertEqual(payload["replacement_count"], 1)
        self.assertTrue((repo / ".agents/brick/index/brick.sqlite3").is_file())

        document = memory.load_memory(path)
        self.assertEqual(document.frontmatter["status"], "redacted")
        self.assertIn(memory.REDACTION_REPLACEMENT, document.body)
        self.assertNotIn("sk_test_1234567890abcdef", document.raw_text)
        self.assertEqual(
            document.frontmatter["evidence"][-1],
            {"kind": "redaction", "text": "Removed leaked test credential."},
        )
        self.assertEqual(
            document.frontmatter["content_hash"],
            memory.compute_content_hash(document.frontmatter, document.body),
        )
        self.assertEqual(memory.validate_memory(document).status, "ok")

        search = run_search(repo, "examples")
        search_payload = json.loads(search.stdout)
        self.assertEqual(search.returncode, 0, search.stdout + search.stderr)
        self.assertEqual(search_payload["results"], [])

    def test_memory_redact_replaces_frontmatter_evidence_pii(self) -> None:
        repo = make_repo(self)
        path = write_memory(
            repo,
            body="The maintainer contact is recorded in evidence.\n",
            evidence=[{"kind": "test", "text": "Email maintainer@example.com for context."}],
        )

        completed = run_redact(
            repo,
            {
                "path": str(path.relative_to(repo)),
                "redactions": ["maintainer@example.com"],
                "reason": "Removed public contact from durable memory.",
                "rebuild": False,
            },
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertFalse(payload["index_rebuilt"])
        document = memory.load_memory(path)
        self.assertIn(memory.REDACTION_REPLACEMENT, document.frontmatter["evidence"][0]["text"])
        self.assertNotIn("maintainer@example.com", document.raw_text)
        self.assertEqual(memory.validate_memory(document).status, "ok")
        self.assertFalse((repo / ".agents/brick/index/brick.sqlite3").exists())

    def test_memory_redact_rejects_missing_target_without_writing(self) -> None:
        repo = make_repo(self)
        path = write_memory(repo, body="Safe memory body.\n")
        original = path.read_text(encoding="utf-8")

        completed = run_redact(
            repo,
            {
                "path": str(path.relative_to(repo)),
                "redactions": ["not present"],
                "reason": "Attempted redaction.",
                "rebuild": False,
            },
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(payload["status"], "invalid")
        self.assertEqual(payload["reason"], "redaction_text_not_found")
        self.assertEqual(path.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
