# Deploy

Use this only when the user named a host, a workflow, or a URL.

1. Do not guess a production host. Do not detect a vendor and deploy to it.
2. Merge only if they said to send. Otherwise stop at a green pull request. Load `ship` with `skill_view("ship")` for that.
3. A canary opens the URL they named, saves a screenshot, and reads the page for errors. Compare to a known-good URL only when they gave one.
4. A preview URL already commented on the pull request can be read with `gh`, or with `hstack-pr` when that helper is installed under the Hermes home at `hstack/bin`.
