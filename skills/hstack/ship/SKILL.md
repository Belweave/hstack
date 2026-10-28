---
name: ship
description: Open a short PR, watch CI, and merge only if told.
version: 0.2.1
author: Preetham Kyanam
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [git, pull-request]
    related_skills: [council, prove, github]
---

# Ship

## When to Use

The work should become a pull request, or an open pull request needs its checks watched. Load bundled `github` with `skill_view("github")` for `gh` command details. Do not copy those flags into this skill.

## Pull request

Lead with the problem the user hit, then the change. Do not open with a list of files. Match the repository's existing title style.

If you write a comment as the agent, say that an agent wrote it. Name the model and the user when you know them. Do not paste a stock disclaimer you did not write for this comment.

## CI

Watch checks with `gh pr checks`. If the user has left and asked the session to stay on it, use `/loop`. Do not write a sleep loop.

## Before you push

List any test, timeout, snapshot, or lint suppression the diff weakened. Show that list before you push.

Rebase with `--force-with-lease` against the commit SHA you just read. Do not force-push any other way.

## Stop line

Merge, enable auto-merge, or push the default branch only when the user explicitly said to send it. Otherwise stop when the pull request is green and the review comments that are real are fixed.

Do not bump a version, write a changelog, or guess a production host. Load `prove` first if the change has no check you ran. Load `council` only when that skill's own rules say to.
