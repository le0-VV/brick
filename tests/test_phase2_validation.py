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


VALID_ID = "01JX3Y1Y8H6TR4Y3Q38K1W9P2A"


def make_repo(test_case: unittest.TestCase) -> Path:
    temp_dir = tempfile.TemporaryDirectory()
    test_case.addCleanup(temp_dir.cleanup)
    repo = Path(temp_dir.name)
    subprocess.run(["git", "init"], cwd=repo, check=True, stdout=subprocess.PIPE)
    return repo


def write_memory_file(
    repo: Path,
    *,
    frontmatter_overrides: dict[str, Any] | None = None,
    body: str = "The project uses hybrid retrieval for memory search.\n",
    path: str = ".agents/memory/decision/01JX3Y1Y8H6TR4Y3Q38K1W9P2A-hybrid-retrieval.md",
    hash_override: str | None = None,
) -> Path:
    frontmatter: dict[str, Any] = {
        "id": VALID_ID,
        "title": "hybrid retrieval decision",
        "type": "decision",
        "status": "active",
        "tags": ["retrieval", "architecture"],
        "created_at": "2026-05-24T00:00:00Z",
        "updated_at": "2026-05-24T00:00:00Z",
        "source": {"kind": "conversation"},
        "evidence": ["User approved hybrid retrieval."],
        "supersedes": [],
        "related": [],
    }
    if frontmatter_overrides:
        for key, value in frontmatter_overrides.items():
            if value is None:
                frontmatter.pop(key, None)
            else:
                frontmatter[key] = value
    frontmatter["content_hash"] = hash_override or memory.compute_content_hash(frontmatter, body)

    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_memory(frontmatter, body), encoding="utf-8")
    return target


def render_memory(frontmatter: dict[str, Any], body: str) -> str:
    lines = ["---"]
    for key, value in frontmatter.items():
        append_yaml(lines, key, value, 0)
    lines.append("---")
    lines.append(body.rstrip())
    lines.append("")
    return "\n".join(lines)


def append_yaml(lines: list[str], key: str, value: Any, indent: int) -> None:
    prefix = " " * indent
    if isinstance(value, dict):
        lines.append(f"{prefix}{key}:")
        for child_key, child_value in value.items():
            append_yaml(lines, child_key, child_value, indent + 2)
    elif isinstance(value, list):
        if not value:
            lines.append(f"{prefix}{key}: []")
            return
        lines.append(f"{prefix}{key}:")
        for item in value:
            item_prefix = " " * (indent + 2)
            if isinstance(item, dict):
                lines.append(f"{item_prefix}-")
                for child_key, child_value in item.items():
                    append_yaml(lines, child_key, child_value, indent + 4)
            else:
                lines.append(f"{item_prefix}- {json.dumps(item)}")
    elif isinstance(value, bool):
        lines.append(f"{prefix}{key}: {'true' if value else 'false'}")
    else:
        lines.append(f"{prefix}{key}: {json.dumps(value)}")


def run_validate(repo: Path, path: Path | None = None) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(ROOT / ".agents/brick/bin/brick"), "memory", "validate"]
    if path is not None:
        command.append(str(path))
    return subprocess.run(
        command,
        cwd=repo,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class Phase2ValidationTests(unittest.TestCase):
    def test_valid_memory_passes_validation(self) -> None:
        repo = make_repo(self)
        path = write_memory_file(repo)

        completed = run_validate(repo, path)

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["checked"], 1)
        self.assertEqual(payload["results"][0]["status"], "ok")

    def test_missing_evidence_is_invalid(self) -> None:
        repo = make_repo(self)
        path = write_memory_file(repo, frontmatter_overrides={"evidence": []})

        completed = run_validate(repo, path)

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(payload["status"], "invalid")
        codes = {issue["code"] for issue in payload["results"][0]["issues"]}
        self.assertIn("missing_evidence", codes)

    def test_low_confidence_durable_memory_is_invalid(self) -> None:
        repo = make_repo(self)
        path = write_memory_file(repo, frontmatter_overrides={"confidence": "low"})

        completed = run_validate(repo, path)

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(payload["status"], "invalid")
        codes = {issue["code"] for issue in payload["results"][0]["issues"]}
        self.assertIn("unsupported_durable_memory", codes)

    def test_hash_mismatch_is_invalid_and_reports_expected_hash(self) -> None:
        repo = make_repo(self)
        path = write_memory_file(repo, hash_override="sha256:" + "0" * 64)

        completed = run_validate(repo, path)

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 1)
        result = payload["results"][0]
        self.assertEqual(result["status"], "invalid")
        self.assertTrue(result["expected_content_hash"].startswith("sha256:"))
        self.assertIn("content_hash_mismatch", {issue["code"] for issue in result["issues"]})

    def test_secret_detection_blocks_memory(self) -> None:
        repo = make_repo(self)
        path = write_memory_file(
            repo,
            body="Use api_key = sk_test_1234567890abcdef for this example.\n",
        )

        completed = run_validate(repo, path)

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(payload["status"], "blocked")
        issue = payload["results"][0]["issues"][0]
        self.assertEqual(issue["code"], "secret_detected")
        self.assertEqual(issue["text"], "[REDACTED]")

    def test_possible_pii_blocks_without_confirmation(self) -> None:
        repo = make_repo(self)
        path = write_memory_file(
            repo,
            body="The maintainer email is maintainer@example.com.\n",
        )

        completed = run_validate(repo, path)

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(payload["status"], "blocked")
        self.assertIn("possible_pii", {issue["code"] for issue in payload["results"][0]["issues"]})

    def test_confirm_public_allows_possible_pii(self) -> None:
        repo = make_repo(self)
        path = write_memory_file(
            repo,
            frontmatter_overrides={"confirm_public": True},
            body="The maintainer email is maintainer@example.com.\n",
        )

        completed = run_validate(repo, path)

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(payload["status"], "ok")

    def test_default_validation_allows_empty_memory_bank(self) -> None:
        repo = make_repo(self)

        completed = run_validate(repo)

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(payload, {"status": "ok", "checked": 0, "results": []})

    def test_generate_ulid_returns_valid_plain_ulid(self) -> None:
        generated = memory.generate_ulid(timestamp_ms=0)

        self.assertRegex(generated, memory.ULID_RE)
        self.assertEqual(len(generated), 26)


if __name__ == "__main__":
    unittest.main()
