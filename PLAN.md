# HStack v0.1 plan

Twelve skills, written for Hermes, in our own words. Nothing in this file is implemented yet. The inventory and the license call are in [RESEARCH.md](RESEARCH.md).

v0.1 is the sprint loop the three stacks share, minus the parts Hermes already runs and minus the product features that only make sense inside Claude Code, Cursor, Aside, or GStack's own browser.

## Idle cost

Descriptions are at most 60 characters, so Hermes will not clip them. Index tokens use Hermes's own estimate, `ceil(utf-8 bytes / 4)`, for the row `    - <name>: <description>`. The category header `  hstack:` is 3 tokens. The shared skills preamble (~293 tokens) belongs to every Hermes profile and is not part of this stack's cost.

| Skill | Idle description | Desc chars | Index tokens | Body ceiling |
|---|---|---:|---:|---:|
| `hstack` | Pick the playbook for this task and load it. | 44 | 15 | 700 |
| `reframe` | Name the real job before any plan or code. | 42 | 15 | 950 |
| `shape` | Settle data shape and module boundaries first. | 46 | 15 | 850 |
| `prove` | Show a failing check, then a passing one, on real behavior. | 59 | 18 | 750 |
| `council` | Have other models challenge the diff, then fix blockers. | 56 | 18 | 900 |
| `ship` | Open a short PR, watch CI, and merge only if told. | 50 | 16 | 1,100 |
| `takeover` | Finish someone else's branch and keep their git credit. | 55 | 18 | 500 |
| `modernize` | Rebase an old PR and decide if it still belongs. | 48 | 17 | 550 |
| `blast` | Find what a small diff can break, and prove the safe fact. | 58 | 18 | 450 |
| `swarm` | Fan out parallel subagents and return one report. | 49 | 16 | 500 |
| `arena` | Try competing approaches, then keep the best parts. | 51 | 16 | 500 |
| `principles` | Apply the design rule that should change this decision. | 55 | 19 | 800 |
| **Total** | category header included | | **204** | **8,550** |

Body ceilings include frontmatter. They are the phase-2 budget, not a measurement of files. A check script should fail a skill whose description is over 60 characters or whose `SKILL.md` exceeds its ceiling. Sibling files under `references/` do not count against the body ceiling. They count when `skill_view` loads that one file, and each playbook file should stay under 500 tokens.

Against GStack installed the way `docs/hosts.md` describes (`gstack-<skill>` in one category): **1,182 idle tokens** and **420,401 tokens** of `SKILL.md`. A planning session that follows `autoplan` and reads the CEO, design, DX, and eng skills loads **62,514 tokens** of `SKILL.md` plus one shared preamble of about 5,600. HStack's planning path is the router, `reframe`, and `shape`: **2,500 tokens**, about 25× smaller, and the idle index is about 6× smaller (204 vs 1,182).

Indexing GStack, PStack, and TStack together would add **2,590 tokens** of index rows, and 57 of PStack's 58 descriptions would be clipped to the point that the row no longer says when to use the skill.

## What each skill merges

### `hstack`

The only skill a user has to remember. It matches the task to one playbook under `references/` and loads that file. It does not contain the playbooks inline.

Replaces the entry-point role of PStack `poteto-mode` and of GStack `autoplan`. It does not replace their bodies. `poteto-mode` is 5,418 tokens plus 19,154 tokens of playbooks and routes into Cursor rules, Bugbot, and cloud agents. `autoplan` is 10,801 tokens and tells the agent to read four more huge skills.

Playbooks, each a reference file, loaded one at a time:

| File | When | Then load | Ceiling |
|---|---|---|---:|
| `frame.md` | The user is deciding what to build | `reframe`, then stop or hand off | 400 |
| `feature.md` | New or changed behavior | `shape`, implement, `prove` | 450 |
| `fix.md` | Something is broken | Bundled `systematic-debugging`, then `prove` | 350 |
| `check.md` | The diff needs a hard look | Bundled `requesting-code-review` or `/review`. `council` only if the user asked for other models. `blast` if the diff looks small and risky | 400 |
| `land.md` | The work should become a PR | `ship` | 300 |

Dropped playbooks, and where the need goes if it is real: perf and hillclimb (a sentence in `prove` about not trusting an unvetted number), prototype (bundled `spike`), visual parity, trace forensics, runtime forensics, eval, orchestrate, autopilot-full, autopilot-stack, worktree cleanup (`/worktree`), pause safely, multi-phase (Kanban or `/goal`), skill authoring (bundled authoring skill and `/learn`), investigation (the fix playbook).

### `reframe`

Push on the request until the job, the user, and the smallest version are named. Disagree in the open. Stop when the evidence says the requested change is the wrong change. Do not write code in this skill.

