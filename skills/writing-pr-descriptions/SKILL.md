---
name: writing-pr-descriptions
description: Drafts clear pull request titles and descriptions from a branch's commits and diff. Use when the user asks for help writing a PR description, summarizing a branch for review, or preparing to open a pull request.
---

# Writing PR Descriptions

## Quick start

1. Read the branch changes: `git log main..HEAD --oneline` and `git diff main...HEAD`
2. Identify the purpose of the change as a whole, not commit by commit.
3. Write the title and description using the format below.

## Format

```
Title: imperative summary under 72 chars

## Summary
What changed and why, in 1-3 sentences.

## Changes
- Notable change one
- Notable change two

## Testing
How the change was verified (tests run, manual steps).
```

Omit `Testing` only if nothing was verified, and say so explicitly rather than leaving it blank.

## Guidelines

- Lead with the reason for the change; the diff already shows the what.
- Call out breaking changes, migrations, and follow-up work in their own bullet.
- Keep it reviewable: if the branch mixes unrelated changes, suggest splitting the PR.
