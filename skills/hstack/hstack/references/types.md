# Types

Use this when a type is the decision, including TypeScript.

1. Load `principles` with `skill_view("principles")`. The rules that apply here are the boundary, impossible states, and one structure for a repeated rule.
2. Prefer a union the compiler can check over a pair of flags.
3. Do not widen a type or add a cast to get past an error. Fix the boundary.
4. A test that only checks a type, and never a value a caller can see, is not `prove`.