Merges GStack `office-hours` (10,972) and `plan-ceo-review` (15,095), and the PStack ideas behind `sharpen`, `in-your-own-words`, and attack-the-premise. Those GStack skills also pull a 5,600-token preamble and tens of thousands of tokens of section files. The useful part is the forcing questions, not the wizard.

`spec` is not a separate skill. If the user wants a written plan after the frame is settled, `shape` tells the agent to use the built-in `/plan`.

### `shape`

Before code crosses a function boundary, name the data, the types, and which module owns the rule. One structure for a rule that would otherwise be copied. Stay in the conversation while the code is filled in. If a plan file is wanted, call `/plan`. Do not reimplement `/plan`.

Merges the architecture pass of GStack `plan-eng-review` (10,878, plus ~31,000 tokens of sibling markdown) and PStack `architect` (1,368), plus the "model the domain" and "data structures first" principles. The eight design red flags and the second-shape comparison that GStack adapted stay as two short checks, rewritten, not as a pasted list.

### `prove`

Done means a check the agent ran. Show it failing for the right reason, then passing. Name what was actually exercised (the CLI, the API, the job, the webhook, the page). A report-only mode lists the check and does not edit product code. A performance claim names the limiter, the repeat, and the error; otherwise it is not a result.

Merges the proof bar in GStack `qa` and `qa-only` (7,314 and 5,479) with PStack prove-it-works and the useful part of `benchmark-checklist` (1,251). Browser exploration stays in bundled `dogfood`. A bug with a cheap unit test stays in bundled `test-driven-development`. This skill points at both and refuses to restate them. If the body cannot say that in 750 tokens, the skill is too long, not the budget too small.

### `council`

Read-only reviewers, via `delegate_task`, on models other than the one that wrote the diff. Default one reviewer. Three only when the user asked for a panel or the change touches auth, permissions, data loss, or concurrency. Cap at 3 rounds, 5 for those high-risk cases while a blocker remains. Nits do not earn another round. Do not grow the diff to please a reviewer. Record reviewer, round, and outcome. Do not invent a score the model did not give.

Merges TStack `council` (541) and `sol-loop` (1,282) with PStack `interrogate` (579) and the second-opinion intent of GStack `codex` (9,463). Hermes suppresses GStack's review army on purpose. `/review` and `/moa` are different: `/review` is one reviewer, `/moa` lets an aggregator act. This skill is the panel. It must not shell out to the Codex CLI or Claude Code. If only one other provider is configured, say so and run one reviewer. That is the Sol loop, without hard-coding a model name.

### `ship`

Open a pull request that leads with the problem the user hit, not a list of files. Match the repo's existing title style. Attribute an agent-written comment to the model and the user, in our own wording, not a copied callout. Watch CI with `gh pr checks`. Use `/loop` if the user has left and asked the session to stay on it. Do not write a sleep loop, and do not port `pr-wait`. Load the bundled `github` skill for the `gh` commands instead of duplicating them.

Merge, enable auto-merge, or push the default branch only when the user explicitly said to send it. Otherwise stop when the PR is green and the review comments that are real are fixed. Rebase with `--force-with-lease` against the SHA just observed. Gate check before push: list any test, timeout, snapshot, or lint suppression the diff weakened. That list is the part of GStack `review` worth keeping. The rest of that 14,728-token skill is the bundled reviewer.

Merges TStack `file-pr`, `babysit-pr`, `leaving-pr-comments`, `full-stop`, and `full-send`, and the ship path of GStack `ship` (15,240) without VERSION bumps, CHANGELOG duties, or the workspace ship queue. `land-and-deploy`, `setup-deploy`, and `canary` are dropped. Hermes does not know the user's production host, and guessing it is how a skill gets huge.

### `takeover`

Finish a PR, branch, or agent thread the user pointed at. Read the review and the later corrections. Keep the original authors on the commits and in the PR body. Use verified names and emails. Do not guess. Do not defend the existing diff. New fixes are new commits. Do not overwrite unrelated work.

Merges TStack `takeover` (516) and the PStack session-pickup playbook. Hermes has `/resume` for its own sessions. It does not have a rule for keeping someone else's git credit.

### `modernize`

Update an old PR onto current main. Then say which of these is true: the patch still matches the idea, the idea stands and the patch does not, or the idea should be closed. Recommend close. Do not close, and do not merge. Show a range-diff. Force-push only with `--force-with-lease` pinned to the head you read before the rebase.

Merges GStack `modernize` (3,609) and TStack `modernize` (1,130). Both already agree on the verdict. HStack does not need two copies, and it does not need GStack's preamble.

### `blast`

For a small diff the user does not trust. Name what it can break outside the diff. Pick the one fact that would make it safe, and prove that fact by running the code. A written argument is not the proof.

