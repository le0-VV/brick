from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / ".agents/brick/src"
sys.path.insert(0, str(SRC))

from brick import __version__
from brick import cli


def root_agents_text() -> str:
    return (ROOT / "AGENTS.md").read_text(encoding="utf-8")


class Phase1SetupTests(unittest.TestCase):
    def make_empty_repo(self) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name)
        subprocess.run(["git", "init"], cwd=repo, check=True, stdout=subprocess.PIPE)
        return repo

    def make_repo(self) -> Path:
        repo = self.make_empty_repo()
        bin_dir = repo / ".agents/brick/bin"
        bin_dir.mkdir(parents=True)
        executable = bin_dir / "brick"
        executable.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
        template = repo / cli.AGENTS_TEMPLATE_RELATIVE_PATH
        template.parent.mkdir(parents=True)
        template.write_text(root_agents_text(), encoding="utf-8")
        return repo

    def test_setup_repo_creates_phase1_files(self) -> None:
        repo = self.make_repo()

        result = cli.setup_repo(repo, skip_venv=True)

        self.assertEqual(result.repo_root, repo.resolve())
        self.assertTrue((repo / "brick").is_symlink())
        self.assertEqual(os.readlink(repo / "brick"), ".agents/brick/bin/brick")
        self.assertTrue((repo / ".agents/brick/index").is_dir())
        self.assertTrue((repo / ".agents/brick/conflicts").is_dir())
        self.assertTrue((repo / ".agents/memory/decision").is_dir())
        gitignore = (repo / ".gitignore").read_text()
        self.assertIn(".agents/brick/.venv/", gitignore)
        self.assertIn(".agents/brick/config.local.json", gitignore)
        self.assertIn("__pycache__/", gitignore)
        self.assertIn("*.pyc", gitignore)
        subprocess.run(
            ["git", "check-ignore", ".agents/brick/src/brick/__pycache__/cli.pyc"],
            cwd=repo,
            check=True,
            stdout=subprocess.PIPE,
        )
        local_config = json.loads((repo / ".agents/brick/config.local.json").read_text())
        self.assertEqual(local_config["embedding"]["url"], "")
        self.assertEqual(local_config["embedding"]["model"], "")
        self.assertEqual(local_config["embedding"]["api_key_env"], "BRICK_EMBEDDING_API_KEY")
        self.assertIn(cli.GITATTRIBUTES_ENTRY, (repo / ".gitattributes").read_text())
        agents = (repo / "AGENTS.md").read_text()
        self.assertEqual(agents, root_agents_text())
        self.assertNotIn(cli.BRICK_AGENT_MARKER, agents)
        self.assertIn("**DO NOT**, unless explicitly instructed by the user", agents)
        self.assertIn("Always use the language of the user's message.", agents)
        self.assertIn("`.agents/TODO.md`", agents)
        self.assertIn("Read a file fully before editing it.", agents)
        self.assertIn("Keep diffs narrow and task-focused.", agents)
        self.assertIn("Do not guess at attribute names, control flow, or config behaviour.", agents)
        self.assertIn("When delegating work to subagents is available", agents)
        self.assertIn("Commit each completed logical unit", agents)
        self.assertNotIn("BRICK_EMBEDDING_URL", agents)
        self.assertNotIn("BRICK_EMBEDDING_MODEL", agents)

        driver = subprocess.run(
            ["git", "config", "--local", "--get", "merge.brick-memory.driver"],
            cwd=repo,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.strip()
        self.assertEqual(driver, "./brick merge-driver %O %A %B %L %P")

    def test_setup_repo_backs_up_existing_agents_file(self) -> None:
        repo = self.make_repo()
        (repo / "AGENTS.md").write_text("Existing project instructions.\n", encoding="utf-8")

        cli.setup_repo(repo, skip_venv=True)

        backup = (repo / cli.AGENTS_BACKUP_NAME).read_text(encoding="utf-8")
        agents = (repo / "AGENTS.md").read_text(encoding="utf-8")
        self.assertEqual(backup, "Existing project instructions.\n")
        self.assertEqual(agents, root_agents_text())

    def test_setup_repo_updates_legacy_brick_agents_file(self) -> None:
        repo = self.make_repo()
        (repo / "AGENTS.md").write_text(
            f"{cli.BRICK_AGENT_MARKER}\nLegacy Brick instructions.\n",
            encoding="utf-8",
        )

        result = cli.setup_repo(repo, skip_venv=True)

        self.assertIn("updated Brick AGENTS.md instructions", result.actions)
        self.assertEqual((repo / "AGENTS.md").read_text(encoding="utf-8"), root_agents_text())
        self.assertFalse((repo / cli.AGENTS_BACKUP_NAME).exists())

    def test_cli_setup_emits_json(self) -> None:
        repo = self.make_repo()

        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / ".agents/brick/bin/brick"),
                "setup",
                "--skip-venv",
                "--json",
            ],
            cwd=repo,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["repo_root"], str(repo.resolve()))

    def test_cli_setup_emits_readable_text_by_default(self) -> None:
        repo = self.make_repo()

        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / ".agents/brick/bin/brick"),
                "setup",
                "--skip-venv",
            ],
            cwd=repo,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )

        self.assertIn("Brick setup complete.", completed.stdout)
        self.assertIn("- ", completed.stdout)

    def test_read_project_dependencies_reads_pyproject_dependencies(self) -> None:
        repo = self.make_repo()
        pyproject = repo / ".agents/brick/pyproject.toml"
        pyproject.write_text(
            "\n".join(
                [
                    "[project]",
                    'dependencies = ["example-dep==1.0", "other-dep>=2"]',
                    "",
                ]
            ),
            encoding="utf-8",
        )

        self.assertEqual(
            cli.read_project_dependencies(pyproject),
            ["example-dep==1.0", "other-dep>=2"],
        )

    def test_ensure_venv_installs_dependencies_with_uv_when_available(self) -> None:
        repo = self.make_repo()
        pyproject = repo / ".agents/brick/pyproject.toml"
        pyproject.write_text(
            '[project]\ndependencies = ["example-dep==1.0"]\n',
            encoding="utf-8",
        )
        python_bin = cli.venv_python_path(repo / cli.BRICK_VENV_RELATIVE_PATH)
        python_bin.parent.mkdir(parents=True)
        python_bin.write_text("", encoding="utf-8")
        result = cli.SetupResult(repo_root=repo.resolve())
        completed = subprocess.CompletedProcess([], 0, "", "")

        with (
            mock.patch.object(cli.shutil, "which", return_value="/opt/bin/uv"),
            mock.patch.object(
                cli,
                "run_dependency_command",
                return_value=completed,
            ) as run_command,
        ):
            cli.ensure_venv(repo, result, skip_venv=False)

        run_command.assert_called_once_with(
            [
                "/opt/bin/uv",
                "pip",
                "install",
                "--python",
                str(python_bin),
                "example-dep==1.0",
            ],
            repo,
        )
        self.assertIn("installed Brick dependencies with uv", result.actions)

    def test_ensure_venv_falls_back_to_pip_when_uv_is_unavailable(self) -> None:
        repo = self.make_repo()
        pyproject = repo / ".agents/brick/pyproject.toml"
        pyproject.write_text(
            '[project]\ndependencies = ["example-dep==1.0"]\n',
            encoding="utf-8",
        )
        python_bin = cli.venv_python_path(repo / cli.BRICK_VENV_RELATIVE_PATH)
        python_bin.parent.mkdir(parents=True)
        python_bin.write_text("", encoding="utf-8")
        result = cli.SetupResult(repo_root=repo.resolve())
        completed = subprocess.CompletedProcess([], 0, "", "")

        with (
            mock.patch.object(cli.shutil, "which", return_value=None),
            mock.patch.object(
                cli,
                "run_dependency_command",
                return_value=completed,
            ) as run_command,
        ):
            cli.ensure_venv(repo, result, skip_venv=False)

        run_command.assert_called_once_with(
            [str(python_bin), "-m", "pip", "install", "example-dep==1.0"],
            repo,
        )
        self.assertIn("installed Brick dependencies with pip", result.actions)

    def test_ensure_venv_reports_actionable_pip_install_failure(self) -> None:
        repo = self.make_repo()
        pyproject = repo / ".agents/brick/pyproject.toml"
        pyproject.write_text(
            '[project]\ndependencies = ["example-dep==1.0"]\n',
            encoding="utf-8",
        )
        python_bin = cli.venv_python_path(repo / cli.BRICK_VENV_RELATIVE_PATH)
        python_bin.parent.mkdir(parents=True)
        python_bin.write_text("", encoding="utf-8")
        result = cli.SetupResult(repo_root=repo.resolve())
        completed = subprocess.CompletedProcess([], 1, "", "pip failed")

        with (
            mock.patch.object(cli.shutil, "which", return_value=None),
            mock.patch.object(cli, "run_dependency_command", return_value=completed),
            self.assertRaisesRegex(
                cli.BrickError,
                "Could not install Brick dependencies",
            ),
        ):
            cli.ensure_venv(repo, result, skip_venv=False)

    def test_cli_version(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROOT / ".agents/brick/bin/brick"), "--version"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        self.assertEqual(completed.stdout.strip(), __version__)

    def test_install_script_bootstraps_repo_from_checkout(self) -> None:
        repo = self.make_empty_repo()

        completed = subprocess.run(
            [str(ROOT / "install.sh"), "--skip-venv", "--json"],
            cwd=repo,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "ok")
        self.assertTrue((repo / ".agents/brick/bin/brick").is_file())
        self.assertTrue((repo / ".agents/brick/AGENT_USAGE.md").is_file())
        self.assertTrue((repo / ".agents/brick/config.example.json").is_file())
        self.assertTrue((repo / ".agents/brick/config.local.json").is_file())
        self.assertTrue((repo / ".agents/brick/examples/llm-ingest/instructions.md").is_file())
        self.assertTrue(
            (repo / ".agents/brick/examples/llm-ingest/memory-ingest.schema.json").is_file()
        )
        self.assertTrue((repo / ".agents/brick/examples/memory-add/decision.json").is_file())
        self.assertEqual(
            (repo / ".agents/brick/templates/AGENTS.md").read_text(encoding="utf-8"),
            root_agents_text(),
        )
        self.assertTrue((repo / "brick").is_symlink())
        self.assertEqual((repo / "AGENTS.md").read_text(encoding="utf-8"), root_agents_text())

    def test_memory_add_without_json_returns_invalid_json(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROOT / ".agents/brick/bin/brick"), "memory", "add"],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
        )

        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "invalid")
        self.assertEqual(payload["reason"], "invalid_json")


if __name__ == "__main__":
    unittest.main()
