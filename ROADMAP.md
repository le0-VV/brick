# Brick Roadmap

Brick is a repo-local memory system for developer teams and open source
projects. This file is both the design plan and the long-horizon implementation
checklist.

Agents working on Brick should keep this file current as work lands. Mark a box
only when the corresponding behavior is implemented, verified, and documented
well enough for another agent to continue from the repository alone.

## Checklist Rules

- [ ] Keep `ROADMAP.md` aligned with `.agents/MEMORIES.md` when product
  decisions change.
- [ ] Keep `.agents/TODO.md` scoped to the current work session.
- [ ] Mark roadmap implementation tasks complete only after verification.
- [ ] Prefer adding concrete follow-up tasks over leaving vague TODO prose.
- [ ] Keep generated state out of Git unless the roadmap explicitly says
  otherwise.

## Product Commitments

- [x] Brick targets developer teams and open source communities first.
- [x] Brick is repo infrastructure, not a hosted service or personal second
  brain.
- [x] Memory lives inside the project repository.
- [x] Canonical memory is human-readable Markdown tracked by Git.
- [x] Semantic search is a generated local projection, never the source of
  truth.
- [x] Forks, branches, pull requests, merges, cherry-picks, and reviews are the
  collaboration model.
- [x] Agent runtimes are not prescribed.
- [x] Agents learn Brick from repo docs, scripts, and instructions.
- [x] V1 assumes Python is available for agentic coding workflows.
- [x] V1 manages its own dependencies instead of depending on the host project
  environment.

## Must-Win Workflow

- [x] A contributor forks or clones a project.
- [x] The contributor's agent reads repo-local memory and project instructions.
- [x] During work, the agent identifies useful project context.
- [x] The agent submits a memory candidate through Brick.
- [x] Brick validates, writes, indexes, and later helps merge that memory
  upstream.

## Design Principles

- [x] Markdown is canonical.
- [x] Generated state is rebuildable.
- [x] Agents do not write memory files directly.
- [x] Unsupported memory is rejected, not stored as low-confidence memory.
- [x] Sensitive information is invalid by default.
- [x] Exact duplicates can merge automatically.
- [x] Semantic similarity requires review.
- [x] Git remains the collaboration layer.
- [x] CLI output must be predictable enough for agents to parse.

## Target Repository Layout

- [ ] Create `.agents/brick/pyproject.toml`.
- [ ] Create one setup entrypoint under `.agents/brick/`.
- [ ] Create `.agents/brick/index/` for generated index state.
- [ ] Create `.agents/brick/conflicts/` for generated conflict reports.
- [ ] Gitignore `.agents/brick/index/`.
- [ ] Gitignore `.agents/brick/conflicts/`.
- [ ] Create `.agents/memory/` as canonical memory root.
- [ ] Organize memory files by type folder under `.agents/memory/`.
- [ ] Use ULID-slug filenames for memory files.

Target structure:

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

Filename examples:

```text
.agents/memory/decision/01JX3Y1Y8H6TR4Y3Q38K1W9P2A-hybrid-search.md
.agents/memory/command/01JX3Y2D8S6Q7M4K2B9P0V1W3T-run-tests.md
```

## Memory Schema Checklist

- [ ] Store every memory as one Markdown file with YAML frontmatter.
- [ ] Allow memory bodies to be freeform Markdown.
- [ ] Do not require a duplicate `# Title` heading in the Markdown body.
- [ ] Require `id`.
- [ ] Require `title`.
- [ ] Require `type`.
- [ ] Require `status`.
- [ ] Require `tags`.
- [ ] Require `created_at`.
- [ ] Require `updated_at`.
- [ ] Require `content_hash`.
- [ ] Require `source.kind`.
- [ ] Require at least one `evidence` item.
- [ ] Allow optional `supersedes`.
- [ ] Allow optional `related`.
- [ ] Validate `supersedes` and `related` entries as memory ULIDs when present.

Required frontmatter shape:

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

- [x] `active`
- [x] `superseded`
- [x] `tombstone`
- [x] `redacted`
- [x] No committed `draft` status.

Allowed v1 `type` values:

- [x] `decision`
- [x] `command`
- [x] `routine`
- [x] `skill`
- [x] `preference`
- [x] `fact`
- [x] `incident`
- [x] `pattern`
- [x] `task`
- [x] `policy`

Tag policy:

- [x] Use `tags` for flexible topic-like labeling.
- [x] Do not add a separate `topics` field in v1.

