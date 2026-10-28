# PARITY

Phase 1 inventory. Every GStack, TStack, and PStack feature in the tables below has one row. Nothing in those tables is optional. A later build may only mark a row done by filling its target. This file is the gate.

Measured from the checkouts named in [RESEARCH.md](RESEARCH.md), on 28 October 2026:

| Source | Commit | What was read |
|---|---|---|
| [garrytan/gstack](https://github.com/garrytan/gstack) | `6f27f0c269cb33ad60b300ec10df63c2b9f296ba` | 61 skill directories, root `SKILL.md`, `connect-chrome` symlink, `bin/` (175 files), `browse/sections/command-list.md`, `hosts/`, hooks, `scripts/` entry points |
| [t3dotgg/tstack](https://github.com/t3dotgg/tstack) | `1085050f3baed1ac724caa4a8166145fb2ac88af` | 9 skills, `skills/babysit-pr/scripts/pr-wait`, four `agents/openai.yaml` files |
| [cursor/plugins](https://github.com/cursor/plugins) `pstack/` | `c742dd61706fbacc1b95f1a20b7b988cf096ce6c` | 58 skills, 23 playbooks, Benny automations, agents, `watch-pr`, statechart scripts |
| [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | `ee7e0f517232fb619c72e49d7e648436bddc598e` | Skills, plugins, MCP, hooks, memory, cron, delegation, browser, terminal backends |

All three stacks are MIT. This repo still does not copy their skill text, word lists, or scripts. No `NOTICE` file until a substantial portion is included. The helpers in the build that follows this file are original.

## How a row is typed

Each row has one disposition:

| Disposition | Meaning |
|---|---|
| `skill` | An existing HStack skill is the behavior. |
| `routed-reference` | A file under `skills/hstack/hstack/references/` loads on demand and then names the skills or tools. |
| `plugin-or-tool` | A Hermes tool, bundled skill, or opt-in MCP server does the job. |
| `helper-script` | An original script under `bin/`, installed only with an addon flag. |
| `skip` | Deliberately not built. The reason says why, and where the underlying job goes if it is real. |

`on_demand` is `0` for a skip, `skill:<name>` when invoking that skill directly, or a route slug. A route slug is the upper bound of what `skill_view` loads when that route fires: the `hstack` skill, `references/routes.md`, the one playbook, and every `skill_view` that playbook names, including branches that return early. One extra hop adds `skill_view` targets inside an HStack skill body. Ship loads bundled `github` on that hop. Idle cost is only the index. It does not include those files.

Measured tokens use Hermes's estimator, `ceil(utf-8 bytes / 4)` with CJK at one token per character (`estimate_tokens_rough` in `agent/model_metadata.py`). Bundled skills use the frozen counts below, from hermes-agent `ee7e0f517232fb619c72e49d7e648436bddc598e`. A direct skill row costs only that skill's body.

## Idle cost

Twelve skills, descriptions unchanged, category header included. **204** index tokens. Keep that number. If a new always-on skill is added, this section must name the tokens and why a route was not enough.

Idle is 204 for every session. The next table is the extra cost when a route fires.

| Stack | Idle index |
|---|---:|
| HStack v0.1 | 204 |
| GStack on Hermes, prefixed names | 1,182 |
| PStack if copied | 1,256 |
| TStack if copied | 152 |
| All three indexed | 2,590 |

## Route budget

Each playbook stays at or under its budget. `references/routes.md` is the catalog the router loads. The catalog measures 390 tokens. The `hstack` skill body stays at or under 700 tokens. Idle stays 204 because none of these files are index rows.

| route | when it fires | budget playbook tokens | measured playbook tokens | measured route upper bound |
|---|---|---:|---:|---:|
| frame | Deciding what to build | 400 | 90 | 1445 |
| feature | New or changed behavior | 450 | 121 | 1444 |
| fix | Something is broken | 350 | 123 | 7191 |
| check | A diff needs a hard look | 400 | 145 | 3562 |
| land | The work should become a pull request | 300 | 69 | 1726 |
| refactor | Behavior-preserving restructure | 500 | 142 | 5776 |
| design | Visual critique, layout, developer friction | 500 | 209 | 5725 |
| qa | Reproduce on a real surface, or report only | 500 | 215 | 3356 |
| perf | A number, a trace of cost, a slow path | 500 | 164 | 1142 |
| trace | A live symptom or a captured profile | 500 | 110 | 757 |
| retro | Weekly retro or a quality snapshot | 500 | 92 | 1351 |
| docs | Docs, README, release notes, PDF | 500 | 121 | 4901 |
| security | Auth, injection, secrets, dependencies | 500 | 142 | 1183 |
| explain | How or why a subsystem works | 500 | 121 | 768 |
| memory | Save or restore working context | 500 | 106 | 753 |
| author | Write or edit a skill | 500 | 136 | 4446 |
| prose | Plain wording, strip tells | 500 | 110 | 11569 |
| experiment | Throwaway prototype | 500 | 87 | 2915 |
| parallel | Slices or competing attempts | 500 | 98 | 1204 |
| overnight | Finish while the user is away | 500 | 181 | 2563 |
| pickup | Resume, pause, or catch up | 500 | 109 | 992 |
| worktree | Clean worktrees | 500 | 62 | 709 |
| spec | Written spec or a phased plan | 500 | 143 | 1498 |
| eval | Test a prompt or skill change | 500 | 95 | 742 |
| deploy | Deploy or watch a host the user named | 500 | 146 | 1803 |
| browse | Drive a page, screenshot, scrape | 500 | 266 | 3076 |
| safety | Destructive commands or a write boundary | 500 | 117 | 764 |
| decisions | A reviewable decision trail | 500 | 93 | 740 |
| triage | Triage or reproduce a report | 500 | 79 | 726 |
| types | Types, including TypeScript | 500 | 114 | 1398 |
| verify | A property a test cannot reach | 500 | 141 | 788 |
| diagram | A diagram | 500 | 91 | 2196 |

Direct skill loads, measured from the skill files in this tree. A `skill:<name>` row costs this many tokens and does not load a playbook:

| skill | measured body tokens |
|---|---:|
| hstack | 257 |
| reframe | 363 |
| shape | 345 |
| prove | 331 |
| council | 394 |
| ship | 398 |
| takeover | 236 |
| modernize | 220 |
| blast | 180 |
| swarm | 236 |
| arena | 223 |
| principles | 637 |

Bundled Hermes skills a route may load, measured at `ee7e0f517232fb619c72e49d7e648436bddc598e`. These are not HStack idle cost. They load only when a playbook names them.

| bundled skill | path | tokens |
|---|---|---:|
| systematic-debugging | `skills/software-development/systematic-debugging/SKILL.md` | 3515 |
| test-driven-development | `skills/software-development/test-driven-development/SKILL.md` | 2575 |
| requesting-code-review | `skills/software-development/requesting-code-review/SKILL.md` | 2196 |
| dogfood | `skills/software-development/dogfood/SKILL.md` | 2163 |
| spike | `skills/software-development/spike/SKILL.md` | 2181 |
| simplify-code | `skills/software-development/simplify-code/SKILL.md` | 3674 |
| hermes-agent-skill-authoring | `skills/software-development/hermes-agent-skill-authoring/SKILL.md` | 3663 |
| github | `skills/software-development/github/SKILL.md` | 612 |
| humanizer | `skills/creative/humanizer/SKILL.md` | 8616 |
| architecture-diagram | `skills/creative/architecture-diagram/SKILL.md` | 1458 |
| design-md | `skills/creative/design-md/SKILL.md` | 2120 |
| pdf | `skills/productivity/pdf/SKILL.md` | 3123 |

The prose route's upper bound includes humanizer (8,616). That is a load cost, not an index cost. Copying a shorter word list into the index would be the nerf. Loading the bundled skill when the route fires is the feature.

## What Hermes already gives us

Citations are paths in the hermes-agent checkout above. Docs also live at `https://hermes-agent.nousresearch.com/docs/`.

**Skills.** Directories with `SKILL.md`. Index row is `name` plus a description clipped at 60 characters (`SKILL_PROMPT_DESC_LIMIT` in `agent/skill_utils.py`). `skills_list` and `skill_view` are `tools/skills_tool.py`. Three levels: index, full `SKILL.md`, then one linked file. Docs: `website/docs/user-guide/features/skills.md`.

**Plugins.** `website/docs/user-guide/features/plugins.md` and `plugins/plugin_loader.py`. A directory in `~/.hermes/plugins/` with `plugin.yaml` can register tools, hooks, slash commands, skills, memory backends, and terminal backends. Bundled plugins live in `plugins/` (browser, memory, delegation, cron_providers, kanban, platforms, and others). Project-local `.hermes/plugins/` is not loaded by the gateway.

**MCP.** `website/docs/user-guide/features/mcp.md`. Servers live under `mcp_servers` in `~/.hermes/config.yaml`. The approved catalog is `optional-mcps/<name>/manifest.yaml`. `hermes mcp install <name>` installs one. GitHub is intentionally not in the catalog. The docs say the bundled `github` skill plus `gh` is the better integration.

**Hooks.** `website/docs/user-guide/features/hooks.md`. Four systems: gateway hooks (`~/.hermes/hooks/<name>/HOOK.yaml` plus `handler.py`), plugin hooks (`ctx.register_hook`), shell hooks in `config.yaml`, and outbound webhooks. HStack does not install a hook by default. The safety route points at approvals instead.

**Memory.** `website/docs/user-guide/features/memory.md` and `memory-providers.md`. `MEMORY.md` (2,200 characters) and `USER.md` (1,375) via the `memory` tool. `session_search` finds older sessions. Providers plug in under `plugins/memory/`.

**Cron and loops.** `website/docs/user-guide/features/cron.md` (`cronjob_manage`, implementation in `cron/`). `website/docs/user-guide/features/loops.md` and `goals.md` cover `/loop` and `/goal`. That is the scheduler. Skills must not sleep in a loop.

**Subagents.** `website/docs/user-guide/features/delegation.md`. `delegate_task` in the `delegation` toolset (`toolsets.py`). Children do not see the parent transcript. Default cap is 10. `/review` is one reviewer. `/moa` is a mixture of agents whose aggregator may act. Council stays read-only.

**Browser.** `website/docs/user-guide/features/browser.md`. `browser_exec` runs Python over CDP with helpers `new_tab`, `goto_url`, `js`, `fill_input`, `capture_screenshot`, and others. Companions: `browser_cdp`, `browser_dialog`, `browser_vault`. Local Chromium by default. `/browser connect` attaches to the user's browser. Real-profile mode is opt-in. Cloud browsers and Lightpanda are separate backends (`plugins/browser`).

**Terminal.** `website/docs/developer-guide/terminal-environment-plugin.md`. Built-in backends in `tools/environments/`: `local.py`, `docker.py`, `ssh.py`, `modal.py`, `managed_modal.py`, `daytona.py`, `vercel_sandbox.py`. Select with `terminal.backend`. Plugins register more through `ctx.register_terminal_environment_provider`.

**Other tools a route may name.** From `toolsets.py`: `terminal`, `read_file`, `write_file`, `patch`, `search_files`, `web_search`, `web_extract`, `clarify`, `execute_code`, `vision_analyze`, `cronjob_manage`, `todo_list`. Kanban tools exist when a kanban worker is running (`website/docs/user-guide/features/kanban.md`).

## Open-source tools worth opting into

Ranked by what a Hermes session gains against setup cost. Only free tools, or MIT / Apache-2.0 code. Nothing here is installed by a default `install.sh`.

| Rank | Tool | License | Setup | Why it is or is not an addon |
|---|---|---|---|---|
| 1 | Hermes `browser_exec` | MIT (hermes-agent) | Already in Hermes | Default browser. No addon required. |
| 2 | `@playwright/mcp` 0.0.83 | Apache-2.0, `microsoft/playwright-mcp` | `npx`, no key | Addon `browser`. Accessibility snapshots and traces beside `browser_exec`. |
| 3 | `gh` | MIT | User installs the GitHub CLI | Addon `github` wraps it. Hermes docs reject the GitHub MCP in favor of `gh`. |
| 4 | Context7 MCP | Free anonymous HTTP, catalogued at `optional-mcps/context7/manifest.yaml` | No key, rate limited | Addon `docs`. URL `https://mcp.context7.com/mcp`. We configure it. We do not vendor the server. |
| 5 | DeepWiki MCP | Free anonymous HTTP, `optional-mcps/deepwiki/manifest.yaml` | No key | Addon `search`. Public repo questions. URL `https://mcp.deepwiki.com/mcp`. Local code search stays `search_files`. |
| 6 | gitleaks | MIT | Only if already on `PATH` | Addon `security` runs it when present. The installer does not download it. |
| 7 | osv-scanner | Apache-2.0 | Only if already on `PATH` | Same security addon. Dependency scan. Not downloaded. |
| 8 | Pillow | HPND | Optional import | Visual diff helper uses it when installed. Otherwise it shells out to `odiff` (MIT) or ImageMagick (Apache-2.0) if present. |
| 9 | hyperfine | MIT | Not required | The perf addon is an original repeat runner so we do not depend on hyperfine. |
| 10 | ast-grep | MIT | Not required | `search_files` covers repo search. Structural search stays a user install. |

Rejected:

- Semgrep's engine is LGPL-2.1, not MIT or Apache-2.0. The hosted MCP also needs the user's OAuth. Not an addon.
- GitHub's MCP server is MIT, and Hermes still tells us to use `gh`. Not an addon.
- Ubicloud, Browserbase, Vercel, and other paid preview or VM products. Preview URLs already posted on a pull request are read with `gh`. We do not deploy.
- The upstream browser daemon, cookie importers, GBrain, and the iOS debug bridge. Those are products. The routes name the Hermes equivalent or they are skips.

## Addons

Default install copies skills only.

| Flag | What it configures | Removes cleanly |
|---|---|---|
| `browser` | `mcp_servers.hstack_playwright` pointing at `npx -y @playwright/mcp@0.0.83`, plus `bin/hstack-visdiff` | yes |
| `github` | `bin/hstack-pr` | yes |
| `docs` | `mcp_servers.hstack_context7` URL only, no token | yes |
| `search` | `mcp_servers.hstack_deepwiki` URL only, no token | yes |
| `perf` | `bin/hstack-bench` | yes |
| `test` | `bin/hstack-test` | yes |
| `security` | `bin/hstack-scan` | yes |
| `trail` | `bin/hstack-decisions` | yes |

`install.sh --with browser,github --dry-run` prints the plan and writes nothing. `--uninstall` removes skills and every addon this installer created. `--uninstall --with browser` removes only that addon. `install.ps1` accepts the same flags for Windows. WSL can run `install.sh`.

## Feature table

`id` is `source:kind:item`. The checker rejects an empty row, an empty cell, a duplicate id, a disposition outside the five names above, or a measured route cost that does not match the files.

520 rows. helper-script 15, plugin-or-tool 3, routed-reference 260, skill 67, skip 175.

| id | source | item | kind | disposition | target | on_demand | reason |
|---|---|---|---|---|---|---|---|
| gstack:skill:SKILL.md | gstack | SKILL.md | skill | skill | skills/hstack/hstack/SKILL.md | skill:hstack | The suite router. HStack's only always-on entry is the hstack skill, which loads one playbook. |
| gstack:skill:autoplan | gstack | autoplan | skill | routed-reference | references/spec.md | spec | Frame, then shape, then a written plan via /plan. One playbook, not four review bodies. |
| gstack:skill:benchmark | gstack | benchmark | skill | routed-reference | references/perf.md | perf | A performance claim needs a limiter, repeats, and the error. The perf route is that bar. |
| gstack:skill:benchmark-models | gstack | benchmark-models | skill | skip | none | 0 | Cross-model bakeoff of this stack's own skills. Hermes already switches models with /model and delegation.model. |
| gstack:skill:browse | gstack | browse | skill | routed-reference | references/browse.md | browse | Drive a page with browser_exec. The opt-in browser addon adds Playwright MCP and a visual diff helper. |
| gstack:skill:canary | gstack | canary | skill | routed-reference | references/deploy.md | deploy | Watch a URL the user named. Do not guess a production host or a deploy vendor. |
| gstack:skill:captain | gstack | captain | skill | routed-reference | references/parallel.md | parallel | Parallel slices return one report via swarm. A merge-train product is not built. |
| gstack:skill:careful | gstack | careful | skill | routed-reference | references/safety.md | safety | Destructive commands are blocked by Hermes approvals, not by a warning-only skill. |
| gstack:skill:codex | gstack | codex | skill | skill | skills/hstack/council/SKILL.md | skill:council | A second opinion is council through delegate_task. The skill does not shell out to another CLI. |
| gstack:skill:connect-chrome | gstack | connect-chrome | skill | routed-reference | references/browse.md | browse | Symlink of open-gstack-browser. Same job: a session browser, which Hermes already launches. |
| gstack:skill:context-restore | gstack | context-restore | skill | routed-reference | references/memory.md | memory | Restore notes with the memory tool and session_search. No second context store. |
| gstack:skill:context-save | gstack | context-save | skill | routed-reference | references/memory.md | memory | Save a short note with the memory tool. MEMORY.md and USER.md stay inside Hermes caps. |
| gstack:skill:cso | gstack | cso | skill | routed-reference | references/security.md | security | Review the diff for auth, injection, and secrets. Optional local scanners only if they are already installed. |
| gstack:skill:design-consultation | gstack | design-consultation | skill | routed-reference | references/design.md | design | Name the visual job and capture the page. A design-system file is the bundled design-md skill, loaded only if asked. |
| gstack:skill:design-html | gstack | design-html | skill | routed-reference | references/design.md | design | Implement the settled layout in the repo's existing markup. No separate HTML dialect. |
| gstack:skill:design-motion | gstack | design-motion | skill | routed-reference | references/design.md | design | Show before and after screenshots. An MP4 is produced only when the user already has an encoder. |
| gstack:skill:design-review | gstack | design-review | skill | routed-reference | references/design.md | design | Screenshot, accessibility tree, spacing and hierarchy. Fixes wait until the user wants them. |
| gstack:skill:design-shotgun | gstack | design-shotgun | skill | routed-reference | references/design.md | design | Several layouts is the arena skill, pointed at from the design route. No comparison-board product. |
| gstack:skill:deslop-shared-libs | gstack | deslop-shared-libs | skill | routed-reference | references/refactor.md | refactor | Recommend one shared structure, then stop unless asked to edit. Bundled simplify-code is the cleanup pass. |
| gstack:skill:devex-review | gstack | devex-review | skill | routed-reference | references/design.md | design | Run the real command or page and name the friction. Do not interview the user with a long questionnaire. |
| gstack:skill:diagram | gstack | diagram | skill | routed-reference | references/diagram.md | diagram | Load the bundled architecture-diagram skill when a diagram is the deliverable. |
| gstack:skill:document-generate | gstack | document-generate | skill | routed-reference | references/docs.md | docs | Write the missing doc in tutorial, how-to, reference, or explanation form. Keep it short. |
| gstack:skill:document-release | gstack | document-release | skill | routed-reference | references/docs.md | docs | Check that the user-facing docs match the change about to ship. Do not invent a docs pipeline. |
| gstack:skill:eval-plan | gstack | eval-plan | skill | routed-reference | references/eval.md | eval | Write the check before changing a prompt or a skill, then compare blinded outputs. |
| gstack:skill:freeze | gstack | freeze | skill | routed-reference | references/safety.md | safety | Stay inside the directory the user named. Hermes's write sandbox is the enforcement. |
| gstack:skill:gstack-upgrade | gstack | gstack-upgrade | skill | skip | none | 0 | Re-running install.sh is the upgrade. A background update checker would be a second product. |
| gstack:skill:guard | gstack | guard | skill | routed-reference | references/safety.md | safety | Same safety route as careful and freeze. Hermes blocks the command and the write. |
| gstack:skill:health | gstack | health | skill | routed-reference | references/retro.md | retro | A quality snapshot is git history, the test result, and open pull requests. No dashboard service. |
| gstack:skill:investigate | gstack | investigate | skill | routed-reference | references/fix.md | fix | No fix before a cause. The fix route loads bundled systematic-debugging, then prove. |
| gstack:skill:ios-clean | gstack | ios-clean | skill | skip | none | 0 | Removes that stack's iOS debug package from an app. HStack does not ship that package, so there is nothing to strip. |
| gstack:skill:ios-design-review | gstack | ios-design-review | skill | routed-reference | references/design.md | design | Visual review of a screen the user can already build. A device debug bridge is not installed. |
| gstack:skill:ios-fix | gstack | ios-fix | skill | routed-reference | references/fix.md | fix | Reproduce and fix with the fix route. Run a simulator only when the user already configured one. |
| gstack:skill:ios-qa | gstack | ios-qa | skill | routed-reference | references/qa.md | qa | Exercise the real surface. Live-device tapping through a private debug bridge is not bundled. |
| gstack:skill:ios-sync | gstack | ios-sync | skill | skip | none | 0 | Regenerates that stack's iOS bridge templates. Those templates are not part of HStack. |
| gstack:skill:land-and-deploy | gstack | land-and-deploy | skill | routed-reference | references/deploy.md | deploy | Merge only if the user said to send, then watch the URL they named. No host auto-detection. |
| gstack:skill:landing-report | gstack | landing-report | skill | routed-reference | references/retro.md | retro | Read-only queue via gh pr list. The retro route writes the snapshot in the reply. |
| gstack:skill:learn | gstack | learn | skill | routed-reference | references/memory.md | memory | A repeated lesson uses /learn or the memory tool. No private learnings database. |
| gstack:skill:make-pdf | gstack | make-pdf | skill | routed-reference | references/docs.md | docs | A markdown PDF loads the bundled pdf skill. Publication layout is that skill, not a port. |
| gstack:skill:modernize | gstack | modernize | skill | skill | skills/hstack/modernize/SKILL.md | skill:modernize | Rebase onto current main, show a range-diff, and recommend keep, rework, or close. Do not close. |
| gstack:skill:office-hours | gstack | office-hours | skill | skill | skills/hstack/reframe/SKILL.md | skill:reframe | Name the job, the user, and the smallest version. Do not write code in that pass. |
| gstack:skill:open-gstack-browser | gstack | open-gstack-browser | skill | routed-reference | references/browse.md | browse | Hermes launches Chromium for browser_exec. The sidebar extension is not required. |
| gstack:skill:pair-agent | gstack | pair-agent | skill | skip | none | 0 | Remote tunnel that lets another machine drive the local browser. That is a credentialed product. Local browsing stays on the browse route. |
| gstack:skill:plan-ceo-review | gstack | plan-ceo-review | skill | skill | skills/hstack/reframe/SKILL.md | skill:reframe | Product challenge before code. Same skill as the frame route. |
| gstack:skill:plan-design-review | gstack | plan-design-review | skill | routed-reference | references/design.md | design | Design questions that change the layout, then screenshots. Not a scored rubric file. |
| gstack:skill:plan-devex-review | gstack | plan-devex-review | skill | routed-reference | references/design.md | design | Developer-experience friction is part of the design route. Ask only what the repo cannot answer. |
| gstack:skill:plan-eng-review | gstack | plan-eng-review | skill | skill | skills/hstack/shape/SKILL.md | skill:shape | Data, types, and module ownership before code crosses a function boundary. |
| gstack:skill:plan-tune | gstack | plan-tune | skill | routed-reference | references/spec.md | spec | Do not ask a question a command can answer. Preferences use clarify. No tuning profile store. |
| gstack:skill:qa | gstack | qa | skill | routed-reference | references/qa.md | qa | Reproduce on the real surface, then prove the fix. Report-only is the same route with no product edits. |
| gstack:skill:qa-only | gstack | qa-only | skill | routed-reference | references/qa.md | qa | The qa route's report-only mode lists the check and does not edit product code. |
| gstack:skill:retro | gstack | retro | skill | routed-reference | references/retro.md | retro | Weekly retro from git log, CI, and open pull requests. No metrics service. |
| gstack:skill:review | gstack | review | skill | routed-reference | references/check.md | check | Independent review plus the weakened-test list in ship. The long specialist army is not copied. |
| gstack:skill:scrape | gstack | scrape | skill | routed-reference | references/browse.md | browse | Extract page content with browser_exec or web_extract. Do not import another browser's cookies to do it. |
| gstack:skill:setup-browser-cookies | gstack | setup-browser-cookies | skill | routed-reference | references/browse.md | browse | Logged-in browsing is Hermes real-profile mode, which the user turns on. Cookie databases are not copied. |
| gstack:skill:setup-deploy | gstack | setup-deploy | skill | routed-reference | references/deploy.md | deploy | Ask for the host or the workflow. Detecting a vendor from the repo and deploying to it is refused. |
| gstack:skill:setup-gbrain | gstack | setup-gbrain | skill | routed-reference | references/memory.md | memory | Hermes memory is the store. Do not install a second database or register another memory MCP from this route. |
| gstack:skill:ship | gstack | ship | skill | skill | skills/hstack/ship/SKILL.md | skill:ship | Open a short pull request, watch checks, merge only when told. No version bump and no changelog factory. |
| gstack:skill:skillify | gstack | skillify | skill | routed-reference | references/author.md | author | Turn a repeated workflow into a skill with /learn. Do not auto-save a scraped flow. |
| gstack:skill:spec | gstack | spec | skill | routed-reference | references/spec.md | spec | Settle the frame, then shape, then /plan if a file is wanted. Five-phase spec ceremony is the spec route in short. |
| gstack:skill:sync-gbrain | gstack | sync-gbrain | skill | routed-reference | references/memory.md | memory | Refresh memory from what this session learned. Do not rewrite a host instruction file to point at another brain. |
| gstack:skill:test-audit | gstack | test-audit | skill | routed-reference | references/check.md | check | Name tests that do not protect a caller-visible behavior. Principle 20 is the rule. Do not delete them until asked. |
| gstack:skill:ubicloud | gstack | ubicloud | skill | skip | none | 0 | Ephemeral 16-vCPU VMs are a paid cloud product. Heavy commands stay on the user's Hermes terminal backend. |
| gstack:skill:unfreeze | gstack | unfreeze | skill | routed-reference | references/safety.md | safety | The user clears a write limit by saying so. The safety route does not invent a second freeze flag. |
| gstack:skill:write-skill | gstack | write-skill | skill | routed-reference | references/author.md | author | Author and edit skills with the bundled authoring skill and /learn. Size checks live in scripts/check_skills.py. |
| pstack:skill:poteto-mode | pstack | poteto-mode | skill | skill | skills/hstack/hstack/SKILL.md | skill:hstack | The entry point. HStack routes, then loads one playbook. |
| pstack:skill:poteto-help | pstack | poteto-help | skill | skill | skills/hstack/hstack/SKILL.md | skill:hstack | If the user only wants the route name, the router names it and stops. |
| pstack:skill:setup-pstack | pstack | setup-pstack | skill | skip | none | 0 | Writes a Cursor model-rule file. Hermes uses /model, delegation.model, and auxiliary.review. |
| pstack:skill:sharpen | pstack | sharpen | skill | skill | skills/hstack/reframe/SKILL.md | skill:reframe | Restate a sharper job and stop. Do not do the task in that pass. |
| pstack:skill:in-your-own-words | pstack | in-your-own-words | skill | skill | skills/hstack/reframe/SKILL.md | skill:reframe | Play the goal back in the user's words before any code. |
| pstack:skill:figure-it-out | pstack | figure-it-out | skill | routed-reference | references/spec.md | spec | When no route fits, write a short plan with a check and a stop line, then follow it. |
| pstack:skill:how | pstack | how | skill | routed-reference | references/explain.md | explain | Walk the subsystem from the code and the git history. |
| pstack:skill:why | pstack | why | skill | routed-reference | references/explain.md | explain | Explain the cause from the code and history. Connected evidence tools are used only if they are already on. |
| pstack:skill:teach | pstack | teach | skill | routed-reference | references/explain.md | explain | One explanation a newcomer can follow. Diagrams only when they change the explanation. |
| pstack:skill:recall | pstack | recall | skill | routed-reference | references/memory.md | memory | Rebuild recent context with session_search and memory. |
| pstack:skill:ketchup | pstack | ketchup | skill | routed-reference | references/pickup.md | pickup | Summarize this chat since the last user message, including what is waiting on them. |
| pstack:skill:ketchup-video | pstack | ketchup-video | skill | skip | none | 0 | A subtitled slide video needs a renderer we do not ship. The text catch-up is the pickup route. |
| pstack:skill:bro | pstack | bro | skill | routed-reference | references/prose.md | prose | Restate the last reply in plain words. The prose route loads the bundled humanizer when the wording is the job. |
| pstack:skill:unslop | pstack | unslop | skill | routed-reference | references/prose.md | prose | Strip tells from writing by loading the bundled humanizer. No word list is copied. |
| pstack:skill:no-comments | pstack | no-comments | skill | routed-reference | references/check.md | check | Comments that only narrate are part of review. Load requesting-code-review. Do not spawn a persona. |
| pstack:skill:technical-writing | pstack | technical-writing | skill | routed-reference | references/docs.md | docs | Docs, READMEs, and pull request text follow the docs route. One standard, not four stacked guides. |
| pstack:skill:typescript-best-practices | pstack | typescript-best-practices | skill | routed-reference | references/types.md | types | TypeScript-specific habits that change a decision, on top of the principles skill. |
| pstack:skill:architect | pstack | architect | skill | skill | skills/hstack/shape/SKILL.md | skill:shape | Settle types and module shape before code crosses a function boundary. |
| pstack:skill:arena | pstack | arena | skill | skill | skills/hstack/arena/SKILL.md | skill:arena | Same brief, several attempts, keep the best parts. |
| pstack:skill:swarm | pstack | swarm | skill | skill | skills/hstack/swarm/SKILL.md | skill:swarm | Different slices, one report, on delegate_task. |
| pstack:skill:interrogate | pstack | interrogate | skill | skill | skills/hstack/council/SKILL.md | skill:council | Other models try to break the diff. Keep findings a run can prove. |
| pstack:skill:blast-radius | pstack | blast-radius | skill | skill | skills/hstack/blast/SKILL.md | skill:blast | Name what a small diff can break and prove the one fact that makes it safe. |
| pstack:skill:tdd | pstack | tdd | skill | plugin-or-tool | bundled test-driven-development | fix | A cheap failing test first is the bundled test-driven-development skill. The fix route points at it. |
| pstack:skill:benchmark-checklist | pstack | benchmark-checklist | skill | routed-reference | references/perf.md | perf | Refuse an unvetted number. Limiter, repeats, errors, and whether the work happened. |
| pstack:skill:automate-me | pstack | automate-me | skill | routed-reference | references/author.md | author | A personal workflow becomes a skill through /learn when the user asks. No mode file is written automatically. |
| pstack:skill:reflect | pstack | reflect | skill | routed-reference | references/author.md | author | After a long task, offer one skill edit. Apply it only if the user wants it saved. |
| pstack:skill:correct | pstack | correct | skill | routed-reference | references/author.md | author | A repeated correction becomes a check, a lint, or a script. Principle 24. Docs are the last resort. |
| pstack:skill:show-me-your-work | pstack | show-me-your-work | skill | helper-script | bin/hstack-decisions | decisions | Append a decision row. The trail addon installs the helper. Without it, the decisions route still writes the row. |
| pstack:skill:make-bot-ui | pstack | make-bot-ui | skill | skip | none | 0 | A page whose buttons wake a hosted bot over a webhook and a private network. Hermes has no that surface. |
| pstack:skill:create-verification-skill | pstack | create-verification-skill | skill | routed-reference | references/verify.md | verify | If the app has no scripted check, write the smallest project check that fails for a real bug. Do not generate a framework. |
| pstack:skill:maintain-verification-skill | pstack | maintain-verification-skill | skill | routed-reference | references/verify.md | verify | When a check drifts from the app, fix the check in the same change as the behavior it protects. |
| pstack:skill:create-formal-verification-skill | pstack | create-formal-verification-skill | skill | routed-reference | references/verify.md | verify | State the property a test cannot reach and the illegal state. Run a model checker only if the user already has one. |
| pstack:skill:maintain-formal-verification-skill | pstack | maintain-formal-verification-skill | skill | routed-reference | references/verify.md | verify | Update the property when the code changes, rerun, and say whether the failure is the model or the code. |
| pstack:skill:statechart | pstack | statechart | skill | routed-reference | references/verify.md | verify | Draw the user-visible states in mermaid when that picture changes a decision. The TLA corpus is not installed. |
| pstack:skill:principle-attack-the-premise | pstack | principle-attack-the-premise | skill | skill | skills/hstack/principles/SKILL.md | skill:principles | One of the 24 principle skills. Collapsed into the principles skill so the index pays one row. |
| pstack:skill:principle-boundary-discipline | pstack | principle-boundary-discipline | skill | skill | skills/hstack/principles/SKILL.md | skill:principles | One of the 24 principle skills. Collapsed into the principles skill so the index pays one row. |
| pstack:skill:principle-build-the-lever | pstack | principle-build-the-lever | skill | skill | skills/hstack/principles/SKILL.md | skill:principles | One of the 24 principle skills. Collapsed into the principles skill so the index pays one row. |
| pstack:skill:principle-encode-lessons-in-structure | pstack | principle-encode-lessons-in-structure | skill | skill | skills/hstack/principles/SKILL.md | skill:principles | One of the 24 principle skills. Collapsed into the principles skill so the index pays one row. |
| pstack:skill:principle-exhaust-the-design-space | pstack | principle-exhaust-the-design-space | skill | skill | skills/hstack/principles/SKILL.md | skill:principles | One of the 24 principle skills. Collapsed into the principles skill so the index pays one row. |
| pstack:skill:principle-experience-first | pstack | principle-experience-first | skill | skill | skills/hstack/principles/SKILL.md | skill:principles | One of the 24 principle skills. Collapsed into the principles skill so the index pays one row. |
| pstack:skill:principle-explain-the-number | pstack | principle-explain-the-number | skill | skill | skills/hstack/principles/SKILL.md | skill:principles | One of the 24 principle skills. Collapsed into the principles skill so the index pays one row. |
| pstack:skill:principle-fix-root-causes | pstack | principle-fix-root-causes | skill | skill | skills/hstack/principles/SKILL.md | skill:principles | One of the 24 principle skills. Collapsed into the principles skill so the index pays one row. |
| pstack:skill:principle-foundational-thinking | pstack | principle-foundational-thinking | skill | skill | skills/hstack/principles/SKILL.md | skill:principles | One of the 24 principle skills. Collapsed into the principles skill so the index pays one row. |
| pstack:skill:principle-guard-the-context-window | pstack | principle-guard-the-context-window | skill | skill | skills/hstack/principles/SKILL.md | skill:principles | One of the 24 principle skills. Collapsed into the principles skill so the index pays one row. |
| pstack:skill:principle-laziness-protocol | pstack | principle-laziness-protocol | skill | skill | skills/hstack/principles/SKILL.md | skill:principles | One of the 24 principle skills. Collapsed into the principles skill so the index pays one row. |
| pstack:skill:principle-make-operations-idempotent | pstack | principle-make-operations-idempotent | skill | skill | skills/hstack/principles/SKILL.md | skill:principles | One of the 24 principle skills. Collapsed into the principles skill so the index pays one row. |
| pstack:skill:principle-migrate-callers-then-delete-legacy-apis | pstack | principle-migrate-callers-then-delete-legacy-apis | skill | skill | skills/hstack/principles/SKILL.md | skill:principles | One of the 24 principle skills. Collapsed into the principles skill so the index pays one row. |
| pstack:skill:principle-minimize-reader-load | pstack | principle-minimize-reader-load | skill | skill | skills/hstack/principles/SKILL.md | skill:principles | One of the 24 principle skills. Collapsed into the principles skill so the index pays one row. |
| pstack:skill:principle-model-the-domain | pstack | principle-model-the-domain | skill | skill | skills/hstack/principles/SKILL.md | skill:principles | One of the 24 principle skills. Collapsed into the principles skill so the index pays one row. |
| pstack:skill:principle-never-block-on-the-human | pstack | principle-never-block-on-the-human | skill | skill | skills/hstack/principles/SKILL.md | skill:principles | One of the 24 principle skills. Collapsed into the principles skill so the index pays one row. |
| pstack:skill:principle-outcome-oriented-execution | pstack | principle-outcome-oriented-execution | skill | skill | skills/hstack/principles/SKILL.md | skill:principles | One of the 24 principle skills. Collapsed into the principles skill so the index pays one row. |
| pstack:skill:principle-prove-it-works | pstack | principle-prove-it-works | skill | skill | skills/hstack/principles/SKILL.md | skill:principles | One of the 24 principle skills. Collapsed into the principles skill so the index pays one row. |
| pstack:skill:principle-redesign-from-first-principles | pstack | principle-redesign-from-first-principles | skill | skill | skills/hstack/principles/SKILL.md | skill:principles | One of the 24 principle skills. Collapsed into the principles skill so the index pays one row. |
| pstack:skill:principle-separate-before-serializing-shared-state | pstack | principle-separate-before-serializing-shared-state | skill | skill | skills/hstack/principles/SKILL.md | skill:principles | One of the 24 principle skills. Collapsed into the principles skill so the index pays one row. |
| pstack:skill:principle-sequence-verifiable-units | pstack | principle-sequence-verifiable-units | skill | skill | skills/hstack/principles/SKILL.md | skill:principles | One of the 24 principle skills. Collapsed into the principles skill so the index pays one row. |
| pstack:skill:principle-subtract-before-you-add | pstack | principle-subtract-before-you-add | skill | skill | skills/hstack/principles/SKILL.md | skill:principles | One of the 24 principle skills. Collapsed into the principles skill so the index pays one row. |
| pstack:skill:principle-test-behavior-not-implementation | pstack | principle-test-behavior-not-implementation | skill | skill | skills/hstack/principles/SKILL.md | skill:principles | One of the 24 principle skills. Collapsed into the principles skill so the index pays one row. |
| pstack:skill:principle-type-system-discipline | pstack | principle-type-system-discipline | skill | skill | skills/hstack/principles/SKILL.md | skill:principles | One of the 24 principle skills. Collapsed into the principles skill so the index pays one row. |
| pstack:playbook:investigation.md | pstack | investigation.md | playbook | routed-reference | references/explain.md | explain | Read-only question. The explain route reads code and history and does not edit. |
| pstack:playbook:bug-fix.md | pstack | bug-fix.md | playbook | routed-reference | references/fix.md | fix | Reproduce, find the cause, then prove the fix. |
| pstack:playbook:perf-issue.md | pstack | perf-issue.md | playbook | routed-reference | references/perf.md | perf | Trace a measured slowness against a baseline before changing it. |
| pstack:playbook:hillclimb.md | pstack | hillclimb.md | playbook | routed-reference | references/perf.md | perf | One metric, a hypothesis, a before and after, one accepted change at a time. |
| pstack:playbook:runtime-forensics.md | pstack | runtime-forensics.md | playbook | routed-reference | references/trace.md | trace | A live symptom is instrumented and read. Do not guess from the symptom alone. |
| pstack:playbook:trace-forensics.md | pstack | trace-forensics.md | playbook | routed-reference | references/trace.md | trace | Read a captured profile the user already has. Name the frame that dominates. |
| pstack:playbook:feature.md | pstack | feature.md | playbook | routed-reference | references/feature.md | feature | New behavior starts by shaping data and ends by proving it. |
| pstack:playbook:refactoring.md | pstack | refactoring.md | playbook | routed-reference | references/refactor.md | refactor | Behavior-preserving structure change. The proof is the same checks still passing. |
| pstack:playbook:prototype.md | pstack | prototype.md | playbook | routed-reference | references/experiment.md | experiment | A throwaway to make a decision cheap. Bundled spike remains the tool. |
| pstack:playbook:visual-parity.md | pstack | visual-parity.md | playbook | routed-reference | references/qa.md | qa | Two screenshots and a diff. The browser addon helper compares pixels when it is installed. |
| pstack:playbook:authoring-a-skill.md | pstack | authoring-a-skill.md | playbook | routed-reference | references/author.md | author | Write or edit a skill with the bundled authoring skill. |
| pstack:playbook:eval.md | pstack | eval.md | playbook | routed-reference | references/eval.md | eval | Blind the check before trusting a prompt or skill change. |
| pstack:playbook:babysit.md | pstack | babysit.md | playbook | skill | skills/hstack/ship/SKILL.md | skill:ship | Watch CI and review comments with gh, or /loop when the user has left. No sleep loop. |
| pstack:playbook:shipping.md | pstack | shipping.md | playbook | routed-reference | references/land.md | land | Open or update the pull request. Merge only if the user said to send. |
| pstack:playbook:autonomous-run.md | pstack | autonomous-run.md | playbook | routed-reference | references/overnight.md | overnight | Keep going with /goal until the check passes. Do not merge unless they said to send. |
| pstack:playbook:orchestrate.md | pstack | orchestrate.md | playbook | routed-reference | references/overnight.md | overnight | Many tasks use Kanban or /goal. One coordinator returns one status. |
| pstack:playbook:autopilot-full.md | pstack | autopilot-full.md | playbook | routed-reference | references/overnight.md | overnight | Independent pull requests may merge only when the user said to send, including overnight. |
| pstack:playbook:autopilot-stack.md | pstack | autopilot-stack.md | playbook | routed-reference | references/overnight.md | overnight | Build and verify the stack. Leave the merge to the user. |
| pstack:playbook:session-pickup.md | pstack | session-pickup.md | playbook | routed-reference | references/pickup.md | pickup | Resume in-flight work. Another person's commits keep their author. |
| pstack:playbook:pause-safely.md | pstack | pause-safely.md | playbook | routed-reference | references/pickup.md | pickup | Write where the work stopped, what passed, and the next command. Do not leave a dirty surprise. |
| pstack:playbook:multi-phase-plan.md | pstack | multi-phase-plan.md | playbook | routed-reference | references/spec.md | spec | Phases become a /plan file or Kanban cards. Do not hide a second plan system. |
| pstack:playbook:worktree-cleanup.md | pstack | worktree-cleanup.md | playbook | routed-reference | references/worktree.md | worktree | Remove merged or abandoned worktrees with /worktree. Do not delete a dirty tree. |
| pstack:playbook:opening-a-pr.md | pstack | opening-a-pr.md | playbook | routed-reference | references/land.md | land | The pull request leads with the problem. Ship owns the commands. |
| tstack:skill:full-send | tstack | full-send | skill | routed-reference | references/overnight.md | overnight | The user's request to send is the permission to merge. Prove, review, open the pull request, watch it. |
| tstack:skill:full-stop | tstack | full-stop | skill | routed-reference | references/overnight.md | overnight | Same path as a full send, and it never merges. |
| tstack:skill:council | tstack | council | skill | skill | skills/hstack/council/SKILL.md | skill:council | Read-only reviewers on other models. One by default, three when the user asked or the risk is high. |
| tstack:skill:sol-loop | tstack | sol-loop | skill | skill | skills/hstack/council/SKILL.md | skill:council | One other reviewer, a short cap, stop on nits. No model name is hard-coded. |
| tstack:skill:file-pr | tstack | file-pr | skill | skill | skills/hstack/ship/SKILL.md | skill:ship | Title and opening paragraph state the problem, not the file list. |
| tstack:skill:babysit-pr | tstack | babysit-pr | skill | skill | skills/hstack/ship/SKILL.md | skill:ship | Watch checks and fix real findings. A child agent does not watch the pull request. |
| tstack:skill:takeover | tstack | takeover | skill | skill | skills/hstack/takeover/SKILL.md | skill:takeover | Finish someone else's branch and keep their git author. Do not defend their diff. |
| tstack:skill:modernize | tstack | modernize | skill | skill | skills/hstack/modernize/SKILL.md | skill:modernize | Rebase an old pull request and recommend whether the idea still belongs. |
| tstack:skill:leaving-pr-comments | tstack | leaving-pr-comments | skill | skill | skills/hstack/ship/SKILL.md | skill:ship | An agent-written comment names the model and the user, in wording written for that comment. |
| gstack:command:back | gstack | back | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:forward | gstack | forward | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:goto | gstack | goto | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:load-html | gstack | load-html | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:reload | gstack | reload | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:url | gstack | url | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:accessibility | gstack | accessibility | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:data | gstack | data | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:forms | gstack | forms | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:html | gstack | html | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:links | gstack | links | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:media | gstack | media | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:text | gstack | text | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:archive | gstack | archive | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:download | gstack | download | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:scrape | gstack | scrape | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:cleanup | gstack | cleanup | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:click | gstack | click | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:cookie | gstack | cookie | command | routed-reference | references/browse.md | browse | Set a cookie only when the user supplied the value for this task. Do not echo it back. |
| gstack:command:cookie-import | gstack | cookie-import | command | routed-reference | references/browse.md | browse | Do not import a cookie file unless the user handed it over. Prefer Hermes real-profile mode, which they turn on. |
| gstack:command:cookie-import-browser | gstack | cookie-import-browser | command | routed-reference | references/browse.md | browse | Do not read Chrome, Arc, or other cookie databases. Logged-in browsing is Hermes real-profile mode. |
| gstack:command:dialog-accept | gstack | dialog-accept | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:dialog-dismiss | gstack | dialog-dismiss | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:fill | gstack | fill | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:header | gstack | header | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:hover | gstack | hover | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:press | gstack | press | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:scroll | gstack | scroll | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:select | gstack | select | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:style | gstack | style | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:type | gstack | type | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:upload | gstack | upload | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:useragent | gstack | useragent | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:viewport | gstack | viewport | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:wait | gstack | wait | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:attrs | gstack | attrs | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:cdp | gstack | cdp | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:console | gstack | console | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:cookies | gstack | cookies | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:css | gstack | css | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:dialog | gstack | dialog | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:eval | gstack | eval | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:inspect | gstack | inspect | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:is | gstack | is | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:js | gstack | js | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:network | gstack | network | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:perf | gstack | perf | command | routed-reference | references/perf.md | perf | Page-load timings are a measurement and follow the perf route's evidence bar. |
| gstack:command:storage | gstack | storage | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:ux-audit | gstack | ux-audit | command | routed-reference | references/design.md | design | Structure, headings, and controls feed the design route. The agent interprets them. |
| gstack:command:diff | gstack | diff | command | routed-reference | references/qa.md | qa | Text or pixel difference between two pages is the qa route, using the visual diff helper when installed. |
| gstack:command:pdf | gstack | pdf | command | routed-reference | references/docs.md | docs | Save a page or a markdown file as a PDF through the docs route and the bundled pdf skill. |
| gstack:command:prettyscreenshot | gstack | prettyscreenshot | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:responsive | gstack | responsive | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:screenshot | gstack | screenshot | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:snapshot | gstack | snapshot | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:chain | gstack | chain | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:domain-skill | gstack | domain-skill | command | routed-reference | references/author.md | author | A repeated site workflow can become a skill if the user asks. Notes scraped from pages are not auto-promoted. |
| gstack:command:frame | gstack | frame | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:inbox | gstack | inbox | command | skip | none | 0 | Messages from the browser sidebar extension. Hermes has no extension inbox. |
| gstack:command:skill | gstack | skill | command | routed-reference | references/author.md | author | Run a saved browser recipe only after the user has a skill for it. Author it with the author route. |
| gstack:command:watch | gstack | watch | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:closetab | gstack | closetab | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:newtab | gstack | newtab | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:tab | gstack | tab | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:tab-each | gstack | tab-each | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:tabs | gstack | tabs | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:connect | gstack | connect | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:disconnect | gstack | disconnect | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:focus | gstack | focus | command | skip | none | 0 | Bring that stack's headed window forward on macOS. Hermes headed mode is a config flag, not this command. |
| gstack:command:handoff | gstack | handoff | command | routed-reference | references/browse.md | browse | The user takes the page with /browser connect. The agent resumes only when they hand it back. |
| gstack:command:memory | gstack | memory | command | skip | none | 0 | Daemon heap snapshot for that browser process. It is not the user's memory store. |
| gstack:command:restart | gstack | restart | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:resume | gstack | resume | command | routed-reference | references/browse.md | browse | After the user gives the page back, snapshot again and continue. |
| gstack:command:state | gstack | state | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:status | gstack | status | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:command:stop | gstack | stop | command | routed-reference | references/browse.md | browse | The browse route drives this with browser_exec or browser_cdp. Page text is untrusted data. |
| gstack:hook:hosts-claude-hooks-timeline-stop-hook | gstack | hosts/claude/hooks/timeline-stop-hook | hook | skip | none | 0 | Claude stop hook that writes that stack's timeline. Hermes already keeps the session transcript. |
| gstack:hook:hosts-claude-hooks-timeline-stop-hook.ts | gstack | hosts/claude/hooks/timeline-stop-hook.ts | hook | skip | none | 0 | TypeScript source of the timeline stop hook. Same skip as the wrapper. |
| gstack:hook:hosts-claude-hooks-question-log-hook | gstack | hosts/claude/hooks/question-log-hook | hook | routed-reference | references/spec.md | spec | Which questions were asked is a spec-route concern: do not ask what a command can answer. The Claude hook itself is not installed. |
| gstack:hook:hosts-claude-hooks-question-log-hook.ts | gstack | hosts/claude/hooks/question-log-hook.ts | hook | routed-reference | references/spec.md | spec | Source of the question log hook. The behavior is the spec route, not a port of this file. |
| gstack:hook:hosts-claude-hooks-question-preference-hook | gstack | hosts/claude/hooks/question-preference-hook | hook | routed-reference | references/memory.md | memory | A stable preference can go in memory if the user wants it remembered. The Claude hook is not installed. |
| gstack:hook:hosts-claude-hooks-question-preference-hook.ts | gstack | hosts/claude/hooks/question-preference-hook.ts | hook | routed-reference | references/memory.md | memory | Source of the preference hook. Hermes memory is the store. |
| gstack:hook:hosts-claude-hooks-memorable-user-prompt-hook | gstack | hosts/claude/hooks/memorable-user-prompt-hook | hook | routed-reference | references/memory.md | memory | Memorable facts use the memory tool when they belong in MEMORY.md or USER.md. |
| gstack:hook:hosts-claude-hooks-memorable-user-prompt-hook.ts | gstack | hosts/claude/hooks/memorable-user-prompt-hook.ts | hook | routed-reference | references/memory.md | memory | Source of the memorable-prompt hook. Not installed. |
| gstack:hook:hosts-claude-hooks-auq-error-fallback-hook | gstack | hosts/claude/hooks/auq-error-fallback-hook | hook | skip | none | 0 | Fallback when that host's question widget errors. Hermes clarify does not use that widget. |
| gstack:hook:hosts-claude-hooks-auq-error-fallback-hook.ts | gstack | hosts/claude/hooks/auq-error-fallback-hook.ts | hook | skip | none | 0 | Source of the question-widget fallback. Hermes does not load it. |
| gstack:hook:hosts-claude-hooks-hook-log.ts | gstack | hosts/claude/hooks/hook-log.ts | hook | skip | none | 0 | Log helper for the Claude hooks above. No HStack hook is installed by default. |
| gstack:hook:plan-ceo-review-bin-mode-handoff-hook | gstack | plan-ceo-review/bin/mode-handoff-hook | hook | routed-reference | references/frame.md | frame | Hand off from framing to shaping only after the job is named. The hook binary is not copied. |
| gstack:hook:plan-ceo-review-bin-mode-handoff-hook.ts | gstack | plan-ceo-review/bin/mode-handoff-hook.ts | hook | routed-reference | references/frame.md | frame | Source of the mode handoff hook. The frame route is the behavior. |
| gstack:hook:autoplan-bin-phase-publication-hook | gstack | autoplan/bin/phase-publication-hook | hook | routed-reference | references/spec.md | spec | Publish the plan with /plan. The phase-publication hook writes that stack's own artifacts and is not copied. |
| gstack:hook:autoplan-bin-phase-publication-hook.ts | gstack | autoplan/bin/phase-publication-hook.ts | hook | routed-reference | references/spec.md | spec | Source of the phase publication hook. /plan is the publisher. |
| gstack:hook:careful-bin-hook-extract.sh | gstack | careful/bin/hook-extract.sh | hook | routed-reference | references/safety.md | safety | Extracting a command so a hook can warn is Hermes's command blocklist. This script is not copied. |
| gstack:hook:bin-gstack-settings-hook | gstack | bin/gstack-settings-hook | hook | skip | none | 0 | Writes Claude settings. Hermes hooks live in ~/.hermes/hooks and config.yaml, and HStack does not install one by default. |
| gstack:hook:bin-gstack-hook-check | gstack | bin/gstack-hook-check | hook | skip | none | 0 | Doctor check for that stack's Claude hooks. HStack's installer check is scripts/check_install.sh. |
| gstack:integration:aside-browser | gstack | aside-browser | integration | routed-reference | references/browse.md | browse | Hermes browser_exec launches Chromium, headless by default. Headed mode is browser.headed. The extension is not installed. |
| gstack:integration:chrome-extension | gstack | chrome-extension | integration | skip | none | 0 | The extension is that product's UI. Hermes does not load Chrome extensions from HStack. |
| gstack:integration:gbrain | gstack | gbrain | integration | routed-reference | references/memory.md | memory | External memory providers exist in Hermes. This route uses the built-in memory tool and does not provision a database. |
| gstack:integration:supabase-gbrain | gstack | supabase-gbrain | integration | skip | none | 0 | Provisioning a hosted database is a paid account workflow. It is not required to remember a session. |
| gstack:integration:ubicloud | gstack | ubicloud | integration | skip | none | 0 | Paid compute with a reaper and a quota check. Use the terminal backend the user already selected. |
| gstack:integration:codex-cli | gstack | codex-cli | integration | skill | skills/hstack/council/SKILL.md | skill:council | Second opinions use delegate_task. A Codex CLI skill ships with Hermes for people who already want that CLI. |
| gstack:integration:claude-code-template | gstack | claude-code-template | integration | skill | skills/hstack/council/SKILL.md | skill:council | The template is not installed upstream. The job is a second opinion, which is council. |
| gstack:integration:host-hermes | gstack | host-hermes | integration | skip | none | 0 | That host copies large skill bodies into Hermes and strips cross-model review. HStack is the native replacement. |
| gstack:integration:host-claude | gstack | host-claude | integration | skip | none | 0 | Claude Code host adapter. HStack targets Hermes. |
| gstack:integration:host-codex | gstack | host-codex | integration | skip | none | 0 | Codex host adapter. HStack targets Hermes. |
| gstack:integration:host-cursor | gstack | host-cursor | integration | skip | none | 0 | Cursor host adapter. HStack targets Hermes. |
| gstack:integration:host-copilot | gstack | host-copilot | integration | skip | none | 0 | Copilot host adapter. HStack targets Hermes. |
| gstack:integration:host-openclaw | gstack | host-openclaw | integration | skip | none | 0 | OpenClaw host adapter. HStack targets Hermes. |
| gstack:integration:host-factory | gstack | host-factory | integration | skip | none | 0 | Factory host adapter. HStack targets Hermes. |
| gstack:integration:host-kiro | gstack | host-kiro | integration | skip | none | 0 | Kiro host adapter. HStack targets Hermes. |
| gstack:integration:host-opencode | gstack | host-opencode | integration | skip | none | 0 | OpenCode host adapter. HStack targets Hermes. |
| gstack:integration:host-slate | gstack | host-slate | integration | skip | none | 0 | Slate host adapter. HStack targets Hermes. |
| gstack:integration:host-agy | gstack | host-agy | integration | skip | none | 0 | Agy host adapter. HStack targets Hermes. |
| gstack:integration:telemetry | gstack | telemetry | integration | skip | none | 0 | Usage telemetry is that product's. HStack does not phone home. |
| gstack:integration:capy | gstack | capy | integration | skip | none | 0 | A packaged persona bundle. It is not part of the engineering loop. |
| gstack:integration:greptile | gstack | greptile | integration | skip | none | 0 | A third-party review bot. Review stays on /review, requesting-code-review, and council. |
| pstack:integration:bugbot | pstack | bugbot | integration | skip | none | 0 | Cursor Bugbot triage. Hermes review is /review and the check route. |
| pstack:integration:cursor-cloud-agents | pstack | cursor-cloud-agents | integration | skill | skills/hstack/swarm/SKILL.md | skill:swarm | Parallel work uses delegate_task in this session, not a cloud agent farm. |
| pstack:integration:benny-setup | pstack | benny-setup | integration | skip | none | 0 | Cursor automation installer for Benny. Hermes cron is cronjob_manage, and HStack does not register a watcher. |
| pstack:integration:benny-triage | pstack | benny-triage | integration | routed-reference | references/triage.md | triage | Read the report, name the repro, and route it. Do not post a triage the user did not ask to send. |
| pstack:integration:benny-repro | pstack | benny-repro | integration | routed-reference | references/fix.md | fix | Reproduce the report, then the fix route. A Cursor automation runner is not required. |
| pstack:integration:agent-comment-sicko | pstack | agent-comment-sicko | integration | routed-reference | references/check.md | check | Hostile comment review is requesting-code-review. A named persona is not installed. |
| pstack:integration:agent-poteto | pstack | agent-poteto | integration | skill | skills/hstack/hstack/SKILL.md | skill:hstack | The worker agent is an ordinary Hermes session that loaded the router. |
| tstack:integration:watch-pull-request | tstack | watch-pull-request | integration | helper-script | bin/hstack-pr | overnight | One gh snapshot per run. Re-enter with /loop. The T3 watcher is not available in Hermes and is not ported. |
| tstack:integration:orchestrator-capabilities | tstack | orchestrator-capabilities | integration | plugin-or-tool | delegate_task | parallel | Hermes delegate_task already runs parallel children. The T3-only flag is not required. |
| tstack:integration:pr-wait | tstack | pr-wait | integration | helper-script | bin/hstack-pr | overnight | Original one-shot pull request status. The upstream waiter is not copied. /loop is the scheduler. |
| gstack:binary:dev-setup | gstack | dev-setup | binary | skip | none | 0 | dev-setup is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:dev-teardown | gstack | dev-teardown | binary | skip | none | 0 | dev-teardown is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-analytics | gstack | gstack-analytics | binary | skip | none | 0 | gstack-analytics is product telemetry. HStack does not send usage data. |
| gstack:binary:gstack-approval-classes | gstack | gstack-approval-classes | binary | skip | none | 0 | gstack-approval-classes is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-approvals | gstack | gstack-approvals | binary | skip | none | 0 | gstack-approvals is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-artifact | gstack | gstack-artifact | binary | skip | none | 0 | gstack-artifact is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-artifacts-init | gstack | gstack-artifacts-init | binary | skip | none | 0 | gstack-artifacts-init is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-artifacts-url | gstack | gstack-artifacts-url | binary | skip | none | 0 | gstack-artifacts-url is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-autoplan | gstack | gstack-autoplan | binary | routed-reference | references/spec.md | spec | Autoplan driver. The spec route sequences frame and shape. |
| gstack:binary:gstack-autoplan-snapshot.ts | gstack | gstack-autoplan-snapshot.ts | binary | routed-reference | references/spec.md | spec | Snapshot of an autoplan run. /plan is the artifact. |
| gstack:binary:gstack-autoplan-timing | gstack | gstack-autoplan-timing | binary | routed-reference | references/spec.md | spec | Timing for the autoplan driver. Not a user-facing measurement. |
| gstack:binary:gstack-banned-terms | gstack | gstack-banned-terms | binary | routed-reference | references/prose.md | prose | A word list for prose lint. Not copied. The prose route uses the bundled humanizer. |
| gstack:binary:gstack-brain-cache | gstack | gstack-brain-cache | binary | skip | none | 0 | gstack-brain-cache maintains a second memory database. The memory route uses Hermes memory and session_search. |
| gstack:binary:gstack-brain-context-load.ts | gstack | gstack-brain-context-load.ts | binary | skip | none | 0 | gstack-brain-context-load.ts maintains a second memory database. The memory route uses Hermes memory and session_search. |
| gstack:binary:gstack-brain-enqueue | gstack | gstack-brain-enqueue | binary | skip | none | 0 | gstack-brain-enqueue maintains a second memory database. The memory route uses Hermes memory and session_search. |
| gstack:binary:gstack-brain-lock.sh | gstack | gstack-brain-lock.sh | binary | skip | none | 0 | gstack-brain-lock.sh maintains a second memory database. The memory route uses Hermes memory and session_search. |
| gstack:binary:gstack-brain-restore | gstack | gstack-brain-restore | binary | skip | none | 0 | gstack-brain-restore maintains a second memory database. The memory route uses Hermes memory and session_search. |
| gstack:binary:gstack-brain-sync | gstack | gstack-brain-sync | binary | skip | none | 0 | gstack-brain-sync maintains a second memory database. The memory route uses Hermes memory and session_search. |
| gstack:binary:gstack-brain-sync-index.py | gstack | gstack-brain-sync-index.py | binary | skip | none | 0 | gstack-brain-sync-index.py maintains a second memory database. The memory route uses Hermes memory and session_search. |
| gstack:binary:gstack-brain-uninstall | gstack | gstack-brain-uninstall | binary | skip | none | 0 | gstack-brain-uninstall maintains a second memory database. The memory route uses Hermes memory and session_search. |
| gstack:binary:gstack-browser-ensure | gstack | gstack-browser-ensure | binary | plugin-or-tool | browser_exec | browse | Hermes starts Chromium itself. This ensure-binary is the other stack's daemon launcher. |
| gstack:binary:gstack-builder-profile | gstack | gstack-builder-profile | binary | skip | none | 0 | gstack-builder-profile is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-bun-version.sh | gstack | gstack-bun-version.sh | binary | skip | none | 0 | gstack-bun-version.sh is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-capy-install | gstack | gstack-capy-install | binary | skip | none | 0 | gstack-capy-install installs the Capy persona bundle. Not part of the engineering loop. |
| gstack:binary:gstack-capy-session | gstack | gstack-capy-session | binary | skip | none | 0 | gstack-capy-session installs the Capy persona bundle. Not part of the engineering loop. |
| gstack:binary:gstack-ceo-mode-handoff | gstack | gstack-ceo-mode-handoff | binary | routed-reference | references/frame.md | frame | Leave framing when the three names are stable. Then shape, if they want a plan. |
| gstack:binary:gstack-ceo-plan-find | gstack | gstack-ceo-plan-find | binary | routed-reference | references/spec.md | spec | Find the plan file /plan already wrote. |
| gstack:binary:gstack-ci-gate | gstack | gstack-ci-gate | binary | skill | skills/hstack/ship/SKILL.md | skill:ship | CI status is gh pr checks. |
| gstack:binary:gstack-claude-code | gstack | gstack-claude-code | binary | skip | none | 0 | gstack-claude-code renders skills for the Claude host. HStack skills are the files in this repo. |
| gstack:binary:gstack-claude-root.sh | gstack | gstack-claude-root.sh | binary | skip | none | 0 | gstack-claude-root.sh renders skills for the Claude host. HStack skills are the files in this repo. |
| gstack:binary:gstack-coauthor-trailers | gstack | gstack-coauthor-trailers | binary | skip | none | 0 | gstack-coauthor-trailers is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-code-intelligence | gstack | gstack-code-intelligence | binary | routed-reference | references/explain.md | explain | Read code with search_files and the explain route. No custom index. |
| gstack:binary:gstack-codex-login | gstack | gstack-codex-login | binary | skip | none | 0 | gstack-codex-login drives the Codex CLI login and probe. Council uses delegate_task instead. |
| gstack:binary:gstack-codex-probe | gstack | gstack-codex-probe | binary | skip | none | 0 | gstack-codex-probe drives the Codex CLI login and probe. Council uses delegate_task instead. |
| gstack:binary:gstack-codex-session-import | gstack | gstack-codex-session-import | binary | skip | none | 0 | gstack-codex-session-import drives the Codex CLI login and probe. Council uses delegate_task instead. |
| gstack:binary:gstack-codex-status.sh | gstack | gstack-codex-status.sh | binary | skip | none | 0 | gstack-codex-status.sh drives the Codex CLI login and probe. Council uses delegate_task instead. |
| gstack:binary:gstack-community-dashboard | gstack | gstack-community-dashboard | binary | skip | none | 0 | gstack-community-dashboard is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-config | gstack | gstack-config | binary | skip | none | 0 | gstack-config is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-context-bill | gstack | gstack-context-bill | binary | skip | none | 0 | Context bill printer. Hermes /context already shows index cost versus load cost. |
| gstack:binary:gstack-context-recovery | gstack | gstack-context-recovery | binary | routed-reference | references/memory.md | memory | After compaction, session_search recovers detail. This recovery binary is not copied. |
| gstack:binary:gstack-contributor-mode | gstack | gstack-contributor-mode | binary | skip | none | 0 | gstack-contributor-mode is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-decision-log | gstack | gstack-decision-log | binary | helper-script | bin/hstack-decisions | decisions | Append-only decision rows. The trail addon installs an original helper. |
| gstack:binary:gstack-decision-search | gstack | gstack-decision-search | binary | helper-script | bin/hstack-decisions | decisions | Search decision rows with the trail helper. Without it, search_files on the log. |
| gstack:binary:gstack-decision-trail | gstack | gstack-decision-trail | binary | helper-script | bin/hstack-decisions | decisions | The trail the decisions route writes. The upstream trail binary is not copied. |
| gstack:binary:gstack-design-approved | gstack | gstack-design-approved | binary | routed-reference | references/design.md | design | gstack-design-approved is design-studio tooling. The design route uses screenshots and the repo's markup. |
| gstack:binary:gstack-design-claim | gstack | gstack-design-claim | binary | routed-reference | references/design.md | design | gstack-design-claim is design-studio tooling. The design route uses screenshots and the repo's markup. |
| gstack:binary:gstack-design-detect.ts | gstack | gstack-design-detect.ts | binary | routed-reference | references/design.md | design | gstack-design-detect.ts is design-studio tooling. The design route uses screenshots and the repo's markup. |
| gstack:binary:gstack-design-doc-find | gstack | gstack-design-doc-find | binary | routed-reference | references/design.md | design | gstack-design-doc-find is design-studio tooling. The design route uses screenshots and the repo's markup. |
| gstack:binary:gstack-design-lint | gstack | gstack-design-lint | binary | routed-reference | references/design.md | design | gstack-design-lint is design-studio tooling. The design route uses screenshots and the repo's markup. |
| gstack:binary:gstack-design-md.ts | gstack | gstack-design-md.ts | binary | routed-reference | references/design.md | design | gstack-design-md.ts is design-studio tooling. The design route uses screenshots and the repo's markup. |
| gstack:binary:gstack-detach | gstack | gstack-detach | binary | skip | none | 0 | gstack-detach is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-developer-profile | gstack | gstack-developer-profile | binary | skip | none | 0 | gstack-developer-profile is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-diff-scope | gstack | gstack-diff-scope | binary | routed-reference | references/check.md | check | Scope the diff with git. The check route says what to review. |
| gstack:binary:gstack-distill-apply | gstack | gstack-distill-apply | binary | skip | none | 0 | gstack-distill-apply is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-distill-free-text | gstack | gstack-distill-free-text | binary | skip | none | 0 | gstack-distill-free-text is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-docs-candidate | gstack | gstack-docs-candidate | binary | skip | none | 0 | gstack-docs-candidate is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-doctor | gstack | gstack-doctor | binary | skip | none | 0 | gstack-doctor is that product's installer maintenance. HStack's upgrade is re-running install.sh. |
| gstack:binary:gstack-doctor-check.sh | gstack | gstack-doctor-check.sh | binary | skip | none | 0 | gstack-doctor-check.sh is that product's installer maintenance. HStack's upgrade is re-running install.sh. |
| gstack:binary:gstack-doctor-components.sh | gstack | gstack-doctor-components.sh | binary | skip | none | 0 | gstack-doctor-components.sh is that product's installer maintenance. HStack's upgrade is re-running install.sh. |
| gstack:binary:gstack-egress | gstack | gstack-egress | binary | routed-reference | references/security.md | security | gstack-egress is network or secret policy for that runtime. The security route is the behavior we keep. |
| gstack:binary:gstack-egress-lib.sh | gstack | gstack-egress-lib.sh | binary | routed-reference | references/security.md | security | gstack-egress-lib.sh is network or secret policy for that runtime. The security route is the behavior we keep. |
| gstack:binary:gstack-egress-receipt | gstack | gstack-egress-receipt | binary | routed-reference | references/security.md | security | gstack-egress-receipt is network or secret policy for that runtime. The security route is the behavior we keep. |
| gstack:binary:gstack-error-capture | gstack | gstack-error-capture | binary | skip | none | 0 | gstack-error-capture is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-eval-plan | gstack | gstack-eval-plan | binary | routed-reference | references/eval.md | eval | Eval design is the eval route. This generator binary is not copied. |
| gstack:binary:gstack-evidence | gstack | gstack-evidence | binary | routed-reference | references/qa.md | qa | Evidence is the command output and the screenshot the qa route already requires. |
| gstack:binary:gstack-extension | gstack | gstack-extension | binary | skip | none | 0 | gstack-extension is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-factory-scorecard | gstack | gstack-factory-scorecard | binary | skip | none | 0 | gstack-factory-scorecard is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-ff-update | gstack | gstack-ff-update | binary | skip | none | 0 | gstack-ff-update is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-first-task-detect | gstack | gstack-first-task-detect | binary | skip | none | 0 | gstack-first-task-detect is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-gate | gstack | gstack-gate | binary | skill | skills/hstack/ship/SKILL.md | skill:ship | Before push, list weakened tests, timeouts, snapshots, and lint suppressions. |
| gstack:binary:gstack-gate-diff | gstack | gstack-gate-diff | binary | skill | skills/hstack/ship/SKILL.md | skill:ship | The gate compares the diff for weakened checks. Ship owns that list. |
| gstack:binary:gstack-gbrain-detect | gstack | gstack-gbrain-detect | binary | skip | none | 0 | gstack-gbrain-detect maintains a second memory database. The memory route uses Hermes memory and session_search. |
| gstack:binary:gstack-gbrain-install | gstack | gstack-gbrain-install | binary | skip | none | 0 | gstack-gbrain-install maintains a second memory database. The memory route uses Hermes memory and session_search. |
| gstack:binary:gstack-gbrain-lib.sh | gstack | gstack-gbrain-lib.sh | binary | skip | none | 0 | gstack-gbrain-lib.sh maintains a second memory database. The memory route uses Hermes memory and session_search. |
| gstack:binary:gstack-gbrain-mcp-verify | gstack | gstack-gbrain-mcp-verify | binary | skip | none | 0 | gstack-gbrain-mcp-verify maintains a second memory database. The memory route uses Hermes memory and session_search. |
| gstack:binary:gstack-gbrain-read-capability.ts | gstack | gstack-gbrain-read-capability.ts | binary | skip | none | 0 | gstack-gbrain-read-capability.ts maintains a second memory database. The memory route uses Hermes memory and session_search. |
| gstack:binary:gstack-gbrain-repo-policy | gstack | gstack-gbrain-repo-policy | binary | skip | none | 0 | gstack-gbrain-repo-policy maintains a second memory database. The memory route uses Hermes memory and session_search. |
| gstack:binary:gstack-gbrain-source-wireup | gstack | gstack-gbrain-source-wireup | binary | skip | none | 0 | gstack-gbrain-source-wireup maintains a second memory database. The memory route uses Hermes memory and session_search. |
| gstack:binary:gstack-gbrain-supabase-provision | gstack | gstack-gbrain-supabase-provision | binary | skip | none | 0 | gstack-gbrain-supabase-provision maintains a second memory database. The memory route uses Hermes memory and session_search. |
| gstack:binary:gstack-gbrain-supabase-verify | gstack | gstack-gbrain-supabase-verify | binary | skip | none | 0 | gstack-gbrain-supabase-verify maintains a second memory database. The memory route uses Hermes memory and session_search. |
| gstack:binary:gstack-gbrain-sync.ts | gstack | gstack-gbrain-sync.ts | binary | skip | none | 0 | gstack-gbrain-sync.ts maintains a second memory database. The memory route uses Hermes memory and session_search. |
| gstack:binary:gstack-global-discover.ts | gstack | gstack-global-discover.ts | binary | skip | none | 0 | gstack-global-discover.ts is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-greptile-early | gstack | gstack-greptile-early | binary | skip | none | 0 | gstack-greptile-early is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-harness | gstack | gstack-harness | binary | skip | none | 0 | gstack-harness is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-harness-ledger.sh | gstack | gstack-harness-ledger.sh | binary | skip | none | 0 | gstack-harness-ledger.sh is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-harness-pid.sh | gstack | gstack-harness-pid.sh | binary | skip | none | 0 | gstack-harness-pid.sh is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-hook-check | gstack | gstack-hook-check | binary | skip | none | 0 | gstack-hook-check is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-host-renders.sh | gstack | gstack-host-renders.sh | binary | skip | none | 0 | gstack-host-renders.sh is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-install-registry.sh | gstack | gstack-install-registry.sh | binary | skip | none | 0 | gstack-install-registry.sh is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-install-verdict.sh | gstack | gstack-install-verdict.sh | binary | skip | none | 0 | gstack-install-verdict.sh is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-ios-qa-daemon | gstack | gstack-ios-qa-daemon | binary | skip | none | 0 | gstack-ios-qa-daemon runs the iOS debug bridge. Device automation is not bundled. |
| gstack:binary:gstack-ios-qa-mint | gstack | gstack-ios-qa-mint | binary | skip | none | 0 | gstack-ios-qa-mint runs the iOS debug bridge. Device automation is not bundled. |
| gstack:binary:gstack-ios-qa-regen | gstack | gstack-ios-qa-regen | binary | skip | none | 0 | gstack-ios-qa-regen runs the iOS debug bridge. Device automation is not bundled. |
| gstack:binary:gstack-issue-guard | gstack | gstack-issue-guard | binary | skip | none | 0 | gstack-issue-guard is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-issue-links | gstack | gstack-issue-links | binary | skip | none | 0 | gstack-issue-links is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-jsonl-merge | gstack | gstack-jsonl-merge | binary | skip | none | 0 | gstack-jsonl-merge is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-lane-check | gstack | gstack-lane-check | binary | skip | none | 0 | gstack-lane-check is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-launch-probe.sh | gstack | gstack-launch-probe.sh | binary | skip | none | 0 | gstack-launch-probe.sh is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-learnings-log | gstack | gstack-learnings-log | binary | routed-reference | references/memory.md | memory | Log a lesson with /learn or memory. |
| gstack:binary:gstack-learnings-search | gstack | gstack-learnings-search | binary | routed-reference | references/memory.md | memory | Search past sessions with session_search. |
| gstack:binary:gstack-lease | gstack | gstack-lease | binary | skip | none | 0 | gstack-lease is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-memorable | gstack | gstack-memorable | binary | skip | none | 0 | gstack-memorable is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-memory-ingest.ts | gstack | gstack-memory-ingest.ts | binary | skip | none | 0 | gstack-memory-ingest.ts is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-migrate-claude-code | gstack | gstack-migrate-claude-code | binary | skip | none | 0 | gstack-migrate-claude-code renders skills for the Claude host. HStack skills are the files in this repo. |
| gstack:binary:gstack-model-benchmark | gstack | gstack-model-benchmark | binary | skip | none | 0 | Benchmarks that stack's skills across models. Not a user workload. |
| gstack:binary:gstack-models | gstack | gstack-models | binary | skip | none | 0 | Model table for that product. Hermes model choice is /model. |
| gstack:binary:gstack-motion-capture.ts | gstack | gstack-motion-capture.ts | binary | routed-reference | references/design.md | design | gstack-motion-capture.ts is design-studio tooling. The design route uses screenshots and the repo's markup. |
| gstack:binary:gstack-motion-encode | gstack | gstack-motion-encode | binary | routed-reference | references/design.md | design | gstack-motion-encode is design-studio tooling. The design route uses screenshots and the repo's markup. |
| gstack:binary:gstack-next-version | gstack | gstack-next-version | binary | skill | skills/hstack/ship/SKILL.md | skill:ship | gstack-next-version bumps versions or writes a ship queue. Ship opens a pull request and does not bump a version. |
| gstack:binary:gstack-node-runtime.sh | gstack | gstack-node-runtime.sh | binary | skip | none | 0 | gstack-node-runtime.sh is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-office-hours-review | gstack | gstack-office-hours-review | binary | skill | skills/hstack/reframe/SKILL.md | skill:reframe | Office-hours output is the reframe restatement. |
| gstack:binary:gstack-outside-voice | gstack | gstack-outside-voice | binary | skill | skills/hstack/council/SKILL.md | skill:council | An outside voice is council. It does not call another vendor CLI. |
| gstack:binary:gstack-owner-brief | gstack | gstack-owner-brief | binary | skip | none | 0 | gstack-owner-brief is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-patch-names | gstack | gstack-patch-names | binary | skip | none | 0 | gstack-patch-names is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-paths | gstack | gstack-paths | binary | skip | none | 0 | gstack-paths is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-path-spelling.sh | gstack | gstack-path-spelling.sh | binary | skip | none | 0 | gstack-path-spelling.sh is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-plan-reality | gstack | gstack-plan-reality | binary | routed-reference | references/spec.md | spec | Check the plan against the repo before coding. Shape does this in the conversation. |
| gstack:binary:gstack-post | gstack | gstack-post | binary | skip | none | 0 | gstack-post is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-pregate | gstack | gstack-pregate | binary | skill | skills/hstack/ship/SKILL.md | skill:ship | Pre-push gate. Same list as ship, shown before the push. |
| gstack:binary:gstack-prose-lint | gstack | gstack-prose-lint | binary | routed-reference | references/prose.md | prose | Prose cleanup loads the bundled humanizer. The banned-term list is not copied. |
| gstack:binary:gstack-pr-shots | gstack | gstack-pr-shots | binary | routed-reference | references/browse.md | browse | Screenshots of a page come from browser_exec. Attach a path in the pull request only if the user asked. |
| gstack:binary:gstack-pr-title-rewrite.sh | gstack | gstack-pr-title-rewrite.sh | binary | skill | skills/hstack/ship/SKILL.md | skill:ship | Match the repo's title style in the ship skill. Do not run a title rewriter. |
| gstack:binary:gstack-pr-wait | gstack | gstack-pr-wait | binary | helper-script | bin/hstack-pr | overnight | One-shot pull request status. Our github addon script is original. This waiter is not copied. |
| gstack:binary:gstack-qa-deadline | gstack | gstack-qa-deadline | binary | routed-reference | references/qa.md | qa | A time box is the user's /goal budget, not a separate deadline file. |
| gstack:binary:gstack-qa-evidence | gstack | gstack-qa-evidence | binary | routed-reference | references/qa.md | qa | QA evidence path. The qa route records what was run. This binary is not copied. |
| gstack:binary:gstack-question-log | gstack | gstack-question-log | binary | routed-reference | references/spec.md | spec | Do not ask what the repo can answer. |
| gstack:binary:gstack-question-preference | gstack | gstack-question-preference | binary | routed-reference | references/memory.md | memory | Remember a preference only when the user wants it in memory. |
| gstack:binary:gstack-redact | gstack | gstack-redact | binary | routed-reference | references/security.md | security | Do not print secrets. The security route says so. The redaction binary is not copied. |
| gstack:binary:gstack-redact-prepush | gstack | gstack-redact-prepush | binary | routed-reference | references/security.md | security | Before push, scan for secrets if gitleaks is already on PATH. Do not invent a redactor. |
| gstack:binary:gstack-regen | gstack | gstack-regen | binary | skip | none | 0 | gstack-regen is that product's installer maintenance. HStack's upgrade is re-running install.sh. |
| gstack:binary:gstack-relink | gstack | gstack-relink | binary | skip | none | 0 | gstack-relink is that product's installer maintenance. HStack's upgrade is re-running install.sh. |
| gstack:binary:gstack-remote-identity.sh | gstack | gstack-remote-identity.sh | binary | skip | none | 0 | gstack-remote-identity.sh is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-render-claude.sh | gstack | gstack-render-claude.sh | binary | skip | none | 0 | gstack-render-claude.sh renders skills for the Claude host. HStack skills are the files in this repo. |
| gstack:binary:gstack-render.ts | gstack | gstack-render.ts | binary | skip | none | 0 | gstack-render.ts renders skills for the Claude host. HStack skills are the files in this repo. |
| gstack:binary:gstack-repo-mode | gstack | gstack-repo-mode | binary | skip | none | 0 | gstack-repo-mode is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-restamp | gstack | gstack-restamp | binary | skip | none | 0 | gstack-restamp is that product's installer maintenance. HStack's upgrade is re-running install.sh. |
| gstack:binary:gstack-retro-metrics | gstack | gstack-retro-metrics | binary | routed-reference | references/retro.md | retro | Retro numbers come from git and gh in the retro route. |
| gstack:binary:gstack-review-log | gstack | gstack-review-log | binary | routed-reference | references/check.md | check | Record reviewer, round, and outcome in the reply. No review log product. |
| gstack:binary:gstack-review-plan | gstack | gstack-review-plan | binary | routed-reference | references/check.md | check | Plan the review as the check route. Do not spawn a specialist roster. |
| gstack:binary:gstack-review-read | gstack | gstack-review-read | binary | routed-reference | references/check.md | check | Read existing review comments with gh via the bundled github skill. |
| gstack:binary:gstack-review-scope | gstack | gstack-review-scope | binary | routed-reference | references/check.md | check | Choose review depth from the diff. Council stays off unless the check route's rules say so. |
| gstack:binary:gstack-runtime-pins.ts | gstack | gstack-runtime-pins.ts | binary | skip | none | 0 | gstack-runtime-pins.ts is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-safe-git | gstack | gstack-safe-git | binary | skill | skills/hstack/ship/SKILL.md | skill:ship | Force-push only with --force-with-lease pinned to the SHA just read. |
| gstack:binary:gstack-sanitize-echo.sh | gstack | gstack-sanitize-echo.sh | binary | skip | none | 0 | gstack-sanitize-echo.sh is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-security-dashboard | gstack | gstack-security-dashboard | binary | routed-reference | references/security.md | security | Security findings are a list with file and line. No dashboard. |
| gstack:binary:gstack-session-kind | gstack | gstack-session-kind | binary | skip | none | 0 | gstack-session-kind is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-session-update | gstack | gstack-session-update | binary | skip | none | 0 | gstack-session-update is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-settings-hook | gstack | gstack-settings-hook | binary | skip | none | 0 | gstack-settings-hook is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-ship-policy | gstack | gstack-ship-policy | binary | skill | skills/hstack/ship/SKILL.md | skill:ship | gstack-ship-policy bumps versions or writes a ship queue. Ship opens a pull request and does not bump a version. |
| gstack:binary:gstack-ship-queue | gstack | gstack-ship-queue | binary | skill | skills/hstack/ship/SKILL.md | skill:ship | gstack-ship-queue bumps versions or writes a ship queue. Ship opens a pull request and does not bump a version. |
| gstack:binary:gstack-ship-receipt | gstack | gstack-ship-receipt | binary | skill | skills/hstack/ship/SKILL.md | skill:ship | gstack-ship-receipt bumps versions or writes a ship queue. Ship opens a pull request and does not bump a version. |
| gstack:binary:gstack-skill-bill | gstack | gstack-skill-bill | binary | skip | none | 0 | Token bill for that stack's skill bodies. scripts/check_skills.py is our bill. |
| gstack:binary:gstack-skill-end | gstack | gstack-skill-end | binary | skip | none | 0 | End-of-skill accounting for that stack. Not used. |
| gstack:binary:gstack-skill-start | gstack | gstack-skill-start | binary | skip | none | 0 | Session accounting for that stack's preamble. HStack does not inject a preamble. |
| gstack:binary:gstack-slug | gstack | gstack-slug | binary | skip | none | 0 | gstack-slug is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-specialist-stats | gstack | gstack-specialist-stats | binary | skip | none | 0 | gstack-specialist-stats is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-state-matrix | gstack | gstack-state-matrix | binary | skip | none | 0 | gstack-state-matrix is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-state-root.sh | gstack | gstack-state-root.sh | binary | skip | none | 0 | gstack-state-root.sh is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-taste-update | gstack | gstack-taste-update | binary | skip | none | 0 | gstack-taste-update is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-team-init | gstack | gstack-team-init | binary | skip | none | 0 | gstack-team-init is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-telemetry-log | gstack | gstack-telemetry-log | binary | skip | none | 0 | gstack-telemetry-log is product telemetry. HStack does not send usage data. |
| gstack:binary:gstack-telemetry-sync | gstack | gstack-telemetry-sync | binary | skip | none | 0 | gstack-telemetry-sync is product telemetry. HStack does not send usage data. |
| gstack:binary:gstack-timeline-log | gstack | gstack-timeline-log | binary | skip | none | 0 | gstack-timeline-log is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-timeline-read | gstack | gstack-timeline-read | binary | skip | none | 0 | gstack-timeline-read is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-tree-receipt | gstack | gstack-tree-receipt | binary | skip | none | 0 | gstack-tree-receipt is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-ubi | gstack | gstack-ubi | binary | skip | none | 0 | gstack-ubi talks to Ubicloud. Paid VMs are out of scope. |
| gstack:binary:gstack-uninstall | gstack | gstack-uninstall | binary | skip | none | 0 | gstack-uninstall is that product's installer maintenance. HStack's upgrade is re-running install.sh. |
| gstack:binary:gstack-update-channel.sh | gstack | gstack-update-channel.sh | binary | skip | none | 0 | gstack-update-channel.sh is that product's installer maintenance. HStack's upgrade is re-running install.sh. |
| gstack:binary:gstack-update-check | gstack | gstack-update-check | binary | skip | none | 0 | gstack-update-check is that product's installer maintenance. HStack's upgrade is re-running install.sh. |
| gstack:binary:gstack-upgrade | gstack | gstack-upgrade | binary | skip | none | 0 | gstack-upgrade is that product's installer maintenance. HStack's upgrade is re-running install.sh. |
| gstack:binary:gstack-verify-gate | gstack | gstack-verify-gate | binary | routed-reference | references/qa.md | qa | The gate is a check you ran, from the qa or prove path. |
| gstack:binary:gstack-version-bump | gstack | gstack-version-bump | binary | skill | skills/hstack/ship/SKILL.md | skill:ship | gstack-version-bump bumps versions or writes a ship queue. Ship opens a pull request and does not bump a version. |
| gstack:binary:gstack-windows-bash.ts | gstack | gstack-windows-bash.ts | binary | skip | none | 0 | gstack-windows-bash.ts is runtime plumbing for that stack's session, paths, or render pipeline. It is not a user workflow. The matching job is in the feature table. |
| gstack:binary:gstack-worktree-audit | gstack | gstack-worktree-audit | binary | routed-reference | references/worktree.md | worktree | Audit worktrees with /worktree and git. This audit binary is not copied. |
| gstack:binary:gstack-wtree | gstack | gstack-wtree | binary | routed-reference | references/worktree.md | worktree | Create and remove worktrees with /worktree. |
| pstack:script:skills-poteto-mode-scripts-bootstrap.ts | pstack | skills/poteto-mode/scripts/bootstrap.ts | script | skip | none | 0 | Cursor plugin bootstrap. HStack's installer is install.sh. |
| pstack:script:skills-poteto-mode-scripts-check-plan.mjs | pstack | skills/poteto-mode/scripts/check-plan.mjs | script | routed-reference | references/spec.md | spec | Plan checking is /plan plus the spec route. This script is not copied. |
| pstack:script:skills-poteto-mode-scripts-check-plan.test.ts | pstack | skills/poteto-mode/scripts/check-plan.test.ts | script | skip | none | 0 | skills/poteto-mode/scripts/check-plan.test.ts is an upstream unit test. Not a user feature and not copied. |
| pstack:script:skills-poteto-mode-scripts-package.json | pstack | skills/poteto-mode/scripts/package.json | script | skip | none | 0 | skills/poteto-mode/scripts/package.json is package metadata for an upstream tool. Not installed. |
| pstack:script:skills-poteto-mode-scripts-watch-pr-cli.ts | pstack | skills/poteto-mode/scripts/watch-pr/cli.ts | script | helper-script | bin/hstack-pr | overnight | skills/poteto-mode/scripts/watch-pr/cli.ts is the upstream pull request watcher. Replaced by an original one-shot gh helper plus /loop. |
| pstack:script:skills-poteto-mode-scripts-watch-pr-cli.test.ts | pstack | skills/poteto-mode/scripts/watch-pr/cli.test.ts | script | skip | none | 0 | skills/poteto-mode/scripts/watch-pr/cli.test.ts is an upstream unit test. Not a user feature and not copied. |
| pstack:script:skills-poteto-mode-scripts-watch-pr-github.ts | pstack | skills/poteto-mode/scripts/watch-pr/github.ts | script | helper-script | bin/hstack-pr | overnight | skills/poteto-mode/scripts/watch-pr/github.ts is the upstream pull request watcher. Replaced by an original one-shot gh helper plus /loop. |
| pstack:script:skills-poteto-mode-scripts-watch-pr-github.test.ts | pstack | skills/poteto-mode/scripts/watch-pr/github.test.ts | script | skip | none | 0 | skills/poteto-mode/scripts/watch-pr/github.test.ts is an upstream unit test. Not a user feature and not copied. |
| pstack:script:skills-poteto-mode-scripts-watch-pr-policy.ts | pstack | skills/poteto-mode/scripts/watch-pr/policy.ts | script | helper-script | bin/hstack-pr | overnight | skills/poteto-mode/scripts/watch-pr/policy.ts is the upstream pull request watcher. Replaced by an original one-shot gh helper plus /loop. |
| pstack:script:skills-poteto-mode-scripts-watch-pr-policy.test.ts | pstack | skills/poteto-mode/scripts/watch-pr/policy.test.ts | script | skip | none | 0 | skills/poteto-mode/scripts/watch-pr/policy.test.ts is an upstream unit test. Not a user feature and not copied. |
| pstack:script:skills-poteto-mode-scripts-watch-pr-render.ts | pstack | skills/poteto-mode/scripts/watch-pr/render.ts | script | helper-script | bin/hstack-pr | overnight | skills/poteto-mode/scripts/watch-pr/render.ts is the upstream pull request watcher. Replaced by an original one-shot gh helper plus /loop. |
| pstack:script:skills-poteto-mode-scripts-watch-pr-types.ts | pstack | skills/poteto-mode/scripts/watch-pr/types.ts | script | helper-script | bin/hstack-pr | overnight | skills/poteto-mode/scripts/watch-pr/types.ts is the upstream pull request watcher. Replaced by an original one-shot gh helper plus /loop. |
| pstack:script:skills-poteto-mode-scripts-watch-pr-types.compile.ts | pstack | skills/poteto-mode/scripts/watch-pr/types.compile.ts | script | helper-script | bin/hstack-pr | overnight | skills/poteto-mode/scripts/watch-pr/types.compile.ts is the upstream pull request watcher. Replaced by an original one-shot gh helper plus /loop. |
| pstack:script:skills-poteto-mode-scripts-watch-pr-fakes.test-helper.ts | pstack | skills/poteto-mode/scripts/watch-pr/fakes.test-helper.ts | script | skip | none | 0 | skills/poteto-mode/scripts/watch-pr/fakes.test-helper.ts is an upstream unit test. Not a user feature and not copied. |
| pstack:script:skills-poteto-mode-scripts-watch-pr-tsconfig.json | pstack | skills/poteto-mode/scripts/watch-pr/tsconfig.json | script | skip | none | 0 | skills/poteto-mode/scripts/watch-pr/tsconfig.json is package metadata for an upstream tool. Not installed. |
| pstack:script:skills-poteto-mode-scripts-worktree-audit.sh | pstack | skills/poteto-mode/scripts/worktree-audit.sh | script | routed-reference | references/worktree.md | worktree | Worktree audit is /worktree. The shell script is not copied. |
| pstack:script:skills-show-me-your-work-scripts-log.sh | pstack | skills/show-me-your-work/scripts/log.sh | script | helper-script | bin/hstack-decisions | decisions | Decision log helper. Replaced by an original trail script, not this file. |
| pstack:script:skills-statechart-scripts-pipeline.ts | pstack | skills/statechart/scripts/pipeline.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/pipeline.ts is part of the statechart compiler. The verify route states the property. The compiler is not copied. |
| pstack:script:skills-statechart-scripts-run.ts | pstack | skills/statechart/scripts/run.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/run.ts is part of the statechart compiler. The verify route states the property. The compiler is not copied. |
| pstack:script:skills-statechart-scripts-statechart.ts | pstack | skills/statechart/scripts/statechart.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/statechart.ts is part of the statechart compiler. The verify route states the property. The compiler is not copied. |
| pstack:script:skills-statechart-scripts-worker.ts | pstack | skills/statechart/scripts/worker.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/worker.ts is part of the statechart compiler. The verify route states the property. The compiler is not copied. |
| pstack:script:skills-statechart-scripts-ir.ts | pstack | skills/statechart/scripts/ir.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/ir.ts is part of the statechart compiler. The verify route states the property. The compiler is not copied. |
| pstack:script:skills-statechart-scripts-package.json | pstack | skills/statechart/scripts/package.json | script | skip | none | 0 | skills/statechart/scripts/package.json is package metadata for an upstream tool. Not installed. |
| pstack:script:skills-statechart-scripts-tsconfig.json | pstack | skills/statechart/scripts/tsconfig.json | script | skip | none | 0 | skills/statechart/scripts/tsconfig.json is package metadata for an upstream tool. Not installed. |
| pstack:script:skills-statechart-scripts-backends-cfg.ts | pstack | skills/statechart/scripts/backends/cfg.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/backends/cfg.ts is a compiler pass or renderer for statecharts. Not copied. The verify route keeps the property and an optional mermaid sketch. |
| pstack:script:skills-statechart-scripts-backends-mermaid.ts | pstack | skills/statechart/scripts/backends/mermaid.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/backends/mermaid.ts is a compiler pass or renderer for statecharts. Not copied. The verify route keeps the property and an optional mermaid sketch. |
| pstack:script:skills-statechart-scripts-backends-plain-text.ts | pstack | skills/statechart/scripts/backends/plain-text.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/backends/plain-text.ts is a compiler pass or renderer for statecharts. Not copied. The verify route keeps the property and an optional mermaid sketch. |
| pstack:script:skills-statechart-scripts-backends-report.ts | pstack | skills/statechart/scripts/backends/report.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/backends/report.ts is a compiler pass or renderer for statecharts. Not copied. The verify route keeps the property and an optional mermaid sketch. |
| pstack:script:skills-statechart-scripts-frontends-config.ts | pstack | skills/statechart/scripts/frontends/config.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/frontends/config.ts is a compiler pass or renderer for statecharts. Not copied. The verify route keeps the property and an optional mermaid sketch. |
| pstack:script:skills-statechart-scripts-frontends-dot.ts | pstack | skills/statechart/scripts/frontends/dot.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/frontends/dot.ts is a compiler pass or renderer for statecharts. Not copied. The verify route keeps the property and an optional mermaid sketch. |
| pstack:script:skills-statechart-scripts-frontends-marks.ts | pstack | skills/statechart/scripts/frontends/marks.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/frontends/marks.ts is a compiler pass or renderer for statecharts. Not copied. The verify route keeps the property and an optional mermaid sketch. |
| pstack:script:skills-statechart-scripts-frontends-messages.ts | pstack | skills/statechart/scripts/frontends/messages.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/frontends/messages.ts is a compiler pass or renderer for statecharts. Not copied. The verify route keeps the property and an optional mermaid sketch. |
| pstack:script:skills-statechart-scripts-frontends-spec.ts | pstack | skills/statechart/scripts/frontends/spec.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/frontends/spec.ts is a compiler pass or renderer for statecharts. Not copied. The verify route keeps the property and an optional mermaid sketch. |
| pstack:script:skills-statechart-scripts-frontends-trace.ts | pstack | skills/statechart/scripts/frontends/trace.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/frontends/trace.ts is a compiler pass or renderer for statecharts. Not copied. The verify route keeps the property and an optional mermaid sketch. |
| pstack:script:skills-statechart-scripts-frontends-value.ts | pstack | skills/statechart/scripts/frontends/value.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/frontends/value.ts is a compiler pass or renderer for statecharts. Not copied. The verify route keeps the property and an optional mermaid sketch. |
| pstack:script:skills-statechart-scripts-frontends-verdict.ts | pstack | skills/statechart/scripts/frontends/verdict.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/frontends/verdict.ts is a compiler pass or renderer for statecharts. Not copied. The verify route keeps the property and an optional mermaid sketch. |
| pstack:script:skills-statechart-scripts-frontends-view.ts | pstack | skills/statechart/scripts/frontends/view.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/frontends/view.ts is a compiler pass or renderer for statecharts. Not copied. The verify route keeps the property and an optional mermaid sketch. |
| pstack:script:skills-statechart-scripts-passes-annotate.ts | pstack | skills/statechart/scripts/passes/annotate.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/passes/annotate.ts is a compiler pass or renderer for statecharts. Not copied. The verify route keeps the property and an optional mermaid sketch. |
| pstack:script:skills-statechart-scripts-passes-label.ts | pstack | skills/statechart/scripts/passes/label.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/passes/label.ts is a compiler pass or renderer for statecharts. Not copied. The verify route keeps the property and an optional mermaid sketch. |
| pstack:script:skills-statechart-scripts-passes-lift.ts | pstack | skills/statechart/scripts/passes/lift.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/passes/lift.ts is a compiler pass or renderer for statecharts. Not copied. The verify route keeps the property and an optional mermaid sketch. |
| pstack:script:skills-statechart-scripts-passes-loop-check.ts | pstack | skills/statechart/scripts/passes/loop-check.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/passes/loop-check.ts is a compiler pass or renderer for statecharts. Not copied. The verify route keeps the property and an optional mermaid sketch. |
| pstack:script:skills-statechart-scripts-passes-paths.ts | pstack | skills/statechart/scripts/passes/paths.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/passes/paths.ts is a compiler pass or renderer for statecharts. Not copied. The verify route keeps the property and an optional mermaid sketch. |
| pstack:script:skills-statechart-scripts-passes-reach.ts | pstack | skills/statechart/scripts/passes/reach.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/passes/reach.ts is a compiler pass or renderer for statecharts. Not copied. The verify route keeps the property and an optional mermaid sketch. |
| pstack:script:skills-statechart-scripts-passes-region-check.ts | pstack | skills/statechart/scripts/passes/region-check.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/passes/region-check.ts is a compiler pass or renderer for statecharts. Not copied. The verify route keeps the property and an optional mermaid sketch. |
| pstack:script:skills-statechart-scripts-passes-regions.ts | pstack | skills/statechart/scripts/passes/regions.ts | script | routed-reference | references/verify.md | verify | skills/statechart/scripts/passes/regions.ts is a compiler pass or renderer for statecharts. Not copied. The verify route keeps the property and an optional mermaid sketch. |
| tstack:script:skills-babysit-pr-scripts-pr-wait | tstack | skills/babysit-pr/scripts/pr-wait | script | helper-script | bin/hstack-pr | overnight | Python waiter, about 6,200 tokens upstream. Not copied. hstack-pr is one gh snapshot. /loop repeats it. |
| tstack:script:skills-full-send-agents-openai.yaml | tstack | skills/full-send/agents/openai.yaml | script | skip | none | 0 | Codex app metadata for full-send. Hermes does not read this file. |
| tstack:script:skills-full-stop-agents-openai.yaml | tstack | skills/full-stop/agents/openai.yaml | script | skip | none | 0 | Codex app metadata for full-stop. Hermes does not read this file. |
| tstack:script:skills-leaving-pr-comments-agents-openai.yaml | tstack | skills/leaving-pr-comments/agents/openai.yaml | script | skip | none | 0 | Codex app metadata for comment style. Ship states the rule in our words. |
| tstack:script:skills-modernize-agents-openai.yaml | tstack | skills/modernize/agents/openai.yaml | script | skip | none | 0 | Codex app metadata for modernize. The modernize skill does not need it. |
| gstack:script:scripts-gen-skill-docs.ts | gstack | scripts/gen-skill-docs.ts | script | skip | none | 0 | scripts/gen-skill-docs.ts is a build or docs generator for that repo. It is not a user command and is not copied. |
| gstack:script:scripts-discover-skills.ts | gstack | scripts/discover-skills.ts | script | skip | none | 0 | scripts/discover-skills.ts is a build or docs generator for that repo. It is not a user command and is not copied. |
| gstack:script:scripts-skill-check.ts | gstack | scripts/skill-check.ts | script | skip | none | 0 | scripts/skill-check.ts is a build or docs generator for that repo. It is not a user command and is not copied. |
| gstack:script:scripts-resolvers-browse.ts | gstack | scripts/resolvers/browse.ts | script | routed-reference | references/browse.md | browse | scripts/resolvers/browse.ts builds that browser daemon. browser_exec is the runtime. |
| gstack:script:scripts-resolvers-qa.ts | gstack | scripts/resolvers/qa.ts | script | routed-reference | references/browse.md | browse | scripts/resolvers/qa.ts builds that browser daemon. browser_exec is the runtime. |
| gstack:script:scripts-resolvers-review-army.ts | gstack | scripts/resolvers/review-army.ts | script | skill | skills/hstack/council/SKILL.md | skill:council | scripts/resolvers/review-army.ts assembles a cross-model review army. Council is the panel. The generator is not copied. |
| gstack:script:scripts-resolvers-design.ts | gstack | scripts/resolvers/design.ts | script | routed-reference | references/design.md | design | scripts/resolvers/design.ts generates design-studio sections. The design route is handwritten. |
| gstack:script:scripts-resolvers-gbrain.ts | gstack | scripts/resolvers/gbrain.ts | script | routed-reference | references/memory.md | memory | scripts/resolvers/gbrain.ts wires a second brain. The memory route does not. |
| gstack:script:scripts-resolvers-outside-voice.ts | gstack | scripts/resolvers/outside-voice.ts | script | skill | skills/hstack/council/SKILL.md | skill:council | scripts/resolvers/outside-voice.ts assembles a cross-model review army. Council is the panel. The generator is not copied. |
| gstack:script:scripts-resolvers-testing.ts | gstack | scripts/resolvers/testing.ts | script | skip | none | 0 | scripts/resolvers/testing.ts is a build or docs generator for that repo. It is not a user command and is not copied. |
| gstack:script:scripts-cso-scanner-catalog.ts | gstack | scripts/cso-scanner-catalog.ts | script | routed-reference | references/security.md | security | scripts/cso-scanner-catalog.ts builds a container scanner catalog. The security route stays on the diff and optional local scanners. |
| gstack:script:scripts-build.sh | gstack | scripts/build.sh | script | skip | none | 0 | scripts/build.sh is a build or docs generator for that repo. It is not a user command and is not copied. |
| gstack:script:scripts-build-cso.sh | gstack | scripts/build-cso.sh | script | routed-reference | references/security.md | security | scripts/build-cso.sh builds a container scanner catalog. The security route stays on the diff and optional local scanners. |
| gstack:script:scripts-app-gstack-browser | gstack | scripts/app/gstack-browser | script | routed-reference | references/browse.md | browse | scripts/app/gstack-browser builds that browser daemon. browser_exec is the runtime. |
| gstack:script:setup | gstack | setup | script | skip | none | 0 | setup installs that stack into many hosts. HStack's installer is install.sh and install.ps1, skills by default. |
| gstack:script:setup.ps1 | gstack | setup.ps1 | script | skip | none | 0 | setup.ps1 installs that stack into many hosts. HStack's installer is install.sh and install.ps1, skills by default. |
| gstack:script:scripts-ci-and-generators | gstack | scripts-ci-and-generators | script | skip | none | 0 | The remaining files under scripts/ are eval shards, paid-test planners, release stamps, and skill renderers. They build that repo. They are not user workflows. User-facing resolvers are the rows above. |
