---
name: hstack
description: Pick the playbook for this task and load it.
version: 0.2.1
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

Load the catalog with `skill_view("hstack", "references/routes.md")`. Pick one row. If the user only asked which playbook fits, name that file and stop.

Load that one playbook with `skill_view("hstack", "references/<file>")`. Do not load a second playbook. Say which file you loaded.

Then load `skill_view("hstack", "references/stacks.md")`. Do that only after the playbook. If no outside stack fits better, do not mention one. If one does, add one line with its name and why, and ask. At most one. Load nothing from it, and download nothing, until the user says yes. A no lasts for this session. Follow that file for the commands.
