# Weekly Funnel Report Design (F2 + F3)

**Date:** 2026-11-10
**Status:** Approved (developer, 2026-11-10)
**Change record:** none (first build of Draft PRD features F2 and F3)
**Migration:** none

## Context

F1 (`lead-funnel check`) and F4 (`lead-funnel synth`) shipped to the public repo `happyresh/lead-funnel-tracker` (main `d50f456`). The product's purpose — a weekly per-agency conversion report in Excel — needs F2 (metrics) and F3 (Excel output). The developer chose (2026-11-10 brainstorm) to build them together as one `report` command, list all agencies even when quiet, and compute every number in Python. Deadline: v1 by 2026-11-16. This is the approved design; the implementation plan is `docs/superpowers/plans/2026-11-10-f2-f3-report.md`.

## Decisions (developer, 2026-11-10)

1. F2 and F3 ship together as `lead-funnel report`.
2. Every agency in the file gets a row; quiet agencies show zeros and "n/a", sorted last.
3. Python computes all values; the workbook holds plain values and number formats, no formulas.
4. Snapshot model: a lead's current stage, grouped by the ISO week of `captured_on`.
5. The safe-write helper moves from `synth.py` to `files.py` (F4 spec decision 8: move when a second user needs it); `synth` reuses it.

## Modules

| File | Purpose | Interface |
|---|---|---|
| `src/lead_funnel/metrics.py` (new) | Pure weekly funnel math | `parse_week(text) -> tuple[date, date]` (raises `ValueError`); `default_week(today: date) -> str`; `weekly_funnel(leads: list[Lead], week: str) -> FunnelReport` |
| `src/lead_funnel/report.py` (new) | Excel output | `write_report(report, load: LoadResult, source_name: str, out_dir: Path, force: bool, generated_at: datetime) -> Path` |
| `src/lead_funnel/files.py` (new) | Shared safe write | `atomic_write(path: Path, force: bool, write_fn: Callable[[Path], None]) -> None` |
| `src/lead_funnel/synth.py` | Use `atomic_write` in `write_csv` | unchanged signature |
| `src/lead_funnel/cli.py` | Add `report`; split `_print_summary` so its first three lines are shared by `check` and `report` | `main(argv) -> int` |

Reuse: `load_leads`, `Lead`, `LoadResult` (`load.py`); `STAGES` (`stages.py`); `generate_leads` for the performance test; the `--debug` parent parser and `_error` in `cli.py`.

`AgencyFunnel(agency: str, reached: tuple[int, int, int, int])` with properties `step_rates -> tuple[float | None, ...]` (3) and `overall -> float | None`.
`FunnelReport(week: str, start: date, end: date, agencies: list[AgencyFunnel], total: AgencyFunnel, leads_in_week: int)`.

## F2 Metrics

- `parse_week` accepts exactly `YYYY-Www`; uses `date.fromisocalendar(y, w, 1)`, so `2026-W60` and week 53 in years without one fail. CLI maps failure to exit 2: `--week must look like 2026-W46`.
- `default_week(today)` = ISO week of `today - 7 days` (last complete week). Summary says `(last complete week)` when used.
- Week filter: `start <= captured_on <= end` (Monday to Sunday inclusive).
- Reached counts: a lead at stage k counts at stages 0..k.
- Step rate i = `reached[i+1] / reached[i]`; overall = `reached[3] / reached[0]`; zero denominator -> `None` (shown "n/a").
- Agencies: every agency appearing in `leads` (all weeks); sorted by `reached[0]` descending, then name ascending. Total = element-wise sum.
- One pass over leads.
- Example: 4 leads at Lead, Contacted, Intro session, Onboarded -> reached (4, 3, 2, 1); rates 75.0%, 66.7%, 50.0%; overall 25.0%.

## F3 Excel Report

- Path is always `<out_dir>/funnel-<week>.xlsx` (name built by the tool, never from input). `out_dir` created if missing. Existing file and no `force` -> `FileExistsError`.
- `atomic_write`: write to a temp file in the target folder, `os.replace` onto the final path, delete temp on any failure.
- Sheet `Funnel`: row 1 title `Lead funnel 2026-W46 (2026-11-09 to 2026-11-15)` bold; row 3 header `Agency, Lead, Contacted, Intro session, Onboarded, Lead→Contacted, Contacted→Intro, Intro→Onboarded, Overall` bold; panes frozen at A4; agency rows; bold `Total` row. Counts `#,##0`; rates `0.0%`; `None` -> text `n/a`, right-aligned. Column widths fit content, max 40.
- Clustered bar chart (openpyxl `BarChart`) of the four stage counts per agency (Total excluded), anchored right of the table.
- Sheet `About`: input file name, rows read, rows rejected, duplicates removed, week, date range, leads in week, generated time, tool version (`importlib.metadata.version("lead-funnel")`). No personal data on any sheet.
- Formula-injection guard: one helper writes every text cell; values starting with `=`, `+`, `-`, `@`, tab or CR are stored as strings (`data_type = "s"`). Applies to agency names and the source file name.

