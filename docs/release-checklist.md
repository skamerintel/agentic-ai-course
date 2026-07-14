# Course Release and Pilot Checklist

Use this checklist before assigning a new course revision to a learner. Run it
from a clean clone, not the author's existing development checkout.

Record results with
`course/instructor/templates/release-record.md`.

## 1. Freeze the candidate revision

- [ ] Select the commit or release candidate under review.
- [ ] Confirm the worktree is clean.
- [ ] Confirm no `.course-progress.toml`, credentials, local databases, reports,
      or learner workspaces are tracked.
- [ ] Record the Python and uv versions used.
- [ ] Review dependency and workflow-action changes.

## 2. Clean-clone setup

Clone into a new temporary directory and follow only checked-in instructions:

```bash
git clone <course-repository> /tmp/agent-course-release-check
cd /tmp/agent-course-release-check
uv sync --only-group dev --frozen
```

- [ ] Setup succeeds without relying on an activated environment from another
      repository.
- [ ] Root README links identify the course specification, roadmap, status, CI,
      and instructor handbook.
- [ ] No undocumented credential is required.

## 3. Repository-quality checks

```bash
uv run --no-sync ruff check .
uv run --no-sync ruff format --check .
uv run --no-sync python -m unittest discover -s tests -p "test_*.py"
uv run --no-sync python scripts/validate_course.py
uv run --no-sync python scripts/verify_module_references.py
```

- [ ] All commands pass.
- [ ] JSON, JSONL, TOML, YAML, Markdown links, required paths, and workflow
      security checks report expected counts.
- [ ] Test discovery makes no live provider request.

## 4. Learner-start smoke tests

From the clean clone:

```bash
python coursectl.py status
python coursectl.py start p01 /tmp/agent-course-p01-start
python coursectl.py start p08 /tmp/agent-course-p08-start
```

- [ ] Status shows `gated` references by default.
- [ ] Terminal output includes setup commands, expected test state, and first
      task.
- [ ] Each workspace contains `START_HERE.md`, `PROJECT.md`, reports, data, and
      project assets as documented.
- [ ] Neither workspace contains `course/instructor/evaluation/` or another
      private holdout path.
- [ ] P01 and P08 initial tests fail only at documented learner TODO gates.
- [ ] `--quiet` prints only the resolved workspace path.
- [ ] Starting into a non-empty directory fails without overwriting files.

Spot-check another project when course-control or shared template logic changed.

## 5. Reference and holdout checks

Verify all reference implementations:

```bash
uv run --no-project --python 3.13 python scripts/verify_reference.py p01
uv run --no-project --python 3.13 python scripts/verify_reference.py p02
uv run --no-project --python 3.13 python scripts/verify_reference.py p03
uv run --no-project --python 3.13 python scripts/verify_reference.py p04
uv run --no-project --python 3.13 python scripts/verify_reference.py p05
uv run --no-project --python 3.13 python scripts/verify_reference.py p06
uv run --no-project --python 3.13 python scripts/verify_reference.py p07
uv run --no-project --python 3.13 python scripts/verify_reference.py p08
```

- [ ] P01-P08 pass Ruff, formatting, tests, Pyright, and package builds.
- [ ] P05-P08 executable private holdouts pass against the reference.
- [ ] Commands do not use OpenAI, Anthropic, GitHub, or AWS credentials.
- [ ] Temporary workspaces are removed after success.

## 6. Solution-access checks

While the project remains locked:

```bash
python coursectl.py solution p01 /tmp/p01-locked-reference
```

- [ ] The command exits with the gated-access message and creates no reference
      workspace.

Create a temporary `.course-progress.toml`, unlock only P01, and rerun:

```bash
python coursectl.py status
python coursectl.py solution p01 /tmp/p01-unlocked-reference
```

- [ ] P01 is available while other references remain gated.
- [ ] The reference workspace includes reference guidance and passes its tests.
- [ ] Remove the temporary progress file after the check.
- [ ] Confirm `course.toml` still uses `solution_access = "gated"`.

## 7. Hosted CI check

- [ ] Push the candidate branch.
- [ ] Observe the repository-quality job.
- [ ] Observe all eight reference matrix jobs.
- [ ] Confirm no job requests secrets or live-service approval.
- [ ] Confirm action references remain full commit SHAs.
- [ ] Confirm required branch checks match the workflow job names if branch
      protection is configured.

Local success is not a substitute for observing at least one hosted run after a
workflow or runner-version change.

## 8. Documentation review

- [ ] Course and implementation dates are current where required.
- [ ] External references used by changed modules were rechecked.
- [ ] Commands are copyable from a clean shell.
- [ ] Project definitions of done agree with tests and rubrics.
- [ ] Intentional starter failures are accurately described.
- [ ] Live, Docker, remote GitHub, and human-only checks are clearly separated
      from default automation.
- [ ] Instructor-only material is labeled and not copied by `coursectl start`.

## 9. Pilot learner run

Use a learner who was not involved in authoring when possible. Give them only
the learner-facing entry point and normal mentor access.

- [ ] Observe M00 setup without explaining repository structure in advance.
- [ ] Observe one `coursectl start` flow.
- [ ] Record every command, term, expected failure, or artifact that causes
      unplanned mentor intervention.
- [ ] Distinguish missing instruction from prerequisite skill gaps.
- [ ] Track time spent on environment problems separately from learning work.
- [ ] Confirm the learner understands AI-review versus mentor authority.
- [ ] Confirm the learner can request a gate review without private knowledge.
- [ ] Run at least one full project gate and one resubmission or changed-constraint
      exercise.

Use `course/instructor/templates/pilot-observation.md` during the run.

## 10. Release decision

Choose one:

- **Release:** automated checks, clean-clone flow, hosted CI, and learner-facing
  instructions are credible.
- **Release with documented limitation:** no core gate is weakened, and the
  limitation is visible to learner and mentor.
- **Do not release:** setup, safety, evaluation integrity, reference access, or
  required learning evidence is unreliable.

Record unresolved limitations, owner, next review date, and the commit approved
for use.
