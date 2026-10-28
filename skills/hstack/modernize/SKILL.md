---
name: modernize
description: Rebase an old PR and decide if it still belongs.
version: 0.2.1
author: Preetham Kyanam
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [git, pull-request]
    related_skills: [ship]
---

# Modernize

## When to Use

An old pull request should be updated onto current main. Do not use this skill to merge it.

## What to do

Read the pull request and the current default branch. Rebase. Show a range-diff with `git range-diff`.

Then say which one of these is true:

- The patch still matches the idea.
- The idea stands and the patch does not.
- The idea should be closed.

Recommend close when that is the case. Do not close. Do not merge.

Force-push only with `--force-with-lease` pinned to the head you read before the rebase.

Load `ship` only if the user still wants the updated branch open as a pull request.
