# Verify

Use this when a test cannot reach a race, a retry, a parser, or a state machine.

1. Write the property in one sentence. Name the state that must be impossible.
2. If the project already has a check for it, run that check.
3. A model checker runs only when the user already has one. Do not install one. Do not copy a model corpus.
4. A short mermaid block of the user-visible states is enough when the picture is what they asked to see.
5. When the code changes, update the property in the same change. Say whether a failure is the model or the product.
