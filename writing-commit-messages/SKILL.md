---
name: writing-commit-messages
description: Generates descriptive, Conventional Commits-style commit messages by analyzing a git diff. Use when the user asks for help writing a commit message, summarizing staged changes, or reviewing a diff before committing.
---

# Writing Commit Messages

## Quick start

1. Read the diff: `git diff --staged` (or `git diff` if nothing is staged yet)
2. Identify the single primary change. If the diff mixes unrelated changes, say so and suggest splitting the commit.
3. Write a message using the format below.

## Format

```
type(scope): short imperative summary (under 72 chars)

Longer explanation of why the change was made, if the summary
isn't self-explanatory. Wrap at ~72 chars.
```

`type` is one of `feat`, `fix`, `chore`, `refactor`, `docs`, `test`, `perf`, `ci`. `scope` is optional and names the affected area (e.g. `auth`, `ci`). See [references/conventional-commits.md](references/conventional-commits.md) for the full type list and edge cases (breaking changes, reverts).

## Examples

**Example 1:**
Input: Added user authentication with JWT tokens
Output:
```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```

**Example 2:**
Input: Fixed bug where dates displayed incorrectly in reports
Output:
```
fix(reports): correct date formatting in timezone conversion

Use UTC timestamps consistently across report generation
```

## Validate before finalizing

Run the summary line through the checker script before presenting it:

```bash
python scripts/check_commit_message.py "feat(auth): implement JWT-based authentication"
```

It exits non-zero and explains what's wrong (wrong type, missing summary, summary too long, trailing period) if the line doesn't fit the format. Fix the message and re-run until it passes.
