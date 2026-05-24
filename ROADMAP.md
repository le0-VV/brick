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
- [x] Repositories can be initialized for Brick through a curlable installer
  script published by Brick.
- [x] `brick setup` owns local agent-instruction installation and conservative
  `AGENTS.md` handling.
- [x] Brick is free for everyone, including companies and commercial projects.
- [x] The licensing model must keep Brick available to indie users.
- [x] Indie projects that use Brick and later become commercial should keep
  the same permissive usage rights.
- [x] Brick monetization is donation-supported, not based on commercial license
  gates.
- [x] V1 uses Apache-2.0 as the free-for-all permissive license.

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

- [x] Create `.agents/brick/pyproject.toml`.
- [x] Create one setup entrypoint under `.agents/brick/`.
- [x] Create `.agents/brick/bin/brick` as the actual executable.
- [x] Create a repo-root `brick` symlink that uses a relative path to
  `.agents/brick/bin/brick`.
- [x] Create `.agents/brick/.venv/` as Brick's owned virtual environment.
- [x] Create `.agents/brick/index/` for generated index state.
- [x] Create `.agents/brick/conflicts/` for generated conflict reports.
- [x] Gitignore `.agents/brick/.venv/`.
- [x] Gitignore `.agents/brick/index/`.
- [x] Gitignore `.agents/brick/conflicts/`.
- [x] Create `.agents/memory/` as canonical memory root.
- [x] Organize memory files by type folder under `.agents/memory/`.
- [x] Use ULID-slug filenames for memory files.

Target structure:

```text
.agents/
  brick/
    pyproject.toml
    bin/
      brick
    setup.py or setup.sh
    .venv/             # generated, gitignored
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

- [x] Store every memory as one Markdown file with YAML frontmatter.
- [x] Allow memory bodies to be freeform Markdown.
- [x] Do not require a duplicate `# Title` heading in the Markdown body.
- [x] Require `id`.
- [x] Require `title`.
- [x] Require `type`.
- [x] Require `status`.
- [x] Require `tags`.
- [x] Require `created_at`.
- [x] Require `updated_at`.
- [x] Require `content_hash`.
- [x] Require `source.kind`.
- [x] Require at least one `evidence` item.
- [x] Allow optional `supersedes`.
- [x] Allow optional `related`.
- [x] Validate `supersedes` and `related` entries as memory ULIDs when present.

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

Content hash policy:

- [x] Calculate `content_hash` from normalized memory content.
- [x] Exclude `content_hash` itself from the hash input.
- [x] Exclude `updated_at` from the hash input.
- [x] Define the exact canonicalization algorithm before implementation.

## Type-Specific Schema Checklist

- [x] Support lightweight structured fields for `command` memories.
- [x] Support lightweight structured fields for `routine` memories.
- [x] Support lightweight structured fields for `skill` memories.
- [x] Keep type-specific detail human-readable in Markdown even when structured
  fields exist.

`command` fields:

- [x] Support `command`.
- [x] Support `cwd`.
- [x] Support `when_to_use`.
- [x] Support `expected_output`.
- [x] Support `failure_notes`.

Example:

```yaml
command: "uv run pytest"
cwd: "."
when_to_use: "Run Python tests before committing."
expected_output: "Tests pass."
failure_notes: "If dependencies are missing, run brick setup."
```

`routine` and `skill` fields:

- [x] Support `steps`.
- [x] Support `prerequisites`.
- [x] Support `verify`.

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

- [x] Parse YAML frontmatter.
- [x] Parse Markdown body.
- [x] Require all core schema fields.
- [x] Validate plain ULID IDs without a `mem_` prefix.
- [x] Validate `type`.
- [x] Validate `status`.
- [x] Validate timestamps.
- [x] Validate `content_hash`.
- [x] Require `source.kind`.
- [x] Require at least one `evidence` item.
- [x] Reject memories without enough evidence.
- [x] Reject unsupported durable memory.
- [x] Reject low-confidence durable memory.
- [x] Reject non-JSON input to `brick memory add`.
- [x] Return structured JSON for validation failures.

