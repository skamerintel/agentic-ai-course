# M13: Context Engineering, Retrieval, and Memory Choices

## Learning objectives

By the end of this module, you can:

- Choose among full context, structured lookup, retrieval, and no added context.
- Measure retrieval independently from generated-answer quality.
- Use metadata filters and bounded result sizes.
- Explain precision, recall, hit rate, and ranking for retrieval.
- Detect semantically similar but irrelevant context.
- Distinguish persistent application data from model conversation memory.

## Prerequisite diagnostic

For each information source, choose full context, structured lookup, retrieval,
or a direct tool:

1. Seven stable team-ownership rules.
2. Twenty thousand historical issues.
3. One issue's repository and component metadata.
4. The current status of a deployment.
5. A user's last three approved preferences.

Explain why “put everything in a vector database” is not a sufficient design.

## Required reading

- [Context engineering references](../../../docs/reference-catalog.md#ref-context-engineering)
- [OpenAI retrieval references](../../../docs/reference-catalog.md#ref-openai-retrieval)

## Concept lesson

### Context is a budget and a design surface

Useful context must be relevant, trustworthy, timely, understandable, and small
enough to avoid crowding out the task. More context can add contradictions,
stale rules, prompt injection, and distracting similarities.

### Prefer deterministic lookup for deterministic relationships

Project 4 maps repositories and components to owning teams through structured
rules. This relationship should be looked up directly, not rediscovered through
semantic retrieval on every request.

### Retrieval is appropriate for candidate discovery

Historical duplicate issues are numerous and expressed in varied language.
Retrieval can find a small candidate set. The triage system then decides whether
the candidates are true duplicates.

Retrieval and duplicate judgment are separate stages with separate metrics.

### Start with inspectable retrieval

Project 4 begins with lexical overlap and metadata filtering. Its limitations
are visible. Later systems may use embeddings or managed retrieval, but the same
questions remain:

- Did the relevant item appear in the top `k`?
- What irrelevant items were returned?
- Were metadata filters correct?
- Did ranking change across slices?
- How much context was added?

### Full context is sometimes correct

If the corpus is tiny, stable, and trusted, passing it in full may be simpler and
more reliable than retrieval. Measure context size and quality rather than using
retrieval by reflex.

### Memory is not one thing

- Thread state: recent conversation or workflow state.
- User memory: approved preferences or facts across sessions.
- Application data: durable records in a database.
- Retrieval index: searchable representations of source documents.

Do not call every stored value “agent memory.” Define ownership, lifetime,
privacy, and update rules.

## Guided lab

For Project 4, compare:

1. No historical-issue context.
2. Full historical issue context.
3. Structured owner lookup plus top-`k` lexical retrieval.

Measure duplicate hit rate, reciprocal rank, irrelevant candidates, context
characters, and final triage metrics separately.

## Independent challenge

Improve lexical retrieval for one failure slice without using labels as query
terms. Consider token normalization, repository filters, component metadata, and
term weighting. Record one case where semantic similarity should not imply a
duplicate.

## Failure-analysis exercise

Diagnose a system whose final duplicate accuracy is poor even though the answer
sounds plausible. Determine whether the relevant issue was absent, ranked too
low, ignored by the model, or incorrectly labeled.

## Comprehension gate

The learner must defend the context strategy for ownership and duplicate
discovery, present retrieval-only metrics, and explain at least one false
positive caused by irrelevant context.

## Interview questions

1. When is structured lookup better than semantic retrieval?
2. How do you evaluate retrieval separately from generation?
3. When is full-context loading appropriate?
4. What is the difference between application state, memory, and retrieval?

## Required GitHub evidence

- Context decision record.
- Retrieval benchmark and queries.
- Full-context versus retrieval comparison.
- False-positive and false-negative analysis.
- Updated failure ledger.
