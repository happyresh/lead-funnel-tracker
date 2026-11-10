# Runbook: Documentation Reconciliation

> Keeps documents from drifting behind the code. Run it before a release, a defense, or every few weeks. Ask Claude with the "Reconcile documents" prompt.

## Steps
1. Check `docs/index.md`: every file under `docs/` is registered, and every registered file exists.
2. Check `docs/context.md` section 2 Current State against the latest commits and `docs/activity-log.md`.
3. Verify claims in the PRD, SDD, RFCs, DESIGN and QAD against the code and tests: features marked done exist and are tested; nothing marked missing exists.
4. Check reviewer names, models and trigger paths match between `docs/sad.md` and `.claude/agents/`.
5. Check `docs/deferred-features.md` against the feature flags in the code.
6. Check change records: none stuck in Approved after their work merged; none marked Applied without matching code.
7. Record findings in an audit (`docs/audit-template.md`).
8. Close material findings through change records or explicit deferrals.
9. Update the Health Check in `docs/index.md` section 7.

Never rewrite old change records or audits to hide drift; add new records instead.
