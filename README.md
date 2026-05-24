# Brick

Brick is repo-local memory tooling for agentic development. Canonical memory is
Markdown in the repository, while search indexes, embeddings, and conflict
reports are generated local state.

> "Im calling it brick because fuck naming."

## Quickstart

From a repository that should use Brick:

```sh
export BRICK_SOURCE_BASE_URL=<raw Brick release URL>
curl -fsSL "$BRICK_SOURCE_BASE_URL/install.sh" | sh
```

From this checkout, bootstrap another local Git repository with:

```sh
/path/to/brick/install.sh --skip-venv --json
```

After setup:

```sh
./brick memory search "project conventions" --pretty
./brick memory add < .agents/brick/examples/memory-add/decision.json
./brick rebuild
./brick conflicts list --pretty
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
- `./brick memory validate` checks schema, hashes, evidence, secrets, and PII.
- `./brick rebuild` regenerates `.agents/brick/index/brick.sqlite3`.
- `./brick memory search` uses keyword search by default and hybrid semantic
  search when `BRICK_EMBEDDING_URL` and `BRICK_EMBEDDING_MODEL` are configured.
- `./brick merge-driver` only auto-resolves exact or fast-forward-safe cases;
  otherwise it writes review reports under `.agents/brick/conflicts/`.

## Embeddings

Semantic search is optional. Configure an OpenAI-compatible embeddings endpoint:

```sh
export BRICK_EMBEDDING_URL=http://127.0.0.1:1234/v1
export BRICK_EMBEDDING_MODEL=text-embedding-model
export BRICK_EMBEDDING_API_KEY=optional-token
./brick rebuild
```

`BRICK_EMBEDDING_URL` may be either a base URL ending in `/v1` or a full
`/embeddings` endpoint.

## Release Scope

The v1 target is local-first, free for everyone, Apache-2.0 licensed, and
agent-runtime agnostic. See `ROADMAP.md` for the implementation checklist.
