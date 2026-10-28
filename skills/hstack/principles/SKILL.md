---
name: principles
description: Apply the design rule that should change this decision.
version: 0.2.0
author: Preetham Kyanam
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design]
    related_skills: [prove, shape, systematic-debugging, test-driven-development]
---

# Principles

## When to Use

A design choice is contested. Apply the rules that would change the decision, and name that decision. Do not recite this list.

## Rules

1. Prefer deleting code. Stop at the smallest change that solves the job.
2. Choose the core data structures before writing behavior around them.
3. When a new requirement shows up, fit it as if it had been a requirement from the start.
4. After two failed fixes, write down the premise they shared and test that premise.
5. Remove the dead path before building beside it.
6. Cut layers and hidden state a reader would have to remember.
7. Point a rewrite at the end state. Do not preserve a compatibility shim that only the migration needed.
8. When the user's result and the implementation's convenience disagree, pick the result.
9. If there is no precedent, build two or three small alternatives before committing to one.
10. If a step can be a script, make it a script a reviewer can rerun. Leave judgment to the agent.
11. Encode a repeated rule in one structure, not in scattered conditionals.
12. Validate at the boundary. Trust the types inside it.
13. Make states that should be impossible unrepresentable.
14. A retry must converge on the same end state.
15. Move every caller, then delete the old API in the same change.
16. Give parallel work separate state. Do not add a lock as the first fix.
17. Prove the real artifact. A proxy that stayed green is not the proof.
18. Reproduce the failure and trace it to a cause before editing.
19. Each small unit ends in a check that can fail.
20. Test what a caller can observe. A test that breaks when internals move is a bad test.
21. Before reporting a number, say what limited it and what else it might have measured.
22. Send bulk reading to a subagent. Keep the finding, not the dump, in the parent.
23. Do reversible work without asking. Ask only when the choice is a preference or a destructive act Hermes will not already block.
24. A lesson stated twice becomes a check, a lint, or a script. Advice in a doc is the last resort.

Rules 17 and 21 are `prove`. Rule 18 is bundled `systematic-debugging`. Rule 20 is bundled `test-driven-development`. Those are reminders. Do not copy those skills into this file.
