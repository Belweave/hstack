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
