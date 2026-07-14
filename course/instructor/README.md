# Instructor Materials

Start with the [Instructor Handbook](../../docs/instructor-handbook.md) and the
[Course Release Checklist](../../docs/release-checklist.md).

## Directory map

- `evaluation/`: private or honor-system holdouts and mentor expectations.
- `reference/`: gated comparison implementations and solution notes.
- `templates/`: mentor session, gate, review, holdout, defense, pilot, and
  release records.

## Important boundary

`coursectl start` does not copy this directory into learner workspaces. That is
an instructional separation, not a security boundary. Keep genuinely blind or
sensitive assessment material in a private instructor-controlled location.

## Routine commands

```bash
python coursectl.py status
uv run --no-sync python scripts/validate_course.py
uv run --no-project --python 3.13 python scripts/verify_reference.py p08
```

The first command checks configured reference access. The second validates the
course repository. The third verifies the selected reference, not a learner
submission.
