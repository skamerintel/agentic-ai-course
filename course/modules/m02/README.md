# M02: Modern Python Project Quality with uv

## Learning objectives

By the end of this module, you can:

- Explain how `pyproject.toml`, `uv.lock`, and the project environment relate.
- Use Ruff, pytest, and basic static analysis for different purposes.
- Design tests around behavior rather than implementation accidents.
- Identify mocks that make tests meaningless.
- Review an AI-generated Python repair instead of accepting green checks blindly.

## Prerequisite diagnostic

Create a temporary `uv` application and answer:

```bash
uv init /tmp/m02-diagnostic
```

- Which file declares project metadata?
- When is a lockfile created?
- What is the difference between a runtime and development dependency?
- How would another developer reproduce the environment?

## Required reading

- [uv project references](../../../docs/reference-catalog.md#ref-uv-projects)
- [Ruff references](../../../docs/reference-catalog.md#ref-ruff)
- [pytest references](../../../docs/reference-catalog.md#ref-pytest)
- [Pyright references](../../../docs/reference-catalog.md#ref-pyright)

## Concept lesson

### One tool, one question

- Ruff asks whether source matches configured lint and formatting rules.
- pytest asks whether exercised behavior matches assertions.
- Pyright asks whether annotated values and operations are type-consistent
  without running the program.
- Pydantic, introduced later, asks whether runtime data matches a schema.

Passing one does not imply passing the others.

### Test public behavior

A strong unit test establishes inputs, invokes a meaningful unit, and checks
observable outputs or side effects. A weak test often:

- Mocks the function being tested.
- Repeats the implementation in the assertion.
- Checks only that a method was called.
- Depends on global state or live networks.
- Passes even when required behavior is removed.

### AI-generated quality theater

Coding agents may add many tests with little value. Review whether each test can
fail for a real defect. Delete or rewrite tests that only increase counts.

## Guided lab

Use the supplied [flawed package](lab/README.md). First run its tests and checks
without changing code. Write a prediction for each failure. Then ask your coding
agent for a repair plan, not an immediate edit.

Review the plan for:

- Scope.
- Assumptions.
- Test quality.
- Unnecessary dependencies.
- Whether the public behavior is clear.

## Independent challenge

Repair the package so that:

- Empty or whitespace-only ticket titles are rejected.
- Valid titles are normalized without changing internal spacing.
- Priority accepts only the documented values.
- Tests exercise the real validation function.
- Ruff and selected type checks pass.

The coding agent may implement the repair. You must explain every changed line
and reject at least one weak test or unnecessary change.

## Failure-analysis exercise

The starter test mocks `validate_ticket` and then asserts that the mock returns
the configured value. Explain why this proves nothing about validation. Replace
it with a test that fails when required behavior is broken.

## Comprehension gate

Submit the repaired package and explain:

- Why each tool is present.
- Which test catches each requirement.
- Which defect static analysis can catch that runtime tests may miss.
- Which AI proposal you rejected and why.

The mentor will mutate one line. Identify which check should catch the mutation.

## Interview questions

1. What is the difference between linting, static type checking, runtime
   validation, and automated testing?
2. When does mocking harm a test?
3. How do lockfiles improve reproducibility?
4. How would you review an AI-generated test suite?

## Required GitHub evidence

- Repair pull request.
- Test-to-requirement matrix.
- Before-and-after check output.
- AI work-log entry documenting a rejected test or change.
