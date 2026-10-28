---
name: council
description: Have other models challenge the diff, then fix blockers.
version: 0.2.1
author: Preetham Kyanam
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [review, delegation]
    related_skills: [ship, blast, requesting-code-review]
---

# Council

## When to Use

The user asked other models to challenge a diff. Also use it when they asked for a hard look and the change touches auth, permissions, data loss, or concurrency.

An ordinary review is `/review` or bundled `requesting-code-review`. This skill is the panel. It is not `/moa`. `/moa` lets an aggregator act.

## What to do

Reviewers are read-only. Send them with `delegate_task`. Each reviewer uses a configured model other than the one that wrote the diff. Do not launch a second coding CLI. Stay on `delegate_task`. Do not hard-code a model name.

Default one reviewer. Use three only when the user asked for a panel, or the change touches auth, permissions, data loss, or concurrency.

If only one other provider is configured, say so and run one reviewer.

Cap the work at 3 rounds. For the high-risk cases above, cap at 5 while a blocker remains. A nit does not earn another round. Do not grow the diff to please a reviewer. Fix blockers only.

For each round, record the reviewer, the round number, and the outcome. Do not invent a score the model did not give.

Stop when no blocker remains, or when the cap is hit. Say which. Load `ship` only if the user asked for a pull request. Load `blast` if the remaining doubt is one fact outside a small diff.
