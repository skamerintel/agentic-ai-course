# Capstone Studio Validator

This package validates the capstone proposal and final artifact manifest. It is
course-development tooling, not the capstone product.

```bash
uv sync
uv run pytest
uv run capstone-studio validate-proposal proposal.json
uv run capstone-studio validate-artifacts \
  artifact-manifest.json data/required-artifacts.json
```

Implement the two functions in `src/capstone_studio/validator.py`. Keep the
Pydantic models strict, report every actionable finding in one run, and separate
blocking findings from warnings.

Your capstone product should have a separate FastAPI/LangGraph package, tests,
uv/Hatchling build, and Docker stack. Do not add those dependencies to this
validator merely to satisfy the course checklist.
