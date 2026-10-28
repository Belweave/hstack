---
name: blast
description: Find what a small diff can break, and prove the safe fact.
version: 0.2.0
author: Preetham Kyanam
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [review, risk]
    related_skills: [prove]
---

# Blast

## When to Use

The diff is small and the user does not trust it. The question is what it can break outside the lines it changes.

## What to do

Name what the diff can break outside itself: callers, stored data, jobs, or the next request.

Pick the one fact that would make the change safe. Prove that fact by running the code with `terminal`. A written argument is not the proof.

Load `prove` for the failing check and the passing one. Do not restate it.
