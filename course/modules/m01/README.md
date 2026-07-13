# M01: Git, GitHub, VS Code, and Coding-Agent Discipline

## Learning objectives

By the end of this module, you can:

- Explain working tree, index, commit, branch, remote, pull request, and merge.
- Perform the required workflow in the terminal and identify its VS Code
  equivalent.
- Review an AI-generated diff before committing it.
- Resolve a basic content conflict without discarding either side's intent.
- Keep commits and pull requests narrow enough to review.

## Prerequisite diagnostic

Explain what each command changes before running it:

```text
git status
git diff
git add
git commit
git switch -c
git push
git merge
```

If you cannot distinguish working-tree changes from staged changes, complete the
guided lab slowly and inspect status after every operation.

## Required reading

- [VS Code source-control references](../../../docs/reference-catalog.md#ref-vscode-git)
- The coding-agent reference selected in M00.

## Concept lesson

### Git is an evidence system

Git is not merely backup. A useful history explains how and why software
changed. Reviewers need to distinguish the intended change from generated noise.

A reviewable change has:

- One coherent purpose.
- A diff that matches that purpose.
- Tests or evidence appropriate to the risk.
- No unrelated formatting or generated files.
- A commit message describing the outcome.

### Review the diff, not the agent's summary

An agent summary may omit accidental changes. Before committing:

1. Inspect `git status`.
2. Inspect unstaged and staged diffs.
3. Check for secrets, generated files, and unrelated edits.
4. Run relevant checks.
5. Ask why each changed file is necessary.

### Conflict resolution is intent resolution

A merge conflict means Git cannot choose between competing text changes. The
correct result is not automatically “ours,” “theirs,” or both. Determine the
intent of each branch, produce the desired combined behavior, remove conflict
markers, and test the result.

## Guided lab: branch to pull request

1. Create a branch named `course/m01-git-workflow`.
2. Add a short M01 learning note.
3. Inspect the change in VS Code and the terminal.
4. Stage only the intended file.
5. Commit with an outcome-focused message.
6. Push the branch and open a pull request.
7. Review the Files Changed view before requesting review.
8. Merge only after the gate is approved.

Record the terminal command and VS Code action for each step.

## Independent challenge: resolve supplied conflict

Run the setup helper in a disposable directory:

```bash
python course/modules/m01/setup_conflict_lab.py /tmp/m01-conflict-lab
```

The helper creates a repository with `main` and `feature/validation-copy`. Merge
the feature branch into `main`, resolve the conflict, and preserve both intended
requirements:

- Invalid records must be rejected with a reason.
- Processing must retain a correlation identifier.

Do not solve the conflict by deleting one requirement.

## Failure-analysis exercise

Ask a coding agent to review this hypothetical status:

```text
M  src/client.py
M  README.md
?? .env
?? debug-response.json
?? architecture.md
```

The requested task was “add a timeout to the client.” Identify what must be
inspected, what likely should not be committed, and what questions must be
answered before accepting the diff.

## Comprehension gate

Demonstrate:

- A clean branch and pull request.
- A basic conflict resolution.
- Inspection of staged and unstaged diffs.
- Rejection or removal of an unrelated agent-generated change.

Then explain working tree, index, commit, branch, remote, pull request, and merge
using the artifacts you just created.

## Interview questions

1. How do you keep AI-generated changes reviewable?
2. Why can a passing test suite be insufficient before a merge?
3. How do you decide the correct resolution to a merge conflict?
4. What should never be committed from an LLM-backed development workflow?

## Required GitHub evidence

- Pull request and review comments.
- Conflict-resolution note.
- Before-and-after status or diff evidence.
- AI work-log entry describing one rejected change.
