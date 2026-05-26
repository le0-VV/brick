# Brick

Brick is a per-repo git-compatible semantic memory tooling for agentic development. Canonical memory is Markdown in the repository, while search indexes, embeddings, and conflict reports are generated local state.

> "I'm calling it brick because fuck naming. And you can quote me on that."
>
> -- Leonard, 2026

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
./brick memory redact < redaction.json
./brick rebuild
./brick conflicts list --pretty
./brick conflicts propose <conflict-id> < proposal.json
```

Brick setup installs `.agents/brick/AGENT_USAGE.md` and examples under `.agents/brick/examples/` so agents can discover the workflow from repository files.

`brick setup` also owns Brick's local Python environment at `.agents/brick/.venv`. It prefers `uv` when available, falls back to Python `venv` plus `pip`, and installs dependencies declared in `.agents/brick/pyproject.toml`.

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
