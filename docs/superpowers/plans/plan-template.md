# Export Reports Implementation Plan (example title)

> Plan template. Superpowers writing-plans writes files in this shape. Save each plan as `YYYY-MM-DD-<topic>.md` in this folder. The content below is a short worked example; replace it.

> **For agentic workers:** use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to run this plan task by task. Steps use checkboxes (`- [ ]`) for tracking.

**Goal:** admins can export the monthly report to Excel.

**Architecture:** two or three sentences on how the pieces fit.

**Tech stack:** read from the dependency file.

**Spec:** `docs/superpowers/specs/2026-01-15-export-design.md` (approved 2026-01-15)

**Change record:** `docs/cr-add-export.md`

## Global Constraints

- Work in a git worktree on branch `feature/export`, cut from the development branch.
- Never edit an applied migration; add a new one.
- Follow `CLAUDE.md`, `AGENTS.md` and `docs/sad.md` rules.
- Comments are one sentence, no emojis.

## Review Focus

- The riskiest parts of this change, so the reviewer looks there first.

## File Structure

- Create `src/reports/export.ts`: builds the Excel file.
- Modify `src/reports/reports.controller.ts`: adds the export endpoint.

## Task 1: Export builder

- [ ] Write a failing test for a three-row report export.
- [ ] Run it and confirm it fails for the right reason.
- [ ] Implement the minimal code to pass.
- [ ] Run the test and confirm it passes.
- [ ] Commit.

## Task 2: Endpoint and permission

- [ ] Write failing tests: admin gets the file (happy), empty month gives an empty sheet (sad), member is refused (abuse).
- [ ] Implement, run, commit.

## Task 3: Documents

- [ ] Update `docs/prd.md`, `docs/qad.md` and `docs/index.md`.
- [ ] Mark the change record Applied after review sign-off.
