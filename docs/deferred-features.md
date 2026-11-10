# Deferred and Hidden Features Register

The single list of features that are hidden behind a flag, postponed, or known to be missing. Agents check it before building, so they do not rebuild or "fix" something that was hidden on purpose.

| Feature | State | Decided | Why | Where | To re-enable |
|---|---|---|---|---|---|
| Social login (example) | Deferred | 2026-01-15 | Not needed for the first release; email sign-in covers all users | `docs/prd.md` F1 out of scope | Add an approved change record and a PRD feature |
| Data export button (example) | Hidden (flag `EXPORT_UI_ENABLED = false`) | 2026-01-20 | Export file format not approved yet | `src/constants/feature-flags.ts` | Set the flag to `true` after approval |

**States:** Hidden (built, switched off by a flag), Deferred (postponed by decision), Gap (found missing), Resolved (fixed; keep the row for history).

## Maintenance

Update this register in the same change that hides, defers or discovers a gap in a feature. Delete the two example rows when you add your first real one.
