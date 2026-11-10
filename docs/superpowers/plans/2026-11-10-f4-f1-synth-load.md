# Synthetic Leads and Lead Loading Implementation Plan (F4 + F1)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `lead-funnel synth` writes a reproducible fake lead CSV and `lead-funnel check` loads and validates a CSV or `.xlsx` lead export with a summary.

**Architecture:** Four small modules under `src/lead_funnel/`: `stages.py` (stage order and parsing), `synth.py` (generator and safe CSV write), `load.py` (reader, row rules, duplicates into a `LoadResult`), and `cli.py` (argparse, output, exit codes). `cli.main(argv) -> int` is the only entry point; tests call it directly.

**Tech Stack:** Python >= 3.12, uv, openpyxl (runtime), pytest and ruff (dev). Standard library for everything else.

**Spec:** `docs/superpowers/specs/2026-11-10-f4-f1-synth-load-design.md` (approved 2026-11-10)

**Change record:** none (first build of Draft PRD features)

## Global Constraints

- Work in a git worktree on branch `feature/f4-f1-synth-load`, cut from `feature/agent-workflow-setup`.
- Runtime dependency: `openpyxl` only. Dev: `pytest`, `ruff`. Versions come from `uv add`, never typed by hand. Installing needs the developer's OK (asked once at Task 1).
- Only `lead_id`, `agency`, `captured_on`, `stage` are ever read from input; no other cell value reaches memory beyond the reader row.
- Messages never contain a cell value except `lead_id` and unknown-stage text cut to 20 characters.
- Exit codes: 0 success, 1 file-level error, 2 usage error, 3 unexpected error.
- Synthetic CSV: UTF-8 without BOM, `\n` line endings, fixed dates 2026-10-05 to 2026-11-15, `random.Random(seed)` only.
- Comments are one sentence, no emojis. Follow `CLAUDE.md`, `AGENTS.md`, `docs/build-guide.md` golden paths and `DESIGN.md`.
- Fast checks before every commit: `uv run ruff check .` and `uv run pytest`.

## Review Focus

Inputs the spec implies but its QAD rows do not exercise, most likely first. Each has a test in the owning task.

1. **CSV saved by Windows Excel as ANSI (cp1252), not UTF-8:** exit 1 with `Error: <file> is not UTF-8. Save it as "CSV UTF-8" and try again.` (Task 4, `test_non_utf8_csv_is_load_error`).
2. **Report file open in Excel on Windows (PermissionError on read or write):** exit 1 with `Error: cannot open <file>. Close it in other programs and try again.`, not exit 3 (Task 4 `test_permission_error_is_load_error`, Task 7 `test_synth_permission_error_exits_1`).
3. **`.xlsx` with numeric `lead_id` cells (1001 or 1001.0):** read as `"1001"`, and 1001 and "1001" are the same lead (Task 6, `test_numeric_lead_id_cells`).
4. **CSV using `;` as delimiter (regional Excel):** exit 1 naming the missing columns, not a crash (Task 4, `test_semicolon_csv_reports_missing_columns`).
5. **`.xlsx` with a title row above the header:** exit 1 naming the missing columns (Task 6, `test_xlsx_title_row_reports_missing_columns`).

---

## File Structure

- Create `pyproject.toml`, `uv.lock`, `.python-version` (uv).
- Create `src/lead_funnel/__init__.py` (empty), `stages.py`, `synth.py`, `load.py`, `cli.py`.
- Create `tests/test_stages.py`, `tests/test_synth.py`, `tests/test_load.py`, `tests/test_cli.py`, `tests/test_privacy.py`, `tests/fixtures/messy.csv`.
- Create `data/sample/leads-seed42.csv`.
- Modify `.github/workflows/ci.yml`, `docs/prd.md`, `docs/qad.md`, `docs/context.md`, `docs/index.md`, `README.md`.

---

### Task 1: Project scaffold and stages

