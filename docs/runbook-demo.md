# Runbook: Demo or Defense Environment

> How to prepare a reliable demo (thesis defense, client presentation). Pair it with `docs/pitch.md`, which holds the script.

## 1. What It Produces
A demo environment with fake data that tells the story in `docs/pitch.md`, plus a snapshot that can be restored in minutes if something breaks.

## 2. Files
- Seed script for demo data (fake data only).
- Snapshot file of the seeded database.
- Demo account list (roles only; passwords kept outside the repository).

## 3. Build the Demo Data
1. Start from a clean staging or local database (`docs/runbook-staging.md`).
2. Run the demo seed script.
3. Check that every number shown in the demo is correct and not suppressed or empty.
4. Take a snapshot (`docs/runbook-backup-restore.md`) and record its file name.

## 4. Rehearsal
- Run the full demo script twice, once per role, on the same device and network as the real demo.
- Note anything slow or fragile in `docs/pitch.md` section 3.4 Do Not Click.
- Record a backup video of the full demo.

## 5. Day-of Checklist
- [ ] Snapshot restored the morning of the demo.
- [ ] All accounts sign in.
- [ ] Background jobs or schedulers started, if the demo needs them.
- [ ] Backup video and slides available offline.

## 6. Known Limits
Write what the demo cannot show and why, so it is stated honestly.

## 7. Fast Recovery
If data gets damaged during the demo, restore the snapshot (command and expected time here).
