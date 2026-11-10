# Documentation Index

> Entry point and registry for every project document. Update it in the same change whenever a document is added, renamed or changes status.

**Workflow kit version:** 1.2.1 (`/agent-workflow:upgrade` compares this with the latest kit)

**Status meanings:** Locked = change only through a change record. Control = process authority. Working = usable, keep it in line with the code. Draft = not authoritative yet. Not triggered = not needed for this project (say why).

## 1. Root Files

| Document | File | Status | Role |
|---|---|---|---|
| House rules | [CLAUDE.md](../CLAUDE.md) | Control | Rules for Claude Code; loads AGENTS.md and context.md |
| Agent instructions | [AGENTS.md](../AGENTS.md) | Control | Rules for every AI agent; session start and end |
| Idea baseline | [IDEA.md](../IDEA.md) | Draft | The original idea, self-contained |
| Brand | [BRAND.md](../BRAND.md) | Not triggered | CLI tool with no visual interface or brand (CLI profile) |
| Design system | [DESIGN.md](../DESIGN.md) | Draft | Adapted to CLI commands, output, errors and Excel report layout |
| Design QA | [design-qa.md](../design-qa.md) | Not triggered | No screens; cli-ux-guardian checks DESIGN.md instead (CLI profile) |
| Setup guide | [README-setup.md](../README-setup.md) | Working | How to get the project running |

## 2. Core Suite (in order of use)

| Stage | Document | File | Status |
|---|---|---|---|
| Start | Project context and current state | [context.md](context.md) | Control |
| Build | Superpowers specs and plans | [superpowers/](superpowers/README.md) | Control |
| Start | Source material | [reference/](reference/README.md) | Working |
| Idea | Validation brief | [validation.md](validation.md) | Draft |
| Idea | Scrutiny gate | [scrutiny.md](scrutiny.md) | Draft |
| Business | Business requirements (BRD) | [brd.md](brd.md) | Draft |
| Business | Unit economics (UES) | [ues.md](ues.md) | Not triggered: portfolio project, not sold |
| Product | Product requirements (PRD) | [prd.md](prd.md) | Draft |
| Design | System design (SDD) | [sdd.md](sdd.md) | Draft |
| Design | RFCs for risky areas | `rfc-<topic>.md` from [rfc-template.md](rfc-template.md) | Draft |
| Quality | Test plan (QAD) | [qad.md](qad.md) | Draft |
| Quality | Compliance and legal register | [compliance.md](compliance.md) | Draft |
| Quality | AI assurance | [aia.md](aia.md) | Not triggered: no AI or model makes decisions |
| Build | Build guide | [build-guide.md](build-guide.md) | Control |
| Build | Agent rulebook (SAD) | [sad.md](sad.md) | Control |
| Build | Change workflow | [change-workflow.md](change-workflow.md) | Control |
| Build | House style and voice | [voice.md](voice.md) | Control |
| Build | Deferred and hidden features | [deferred-features.md](deferred-features.md) | Control |
| Operate | Operations runbook | [ops.md](ops.md) | Not triggered: runs locally, nothing in production |
| Operate | Local development runbook | [runbook-local-dev.md](runbook-local-dev.md) | Working |
| Operate | Backup and restore runbook | [runbook-backup-restore.md](runbook-backup-restore.md) | Working (no database; code and seeds) |
| Operate | Experiment tracking runbook (dataset versions, report reproducibility) | [runbook-experiment-tracking.md](runbook-experiment-tracking.md) | Working |
| Operate | Database migrations runbook | [runbook-migrations.md](runbook-migrations.md) | Not triggered: no database |
| Operate | Staging environment runbook | [runbook-staging.md](runbook-staging.md) | Not triggered: no server or deploy |
| Operate | Documentation reconciliation runbook | [runbook-doc-reconciliation.md](runbook-doc-reconciliation.md) | Control |
| Launch | Demo or defense environment runbook | [runbook-demo.md](runbook-demo.md) | Not triggered: no hosted environment; the demo is one CLI run (see pitch.md) |
| Launch | Go-to-market plan | [gtm.md](gtm.md) | Not triggered: private portfolio tool, not released publicly |
| Launch | Pitch and demo script | [pitch.md](pitch.md) | Draft |
| Close | Wrap-up and next steps | [wrap.md](wrap.md) | Draft |
| Memory | Activity log (per session) | [activity-log.md](activity-log.md) | Working |
| Memory | Build session log (milestones, lessons) | [log.md](log.md) | Control; append-only |

