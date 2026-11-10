# Product Requirements Document (PRD)

**Status:** Draft (F1 and F4 gates confirmed 2026-11-10; F2 and F3 to confirm in their brainstorm)

## 1. Problem

Event and agency marketing teams must report weekly how each agency's roadshow leads move through the funnel. Building that report by hand from a lead export is slow and error-prone (see `IDEA.md`).

## 2. Users and Roles

| Role | Can do | Cannot do |
|---|---|---|
| Report owner (runs the CLI) | Generate synthetic data, run reports on any lead file they have | See individual lead details in the report |
| Report reader (opens the `.xlsx`) | Read per-agency totals and conversion | See lead names, emails or phones |

## 3. Features

Each feature has an ID (F1, F2...). Each gate criterion has an ID (G-F1-1...) and must be a yes-or-no check. Input columns: `lead_id`, `name`, `email`, `phone`, `company`, `agency`, `event`, `captured_on` (date), `stage`.

### F1 Load and validate leads

**Goal:** Read a CSV or `.xlsx` lead export and keep only clean, unique rows.

**Gate criteria:**
- G-F1-1: A valid CSV or `.xlsx` file with the required columns loads, and the CLI prints rows read, rejected and duplicated.
- G-F1-2: A missing required column or an empty file stops the run with exit code 1 naming the column or file; a row with a blank id, blank agency, unknown stage or bad date is skipped, counted and listed by row number, and the run continues.
- G-F1-3: Rows with a repeated `lead_id` are counted once, and the duplicate count is reported.

**Command:** `lead-funnel check <file>`. Only `lead_id`, `agency`, `captured_on` and `stage` are read; other columns are ignored.

**Use cases:**
- UC-F1-1: The report owner runs the tool on last week's export and sees how many rows were rejected and why.

**Out of scope:** guessing misspelled stage names; `.xls` and `.xlsm` files.

### F2 Weekly per-agency funnel metrics

**Goal:** For one ISO week, count per agency how many leads reached each stage and compute conversion rates.

**Gate criteria:**
- G-F2-1: Reached-stage counts and step and overall conversion rates match a hand-checked fixture.
- G-F2-2: Only leads whose `captured_on` falls in the given ISO week (Monday to Sunday) are counted.
- G-F2-3: An agency with zero leads at a step shows "n/a" for that conversion, never an error.

**Use cases:**
- UC-F2-1: The report owner gets week 46 numbers for every agency.

**Out of scope:** week-over-week trends (Later).

### F3 Excel report

**Goal:** Write the metrics to an `.xlsx` that opens cleanly in Excel.

**Gate criteria:**
- G-F3-1: The report has a per-agency funnel table (counts and conversion percentages) and a funnel chart, and opens in Excel without repair warnings.
- G-F3-2: Text from the input that starts with `=`, `+`, `-` or `@` is written as plain text, never as a formula.
- G-F3-3: An existing report is not overwritten without `--force`, and nothing is written outside `--out`.

**Use cases:**
- UC-F3-1: The report owner shares `funnel-2026-W46.xlsx` with the agency team lead.

**Out of scope:** Google Sheets export (Later); emailing the report (Never).

### F4 Synthetic lead generator

**Goal:** Produce realistic but fake lead files for development, tests and demos.

**Gate criteria:**
- G-F4-1: `lead-funnel synth --rows N --seed S` writes a CSV with the required columns and N rows.
- G-F4-2: The same seed produces a byte-identical file.
- G-F4-3: Generated personal fields are clearly fake (`example.com` emails, reserved phone patterns).

**Use cases:**
- UC-F4-1: The developer creates `data/sample/leads-seed42.csv` for tests and the demo.

**Out of scope:** imitating a real company's data.

## 4. Non-functional Requirements

- NFR-1 Correctness: no row is dropped without being counted and reported.
- NFR-2 Performance: 100,000 leads produce a report in under 10 seconds on the development laptop.
- NFR-3 Privacy: personal data never appears in reports, logs or error messages; only synthetic data is committed.
- NFR-4 Usability: CLI follows `DESIGN.md`; exit codes 0, 1, 2, 3.
- NFR-5 Portability: works on Windows and Linux with Python 3.12.
