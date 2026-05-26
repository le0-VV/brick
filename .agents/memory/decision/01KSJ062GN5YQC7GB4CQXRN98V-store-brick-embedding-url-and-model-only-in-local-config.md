---
id: "01KSJ062GN5YQC7GB4CQXRN98V"
title: "Store Brick embedding URL and model only in local config"
type: "decision"
status: "active"
tags:
  - "brick"
  - "embeddings"
  - "config"
  - "agent-workflow"
created_at: "2026-05-26T11:19:41Z"
updated_at: "2026-05-26T11:19:41Z"
source:
  kind: "conversation"
  ref: "Current user instruction"
evidence:
  -
    kind: "quote"
    text: "Embedding URL and model should always be inside the config file. Agent shoud ask user if they want to use embedding models for semantic retrival, opted-in users should provide the model and the server URL"
supersedes:
  - "01KSEQJD8HGZ4NPAXBZP1520KV"
  - "01KSEQJKKP85FF1K3SKTN9DNEV"
  - "01KSEQJKS0EWPZGZC8TMK88QPQ"
  - "01KSEQJKYA3RY3A9KED5BM8EPZ"
  - "01KSEQJM0YSP3DESMB43VYT0A9"
content_hash: "sha256:fee07e291c1692db4922c7aa90b0d347978832e61ae9ae64c8be404949a8e801"
---
Brick embedding endpoint URL and model must be configured in the device-local `.agents/brick/config.local.json` file. Agents setting up Brick should ask the user whether they want semantic retrieval for that machine; opted-in users must provide the embedding server URL and embedding model name so the agent can write `embedding.url` and `embedding.model` to local config before running `./brick rebuild`. Environment variables are not configuration sources for the embedding URL or model, though the API key value may still come from the environment variable named by `embedding.api_key_env`.
