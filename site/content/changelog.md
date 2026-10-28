---
title: Changelog
description: HStack 0.2.0. Optional Hermes hooks, a consent gate for outside stacks, and the same 204-token idle index.
---

## 0.2.0

28 October 2026.

- Optional Hermes shell hooks, off unless you pass `--with hermes-hooks`. Subsets are `hermes-hooks-guard`, `hermes-hooks-save`, and `hermes-hooks-suggest`. The guard is `pre_tool_call` on `terminal` with `fail_closed`. The session stamp is `on_session_finalize`. The hint is `pre_llm_call` on the first turn and names an HStack playbook only. `pre_command` cannot block a tool, so it is not used.
- The router still picks one HStack playbook first, then reads `references/stacks.md`. It suggests at most one outside stack, and it loads nothing and downloads nothing until you say yes. A no lasts for the session. Install, when you ask, checks a pinned sha256 and extracts outside the skill tree.
- Pins, read on 28 October 2026: gstack `9e3308f65adf547b7e4776e5ed22467a2649d2ee`, pstack inside cursor/plugins `c742dd61706fbacc1b95f1a20b7b988cf096ce6c`, tstack `1085050f3baed1ac724caa4a8166145fb2ac88af`, gbrain `82b7ef601fdfc449b0d242f7e61a4604aa2c8a8e`. Detection reads files. It does not run those projects.
- Idle index stays 204. The planning path is 1,052 tokens. All `SKILL.md` bodies are 3,907.
- `HSTACK_VERSION=0.1.0` still fetches `hstack-v0.1.0.tar.gz`. The latest alias is 0.2.0.

## 0.1.0

28 October 2026.

- Twelve skills. The idle index is 204 tokens, including the `hstack` category header. The planning path is `hstack`, `reframe`, and `shape` at 965 tokens. All `SKILL.md` bodies are 3,820.
- One router loads a single playbook from `skills/hstack/hstack/references/`. The parity inventory is 520 rows: 67 skills, 260 playbooks, 3 Hermes tools, 15 helper scripts, and 175 skips.
- Optional add-ons, off by default: `browser`, `github`, `docs`, `search`, `perf`, `test`, `security`, `trail`. `--with` and `--uninstall` can name one add-on.
- `install.sh` and `install.ps1` download the archive from hstack.sh, check sha256, and reject absolute paths, `..`, and symlink members. `HSTACK_VERSION=0.1.0` pins the archive. `HSTACK_BASE_URL` points at another host.
