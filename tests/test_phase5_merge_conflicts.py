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

from brick import conflicts
from brick import memory


def make_repo(test_case: unittest.TestCase) -> Path:
    temp_dir = tempfile.TemporaryDirectory()
    test_case.addCleanup(temp_dir.cleanup)
    repo = Path(temp_dir.name)
    subprocess.run(["git", "init"], cwd=repo, check=True, stdout=subprocess.PIPE)
    return repo


def memory_text(
    *,
    memory_id: str = "01JX3Y1Y8H6TR4Y3Q38K1W9P2A",
    title: str,
    body: str,
    frontmatter_overrides: dict[str, Any] | None = None,
) -> str:
    frontmatter: dict[str, Any] = {
        "id": memory_id,
        "title": title,
        "type": "decision",
        "status": "active",
        "tags": ["merge"],
        "created_at": "2026-05-24T00:00:00Z",
        "updated_at": "2026-05-24T00:00:00Z",
        "source": {"kind": "test", "ref": title},
        "evidence": [{"kind": "test", "text": f"{title} fixture"}],
        "supersedes": [],
        "related": [],
    }
    if frontmatter_overrides:
        for key, value in frontmatter_overrides.items():
            if value is None:
                frontmatter.pop(key, None)
            else:
                frontmatter[key] = value
    frontmatter["content_hash"] = memory.compute_content_hash(frontmatter, body)
    return memory.render_memory_text(frontmatter, body)


def write_merge_files(repo: Path, base: str, ours: str, theirs: str) -> tuple[Path, Path, Path]:
    base_path = repo / "base.md"
    ours_path = repo / "ours.md"
    theirs_path = repo / "theirs.md"
    base_path.write_text(base, encoding="utf-8")
    ours_path.write_text(ours, encoding="utf-8")
    theirs_path.write_text(theirs, encoding="utf-8")
    return base_path, ours_path, theirs_path


