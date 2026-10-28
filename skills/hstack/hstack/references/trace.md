# Trace

Use this for a live symptom or a profile the user already captured.

1. Name the symptom: a leak, a spin, a hitch, or a hot frame.
2. If they have a profile, read it. Name the frame or the allocation that dominates. Do not guess from the symptom.
3. If they do not, add the smallest log or counter that can fail, reproduce, then read it.
4. When the cause is named, follow `references/fix.md` next. This file does not edit first.
