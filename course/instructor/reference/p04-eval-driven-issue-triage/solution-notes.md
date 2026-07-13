# Project 4 Reference Notes

The reference implementation keeps evaluation layers separate:

- Structured ownership rules are deterministic lookup.
- Historical duplicate discovery is lexical retrieval with metadata filtering.
- Retrieval hit rate and ranking are measured before final triage quality.
- Category, urgency, owner, labels, duplicate ranking, and follow-up use separate
  metrics.
- Slice metrics include sample counts.
- Experiment comparison rejects mismatched dataset fingerprints.

The lexical retriever is intentionally simple. Its inspectability is useful for
learning, but production systems may require embeddings, hybrid search,
reranking, or managed retrieval. Those changes still require the same retrieval
benchmark and failure analysis.
