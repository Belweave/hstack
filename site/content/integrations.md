---
title: Integrations
description: What HStack connects to Hermes. Skills are the default. Browser, GitHub, Context7, DeepWiki, and the helper scripts are opt-in.
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

Commands, dry-run, and the Windows `-File` form are on the [add-ons](/docs/addons) page. Upstream inventories are [GStack](https://github.com/garrytan/gstack), [TStack](https://github.com/t3dotgg/tstack), and [PStack](https://github.com/cursor/plugins/tree/main/pstack). Hermes itself is documented at [hermes-agent.nousresearch.com](https://hermes-agent.nousresearch.com/docs/).
