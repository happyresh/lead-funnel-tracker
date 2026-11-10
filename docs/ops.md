# Operations and Observability Runbook

**Status:** Draft

> How the running system is deployed, watched and recovered. Lines starting with "Guide:" explain what to write.

## 1. Operating Posture
- **Environments:** Guide: local, development (preview), production, and their URLs.
- **Deploy trigger:** Guide: which branch deploys where.
- **Release verification:** Guide: what to check after each deploy (health endpoint, sign-in, one key flow).

## 2. Service Levels

| Indicator | Target | How measured |
|---|---|---|
| Availability | Guide: for example 99% monthly | |
| Main page load (p95) | Guide: for example under 2 s | |
| Error rate | Guide: for example under 1% of requests | |

## 3. Observability
- **Logs:** Guide: where they are and how long kept. Never log personal data or secrets.
- **Errors:** Guide: error tracking tool, if any.
- **Metrics:** Guide: dashboards to watch.

## 4. Alerts and On-call
Guide: what triggers an alert, who receives it, and how fast they respond.

## 5. Incident Response
1. Confirm and assess impact.
2. Stop the damage (roll back, switch off a feature flag, block access).
3. Communicate to affected users if needed.
4. Fix and verify.
5. Write a postmortem (`docs/postmortem-template.md`).

## 6. Routine Operations

| Task | How often | How | Who |
|---|---|---|---|
| Backup check | Guide: weekly | See `docs/runbook-backup-restore.md` | |
| Dependency updates | Guide: monthly | | |
| Access review | Guide: each term or quarter | | |
| Secret rotation | Guide: when someone leaves or a key leaks | | |
