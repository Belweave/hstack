# Overnight

Use this when the user is leaving and the work should keep going.

1. If they said to send or to merge, that sentence is permission to merge. If they said to stop, never merge. Otherwise load `ship` with `skill_view("ship")` and stop when the pull request is green.
2. Load `prove` with `skill_view("prove")` before you open the pull request. Load `council` with `skill_view("council")` only under that skill's rules.
3. Watch checks with `gh pr checks`. When `hstack-pr` exists under the Hermes home at `hstack/bin`, one run is one snapshot. Re-enter with `/loop`. Do not write a sleep loop.
4. Many independent tasks use Kanban or `/goal`. Return one status.
5. A child agent does not watch the pull request.
