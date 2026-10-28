# Decisions

Use this when the user wants a reviewable trail of choices.

1. One row per decision: the date, the choice, the alternative rejected, and the reason.
2. Run `hstack-decisions` when that file exists under the Hermes home at `hstack/bin`. Otherwise append the row to a TSV with `write_file`, and only when the user wants it committed.
3. Do not log secrets.
