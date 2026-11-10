# Runbook: Staging Environment

> How to build a staging (or development preview) environment that mirrors production without real data. Fill the provider-specific steps during setup.

## 1. Prerequisites
- A separate database project or instance, never shared with production.
- Separate API keys and secrets; stored in the hosting provider's environment settings, never in Git.

## 2. Environment Files
- Copy `.env.example` to the staging settings. List each variable name in `README-setup.md`; never write values in documents.

## 3. Build the Schema
- Apply every migration from empty, in order (`docs/runbook-migrations.md`).
- Verify the migration ledger shows every migration with matching checksums.

## 4. Seed Fake Data
- Use a seed script that creates realistic but fake organizations, users and records.
- Never copy production data into staging.

## 5. Point the Deployments
- Point the development preview of the web app and API at staging.
- Confirm production still points at production.

## 6. Verification
- [ ] The preview URLs respond.
- [ ] Sign-in works for one account per role.
- [ ] One key flow works end to end.
- [ ] A role is refused where it should be (abuse check).

## 7. Verified Facts
Record the date, the migration ledger state and the checks passed, here and in `docs/activity-log.md`.

| Date | Ledger state | Checks passed | Notes |
|---|---|---|---|
| | | | |
