# Safety

Use this when a command is destructive or writes should stay in one directory.

1. Do not add a warning-only skill. Hermes `approvals.mode`, the command blocklist, and `approvals.deny` already block dangerous commands.
2. Stay inside the directory the user named. Do not patch outside it. The write sandbox is the enforcement.
3. Clear that limit only when the user says so.
4. Hooks exist for people who want them. Do not install one from this playbook.
5. `pre_command` cannot block a tool. The optional guard is a `pre_tool_call` hook on `terminal`, and only the installer flag adds it.
