# Project 1 Reference Notes

The reference implementation is one acceptable design, not the canonical
answer. It deliberately:

- Imports provider SDKs only inside live-call functions.
- Preserves provider, API, model, response ID, usage, latency, and output types.
- Rejects payloads that contain no supported text.
- Treats automatic fact checks as coarse lexical signals.
- Leaves human judgment outside the automatic score.

The lexical evaluator can miss paraphrases and can flag phrases without
understanding negation. That limitation is part of the lesson; it should not be
hidden behind a more elaborate judge before the learner understands it.
