---
id: "01KSEQJKPBG1WXWHQ9P6VVWNM5"
title: "Embedding API configuration is per-machine; repos using Brick should have a device-lo..."
type: "decision"
status: "active"
tags:
  - "migrated"
  - "implementation-choice"
  - "v1"
  - "agents"
  - "api"
  - "embeddings"
  - "retrieval"
created_at: "2026-05-25T04:51:31Z"
updated_at: "2026-05-25T04:51:31Z"
source:
  kind: "file"
  path: ".agents/MEMORIES.md"
  line: "156"
  section: "Settled v1 implementation choices"
evidence:
  -
    kind: "file_excerpt"
    path: ".agents/MEMORIES.md"
    line: "156"
    text: "Embedding API configuration is per-machine; repos using Brick should have a device-local config file that includes embedding server configuration, and Brick agent instructions should tell agents to check that local embedding config before relying on Brick retrieval."
confirm_public: true
content_hash: "sha256:0540032af415d025d8cbd21b2d809d72fe0c5fdd514be90b75045b302a70a182"
---
Migrated from `.agents/MEMORIES.md` line 156 under `Settled v1 implementation choices`.

Embedding API configuration is per-machine; repos using Brick should have a device-local config file that includes embedding server configuration, and Brick agent instructions should tell agents to check that local embedding config before relying on Brick retrieval.
