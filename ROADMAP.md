# Brick Roadmap

Brick is a repo-local memory system for developer teams and open source
projects. Its core job is to let contributors fork or clone a repository,
give their agents useful project memory immediately, and contribute new
memories back upstream through normal Git workflows.

This document is the working design plan and implementation roadmap. The
canonical decision log lives in `.agents/MEMORIES.md`; this file turns those
decisions into a buildable plan.

## Product Shape

Brick is not a hosted service and not a general personal second brain. It is
repo infrastructure:

- Memory lives inside the project repository.
- Canonical memory is human-readable Markdown tracked by Git.
- Semantic search is a generated local projection, never the source of truth.
- Forks, branches, pull requests, merges, cherry-picks, and reviews are the
  collaboration model.
- Agent runtimes are not prescribed. Agents learn Brick from repo docs,
  scripts, and instructions.
- V1 should work with Python available and should manage its own dependencies.

The first must-win workflow:

1. A contributor forks or clones a project.
2. Their agent reads the repo-local memory and project instructions.
3. During work, the agent identifies useful project context.
4. The agent submits a memory candidate through Brick.
5. Brick validates, writes, indexes, and later helps merge that memory upstream.

## Design Principles

1. Markdown is canonical.
2. Generated state is rebuildable.
3. Agents do not write memory files directly.
4. Unsupported memory is rejected, not stored as low-confidence memory.
5. Sensitive information is invalid by default.
6. Exact duplicates can merge automatically; semantic similarity needs review.
7. Git remains the collaboration layer.
8. CLI output must be predictable enough for agents to parse.

## Repository Layout

Target layout:

```text
.agents/
  brick/
    pyproject.toml
    setup.py or setup.sh
    index/              # generated, gitignored
    conflicts/          # generated, gitignored
  memory/
    decision/
    command/
    routine/
    skill/
    preference/
    fact/
    incident/
    pattern/
    task/
    policy/
```

Memory files use type folders and ULID-slug filenames:

```text
.agents/memory/decision/01JX3Y1Y8H6TR4Y3Q38K1W9P2A-hybrid-search.md
.agents/memory/command/01JX3Y2D8S6Q7M4K2B9P0V1W3T-run-tests.md
```

Generated state under `.agents/brick/index/` and `.agents/brick/conflicts/`
must be ignored by Git by default.

## Memory Schema

Every memory is one Markdown file with YAML frontmatter and a freeform Markdown
body. The body does not need to duplicate the title as a `# Heading`.

Required frontmatter:

```yaml
id: 01JX3Y1Y8H6TR4Y3Q38K1W9P2A
title: "Decision to use hybrid retrieval"
type: decision
status: active
tags:
  - retrieval
  - architecture
created_at: 2026-05-24T00:00:00Z
updated_at: 2026-05-24T00:00:00Z
content_hash: "sha256:..."
source:
  kind: conversation
evidence:
  - "Quoted user text or concrete work artifact reference."
```

Allowed `status` values:

```text
active
superseded
tombstone
redacted
```

Committed memory must not use `draft`. Candidates stay outside canonical memory
until valid.

Optional relationship fields:

```yaml
supersedes: []
related: []
```

When present, `supersedes` and `related` entries must be valid memory ULIDs.

### Trust Signals

Brick should not preserve low-confidence committed memory. In v1, trust is
expressed through required source/evidence fields, validation status, memory
status, and retrieval scoring. If a later implementation adds an explicit
confidence field, it must not become a way to store weak or unsupported memory
as durable project context.

V1 types:

```text
decision
command
routine
skill
preference
fact
incident
pattern
task
policy
```

Tags provide flexible topic-like labeling. Brick should not have a separate
`topics` field in v1.

### Type-Specific Fields

`command` memories may include:

```yaml
command: "uv run pytest"
cwd: "."
when_to_use: "Run Python tests before committing."
expected_output: "Tests pass."
failure_notes: "If dependencies are missing, run brick setup."
```

`routine` and `skill` memories may include:

```yaml
steps:
  - "Run tests."
  - "Update changelog."
prerequisites:
  - "Clean worktree."
verify: "CI passes and release artifact exists."
```

## Validation And Safety

Validation is part of the core product, not a later hardening step.

Required validation:

