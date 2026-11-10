# Quality Assurance Document (QAD)

**Status:** Draft (follows the Draft gates in `docs/prd.md`)

## 1. Quality Areas (ISO/IEC 25010)

Functional Suitability, Performance Efficiency, Compatibility, Usability, Reliability, Security, Maintainability, Portability.

## 2. Test Rows

Every gate criterion in the PRD gets three rows: **happy** (it works), **sad** (bad input is handled) and **abuse** (an attack or forbidden action is blocked). Test files are planned paths.

| ID | Gate | Path | Scenario | Expected result | Test file | ISO area |
|---|---|---|---|---|---|---|
| QAD-F1-1 | G-F1-1 | happy | Valid CSV and valid `.xlsx` with all columns | Both load; summary shows rows read, 0 rejected | `tests/test_load.py` | Functional Suitability |
| QAD-F1-2 | G-F1-1 | sad | Empty file (header only) | Exit 1, "no leads found in <file>" | `tests/test_load.py` | Reliability |
| QAD-F1-3 | G-F1-1 | abuse | `.xlsm` file or a CSV with a 50 MB single field | Refused with exit 1; no macro run, no hang | `tests/test_load.py` | Security |
| QAD-F1-4 | G-F1-2 | happy | Stage names with mixed case and spaces (" contacted ") | Normalized and accepted | `tests/test_load.py` | Functional Suitability |
| QAD-F1-5 | G-F1-2 | sad | Missing `agency` column; unknown stage "Won" on row 7 | Missing column: exit 1 naming it. Unknown stage on row 7: row rejected and listed, run continues with exit 0 | `tests/test_load.py` | Usability |
| QAD-F1-6 | G-F1-2 | abuse | Error on a row containing a lead's email | Message names row and column, never prints the email | `tests/test_load.py` | Security |
| QAD-F1-7 | G-F1-3 | happy | Same `lead_id` twice | Counted once; "1 duplicate" reported | `tests/test_load.py` | Functional Suitability |
| QAD-F1-8 | G-F1-3 | sad | Duplicate ids with different stages | Furthest stage kept; conflicting agency or date produces a warning | `tests/test_load.py` | Reliability |
| QAD-F1-9 | G-F1-3 | abuse | Blank `lead_id` values | Rejected and counted, not merged into one lead | `tests/test_load.py` | Reliability |
| QAD-F2-1 | G-F2-1 | happy | Fixture with known counts for 3 agencies | Counts and rates equal the hand-checked table | `tests/test_metrics.py` | Functional Suitability |
| QAD-F2-2 | G-F2-1 | sad | Agency with only Lead-stage rows | Later stages 0; conversions computed correctly | `tests/test_metrics.py` | Functional Suitability |
| QAD-F2-3 | G-F2-1 | abuse | 100,000 synthetic rows | Finishes under 10 s; totals equal row count | `tests/test_metrics.py` | Performance Efficiency |
| QAD-F2-4 | G-F2-2 | happy | `--week 2026-W46` | Only 2026-11-09 to 2026-11-15 counted | `tests/test_metrics.py` | Functional Suitability |
| QAD-F2-5 | G-F2-2 | sad | Leads on Sunday 2026-11-15 and Monday 2026-11-16 | Sunday in W46, Monday in W47 | `tests/test_metrics.py` | Reliability |
| QAD-F2-6 | G-F2-2 | abuse | `--week 2026-W60` or `--week lastweek` | Exit 2 with usage message | `tests/test_cli.py` | Usability |
| QAD-F2-7 | G-F2-3 | happy | Agency with 0 Contacted leads | Contacted→Intro shows "n/a" | `tests/test_metrics.py` | Reliability |
| QAD-F2-8 | G-F2-3 | sad | Week with no leads at all | Report written with zeros; stdout `No leads in 2026-W46; wrote an empty report`; exit 0 | `tests/test_cli.py` | Usability |
| QAD-F2-9 | G-F2-3 | abuse | Every agency empty after duplicate removal | No ZeroDivisionError; all rates "n/a" | `tests/test_metrics.py` | Reliability |
| QAD-F3-1 | G-F3-1 | happy | Report for the sample week | Table and chart present; opens in openpyxl (Excel checked by hand) | `tests/test_report.py` | Functional Suitability |
| QAD-F3-2 | G-F3-1 | sad | Agency name of 200 characters | Written in full; column width capped | `tests/test_report.py` | Usability |
| QAD-F3-3 | G-F3-1 | abuse | Run interrupted mid-write | No partial file under the final name | `tests/test_report.py` | Reliability |
| QAD-F3-4 | G-F3-2 | happy | Agency named "Acme Events" | Written as text | `tests/test_report.py` | Functional Suitability |
| QAD-F3-5 | G-F3-2 | sad | Agency named "-Minus Media" | Written as text, not a formula | `tests/test_report.py` | Security |
| QAD-F3-6 | G-F3-2 | abuse | Agency named `=HYPERLINK("http://x","click")` | Cell holds plain text; no formula in the file | `tests/test_report.py` | Security |
| QAD-F3-7 | G-F3-3 | happy | `--out reports/` that does not exist | Folder created; report written there | `tests/test_cli.py` | Functional Suitability |
| QAD-F3-8 | G-F3-3 | sad | Report already exists, no `--force` | Exit 1 "already exists, use --force" | `tests/test_cli.py` | Reliability |
| QAD-F3-9 | G-F3-3 | abuse | `--out` that is an existing file; input text in the file name | File name built by the tool (`funnel-<week>.xlsx`), never from input; `--out` that is a file exits 1 | `tests/test_cli.py` | Security |
| QAD-F4-1 | G-F4-1 | happy | `synth --rows 500 --seed 42` | CSV with 500 rows and all columns | `tests/test_synth.py` | Functional Suitability |
| QAD-F4-2 | G-F4-1 | sad | `--rows 0` or `--rows -5` | Exit 2 with usage message | `tests/test_cli.py` | Usability |
| QAD-F4-3 | G-F4-1 | abuse | `--rows 100000000` | Refused above a documented maximum | `tests/test_cli.py` | Performance Efficiency |
| QAD-F4-4 | G-F4-2 | happy | Same seed twice | Byte-identical files | `tests/test_synth.py` | Reliability |
| QAD-F4-5 | G-F4-2 | sad | Different seeds | Different files | `tests/test_synth.py` | Functional Suitability |
| QAD-F4-6 | G-F4-2 | abuse | Committed sample compared byte for byte on the developer machine | Same bytes (fixed line endings and encoding) | `tests/test_synth.py` | Portability |
| QAD-F4-7 | G-F4-3 | happy | Generated emails | All end in `example.com` / `example.org` | `tests/test_synth.py` | Security |
| QAD-F4-8 | G-F4-3 | sad | Generated phones | Match a reserved fake pattern | `tests/test_synth.py` | Security |
| QAD-F4-9 | G-F4-3 | abuse | Committed files under `data/` | A test scans them and fails on any non-example email domain | `tests/test_privacy.py` | Security |

## 3. Release Criteria

- Every gate's happy, sad and abuse rows pass.
- No reviewer returns BLOCKED on the final code.
- No secrets or real personal data in the change.
