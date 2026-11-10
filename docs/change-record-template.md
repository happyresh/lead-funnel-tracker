# Change Record Template

> Use a change record when an approved requirement, design, data model or security rule must change. Copy this file to `docs/cr-<short-name>.md` (for example `docs/cr-add-export.md`) and answer each section. Audits record findings; change records record decisions. The full workflow, statuses and a worked example are in `docs/change-workflow.md`. Register every change record in `docs/index.md` section 4.

**Date:** write the date.
**Status:** Proposed, Approved, Applied, Deferred or Rejected.

## 1. Trigger
What verified problem, decision, request or audit finding started this change?

## 2. Current Behavior
What do the current documents and code do today?

## 3. Proposed Change
The exact change to behavior, data, security, interface or documents.

## 4. Impact
- **Product:** what users will notice.
- **Data / migration:** schema or data changes.
- **Permissions / privacy:** who can see or do what.
- **API:** endpoints or contracts that change.
- **Interface:** screens that change.
- **Tests:** tests to add or update.
- **Documents:** files to update.

## 5. Alternatives Considered
Include "do nothing" and the simplest option.

## 6. Rollout and Rollback
How the change is applied, and how it is safely undone.

## 7. Verification
The exact tests and evidence that prove it works.

## 8. Approval
Who approved it, and when.

## 9. Disposition
What was applied, what was deferred, and follow-ups. Do not mark Applied until the code and tests match.

## Workflow

```text
explore -> write this record -> check against code and docs -> get approval -> apply -> test -> update docs and index -> mark Applied, Deferred or Rejected
```
