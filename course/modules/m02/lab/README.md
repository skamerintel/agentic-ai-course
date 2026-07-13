# Flawed Ticket Rules Package

This is a small `uv` package containing deliberately flawed validation code and
tests that mock the unit under test.

Run the initial checks:

```bash
cd course/modules/m02/lab
uv sync
uv run pytest
uv run ruff check .
uv run pyright src
```

Some checks can pass even though the required behavior is missing. That is the
point of the exercise. Replace the weak tests before repairing the implementation.

Required public behavior:

```text
validate_ticket(title: str, priority: str) -> tuple[str, str]
```

- Strip leading and trailing whitespace from `title`.
- Reject a title that is empty after stripping.
- Preserve internal title spacing.
- Normalize priority to lowercase.
- Accept only `low`, `medium`, `high`, and `critical`.

The mentor may run the separate `acceptance_tests` after your submitted tests
pass.
