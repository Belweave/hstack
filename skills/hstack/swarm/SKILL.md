---
name: swarm
description: Fan out parallel subagents and return one report.
version: 0.2.0
author: Preetham Kyanam
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [delegation]
    related_skills: [prove]
---

# Swarm

## When to Use

The task splits into slices that do not write the same files. This is not `arena`. Swarm partitions the work. Arena duplicates the same brief.

## What to do

Send one `delegate_task` batch. Stay inside `delegation.max_concurrent_children`. That cap is 10 unless the user raised it. A larger batch is an error, not something to work around.

Each child gets the goal, its slice, and the check that slice must run. Children do not watch pull requests and do not spawn their own panels.

Races are allowed when the slices are competing proofs of the same question.

Return one report. Keep the findings, not each child's transcript. Load `prove` for the check each slice owes.
