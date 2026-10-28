---
title: Add-ons
description: Optional HStack add-ons for browser, GitHub, docs, search, perf, test, security, and a decision trail. Off unless you pass --with.
---

A default install is skills only. Pass `--with` to turn on helpers and MCP entries. The installer does not download Playwright, gitleaks, or osv-scanner.

:::tabs
:::tab macOS / Linux
```sh install.sh
sh install.sh --with browser,github,docs,search,perf,test,security,trail
sh install.sh --dry-run --with browser
sh install.sh --uninstall --with browser
```
:::tab Windows
```powershell install.ps1
powershell -ExecutionPolicy Bypass -File .\install.ps1 --with browser,github,docs,search,perf,test,security,trail
powershell -ExecutionPolicy Bypass -File .\install.ps1 --dry-run --with browser
powershell -ExecutionPolicy Bypass -File .\install.ps1 --uninstall --with browser
```
:::

Helpers are copied to `$HERMES_HOME/hstack/bin`. MCP entries use an `hstack_` prefix in `config.yaml`. `--dry-run` writes nothing. `--uninstall` without `--with` removes the skills and every add-on this installer created.

| Flag | What you get |
|---|---|
| `browser` | Playwright MCP at `@playwright/mcp@0.0.83`, plus `hstack-visdiff` |
| `github` | `hstack-pr`, one `gh` snapshot |
| `docs` | Context7 MCP, URL only |
| `search` | DeepWiki MCP, URL only |
| `perf` | `hstack-bench` |
| `test` | `hstack-test` |
| `security` | `hstack-scan`, only if gitleaks or osv-scanner is already installed |
| `trail` | `hstack-decisions` |

The browser server is `npx -y @playwright/mcp@0.0.83` under `mcp_servers.hstack_playwright`. Docs and search store a URL and no token: `https://mcp.context7.com/mcp` and `https://mcp.deepwiki.com/mcp`.

## Hermes hooks

Hooks are separate from the add-ons above. A default install adds none. `--with hermes-hooks` registers three shell hooks. Each shim is a few lines and calls `hstack_hook.py` under `$HERMES_HOME/hstack/hooks`. The skills do not import that module.

| Flag | Event | What it does |
|---|---|---|
| `hermes-hooks-guard` | `pre_tool_call` matcher `terminal`, `fail_closed` | Blocks a fork bomb, a power command, `mkfs`, `dd` onto a disk device, and `rm -rf` of a filesystem root |
| `hermes-hooks-save` | `on_session_finalize` | Appends time, session id, and platform to `session-log.tsv`. It does not write the user message |
| `hermes-hooks-suggest` | `pre_llm_call`, first turn only | Adds one line naming an HStack playbook. It does not name another stack |

`pre_command` cannot block, so the guard does not use it. The installer backs up `config.yaml` before a real change and leaves every other hook in place. It does not set `hooks_auto_accept` and it does not write Hermes's hook allowlist. A second run that would write the same text does not take another backup. `--uninstall --with hermes-hooks-guard` removes that entry only.