## 3. Templates

| Template | File | Use for |
|---|---|---|
| Change record | [change-record-template.md](change-record-template.md) | Changing anything approved |
| Audit | [audit-template.md](audit-template.md) | Recording findings |
| Postmortem | [postmortem-template.md](postmortem-template.md) | Learning from incidents |
| Handoff | [handoff-template.md](handoff-template.md) | Continuing unfinished work elsewhere |
| Manual feature test | [runbook-feature-test.md](runbook-feature-test.md) | Step-by-step acceptance test of one feature |
| Options analysis | [options-template.md](options-template.md) | Comparing solutions before a decision |
| RFC | [rfc-template.md](rfc-template.md) | Detailed contract for a risky area |
| Superpowers spec | [superpowers/specs/spec-template.md](superpowers/specs/spec-template.md) | Design of one change |
| Superpowers plan | [superpowers/plans/plan-template.md](superpowers/plans/plan-template.md) | Task list for one spec |

## 4. Change Records, Specs, Plans, Audits

| Kind | File | Date | Scope | Status |
|---|---|---|---|---|
| Spec | [superpowers/specs/2026-11-10-f4-f1-synth-load-design.md](superpowers/specs/2026-11-10-f4-f1-synth-load-design.md) | 2026-11-10 | F4 synthetic generator, F1 loader, `check` command | Executed |
| Plan | [superpowers/plans/2026-11-10-f4-f1-synth-load.md](superpowers/plans/2026-11-10-f4-f1-synth-load.md) | 2026-11-10 | 7 tasks: scaffold, synth, safe write, CSV loader, duplicates, xlsx, CLI and docs | Executed |

## 5. Traceability

Every feature follows: feature `F1` (PRD) -> gate criteria `G-F1-1` -> test rows `QAD-F1-1` (QAD) -> ISO/IEC 25010 quality area.

| Feature | Gates | Test rows | Change records | Status |
|---|---|---|---|---|
| F1 Load and validate leads | G-F1-1 to G-F1-3 | QAD-F1-1 to QAD-F1-9 | none | Shipped (PR #2) |
| F2 Weekly per-agency funnel metrics | G-F2-1 to G-F2-3 | QAD-F2-1 to QAD-F2-9 | none | Planned |
| F3 Excel report | G-F3-1 to G-F3-3 | QAD-F3-1 to QAD-F3-9 | none | Planned |
| F4 Synthetic lead generator | G-F4-1 to G-F4-3 | QAD-F4-1 to QAD-F4-9 | none | Shipped (PR #2) |

## 6. Change Log

| Date | Change |
|---|---|
| 2026-11-10 | Documentation suite created from the agent workflow kit 1.2.1; adapted to CLI tool + Data / analysis, solo mode |
| 2026-11-10 | F1 and F4 shipped (PR #2); personal references removed before making the repository public |
| 2026-11-10 | Republished as a clean public repo; hosted CI removed and replaced by `.githooks/pre-push` (ruff + pytest) |

## 7. Health Check

- [ ] Every file under `docs/` is registered here.
- [ ] `docs/context.md` section 2 Current State is up to date.
- [ ] Reviewer names and models match between `docs/sad.md` and `.claude/agents/`.
- [ ] No change record is stuck in Approved after its work merged.

## 8. Rules

1. Changes to Locked documents need a change record.
2. Audits record findings; they do not change contracts.
3. `docs/log.md` is append-only.
4. When code and a document disagree, verify the code, then fix the document or open a change record.
