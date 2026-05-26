# Brick

Brick is a per-repo git-compatible semantic memory tooling for agentic development. Canonical memory is Markdown in the repository, while search indexes, embeddings, and conflict reports are generated local state.

> "I'm calling it brick because fuck naming. And you can quote me on that."
>
> -- Leonard, 2026

## Quickstart

Brick is installed into each repository that should carry its own memory bank.
Run the installer from inside the target Git worktree.

Prerequisites:

- Git.
- Python 3.11+ for the repo-local Brick environment.
- Optional but recommended: `uv`, which Brick uses when available to create
  `.agents/brick/.venv` and install dependencies faster.

Normal install, once Brick is hosted:

```sh
cd /path/to/project-that-should-use-brick
export BRICK_SOURCE_BASE_URL=https://raw.githubusercontent.com/le0-VV/brick/main
curl -fsSL "$BRICK_SOURCE_BASE_URL/install.sh" | sh
```

Local development install from this checkout:

```sh
cd /path/to/project-that-should-use-brick
/path/to/brick/install.sh
```

The installer copies Brick into `.agents/brick/`, makes `./brick` point at
`.agents/brick/bin/brick`, then runs `./brick setup`.

Setup creates or repairs:

- `.agents/memory/<type>/` canonical memory directories.
- `.agents/brick/index/` and `.agents/brick/conflicts/` generated state
  directories.
- `.agents/brick/config.local.json`, which is gitignored and device-local.
- `.gitignore` entries for generated Brick state.
- `.gitattributes` entry for the Brick memory merge driver.
- Local Git merge-driver config.
- `AGENTS.md` Brick instructions. If an existing non-Brick `AGENTS.md` is
  present, setup backs it up to `AGENTS.md.brick-backup` and asks agents to make
  user-reviewed merging the first task.
- `.agents/brick/.venv`, unless `--skip-venv` is used.

Re-run setup any time the copied Brick tooling, root symlink, dependency
environment, generated directories, or Git config look incomplete:

```sh
./brick setup
```

After setup, typical agent commands are:

```sh
./brick memory search "project conventions" --pretty
./brick memory add < .agents/brick/examples/memory-add/decision.json
./brick memory redact < redaction.json
./brick rebuild
./brick conflicts list --pretty
./brick conflicts propose <conflict-id> < proposal.json
```

Brick setup installs `.agents/brick/AGENT_USAGE.md` and examples under
`.agents/brick/examples/` so agents can discover the workflow from repository
files.

`brick setup` also owns Brick's local Python environment at
`.agents/brick/.venv`. It prefers `uv` when available, falls back to Python
`venv` plus `pip`, and installs dependencies declared in
`.agents/brick/pyproject.toml`.

## Memory Model

- Canonical memory lives under `.agents/memory/<type>/` as Markdown with
  constrained YAML frontmatter.
- Agents add memory through `./brick memory add` using JSON stdin.
- Agents redact leaked sensitive memory through `./brick memory redact` using
  JSON stdin with exact text values to replace with `[REDACTED]`.
- `./brick memory validate` checks schema, hashes, evidence, secrets, and PII.
- `./brick rebuild` regenerates `.agents/brick/index/brick.sqlite3`.
- `./brick memory search` uses keyword search by default and hybrid semantic
  search when local embedding settings are configured.
- `./brick merge-driver` only auto-resolves exact or fast-forward-safe cases;
  otherwise it writes review reports under `.agents/brick/conflicts/`.
- Agents can attach proposed conflict resolutions through `./brick conflicts
propose`; this updates only the local report and still requires human review.

## Embeddings

Semantic search is optional. `brick setup` creates a gitignored, device-local config file at `.agents/brick/config.local.json`. Configure an OpenAI-compatible embeddings endpoint there:

```json
{
    "embedding": {
        "url": "http://127.0.0.1:1234/v1",
        "model": "text-embedding-model",
        "api_key_env": "BRICK_EMBEDDING_API_KEY"
    }
}
```

Then rebuild:

```sh
./brick rebuild
```

`embedding.url` may be either a base URL ending in `/v1` or a full `/embeddings` endpoint. Do not put API keys directly in the local config; put the environment variable name in `embedding.api_key_env`. The `BRICK_EMBEDDING_URL`, `BRICK_EMBEDDING_MODEL`, and `BRICK_EMBEDDING_API_KEY` environment variables override the local file when set.

## Release Scope

The v1 target is local-first, free for everyone, Apache-2.0 licensed, and agent-runtime agnostic. See `ROADMAP.md` for the implementation checklist.
