---
id: "01KSEQJDGFY6YV4CCSJRXM9KX5"
title: "Stable content hashes may live in Markdown, but volatile index state such as embeddin..."
type: "decision"
status: "active"
tags:
  - "migrated"
  - "product-direction"
  - "embeddings"
  - "content-hash"
  - "index"
created_at: "2026-05-25T04:51:25Z"
updated_at: "2026-05-25T04:51:25Z"
source:
  kind: "file"
  path: ".agents/MEMORIES.md"
  line: "76"
  section: "Product direction: repo-local project memory system"
evidence:
  -
    kind: "file_excerpt"
    path: ".agents/MEMORIES.md"
    line: "76"
    text: "Stable content hashes may live in Markdown, but volatile index state such as embedding timestamps, model versions, chunk hashes, vector DB status, and index timestamps should live outside canonical Markdown."
confirm_public: true
content_hash: "sha256:78806b77a220b3f0254a1658c780edf629313f4ed826b664407cb7881758dbf0"
---
Migrated from `.agents/MEMORIES.md` line 76 under `Product direction: repo-local project memory system`.

Stable content hashes may live in Markdown, but volatile index state such as embedding timestamps, model versions, chunk hashes, vector DB status, and index timestamps should live outside canonical Markdown.
