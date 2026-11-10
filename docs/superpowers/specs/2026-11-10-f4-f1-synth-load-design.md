# Synthetic Leads and Lead Loading Design (F4 + F1)

**Date:** 2026-11-10
**Status:** Approved (developer, 2026-11-10)
**Change record:** none (first build of Draft PRD features; PRD G-F1-2 clarified in the same change)
**Migration:** none

## Goal

`lead-funnel synth` writes a reproducible, obviously fake lead CSV (F4), and `lead-funnel check` loads a CSV or `.xlsx` lead export, rejects and counts bad rows, removes duplicates, and prints a summary (F1). The loader's result is what F2 metrics will consume.

## Current State

- No code yet. `pyproject.toml` does not exist; CI skips its checks until it does (`.github/workflows/ci.yml`).
- PRD `docs/prd.md` F1 and F4 and QAD `docs/qad.md` rows QAD-F1-1 to F1-9 and QAD-F4-1 to F4-9 are Draft.
- PRD G-F1-2 (unknown stage stops the run) contradicts `DESIGN.md` section 2 (rejected rows are counted); resolved below.

## Decisions

Developer decisions, 2026-11-10:

1. **File-level problems stop, row-level problems are rejected.** Missing file, unsupported type, missing required column, or no data rows: exit 1. Blank `lead_id`, blank `agency`, unknown stage or bad date on a row: the row is skipped, counted by reason, and listed by row number; the run continues with exit 0.
2. **Duplicates: the furthest stage wins.** Ties keep the earliest row. Every duplicate is counted. Duplicates that disagree on `agency` or `captured_on` produce a warning naming the `lead_id` and both row numbers.
3. **A `check` command ships with F1**, so F1 is runnable and demoable before the report exists. `report` (F2/F3) will reuse the same loader and summary.

Design decisions:

4. **Only four columns are read:** `lead_id`, `agency`, `captured_on`, `stage`. Name, email, phone and company are never loaded, so the tool never holds personal data. Extra columns are ignored. Header matching ignores case and surrounding whitespace.
5. **Synthetic data is always clean.** Bad-row cases live in small hand-written fixtures with hand-checked expected counts. A `--messy` demo option is deferred.
6. **Dates in synthetic data use a fixed range** (2026-10-05 to 2026-11-15, ISO weeks 2026-W41 to W46), never today's date, so output depends only on the seed.
7. **Standard library plus openpyxl only.** `argparse`, `csv`, `random.Random(seed)`, `dataclasses`, `os.replace`.
8. **The safe-write helper stays in `synth.py`** until F3 needs it too; then it moves to its own module.

## Data and Migration

None. No database; nothing is stored between runs.

## Modules

| File | Purpose | Public interface |
|---|---|---|
| `src/lead_funnel/stages.py` | The four stages in order and name normalizing | `STAGES = ("Lead", "Contacted", "Intro session", "Onboarded")`; `parse_stage(text) -> int or None` (index into `STAGES`; case-insensitive, internal whitespace collapsed) |
| `src/lead_funnel/synth.py` | F4 generator and safe write | `generate_leads(rows, seed) -> list[dict]`; `write_csv(path, leads, force) -> None` |
| `src/lead_funnel/load.py` | F1 loader | `load_leads(path) -> LoadResult`; `LoadError(Exception)` for file-level problems |
| `src/lead_funnel/cli.py` | Commands, output, exit codes | `main(argv=None) -> int` |

`Lead` is a frozen dataclass: `lead_id: str, agency: str, captured_on: date, stage: int, row: int`.
`LoadResult` is a dataclass: `leads: list[Lead]` (first-appearance order), `rows_read: int`, `rejected: list[tuple[int, str, str]]` (row, lead_id or "", reason), `duplicates: int`, `warnings: list[str]`.

## F4 Synthetic Generator

- `generate_leads(rows, seed)` uses one `random.Random(seed)`; no global random state, no clock.
- Columns in order: `lead_id, name, email, phone, company, agency, event, captured_on, stage`.
- `lead_id`: `L00001` upward (five digits; 100,000 fits as `L100000`).
- Six fictional agencies (for example "Northwind Events", "Bluepeak Media") and four fictional roadshows; no real company names.
- Names from short fictional first and last name lists. Email `first.last<n>@example.com`; phone `+00 900 000 NNNN` (country code `+00` does not exist).
- Company from a short fictional list.
- `captured_on` uniform over 2026-10-05 to 2026-11-15 inclusive, written as `YYYY-MM-DD`.
- Each agency gets its own step probabilities drawn from the seed (each between 0.3 and 0.8), so agencies convert differently. A lead advances stage by stage while a draw is below that step's probability.
- `write_csv`: UTF-8 without BOM, `\n` line endings, header row first. Writes to a temporary file in the target folder, then `os.replace` onto the final path; creates the parent folder if missing. If the target exists and `force` is false, raise `FileExistsError`; the CLI prints `Error: <path> already exists. Use --force to replace it.` and exits 1.
- Committed sample: `data/sample/leads-seed42.csv`, 500 rows, seed 42.

## F1 Loader

- Extension decides the reader: `.csv` uses `csv.DictReader` with `encoding="utf-8-sig"` (accepts an Excel BOM); `.xlsx` uses `openpyxl.load_workbook(read_only=True, data_only=True)`, first sheet only. Any other extension: `LoadError("only .csv and .xlsx files are supported")`.
- A CSV field over the `csv` module's default size limit raises `csv.Error`, converted to `LoadError` naming the file.
- Missing file: `LoadError` naming the path. Missing required column: `LoadError` naming every missing column. Header present but no data rows: `LoadError("no leads found in <file>")`. Fully blank rows are skipped without counting.
- Row numbers are 1-based with the header as row 1, matching Excel.
- Row rules, applied in this order (first failure wins):

