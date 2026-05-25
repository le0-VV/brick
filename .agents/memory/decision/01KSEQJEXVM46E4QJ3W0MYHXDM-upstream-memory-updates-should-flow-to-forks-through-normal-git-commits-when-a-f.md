---
id: "01KSEQJEXVM46E4QJ3W0MYHXDM"
title: "Upstream memory updates should flow to forks through normal Git commits; when a fork..."
type: "decision"
status: "active"
tags:
  - "migrated"
  - "product-direction"
  - "forks"
  - "git"
  - "merge"
created_at: "2026-05-25T04:51:26Z"
updated_at: "2026-05-25T04:51:26Z"
source:
  kind: "file"
  path: ".agents/MEMORIES.md"
  line: "93"
  section: "Product direction: repo-local project memory system"
evidence:
  -
    kind: "file_excerpt"
    path: ".agents/MEMORIES.md"
    line: "93"
    text: "Upstream memory updates should flow to forks through normal Git commits; when a fork pulls, merges, or rebases from upstream, it receives the new memory files the same way it receives code changes."
confirm_public: true
content_hash: "sha256:0efdfe20a33dac83868d365cc7ed5e52b25f02697fac567ed29fad9c1504b003"
---
Migrated from `.agents/MEMORIES.md` line 93 under `Product direction: repo-local project memory system`.

Upstream memory updates should flow to forks through normal Git commits; when a fork pulls, merges, or rebases from upstream, it receives the new memory files the same way it receives code changes.
