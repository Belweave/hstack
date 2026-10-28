# Check

Use this when the diff needs a hard look.

Load `requesting-code-review` with `skill_view("requesting-code-review")`, or run `/review`. `/review` is one reviewer.

Load `council` with `skill_view("council")` only if the user asked for other models.

Load `blast` with `skill_view("blast")` if the diff is small and it can break something outside the lines it changes.

A comment that only narrates the next line is a finding. A test that never calls a behavior a caller can see is a finding. Do not delete tests until the user agrees.

Do not start a panel by default.
