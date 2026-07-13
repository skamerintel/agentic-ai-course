# Technical Defense Question Bank

The mentor chooses questions based on the learner's implementation.

## Architecture

- Remove LangGraph. What behavior becomes harder, and what remains simple?
- Redis is unavailable for an hour. Which guarantees still hold?
- The second API adds eventual consistency. Where is staleness represented?
- A second tenant is added. Which assumptions become security boundaries?

## Model boundary

- Show how valid but unsupported output is rejected.
- Change the structured schema and trace migration and evaluation impact.
- Explain model selection without relying on a permanent “best model” claim.
- Identify what must be logged and what must never be logged.

## Reliability and authority

- Crash after the external write but before the local receipt. Demonstrate recovery.
- Replay the same event with changed content. Explain the expected result.
- Show that an injected instruction cannot approve or expand capabilities.
- Revoke an approval after source evidence changes.

## Evaluation

- Defend one metric and show how it can be gamed.
- Explain the worst slice and why the final design accepts or fixes it.
- Show one failed iteration and what was learned.
- Explain why the holdout is still credible.

## AI collaboration

- Identify a generated change you rejected and the evidence behind the decision.
- Explain selected code line by line, then modify one requirement.
- Show a test that caught an AI-generated mistake.
