---
name: prove
description: Show a failing check, then a passing one, on real behavior.
version: 0.2.1
author: Preetham Kyanam
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [testing, verification]
    related_skills: [test-driven-development, dogfood, ship]
---

# Prove

## When to Use

The change is supposed to be done, or the user asked for a report of what to run. Load this after `shape`, or after bundled `systematic-debugging`.

## What to do

Done means a check you ran. Show it failing for the right reason, then passing.

Name the surface you exercised: the CLI, the API, the job, the webhook, or the page. A unit test that never calls that surface is not this check. Run the check with `terminal`.

Report-only mode lists the check, the command, and the expected failure. Do not edit product code in that mode.

A performance claim names the limiter, how many times you repeated it, and the error. Otherwise it is not a result. An unvetted number is not a result.

Do not restate bundled skills. Load them with `skill_view`:

- A bug with a cheap unit test: `test-driven-development`.
- Browser exploration of a page: `dogfood`. Use `browser_exec` only as that skill directs.

When the passing check is real, stop. Opening a pull request is `ship`, and only when the user asks.
