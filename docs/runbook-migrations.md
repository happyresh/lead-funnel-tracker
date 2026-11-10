# Runbook: Database Migrations

> How to change the database schema safely. Reviewed by `database-guardian` (`docs/sad.md`). Fill the exact commands for your ORM or migration tool during setup.

## Principles
- Every schema change is a new migration file; never edit a migration that has already run anywhere.
- Destructive changes (drop or retype a table or column) need a change record, a backup and a tested rollback.
- New columns are nullable or have a default; large data changes use staged backfills.
- Migrations run in order: local, then throwaway replay, then development or staging, then production.

## Steps
1. **Write** the migration in a feature branch. Name it with the next number and a short description.
2. **Replay** the full migration history on a throwaway database from empty, and confirm it finishes without errors.
3. **Drift check:** compare the database produced by the migrations with the schema file (for example `schema.prisma`); they must match.
4. **Test:** run the tests that touch the changed tables, including permission (abuse) tests.
5. **Review:** run `claude --agent review-orchestrator`; `database-guardian` and `security-guardian` must PASS.
6. **Apply to development or staging:** check the migration ledger first (which migrations already ran, and their checksums), apply, then verify the ledger again.
7. **Apply to production** only after developer approval, with a fresh backup (`docs/runbook-backup-restore.md`).
8. **Record** the result in `docs/activity-log.md` and update `docs/sdd.md` if the data model changed.

## If a Migration Fails
- Stop. Do not edit the applied migration.
- Read the error and the ledger; restore from backup if data was damaged.
- Fix with a new forward migration, and write a postmortem if production was affected.