Trust policy:

- [x] Do not preserve low-confidence committed memory.
- [x] Express trust through required source/evidence fields.
- [x] Express trust through validation status.
- [x] Express trust through memory status.
- [x] Express retrieval confidence through retrieval scoring, not weak durable
  memory.
- [ ] If a later explicit confidence field is added, prevent it from becoming a
  way to store weak or unsupported memory as durable project context.

## Type-Specific Schema Checklist

- [ ] Support lightweight structured fields for `command` memories.
- [ ] Support lightweight structured fields for `routine` memories.
- [ ] Support lightweight structured fields for `skill` memories.
- [ ] Keep type-specific detail human-readable in Markdown even when structured
  fields exist.

`command` fields:

- [ ] Support `command`.
- [ ] Support `cwd`.
- [ ] Support `when_to_use`.
- [ ] Support `expected_output`.
- [ ] Support `failure_notes`.

Example:

```yaml
command: "uv run pytest"
cwd: "."
when_to_use: "Run Python tests before committing."
expected_output: "Tests pass."
failure_notes: "If dependencies are missing, run brick setup."
```

`routine` and `skill` fields:

- [ ] Support `steps`.
- [ ] Support `prerequisites`.
- [ ] Support `verify`.

Example:

```yaml
steps:
  - "Run tests."
  - "Update changelog."
prerequisites:
  - "Clean worktree."
verify: "CI passes and release artifact exists."
```

## Validation And Safety Checklist

- [ ] Parse YAML frontmatter.
- [ ] Parse Markdown body.
- [ ] Require all core schema fields.
- [ ] Validate plain ULID IDs without a `mem_` prefix.
- [ ] Validate `type`.
- [ ] Validate `status`.
- [ ] Validate timestamps.
- [ ] Validate `content_hash`.
- [ ] Require `source.kind`.
- [ ] Require at least one `evidence` item.
- [ ] Reject memories without enough evidence.
- [ ] Reject unsupported durable memory.
- [ ] Reject low-confidence durable memory.
- [ ] Reject non-JSON input to `brick memory add`.
- [ ] Return structured JSON for validation failures.

Secret and PII checks:

- [ ] Block obvious API keys before writing memory.
- [ ] Block private keys before writing memory.
- [ ] Block tokens before writing memory.
- [ ] Block passwords before writing memory.
- [ ] Block possible names until explicitly confirmed.
- [ ] Block possible emails until explicitly confirmed.
- [ ] Block possible phone numbers until explicitly confirmed.
- [ ] Block possible addresses until explicitly confirmed.
- [ ] Ensure committed memory is safe for the repository's intended audience.

Redaction:

- [ ] Provide a redaction flow for sensitive content that slips through.
- [ ] Replace leaked text with `[REDACTED]`.
- [ ] Create a tombstone or evidence note explaining why redaction happened.
- [ ] Rebuild the local index after redaction.

Blocked candidate response shape:

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

## CLI Checklist

Command surface:

- [ ] Implement `brick setup`.
- [ ] Implement `brick memory add`.
- [ ] Implement `brick memory validate [path]`.
- [ ] Implement `brick memory search "query"`.
- [ ] Implement `brick rebuild`.
- [ ] Implement `brick merge-driver ...`.
- [ ] Implement `brick conflicts list`.
- [ ] Implement `brick conflicts export <id>`.

Input and output rules:

- [ ] Keep memory operations under `brick memory`.
- [ ] Make `brick memory add` read JSON from stdin by default.
- [ ] Make `brick memory add` reject non-JSON input.
- [ ] Make `brick memory add` return JSON by default.
- [ ] Make `brick memory search` return JSON by default.
- [ ] Make `brick memory validate` return JSON by default.
- [ ] Make `brick conflicts list` return JSON by default.
- [ ] Make `brick conflicts export` return JSON by default.
- [ ] Allow `brick setup` to print readable text by default.
- [ ] Allow `brick rebuild` to print readable text by default.
- [ ] Add `--pretty` for JSON-oriented commands in v1.

## Dependency Checklist

- [ ] Assume Python is available.
- [ ] Prefer `uv` for dependency setup.
- [ ] Fall back to `pip`.
- [ ] Keep Brick dependencies under `.agents/brick/pyproject.toml`.
- [ ] Use a Brick-owned virtual environment.
- [ ] Do not use the host project's main virtual environment.
- [ ] Provide one setup entrypoint.
- [ ] Make Brick commands run setup or resolve dependencies when possible.
- [ ] Emit actionable setup/dependency messages when automatic setup cannot
  proceed.

