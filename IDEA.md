# Idea Baseline

**Status:** Draft

> The self-contained idea behind the project. Change it only when the idea itself changes.

**One-line pitch:** A command-line tool that turns an export of event leads into a weekly per-agency conversion report in Excel, for event and agency marketing teams.

**Problem:** Teams that collect leads at roadshows must report, every week, how each agency's leads move through the funnel. Doing it by hand in a spreadsheet is slow and easy to get wrong.

**Insight (why this, why now):** The report is the same calculation every week; one tested script removes the manual work and the errors. It also shows the Excel and lead-funnel skills that agency project roles ask for.

**Primary user:** An agency project intern or coordinator who owns the weekly roadshow lead report.

**Their moment of pain:** Monday morning, building last week's per-agency conversion table from a messy lead export before the team meeting.

**If we only ship one thing:** F2 + F3: correct weekly per-agency funnel numbers written to an `.xlsx`.

## 1. The Idea

### 1.1 Purpose
Make the weekly per-agency lead conversion report a one-command job with numbers you can trust. It is also a portfolio project that shows data, Excel and project-management skills.

### 1.2 Description
1. Export leads from wherever they are kept as CSV or Excel (or generate synthetic ones with F4).
2. Run `lead-funnel report leads.csv --week 2026-W46 --out reports/`.
3. The tool checks the file, removes duplicates, keeps the leads captured that week, and counts how many leads per agency reached each stage.
4. It writes `reports/funnel-2026-W46.xlsx` with a per-agency funnel table, conversion percentages and a chart, and prints a short summary.

### 1.3 What the system is not
- Not a CRM; it never stores or edits leads.
- Not a web app or dashboard.
- Not connected to email or other systems.

### 1.4 Expected outcomes
The weekly report takes one command instead of manual spreadsheet work, and every number is backed by tests.

## 2. Setting and Context

Event and agency marketing teams running roadshows and workshops, who track leads in spreadsheets today. TODO: no real team interviewed.

## 3. Problem Analysis

### 3.1 Problem statement
Weekly per-agency funnel reporting is manual and error-prone: duplicates are counted twice, leads land in the wrong week, and conversion formulas break on agencies with no leads.

### 3.2 Root causes
- Process: the same report is rebuilt by hand every week.
- Data: exports contain duplicates and inconsistent stage names.
- Tools: spreadsheet formulas are copied and break silently.

### 3.3 Problem to requirement matrix

| Problem | Requirement that solves it | Feature |
|---|---|---|
| Messy exports, duplicates | Validate columns and stages; drop and count duplicates | F1 |
| Wrong week, broken formulas | Tested ISO-week filter and conversion math | F2 |
| Manual report building | Generate the `.xlsx` automatically | F3 |
| No safe data to build and demo with | Seeded synthetic lead generator | F4 |

### 3.4 Evidence
Agency project job descriptions list this report as a weekly duty (reviewed by the developer; kept outside the repo). TODO: no other evidence.

## 4. Objectives

- **General objective:** generate a correct weekly per-agency conversion report in Excel from a lead export with one command.
- **Specific objectives:**
  1. Load and validate a CSV or Excel export, reporting every rejected and duplicate row.
  2. Compute per-agency reached-stage counts and conversion rates for an ISO week, matching hand-checked fixtures.
  3. Write an `.xlsx` report with a table and chart that opens cleanly in Excel.
  4. Ship v1 and record career evidence by 2026-11-16.

## 5. Users and Roles

| Role | Description | Main tasks |
|---|---|---|
| Report owner | Intern or coordinator who runs the tool | Export leads, run the command, share the report |
| Report reader | Agency team lead | Reads per-agency conversion in Excel |

## 6. Scope and Limitations

- **Covered:** CLI, synthetic data, load and validate, weekly metrics, Excel report.
- **Limitations:** one week per run; fixed four-stage funnel; synthetic data only in the repo.
- **Bounds:** Windows and Linux; tested up to 100,000 leads; English output.

## 7. Related Systems

| System | What it does well | What it misses that we solve |
|---|---|---|
| Manual spreadsheet with pivot tables | Flexible, familiar | Rebuilt by hand weekly; duplicates and week errors |
| TODO: CRM reports | | |

## 8. Methodology and Evaluation

Built solo with the agent workflow: superpowers spec and plan per feature, test-first, reviewers before merge. Evaluated by fixture tests with hand-checked totals and a manual check of the report in Excel.

## 9. Open Questions

- Confirm the PRD gate criteria during the first feature brainstorm.
