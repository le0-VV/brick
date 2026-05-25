---
id: "01KSEQJK108A4925ASDBWD26XF"
title: "Brick rebuild should validate every canonical Markdown memory before replacing the lo..."
type: "decision"
status: "active"
tags:
  - "migrated"
  - "implementation-choice"
  - "v1"
  - "index"
  - "sqlite"
created_at: "2026-05-25T04:51:30Z"
updated_at: "2026-05-25T04:51:30Z"
source:
  kind: "file"
  path: ".agents/MEMORIES.md"
  line: "148"
  section: "Settled v1 implementation choices"
evidence:
  -
    kind: "file_excerpt"
    path: ".agents/MEMORIES.md"
    line: "148"
    text: "`brick rebuild` should validate every canonical Markdown memory before replacing the local SQLite index and should fail without writing a new index when any memory is invalid or blocked."
confirm_public: true
content_hash: "sha256:33d201664f50adf0d2a29fc1b23c43f198bb07044e7fcdd6ad36f156264edd61"
---
Migrated from `.agents/MEMORIES.md` line 148 under `Settled v1 implementation choices`.

`brick rebuild` should validate every canonical Markdown memory before replacing the local SQLite index and should fail without writing a new index when any memory is invalid or blocked.
