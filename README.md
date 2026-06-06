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

```text
Setup this project to use https://github.com/le0-VV/brick
```

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

3. If `.agents/TODO.md` exists, make sure it is not tracked. Preserve the
    local file and remove it only from Git's index when needed.

    ```sh
    if [ -f .agents/TODO.md ] && git ls-files --error-unmatch .agents/TODO.md >/dev/null 2>&1; then
      git rm --cached -- .agents/TODO.md
    fi
    ```

4. Verify setup.

    ```sh
    ./brick setup --json --pretty
    ./brick memory validate --pretty
    ./brick memory search "project context" --pretty
    ```

5. Know that `./brick setup` checks upstream Brick at most once per day using
    `.agents/brick/source.json`, then writes the gitignored local check state to
    `.agents/brick/update-state.json`. If upstream package files change, review
    and commit the updated Brick files as part of the setup change.

6. Check whether semantic retrieval is configured. Brick reads `embedding.url`
    and `embedding.model` from the gitignored device-local file
    `.agents/brick/config.local.json`. After first setup, if there is no clear
    user answer on whether to use semantic retrieval, ask it as an important
    setup question. If the user opts in, ask for the embedding server URL and
    model name, write both values to the local config file, and run `./brick
    rebuild`. If they opt out, tell them Brick search is keyword-only.

7. If setup backs up an existing `AGENTS.md` to `AGENTS.md.brick-backup`, review the backup with the user before merging any old project-specific instructions back into the new file.

8. Commit only the coherent Brick setup files when the repository is verified. Do not commit `.agents/TODO.md`, `.agents/brick/.venv/`, `.agents/brick/index/`, `.agents/brick/conflicts/`, `.agents/brick/config.local.json`, or `.agents/brick/update-state.json`.
