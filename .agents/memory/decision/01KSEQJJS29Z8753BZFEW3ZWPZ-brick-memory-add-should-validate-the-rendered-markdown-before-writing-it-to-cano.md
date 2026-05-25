---
id: "01KSEQJJS29Z8753BZFEW3ZWPZ"
title: "Brick memory add should validate the rendered Markdown before writing it to canonical..."
type: "decision"
status: "active"
tags:
  - "migrated"
  - "implementation-choice"
  - "v1"
  - "validation"
created_at: "2026-05-25T04:51:30Z"
updated_at: "2026-05-25T04:51:30Z"
source:
  kind: "file"
  path: ".agents/MEMORIES.md"
  line: "145"
  section: "Settled v1 implementation choices"
evidence:
  -
    kind: "file_excerpt"
    path: ".agents/MEMORIES.md"
    line: "145"
    text: "`brick memory add` should validate the rendered Markdown before writing it to canonical memory and return the same blocked/invalid JSON style as validation failures."
confirm_public: true
content_hash: "sha256:bdb9b8424fb48144ccbdc5c419c9148ef048e940eeffb95b1aae405640580289"
---
Migrated from `.agents/MEMORIES.md` line 145 under `Settled v1 implementation choices`.

`brick memory add` should validate the rendered Markdown before writing it to canonical memory and return the same blocked/invalid JSON style as validation failures.
