---
name: shape
description: Settle data shape and module boundaries first.
version: 0.2.1
author: Preetham Kyanam
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design, planning]
    related_skills: [reframe, prove, arena, principles]
---

# Shape

## When to Use

Before code crosses a function boundary, or while a design choice is still open. Load `reframe` first if the job, the user, and the smallest version are not named.

## What to do

Name these before writing the behavior:

- The data the change stores or passes.
- The types, and which states should be impossible to represent.
- The module that owns the rule. One structure for a rule that would otherwise be copied.

Stay in the conversation while the code is filled in. If a plan file is wanted, call `/plan`. Do not reimplement `/plan`. Do not keep a second planner in this skill.

Two checks, then lock the shape:

1. Compare a second shape before locking the first. If the user wants those attempts built, load `arena`. A throwaway experiment they will delete is bundled `spike`, not `arena`.
2. Stop if a module owns a rule it does not use, or if a caller has to know the callee's internals to use it correctly.

Load `principles` when a design choice is contested. Name the decision the rule changes. Do not recite the rules.

Load `prove` once there is behavior to check.