Secret and PII checks:

- [x] Block obvious API keys before writing memory.
- [x] Block private keys before writing memory.
- [x] Block tokens before writing memory.
- [x] Block passwords before writing memory.
- [x] Block possible names until explicitly confirmed.
- [x] Block possible emails until explicitly confirmed.
- [x] Block possible phone numbers until explicitly confirmed.
- [x] Block possible addresses until explicitly confirmed.
- [x] Support candidate-level `confirm_public: true` JSON confirmation.
- [x] Require explicit confirmation before saving public human names.
- [x] Require explicit confirmation before saving public email addresses.
- [x] Ensure committed memory is safe for the repository's intended audience.

Redaction:

- [x] Provide a redaction flow for sensitive content that slips through.
- [x] Replace leaked text with `[REDACTED]`.
- [x] Create a tombstone or evidence note explaining why redaction happened.
- [x] Rebuild the local index after redaction.

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

Entrypoint rules:

- [x] Put the actual executable at `.agents/brick/bin/brick`.
- [x] Expose a repo-root `brick` symlink using a relative path.
- [x] Use Python stdlib `argparse` for the v1 CLI.

Command surface:

- [x] Implement `brick setup`.
- [x] Implement `brick memory add`.
- [x] Implement `brick memory redact`.
- [x] Implement `brick memory validate [path]`.
- [x] Implement `brick memory search "query"`.
- [x] Implement `brick rebuild`.
- [x] Implement `brick merge-driver ...`.
- [x] Implement `brick conflicts list`.
- [x] Implement `brick conflicts export <id>`.

Input and output rules:

- [x] Keep memory operations under `brick memory`.
- [x] Make `brick memory add` read JSON from stdin by default.
- [x] Make `brick memory add` reject non-JSON input.
- [x] Make `brick memory add` return JSON by default.
- [x] Make `brick memory search` return JSON by default.
- [x] Make `brick memory validate` return JSON by default.
- [x] Make `brick conflicts list` return JSON by default.
- [x] Make `brick conflicts export` return JSON by default.
- [x] Allow `brick setup` to print readable text by default.
- [x] Allow `brick rebuild` to print readable text by default.
- [x] Add `--pretty` for JSON-oriented commands in v1.

Proposed `brick memory add` input contract:

```json
{
  "title": "Decision to use hybrid retrieval",
  "type": "decision",
  "tags": ["retrieval", "architecture"],
  "body": "Markdown body for the memory.",
  "source": {
    "kind": "conversation",
    "ref": "chat thread, commit, file, issue, or manual note"
  },
  "evidence": [
    {
      "kind": "quote",
      "text": "Quoted user text or concrete artifact reference."
    }
  ],
  "confirm_public": false,
  "supersedes": [],
  "related": [],
  "fields": {}
}
```

- [x] Finalize the `brick memory add` JSON input contract.
- [x] Map `fields` into type-specific frontmatter keys after validation.
- [x] Reject unknown top-level fields unless a compatibility policy is added.

## Dependency Checklist

- [x] Assume Python is available.
- [x] Prefer `uv` for dependency setup.
- [x] Fall back to `pip`.
- [x] Keep Brick dependencies under `.agents/brick/pyproject.toml`.
- [x] Use a Brick-owned virtual environment.
- [x] Put the Brick-owned virtual environment at `.agents/brick/.venv/`.
- [x] Do not use the host project's main virtual environment.
- [x] Provide one setup entrypoint.
- [x] Make Brick commands run setup or resolve dependencies when possible.
- [x] Emit actionable setup/dependency messages when automatic setup cannot
  proceed.

## Local Index And Retrieval Checklist

Index:

- [x] Store generated index state under `.agents/brick/index/`.
- [x] Keep generated index state out of Git.
- [x] Use simple local files and/or SQLite for v1.
- [x] Do not require Chroma, Qdrant, or another external vector database in v1.
- [x] Implement `brick rebuild`.
- [x] Rebuild deterministically from canonical Markdown memory files.
- [x] Keep stable `content_hash` in frontmatter.
- [x] Keep volatile index state outside canonical Markdown.

SQLite index schema:

- [x] Store the generated database at `.agents/brick/index/brick.sqlite3`.
- [x] Use a `metadata` table keyed by `key` with string `value` entries for
  schema version, rebuild timestamp, and memory count.
- [x] Use a `memories` table keyed by memory ULID with relative path, title,
  type, status, tags JSON, source JSON, evidence JSON, content hash, summary,
  body, search text, and updated timestamp.
- [x] Use an `embeddings` table keyed by memory ULID with content hash, model,
  dimensions, and vector JSON for generated semantic state.

Embedding:

- [x] Use `BRICK_EMBEDDING_URL` as the standard embedding endpoint environment
  variable.
- [x] Use an OpenAI-compatible embedding endpoint contract for v1.
- [x] Define model configuration as `BRICK_EMBEDDING_MODEL`.
- [x] Support a local system-wide embedding service.
- [x] Support API-backed embeddings.
- [x] Fall back to keyword search when no embedding endpoint or API is
  configured.
- [x] Clearly report when semantic search is unavailable.

Retrieval:

- [x] Use hybrid retrieval when embeddings are available.
- [x] Do not require reranking in v1.
- [x] Ignore superseded memories by default.
- [x] Allow explicit retrieval of superseded memories.
- [x] Return summary in retrieval context packages.
- [x] Return source path in retrieval context packages.
- [x] Return status/trust information in retrieval context packages.
- [x] Return evidence in retrieval context packages.
- [x] Return a full-text link in retrieval context packages.

## Merge Driver Checklist

Core merge behavior:

- [x] Implement `brick merge-driver`.
- [x] Add `.gitattributes` guidance for memory files.
- [x] Have `brick setup` install or configure the merge driver.
- [x] Auto-merge exact duplicate memory IDs.
- [x] Auto-merge exact duplicate content.
- [x] Do not silently merge semantically similar memories.
- [x] Create structured conflict/review items for semantic similarity.
- [ ] Allow agents to propose merged memories.
- [x] Require human acceptance before Brick writes a final merged memory.
- [x] Merge deterministic frontmatter fields automatically when non-conflicting.
- [x] Use normal Git-style text merge behavior for Markdown body edits.
- [x] Block when the same structured frontmatter field changes differently on
  both sides.
- [x] Create a conflict report when structured frontmatter conflicts.
- [x] Union distinct entries for append-only fields such as `evidence`.

Conflict reports:

- [x] Store conflict reports under `.agents/brick/conflicts/`.
- [x] Keep conflict reports gitignored by default.
- [x] Implement `brick conflicts list`.
- [x] Implement `brick conflicts export <id>`.
- [x] Make conflict reports exportable for PR discussion or review.
- [x] Use the following conflict report JSON schema as the v1 baseline.

Proposed conflict report shape:

```json
{
  "schema_version": 1,
  "id": "conflict-01JX3Y7Q8M9N2P4R6S8T0V1W",
  "created_at": "2026-05-24T00:00:00Z",
  "kind": "semantic_similarity",
  "severity": "review_required",
  "merge": {
    "base_ref": "base",
    "ours_ref": "ours",
    "theirs_ref": "theirs"
  },
  "memories": [
    {
      "side": "ours",
      "id": "01JX3Y1Y8H6TR4Y3Q38K1W9P2A",
      "path": ".agents/memory/decision/example.md",
      "title": "Example memory",
      "type": "decision",
      "status": "active",
      "content_hash": "sha256:..."
    }
  ],
  "similarity": {
    "method": "embedding_or_keyword",
    "score": 0.91
  },
  "conflicts": [
    {
      "field": "body",
      "reason": "semantically_similar_memory"
    }
  ],
  "appendable_unions": {
    "evidence": []
  },
  "proposed_resolution": null,
  "required_action": "human_review"
}
```