| Check | Rejection reason |
|---|---|
| `lead_id` blank after trimming | `blank lead_id` |
| `agency` blank after trimming | `blank agency` |
| `stage` not one of the four after normalizing | `unknown stage "<value cut to 20 chars>"` |
| `captured_on` is not a date cell and not `YYYY-MM-DD` text | `bad date` |

- `agency` is trimmed; case is kept. A `datetime` cell becomes its date.
- Duplicates: keyed by trimmed `lead_id`. The kept lead is the one with the highest stage; on a tie, the earliest row. `duplicates` counts every extra row. If the rows disagree on `agency` or `captured_on`: warning `<lead_id>: rows <a> and <b> disagree on <field>; kept row <n>`.
- No message ever contains a cell value other than `lead_id` and the cut unknown-stage text.

## Interface (CLI)

```text
lead-funnel [--debug] synth --out FILE [--rows N] [--seed S] [--force]
lead-funnel [--debug] check FILE
```

- `--rows`: integer 1 to 100,000, default 500. `--seed`: integer, default 42. Out-of-range values are argparse usage errors (exit 2).
- Every flag has help text; each subcommand's help shows one example (`DESIGN.md` section 1).
- `synth` stdout: `Wrote 500 leads to data/sample/leads-seed42.csv (seed 42)`.
- `check` stdout:

```text
Read 1,240 rows from leads.csv
Rejected 3 rows (unknown stage: 2, bad date: 1)
Removed 5 duplicate lead ids
Kept 1,232 leads across 6 agencies
```

  The "Rejected" and "Removed" lines are always printed (with 0). Rejected rows and warnings go to stderr, one per line (`Row 7 (L00007): unknown stage "Won"`), at most 20 lines, then `...and N more`.
- Exit codes: 0 success (rejected rows allowed); 1 `LoadError` or `FileExistsError`, printed as `Error: <message>` on stderr; 2 usage errors (argparse); 3 any other exception, printed as `Error: something went wrong. Run with --debug for details.`; with `--debug` the traceback is printed to stderr.
- `pyproject.toml`: `[project.scripts] lead-funnel = "lead_funnel.cli:main"`.

## Security and Privacy

- Personal columns are never read (Decision 4); messages print only row numbers, `lead_id`s and cut stage text.
- `.xlsm` and other types are refused; openpyxl `data_only=True` never evaluates formulas.
- Generated data is fake by construction; `tests/test_privacy.py` fails on any email under `data/` or `tests/fixtures/` not on `example.com` or `example.org`.
- No secrets involved.

## Testing

Test-first, one QAD row at a time. Expected numbers in each fixture test are hand-counted and written in the test.

| QAD row | Test |
|---|---|
| F4-1 | 500 rows, nine columns in order |
| F4-2, F4-3 | `--rows 0`, `-5`, `100001` exit 2 (`tests/test_cli.py`) |
| F4-4, F4-5 | same seed same bytes; different seed different bytes |
| F4-6 | generated seed 42 equals committed `data/sample/leads-seed42.csv` byte for byte (runs on Windows locally and Linux in CI) |
| F4-7, F4-8 | every email ends `@example.com`; every phone starts `+00 ` |
| F4-9 | `tests/test_privacy.py` scan |
| F1-1 | valid CSV and `.xlsx` (built in the test) load; BOM CSV loads |
| F1-2 | header-only file exits 1 "no leads found" |
| F1-3 | `.xlsm` refused; oversized field refused, exit 1 |
| F1-4 | `" intro  SESSION "` accepted as Intro session |
| F1-5 | missing `agency` column exits 1 naming it; unknown stage on row 7 rejected and counted, exit 0 |
| F1-6 | rejected row with an email in the file: message has row and lead_id, never the email |
| F1-7 | repeated `lead_id` counted once, 1 duplicate |
| F1-8 | duplicates with different stages keep the furthest; conflicting agency produces a warning |
| F1-9 | blank `lead_id` rows rejected individually, not merged |
| CLI | exit 3 path with and without `--debug`; stdout vs stderr split; 20-line cap; `--force` |

Files: `tests/test_synth.py`, `tests/test_load.py`, `tests/test_cli.py`, `tests/test_privacy.py`, `tests/fixtures/*.csv`.

## Documents Updated in the Same Change

- `docs/prd.md`: G-F1-2 reworded to Decision 1; F1 notes the `check` command and the four read columns.
- `docs/qad.md`: QAD-F1-5 and QAD-F1-8 expected results match Decisions 1 and 2.
- `docs/context.md` section 11: Decisions 1 to 4.
- `docs/index.md`: this spec and its plan registered.
- `.github/workflows/ci.yml`: the temporary `if:` lines removed.
- `README.md`: a short "Try it" section.

## Out of Scope

`report` command, weekly metrics, Excel output (F2, F3); `--messy`; `python -m lead_funnel`; date formats other than ISO and Excel date cells; agency name case folding.

## Risks and Open Questions

- Real exports may use `DD/MM/YYYY` dates; they will be rejected as `bad date` and counted. Revisit only if a real export needs it.
- Agencies differing only by case ("Northwind" vs "northwind") count as different agencies; the summary's agency count makes this visible.
