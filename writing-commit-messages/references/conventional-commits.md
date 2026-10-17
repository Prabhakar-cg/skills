# Conventional Commits Reference

## Types

| Type       | Use for |
|------------|---------|
| `feat`     | A new feature |
| `fix`      | A bug fix |
| `chore`    | Maintenance, tooling, dependency bumps |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `docs`     | Documentation only |
| `test`     | Adding or correcting tests |
| `perf`     | A performance improvement |
| `ci`       | CI/build pipeline changes |

## Breaking changes

Append `!` after the type/scope, and add a `BREAKING CHANGE:` footer explaining the migration:

```
feat(api)!: remove deprecated v1 endpoints

BREAKING CHANGE: clients must migrate to /v2 endpoints before upgrading.
```

## Reverts

```
revert: feat(auth): implement JWT-based authentication

Reverts the commit above because it broke session persistence.
```

## Scope guidance

Use the scope to name the affected module, package, or directory — not the whole repo. Omit it when the change is repo-wide (e.g. a README fix) or when a single clear scope doesn't exist.