## Local Index And Retrieval Checklist

Index:

- [ ] Store generated index state under `.agents/brick/index/`.
- [ ] Keep generated index state out of Git.
- [ ] Use simple local files and/or SQLite for v1.
- [ ] Do not require Chroma, Qdrant, or another external vector database in v1.
- [ ] Implement `brick rebuild`.
- [ ] Rebuild deterministically from canonical Markdown memory files.
- [ ] Keep stable `content_hash` in frontmatter.
- [ ] Keep volatile index state outside canonical Markdown.

Embedding:

- [ ] Use `BRICK_EMBEDDING_URL` as the standard embedding endpoint environment
  variable.
- [ ] Support a local system-wide embedding service.
- [ ] Support API-backed embeddings.
- [ ] Fall back to keyword search when no embedding endpoint or API is
  configured.
- [ ] Clearly report when semantic search is unavailable.

Retrieval:

- [ ] Use hybrid retrieval when embeddings are available.
- [ ] Do not require reranking in v1.
- [ ] Ignore superseded memories by default.
- [ ] Allow explicit retrieval of superseded memories.
- [ ] Return summary in retrieval context packages.
- [ ] Return source path in retrieval context packages.
- [ ] Return status/trust information in retrieval context packages.
- [ ] Return evidence in retrieval context packages.
- [ ] Return a full-text link in retrieval context packages.

## Merge Driver Checklist

Core merge behavior:

- [ ] Implement `brick merge-driver`.
- [ ] Add `.gitattributes` guidance for memory files.
- [ ] Auto-merge exact duplicate memory IDs.
- [ ] Auto-merge exact duplicate content.
- [ ] Do not silently merge semantically similar memories.
- [ ] Create structured conflict/review items for semantic similarity.
- [ ] Allow agents to propose merged memories.
- [ ] Require human acceptance before Brick writes a final merged memory.
- [ ] Merge deterministic frontmatter fields automatically when non-conflicting.
- [ ] Use normal Git-style text merge behavior for Markdown body edits.
- [ ] Block when the same structured frontmatter field changes differently on
  both sides.
- [ ] Create a conflict report when structured frontmatter conflicts.
- [ ] Union distinct entries for append-only fields such as `evidence`.

Conflict reports:

- [ ] Store conflict reports under `.agents/brick/conflicts/`.
- [ ] Keep conflict reports gitignored by default.
- [ ] Implement `brick conflicts list`.
- [ ] Implement `brick conflicts export <id>`.
- [ ] Make conflict reports exportable for PR discussion or review.

## Phase Roadmap Checklist

### Phase 0 - Specification Baseline

Goal: capture product decisions in a form that can drive implementation.

- [x] Create `ROADMAP.md`.
- [x] Capture initial schema contract.
- [x] Capture initial command surface.
- [x] Capture initial repo layout.
- [x] Capture initial safety policy.
- [x] Capture initial merge-driver policy.
- [ ] Keep the roadmap checklist updated as implementation discovers concrete
  details.

Exit criteria:

- [x] Product boundaries are clear.
- [x] V1 scope is narrow enough to build.
- [x] Remaining unknowns are implementation details, not product identity.

### Phase 1 - Skeleton And Setup

Goal: make Brick runnable from a cloned repo.

- [ ] Add `.agents/brick/pyproject.toml`.
- [ ] Add setup entrypoint.
- [ ] Add Brick-owned venv handling.
- [ ] Implement `brick setup`.
- [ ] Add basic CLI argument parser.
- [ ] Add gitignore entries for generated index state.
- [ ] Add gitignore entries for generated conflict reports.

Exit criteria:

- [ ] A fresh clone can run `brick setup`.
- [ ] Commands fail with actionable dependency/setup messages.
- [ ] No generated state is accidentally tracked.

### Phase 2 - Schema And Validation

Goal: make canonical Markdown memory safe and consistent.

- [ ] Implement YAML frontmatter parser.
- [ ] Implement Markdown memory loader.
- [ ] Implement schema validator.
- [ ] Implement ULID generation.
- [ ] Implement ULID validation.
- [ ] Implement content hash calculation.
- [ ] Implement secret scanner.
- [ ] Implement PII block-until-confirmed flow.
- [ ] Implement structured validation output.
- [ ] Implement `brick memory validate`.

