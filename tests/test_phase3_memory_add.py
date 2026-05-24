from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


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


def base_candidate(**overrides: object) -> dict[str, object]:
    candidate: dict[str, object] = {
        "id": "01JX3Y1Y8H6TR4Y3Q38K1W9P2A",
        "title": "Hybrid retrieval decision",
        "type": "decision",
        "tags": ["retrieval", "architecture"],
        "body": "Use hybrid retrieval for memory search.",
        "source": {"kind": "conversation", "ref": "test"},
        "evidence": [{"kind": "quote", "text": "Hybrid retrieval lgtm."}],
    }
    candidate.update(overrides)
    return candidate


def run_memory_add(repo: Path, payload: object | str) -> subprocess.CompletedProcess[str]:
    input_text = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(
        [sys.executable, str(ROOT / ".agents/brick/bin/brick"), "memory", "add"],
        cwd=repo,
        input=input_text,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def run_memory_validate(repo: Path, path: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / ".agents/brick/bin/brick"), "memory", "validate", path],
        cwd=repo,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class Phase3MemoryAddTests(unittest.TestCase):
    def test_memory_add_writes_valid_markdown_file(self) -> None:
        repo = make_repo(self)

        completed = run_memory_add(repo, base_candidate())

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["id"], "01JX3Y1Y8H6TR4Y3Q38K1W9P2A")
        self.assertEqual(
            payload["path"],
            ".agents/memory/decision/01JX3Y1Y8H6TR4Y3Q38K1W9P2A-hybrid-retrieval-decision.md",
        )
        written = repo / payload["path"]
        self.assertTrue(written.is_file())

        validation = run_memory_validate(repo, payload["path"])
        validation_payload = json.loads(validation.stdout)
        self.assertEqual(validation.returncode, 0)
        self.assertEqual(validation_payload["status"], "ok")

        document = memory.load_memory(written)
        self.assertEqual(document.frontmatter["title"], "Hybrid retrieval decision")
        self.assertTrue(document.frontmatter["content_hash"].startswith("sha256:"))

    def test_memory_add_rejects_non_json(self) -> None:
        repo = make_repo(self)

        completed = run_memory_add(repo, "not json")

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(payload["status"], "invalid")
        self.assertEqual(payload["reason"], "invalid_json")

    def test_memory_add_rejects_unknown_top_level_fields(self) -> None:
        repo = make_repo(self)

        completed = run_memory_add(repo, base_candidate(topic="not allowed"))

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(payload["status"], "invalid")
        self.assertIn("unknown_field", {issue["code"] for issue in payload["issues"]})
        self.assertFalse((repo / ".agents/memory").exists())

    def test_memory_add_blocks_unsafe_candidate(self) -> None:
        repo = make_repo(self)

        completed = run_memory_add(
            repo,
            base_candidate(body="Use api_key = sk_test_1234567890abcdef for examples."),
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["actions"], ["redact", "confirm_public", "reject"])
        self.assertFalse((repo / ".agents/memory").exists())

    def test_memory_add_writes_command_fields(self) -> None:
        repo = make_repo(self)

        completed = run_memory_add(
            repo,
            base_candidate(
                id="01JX3Y2D8S6Q7M4K2B9P0V1W3T",
                title="Run tests",
                type="command",
                tags=["tests"],
                body="Run the Python unit tests before committing.",
                fields={
                    "command": "python3 -m unittest discover -s tests",
                    "cwd": ".",
                    "when_to_use": "Before committing Python changes.",
                    "expected_output": "Tests pass.",
                    "failure_notes": "Fix failures before continuing.",
                },
            ),
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0)
        document = memory.load_memory(repo / payload["path"])
        self.assertEqual(document.frontmatter["command"], "python3 -m unittest discover -s tests")
        self.assertEqual(document.frontmatter["cwd"], ".")

    def test_memory_add_writes_routine_fields(self) -> None:
        repo = make_repo(self)

        completed = run_memory_add(
            repo,
            base_candidate(
                id="01JX3Y2D8S6Q7M4K2B9P0V1W3T",
                title="Release routine",
                type="routine",
                tags=["release"],
                body="Follow the release routine before tagging.",
                fields={
                    "steps": ["Run tests.", "Update roadmap."],
                    "prerequisites": ["Clean worktree."],
                    "verify": "Release checks pass.",
                },
            ),
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0)
        document = memory.load_memory(repo / payload["path"])
        self.assertEqual(document.frontmatter["steps"], ["Run tests.", "Update roadmap."])
        self.assertEqual(document.frontmatter["prerequisites"], ["Clean worktree."])
        self.assertEqual(document.frontmatter["verify"], "Release checks pass.")

    def test_memory_add_rejects_fields_for_plain_decision(self) -> None:
        repo = make_repo(self)

        completed = run_memory_add(repo, base_candidate(fields={"command": "nope"}))

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(payload["status"], "invalid")
        self.assertIn("fields.command", {issue.get("field") for issue in payload["issues"]})

    def test_memory_add_supports_all_allowed_statuses(self) -> None:
        repo = make_repo(self)
        statuses = ["active", "superseded", "tombstone", "redacted"]

        for index, status in enumerate(statuses):
            candidate = base_candidate(
                id=f"01JX3Y1Y8H6TR4Y3Q38K1W9P2{index}",
                title=f"{status} memory",
                status=status,
            )

            completed = run_memory_add(repo, candidate)
            payload = json.loads(completed.stdout)
            self.assertEqual(completed.returncode, 0, payload)
            document = memory.load_memory(repo / payload["path"])
            self.assertEqual(document.frontmatter["status"], status)


if __name__ == "__main__":
    unittest.main()
