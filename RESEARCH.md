# HStack research

Phase 1 only. This file inventories Hermes Agent, GStack, PStack, and TStack, then decides what a Hermes-native stack should keep. No skills are implemented here. The build plan is [PLAN.md](PLAN.md).

Measured on 28 October 2026 from these commits:

| Source | Commit | License line |
|---|---|---|
| [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | `ee7e0f517232fb619c72e49d7e648436bddc598e` | MIT. Copyright (c) 2025 Nous Research |
| [garrytan/gstack](https://github.com/garrytan/gstack) | `6f27f0c269cb33ad60b300ec10df63c2b9f296ba` (version `1.91.291.0`) | MIT. Copyright (c) 2026 Garry Tan |
| [t3dotgg/tstack](https://github.com/t3dotgg/tstack) | `1085050f3baed1ac724caa4a8166145fb2ac88af` | MIT. Copyright (c) 2026 Theo Browne |
| [cursor/plugins](https://github.com/cursor/plugins/tree/main/pstack) `pstack/` | `c742dd61706fbacc1b95f1a20b7b988cf096ce6c` (plugin `0.15.36`) | MIT. Copyright (c) 2026 Lauren Tan |

PStack has no standalone public repository under poteto's account. The copy used here is Cursor's own plugin tree, linked from [cursor.com/marketplace/cursor/pstack](https://cursor.com/marketplace/cursor/pstack) and from `plugin.json` (`repository`: `https://github.com/cursor/plugins`). Third-party GitHub mirrors were not used.

## How tokens were counted

Hermes estimates tokens as `ceil(utf-8 bytes / 4)`, with CJK counted one token per character. The function is `estimate_tokens_rough` in `agent/model_metadata.py`, and `CHARS_PER_TOKEN = 4`. Every number below uses that function. Skill text here is ASCII, so the estimate is exact for Hermes's own budget math. It is not a tokenizer for one model.

Two costs matter:

- **Idle.** Hermes puts one index row per skill in the system prompt and clips the description to 60 characters (`SKILL_PROMPT_DESC_LIMIT` in `agent/skill_utils.py`). The row is `    - <name>: <clipped description>`, under a category header. That row is the idle cost. The shared "## Skills" preamble is about 273 tokens plus a 20-token footer (`agent/prompt_builder.py`, `_render_skills_index`). It is paid once per session for every skill the profile has, so it is not counted against HStack or GStack.
- **Body.** `skill_view(name)` returns the whole `SKILL.md`. That is the level-1 cost. Files under `references/`, `sections/`, or `scripts/` load only when a later `skill_view(name, path)` or a read asks for them.

GStack on Hermes installs each skill as `gstack-<name>` in the category `gstack` (`docs/hosts.md`). The GStack index tokens below use that prefixed name. PStack and TStack tokens use each skill's own `name:`, which is what Hermes would index if the folders were copied in.

## License call

All four sources are MIT, so reuse with the copyright and permission notice is allowed. This repository does not copy skill text, scripts, or word lists from any of them. A `NOTICE` file is not required until we include a substantial portion of someone else's software. Phase 2 should keep writing in our own words, for the same reason: one voice, and no notice to maintain.

GStack's own `NOTICE.md` is the map of what a port would drag along. It records derived work from impeccable (Paul Bakaus, Apache-2.0), ai-design-skills (Elaya, MIT), hallmark (MIT), Google's DESIGN.md spec (Apache-2.0), skill-diet (Nico Bailon, MIT), TStack (Theo Browne, MIT), and PStack (Lauren Tan, MIT). Some of those entries are ideas GStack rewrote and marked as courtesy. Two are real code ports (`gstack-decision-trail`, `gstack-worktree-audit`) that carry PStack's MIT text, and the unslop word lists in `lib/prose-lint.ts` are taken from PStack's unslop rules. HStack will not port those files. We also will not add courtesy credits. The MIT notice is the only credit the license requires, and it applies only to portions we actually include.

Hermes documents say its skill format is compatible with [agentskills.io](https://agentskills.io/specification). Citing that, and citing the files above, is not a redistribution.

## Hermes Agent

Docs used, all in the hermes-agent tree and published at `https://hermes-agent.nousresearch.com/docs/`:

- `website/docs/user-guide/features/skills.md` — discovery, progressive disclosure, `SKILL.md` shape, slash commands, external dirs
- `website/docs/developer-guide/creating-skills.md` — directory layout, frontmatter, conditional activation
- `skills/software-development/hermes-agent-skill-authoring/SKILL.md` — the repo's hardline (60-character descriptions)
- `agent/prompt_builder.py`, `agent/skill_utils.py`, `tools/skills_tool.py` — what actually lands in the prompt
- `website/docs/user-guide/features/memory.md`, `delegation.md`, `context-files.md`, `goals.md`, `mixture-of-agents.md`
- `website/docs/reference/slash-commands.md`, `website/docs/user-guide/security.md`
- `website/docs/developer-guide/context-compression-and-caching.md`
- `website/docs/user-guide/configuring-models.md`, `website/docs/reference/model-catalog.md`
- `hermes_cli/models_catalog_static.py` (`PREFERRED_SILENT_DEFAULT_MODEL`)
- `toolsets.py` — tool names
- `README.md` — provider stance

### How a skill is found and loaded

Skills are directories with a `SKILL.md`. On a normal install they live in `~/.hermes/skills/<category>/<name>/SKILL.md`. Bundled skills are copied there on first setup. Hub installs, agent-written skills, and `skills.external_dirs` are scanned too. Precedence is project, then `~/.hermes/skills/`, then `skills.create_dir`, then external dirs. The same name in a higher tier shadows the others.

A skill is a slash command, `/<name>`, on the CLI and on messaging gateways. Up to five leading skill names can be stacked. `/plan` used to be a skill and is now a built-in. If a skill name collides with a built-in, the built-in wins and the skill is only reachable as `/skill <name>`.

Loading is three levels:

1. The system prompt lists `name`, a clipped description, and the category. The docs call `skills_list()` about 3,000 tokens for the bundled catalog. The index is part of the cached system prompt. A skill installed mid-conversation is announced once on the next user message. The prompt itself updates at the next compaction. `/reload-skills` refreshes slash commands. It is not required for the index.
2. `skill_view(name)` returns the full `SKILL.md` plus metadata.
3. `skill_view(name, path)` returns one linked file (`references/`, `templates/`, `scripts/`, `assets/`).

The prompt tells the agent to load a skill when it is even partly relevant, and to patch a skill that was wrong. Plugin skills registered in process are not in the index until loaded by name.

`platforms: [linux, macos, windows]` hides a skill on other operating systems. `metadata.hermes.requires_toolsets` / `requires_tools` hide it when those tools are absent. `fallback_for_toolsets` / `fallback_for_tools` hide it when a richer tool is already available. That is how a skill stays out of the index on a session that does not need it.

### File format

Hermes accepts an agentskills.io-style file: YAML frontmatter between `---` lines, then a markdown body. The validator (`tools/skill_manager_tool.py`) requires `name` and `description` (hard ceiling 1,024 characters) and a non-empty body. The repo's authoring standard is stricter and is the one HStack should follow:

- `description` is at most 60 characters, one sentence, ends with a period. The index clips anything longer on a word boundary and adds `...`. `skill_manage` rejects a new or edited description over 60.
- `name` is lowercase, hyphenated, at most 64 characters.
- Expected fields: `version` (start at `0.1.0`), `author`, `license`, `platforms`, and `metadata.hermes.tags` plus `related_skills`.
- A colon inside an unquoted description breaks the docs generator. Quote it.

Optional blocks the docs support and HStack does not need for v0.1: `config` prompts, `required_environment_variables`, cron `blueprint`, and inline shell snippets (`` !`cmd` ``). Those snippets are off by default because they run on the host without approval. Community hub installs do not get to turn them on.

### Tools a skill can actually call

Names from `toolsets.py`. GStack's Hermes host (`hosts/hermes.ts`) rewrites Claude Code tool names onto a smaller set and misses some of these.

| Hermes tool | What it is |
|---|---|
| `terminal`, `process_manage` | Shell and background processes |
| `read_file`, `write_file`, `patch`, `search_files` | Files. New files are `write_file`. Edits are `patch`. |
| `web_search`, `web_extract` | Web |
| `browser_exec` | The browser tool (Python over CDP) |
| `clarify` | One question to the user. This is what GStack's host maps `AskUserQuestion` onto. |
| `delegate_task` | Subagents |
| `skill_view`, `skills_list`, `skill_manage` | Skills |
| `memory` | `MEMORY.md` and `USER.md` |
| `session_search` | Search past sessions |
| `execute_code` | A script that can call tools, so a long pipeline does not sit in the chat |

GStack's Hermes rewrite maps both Write and Edit to `patch`, and Grep/Glob to prose ("search for", "find files matching"). A native skill should use the real tool names.

### Memory

`MEMORY.md` is capped at 2,200 characters and `USER.md` at 1,375. Both live in `~/.hermes/memories/` and are injected once, at session start, so the prompt cache stays valid. The agent writes them with the `memory` tool. Overflow is an error, not a silent trim. `session_search` is how a later session gets back detail that was not worth a memory slot. `/new` is the boundary that makes this work. A gateway chat that never resets is one long session.

External memory providers exist. GBrain is not one of them unless the user installs it.

### Subagents

`delegate_task` starts a child with a fresh conversation. The child does not see the parent's history. The parent must pass `goal` and `context`. Children inherit the workspace's project context files (`.hermes.md`, `AGENTS.md`, `CLAUDE.md`, `.cursorrules`), not `SOUL.md`. A batch can run in parallel. The default cap is 10 concurrent children (`delegation.max_concurrent_children`), configurable, with no hard ceiling. An optional `output_schema` is checked, with one correction turn.

`/review` spawns one independent reviewer over the last work discussed and posts the review back into the session. Its model is `auxiliary.review`, or the main model if that is unset. `/bg` is a side session. Top-level delegations return a handle and finish in the background.

`delegation.model` can pin a cheaper model for children while the parent stays on a frontier model. That is the native place for "workers are cheap, judgment is not."

### Slash commands that already cover stack ideas

From `website/docs/reference/slash-commands.md`, the ones that collide with these stacks:

| Command | What it already does |
|---|---|
| `/plan` | Write an implementation plan under `.hermes/plans/`. Does not run a product review. |
| `/review` | One independent reviewer subagent. |
| `/goal`, `/subgoal` | Keep working across turns until a judge says done. Default budget 20 turns. |
| `/loop`, `/heartbeat` | Re-enter this session on an interval. |
| `/learn` | Turn notes, a doc, or the last workflow into a skill. Large sources become a `SKILL.md` plus `references/`. |
| `/refine` | Background pass that updates memory and skills. |
| `/model` | Switch provider and model. Optional reasoning effort. |
| `/moa` | Run one prompt through a Mixture of Agents preset. The aggregator is the model that acts. References advise. This is not a read-only review panel. |
| `/compress`, `/context` | Compact, and show per-skill index cost versus load cost. |
| `/worktree` | Isolated git worktrees. |
| `/status` | Local session recap. No model call. |

Do not ship a HStack skill named `plan`, `review`, `learn`, `goal`, `loop`, `model`, `context`, `status`, `skills`, `help`, `compress`, `snapshot`, or `worktree`.

### Context budget

Compaction defaults to 50% of the model's context window (`compression.threshold: 0.50` in `website/docs/developer-guide/context-compression-and-caching.md`). The lean tail keeps about 2.5% of the window, clamped between 10k and 25k tokens, plus a summary, an anchor index, and a pointer to `session_search`. Context files (`.hermes.md`, `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `.cursor/rules/*.mdc`, global `SOUL.md`) are injected with their own size cap. One project context type wins. `SOUL.md` always loads from `HERMES_HOME`.

The skill index is the part of this a stack controls. Every extra skill is another always-on row, whether or not the task needs it. A 15,000-token `SKILL.md` does not cost 15,000 tokens while idle. It costs that the moment the agent follows the "load it if relevant" instruction, which the system prompt tells it to do generously.

### Models

Hermes is not tied to a model. The README says to use Nous Portal, OpenRouter, OpenAI, or another endpoint, and to switch with `hermes model`. Nous Portal is documented as one subscription over 300+ models.

When the user never picks, the catalog's silent default is `z-ai/glm-5.3` (`PREFERRED_SILENT_DEFAULT_MODEL` in `hermes_cli/models_catalog_static.py`, and the `"default": true` entry for both OpenRouter and Nous in `website/docs/reference/model-catalog.md`). That default is described as a capable cheap model, not a flagship. An explicit `model.default` example in the configuring-models doc is `anthropic/claude-opus-4.7`. That is an example configuration, not the silent default.

Auxiliary jobs (compression, titles, vision, the approval classifier, web extract) can be pinned to a cheaper model. There is no PStack-style per-role model table inside the skill format. Role routing belongs in `delegation.model`, `auxiliary.review`, and `/model`.

### What GStack's Hermes host does not do

`hosts/hermes.ts` marks Hermes `experimental`. `planMode: false`. Safety hooks are advisory, not blocking. These resolvers are suppressed (`hosts/define-host.ts`, `CROSS_MODEL_RESOLVERS`): `DESIGN_OUTSIDE_VOICES`, `ADVERSARIAL_STEP`, `CODEX_SECOND_OPINION`, `CODEX_PLAN_REVIEW`, `REVIEW_ARMY`. The outside-model review army does not run. GBrain resolvers stay compiled in and no-op when GBrain is absent. Install is `./setup --host hermes` or automatic when `HERMES_AGENT=true`, writing `gstack-<skill>` under `${HERMES_HOME:-~/.hermes}/skills/gstack`. Frontmatter keeps only `name` and `description`, with no description limit on the way in. Hermes then clips the description to 60 characters anyway.

So "install GStack into Hermes" copies Claude-sized bodies, strips the cross-model reviews, and shows a clipped one-liner. The bodies still tell the agent to use paths like `~/.claude/skills/gstack/...` until the host rewriter runs, and they still say to read a shared preamble.

## GStack

Public inventory from `README.md` and `AGENTS.md` at the commit above. 61 unique skills. `connect-chrome` is a symlink of `open-gstack-browser` and is not counted twice. `claude-code/` has `SKILL.md.tmpl` only, so it is not an installed skill in this checkout even though `AGENTS.md` lists `/claude-code`. OpenClaw copies, the Capy bundle, browser-skill examples, and test fixtures are not user skills.

46 of the 61 tell the agent to read `sections/preamble.md` before the command. That file is about 5,600 tokens. The skill says to skip it if the same preamble id is already in context, so a session pays it once, not once per skill. Many skills then point at more section files. Those are level-2 costs. The table is level-0 and level-1 only.

Index total for the 61 prefixed names: **1,182 tokens**. Sum of `SKILL.md` files: **420,401 tokens**. 34 descriptions are longer than 60 characters, so Hermes clips them and the idle row is dumber than the author wrote.

What each skill is for:

**Frame and plan.** `office-hours` reframes a product idea before code (two modes, 10,972-token body). `plan-ceo-review` looks for a sharper product inside the request. `plan-eng-review` locks architecture, data flow, edges, and tests. `plan-design-review` scores design dimensions. `plan-devex-review` walks developer-experience friction, often with dozens of questions. `autoplan` runs CEO, then design, then DX, then eng, and its description says it reads those skills from disk. `plan-tune` tunes how often the stack asks the user. `spec` turns intent into a five-phase spec, can file a GitHub issue, and can spawn Claude Code. `design-consultation` builds a design system and a `DESIGN.md`.

**Build, review, debug.** `review` is the pre-landing bug pass and the gate-integrity list (weakened tests, timeouts, snapshots). 14,728 tokens. `investigate` is root-cause debugging with no fix first. `deslop-shared-libs` recommends shared-code extractions and does not edit. `test-audit` lists low-value tests and waits for approval. `write-skill` is GStack's skill editor, including a size bill and a diet. `codex` shells out to the Codex CLI for a second opinion. The Claude Code twin is the template noted above.

**Design and browser, tied to Aside or GStack's Chromium.** `design-review`, `design-shotgun`, `design-html`, `design-motion`, `devex-review`, `browse`, `open-gstack-browser`, `setup-browser-cookies`, `scrape`, `skillify`, `pair-agent`, `make-pdf`, `diagram`. `design-review` is the largest body in the repo at 21,217 tokens. `qa` reproduces bugs on browser, API, CLI, job, worker, and webhook surfaces and fixes them. `qa-only` reports and does not edit product code.

**Release.** `ship` tests, reviews, bumps VERSION, updates CHANGELOG, pushes, opens a PR (15,240 tokens). `land-and-deploy` merges and checks production. `setup-deploy` detects a host. `canary` watches a deploy in the browser. `landing-report` is a read-only ship-queue dashboard. `modernize` rebases an old PR and chooses MODERNIZE, REWORK, or CLOSE, and does not close by itself. `document-release` and `document-generate` cover docs, the latter in the Diátaxis shapes. `gstack-upgrade` updates GStack.

**Memory and ops.** `context-save`, `context-restore`, `learn` (GStack's own learning store), `setup-gbrain`, `sync-gbrain`, `retro`, `health`, `benchmark`, `benchmark-models`, `eval-plan`, `ubicloud` (ephemeral 16-vCPU VMs), `captain` (a crew controller, also `/crew`).

**Safety.** `careful`, `freeze`, `guard` (both), `unfreeze`. These are Claude Code hooks. On Hermes the host marks safety advisory.

**Security and iOS.** `cso` is a security audit with optional Docker scanner images. `ios-qa`, `ios-fix`, `ios-design-review`, `ios-clean`, `ios-sync` drive a real iPhone through a debug bridge.

| Skill | Desc chars | Hermes index tokens | SKILL.md tokens | Loads 5.6k preamble |
|---|---:|---:|---:|:---:|
| `autoplan` | 171 | 21 | 10801 | yes |
| `benchmark` | 46 | 18 | 7823 |  |
| `benchmark-models` | 49 | 20 | 3909 |  |
| `browse` | 128 | 20 | 8557 |  |
| `canary` | 39 | 15 | 7404 | yes |
| `captain` | 205 | 20 | 6434 | yes |
| `careful` | 52 | 19 | 1185 |  |
| `codex` | 48 | 18 | 9463 | yes |
| `context-restore` | 64 | 22 | 6016 | yes |
| `context-save` | 30 | 15 | 4881 | yes |
| `cso` | 110 | 19 | 4691 |  |
| `design-consultation` | 208 | 24 | 10059 | yes |
| `design-html` | 83 | 20 | 8511 | yes |
| `design-motion` | 84 | 22 | 4520 | yes |
| `design-review` | 150 | 22 | 21217 | yes |
| `design-shotgun` | 129 | 21 | 8915 | yes |
| `deslop-shared-libs` | 64 | 23 | 3263 |  |
| `devex-review` | 41 | 17 | 14642 | yes |
| `diagram` | 177 | 20 | 4100 |  |
| `document-generate` | 94 | 21 | 5753 | yes |
| `document-release` | 37 | 17 | 4262 | yes |
| `eval-plan` | 160 | 21 | 4676 | yes |
| `freeze` | 69 | 19 | 1066 |  |
| `gstack-upgrade` | 37 | 17 | 6025 |  |
| `guard` | 81 | 18 | 956 |  |
| `health` | 32 | 14 | 5565 | yes |
| `investigate` | 60 | 22 | 7459 | yes |
| `ios-clean` | 85 | 20 | 2331 | yes |
| `ios-design-review` | 59 | 23 | 2492 | yes |
| `ios-fix` | 34 | 14 | 2207 | yes |
| `ios-qa` | 45 | 17 | 5650 | yes |
| `ios-sync` | 86 | 19 | 2358 | yes |
| `land-and-deploy` | 34 | 16 | 12998 | yes |
| `landing-report` | 60 | 23 | 3128 | yes |
| `learn` | 25 | 12 | 2094 | yes |
| `make-pdf` | 63 | 20 | 4979 |  |
| `modernize` | 167 | 20 | 3609 | yes |
| `office-hours` | 37 | 17 | 10972 | yes |
| `open-gstack-browser` | 83 | 24 | 4662 |  |
| `pair-agent` | 50 | 19 | 5064 | yes |
| `plan-ceo-review` | 38 | 17 | 15095 | yes |
| `plan-design-review` | 75 | 23 | 14053 | yes |
| `plan-devex-review` | 54 | 22 | 11687 | yes |
| `plan-eng-review` | 38 | 17 | 10878 | yes |
| `plan-tune` | 99 | 18 | 8817 | yes |
| `qa` | 53 | 18 | 7314 | yes |
| `qa-only` | 56 | 20 | 5479 | yes |
| `retro` | 42 | 16 | 12901 | yes |
| `review` | 31 | 13 | 14728 | yes |
| `scrape` | 101 | 19 | 6997 |  |
| `setup-browser-cookies` | 89 | 24 | 3356 |  |
| `setup-deploy` | 51 | 20 | 5490 | yes |
| `setup-gbrain` | 154 | 21 | 9577 | yes |
| `ship` | 132 | 19 | 15240 | yes |
| `skillify` | 95 | 20 | 5596 | yes |
| `spec` | 74 | 20 | 8742 | yes |
| `sync-gbrain` | 98 | 21 | 9328 | yes |
| `test-audit` | 82 | 21 | 4422 | yes |
| `ubicloud` | 140 | 21 | 3439 | yes |
| `unfreeze` | 91 | 21 | 392 |  |
| `write-skill` | 122 | 22 | 2173 | yes |

A representative "plan the feature" load, if the agent does what `autoplan` says and reads the four review skills, is the five `SKILL.md` files: 10,801 + 15,095 + 14,053 + 11,687 + 10,878 = **62,514 tokens**, plus one preamble (~5,600) the first time, plus whichever section files those skills then open. `plan-eng-review` alone has about 31,000 tokens of sibling markdown.

## PStack

Cursor plugin by Lauren Tan (poteto). README: `pstack/README.md`. Guide: `pstack/docs/guide/`. 58 skills, plus 23 playbooks that are not separate skills. Playbooks live in `skills/poteto-mode/playbooks/` and add **19,154 tokens** when read. `poteto-mode` itself is 5,418 tokens and is the thing a user actually invokes.

Index total if copied into Hermes: **1,256 tokens**. Sum of `SKILL.md`: **55,797 tokens**. Full description fields sum to **3,055 tokens**, which is what a host that shows the whole description pays. **57 of 58 descriptions are over 60 characters.** On Hermes they are clipped, and the clip usually cuts off the trigger ("Use for /architect, 'architect this'..."). `unslop` is the one description that fits. The 24 `principle-*` skills alone cost **591 index tokens** for **8,369 tokens** of bodies, most of them a few hundred tokens. That is an expensive way to store short rules.

`statechart`'s `SKILL.md` is 2,275 tokens. The skill directory also holds hundreds of `.out`, `.tla`, and `.dot` fixtures, on the order of 700,000 tokens of text. Those are not part of the skill body and must not be installed into Hermes.

The summaries below are our wording of the public README and the principles guide. They are not the skill text. Phase 2 rewrites anything we keep. We do not copy the files.

**Entry.** `poteto-mode` matches a task to a playbook and runs other skills as the steps need them. `poteto-help` picks a skill and hands back a prompt. `setup-pstack` writes a Cursor rule (`~/.cursor/rules/pstack-models.mdc`, or the Claude path in the adapter) that maps roles to models. `sharpen` rewrites a prompt and does not do the task. `in-your-own-words` plays the goal back before work starts. `figure-it-out` invents a playbook when none fits.

**Understand.** `how` walks a subsystem. `why` asks why it is shaped that way and, in Cursor, queries whatever evidence MCPs are connected. `teach` combines those two into one explanation. `recall` rebuilds recent context from the user's own chats. `ketchup` summarizes the chat since the last user message. `ketchup-video` turns that into slides. `bro` restates the last reply in plain words.

**Change the code.** `architect` settles types and module shape before code crosses a function boundary. `arena` runs several attempts at one brief and keeps the best pieces. `swarm` runs workers on different slices, or races them, and returns one report. `interrogate` has different models try to break a diff and keeps findings a run can prove. `blast-radius` names what else a small diff can break and proves the one fact that makes it safe by running code. `tdd` writes a failing test first when a cheap local test exists. `benchmark-checklist` refuses a performance number that was not vetted (limiter, repeats, errors, whether the work happened).

**Prose and types.** `unslop` strips AI tells from writing. `no-comments` sends comments to a hostile reviewer pass. `technical-writing` applies a layered doc standard to docs, RFCs, READMEs, PR text, and commits. `typescript-best-practices` is the type-system principle specialized to TypeScript.

**Cursor-shaped extras.** `automate-me` drafts a personal mode skill from how the user works. `reflect` turns a finished task into a skill edit. `correct` mines repeated mistakes and tries to encode each one as a lint or a check. `show-me-your-work` appends a decision log. `make-bot-ui` builds a page whose buttons wake a Grok bot. `create-verification-skill` and `maintain-verification-skill` generate a project-local way to drive the app. The formal-verification pair does the same for one property a test cannot reach. `statechart` draws a user-visible state chart from a TLA+ model.

**Principles (24 skills, invoked by name, not as the main command).** From `docs/guide/08-principles.md`: prefer the smallest change; pick data structures first; fold a new requirement in as if it had always been there; test the premise shared by failed fixes; delete dead weight before adding; reduce what a reader must hold; aim rewrites at the end state; choose the user's result; try more than one design when there is no precedent; build a script a reviewer can rerun; put repeated rules in one structure; validate at the boundary; make illegal states unrepresentable; make retries converge; migrate callers and delete the old API in one wave; split shared state before coordinating it; prove the real artifact; fix causes, not symptoms; end each unit with a check; test observable behavior; explain a measured number before trusting it; send bulk reading to subagents; do reversible work without waiting; turn a repeated lesson into a check.

**Playbooks inside `poteto-mode` (23).** Investigation, bug fix, perf, hillclimb, runtime forensics, trace forensics, feature, refactoring, prototype, visual parity, authoring a skill, eval, babysit, shipping, autonomous run, orchestrate, autopilot-full, autopilot-stack, session pickup, pause safely, multi-phase plan, worktree cleanup, opening a PR.

| Skill | Desc chars | Full desc tokens | Hermes index tokens | SKILL.md tokens | On Hermes |
|---|---:|---:|---:|---:|---|
| `architect` | 238 | 60 | 19 | 1368 | clipped |
| `arena` | 239 | 60 | 17 | 1400 | clipped |
| `automate-me` | 304 | 76 | 20 | 1825 | clipped |
| `benchmark-checklist` | 222 | 56 | 22 | 1251 | clipped |
| `blast-radius` | 267 | 67 | 20 | 964 | clipped |
| `bro` | 65 | 17 | 18 | 67 | clipped |
| `correct` | 305 | 77 | 19 | 620 | clipped |
| `create-formal-verification-skill` | 360 | 90 | 25 | 1407 | clipped |
| `create-verification-skill` | 272 | 69 | 23 | 1634 | clipped |
| `figure-it-out` | 264 | 66 | 21 | 1028 | clipped |
| `how` | 305 | 77 | 17 | 663 | clipped |
| `in-your-own-words` | 131 | 33 | 22 | 79 | clipped |
| `interrogate` | 253 | 64 | 18 | 579 | clipped |
| `ketchup` | 211 | 53 | 18 | 1607 | clipped |
| `ketchup-video` | 153 | 39 | 20 | 972 | clipped |
| `maintain-formal-verification-skill` | 462 | 116 | 25 | 1753 | clipped |
| `maintain-verification-skill` | 262 | 66 | 24 | 1231 | clipped |
| `make-bot-ui` | 188 | 47 | 20 | 1163 | clipped |
| `no-comments` | 88 | 22 | 19 | 674 | clipped |
| `poteto-help` | 141 | 36 | 19 | 3937 | clipped |
| `poteto-mode` | 189 | 48 | 19 | 5418 | clipped |
| `principle-attack-the-premise` | 168 | 42 | 24 | 479 | clipped |
| `principle-boundary-discipline` | 211 | 53 | 22 | 471 | clipped |
| `principle-build-the-lever` | 266 | 67 | 23 | 597 | clipped |
| `principle-encode-lessons-in-structure` | 196 | 49 | 24 | 140 | clipped |
| `principle-exhaust-the-design-space` | 176 | 44 | 26 | 99 | clipped |
| `principle-experience-first` | 163 | 41 | 23 | 296 | clipped |
| `principle-explain-the-number` | 249 | 63 | 24 | 481 | clipped |
| `principle-fix-root-causes` | 167 | 42 | 22 | 456 | clipped |
| `principle-foundational-thinking` | 208 | 52 | 25 | 383 | clipped |
| `principle-guard-the-context-window` | 172 | 43 | 25 | 130 | clipped |
| `principle-laziness-protocol` | 176 | 44 | 24 | 138 | clipped |
| `principle-make-operations-idempotent` | 178 | 45 | 25 | 453 | clipped |
| `principle-migrate-callers-then-delete-legacy-apis` | 172 | 43 | 28 | 160 | clipped |
| `principle-minimize-reader-load` | 194 | 49 | 23 | 499 | clipped |
| `principle-model-the-domain` | 106 | 27 | 24 | 465 | clipped |
| `principle-never-block-on-the-human` | 62 | 16 | 26 | 228 | clipped |
| `principle-outcome-oriented-execution` | 190 | 48 | 24 | 270 | clipped |
| `principle-prove-it-works` | 189 | 48 | 22 | 343 | clipped |
| `principle-redesign-from-first-principles` | 65 | 17 | 27 | 190 | clipped |
| `principle-separate-before-serializing-shared-state` | 189 | 48 | 29 | 392 | clipped |
| `principle-sequence-verifiable-units` | 263 | 66 | 25 | 427 | clipped |
| `principle-subtract-before-you-add` | 155 | 39 | 25 | 228 | clipped |
| `principle-test-behavior-not-implementation` | 186 | 47 | 28 | 654 | clipped |
| `principle-type-system-discipline` | 261 | 66 | 23 | 390 | clipped |
| `recall` | 321 | 81 | 18 | 1337 | clipped |
| `reflect` | 172 | 43 | 18 | 1249 | clipped |
| `setup-pstack` | 275 | 69 | 20 | 1597 | clipped |
| `sharpen` | 74 | 19 | 19 | 166 | clipped |
| `show-me-your-work` | 322 | 81 | 20 | 1638 | clipped |
| `statechart` | 277 | 70 | 20 | 2275 | clipped |
| `swarm` | 149 | 38 | 18 | 685 | clipped |
| `tdd` | 225 | 57 | 18 | 786 | clipped |
| `teach` | 251 | 63 | 17 | 1406 | clipped |
| `technical-writing` | 249 | 63 | 21 | 2274 | clipped |
| `typescript-best-practices` | 76 | 19 | 23 | 692 | clipped |
| `unslop` | 30 | 8 | 11 | 1457 | fits |
| `why` | 421 | 106 | 17 | 2226 | clipped |

## TStack

Nine skills. README says they work in Claude Code and Codex, and that some use T3 Code tools (`delegate_task` with `orchestrator_capabilities`, `watch_pull_request`) and fall back to native tools otherwise. `babysit-pr` ships a Python `pr-wait` script (about 6,200 tokens). A few skills have a tiny `agents/openai.yaml`. Index total: **152 tokens**. Sum of `SKILL.md`: **7,664 tokens**. Five descriptions exceed 60 characters. This is already a small stack. Its Hermes problem is the host-specific tools and the trigger-only descriptions ("Trigger this if the user says 'full send'"), not the size.

| Skill | What it does | SKILL.md tokens |
|---|---|---:|
| `full-send` | The user is not watching. Finish the change, prove it, run `sol-loop`, file a PR, babysit, merge when the gate passes. The request itself is the permission to merge and to use the test methods. | 1,349 |
| `full-stop` | The same path, and it never merges. It reads `full-send` and overrides the merge permission. | 553 |
| `council` | Three models from three providers, in parallel, read-only for a review. Scores out of 10. Loop until they agree. Fight scope creep. Write the table into the PR description. | 541 |
| `sol-loop` | One GPT Sol reviewer, default 3 rounds, 5 only for security, auth, data loss, or concurrency. Stop on nits. Keep a ledger. The reviewer does not start its own reviewers. | 1,282 |
| `file-pr` | Open a PR whose title and first paragraph state the problem. Do not lead with a file inventory. End with the model and harness that made the change. | 568 |
| `babysit-pr` | Watch CI and review bots. Fix real findings. Use one watcher (`watch_pull_request` or `pr-wait`), never a handwritten sleep loop. A child reviewer must not watch the PR. | 1,325 |
| `takeover` | Finish someone else's PR, branch, or thread. Keep their git authorship. Do not defend a diff because another agent wrote it. | 516 |
| `modernize` | Rebase an old PR onto current main and decide whether the idea still belongs. Force-push only with `--force-with-lease` against the SHA you observed. Do not merge or close. | 1,130 |
| `leaving-pr-comments` | Any comment the agent posts for the user starts with a note naming the model and the user. | 400 |

`full-send` depends on `sol-loop`, `file-pr`, and `babysit-pr`. `full-stop` depends on `full-send`. `takeover` depends on `modernize`, `file-pr`, `babysit-pr`, and `leaving-pr-comments`.

| Skill | Desc chars | Full desc tokens | Hermes index tokens | SKILL.md tokens | On Hermes |
|---|---:|---:|---:|---:|---|
| `babysit-pr` | 104 | 26 | 19 | 1325 | clipped |
| `council` | 40 | 10 | 14 | 541 | fits |
| `file-pr` | 82 | 21 | 18 | 568 | clipped |
| `full-send` | 42 | 11 | 15 | 1349 | fits |
| `full-stop` | 99 | 25 | 18 | 553 | clipped |
| `leaving-pr-comments` | 40 | 10 | 17 | 400 | fits |
| `modernize` | 77 | 20 | 19 | 1130 | clipped |
| `sol-loop` | 34 | 9 | 13 | 1282 | fits |
| `takeover` | 115 | 29 | 19 | 516 | clipped |

## Where they duplicate each other

| Job | GStack | PStack | TStack |
|---|---|---|---|
| Name the real problem before code | `office-hours`, `plan-ceo-review` | `sharpen`, `in-your-own-words`, attack-the-premise | |
| Lock structure | `plan-eng-review`, `spec` | `architect`, model-the-domain | |
| Design critique and mockups | five `plan-design` / `design-*` skills, `devex-review` | | |
| Debug before fixing | `investigate` | fix-root-causes, bug-fix playbook | |
| Test first | `qa` (includes writing a failing regression) | `tdd` | proof step inside `full-send` |
| Second model on a diff | `codex`, `claude-code` template, suppressed review army | `interrogate` | `council`, `sol-loop` |
| Pre-landing review | `review` | `interrogate`, no-comments | council scores |
| Open and watch a PR | `ship`, `land-and-deploy` | opening-a-PR, babysit, shipping playbooks | `file-pr`, `babysit-pr`, `full-send`, `full-stop` |
| Old PR | `modernize` | | `modernize` |
| Take over someone else's work | | session-pickup playbook | `takeover` |
| Parallel attempts | `captain` (a product) | `swarm`, `arena` | council's parallel delegates |
| Memory across sessions | `context-save`, `context-restore`, `learn`, GBrain | `recall` | |
| Safety rails | `careful`, `freeze`, `guard` | | |
| Skill authoring | `write-skill` | `reflect`, `automate-me`, authoring playbook | |
| Strip AI prose | | `unslop`, `bro` | |
| Docs | `document-release`, `document-generate` | `technical-writing` | PR prose rules inside `file-pr` |
| Model roles | | `setup-pstack` | council's provider rule, Sol specifically |

GStack's NOTICE shows it has already pulled TStack and PStack ideas into `ship`, `review`, `modernize`, `investigate`, and `plan-eng-review`, and then kept its own 10k-token skills on top. Installing all three would index the same job two or three times.

## What Hermes already does, so we will not rebuild it

| Upstream piece | Hermes already has | Cut? |
|---|---|---|
| GStack `investigate`, PStack fix-root-causes and the bug-fix investigation rule | Bundled `systematic-debugging`. Same iron law: no fix before a root cause. `skills/software-development/systematic-debugging/SKILL.md` | Cut |
| PStack `tdd` | Bundled `test-driven-development` | Cut |
| GStack `review` as a general review pass | Bundled `requesting-code-review` (scan, gates, independent subagent, auto-fix) and `/review` | Cut the general review. Keep only the multi-model loop, which Hermes does not have |
| GStack `deslop-shared-libs` | Bundled `simplify-code` (parallel cleanup of recent changes) | Cut |
| PStack prototype playbook, "try it before you commit" | Bundled `spike` | Cut |
| GStack `qa` on a website | Bundled `dogfood` (`browser_exec`, evidence, a bug report) | Cut the browser tour. Keep a thin proof skill for CLI, API, job, and webhook surfaces, and for the red-then-green bar |
| GStack `browse`, `scrape`, `pair-agent`, cookie import, headed Chromium | `browser_exec` plus `web_extract` | Cut. Those skills are the Aside / GStack browser product |
| GStack `learn`, `context-save`, `context-restore`, `setup-gbrain`, `sync-gbrain`; PStack `recall` | `memory`, `session_search`, `/learn`, `/refine` | Cut |
| GStack `careful`, `freeze`, `guard`, `unfreeze` | `approvals.mode`, the hard blocklist, `approvals.deny`, and the write sandbox in `website/docs/user-guide/security.md` | Cut. Hermes blocks dangerous commands and out-of-sandbox writes in the runtime. A skill that only warns is weaker |
| GStack `write-skill`; PStack `reflect`, `automate-me`, skill-authoring playbook | Bundled `hermes-agent-skill-authoring`, `/learn`, `skill_manage` | Cut |
| PStack `unslop`, `bro` | Bundled `humanizer` | Cut |
| GStack `diagram` | Bundled `architecture-diagram` for infra diagrams. Not a general diagram studio | Cut for v0.1 |
| GStack `make-pdf` | Bundled `pdf` (create, merge, fill, OCR). Not GStack's publication layout | Cut |
| GStack `design-consultation`'s DESIGN.md output | Bundled `design-md` | Cut the design studio. The format skill already exists |
| GStack `codex` and the Claude Code template | Bundled `codex`, `claude-code`, and `opencode` skills under `skills/autonomous-ai-agents/` | Cut. A HStack review must use `delegate_task`, not a second CLI |
| PStack `setup-pstack` | `/model`, `delegation.model`, `auxiliary.review` | Cut. It writes a Cursor rule file |
| PStack `ketchup`, `ketchup-video` | `/status` recap, and the transcript the user is already in | Cut |
| PStack worktree-cleanup playbook | `/worktree` | Cut |
| PStack autonomous-run, autopilot, orchestrate; TStack "don't stop" as a runtime | `/goal` and `/loop`. Kanban for many tasks | Cut the runtime. The merge policy stays, as a skill |
| GStack `plan-tune` (how often to ask) | `clarify`, and the principle of not asking a question a command can answer | Cut |
| GStack `landing-report`, `retro`, `health`, `gstack-upgrade` | Nothing equivalent, and none of it is a Hermes workflow | Cut. They are GStack product features |
| GStack iOS bridge, `cso` Docker catalog, `ubicloud`, `benchmark-models`, `eval-plan`, `captain` | Not Hermes features, and not useful to most Hermes sessions | Cut |
| PStack `make-bot-ui`, verification-skill generators, formal verification, `statechart`, `typescript-best-practices`, `show-me-your-work` | Not Hermes features. TypeScript rules and TLA+ corpora do not belong in the always-on index | Cut |
| TStack `watch_pull_request` | No such tool. `gh` is available. `/loop` can re-enter a session | Do not port the T3 watcher. Do not invent a sleep loop |
| `/plan` | Writes the plan file | Keep using it. It does not replace a product or architecture review |

`codebase-inspection` counts lines with pygount. It does not explain a subsystem. `sdlc-review` only runs inside Kanban. Neither replaces a skill below.

## Keep, merge, drop

Twelve skills. Each one earns an index row. Overlaps become one skill. Host-specific machinery is dropped. The bodies are budgets for phase 2, not files that exist yet. Idle tokens are the Hermes index row for the description in [PLAN.md](PLAN.md), plus the `hstack` category header (3 tokens).

| Decision | What | Why |
|---|---|---|
| Keep, merged | `hstack` router | Replaces PStack `poteto-mode` and GStack `autoplan` as the single entry. Five short playbooks live in `references/`, not as skills |
| Keep, merged | `reframe` | `office-hours` + `plan-ceo-review` + `sharpen` + `in-your-own-words` + attack-the-premise. One product conversation, not two 10k reviews |
| Keep, merged | `shape` | `plan-eng-review` + `architect` + model-the-domain. Then the agent uses built-in `/plan` if it needs a plan file |
| Keep, merged | `prove` | The red-then-green bar from `qa` / `qa-only` / prove-it-works / `benchmark-checklist`, for surfaces `dogfood` does not cover. Points at bundled TDD and `dogfood` instead of restating them |
| Keep, merged | `council` | `council` + `sol-loop` + `interrogate` + the second-opinion idea behind `codex`. Uses `delegate_task`. Does not shell out to Codex or Claude Code |
| Keep, merged | `ship` | `file-pr` + `babysit-pr` + `leaving-pr-comments` + `full-stop` + `full-send` + GStack `ship` without VERSION/CHANGELOG factory behavior. Merge only when the user said to send |
| Keep | `takeover` | TStack `takeover` plus the session-pickup idea. Small, and Hermes does not do authorship preservation |
| Keep, merged | `modernize` | Both `modernize` skills. Same verdict: keep, rework, or recommend close. Never close or merge by itself |
| Keep | `blast` | PStack `blast-radius`. One skill. Prove the safety fact by running code |
| Keep | `swarm` | PStack `swarm`, on `delegate_task`. Different slices, one report |
| Keep | `arena` | PStack `arena`. Same brief, several attempts, keep the best parts. Not the same as swarm |
| Keep, merged | `principles` | All 24 principle skills, rewritten as one skill. 591 index tokens become one row |
| Drop | The other ~100 skills and 18 playbooks | Listed in the Hermes table above and in PLAN.md. They are product features, duplicates, or Claude/Cursor-only |

Idle cost of these twelve rows plus the category header is **204 tokens**. GStack's Hermes index is **1,182 tokens**. Indexing all three stacks would be 1,182 + 1,256 + 152 = **2,590 tokens**, and PStack's 1,256 of that is mostly clipped descriptions that no longer say when to load the skill.

## What phase 2 has to beat

| | Idle index | One planning load | Notes |
|---|---:|---:|---|
| GStack on Hermes | 1,182 | ≥ 62,514 | Five `SKILL.md` files for autoplan's read-from-disk path, plus one ~5,600 preamble, plus section files |
| PStack on Hermes | 1,256 | ≥ 5,418 | `poteto-mode` alone. All 23 playbooks are another 19,154. 57 descriptions clip |
| TStack on Hermes | 152 | ~7,664 if every skill loads | Small, and tied to T3 Code watchers and a named Sol model |
| All three indexed | 2,590 | | Same jobs repeated |
| HStack v0.1 budget | 204 | ≤ 2,500 | Router + `reframe` + `shape`. About 6× less idle than GStack, about 25× less than that planning load |

The body ceiling for all twelve HStack skills together is 8,550 tokens, against 420,401 tokens of GStack `SKILL.md` files. That catalog number is not what one task loads. The planning load is the comparison that matches how the stacks tell the agent to work.
