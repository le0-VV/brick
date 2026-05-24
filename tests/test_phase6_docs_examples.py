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


VALID_EXAMPLES = (
    "decision.json",
    "command.json",
    "routine.json",
    "skill.json",
)


def make_repo(test_case: unittest.TestCase) -> Path:
    temp_dir = tempfile.TemporaryDirectory()
    test_case.addCleanup(temp_dir.cleanup)
    repo = Path(temp_dir.name)
    subprocess.run(["git", "init"], cwd=repo, check=True, stdout=subprocess.PIPE)
    return repo


def run_brick(repo: Path, *args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / ".agents/brick/bin/brick"), *args],
        cwd=repo,
        input=input_text,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class Phase6DocsExamplesTests(unittest.TestCase):
    def test_readme_and_agent_usage_document_core_workflows(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        usage = (ROOT / ".agents/brick/AGENT_USAGE.md").read_text(encoding="utf-8")

        for command in (
            "./brick setup",
            "./brick memory add",
            "./brick memory search",
            "./brick rebuild",
            "./brick conflicts list",
        ):
            self.assertIn(command, readme + usage)
        self.assertIn("Im calling it brick because fuck naming.", readme)

    def test_example_memory_files_validate(self) -> None:
        completed = run_brick(
            ROOT,
            "memory",
            "validate",
            ".agents/brick/examples/memory-files",
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["checked"], 4)

    def test_example_memory_add_payloads_are_valid_and_blocked_example_is_blocked(self) -> None:
        repo = make_repo(self)
        examples = ROOT / ".agents/brick/examples/memory-add"

        for filename in VALID_EXAMPLES:
            payload_text = (examples / filename).read_text(encoding="utf-8")
            added = run_brick(repo, "memory", "add", input_text=payload_text)
            added_payload = json.loads(added.stdout)
            self.assertEqual(added.returncode, 0, added.stdout + added.stderr)
            self.assertEqual(added_payload["status"], "ok")

        validation = run_brick(repo, "memory", "validate")
        validation_payload = json.loads(validation.stdout)
        self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)
        self.assertEqual(validation_payload["checked"], 4)

        blocked_text = (examples / "blocked-unsafe.json").read_text(encoding="utf-8")
        blocked = run_brick(repo, "memory", "add", input_text=blocked_text)
        blocked_payload = json.loads(blocked.stdout)
        self.assertEqual(blocked.returncode, 1)
        self.assertEqual(blocked_payload["status"], "blocked")
        self.assertIn("redact", blocked_payload["actions"])


if __name__ == "__main__":
    unittest.main()
