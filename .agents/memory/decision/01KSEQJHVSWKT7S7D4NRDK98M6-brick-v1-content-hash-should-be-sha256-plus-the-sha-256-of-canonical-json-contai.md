---
id: "01KSEQJHVSWKT7S7D4NRDK98M6"
title: "Brick v1 content_hash should be sha256: plus the SHA-256 of canonical JSON containing..."
type: "decision"
status: "active"
tags:
  - "migrated"
  - "implementation-choice"
  - "v1"
  - "content-hash"
created_at: "2026-05-25T04:51:29Z"
updated_at: "2026-05-25T04:51:29Z"
source:
  kind: "file"
  path: ".agents/MEMORIES.md"
  line: "134"
  section: "Settled v1 implementation choices"
evidence:
  -
    kind: "file_excerpt"
    path: ".agents/MEMORIES.md"
    line: "134"
    text: "Brick v1 `content_hash` should be `sha256:` plus the SHA-256 of canonical JSON containing sorted frontmatter with `content_hash` and `updated_at` removed plus a normalized Markdown body."
confirm_public: true
content_hash: "sha256:5fc7f23192a63cc2db15ee47907284f1e57d22d5128e2ecc084f0fa8c040d1fe"
---
Migrated from `.agents/MEMORIES.md` line 134 under `Settled v1 implementation choices`.

Brick v1 `content_hash` should be `sha256:` plus the SHA-256 of canonical JSON containing sorted frontmatter with `content_hash` and `updated_at` removed plus a normalized Markdown body.
