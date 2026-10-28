# Refactor

Use this when the behavior stays and the structure changes.

1. Name the behavior a caller can still observe.
2. If a module boundary moves, load `shape` with `skill_view("shape")`.
3. Load `prove` with `skill_view("prove")`. The same checks pass before and after.
4. If the job is duplicated code, load `simplify-code` with `skill_view("simplify-code")` and recommend one structure. Do not edit until the user agrees.
5. Load `principles` with `skill_view("principles")` only when a rule is what the argument is about. Apply it. Do not recite the list.
