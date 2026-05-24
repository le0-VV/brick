from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / ".agents/brick/src"
sys.path.insert(0, str(SRC))

from brick import __version__
from brick import cli


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
        self.assertIn(".agents/brick/.venv/", (repo / ".gitignore").read_text())
        self.assertIn(cli.GITATTRIBUTES_ENTRY, (repo / ".gitattributes").read_text())
        self.assertIn(cli.BRICK_AGENT_MARKER, (repo / "AGENTS.md").read_text())

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
        self.assertIn("First task", agents)
        self.assertIn(cli.AGENTS_BACKUP_NAME, agents)

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
        self.assertTrue((repo / ".agents/brick/examples/memory-add/decision.json").is_file())
        self.assertTrue((repo / "brick").is_symlink())
        self.assertIn(cli.BRICK_AGENT_MARKER, (repo / "AGENTS.md").read_text())

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
