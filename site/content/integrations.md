---
title: Integrations
description: What HStack connects to Hermes. Skills are the default. Hooks, browser, GitHub, Context7, DeepWiki, and the helper scripts are opt-in.
---

Hermes already has a browser, a terminal, delegation, and a bundled GitHub skill. HStack does not replace those. Optional add-ons sit beside them and remove cleanly.

| Flag | Configured name | Removes cleanly |
|---|---|---|
| `browser` | `mcp_servers.hstack_playwright`, `bin/hstack-visdiff` | yes |
| `github` | `bin/hstack-pr` | yes |
| `docs` | `mcp_servers.hstack_context7` | yes |
| `search` | `mcp_servers.hstack_deepwiki` | yes |
| `perf` | `bin/hstack-bench` | yes |
| `test` | `bin/hstack-test` | yes |
| `security` | `bin/hstack-scan` | yes |
| `trail` | `bin/hstack-decisions` | yes |

`browser` points at `npx -y @playwright/mcp@0.0.83`. Hermes `browser_exec` stays the default browser. The add-on adds accessibility snapshots and a visual diff helper.

`github` wraps the GitHub CLI. Hermes docs prefer `gh` over the GitHub MCP server. `hstack-pr` takes one snapshot.

`docs` and `search` are URL-only. Context7 is `https://mcp.context7.com/mcp`. DeepWiki is `https://mcp.deepwiki.com/mcp`. No token is written. Local code search stays Hermes `search_files`.

`security` runs gitleaks or osv-scanner only when one of them is already on `PATH`. The installer does not fetch either binary. It also does not download Playwright.

Commands, dry-run, and the Windows `-File` form are on the [add-ons](/docs/addons) page.

## Hooks

Since 0.2.0, `--with hermes-hooks` registers shell hooks in `~/.hermes/config.yaml`. Nothing in the skills imports them, so a Hermes update that moves a Python API does not break the router. The guard blocks a short denylist of destructive terminal commands. The session hook appends a stamp when the session actually ends (`on_session_finalize`, not `on_session_end`, which fires every turn). The suggest hook can add context on the first turn only, and only an HStack playbook name. Hermes still asks before a new hook command runs, unless you pass `--accept-hooks` yourself.

## Outside stacks

HStack does not copy gstack, pstack, tstack, or gbrain into this repo, and it does not put them on `skills.external_dirs`. The registry is `skills/hstack/hstack/references/stacks.md`. The router reads it only after an HStack playbook. If one installed stack fits better, the reply is one line with the name and why, then a question. Nothing from that stack loads until the answer is yes. If it is not installed, the reply shows the install command and waits. Yes runs `hstack_stack.py install --yes`, which checks the pinned sha256 before extract. The files land in `$HERMES_HOME/hstack/external/<id>/<commit>/`. No is remembered for the session.

Detection does not execute the other project. gstack counts when a skill file is under the Hermes `skills/gstack` directory, or when `gstack-state-root.sh` is present under Claude or Codex skills. `~/.gstack` is state, not an install. pstack counts when `skills/poteto-mode/SKILL.md` is under `~/.cursor/plugins` or `~/.claude/plugins`. tstack counts when one skills directory holds both `leaving-pr-comments/SKILL.md` and `sol-loop/SKILL.md`. gbrain counts when `~/.gbrain/config.json` exists, when `GBRAIN_HOME` points at that config, or when `mcp_servers.gbrain` is already in the Hermes config. A `gbrain` binary on `PATH` is not enough.

Upstream inventories are [GStack](https://github.com/garrytan/gstack), [TStack](https://github.com/t3dotgg/tstack), [PStack](https://github.com/cursor/plugins/tree/main/pstack), and [GBrain](https://github.com/garrytan/gbrain). Hermes itself is documented at [hermes-agent.nousresearch.com](https://hermes-agent.nousresearch.com/docs/).
