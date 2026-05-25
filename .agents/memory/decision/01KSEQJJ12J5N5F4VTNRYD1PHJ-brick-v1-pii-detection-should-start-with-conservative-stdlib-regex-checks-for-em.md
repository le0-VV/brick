---
id: "01KSEQJJ12J5N5F4VTNRYD1PHJ"
title: "Brick v1 PII detection should start with conservative stdlib regex checks for emails..."
type: "decision"
status: "active"
tags:
  - "migrated"
  - "implementation-choice"
  - "v1"
  - "safety"
  - "validation"
created_at: "2026-05-25T04:51:29Z"
updated_at: "2026-05-25T04:51:29Z"
source:
  kind: "file"
  path: ".agents/MEMORIES.md"
  line: "136"
  section: "Settled v1 implementation choices"
evidence:
  -
    kind: "file_excerpt"
    path: ".agents/MEMORIES.md"
    line: "136"
    text: "Brick v1 PII detection should start with conservative stdlib regex checks for emails, phone-like numbers, address-like phrases, and two-word human-name-like phrases, with `confirm_public: true` as the validation escape hatch."
confirm_public: true
content_hash: "sha256:ac692d5a8f82ed3a7bde1f58732d759d39b6c1192d4aab45ffbbf22851acdf6f"
---
Migrated from `.agents/MEMORIES.md` line 136 under `Settled v1 implementation choices`.

Brick v1 PII detection should start with conservative stdlib regex checks for emails, phone-like numbers, address-like phrases, and two-word human-name-like phrases, with `confirm_public: true` as the validation escape hatch.
