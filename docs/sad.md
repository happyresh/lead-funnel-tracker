# Subagent Document (SAD)

**Status:** Control

## 1. Purpose

Reviewers are read-only helpers, not owners. This document is the single source of truth for every reviewer. The job cards in `.claude/agents/` only point here.

## 2. Roster

Team for the **CLI tool + Data / analysis** profiles. `database-guardian` was removed (no database). Trigger paths match the planned layout in `docs/context.md` section 8; `**` matches any number of folders. They are the minimum: a coordinator adds a reviewer whenever a change clearly touches its area, even if no pattern matches.

| Reviewer | Protects | Trigger paths | ISO 25010 pillars | Model |
|---|---|---|---|---|
| security-guardian | File paths, formula injection, unsafe parsing, secrets | `src/lead_funnel/cli.py`, `src/lead_funnel/load*.py`, `src/lead_funnel/report*.py`, `src/lead_funnel/**/*io*.py`, `.githooks/**`, `**/.env.example` | Security | opus |
| privacy-guardian | Personal data in sample files, reports, logs and errors | `src/lead_funnel/**`, `data/**`, `tests/fixtures/**`, `docs/reference/**` | Security, Compatibility | opus |
| data-quality-guardian | Correct numbers: validation, duplicates, week boundaries, no silent row loss, reproducible seeds | `src/lead_funnel/load*.py`, `src/lead_funnel/metrics*.py`, `src/lead_funnel/synth*.py`, `src/lead_funnel/report*.py`, `data/**`, `tests/fixtures/**` | Functional Suitability, Reliability | sonnet |
| cli-ux-guardian | Flags, help text, exit codes, output and error messages | `src/lead_funnel/cli.py`, `src/lead_funnel/__main__.py`, `pyproject.toml` (`[project.scripts]`), `DESIGN.md` | Usability, Compatibility | sonnet |
| restraint-guardian | No needless libraries or complexity | `pyproject.toml`, `uv.lock`, `requirements*.txt`, `.githooks/**` | Maintainability | sonnet |
| design-qa-agent | General quality across all eight areas | every changed file under `src/**` and `tests/**` | All eight | sonnet |
## 3. Rules

### security-guardian
- Input and output paths come from the user's flags only; reports are written inside `--out`, never outside it (no `..` escapes), and never overwrite without `--force`.
- Text written to Excel cells that starts with `=`, `+`, `-`, `@`, tab or carriage return is escaped (prefixed with `'` or stored as an explicit string); no formulas are built from input values.
- Files are parsed with openpyxl or the `csv` module only; never `eval`, `pickle`, shell commands or macros (`.xlsm`) on input.
- Secrets, if any ever exist, live in environment variables, never in code, logs or reports.

### privacy-guardian
- Only synthetic data is committed: sample and fixture files use fake names and `example.com`-style emails; anything that looks real is BLOCKED.
- Reports contain per-agency totals only, never individual lead names, emails or phones.
- Personal data never appears in log lines, error messages or the CLI summary.

### data-quality-guardian
- Every rejected, filtered or duplicate row is counted and reported; no row disappears silently.
- Required columns and stage names are validated before any metric is computed; unknown stages are rejected, not guessed.
- Report week is the ISO week (Monday to Sunday) of the capture date; boundaries are tested on Sunday and Monday dates.
- Conversion rates never divide by zero; an empty step shows "n/a".
- Anything random takes an explicit seed; the same seed gives byte-identical sample data.

### cli-ux-guardian
- Every command and flag has help text; `--help` works and shows an example.
- Exit codes: 0 success, 1 expected error (bad input), 2 usage error, 3 unexpected error.
- Results go to stdout, errors and warnings to stderr; output is readable without color.
- Error messages name the file, row or flag and say how to fix it; no stack trace unless `--debug`.
- Output and messages follow `DESIGN.md`.

### restraint-guardian
- Flag every new external dependency; it needs a reason the standard library, openpyxl or an existing dependency cannot cover (for example no pandas for a few group-bys, no click for one command).
- Flag abstractions that add coupling without a current need. Never cut security, validation, tests or accessibility for simplicity.

### design-qa-agent

| Pillar | Check |
|---|---|
| Functional Suitability | Type hints on public functions, gate criteria met, edge cases handled |
| Performance Efficiency | Single pass over the input where possible; handles 100,000 rows without loading needless copies |
| Compatibility | Input column names and report layout stay compatible with earlier versions |
| Usability | CLI follows `DESIGN.md`; report readable in Excel (headers, number formats, column widths) |
| Reliability | Clear errors, safe file writes, no partial reports left behind |
| Security | Validated input, escaped cells, no secret leakage |
| Maintainability | Small cohesive modules, pure metric functions, tests next to behavior |
| Portability | Works on Windows and Linux; `pathlib` paths, no machine-specific paths, UTF-8 everywhere |

A PASS must state all eight pillars were considered; mark unrelated ones "not applicable". CLI changes are also checked against `DESIGN.md` section 6 Quality Gate.

## 4. Review Pipeline

Steps run in order. A failed gate stops every later step.

| Step | Action | Output |
|---|---|---|
| S0 Ground | Read `docs/index.md`, `docs/build-guide.md` and the documents related to the change. | document list |
| S1 Route | List changed files and match them to the roster trigger paths. | reviewer/file pairs |
| S2 Review | Send one work order per reviewer, at most 4 at a time. | report envelopes |
| G1 Gate | Any BLOCKED stops work; findings go to the developer. | pass or fix list |
| S3 Fix | The developer or main session fixes and tests. The coordinator never edits code. | changed code |
| S4/S5 Re-check | Route again; re-review with open findings in `prior_findings`. | final envelopes |
| S6 Assemble | Merge final envelopes into `.tmp/review/<run>/reviews.json`. | evidence file |
| G2 Sign-off | Every routed reviewer/file pair has PASS on the final code. | sign-off or Human Intervention block |

## 5. Work Order (Handoff Packet)

```json
{
  "run_id": "20261112-1430-funnel-metrics",
  "stage": "S2",
  "change_digest": "<fingerprint of the change>",
  "role": "data-quality-guardian",
  "paths": ["src/lead_funnel/metrics.py"],
  "contracts": ["docs/sad.md", "docs/prd.md"],
  "prior_findings": [],
  "constraints": ["read-only", "review listed paths only", "return section 6 envelope only"]
}
```

## 6. Report Format (Envelope)

One entry per finding, or one PASS entry per reviewed file. `implicated_lines` is a list of positive line numbers, `[]` if none.

```json
{
  "subagent_evaluations": [
    {
      "subagent": "data-quality-guardian",
      "status": "BLOCKED",
      "iso_25010_compliance": ["Functional Suitability", "Reliability"],
      "findings": {
        "file_path": "src/lead_funnel/metrics.py",
        "implicated_lines": [42],
        "violation_evidence": "Conversion rate divides by the Contacted count, which is 0 for agencies with no contacted leads."
      },
      "prescribed_remediation": "Return None for an empty step and render it as \"n/a\"; add a fixture test for an agency with zero contacted leads."
    }
  ]
}
```

## 7. Evidence

Fingerprints, work orders and reports live in `.tmp/review/<run>/`, which is Git-ignored. Never commit them.

## 8. Maintenance

- Changing a reviewer, trigger path or model updates this file and its job card in the same commit.
- Add a reviewer only when a real mistake slipped through or a new risk area appears.
