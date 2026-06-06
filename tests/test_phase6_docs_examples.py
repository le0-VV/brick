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
    def test_github_actions_ci_runs_unittest_discovery(self) -> None:
        workflow_path = ROOT / ".github/workflows/ci.yml"
        workflow = workflow_path.read_text(encoding="utf-8")

        self.assertTrue(workflow_path.is_file())
        self.assertIn("name: CI", workflow)
        self.assertIn("pull_request:", workflow)
        self.assertIn("branches:\n      - main", workflow)
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertIn("runs-on: ubuntu-24.04", workflow)
        self.assertIn("actions/checkout@08eba0b27e820071cde6df949e0beb9ba4906955", workflow)
        self.assertNotIn("actions/checkout@v4", workflow)
        self.assertIn("python3 -B -m unittest discover tests", workflow)

    def test_readme_and_agent_usage_document_core_workflows(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        usage = (ROOT / ".agents/brick/AGENT_USAGE.md").read_text(encoding="utf-8")
        rendered_readme = " ".join(readme.split())
        rendered_usage = " ".join(usage.split())

        for command in (
            "./brick setup",
            "./brick memory add",
            "./brick memory redact",
            "./brick memory search",
            "./brick rebuild",
            "./brick conflicts list",
            "./brick conflicts propose",
        ):
            self.assertIn(command, readme + usage)
        self.assertIn("I'm calling it brick because fuck naming.", readme)
        self.assertIn(".agents/brick/config.local.json", readme)
        self.assertIn(".agents/brick/config.local.json", usage)
        self.assertIn(".agents/brick/source.json", readme)
        self.assertIn(".agents/brick/source.json", usage)
        self.assertIn(".agents/brick/update-state.json", readme)
        self.assertIn(".agents/brick/update-state.json", usage)
        self.assertIn("at most once per day", readme)
        self.assertIn("at most once per day", usage)
        self.assertIn("embedding.url", usage)
        self.assertIn("embedding.model", usage)
        self.assertIn("important setup question", rendered_readme)
        self.assertIn("important setup question", rendered_usage)
        self.assertIn("keyword-only", usage)
        self.assertIn(".agents/TODO.md", readme)
        self.assertIn("Preserve the local file", rendered_readme)
        self.assertIn("git ls-files --error-unmatch .agents/TODO.md", readme)
        self.assertIn("git rm --cached -- .agents/TODO.md", readme)
        self.assertIn("llm-ingest/instructions.md", usage)
        self.assertIn("memory-ingest.schema.json", usage)
        self.assertIn("add", usage)
        self.assertIn("clarify", usage)
        self.assertIn("reject", usage)

    def test_llm_ingest_schema_guides_reviewable_candidates(self) -> None:
        schema_path = ROOT / ".agents/brick/examples/llm-ingest/memory-ingest.schema.json"
        instructions = (
            ROOT / ".agents/brick/examples/llm-ingest/instructions.md"
        ).read_text(encoding="utf-8")
        schema = json.loads(schema_path.read_text(encoding="utf-8"))

        self.assertEqual(schema["additionalProperties"], False)
        self.assertEqual(schema["properties"]["action"]["enum"], ["add", "clarify", "reject"])
        self.assertIn("candidate", schema["required"])
        candidate_schema = schema["properties"]["candidate"]["anyOf"][1]
        self.assertEqual(candidate_schema["additionalProperties"], False)
        self.assertIn("confirm_public", candidate_schema["required"])
        self.assertIn("source", candidate_schema["required"])
        self.assertIn("evidence", candidate_schema["required"])
        self.assertNotIn("fields", candidate_schema["properties"])
        self.assertIn("Write the memory body as one concise", instructions)
        self.assertIn('phrase "remember that" is only a signal', instructions)
        self.assertIn("A direct user statement is valid evidence", instructions)
        self.assertIn("Do not emit `fields`", instructions)
        self.assertIn("If `action` is `clarify`, ask", instructions)
        self.assertIn("./brick memory add", instructions)

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