- Parse YAML frontmatter and Markdown body.
- Require all core schema fields.
- Validate plain ULID IDs.
- Validate `type`, `status`, timestamps, and `content_hash`.
- Require `source.kind`.
- Require at least one `evidence` item.
- Reject memories without enough evidence.
- Reject unsupported or low-confidence durable memory.
- Block obvious secrets before writing memory.
- Block possible PII until explicitly confirmed.
- Reject non-JSON input to `brick memory add`.

Secret and PII handling:

- Obvious secrets include API keys, private keys, tokens, and passwords.
- Possible PII includes names, emails, phone numbers, and addresses.
- Committed memory should be safe for the repository's intended audience.
- If sensitive content slips through, redaction creates a new commit replacing
  leaked text with `[REDACTED]` plus a tombstone or evidence note.

Blocked candidates must return structured JSON:

```json
{
  "status": "blocked",
  "reason": "possible_pii",
  "matches": [
    {"kind": "email", "text": "[REDACTED]", "line": 12}
  ],
  "actions": ["redact", "confirm_public", "reject"]
}
```

## CLI Surface

V1 command surface:

```text
brick setup
brick memory add
brick memory validate [path]
brick memory search "query"
brick rebuild
brick merge-driver ...
brick conflicts list
brick conflicts export <id>
```

CLI rules:

- Keep memory operations under `brick memory`.
- `brick memory add` reads JSON from stdin by default.
- `brick memory add` rejects non-JSON input.
- Agent-facing commands return JSON by default:
  - `brick memory add`
  - `brick memory search`
  - `brick memory validate`
  - `brick conflicts list`
  - `brick conflicts export`
- Human/convenience commands such as `brick setup` and `brick rebuild` may print
  readable text by default.
- JSON-oriented commands support `--pretty` in v1.

## Dependency Management

Brick can assume Python is available for agentic coding workflows.

Dependency rules:

- Prefer `uv`.
- Fall back to `pip`.
- Keep Brick dependencies under `.agents/brick/pyproject.toml`.
- Use a Brick-owned virtual environment, not the host project's main venv.
- Provide one setup entrypoint.
- Brick commands should run setup or resolve dependencies instead of leaving
  users or agents to manually install packages.

## Local Index And Retrieval

The Markdown files are authoritative. The local index is disposable.

Index rules:

- Generated state lives under `.agents/brick/index/`.
- Generated state is gitignored.
- V1 uses simple local files and/or SQLite.
- V1 does not require Chroma, Qdrant, or another external vector database.
- `brick rebuild` regenerates the local index from Markdown memory files.
- Stable `content_hash` lives in frontmatter.
- Volatile index state stays outside canonical Markdown.

Embedding rules:

- `BRICK_EMBEDDING_URL` is the standard embedding endpoint variable.
- Brick can use a local system-wide embedding service or API-backed embeddings.
- If no embedding endpoint or API is configured, Brick falls back to keyword
  search and clearly reports that semantic search is unavailable.

Retrieval rules:

- Retrieval is hybrid when embeddings are available.
- Reranking is not a v1 requirement.
- Superseded memories are ignored by default.
- Superseded memories can be retrieved explicitly.
- Returned context packages include summary, source path, confidence/status
  information, evidence, and a full-text link.

## Merge Driver

The merge driver is central to Brick because the product exists to make memory
safe to manage through forks and PRs.

Merge behavior:

- Auto-merge exact duplicate memory IDs or exact duplicate content.
- Do not silently merge semantically similar memories.
- Create structured conflict/review items for semantic similarity.
- Agents may propose merged memories.
- Human acceptance is required before Brick writes a final merged memory.
- Deterministic frontmatter fields merge automatically when non-conflicting.
- The Markdown body uses normal Git-style text merge behavior.
- If the same structured frontmatter field changes differently on both sides,
  Brick blocks and creates a conflict report.
- Append-only fields such as `evidence` may union distinct entries.

Conflict reports:

- Stored under `.agents/brick/conflicts/`.
- Gitignored by default.
- Exportable when a user wants to share a report in PR discussion or review.

## Roadmap

### Phase 0 - Specification Baseline

Goal: capture product decisions in a form that can drive implementation.

Deliverables:

- `ROADMAP.md`
- Initial schema contract
- Initial command surface
- Initial repo layout
- Initial safety and merge-driver policy

