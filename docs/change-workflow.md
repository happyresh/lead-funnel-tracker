# Change Workflow

**Status:** Control

How every change moves from idea to done, and how change records, audits, deferrals, postmortems, superpowers specs and plans, and reviews fit together. Templates: `docs/change-record-template.md`, `docs/audit-template.md`, `docs/postmortem-template.md`, `docs/superpowers/`.

## 1. Which Record Do I Need?

| Situation | Record | File |
|---|---|---|
| Bug fix, refactor or new code that matches the approved PRD, design and rules | None; just a commit, a review and an activity log entry | |
| A new feature already in the PRD | Superpowers spec and plan | `docs/superpowers/specs/`, `docs/superpowers/plans/` |
| Change to anything approved: a PRD feature or gate, the data model, permissions, privacy, API contract, design system, reviewer rules | **Change record** (then a spec and plan if it needs code) | `docs/cr-<short-name>.md` |
| You checked something and found problems | Audit (findings only, no decisions) | `docs/audit-<topic>-<date>.md` |
| Decided to postpone, hide or accept a missing feature | Deferred register row | `docs/deferred-features.md` |
| Something broke in use | Postmortem | `docs/postmortem-<short-name>.md` |

**Rule of thumb:** if the change makes a document stop telling the truth about the system, it needs a change record.

**Audit vs change record:** an audit records what was found; a change record records what was decided. Never build directly from an audit finding: close each finding with a change record, a deferral, or evidence that it is false.

## 2. Change Record Lifecycle

```text
Proposed -> Approved -> Applied
         -> Deferred (postponed, with a reason and a register row)
         -> Rejected (kept for history)
```

| Status | Meaning | Who sets it |
|---|---|---|
| Proposed | Written and checked against code and docs; waiting for a decision | Claude or developer |
| Approved | The developer agreed; work may start | Developer only |
| Applied | Code, tests and docs all match the record | Claude, after verification |
| Deferred | Postponed; a row exists in `docs/deferred-features.md` | Developer |
| Rejected | Not doing it; reason recorded | Developer |

Never mark Applied until the code and the required tests match the approved change. Never delete a change record; history matters.

## 3. Step by Step

1. **Explore.** Read `docs/context.md`, the affected documents and the code. State the trigger in one sentence.
2. **Write the change record** as Proposed (`docs/cr-<short-name>.md`, from the template). Fill current behavior, proposed change, impact, alternatives (always include "do nothing" and the simplest option), rollout and rollback, and verification.
3. **Verify the record** against the repository and every dependent document (PRD, QAD, DESIGN, SAD). Fix contradictions before asking for approval.
4. **Get approval.** The developer reads it and replies approve, change or reject. Record the decision and date in section 8, and add the decision to `docs/context.md` section 11.
5. **Design (if code is needed).** Use superpowers brainstorming to write the spec in `docs/superpowers/specs/`, linking the change record. Large changes get a spec; tiny ones can go straight to a plan.
6. **Plan.** Use superpowers writing-plans to write the task-by-task plan in `docs/superpowers/plans/`.
7. **Implement** on a feature branch (a git worktree is best), test first (happy, sad, abuse), following the plan.
8. **Review.** Run `claude --agent review-orchestrator`. Fix every BLOCKED finding and review again until sign-off.
9. **Update documents** in the same branch: PRD, QAD, DESIGN or other affected docs; `docs/index.md` (register the change record, spec and plan, and add a change log row); `docs/deferred-features.md` if anything was left out.
10. **Mark the change record Applied** (or Deferred for the parts not done), and fill section 9 Disposition with what changed, where, and any follow-ups.
11. **Close the session:** update `docs/context.md` section 2 and `docs/activity-log.md`.

## 4. Naming

| Record | Name pattern | Example |
|---|---|---|
| Change record | `docs/cr-<short-name>.md` | `docs/cr-add-export.md` |
| Spec | `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` | `2026-01-15-export-design.md` |
| Plan | `docs/superpowers/plans/YYYY-MM-DD-<topic>.md` | `2026-01-16-export.md` |
| Audit | `docs/audit-<topic>-YYYYMMDD.md` | `audit-security-20260120.md` |
| Postmortem | `docs/postmortem-<short-name>.md` | `postmortem-login-outage.md` |

## 5. How They Link

```text
PRD feature or audit finding
  -> change record (decision: what and why)
    -> superpowers spec (design: how)
      -> superpowers plan (tasks: in what order)
        -> code and tests on a feature branch
          -> review sign-off (docs/sad.md)
            -> documents updated, index updated
              -> change record Applied
                -> context.md and activity-log.md updated
```

Each file names the one before it: the spec header names its change record, the plan header names its spec, and the change record's disposition names the branch, commits and documents changed.

## 6. Worked Example

1. The client asks to export reports to Excel. The PRD says export is out of scope, so a change record is needed.
2. Claude writes `docs/cr-add-export.md` as Proposed: trigger (client request), current (no export), change (Excel export for admins only), impact (new endpoint, permission, button), alternatives (CSV only; do nothing), rollback (feature flag), verification (QAD rows for happy, sad and abuse).
3. The developer approves. Status becomes Approved; the decision goes into `docs/context.md` section 11.
4. Superpowers writes `2026-01-15-export-design.md` and `2026-01-16-export.md`.
5. Claude implements on `feature/export` with tests, the review signs off, and the PRD, QAD and index are updated.
6. Status becomes Applied with the branch and files listed in section 9.
