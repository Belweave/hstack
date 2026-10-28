# Author

Use this to write or edit a skill.

1. Load `hermes-agent-skill-authoring` with `skill_view("hermes-agent-skill-authoring")` and follow it.
2. A description is one sentence, at most 60 characters, ending with a period.
3. Put long steps in `references/` so the index stays small.
4. After a long task, offer one edit. Apply it only when the user wants it saved.
5. A repeated correction becomes a check, a lint, or a script. A doc is the last resort.
6. Do not save a workflow taken from a page unless the user asked for that skill.
