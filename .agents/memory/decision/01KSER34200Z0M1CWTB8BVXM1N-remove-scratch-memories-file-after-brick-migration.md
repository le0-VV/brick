---
id: "01KSER34200Z0M1CWTB8BVXM1N"
title: "Remove scratch MEMORIES file after Brick migration"
type: "decision"
status: "active"
tags:
  - "memory"
  - "migration"
  - "canonical-memory"
  - "cleanup"
created_at: "2026-05-25T05:00:32Z"
updated_at: "2026-05-25T05:00:32Z"
source:
  kind: "conversation"
  ref: "user request after Brick memory migration"
evidence:
  -
    kind: "quote"
    text: "if memory is fully migrated, then [MEMORIES.md](.agents/MEMORIES.md) isn't needed"
confirm_public: true
content_hash: "sha256:80a02ea05a763455f14cfc65a34a637095ced279e154cc35314c840f35faa910"
---
After `.agents/MEMORIES.md` has been fully migrated into canonical Brick memory under `.agents/memory/`, `.agents/MEMORIES.md` is no longer needed and should be removed. Brick memory is now the canonical project memory store.
