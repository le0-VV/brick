---
id: "01KSEQJM6AXDYP2CY4JZFK4EZM"
title: "If embedding rebuild fails because the endpoint errors or returns malformed data, bri..."
type: "decision"
status: "active"
tags:
  - "migrated"
  - "implementation-choice"
  - "v1"
  - "embeddings"
  - "index"
created_at: "2026-05-25T04:51:32Z"
updated_at: "2026-05-25T04:51:32Z"
source:
  kind: "file"
  path: ".agents/MEMORIES.md"
  line: "162"
  section: "Settled v1 implementation choices"
evidence:
  -
    kind: "file_excerpt"
    path: ".agents/MEMORIES.md"
    line: "162"
    text: "If embedding rebuild fails because the endpoint errors or returns malformed data, `brick rebuild` should fail without replacing the previous index."
confirm_public: true
content_hash: "sha256:6453f6bb19b805cc87d28aeb40de78c4e56618506991ab7a39d1bc48c0009bc7"
---
Migrated from `.agents/MEMORIES.md` line 162 under `Settled v1 implementation choices`.

If embedding rebuild fails because the endpoint errors or returns malformed data, `brick rebuild` should fail without replacing the previous index.
