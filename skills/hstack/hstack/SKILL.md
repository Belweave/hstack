---
name: hstack
description: Pick the playbook for this task and load it.
version: 0.1.0
author: Preetham Kyanam
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [workflow, router]
    related_skills: [reframe, shape, prove, ship, systematic-debugging]
---

# HStack

## When to Use

Load this when a coding task starts and the user has not named another HStack skill. If they name `reframe`, `shape`, `prove`, `council`, `ship`, `takeover`, `modernize`, `blast`, `swarm`, `arena`, or `principles`, load that skill with `skill_view` and stop.

A one-line edit does not need a playbook.

## Route

Restate the goal in one sentence. If the evidence says the requested change is the wrong change, say so and stop.

Load one playbook and follow it. Do not load the others.

- Deciding what to build: `skill_view("hstack", "references/frame.md")`
- New or changed behavior: `skill_view("hstack", "references/feature.md")`
- Something is broken: `skill_view("hstack", "references/fix.md")`
- The diff needs a hard look: `skill_view("hstack", "references/check.md")`
- The work should become a pull request: `skill_view("hstack", "references/land.md")`

Say which playbook you loaded.

These jobs are not playbooks:

- A throwaway experiment: bundled `spike`.
- Worktree cleanup: `/worktree`.
- Multi-phase work: Kanban or `/goal`.
- Writing a skill: bundled `hermes-agent-skill-authoring` and `/learn`.
