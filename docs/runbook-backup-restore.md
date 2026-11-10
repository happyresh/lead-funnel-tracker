# Runbook: Backup and Restore

> This project has no database. What needs protecting is the code, the committed synthetic samples and their seeds. Any report can be rebuilt from a sample file.

## Principles
- GitHub (`origin`, private) is the backup of code, docs and `data/sample/`.
- Generated reports in `reports/` are throwaway; rebuild them instead of backing them up.
- Real lead exports are never stored in the repository or its backups.

## Backup
1. Push the task branch after each work session (`/agent-workflow:save`).
2. Every committed sample file has its seed in its name (`leads-seed42.csv`).

## Restore Rehearsal
1. Clone the repository into a temporary folder.
2. `uv sync`, then `uv run pytest`.
3. Regenerate a sample: `uv run lead-funnel synth --rows 500 --seed 42 --out .tmp/leads-seed42.csv`, and confirm it is byte-identical to `data/sample/leads-seed42.csv`.
4. Run a report from it and open the `.xlsx`.
5. Delete the temporary folder.

## Evidence
Record the date and result in `docs/activity-log.md`.

## Final Rule
Ask the developer before deleting any file outside `.tmp/` or `reports/`.
