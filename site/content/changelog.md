---
title: Changelog
description: HStack 0.1.0. Twelve skills, an idle index of 204 tokens, optional add-ons, and a sha256-checked install from hstack.sh.
---

## 0.1.0

28 October 2026.

- Twelve skills. The idle index is 204 tokens, including the `hstack` category header. The planning path is `hstack`, `reframe`, and `shape` at 965 tokens. All `SKILL.md` bodies are 3,820.
- One router loads a single playbook from `skills/hstack/hstack/references/`. The parity inventory is 520 rows: 67 skills, 260 playbooks, 3 Hermes tools, 15 helper scripts, and 175 skips.
- Optional add-ons, off by default: `browser`, `github`, `docs`, `search`, `perf`, `test`, `security`, `trail`. `--with` and `--uninstall` can name one add-on.
- `install.sh` and `install.ps1` download the archive from hstack.sh, check sha256, and reject absolute paths, `..`, and symlink members. `HSTACK_VERSION=0.1.0` pins the archive. `HSTACK_BASE_URL` points at another host.
