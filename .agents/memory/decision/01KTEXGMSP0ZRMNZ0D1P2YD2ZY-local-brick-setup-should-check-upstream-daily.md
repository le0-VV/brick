---
id: "01KTEXGMSP0ZRMNZ0D1P2YD2ZY"
title: "Local Brick setup should check upstream daily"
type: "decision"
status: "active"
tags:
  - "setup"
  - "upstream"
  - "updates"
  - "installer"
  - "agents"
created_at: "2026-06-06T16:51:00Z"
updated_at: "2026-06-06T16:51:00Z"
source:
  kind: "conversation"
  ref: "user daily upstream update requirement"
evidence:
  -
    kind: "quote"
    text: "local brick setups should check and pull update from upstream brick every day"
content_hash: "sha256:b8826bccf4999ffe189f8606e99bf758414048ed35b54d2e563b09a8fab1a3e8"
---
Local Brick-enabled repositories should have setup logic that checks upstream Brick at most once per day and pulls updated Brick package files into the local repository when upstream files are available. The daily check should be local-state driven so normal setup does not repeatedly hit the network within the same day.