**Files:**
- Create: `pyproject.toml`, `uv.lock`, `.python-version`, `src/lead_funnel/__init__.py`, `src/lead_funnel/stages.py`
- Modify: `.github/workflows/ci.yml`
- Test: `tests/test_stages.py`

**Interfaces:**
- Produces: `STAGES: tuple[str, ...] = ("Lead", "Contacted", "Intro session", "Onboarded")`; `parse_stage(text: object) -> int | None`.

- [ ] **Step 1: Ask the developer to approve installing openpyxl, pytest and ruff.** Stop if refused.
- [ ] **Step 2: Scaffold.** Run `uv init --package --name lead-funnel --python 3.12 --vcs none --no-readme .`, then `uv add openpyxl` and `uv add --dev pytest ruff`. In `pyproject.toml` set `[project.scripts] lead-funnel = "lead_funnel.cli:main"`, `description = "Turns event leads into a weekly per-agency conversion report in Excel"`, and add `[tool.pytest.ini_options] testpaths = ["tests"]`. Empty `src/lead_funnel/__init__.py` (remove uv's hello `main`).
- [ ] **Step 3: Write the failing test** `tests/test_stages.py`:

```python
from lead_funnel.stages import STAGES, parse_stage

def test_stage_order():
    assert STAGES == ("Lead", "Contacted", "Intro session", "Onboarded")

def test_parse_stage_normalizes_case_and_spaces():
    assert parse_stage(" intro  SESSION ") == 2
    assert parse_stage("lead") == 0
    assert parse_stage("Onboarded") == 3

def test_parse_stage_unknown():
    assert parse_stage("Won") is None
    assert parse_stage("") is None
    assert parse_stage(None) is None
```

- [ ] **Step 4: Run** `uv run pytest tests/test_stages.py -v`. Expected: FAIL, module `lead_funnel.stages` not found.
- [ ] **Step 5: Implement** `stages.py`: `parse_stage` lowercases `" ".join(str(text).split())` and looks it up in a dict built from `STAGES`; `None` input returns `None`.
- [ ] **Step 6: Run** `uv run pytest -v` and `uv run ruff check .`. Expected: 3 passed, ruff clean.
- [ ] **Step 7: CI.** In `.github/workflows/ci.yml` delete the `shortcut:` comment and the three `if: hashFiles(...)` lines so the steps always run.
- [ ] **Step 8: Commit** `feat(stages): project scaffold and funnel stage parsing`.

---

### Task 2: Synthetic lead generator

**Files:**
- Create: `src/lead_funnel/synth.py`
- Test: `tests/test_synth.py`

**Interfaces:**
- Consumes: `STAGES`.
- Produces: `COLUMNS: tuple[str, ...] = ("lead_id", "name", "email", "phone", "company", "agency", "event", "captured_on", "stage")`; `generate_leads(rows: int, seed: int) -> list[dict[str, str]]` (all values strings, keys in `COLUMNS` order).

- [ ] **Step 1: Write the failing tests:**

```python
from lead_funnel.stages import STAGES
from lead_funnel.synth import COLUMNS, generate_leads

def test_generates_rows_with_columns_in_order():  # QAD-F4-1
    leads = generate_leads(500, 42)
    assert len(leads) == 500
    assert all(tuple(lead) == COLUMNS for lead in leads)
    assert leads[0]["lead_id"] == "L00001" and leads[-1]["lead_id"] == "L00500"

def test_same_seed_same_data():  # QAD-F4-4
    assert generate_leads(200, 7) == generate_leads(200, 7)

def test_different_seed_different_data():  # QAD-F4-5
    assert generate_leads(200, 7) != generate_leads(200, 8)

def test_values_are_fake_and_in_range():  # QAD-F4-7, F4-8
    leads = generate_leads(500, 42)
    assert all(l["email"].endswith("@example.com") for l in leads)
    assert all(l["phone"].startswith("+00 900 000 ") for l in leads)
    assert all("2026-10-05" <= l["captured_on"] <= "2026-11-15" for l in leads)
    assert {l["stage"] for l in leads} <= set(STAGES)
    assert len({l["agency"] for l in leads}) == 6
    assert len({l["event"] for l in leads}) == 4

def test_agencies_convert_differently():
    leads = generate_leads(5000, 42)
    onboarded = {}
    for l in leads:
        onboarded.setdefault(l["agency"], []).append(l["stage"] == "Onboarded")
    rates = [sum(v) / len(v) for v in onboarded.values()]
    assert max(rates) - min(rates) > 0.05
```

- [ ] **Step 2: Run** `uv run pytest tests/test_synth.py -v`. Expected: FAIL, import error.
- [ ] **Step 3: Implement** `generate_leads` in `synth.py` with one `rng = random.Random(seed)`. Fictional lists as module constants: 6 agencies (for example "Northwind Events", "Bluepeak Media", "Harborlight Agency", "Kestrel Promotions", "Saltwater Creative", "Tamarind Marketing"), 4 events (for example "Manila Roadshow", "Cebu Roadshow", "Davao Workshop", "Clark Roadshow"), about 10 first names, 10 last names, 8 companies. Draw order (fixes byte output): first, for each agency in list order, three step probabilities `rng.uniform(0.3, 0.8)`; then per row i (1-based): first name, last name, company, agency, event, day offset `rng.randrange(42)` added to 2026-10-05, then advance stage while `stage < 3 and rng.random() < probs[agency][stage]`. Email `f"{first}.{last}{i}@example.com".lower()`, phone `f"+00 900 000 {i % 10000:04d}"`, lead_id `f"L{i:05d}"`.
- [ ] **Step 4: Run** `uv run pytest -v`. Expected: all pass.
- [ ] **Step 5: Commit** `feat(synth): seeded synthetic lead generator`.

---

### Task 3: Safe CSV write, committed sample, privacy scan

**Files:**
- Modify: `src/lead_funnel/synth.py`
- Create: `data/sample/leads-seed42.csv`, `tests/test_privacy.py`
- Test: `tests/test_synth.py`

**Interfaces:**
- Consumes: `generate_leads`, `COLUMNS`.
- Produces: `write_csv(path: pathlib.Path, leads: list[dict[str, str]], force: bool = False) -> None`; raises `FileExistsError` if `path` exists and not `force`.

- [ ] **Step 1: Write the failing tests** (add to `tests/test_synth.py`):

```python
from pathlib import Path
import pytest
from lead_funnel.synth import generate_leads, write_csv

SAMPLE = Path(__file__).parent.parent / "data" / "sample" / "leads-seed42.csv"

def test_write_csv_bytes(tmp_path):
    out = tmp_path / "sub" / "leads.csv"
    write_csv(out, generate_leads(3, 1))
    data = out.read_bytes()
    assert not data.startswith(b"\xef\xbb\xbf")
    assert b"\r\n" not in data
    assert data.split(b"\n")[0] == b"lead_id,name,email,phone,company,agency,event,captured_on,stage"
    assert data.count(b"\n") == 4

def test_write_csv_refuses_overwrite(tmp_path):
    out = tmp_path / "leads.csv"
    out.write_text("keep")
    with pytest.raises(FileExistsError):
        write_csv(out, generate_leads(3, 1))
    assert out.read_text() == "keep"
    write_csv(out, generate_leads(3, 1), force=True)
    assert out.read_text().startswith("lead_id,")

def test_write_csv_leaves_no_temp_files(tmp_path):
    write_csv(tmp_path / "leads.csv", generate_leads(3, 1))
    assert [p.name for p in tmp_path.iterdir()] == ["leads.csv"]

def test_committed_sample_matches_seed_42(tmp_path):  # QAD-F4-6
    out = tmp_path / "leads.csv"
    write_csv(out, generate_leads(500, 42))
    assert out.read_bytes() == SAMPLE.read_bytes()
```

`tests/test_privacy.py` (QAD-F4-9):

```python
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
EMAIL = re.compile(r"[\w.+-]+@([\w-]+\.)+[\w-]+")

def test_committed_data_uses_example_domains_only():
    files = [p for d in ("data", "tests/fixtures") for p in (ROOT / d).rglob("*") if p.is_file()]
    assert files
    for path in files:
        for match in EMAIL.finditer(path.read_text(encoding="utf-8")):
            assert match.group().lower().endswith(("@example.com", "@example.org")), path.name
```

- [ ] **Step 2: Run** `uv run pytest tests/test_synth.py -v`. Expected: FAIL, `write_csv` not defined.
- [ ] **Step 3: Implement** `write_csv`: if `path.exists()` and not `force`, raise `FileExistsError(path)`; `path.parent.mkdir(parents=True, exist_ok=True)`; `tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False)`; `csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")`; header and rows; close; `os.replace(tmp, path)`; on any exception remove the temp file and re-raise.
- [ ] **Step 4: Generate the sample** with `uv run python -c "from pathlib import Path; from lead_funnel.synth import generate_leads, write_csv; write_csv(Path('data/sample/leads-seed42.csv'), generate_leads(500, 42))"`.
- [ ] **Step 5: Run** `uv run pytest -v`. Expected: all pass (the privacy test needs `tests/fixtures/` to exist; create `tests/fixtures/.gitkeep` if Task 4 has not yet).
- [ ] **Step 6: Commit** `feat(synth): safe CSV write and seed 42 sample`.

---

### Task 4: CSV loader with file-level errors and row rules

**Files:**
- Create: `src/lead_funnel/load.py`, `tests/fixtures/messy.csv`
- Test: `tests/test_load.py`

**Interfaces:**
- Consumes: `parse_stage`.
- Produces:
  - `REQUIRED = ("lead_id", "agency", "captured_on", "stage")`
  - `class LoadError(Exception)`; its `str()` is the user-facing message without the `Error: ` prefix.
  - `@dataclass(frozen=True) class Lead: lead_id: str; agency: str; captured_on: datetime.date; stage: int; row: int`
  - `@dataclass class LoadResult: leads: list[Lead]; rows_read: int; rejected: list[tuple[int, str, str]]; duplicates: int; warnings: list[str]`
  - `load_leads(path: pathlib.Path) -> LoadResult`

Exact `LoadError` messages:
- missing file: `<name> not found`
- unsupported extension: `only .csv and .xlsx files are supported`
- missing columns: `<name> is missing column(s): agency, stage` (in `REQUIRED` order)
- no data rows: `no leads found in <name>`
- non-UTF-8: `<name> is not UTF-8. Save it as "CSV UTF-8" and try again`
- PermissionError: `cannot open <name>. Close it in other programs and try again`
- `csv.Error` (oversized field): `<name> could not be read as CSV: a field is too large or malformed`

`<name>` is `path.name`. Rejection reasons: `blank lead_id`, `blank agency`, `unknown stage "<text[:20]>"`, `bad date`.

`tests/fixtures/messy.csv` (header is row 1), expected: rows_read 8, rejected 3 (row 4 unknown stage "Won", row 6 bad date, row 8 blank lead_id), duplicates 1 (L3 rows 3 and 7, Onboarded kept from row 7, no warning), 4 leads, 2 agencies:

```text
lead_id,name,email,phone,company,agency,event,captured_on,stage
L1,Ana Cruz,ana@example.com,+00 900 000 0001,Bluebird Bakery,Northwind Events,Manila Roadshow,2026-11-09,Lead
L3,Ben Reyes,ben@example.com,+00 900 000 0002,Corner Café,Northwind Events,Manila Roadshow,2026-11-10,Contacted
L4,Cara Lim,cara@example.com,+00 900 000 0003,Bluebird Bakery,Bluepeak Media,Cebu Roadshow,2026-11-11,Won
L5,Dan Uy,dan@example.com,+00 900 000 0004,Corner Café,Bluepeak Media,Cebu Roadshow,2026-11-12,Intro session
L6,Eva Tan,eva@example.com,+00 900 000 0005,Bluebird Bakery,Bluepeak Media,Cebu Roadshow,11/13/2026,Lead
L3,Ben Reyes,ben@example.com,+00 900 000 0002,Corner Café,Northwind Events,Manila Roadshow,2026-11-10,Onboarded
,Fay Go,fay@example.com,+00 900 000 0006,Corner Café,Bluepeak Media,Cebu Roadshow,2026-11-14,Lead
L9,Gil Sy,gil@example.com,+00 900 000 0007,Bluebird Bakery,Bluepeak Media,Cebu Roadshow,2026-11-15,  onboarded
```

- [ ] **Step 1: Write the failing tests** in `tests/test_load.py` (helper `write(tmp_path, text, name="leads.csv", encoding="utf-8")` writes a file and returns its path):
  - `test_messy_fixture_counts` (QAD-F1-1, F1-5, F1-9): load `tests/fixtures/messy.csv`; assert `rows_read == 8`, `rejected == [(4, "L4", 'unknown stage "Won"'), (6, "L6", "bad date"), (8, "", "blank lead_id")]`, `duplicates == 1`, `[l.lead_id for l in leads] == ["L1", "L3", "L5", "L9"]`, the `L3` lead has `stage == 3` and `row == 7`, `L9` has `stage == 3`, `warnings == []`.
  - `test_bom_csv_loads`: header written with `encoding="utf-8-sig"` loads one lead.
  - `test_header_case_and_spaces`: header ` Lead_ID , AGENCY,captured_on,Stage ` with one row loads.
  - `test_only_required_columns_needed`: a four-column file loads.
  - `test_missing_columns` (QAD-F1-5): header without `agency` and `stage` raises `LoadError` with message `leads.csv is missing column(s): agency, stage`.
  - `test_header_only_file` (QAD-F1-2): `LoadError("no leads found in leads.csv")`; a file whose data rows are all blank lines gives the same error.
  - `test_missing_file`: `LoadError("nope.csv not found")`.
  - `test_unsupported_extensions` (QAD-F1-3): `.xlsm`, `.xls`, `.txt` each raise `LoadError("only .csv and .xlsx files are supported")`.
  - `test_oversized_field` (QAD-F1-3): a row with a 200,000-character `agency` raises `LoadError` starting `leads.csv could not be read as CSV`.
  - `test_rejection_never_prints_personal_data` (QAD-F1-6): row with stage `Won` and email `secret.person@example.com`; assert `"secret.person"` appears in no rejection tuple.
  - `test_unknown_stage_text_is_cut`: stage of 50 `x` characters gives reason `'unknown stage "' + "x" * 20 + '"'`.
  - `test_blank_agency_rejected`: reason `blank agency`.
  - `test_non_utf8_csv_is_load_error` (Review Focus 1): file written with `encoding="cp1252"` containing `Café` raises `LoadError('leads.csv is not UTF-8. Save it as "CSV UTF-8" and try again')`.
  - `test_permission_error_is_load_error` (Review Focus 2): monkeypatch `builtins.open` (or `Path.open`, whichever the reader uses) to raise `PermissionError`; expect `LoadError("cannot open leads.csv. Close it in other programs and try again")`.
  - `test_semicolon_csv_reports_missing_columns` (Review Focus 4): `lead_id;agency;captured_on;stage` header raises `LoadError` whose message starts `leads.csv is missing column(s): lead_id`.
- [ ] **Step 2: Run** `uv run pytest tests/test_load.py -v`. Expected: FAIL, import error.
- [ ] **Step 3: Implement** in `load.py`: `load_leads` checks existence and extension, then gets `(header, rows)` from `_read_csv(path)` (a generator of value lists, header normalized with `.strip().lower()`), maps `REQUIRED` to column indexes, and applies the row rules in spec order. Row numbers start at 2. Fully blank rows are skipped uncounted. `captured_on` text must match `YYYY-MM-DD` via `date.fromisoformat` on a stripped 10-character string; `date` and `datetime` objects are accepted (datetimes become `.date()`). Duplicates are handled in Task 5; for now keep the first. Wrap reading so `UnicodeDecodeError`, `PermissionError` and `csv.Error` become the `LoadError` messages above.
- [ ] **Step 4: Run** `uv run pytest -v` and `uv run ruff check .`. Expected: all pass, except `test_messy_fixture_counts` until Task 5 (duplicate rule); mark it `@pytest.mark.xfail(strict=True, reason="duplicates in Task 5")` now.
- [ ] **Step 5: Commit** `feat(load): CSV loader with validation and row rejections`.

---

### Task 5: Duplicate lead ids

**Files:**
- Modify: `src/lead_funnel/load.py`
- Test: `tests/test_load.py`

**Interfaces:**
- Produces: `LoadResult.duplicates` and `LoadResult.warnings` filled. Warning format: `<lead_id>: rows <a> and <b> disagree on <field>; kept row <n>` where `<a>` is the earlier row, `<b>` the later, `<field>` is `agency` or `captured_on` (one warning per field), `<n>` the kept row.

- [ ] **Step 1: Write the failing tests:**
  - `test_repeated_id_counted_once` (QAD-F1-7): two identical `L1` rows give 1 lead, `duplicates == 1`, no warnings.
  - `test_furthest_stage_wins` (QAD-F1-8): `L1` Onboarded on row 2, Contacted on row 3; kept lead has `stage == 3`, `row == 2`.
  - `test_tie_keeps_earliest_row`: two `L1` rows at Lead with different `captured_on`; kept `row == 2`; warnings `["L1: rows 2 and 3 disagree on captured_on; kept row 2"]`.
  - `test_conflicting_agency_warns`: `L1` Lead at Northwind Events row 2, Onboarded at Bluepeak Media row 3; warnings `["L1: rows 2 and 3 disagree on agency; kept row 3"]`.
  - `test_three_copies`: three `L1` rows give `duplicates == 2`.
  - Remove the `xfail` from `test_messy_fixture_counts`.
- [ ] **Step 2: Run** `uv run pytest tests/test_load.py -v`. Expected: the new tests FAIL.
- [ ] **Step 3: Implement** with a dict `lead_id -> Lead` in first-appearance order; on a repeat, increment `duplicates`, compare `agency` and `captured_on` with the stored lead to add warnings, and replace the stored lead only if the new stage is higher (dict order keeps the first-appearance position).
- [ ] **Step 4: Run** `uv run pytest -v` and `uv run ruff check .`. Expected: all pass.
- [ ] **Step 5: Commit** `feat(load): duplicate lead ids keep the furthest stage`.

---

### Task 6: Excel (.xlsx) input

**Files:**
- Modify: `src/lead_funnel/load.py`
- Test: `tests/test_load.py`

**Interfaces:**
- Produces: `load_leads` accepts `.xlsx` through `_read_xlsx(path)` with the same `(header, rows)` shape as `_read_csv`.

- [ ] **Step 1: Write the failing tests** (build workbooks in the test with `openpyxl.Workbook()`, saved to `tmp_path`):
  - `test_xlsx_loads` (QAD-F1-1): header plus 3 rows, one `captured_on` as a `datetime(2026, 11, 9, 14, 30)` cell and one as text `"2026-11-10"`; 3 leads, the first with `captured_on == date(2026, 11, 9)`.
  - `test_xlsx_first_sheet_only`: a second sheet with more rows is ignored.
  - `test_xlsx_formula_cell_not_evaluated`: a `stage` cell containing `=1+1` (no cached value) is rejected as `unknown stage`, never computed.
  - `test_numeric_lead_id_cells` (Review Focus 3): `lead_id` cells `1001` (int) on row 2 and `1001.0` (float) on row 3; one lead with `lead_id == "1001"`, `duplicates == 1`.
  - `test_xlsx_title_row_reports_missing_columns` (Review Focus 5): row 1 `"Weekly leads"`, header on row 2; `LoadError` starting `leads.xlsx is missing column(s): lead_id`.
- [ ] **Step 2: Run** `uv run pytest tests/test_load.py -v`. Expected: the new tests FAIL.
- [ ] **Step 3: Implement** `_read_xlsx`: `openpyxl.load_workbook(path, read_only=True, data_only=True)`, `wb.worksheets[0].iter_rows(values_only=True)`; close the workbook when done. Normalize cells in the shared row code: `None` becomes `""`; a float with no fraction becomes its `int` string; other non-date values go through `str()`. Wrap `zipfile.BadZipFile` and `openpyxl` `InvalidFileException` as `LoadError("<name> could not be read as .xlsx")`, and `PermissionError` as in Task 4.
- [ ] **Step 4: Run** `uv run pytest -v` and `uv run ruff check .`. Expected: all pass.
- [ ] **Step 5: Commit** `feat(load): read .xlsx lead exports`.

---

### Task 7: CLI (`synth`, `check`) and documents

**Files:**
- Create: `src/lead_funnel/cli.py`
- Modify: `README.md`, `docs/prd.md`, `docs/qad.md`, `docs/context.md`, `docs/index.md`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: `generate_leads`, `write_csv`, `load_leads`, `LoadError`, `LoadResult`.
- Produces: `main(argv: list[str] | None = None) -> int`.

Exact copy (from the spec):
- synth stdout: `Wrote 500 leads to <out> (seed 42)`
- check stdout, four lines: `Read 1,240 rows from <name>`, `Rejected 3 rows (unknown stage: 2, bad date: 1)` (categories in rule order, only non-zero ones; `Rejected 0 rows` when none), `Removed 5 duplicate lead ids`, `Kept 1,232 leads across 6 agencies`
- stderr detail lines: `Row 7 (L00007): unknown stage "Won"`, or `Row 8: blank lead_id` when the id is blank; then warnings; at most 20 lines total, then `...and N more`
- errors: `Error: <LoadError message>`; `Error: <path> already exists. Use --force to replace it.`; `Error: cannot write <path>. Close it in other programs and try again.`; `Error: something went wrong. Run with --debug for details.`
- `--rows` out of range: argparse error `must be between 1 and 100000`

- [ ] **Step 1: Write the failing tests** in `tests/test_cli.py` (use `capsys`; call `main([...])`):
  - `test_synth_writes_file`: `main(["synth", "--out", str(p), "--rows", "5", "--seed", "3"]) == 0`; stdout `Wrote 5 leads to <p> (seed 3)\n`; file has 6 lines.
  - `test_synth_refuses_overwrite`: second run exits 1 with stderr `Error: <p> already exists. Use --force to replace it.`; with `--force` exits 0.
  - `test_synth_rows_limits` (QAD-F4-2, F4-3): `--rows 0`, `-5`, `100001`, `abc` each raise `SystemExit` with code 2 and stderr containing `must be between 1 and 100000` (or argparse's invalid value message for `abc`).
  - `test_synth_permission_error_exits_1` (Review Focus 2): monkeypatch `lead_funnel.cli.write_csv` to raise `PermissionError`; exit 1, stderr `Error: cannot write <p>. Close it in other programs and try again.`
  - `test_check_messy_fixture`: exit 0; stdout exactly `Read 8 rows from messy.csv\nRejected 3 rows (blank lead_id: 1, unknown stage: 1, bad date: 1)\nRemoved 1 duplicate lead ids\nKept 4 leads across 2 agencies\n`; stderr lines `Row 4 (L4): unknown stage "Won"`, `Row 6 (L6): bad date`, `Row 8: blank lead_id`.
  - `test_check_load_error_exits_1`: missing column file exits 1 with stderr `Error: leads.csv is missing column(s): agency\n`.
  - `test_check_caps_detail_lines`: 25 rejected rows give 20 detail lines plus `...and 5 more`.
  - `test_unexpected_error_exits_3`: monkeypatch `lead_funnel.cli.load_leads` to raise `RuntimeError("boom")`; exit 3, stderr `Error: something went wrong. Run with --debug for details.\n`, no `Traceback`; with `["--debug", "check", ...]` exit 3 and stderr contains `Traceback` and `boom`.
  - `test_help_shows_examples`: `synth --help` and `check --help` raise `SystemExit(0)` and stdout contains `Example:`.
  - `test_synth_then_check_sample`: `check data/sample/leads-seed42.csv` exits 0 with `Read 500 rows`, `Rejected 0 rows`, `Removed 0 duplicate lead ids`, `Kept 500 leads across 6 agencies`.
- [ ] **Step 2: Run** `uv run pytest tests/test_cli.py -v`. Expected: FAIL, `lead_funnel.cli` not found.
- [ ] **Step 3: Implement** `cli.py` with argparse subparsers (`prog="lead-funnel"`, global `--debug`, each subparser `epilog` with `Example: ...` from `DESIGN.md` and `RawDescriptionHelpFormatter`). A `rows_type` function raises `argparse.ArgumentTypeError("must be between 1 and 100000")`. `main` catches `LoadError` and `FileExistsError` (exit 1), `PermissionError` on write (exit 1), any other `Exception` (exit 3, traceback via `traceback.print_exc()` only with `--debug`). Note: the Rejected line orders categories by rule order (`blank lead_id`, `blank agency`, `unknown stage`, `bad date`), which is why the messy fixture line reads `blank lead_id: 1, unknown stage: 1, bad date: 1`; detail lines keep row order.
- [ ] **Step 4: Run** `uv run pytest -v` and `uv run ruff check .`. Expected: all pass. Then by hand: `uv run lead-funnel synth --out .tmp/try.csv --rows 50` and `uv run lead-funnel check tests/fixtures/messy.csv`; outputs match the spec.
- [ ] **Step 5: Documents.**
  - `docs/prd.md` F1: G-F1-2 becomes "A missing required column or an empty file stops the run with exit code 1 naming the column or file; a row with a blank id, blank agency, unknown stage or bad date is skipped, counted and listed by row number, and the run continues." Add under F1: "Command: `lead-funnel check <file>`. Only `lead_id`, `agency`, `captured_on` and `stage` are read; other columns are ignored."
  - `docs/qad.md`: QAD-F1-5 expected becomes "Missing column: exit 1 naming it. Unknown stage on row 7: row rejected and listed, run continues with exit 0"; QAD-F1-8 expected becomes "Furthest stage kept; conflicting agency or date produces a warning".
  - `docs/context.md` section 11: add the four developer and design decisions from the spec (dated 2026-11-10). Section 2: update Current State.
  - `docs/index.md`: plan row status Executed, spec row Executed; traceability rows F1 and F4 status "Built, in review".
  - `README.md`: add a "Try it" section with `uv sync`, the `synth` command and the `check` command.
- [ ] **Step 6: Commit** `feat(cli): synth and check commands; docs for F1 and F4`.

---

## Finish

- [ ] Run `uv run ruff check .` and `uv run pytest -v`; paste the result.
- [ ] Run the review pipeline: `claude --agent review-orchestrator` against `feature/agent-workflow-setup`. Expected routes: security, privacy, data-quality, cli-ux, restraint, design-qa.
- [ ] Hand back to the developer for `/agent-workflow:save`.
