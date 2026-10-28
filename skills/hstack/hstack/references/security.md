# Security

Use this for auth, permissions, injection, secrets, or dependencies.

1. Read the diff. Name the trust boundary.
2. Do not write an exploit, a payload, or a proof of compromise.
3. Run `hstack-scan` when that file exists under the Hermes home at `hstack/bin`. It runs a secret scanner and a dependency scanner only when those programs are already installed.
4. Report file and line. A finding you did not verify is a question, not a bug.
5. Load `council` with `skill_view("council")` when the change touches auth, permissions, data loss, or concurrency.
