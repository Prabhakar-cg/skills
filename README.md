# Skills

A collection of [Agent Skills](https://agentskills.io/home), one folder per skill under `skills/`. Skills follow the [Agent Skills specification](https://agentskills.io/specification), and CI enforces it.

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

   - `name`: required, 1-64 characters, lowercase letters, numbers, and single hyphens, no leading or trailing hyphen, and it must match the directory name. Must be unique across the repo.
   - `description`: required, 1-1024 characters. Say both what the skill does and when to use it, with keywords that help an agent recognize relevant tasks.
   - Optional: `license`, `compatibility` (max 500 characters, only if the skill has environment requirements), `metadata` (string keys to string values, e.g. `author`, `version`), and the experimental `allowed-tools`. Put any custom keys under `metadata`.
3. Put long material in `references/` and link to it from `SKILL.md` (for example `[details](references/details.md)`). Every referenced file must exist.
4. Validate locally:

   ```bash
   pip install pyyaml
   python scripts/validate_skills.py                 # all skills
   python scripts/validate_skills.py skills/my-skill # one skill
   ```

5. Open a pull request. `main` is protected, so changes go through a PR.

Keep `SKILL.md` under 500 lines (about 5000 tokens) and move detail into `references/`, linked one level deep from `SKILL.md` with relative paths. Warnings do not fail the build but are worth fixing: a `SKILL.md` body over 500 lines, reference files over 100 lines without a table of contents, and unknown frontmatter fields.

## CI

The `Validate Skills` workflow runs on pushes to `main`, pull requests, and manual dispatch:

- `Discover skills` finds every directory containing a `SKILL.md`.
- `Validate skills/<name>` runs once per skill, so a failure points at the skill responsible.
- `Validate SKILL.md structure` validates all skills together and catches duplicate names. This is the required status check for merging.

New skills are picked up automatically; the workflow needs no edits.