## Phase Roadmap Checklist

### Phase 0 - Specification Baseline

Goal: capture product decisions in a form that can drive implementation.

- [x] Create `ROADMAP.md`.
- [x] Capture initial schema contract.
- [x] Capture initial command surface.
- [x] Capture initial repo layout.
- [x] Capture initial safety policy.
- [x] Capture initial merge-driver policy.
- [x] Choose Apache-2.0 as the v1 license.
- [x] Add Apache-2.0 `LICENSE`.
- [ ] Keep the roadmap checklist updated as implementation discovers concrete
  details.

Exit criteria:

- [x] Product boundaries are clear.
- [x] V1 scope is narrow enough to build.
- [x] Remaining unknowns are implementation details, not product identity.

### Phase 1 - Skeleton And Setup

Goal: make Brick runnable from a cloned repo.

- [x] Add `.agents/brick/pyproject.toml`.
- [x] Add setup entrypoint.
- [x] Add `.agents/brick/bin/brick`.
- [x] Add repo-root relative `brick` symlink.
- [x] Add Brick-owned venv handling.
- [x] Put Brick-owned venv state under `.agents/brick/.venv/`.
- [x] Implement `brick setup`.
- [x] Add basic CLI argument parser.
- [x] Use Python stdlib `argparse`.
- [x] Add curlable repository bootstrap script.
- [x] Add gitignore entries for generated index state.
- [x] Add gitignore entries for generated conflict reports.
- [x] Add gitignore entry for `.agents/brick/.venv/`.

Exit criteria:

- [x] A fresh clone can run `brick setup`.
- [x] Commands fail with actionable dependency/setup messages.
- [x] No generated state is accidentally tracked.

### Phase 2 - Schema And Validation

Goal: make canonical Markdown memory safe and consistent.

- [x] Implement YAML frontmatter parser.
- [x] Implement Markdown memory loader.
- [x] Implement schema validator.
- [x] Implement ULID generation.
- [x] Implement ULID validation.
- [x] Implement content hash calculation.
- [x] Exclude `content_hash` and `updated_at` from hash input.
- [x] Implement secret scanner.
- [x] Implement PII block-until-confirmed flow.
- [x] Implement `confirm_public` handling in JSON candidates.
- [x] Implement structured validation output.
- [x] Implement `brick memory validate`.

Exit criteria:

- [x] Invalid memory is rejected with machine-readable reasons.
- [x] Missing evidence is rejected.
- [x] Obvious secrets are blocked.
- [x] Possible PII is blocked until confirmed.

### Phase 3 - Memory Write Path

Goal: let agents add memory without writing files directly.

- [x] Implement `brick memory add`.
- [x] Define JSON stdin input contract.
- [x] Support the v1 candidate JSON shape documented in this roadmap.
- [x] Implement slug generation.
- [x] Implement type-folder file creation.
- [x] Implement type-specific field validation.
- [x] Implement `active` status handling.
- [x] Implement `superseded` status handling.
- [x] Implement `tombstone` status handling.
- [x] Implement `redacted` status handling.
- [x] Implement human-readable `--pretty` output.

Exit criteria:

- [x] Agents can submit valid JSON and Brick writes Markdown.
- [x] Non-JSON input is rejected.
- [x] Written files pass validation.
- [x] Generated filenames are stable and reviewable.

### Phase 4 - Index And Search

Goal: give agents useful retrieval immediately, even without embeddings.

