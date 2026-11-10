# Build Guide

**Status:** Control

## 1. Project Setup Facts

Claude fills this section during setup by reading the repository. Agents use it for every command.

| Fact | Value |
|---|---|
| Working mode | Solo |
| Development branch | none; task branches `feature/<slug>` and `fix/<slug>` cut from `main` |
| Production branch | `main` |
| Install command | `uv sync` (planned; `pyproject.toml` is created by the first feature) |
| Test command | `uv run pytest` |
| Typecheck / lint command | `uv run ruff check .` (no type checker; add one only if a real bug calls for it) |
| Build command | none (run with `uv run lead-funnel ...`) |
| Run command | `uv run lead-funnel report <leads.csv or .xlsx> --week <YYYY-Www> --out reports/` (planned) |
| Paths that need human approval to release | `pyproject.toml`, `uv.lock` (new dependencies), `data/sample/**` (privacy check), `.githooks/**` |
| How to confirm a development deploy works | No deploy. The pre-push hook (ruff + pytest) passes, and the CLI run on `data/sample/` writes a report that opens in Excel with the expected per-agency totals |

## 2. Read Order

Before substantial work, read:

1. `docs/context.md` (loaded automatically through `CLAUDE.md`)
2. `docs/index.md`
3. `IDEA.md`
4. `docs/prd.md`
5. `docs/sdd.md` and any `docs/rfc-<topic>.md` for the area
6. `docs/qad.md`
7. `docs/sad.md` (before changing any code)
8. `DESIGN.md` (before changing commands, flags, output or error messages)
9. `docs/compliance.md` (before handling personal data)
10. this guide

Also check `docs/deferred-features.md` so nothing hidden on purpose gets rebuilt.

## 3. Golden Paths

The one correct way to do common risky tasks in this CLI + data project.

### Argument parsing

```text
argparse (standard library) -> validate paths and --week before any work -> usage error on stderr with exit code 2
```

No extra CLI library. Every flag has help text; `--help` works on every command.

### Safe file writes

```text
resolve --out -> create the folder if missing -> write to a temp file in the same folder -> os.replace onto the final name
```

Never overwrite an existing report without `--force`. Never write outside the folder given by `--out`.

### Clear errors

```text
expected problem (missing file, bad column, bad week) -> one-line message naming the file, row or flag and the fix -> exit code 1
unexpected exception -> short message plus "run with --debug for details" -> exit code 3
```

No stack traces by default. Error messages never print lead names, emails or phones.

### Raw to clean to metrics to report

```text
load (CSV or xlsx) -> check required columns -> normalize (trim, stage names, dates) -> drop duplicate lead ids (count them)
-> filter to the ISO week -> reached-stage counts per agency -> conversion rates (0 leads -> "n/a", never divide by zero)
-> write xlsx (text cells escaped against formula injection) -> print a summary of rows read, rejected and duplicated
```

Every dropped or rejected row is counted and reported; nothing disappears silently. Metrics are pure functions tested on hand-checked fixtures.

### Dataset versioning

```text
synthetic generator with --seed -> same seed gives the same file -> sample file committed under data/sample/ with its seed in the name
```

Only synthetic data is committed. Real exports stay outside the repository.

## 4. Conventions

### Always
- validate external input;
- test happy, sad and abuse paths;
- count and report every rejected or duplicate row;
- escape text cells that start with `=`, `+`, `-` or `@` before writing them to Excel;
- fix the random seed in anything that generates data.

### Never
- weaken security to make a test pass;
- commit real lead data, even "just for a test";
- print personal data in logs, errors or reports;
- divide by a count that can be zero.

### Restraint ladder

Before adding complexity, ask in order: does it need to exist? Does the repo already have a pattern? Can the platform do it? Can an installed dependency do it? Can a small explicit implementation do it? Only then add an abstraction or dependency. Never cut security, privacy, validation, tests or accessibility for simplicity.

## 5. Change Workflow

Changing anything approved (a PRD feature, data model, permissions, privacy, API contract, design system or reviewer rule) needs a change record. Follow `docs/change-workflow.md`: change record, then superpowers spec and plan, then implement, review, update documents, and mark the change record Applied.

## 6. Review and Sign-off

Run reviews with `claude --agent review-orchestrator`, following `docs/sad.md` section 4. Missing or BLOCKED reviews mean no sign-off. Changing code after a review cancels that review.

## 7. Release Sequence

Solo mode uses the **short release**. Run with `/agent-workflow:ship` or `claude --agent release-integrator`. Any failure stops later steps.

1. **S-R1 Review:** the task branch passes the review pipeline against `main` (`claude --agent review-orchestrator`), plus a Codex review if the Codex plugin is installed.
2. **S-R2 Checks:** `uv run ruff check .` and `uv run pytest` pass on the final head commit; the pre-push hook (`.githooks/pre-push`) enforces this on every push. There is no hosted CI.
3. **S-R3 Requirements QA:** `requirements-qa-gate` confirms each feature in the branch meets its PRD gates.
4. **S-R4 Merge:** after the developer approves, merge the PR into `main` (no force-push, no history rewrite).
5. **S-R5 Check:** on `main`, run the CLI on `data/sample/` and open the report.

The full R1 to R6 sequence (integration branch, development branch, production approval) applies only if the tool is ever deployed to real users; add a `dev` branch first.

## 8. Human Intervention Block

When a human must act, agents report exactly this:

```text
HUMAN INTERVENTION REQUIRED: <title>

Why:
<verified reason>

Developer steps:
1. <exact action>

Expected result:
<what should be observed>

Reply with:
<exact response needed>

Blocked:
<what is stopped>

Can continue:
<what is still safe to do>
```

## 9. Definition of Done

- [ ] feature gate criteria satisfied
- [ ] happy, sad and abuse tests pass
- [ ] all required reviewers PASS on the final code
- [ ] no secrets or real personal data committed
- [ ] docs and `docs/index.md` updated if a requirement changed
- [ ] activity log updated
- [ ] career evidence recorded (`/evidence` in the Brain vault)