Exit criteria:

- [ ] Invalid memory is rejected with machine-readable reasons.
- [ ] Missing evidence is rejected.
- [ ] Obvious secrets are blocked.
- [ ] Possible PII is blocked until confirmed.

### Phase 3 - Memory Write Path

Goal: let agents add memory without writing files directly.

- [ ] Implement `brick memory add`.
- [ ] Define JSON stdin input contract.
- [ ] Implement slug generation.
- [ ] Implement type-folder file creation.
- [ ] Implement type-specific field validation.
- [ ] Implement `active` status handling.
- [ ] Implement `superseded` status handling.
- [ ] Implement `tombstone` status handling.
- [ ] Implement `redacted` status handling.
- [ ] Implement human-readable `--pretty` output.

Exit criteria:

- [ ] Agents can submit valid JSON and Brick writes Markdown.
- [ ] Non-JSON input is rejected.
- [ ] Written files pass validation.
- [ ] Generated filenames are stable and reviewable.

### Phase 4 - Index And Search

Goal: give agents useful retrieval immediately, even without embeddings.

- [ ] Implement local index storage under `.agents/brick/index/`.
- [ ] Implement SQLite or simple local file index.
- [ ] Implement `brick rebuild`.
- [ ] Implement keyword fallback search.
- [ ] Implement optional embedding endpoint integration through
  `BRICK_EMBEDDING_URL`.
- [ ] Implement `brick memory search`.
- [ ] Implement retrieval context package JSON.

Exit criteria:

- [ ] Search works without embeddings.
- [ ] Semantic search activates when an endpoint is configured.
- [ ] Missing semantic capability is reported clearly.
- [ ] Rebuild is deterministic from Markdown.

### Phase 5 - Merge Driver And Conflict Review

Goal: make fork/upstream memory collaboration safe.

- [ ] Implement `brick merge-driver`.
- [ ] Add `.gitattributes` guidance.
- [ ] Implement exact duplicate auto-merge.
- [ ] Implement structured frontmatter merge.
- [ ] Implement evidence union behavior.
- [ ] Implement semantic similarity detection hook.
- [ ] Implement conflict report generation.
- [ ] Implement `brick conflicts list`.
- [ ] Implement `brick conflicts export`.

Exit criteria:

- [ ] Exact duplicates do not create noisy conflicts.
- [ ] Semantic similarity never silently rewrites memory.
- [ ] Agents can read conflict reports and propose fixes.
- [ ] Users can export conflict reports for PR review.

### Phase 6 - Agent Instructions And Examples

Goal: make Brick self-explanatory to agents working in a repo.

- [ ] Add agent-facing usage instructions.
- [ ] Add example memory files for each core type.
- [ ] Add example `brick memory add` payloads.
- [ ] Add example search workflow.
- [ ] Add example conflict workflow.
- [ ] Add README quickstart.

Exit criteria:

- [ ] A new agent can discover how to use Brick from repo files.
- [ ] Contributors can fork, run setup, search memory, and add memory.

### Phase 7 - Quality And Regression Tests

Goal: keep Brick from corrupting or poisoning repo memory.

- [ ] Add schema validation tests.
- [ ] Add secret scanner tests.
- [ ] Add PII scanner tests.
- [ ] Add hash stability tests.
- [ ] Add CLI JSON contract tests.
- [ ] Add rebuild/search tests.
- [ ] Add merge-driver fixture tests.
- [ ] Add redaction/tombstone tests.

Exit criteria:

- [ ] Core workflows are covered by fixtures.
- [ ] Regression tests catch malformed memory.
- [ ] Regression tests catch unsafe memory.
- [ ] Regression tests catch unsafe merges.

## Remaining Implementation Decisions

- [ ] Choose exact Python CLI framework, if any.
- [ ] Define exact local SQLite schema.
- [ ] Define exact content hash canonicalization algorithm.
- [ ] Choose exact secret detector implementation.
- [ ] Choose exact PII detector implementation.
- [ ] Define exact embedding endpoint request/response contract.
- [ ] Define exact conflict report JSON schema.
- [ ] Define exact `.gitattributes` merge-driver installation flow.

## V1 Non-Goals

- [x] Hosted service.
- [x] Product telemetry.
- [x] Realtime collaborative editing.
- [x] Required external vector database.
- [x] Required reranker model.
- [x] PR/issue/commit mining as a first ingest source.
- [x] Storing secrets or sensitive private data in memory.
