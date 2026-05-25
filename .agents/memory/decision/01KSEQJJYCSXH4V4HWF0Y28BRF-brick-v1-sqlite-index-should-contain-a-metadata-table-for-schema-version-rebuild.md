---
id: "01KSEQJJYCSXH4V4HWF0Y28BRF"
title: "Brick v1 SQLite index should contain a metadata table for schema/version/rebuild fact..."
type: "decision"
status: "active"
tags:
  - "migrated"
  - "implementation-choice"
  - "v1"
  - "evidence"
  - "content-hash"
  - "index"
  - "schema"
  - "sqlite"
  - "tags"
created_at: "2026-05-25T04:51:30Z"
updated_at: "2026-05-25T04:51:30Z"
source:
  kind: "file"
  path: ".agents/MEMORIES.md"
  line: "147"
  section: "Settled v1 implementation choices"
evidence:
  -
    kind: "file_excerpt"
    path: ".agents/MEMORIES.md"
    line: "147"
    text: "Brick v1 SQLite index should contain a `metadata` table for schema/version/rebuild facts and a `memories` table keyed by memory ULID, with relative path, title, type, status, tags JSON, source JSON, evidence JSON, content hash, summary, body, search text, and updated timestamp."
confirm_public: true
content_hash: "sha256:21f7b6fff679b769e338b251d34ced6b50dc88d352a75e895e65ab5e8f9438de"
---
Migrated from `.agents/MEMORIES.md` line 147 under `Settled v1 implementation choices`.

Brick v1 SQLite index should contain a `metadata` table for schema/version/rebuild facts and a `memories` table keyed by memory ULID, with relative path, title, type, status, tags JSON, source JSON, evidence JSON, content hash, summary, body, search text, and updated timestamp.
