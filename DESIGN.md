# CLI Design Conventions

**Status:** Draft

> This project is a command-line tool, so the design system is its commands, output, error messages and the Excel report layout. `cli-ux-guardian` checks changes against this file. The code must match it; record changes in `docs/context.md` section 11.

## 1. Commands and Flags

| Command | Purpose | Example |
|---|---|---|
| `lead-funnel report <file>` | Weekly per-agency funnel report | `lead-funnel report data/sample/leads-seed42.csv --week 2026-W46 --out reports/` |
| `lead-funnel synth` | Synthetic lead file | `lead-funnel synth --rows 500 --seed 42 --out data/sample/leads-seed42.csv` |

- Built with `argparse` (standard library).
- Long flags in kebab-case (`--week`, `--out`, `--force`, `--debug`); short flags only for `-h`.
- Positional argument only for the input file.
- `--week` uses ISO format `YYYY-Www`; if omitted, it defaults to the last complete ISO week and the summary says which week was used.
- `--help` on every command shows a one-line purpose, every flag, and one example.

## 2. Output

- Results and the summary go to **stdout**; warnings and errors go to **stderr**.
- Plain text, readable without color; no emojis, no spinners.
- Summary format, one fact per line:

```text
Read 1,240 rows from leads.csv
Rejected 3 rows (unknown stage: 2, missing date: 1)
Removed 5 duplicate lead ids
Week 2026-W46: 312 leads across 6 agencies
Wrote reports/funnel-2026-W46.xlsx
```

- Numbers use thousands separators; rates show one decimal (`42.5%`); an empty step shows `n/a`.

## 3. Errors and Exit Codes

| Exit code | Meaning | Example message |
|---|---|---|
| 0 | Success (including "no leads in that week") | `No leads in 2026-W46; wrote an empty report` |
| 1 | Expected problem with input or files | `Error: leads.csv is missing column "agency". Add it or check the export.` |
| 2 | Usage error (bad flag or value) | `Error: --week must look like 2026-W46` |
| 3 | Unexpected error | `Error: something went wrong reading leads.xlsx. Run with --debug for details.` |

- Format: `Error: <what is wrong, naming the file, row or flag>. <how to fix it>.`
- Row numbers are 1-based and count the header as row 1, matching Excel.
- Never print lead names, emails or phones; refer to rows by number and `lead_id`.
- No stack trace unless `--debug`.

## 4. Excel Report Layout

- File name: `funnel-<YYYY-Www>.xlsx`.
- Sheet `Funnel`: title row with the week and date range; table with one row per agency, sorted by lead count descending, plus a Total row.
- Columns: Agency, Lead, Contacted, Intro session, Onboarded, Lead→Contacted, Contacted→Intro, Intro→Onboarded, Overall.
- Counts use number format `#,##0`; rates use `0.0%`; `n/a` cells are text, right-aligned.
- Bold header row, frozen panes under the header, column widths fitted (capped at 40 characters).
- A clustered bar chart of stage counts per agency is placed next to the table.
- Sheet `About`: input file name, rows read, rejected, duplicates, week, generated time, tool version. No personal data on any sheet.

## 5. Accessibility

- Output never relies on color alone.
- The report uses real header rows and plain-language labels so screen readers in Excel read it correctly.

## 6. Quality Gate

A CLI or report change is done when:
- [ ] commands, flags and messages follow sections 1 to 3;
- [ ] `--help` shows an example;
- [ ] exit codes are tested for success, input error and usage error;
- [ ] the report follows section 4 and opens in Excel;
- [ ] copy follows `docs/voice.md`.