- [x] Implement local index storage under `.agents/brick/index/`.
- [x] Implement SQLite or simple local file index.
- [x] Implement `brick rebuild`.
- [x] Implement keyword fallback search.
- [x] Implement optional embedding endpoint integration through
  `BRICK_EMBEDDING_URL`.
- [x] Implement OpenAI-compatible embedding requests.
- [x] Implement `brick memory search`.
- [x] Implement retrieval context package JSON.

Exit criteria:

- [x] Search works without embeddings.
- [x] Semantic search activates when an endpoint is configured.
- [x] Missing semantic capability is reported clearly.
- [x] Rebuild is deterministic from Markdown.

### Phase 5 - Merge Driver And Conflict Review

Goal: make fork/upstream memory collaboration safe.

- [x] Implement `brick merge-driver`.
- [x] Add `.gitattributes` guidance.
- [x] Configure the merge driver from `brick setup`.
- [x] Implement exact duplicate auto-merge.
- [x] Implement structured frontmatter merge.
- [x] Implement evidence union behavior.
- [x] Implement semantic similarity detection hook.
- [x] Implement conflict report generation.
- [x] Implement `brick conflicts list`.
- [x] Implement `brick conflicts export`.

Exit criteria:

- [x] Exact duplicates do not create noisy conflicts.
- [x] Semantic similarity never silently rewrites memory.
- [x] Agents can read conflict reports and propose fixes.
- [x] Users can export conflict reports for PR review.

### Phase 6 - Agent Instructions And Examples

Goal: make Brick self-explanatory to agents working in a repo.

- [x] Add agent-facing usage instructions.
- [x] Add Brick `AGENTS.md` template.
- [x] Add `AGENTS.md` backup flow for repositories with existing agent
  instructions.
- [x] Add first-task instruction requiring user-reviewed merge of backed-up
  instructions and Brick instructions.
- [x] Add example memory files for each core type.
- [x] Add example `brick memory add` payloads.
- [x] Add blocked unsafe-memory example.
- [x] Add example search workflow.
- [x] Add example conflict workflow.
- [x] Add README quickstart.

Exit criteria:

- [x] A new agent can discover how to use Brick from repo files.
- [x] Contributors can fork, run setup, search memory, and add memory.

### Phase 7 - Quality And Regression Tests

Goal: keep Brick from corrupting or poisoning repo memory.

- [x] Add schema validation tests.
- [x] Add secret scanner tests.
- [x] Add PII scanner tests.
- [x] Add hash stability tests.
- [x] Add CLI JSON contract tests.
- [x] Add rebuild/search tests.
- [x] Add embedding endpoint and hybrid search tests.
- [x] Add merge-driver fixture tests.
- [x] Add docs and example workflow tests.
- [x] Add redaction/tombstone tests.

Exit criteria:

- [ ] Core workflows are covered by fixtures.
- [ ] Regression tests catch malformed memory.
- [ ] Regression tests catch unsafe memory.
- [ ] Regression tests catch unsafe merges.

## Remaining Implementation Decisions

- [x] Choose exact license: Apache-2.0.
- [x] Define exact local SQLite schema.
- [x] Define exact content hash canonicalization algorithm.
- [x] Choose exact secret detector implementation.
- [x] Choose exact PII detector implementation.
- [x] Define exact OpenAI-compatible embedding endpoint request/response
  details.
- [x] Decide whether to standardize `BRICK_EMBEDDING_MODEL`.
- [x] Refine conflict report fields during implementation without changing the
  accepted v1 baseline shape.
- [x] Define exact `.gitattributes` and local Git config mutations performed by
  `brick setup`.
- [x] Define exact `AGENTS.md` backup filename and merge-instruction text.

## V1 Non-Goals

- [x] Hosted service.
- [x] Product telemetry.
- [x] Realtime collaborative editing.
- [x] Required external vector database.
- [x] Required reranker model.
- [x] PR/issue/commit mining as a first ingest source.
- [x] Storing secrets or sensitive private data in memory.
