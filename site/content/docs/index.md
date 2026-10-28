---
title: Getting started
description: Twelve Hermes Agent skills. One router stays in the index. A playbook loads only when the task needs it.
---

HStack is twelve skills for Hermes Agent. Frame the job, shape the change, prove it, and open the pull request. The index stays small because only the router is required reading.

Skills land in `~/.hermes/skills/hstack/`. Set `HERMES_HOME` when Hermes lives somewhere else. A default install is skills only. Browser, GitHub, docs, search, benchmarks, tests, security scans, and the decision trail stay off until you name them.

`/hstack` is the one to remember. It loads a catalog, picks one playbook, and stops. Name another skill when you already know the step.

```text session
/hstack the export drops rows over 10 MB
/reframe
/ship
```

The planning path is `hstack`, `reframe`, and `shape`: 1,052 tokens, under 2% of GStack's planning load on Hermes. The idle index is 204 tokens. All twelve `SKILL.md` bodies are 3,907. Counts use Hermes's estimator, `ceil(bytes / 4)`.

Playbooks live under `skills/hstack/hstack/references/` and load one at a time. After that playbook, the router may read `stacks.md` and ask before using gstack, pstack, tstack, or gbrain. Hermes shell hooks stay off unless the install names `--with hermes-hooks`. The [skills index](/skills) lists each skill. [Parity](/parity) has one row for every GStack, TStack, and PStack feature that was inventoried.
