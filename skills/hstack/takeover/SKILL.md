---
name: takeover
description: Finish someone else's branch and keep their git credit.
version: 0.2.1
author: Preetham Kyanam
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [git, review]
    related_skills: [modernize, ship]
---

# Takeover

## When to Use

The user pointed at a pull request, branch, or thread for you to finish. `/resume` is for this agent's own sessions. This skill is for someone else's work.

## What to do

Read the review and the later corrections before you edit. Use `read_file` on the diff and the thread.

Keep the original authors on the commits and in the pull request body. Use names and emails you verified from existing commits. Do not guess either.

Do not defend the existing diff. New fixes are new commits. Do not overwrite unrelated work.

Load `modernize` if the branch is stale against the default branch. Load `ship` when it is ready to open or update a pull request.
