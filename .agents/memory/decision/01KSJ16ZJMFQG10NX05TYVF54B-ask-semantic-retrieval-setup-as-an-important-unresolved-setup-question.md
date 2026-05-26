---
id: "01KSJ16ZJMFQG10NX05TYVF54B"
title: "Ask semantic retrieval setup as an important unresolved setup question"
type: "decision"
status: "active"
tags:
  - "brick"
  - "embeddings"
  - "semantic-retrieval"
  - "agent-workflow"
  - "setup"
created_at: "2026-05-26T11:37:39Z"
updated_at: "2026-05-26T11:37:39Z"
source:
  kind: "conversation"
  ref: "Current user instruction"
evidence:
  -
    kind: "quote"
    text: "instructions shoud tell agents that after first setup with no clear answer on whether to use semantic retrival or not, agents should always ask user whether to set it up as an important question"
related:
  - "01KSJ062GN5YQC7GB4CQXRN98V"
content_hash: "sha256:f49d57ebb7d4ea9153b0855b30e26193c613df5b01e800b8be34d2f9ce1d0928"
---
After first Brick setup, if the user has not clearly answered whether to use semantic retrieval on that machine, agents should ask whether to configure semantic retrieval as an important setup question. If the user opts in, agents should collect the embedding server URL and model name, write them to `.agents/brick/config.local.json`, and run `./brick rebuild`. If the user opts out, agents should explicitly say Brick search remains keyword-only.
