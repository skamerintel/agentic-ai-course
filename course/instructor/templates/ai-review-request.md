# AI Review Request

Use the project-specific AI rubric when available. Replace bracketed fields.

```text
Act as an advisory reviewer for [project and gate]. You cannot pass or fail the
gate. Apply [rubric path] to the repository at [commit/PR].

Business brief and scope:
[brief path and relevant non-goals]

Evidence supplied:
- changed files or diff: [path/link]
- tests and commands already run: [commands/results]
- architecture/evaluation reports: [paths]
- known limitations: [list]

Review rules:
1. Cite a file, symbol, test, trace, metric, or missing artifact for every
   material finding.
2. Separate blocking findings, correctness/reliability concerns, and optional
   improvements.
3. Check the rubric's critical or blocking conditions explicitly.
4. Challenge unsupported claims, model-controlled authority, evaluation
   leakage, and code the learner may not understand.
5. Do not invent runtime results or assume framework use proves behavior.
6. Do not request or reveal private mentor holdout answers.
7. Do not call the system production-ready or declare the gate passed.
8. Ask up to five technical-defense questions based on the highest-risk areas.

Output:
- evidence reviewed;
- blocking findings;
- other material findings;
- optional improvements;
- unsupported claims;
- suggested defense questions;
- checks that remain unverified.
```

The learner must classify material findings as accepted, corrected, rejected,
or deferred and cite the evidence behind that decision.
