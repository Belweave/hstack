# External stacks

Load this after one HStack playbook, not before. This file is not a playbook. Do not load a second playbook from here.

Run `python3` on `skills/hstack/hstack/scripts/hstack_stack.py` inside the Hermes home, with `detect` and `--session` set to this chat. The script reads files and config. It does not run the other stack, and it does not download.

Suggest at most one stack. Prefer one the script marks installed when it fits this task better than the playbook you already loaded. Say the name and why in one line, then ask.

Load nothing from that stack, and download nothing, until the user says yes.

On no, run the script's `decline` with the same session and that id. Do not suggest it again this session.

On yes to an install, run `hstack_stack.py install` with `--yes` and the same session. That flag is the user's yes. Do not add it yourself. The script checks the pinned sha256 before it extracts, into the HStack external directory, and it does not copy those files into HStack skills. Then hand off: name the path and stop. Do not read their skill text until the user says yes to that too.

A stack that is not installed can be the one suggestion only when no installed stack fits. Show the install command the script printed. Do not run it until the user says yes.

The fenced block is the pin list. Detect without running the stack:

- gstack: a SKILL.md under the Hermes `skills/gstack` directory, or `gstack-state-root.sh` inside `~/.claude/skills/gstack/bin` or the Codex twin. Do not execute that file. `~/.gstack` is state, not an install.
- pstack: a file ending in `skills/poteto-mode/SKILL.md` under `~/.cursor/plugins` or `~/.claude/plugins`.
- tstack: one directory holds both `leaving-pr-comments/SKILL.md` and `sol-loop/SKILL.md` under Claude, Codex, agents, or Hermes skills.
- gbrain: `config.json` in `~/.gbrain`, or in `$GBRAIN_HOME/.gbrain` when that variable is set, or an `mcp_servers.gbrain` entry. A binary on PATH is not enough.

```json
{
  "stacks": [
    {
      "id": "gstack",
      "good_at": "Product framing, design review, QA, and release skills written for Claude Code.",
      "license": "MIT",
      "commit": "9e3308f65adf547b7e4776e5ed22467a2649d2ee",
      "sha256": "3beaffdfc83012c6784c7f0610b580290c7e0b41a416e230d4ed63df7311ebc7",
      "archive": "https://codeload.github.com/garrytan/gstack/tar.gz/9e3308f65adf547b7e4776e5ed22467a2649d2ee"
    },
    {
      "id": "pstack",
      "good_at": "Rigorous playbooks, parallel subagents, and principle skills. The tree's skills are under pstack/.",
      "license": "MIT",
      "commit": "c742dd61706fbacc1b95f1a20b7b988cf096ce6c",
      "sha256": "4f899c71d737afe7662ff515df0518b193562e4f9ec370ffb2d7d837aaf436ef",
      "archive": "https://codeload.github.com/cursor/plugins/tar.gz/c742dd61706fbacc1b95f1a20b7b988cf096ce6c"
    },
    {
      "id": "tstack",
      "good_at": "Short pull-request skills: file a PR, a review council, takeover, and modernize.",
      "license": "MIT",
      "commit": "1085050f3baed1ac724caa4a8166145fb2ac88af",
      "sha256": "9ef4b8abe9a8595f2309fdb096e4c41569b26920bcf6e91fba07854a9092cf1c",
      "archive": "https://codeload.github.com/t3dotgg/tstack/tar.gz/1085050f3baed1ac724caa4a8166145fb2ac88af"
    },
    {
      "id": "gbrain",
      "good_at": "A personal knowledge store. It is not Hermes memory unless this install is present.",
      "license": "MIT",
      "commit": "82b7ef601fdfc449b0d242f7e61a4604aa2c8a8e",
      "sha256": "b7127348f6ed1163c32106957844af637426d491c669a3ee68e989f2c68ed451",
      "archive": "https://codeload.github.com/garrytan/gbrain/tar.gz/82b7ef601fdfc449b0d242f7e61a4604aa2c8a8e"
    }
  ]
}
```
