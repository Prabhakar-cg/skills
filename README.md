# Skills

A collection of [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview), one folder per skill under `skills/`.

## Layout

```
skills/
  <skill-name>/
    SKILL.md          # required: frontmatter + instructions
    references/       # optional: longer docs loaded on demand
    scripts/          # optional: helper scripts the skill runs
    assets/           # optional: templates and other files
scripts/validate_skills.py
.github/workflows/validate-skills.yml
```

## Current skills

- `writing-commit-messages`: Conventional Commits messages from a git diff
- `writing-pr-descriptions`: PR titles and descriptions from a branch

## Adding a skill

1. Create `skills/<skill-name>/SKILL.md`. Use lowercase letters, numbers, and hyphens; keep the directory name identical to the `name` in the frontmatter.
2. Start the file with frontmatter:

   ```markdown
   ---
   name: my-skill
   description: What the skill does and when to use it.
   ---

   # My Skill

   Instructions go here.
   ```

   - `name`: max 64 characters, must not contain `anthropic` or `claude`, must be unique across the repo.
   - `description`: required, max 1024 characters, no XML tags. Say both what the skill does and when to use it.
3. Put long material in `references/` and link to it from `SKILL.md` (for example `[details](references/details.md)`). Every referenced file must exist.
4. Validate locally:

   ```bash
   pip install pyyaml
   python scripts/validate_skills.py                 # all skills
   python scripts/validate_skills.py skills/my-skill # one skill
   ```

5. Open a pull request. `main` is protected, so changes go through a PR.

Warnings do not fail the build but are worth fixing: a `SKILL.md` body over 500 lines, reference files over 100 lines without a table of contents, and a directory name that differs from `name`.

## CI

The `Validate Skills` workflow runs on pushes to `main`, pull requests, and manual dispatch:

- `Discover skills` finds every directory containing a `SKILL.md`.
- `Validate skills/<name>` runs once per skill, so a failure points at the skill responsible.
- `Validate SKILL.md structure` validates all skills together and catches duplicate names. This is the required status check for merging.

New skills are picked up automatically; the workflow needs no edits.
