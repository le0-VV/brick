# Brick

Brick is a per-repo git-compatible semantic memory tooling for agentic development. Canonical memory is Markdown in the repository, while search indexes, embeddings, and conflict reports are generated local state.

> "I'm calling it brick because fuck naming. And you can quote me on that."
>
> -- Leonard, 2026

## Setup

**Prerequisites**:

- Git.
- Python 3.11+ for the repo-local Brick environment.
- Optional but recommended: `uv`, which Brick uses when available to create
  `.agents/brick/.venv` and install dependencies faster.

From inside your project, ask your agent:

> Setup this project to use https://github.com/le0-VV/brick

## Agent instructions

Setup script: https://github.com/le0-VV/brick/raw/refs/heads/main/install.sh

When a user asks you to set up Brick in a project:

1. Make sure you are inside the target Git worktree.

   ```sh
   git rev-parse --show-toplevel
   ```

2. Run the installer from the target repository root.

   ```sh
   cd "$(git rev-parse --show-toplevel)"
   curl -fsSL https://github.com/le0-VV/brick/raw/refs/heads/main/install.sh | sh
   ```

3. Verify setup.

   ```sh
   ./brick setup --json --pretty
   ./brick memory validate --pretty
   ./brick memory search "project context" --pretty
   ```

4. Check whether semantic retrieval is configured. Brick uses the gitignored
   device-local file `.agents/brick/config.local.json`, or the
   `BRICK_EMBEDDING_URL` and `BRICK_EMBEDDING_MODEL` environment variables. If
   no embedding config is present, tell the user Brick search is keyword-only
   until they configure embeddings and run `./brick rebuild`.

5. If setup backs up an existing `AGENTS.md` to `AGENTS.md.brick-backup`, make
   user-reviewed merging of the old and new agent instructions the first follow-up
   task.

6. Commit only the coherent Brick setup files when the repository is verified.
   Do not commit `.agents/brick/.venv/`, `.agents/brick/index/`,
   `.agents/brick/conflicts/`, or `.agents/brick/config.local.json`.
