# Perf

Use this when someone cites a number, or a path is slow.

1. Name the limiter: CPU, memory, network, a lock, or a query.
2. Repeat the same command at least three times. Report min, median, max, and any non-zero exit. One sample is not a result.
3. Run `hstack-bench` when that file exists under the Hermes home at `hstack/bin`. Otherwise time the repeats yourself with the terminal.
4. A page timing is still a number and follows the same bar.
5. Hill climb means one hypothesis, a before, and an after. Keep the change only when the median moved. One accepted change at a time.
6. Load `prove` with `skill_view("prove")` before you call it done.
