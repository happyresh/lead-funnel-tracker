# Audit Template

> Use an audit to record what was found when checking part of the project (security, requirements, design, performance). Copy this file to `docs/audit-<topic>-<date>.md`. An audit records findings only; fixing them needs a change record or a deferral.

**Date:** write the date.
**Scope:** files, features or documents checked.

## 1. Baseline
What was inspected: documents, code paths, environments.

## 2. Findings

| ID | Severity | Finding | Evidence | Affects | Recommended action |
|---|---|---|---|---|---|
| A-1 | High, Medium or Low | What is wrong | File and line, screenshot or test output | Which requirement or rule | Fix, defer or accept |

## 3. Verified Controls
Important things that were checked and found correct, so the audit is not only a list of defects.

## 4. Closure Path
Every finding must be closed by an approved change record, deferred with a reason (in `docs/deferred-features.md`), or shown false with evidence.

## 5. Summary
Counts by severity and the highest-risk open items.