def run_cli(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / ".agents/brick/bin/brick"), *args],
        cwd=repo,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class Phase5MergeConflictTests(unittest.TestCase):
    def test_conflicts_list_and_export_report_json(self) -> None:
        repo = make_repo(self)
        report = {
            "schema_version": 1,
            "id": "conflict-01JX3Y1Y8H6TR4Y3Q38K1W9P2A",
            "created_at": "2026-05-24T00:00:00Z",
            "kind": "memory_merge_conflict",
            "severity": "review_required",
            "merge": {"base_ref": "base", "ours_ref": "ours", "theirs_ref": "theirs"},
            "memories": [],
            "similarity": {"method": "not_evaluated", "score": None},
            "conflicts": [{"field": "file", "reason": "test"}],
            "appendable_unions": {"evidence": []},
            "proposed_resolution": None,
            "required_action": "human_review",
        }
        conflicts.write_conflict_report(repo, report)

        listed = run_cli(repo, "conflicts", "list")
        listed_payload = json.loads(listed.stdout)
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertEqual(listed_payload["status"], "ok")
        self.assertEqual(listed_payload["count"], 1)
        self.assertEqual(listed_payload["reports"][0]["id"], report["id"])

        exported = run_cli(repo, "conflicts", "export", report["id"])
        exported_payload = json.loads(exported.stdout)
        self.assertEqual(exported.returncode, 0, exported.stderr)
        self.assertEqual(exported_payload["status"], "ok")
        self.assertEqual(exported_payload["report"]["id"], report["id"])

    def test_merge_driver_uses_theirs_when_ours_is_unchanged_from_base(self) -> None:
        repo = make_repo(self)
        base_text = memory_text(title="Base memory", body="Base body.")
        theirs_text = memory_text(title="Base memory", body="Theirs changed body.")
        base, ours, theirs = write_merge_files(repo, base_text, base_text, theirs_text)

        completed = run_cli(
            repo,
            "merge-driver",
            str(base),
            str(ours),
            str(theirs),
            "7",
            ".agents/memory/decision/example.md",
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(ours.read_text(encoding="utf-8"), theirs_text)

    def test_merge_driver_keeps_ours_when_theirs_is_unchanged_from_base(self) -> None:
        repo = make_repo(self)
        base_text = memory_text(title="Base memory", body="Base body.")
        ours_text = memory_text(title="Base memory", body="Ours changed body.")
        base, ours, theirs = write_merge_files(repo, base_text, ours_text, base_text)

        completed = run_cli(
            repo,
            "merge-driver",
            str(base),
            str(ours),
            str(theirs),
            "7",
            ".agents/memory/decision/example.md",
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(ours.read_text(encoding="utf-8"), ours_text)

    def test_merge_driver_resolves_identical_outputs(self) -> None:
        repo = make_repo(self)
        base_text = memory_text(title="Base memory", body="Base body.")
        merged_text = memory_text(title="Base memory", body="Same changed body.")
        base, ours, theirs = write_merge_files(repo, base_text, merged_text, merged_text)

        completed = run_cli(
            repo,
            "merge-driver",
            str(base),
            str(ours),
            str(theirs),
            "7",
            ".agents/memory/decision/example.md",
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(ours.read_text(encoding="utf-8"), merged_text)

    def test_merge_driver_writes_conflict_report_for_manual_review(self) -> None:
        repo = make_repo(self)
        base_text = memory_text(title="Base memory", body="Base body.")
        ours_text = memory_text(title="Base memory", body="Ours changed body.")
        theirs_text = memory_text(title="Base memory", body="Theirs changed body.")
        base, ours, theirs = write_merge_files(repo, base_text, ours_text, theirs_text)

        completed = run_cli(
            repo,
            "merge-driver",
            str(base),
            str(ours),
            str(theirs),
            "7",
            ".agents/memory/decision/example.md",
        )

        self.assertEqual(completed.returncode, 1)
        self.assertIn("human review", completed.stderr)
        self.assertEqual(ours.read_text(encoding="utf-8"), ours_text)

        listed = run_cli(repo, "conflicts", "list")
        listed_payload = json.loads(listed.stdout)
        self.assertEqual(listed_payload["count"], 1)
        report_id = listed_payload["reports"][0]["id"]

        exported = run_cli(repo, "conflicts", "export", report_id)
        exported_payload = json.loads(exported.stdout)
        report = exported_payload["report"]
        self.assertEqual(report["required_action"], "human_review")
        self.assertEqual(report["kind"], "memory_merge_conflict")
        self.assertEqual(report["merge"]["path"], ".agents/memory/decision/example.md")
        self.assertEqual({entry["side"] for entry in report["memories"]}, {"base", "ours", "theirs"})

    def test_merge_driver_structurally_merges_one_sided_frontmatter_and_body_changes(self) -> None:
        repo = make_repo(self)
        base_text = memory_text(title="Base memory", body="Base body.")
        ours_text = memory_text(title="Ours title", body="Base body.")
        theirs_text = memory_text(title="Base memory", body="Theirs changed body.")
        base, ours, theirs = write_merge_files(repo, base_text, ours_text, theirs_text)

        completed = run_cli(
            repo,
            "merge-driver",
            str(base),
            str(ours),
            str(theirs),
            "7",
            ".agents/memory/decision/example.md",
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        merged = memory.load_memory(ours)
        self.assertEqual(merged.frontmatter["title"], "Ours title")
        self.assertEqual(memory.normalize_body(merged.body), "Theirs changed body.\n")
        self.assertEqual(
            merged.frontmatter["content_hash"],
            memory.compute_content_hash(merged.frontmatter, merged.body),
        )

    def test_merge_driver_unions_evidence_when_both_sides_append(self) -> None:
        repo = make_repo(self)
        base_evidence = [{"kind": "test", "text": "base evidence"}]
        ours_evidence = [
            {"kind": "test", "text": "base evidence"},
            {"kind": "test", "text": "ours evidence"},
        ]
        theirs_evidence = [
            {"kind": "test", "text": "base evidence"},
            {"kind": "test", "text": "theirs evidence"},
        ]
        base_text = memory_text(
            title="Base memory",
            body="Base body.",
            frontmatter_overrides={"evidence": base_evidence},
        )
        ours_text = memory_text(
            title="Base memory",
            body="Base body.",
            frontmatter_overrides={"evidence": ours_evidence},
        )
        theirs_text = memory_text(
            title="Base memory",
            body="Base body.",
            frontmatter_overrides={"evidence": theirs_evidence},
        )
        base, ours, theirs = write_merge_files(repo, base_text, ours_text, theirs_text)

        completed = run_cli(
            repo,
            "merge-driver",
            str(base),
            str(ours),
            str(theirs),
            "7",
            ".agents/memory/decision/example.md",
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        merged = memory.load_memory(ours)
        self.assertEqual(
            [item["text"] for item in merged.frontmatter["evidence"]],
            ["base evidence", "ours evidence", "theirs evidence"],
        )
        self.assertEqual(
            merged.frontmatter["content_hash"],
            memory.compute_content_hash(merged.frontmatter, merged.body),
        )

    def test_merge_driver_blocks_same_frontmatter_field_changed_on_both_sides(self) -> None:
        repo = make_repo(self)
        base_text = memory_text(title="Base memory", body="Base body.")
        ours_text = memory_text(title="Ours title", body="Base body.")
        theirs_text = memory_text(title="Theirs title", body="Base body.")
        base, ours, theirs = write_merge_files(repo, base_text, ours_text, theirs_text)

        completed = run_cli(
            repo,
            "merge-driver",
            str(base),
            str(ours),
            str(theirs),
            "7",
            ".agents/memory/decision/example.md",
        )

        self.assertEqual(completed.returncode, 1)
        listed = run_cli(repo, "conflicts", "list")
        report_id = json.loads(listed.stdout)["reports"][0]["id"]
        exported = run_cli(repo, "conflicts", "export", report_id)
        report = json.loads(exported.stdout)["report"]
        self.assertIn(
            {"field": "title", "reason": "structured_frontmatter_conflict"},
            report["conflicts"],
        )

    def test_merge_driver_reports_semantic_similarity_for_different_memory_ids(self) -> None:
        repo = make_repo(self)
        base_text = memory_text(title="Base memory", body="Base body.")
        ours_text = memory_text(
            memory_id="01JX3Y1Y8H6TR4Y3Q38K1W9P2B",
            title="Hybrid retrieval for memory search",
            body=(
                "Brick memory search should combine keyword ranking and semantic "
                "embedding retrieval so agents can find project context."
            ),
            frontmatter_overrides={
                "tags": ["retrieval", "search", "semantic"],
                "evidence": [{"kind": "test", "text": "hybrid retrieval evidence"}],
            },
        )
        theirs_text = memory_text(
            memory_id="01JX3Y1Y8H6TR4Y3Q38K1W9P2C",
            title="Hybrid search for project memory",
            body=(
                "Brick should combine keyword search with semantic embedding "
                "retrieval to give agents accurate project context."
            ),
            frontmatter_overrides={
                "tags": ["retrieval", "search", "semantic"],
                "evidence": [{"kind": "test", "text": "semantic search evidence"}],
            },
        )
        base, ours, theirs = write_merge_files(repo, base_text, ours_text, theirs_text)

        completed = run_cli(
            repo,
            "merge-driver",
            str(base),
            str(ours),
            str(theirs),
            "7",
            ".agents/memory/decision/example.md",
        )

        self.assertEqual(completed.returncode, 1)
        self.assertEqual(ours.read_text(encoding="utf-8"), ours_text)
        listed = run_cli(repo, "conflicts", "list")
        report_id = json.loads(listed.stdout)["reports"][0]["id"]
        exported = run_cli(repo, "conflicts", "export", report_id)
        report = json.loads(exported.stdout)["report"]
        self.assertEqual(report["kind"], "semantic_similarity")
        self.assertEqual(report["similarity"]["method"], "keyword")
        self.assertGreaterEqual(
            report["similarity"]["score"],
            conflicts.SEMANTIC_SIMILARITY_THRESHOLD,
        )
        self.assertEqual(
            report["conflicts"],
            [{"field": "body", "reason": "semantically_similar_memory"}],
        )


if __name__ == "__main__":
    unittest.main()
