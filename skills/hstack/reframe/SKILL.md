---
name: reframe
description: Name the real job before any plan or code.
version: 0.2.0
author: Preetham Kyanam
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [planning, framing]
    related_skills: [shape, principles]
---

# Reframe

## When to Use

The user is deciding what to build, or the request names a solution before it names the job. The frame playbook loads this skill.

## What to do

Do not write code. Do not open a plan file. There is no separate spec skill. If they want a written plan after the frame is settled, load `shape`, which calls `/plan`.

Push until three things are named in the user's words:

1. The job. What changes for whom when this is done.
2. The user. Who hits the problem, and what they do today.
3. The smallest version. The least change that solves that job.

Disagree in the open. If the request solves a different job than the one they described, say so. If the evidence says the requested change is the wrong change, stop. Do not keep that change on the list as the recommendation.

Use `clarify` when a preference would change the design. Do not ask about facts you can read from the repo with `read_file` or `search_files`.

When the three names are stable, stop. The output is one short restatement. Do not expand it into a spec.

Load `principles` only when a design rule is what the disagreement is about. Apply the rule that changes the decision. Do not recite the list.