## Interface (CLI)

```text
lead-funnel [--debug] report FILE [--week YYYY-Www] [--out DIR] [--force]
```
- `--out` default `reports/`; `--debug` accepted before or after `report`; help epilog example from DESIGN.md.
- stdout:
```text
Read 1,240 rows from leads.csv
Rejected 3 rows (unknown stage: 2, bad date: 1)
Removed 5 duplicate lead ids
Week 2026-W46: 312 leads across 6 agencies
Wrote reports/funnel-2026-W46.xlsx
```
  "across N agencies" counts agencies with at least one lead that week. Empty week: `No leads in 2026-W46; wrote an empty report` then the `Wrote` line, exit 0. Rejected-row details to stderr as in `check`.
- Exit codes: 0 written; 1 load error, `FileExistsError` (`Error: <path> already exists. Use --force to replace it.`), `PermissionError` (`Error: cannot write <path>. Close it in Excel and try again.`); 2 bad `--week`/usage; 3 unexpected.

## Security and Privacy

Output only inside `--out` with a tool-built name; no formulas in the file; text cells escaped; only agency names and counts written; no lead ids or contact data in the report.

## Testing (test-first; expected numbers hand-counted in each test)

| File | Covers |
|---|---|
| `tests/test_metrics.py` | parse_week valid / `W60` / no-W53 year / junk; default_week (Tuesday -> previous week; 2026-01-05 -> `2026-W01`); hand-checked 3-agency fixture (QAD-F2-1); Lead-only agency (F2-2); 100,000 synthetic leads under 10 s (F2-3); Sunday in W46 / Monday in W47 (F2-5); zero Contacted -> None (F2-7); all agencies empty (F2-9); quiet agencies listed last with zeros; tie order; Total = sum |
| `tests/test_report.py` | sheets, headers, formats, n/a, chart present (F3-1); 200-char agency full text, width capped (F3-2); failure mid-save leaves no file (F3-3); `Acme`, `-Minus Media`, `=HYPERLINK(...)` stored as strings and no `<f>` in sheet XML (F3-4..6); About sheet has no personal data |
| `tests/test_files.py` | atomic_write creates folders, refuses overwrite without force, leaves no temp file (moved from test_synth) |
| `tests/test_cli.py` | exact report stdout; `--week 2026-W60` and `lastweek` exit 2 (F2-6); empty week exit 0 (F2-8); `--out` created (F3-7); existing without `--force` exit 1 (F3-8); PermissionError exit 1; `--debug` after subcommand; help example |
| `tests/fixtures/week46.csv` | 3 agencies plus leads on 2026-11-08 and 2026-11-16 (excluded) |

## Documents Updated in the Same Change

`docs/prd.md` F2/F3 gates confirmed; `docs/qad.md` rows aligned; `docs/context.md` section 11 decisions 1–5 and section 2; `docs/index.md` spec, plan, traceability F2/F3; `README.md` Try it adds `report`; `README-setup.md` replaces the stale "Open reports/…" step (line 35) with the real `report` command.

## Out of Scope

Week-over-week trends, multiple weeks per run, Google Sheets, live Excel formulas, pivot tables, the deferred F1 minors.

## Risks

- openpyxl chart rendering differs slightly between Excel and LibreOffice; verified by opening in Excel manually once.
- Report includes a generated timestamp, so files are not byte-identical between runs (tests pass `generated_at`).

## Verification (after build)

- `uv run ruff check .` and `uv run pytest` pass (pre-push hook enforces on push).
- `uv run lead-funnel synth --rows 500 --seed 42 --out .tmp/leads.csv --force` then `uv run lead-funnel report .tmp/leads.csv --week 2026-W46 --out .tmp/reports` prints the five lines; open `.tmp/reports/funnel-2026-W46.xlsx` in Excel: table, Total row, chart, About sheet, no repair warning.
- Reviewer pipeline (`claude --agent review-orchestrator`) on the branch before merge.
