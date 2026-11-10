# Runbook: Local Development

> The daily routine for working on this project. Commands come from `docs/build-guide.md` section 1.

## Principles
- Work on a `feature/<slug>` or `fix/<slug>` branch from `main`; never commit directly to `main`.
- Use synthetic data only (`data/sample/` or `lead-funnel synth`). Real lead exports stay outside the repository.

## Session Start
1. `git switch main` and `git pull`.
2. Create or switch to the task branch: `git switch -c feature/<slug>`.
3. `uv sync` if `pyproject.toml` or `uv.lock` changed.
4. In Claude Code, start the session so it reads `docs/context.md` section 2.

## Environment Safety
- No secrets are needed. If one is ever added, `.env` is never committed and `.env.example` lists names only.
- Reports go to `reports/`, which is Git-ignored.
- Ask before any command that deletes files.

## Fast Checks
Run before every commit:

```text
uv run ruff check .
uv run pytest
```

## End of Session
1. Run the fast checks.
2. Commit with a clear message, or leave a note in Current State if unfinished.
3. Update `docs/context.md` section 2 and `docs/activity-log.md`.
