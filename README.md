<p align="center">
  <img src="assets/hstack-wordmark.svg" alt="HStack" height="72">
  &nbsp;&nbsp;
  <img src="assets/hermes-agent.png" alt="Hermes Agent" height="72">
  <br>
  <em>Designed for Hermes Agent</em>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-111111" alt="License MIT"></a>
  <img src="https://img.shields.io/badge/Hermes%20Agent-compatible-111111" alt="Hermes Agent compatible">
  <a href="https://github.com/Belweave/hstack/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/Belweave/hstack/ci.yml?label=CI" alt="CI status"></a>
  <img src="https://img.shields.io/badge/skills-12-111111" alt="12 skills">
  <img src="https://img.shields.io/badge/idle%20tokens-~204-111111" alt="About 204 idle tokens">
</p>

> HStack is a community project made for the Hermes Agent community. It is not affiliated with, endorsed by, or an official product of Nous Research. Hermes Agent and the Nous Research logo belong to Nous Research and appear here only to show compatibility.

Twelve skills for Hermes Agent. Frame the job, shape the change, prove it, and open the pull request. The index stays small because only the router is required reading.

## Install

```sh
curl -fsSL https://hstack.sh/install | sh
```

From a checkout of this repo, `sh install.sh` installs that checkout. A second run replaces the HStack skills and leaves every other skill alone. Pass `--dry-run` to print the plan and write nothing.

Skills land in `~/.hermes/skills/hstack/`. Set `HERMES_HOME` if Hermes lives somewhere else. The shell script is for macOS and Linux. On Windows, copy `skills/hstack` into the Hermes skills directory.

## Why this instead of GStack

GStack's Hermes host puts every skill in the always-on index. HStack puts one router there and loads a single playbook when the task needs it. Counts use Hermes's estimator, `ceil(bytes / 4)`.

| | GStack on Hermes | HStack |
|---|---:|---:|
| Idle index | 1,182 | 204 |
| Planning load | 62,514 of SKILL.md, plus a ~5,600 preamble | 2,500 |
| All SKILL.md bodies | 420,401 | 8,550 |

The planning path is `hstack`, `reframe`, and `shape`. 2,500 against 62,514 is about 25× smaller. The idle index is about 6× smaller. HStack's body figures are the v0.1 ceilings. 204 is the index cost of these descriptions, including the `hstack` category header.

## Skills

- **hstack** — Pick the playbook for this task and load it.
- **reframe** — Name the real job before any plan or code.
- **shape** — Settle data shape and module boundaries first.
- **prove** — Show a failing check, then a passing one, on real behavior.
- **council** — Have other models challenge the diff, then fix blockers.
- **ship** — Open a short PR, watch CI, and merge only if told.
- **takeover** — Finish someone else's branch and keep their git credit.
- **modernize** — Rebase an old PR and decide if it still belongs.
- **blast** — Find what a small diff can break, and prove the safe fact.
- **swarm** — Fan out parallel subagents and return one report.
- **arena** — Try competing approaches, then keep the best parts.
- **principles** — Apply the design rule that should change this decision.

## Usage

```text
/hstack the export drops rows over 10 MB
/reframe
/ship
/council
```

`/hstack` is the one to remember. Name another skill when you already know which step you want. Playbooks live under `skills/hstack/hstack/references/` and load one at a time.

## Uninstall

```sh
curl -fsSL https://hstack.sh/install | sh -s -- --uninstall
```

From a checkout: `sh install.sh --uninstall`. This removes `skills/hstack` only when this installer created it.

---

HStack is a community project made for the Hermes Agent community. It is not affiliated with, endorsed by, or an official product of Nous Research. Hermes Agent and the Nous Research logo belong to Nous Research and appear here only to show compatibility.

MIT license. Copyright (c) 2026 Preetham Kyanam / belweave.
