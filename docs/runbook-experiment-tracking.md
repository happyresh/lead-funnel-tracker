# Runbook: Experiment Tracking

> The data profile asks for this runbook. There is no model here, so the "experiments" are dataset versions and report runs. The goal is that any number in a report can be reproduced and explained.

## Principles
- Same input file, same week, same tool version: same report.
- Every dataset has a seed; every report records its inputs on its `About` sheet.

## Dataset Versions

| File | Seed | Rows | Generator version | Purpose |
|---|---|---|---|---|
| Guide: one row per committed sample, for example `data/sample/leads-seed42.csv` | 42 | 500 | 0.1.0 | Tests and demo |

## Reproducing a Report
1. Check out the commit whose version is on the report's `About` sheet.
2. `uv sync`.
3. Rerun the command with the same input file and `--week`.
4. Compare the two reports' `Funnel` sheets cell by cell (a test helper may do this).

## When a Number Looks Wrong
1. Rerun on the sample file and compare with the hand-checked fixture in `tests/fixtures/`.
2. Check the `About` sheet: rows rejected and duplicates removed.
3. Add a fixture that reproduces the problem before fixing it (`fix/<slug>` branch).

## Evidence
Record dataset changes and investigations in `docs/activity-log.md`.