PStack `blast-radius` (964). GStack folded a version of this into `investigate`. The bundled debugger does not ask for this specifically. One short skill is enough.

### `swarm`

Split a task into slices that do not write the same files. One `delegate_task` batch, default cap respected (10 unless the user raised it). Each child gets the goal, the slice, and the check. The parent returns one report. Races are allowed when the slices are competing proofs of the same question. Children do not watch PRs and do not spawn their own panels.

PStack `swarm` (685), on Hermes's `delegate_task` instead of Cursor cloud agents. GStack `captain` is a crew product with merge trains. Dropped.

### `arena`

Same brief, several attempts, separate worktrees. The parent keeps the best pieces and deletes the rest. This is for a design or an approach that has no obvious winner. It is not swarm. Swarm partitions. Arena duplicates.

PStack `arena` (1,400). The "try two shapes" check inside `shape` can point here when the user wants the attempts actually built. Bundled `spike` remains the right tool for a throwaway experiment the user will delete.

### `principles`

One skill. The agent loads it when a design choice is contested, then applies the rules that change a decision and names the decision. It does not recite the list.

The 24 PStack principle skills cost 591 idle tokens. Collapsed, they cost 19. The body is one sentence per rule, rewritten, about 800 tokens. No per-rule skill, no Cursor custom mode.

The sentences phase 2 should write, in our words:

1. Prefer deleting code. Stop at the smallest change that solves the job.
2. Choose the core data structures before writing behavior around them.
3. When a new requirement shows up, fit it as if it had been a requirement from the start.
4. After two failed fixes, write down the premise they shared and test that premise.
5. Remove the dead path before building beside it.
6. Cut layers and hidden state a reader would have to remember.
7. Point a rewrite at the end state. Do not preserve a compatibility shim that only the migration needed.
8. When the user's result and the implementation's convenience disagree, pick the result.
9. If there is no precedent, build two or three small alternatives before committing to one.
10. If a step can be a script, make it a script a reviewer can rerun. Leave judgment to the agent.
11. Encode a repeated rule in one structure, not in scattered conditionals.
12. Validate at the boundary. Trust the types inside it.
13. Make states that should be impossible unrepresentable.
14. A retry must converge on the same end state.
15. Move every caller, then delete the old API in the same change.
16. Give parallel work separate state. Do not add a lock as the first fix.
17. Prove the real artifact. A proxy that stayed green is not the proof.
18. Reproduce the failure and trace it to a cause before editing.
19. Each small unit ends in a check that can fail.
20. Test what a caller can observe. A test that breaks when internals move is a bad test.
21. Before reporting a number, say what limited it and what else it might have measured.
22. Send bulk reading to a subagent. Keep the finding, not the dump, in the parent.
23. Do reversible work without asking. Ask only when the choice is a preference or a destructive act Hermes will not already block.
24. A lesson stated twice becomes a check, a lint, or a script. Advice in a doc is the last resort.

Rules 17, 18, 20, and 21 point at `prove` and the bundled debugger and TDD skill. They are reminders, not second copies.

## Cut because Hermes already does it

These do not get a HStack skill, a playbook, or a paragraph pasted from upstream.

| Piece | Use this instead |
|---|---|
| GStack `investigate`. PStack fix-root-causes. The bug-fix playbook's investigation law | Bundled `systematic-debugging` |
| PStack `tdd` | Bundled `test-driven-development` |
| GStack `review` as a general review. PStack `no-comments` as a persona | Bundled `requesting-code-review` and `/review`. The weakened-test list lives in `ship` |
| GStack `deslop-shared-libs` | Bundled `simplify-code` |
| PStack prototype playbook | Bundled `spike` |
| GStack website `qa` | Bundled `dogfood` |
| GStack `browse`, `scrape`, `skillify`, `setup-browser-cookies`, `open-gstack-browser`, `pair-agent` | `browser_exec`, `web_extract` |
| GStack `learn`, `context-save`, `context-restore`, `setup-gbrain`, `sync-gbrain`. PStack `recall` | `memory`, `session_search`, `/learn`, `/refine` |
| GStack `careful`, `freeze`, `guard`, `unfreeze` | `approvals.mode`, the command blocklist, `approvals.deny`, the write sandbox |
| GStack `write-skill`. PStack `reflect`, `automate-me`, the authoring playbook | Bundled `hermes-agent-skill-authoring`, `/learn`, `skill_manage` |
| PStack `unslop`, `bro` | Bundled `humanizer` |
| GStack `diagram`, `make-pdf` | Bundled `architecture-diagram` and `pdf`, when those jobs come up. Not part of HStack |
| GStack `design-consultation` output format | Bundled `design-md` |
| GStack `codex`, Claude Code second opinion | `delegate_task`. Bundled `codex` / `claude-code` skills only if the user already wants those CLIs |
| PStack `setup-pstack` | `/model`, `delegation.model`, `auxiliary.review` |
| PStack `ketchup`, `ketchup-video` | `/status`, the live transcript |
| PStack worktree cleanup | `/worktree` |
| "Keep going until it is done" as a runtime. PStack autopilot, orchestrate, autonomous-run | `/goal`, `/loop`, Kanban |
| GStack `plan-tune` | `clarify`, and principle 23 |
| TStack `watch_pull_request` and `pr-wait` | `gh pr checks`, `/loop` |
| Built-in `/plan` | Call it from `shape`. Do not ship a skill named `plan` |