Exit criteria:

- Product boundaries are clear.
- V1 scope is narrow enough to build.
- Remaining unknowns are implementation details, not product identity.

### Phase 1 - Skeleton And Setup

Goal: make Brick runnable from a cloned repo.

Deliverables:

- `.agents/brick/pyproject.toml`
- Setup entrypoint
- Brick-owned venv handling
- `brick setup`
- Basic CLI argument parser
- `.gitignore` entries for generated index and conflict reports

Exit criteria:

- A fresh clone can run `brick setup`.
- Commands fail with actionable dependency/setup messages.
- No generated state is accidentally tracked.

### Phase 2 - Schema And Validation

Goal: make canonical Markdown memory safe and consistent.

Deliverables:

- YAML frontmatter parser
- Markdown memory loader
- Schema validator
- ULID generation and validation
- Content hash calculation
- Secret scanner
- PII block-until-confirmed flow
- Structured validation output
- `brick memory validate`

Exit criteria:

- Invalid memory is rejected with machine-readable reasons.
- Missing evidence is rejected.
- Obvious secrets are blocked.
- Possible PII is blocked until confirmed.

### Phase 3 - Memory Write Path

Goal: let agents add memory without writing files directly.

Deliverables:

- `brick memory add`
- JSON stdin input contract
- Slug generation
- Type-folder file creation
- Type-specific field validation
- `active`, `superseded`, `tombstone`, `redacted` status handling
- Human-readable `--pretty` output

Exit criteria:

- Agents can submit valid JSON and Brick writes Markdown.
- Non-JSON input is rejected.
- Written files pass validation.
- Generated filenames are stable and reviewable.

### Phase 4 - Index And Search

Goal: give agents useful retrieval immediately, even without embeddings.

Deliverables:

- Local index storage under `.agents/brick/index/`
- SQLite or simple local file index
- `brick rebuild`
- Keyword fallback search
- Optional embedding endpoint integration through `BRICK_EMBEDDING_URL`
- `brick memory search`
- Retrieval context package JSON

Exit criteria:

- Search works without embeddings.
- Semantic search activates when an endpoint is configured.
- Missing semantic capability is reported clearly.
- Rebuild is deterministic from Markdown.

### Phase 5 - Merge Driver And Conflict Review

Goal: make fork/upstream memory collaboration safe.

Deliverables:

- `brick merge-driver`
- `.gitattributes` guidance
- Exact duplicate auto-merge
- Structured frontmatter merge
- Evidence union behavior
- Semantic similarity detection hook
- Conflict report generation
- `brick conflicts list`
- `brick conflicts export`

Exit criteria:

- Exact duplicates do not create noisy conflicts.
- Semantic similarity never silently rewrites memory.
- Agents can read conflict reports and propose fixes.
- Users can export conflict reports for PR review.

### Phase 6 - Agent Instructions And Examples

Goal: make Brick self-explanatory to agents working in a repo.

Deliverables:

- Agent-facing usage instructions
- Example memory files for each core type
- Example `brick memory add` payloads
- Example search and conflict workflows
- README quickstart

Exit criteria:

- A new agent can discover how to use Brick from repo files.
- Contributors can fork, run setup, search memory, and add memory.

### Phase 7 - Quality And Regression Tests

Goal: keep Brick from corrupting or poisoning repo memory.

Deliverables:

- Schema validation tests
- Secret/PII scanner tests
- Hash stability tests
- CLI JSON contract tests
- Rebuild/search tests
- Merge-driver fixture tests
- Redaction/tombstone tests

Exit criteria:

- Core workflows are covered by fixtures.
- Regression tests catch malformed memory, unsafe memory, and unsafe merges.

## Remaining Implementation Decisions

These should be resolved during implementation rather than through more product
definition:

- Exact Python CLI framework, if any.
- Exact local SQLite schema.
- Exact content hash canonicalization algorithm.
- Exact secret and PII detector implementation.
- Exact embedding endpoint request/response contract.
- Exact conflict report JSON schema.
- Exact `.gitattributes` merge-driver installation flow.

## V1 Non-Goals

- Hosted service.
- Product telemetry.
- Realtime collaborative editing.
- Required external vector database.
- Required reranker model.
- PR/issue/commit mining as a first ingest source.
- Storing secrets or sensitive private data in memory.
