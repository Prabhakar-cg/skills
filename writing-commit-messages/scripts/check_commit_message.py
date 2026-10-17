#!/usr/bin/env python3
"""Validate a commit summary line against the Conventional Commits format
used by this skill. Exits 0 and prints "OK" if valid, otherwise exits 1
and explains exactly what's wrong so the caller can fix and re-check.
"""
import re
import sys

# Keep in sync with the type table in references/conventional-commits.md.
ALLOWED_TYPES = ("feat", "fix", "chore", "refactor", "docs", "test", "perf", "ci", "revert")

# GitHub truncates commit summaries in several UIs around 72 chars; this
# keeps messages readable in `git log --oneline` and PR titles.
MAX_SUMMARY_LEN = 72

SUMMARY_PATTERN = re.compile(
    r"^(?P<type>[a-z]+)(?:\((?P<scope>[\w./-]+)\))?(?P<breaking>!)?: (?P<summary>.+)$"
)


def check(line: str) -> list[str]:
    errors = []
    line = line.strip()

    if not line:
        return ["commit summary is empty"]

    if len(line) > MAX_SUMMARY_LEN:
        errors.append(f"summary line is {len(line)} chars; keep it under {MAX_SUMMARY_LEN}")

    if line.endswith("."):
        errors.append("summary line should not end with a period")

    match = SUMMARY_PATTERN.match(line)
    if not match:
        errors.append(
            "summary line must match 'type(scope): description' or 'type: description' "
            f"(got: {line!r})"
        )
        return errors

    commit_type = match.group("type")
    summary = match.group("summary").strip()

    if commit_type not in ALLOWED_TYPES:
        errors.append(
            f"type '{commit_type}' is not one of: {', '.join(ALLOWED_TYPES)} "
            "(see references/conventional-commits.md)"
        )

    if not summary:
        errors.append("description after 'type:' is empty")
    elif summary[0].isupper():
        errors.append("description should start lowercase (imperative style, e.g. 'add', not 'Add')")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_commit_message.py '<commit summary line>'", file=sys.stderr)
        return 2

    errors = check(sys.argv[1])
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