## Cut because it does not earn a row

Dropped even though Hermes has no twin. They are large, host-specific, or rare.

- GStack design studio: `plan-design-review`, `design-review`, `design-shotgun`, `design-html`, `design-motion`, `design-consultation`, `devex-review`, `plan-devex-review`. Bodies from 4,500 to 21,000 tokens, tied to Aside or to files GStack's NOTICE traces to impeccable (Apache-2.0) and other design sources. Revisit only if a later version can state a design bar in under 800 tokens without those files.
- GStack product ops: `canary`, `retro`, `health`, `landing-report`, `benchmark`, `benchmark-models`, `eval-plan`, `ubicloud`, `captain`, `gstack-upgrade`, `setup-deploy`, `land-and-deploy`, `cso`, the five `ios-*` skills.
- GStack `test-audit` as its own skill. Principle 20 covers the rule. A repo-wide sweep can wait.
- GStack `document-generate` and `document-release`, and PStack `technical-writing`, as their own skills. `ship` requires the PR to lead with the problem. A full Diátaxis writer is a later skill if the body can stay under 700 tokens.
- PStack `how`, `why`, `teach`. `why` is built around Cursor MCP discovery. The fix and feature playbooks should say: read the code and the git history before explaining a cause. That does not need an index row.
- PStack `poteto-help`, `figure-it-out`, `show-me-your-work`, `correct`, `make-bot-ui`, both verification-skill pairs, both formal-verification skills, `statechart` (and its fixture corpus), `typescript-best-practices`.
- TStack as a package to copy. Its nine skills are the right size, and their behavior is merged above. Copying them would keep T3 Code tool names and a hardcoded Sol reviewer.

## How phase 2 should write them

Install layout, when an installer exists: `~/.hermes/skills/hstack/<name>/SKILL.md`, so the index groups them under `hstack`. In the repo, the same tree under `skills/`.

Frontmatter, matching Hermes's authoring standard (`skills/software-development/hermes-agent-skill-authoring/SKILL.md`):

- `name`, `description` of at most 60 characters, ending with a period
- `version: 0.1.0`
- `license: MIT`
- `platforms: [linux, macos, windows]`
- `metadata.hermes.tags` and `related_skills` pointing at the bundled skills named above

Tools the bodies may name: `terminal`, `read_file`, `write_file`, `patch`, `search_files`, `web_search`, `web_extract`, `browser_exec`, `clarify`, `delegate_task`, `skill_view`, `memory`, `session_search`. Not Bash, Read, Write, Edit, Grep, Glob, Agent, or AskUserQuestion.

`related_skills` entries have to name skills that exist on the machine. Pointing at bundled Hermes skills is correct. Pointing at a HStack skill that ships in the same install is correct. Do not point at GStack or PStack names.

Write every procedure in our own words. Do not copy a `SKILL.md`, a preamble, a word list, or a script from GStack, PStack, or TStack. All three are MIT, so a later copy would be legal if we added the copyright and permission notice. v0.1 should not need that. No `NOTICE` file until a substantial portion is actually included. Do not add courtesy credits.

PStack specifically: the ideas above were taken from Cursor's public plugin (README, principles guide, and skill descriptions for size). The skill text stays in Cursor's repo. We rewrite.

Descriptions that are only a trigger phrase ("if the user says full send") are how TStack and parts of GStack get indexed. Hermes clips those and the model cannot see the behavior. The description states the capability. The body states the trigger.

Inline shell snippets stay off. No required API keys. No `~/.claude` paths. No Cursor rule files. No model slug baked into a skill. `council` asks `delegate_task` to use a configured model that is not the parent, and reports it when that is impossible.

The check script in phase 2 should parse every `SKILL.md`, reject a description over 60 characters, reject a missing `name`, and reject a body over the ceiling in the table above. Shellcheck belongs to the installer, which is also phase 2.

## Out of scope for this repo today

No skill files, no installer, no `hstack.sh` script, no smoke test against a live Hermes. Those are the next phase. This plan is the contract for that work: twelve skills, 204 idle tokens, 8,550 tokens of body budget, and the cuts above left on the floor.
