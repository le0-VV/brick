---
id: "01KSEQJM90E4VTK249VAKTN9AN"
title: "Brick memory search should use hybrid scoring when indexed embeddings and a query emb..."
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
  line: "163"
  section: "Settled v1 implementation choices"
evidence:
  -
    kind: "file_excerpt"
    path: ".agents/MEMORIES.md"
    line: "163"
    text: "`brick memory search` should use hybrid scoring when indexed embeddings and a query embedding are available, combining deterministic keyword score with cosine similarity."
confirm_public: true
content_hash: "sha256:3d1ca17cd596c6e421d9728703e0b8471009b7084b12a65bf522f7bd4ff5ba1f"
---
Migrated from `.agents/MEMORIES.md` line 163 under `Settled v1 implementation choices`.

`brick memory search` should use hybrid scoring when indexed embeddings and a query embedding are available, combining deterministic keyword score with cosine similarity.
