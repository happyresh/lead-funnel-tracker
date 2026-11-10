# Project Context

**Last updated:** 2026-11-10

> How to use this file: it is loaded into every Claude Code session through `CLAUDE.md`, so Claude never starts cold. Keep the whole file under about three pages. Long material belongs in `docs/reference/`, summarized in section 13.

## 1. Project Summary

Lead-Funnel Tracker is a command-line tool that turns an export of event leads into a weekly per-agency conversion report in Excel (source: `README.md`). It is for event and agency marketing teams (source: `README.md`), and is a portfolio piece that proves data, Excel and project-management skills for agency project roles (source: the developer's private project notes, outside the repo). Stage: in development (F1 and F4 shipped). Profiles: **CLI tool + Data / analysis** (confirmed 2026-11-10). Working mode: **solo** (confirmed 2026-11-10).

## 2. Current State

| Item | Status |
|---|---|
| Phase | Building: F1 and F4 merged to `main` (PR #1, PR #2); repository going public |
| Last session | 2026-11-10: F1 and F4 shipped; repo republished as a clean public repo (old history archived privately); hosted CI replaced by a local pre-push hook |
| In progress | `fix/local-checks` |
| Next steps | 1. `/agent-workflow:feature` F2 metrics. 2. F3 Excel report. 3. `/evidence` |
| Blockers | None. GitHub Actions stays unavailable while the account has a billing lock |
| Questions for the developer | None |

## 3. Background and Problem

Agency project roles in event marketing are often asked to monitor leads per agency through the funnel and produce a weekly per-agency conversion report from roadshows (source: job descriptions the developer reviewed, kept outside the repo). Doing this by hand in a spreadsheet each week is slow and error-prone (duplicates, wrong week, broken formulas). TODO: no interviews or real data; `docs/reference/` is empty.

## 4. Goals and Success Measures

| Goal | How we measure it | Target |
|---|---|---|
| Produce a weekly per-agency conversion report in Excel | One CLI command on the synthetic dataset writes a correct `.xlsx` | Works by 2026-11-16 |
| Numbers are correct | Metric tests on hand-checked fixtures pass | 100% of QAD rows |
| Show Excel and lead-funnel skills as career evidence | Evidence note recorded with `/evidence` | By 2026-11-16 |

## 5. Users and Stakeholders

| Who | What they need | How they use the system | Notes |
|---|---|---|---|
| Event and agency marketing teams | A weekly per-agency conversion report without manual spreadsheet work | Run one command on a lead export, open the `.xlsx` | Comfortable with Excel, not necessarily with terminals |
| Recruiters and interviewers | Proof of Excel and data skills | Read the repo, README and a sample report | Portfolio audience |
| The developer | A finished practice-run project | Builds it with the agent workflow | Solo |

## 6. Scope

- **Now:** the CLI; a seeded synthetic-data generator; loading and validating a CSV or Excel lead export; weekly per-agency funnel metrics; an `.xlsx` report with a funnel table, conversion percentages and a chart.
- **Later:** week-over-week trends; a Google Sheets export.
- **Never:** web UI, CRM sync, sending emails.

## 7. Domain Glossary

| Term | Meaning | Not to be confused with |
|---|---|---|
| Lead | One prospective client captured at an event; one row in the input | A contact person inside an agency |
| Agency | The marketing agency the lead is attributed to; the report groups by it | The client business itself |
| Event / roadshow | The in-person promotional event where the lead was captured | |
| Funnel stage | Ordered: Lead → Contacted → Intro session → Onboarded | |
| Reached stage | A lead counts at every stage up to and including its current stage | Being at that stage right now |
| Conversion rate | Leads that reached stage N+1 divided by leads that reached stage N; overall = Onboarded / Lead | |
| Report week | ISO week (Monday to Sunday) of the date the lead was captured | Calendar month |

## 8. Technical Environment

| Item | Choice |
|---|---|
| Project profile(s) | CLI tool + Data / analysis |
| Languages and frameworks | Python 3.12 (machine has 3.12.3), uv 0.13.1, openpyxl; pytest and ruff as dev tools. Pinned in `pyproject.toml` and `uv.lock` |
| Planned layout | `src/lead_funnel/` (code), `tests/`, `data/sample/` (synthetic only), `reports/` (output, Git-ignored) |
| Database | None |
| Hosting and deployment | None; runs locally. No hosted CI: `.githooks/pre-push` runs ruff and pytest before every push |
| Sign-in / authentication | None |
| Third-party services | None |
| Repository and branches | `https://github.com/happyresh/lead-funnel-tracker` (public from 2026-11-10); `main` plus `feature/<slug>` and `fix/<slug>` |
| Development machine and OS | Windows 11, VS Code |
| Where secrets are kept | None needed; `.env` is Git-ignored if ever used |

## 9. Data and Privacy

- **Data stored:** lead records (lead id, name, email, phone, company, agency, event, date captured, stage) as input files; generated reports.
- **Sensitive fields:** name, email, phone are personal data. Reports show per-agency totals only, never individual leads.
- **Privacy rules:** the repo only ever holds synthetic data. If real data is ever used: Data Privacy Act of 2012 (RA 10173), and real files stay outside the repo.
- **Test data:** seeded synthetic generator with obviously fake values (for example `example.com` emails). Real personal data is never used.

## 10. Constraints

- **Deadlines:** v1 working and recorded as evidence by 2026-11-16 (end of the practice run). No other hard date.
- **Budget and accounts:** free only. The GitHub account has a billing lock, so GitHub Actions cannot run on any repo; checks run locally.
- **Required by school, client or employer:** none.
- **Must use / must not use:** Python + openpyxl; no new library without a reason.
- **Accessibility and devices:** reports open in Excel; text-only CLI output works without color.

## 11. Key Decisions

| Date | Decision | Why | Alternatives rejected |
|---|---|---|---|
| 2026-11-10 | Python + openpyxl | Scriptable, tested, produces real `.xlsx` | Google Sheets build |
| 2026-11-10 | Profiles CLI tool + Data / analysis; solo mode | Confirmed in setup | Web app (out of scope) |
| 2026-11-10 | Funnel stages Lead → Contacted → Intro session → Onboarded | Mirrors a typical agency onboarding funnel | |
| 2026-11-10 | Synthetic data only in the repo | Privacy | Real exports |
| 2026-11-10 | File problems stop the run (exit 1); bad rows are rejected, counted and listed | Real exports have typos; nothing disappears silently | Strict mode; a `--strict` flag |
| 2026-11-10 | Duplicate `lead_id`: furthest stage wins, ties keep the earliest row, conflicts warn | Order-independent and closest to the truth | Last row wins; first row wins |
| 2026-11-10 | `lead-funnel check` command ships with F1 | F1 runnable and demoable before the report | Library only; skeleton `report` |
| 2026-11-10 | Only `lead_id`, `agency`, `captured_on`, `stage` are read from input | The tool never holds personal data | Reading all columns |
| 2026-11-10 | Messages never echo stage cell text; email- or phone-like lead ids print as "(id hidden)" | privacy-guardian review: shifted columns and CRM exports can carry names or contacts there | Echoing stage-like words only |
| 2026-11-10 | Republished as a new public repo with one clean commit; the old repo (full history) is archived privately as `lead-funnel-tracker-archive`; commits use the GitHub noreply email | Portfolio visibility without exposing old history | Making the old repo public (history held personal details) |
| 2026-11-10 | No hosted CI; a git pre-push hook runs ruff and pytest before every push | The account billing lock blocks GitHub Actions on public and private repos | Self-hosted runner (also blocked); paying the balance (developer's choice, later) |

## 12. Risks and Open Questions

| Risk or question | Impact | What we do about it | Owner |
|---|---|---|---|
| Wrong numbers (duplicates, week boundaries, divide by zero) | High | data-quality-guardian; fixture tests with hand-checked totals | Developer |
| Excel formula injection from lead fields (`=`, `+`, `-`, `@`) | Medium | security-guardian rule; text cells escaped; abuse tests | Developer |
| Real personal data in sample files | Medium | privacy-guardian; generator uses fake domains | Developer |
| Tight deadline (Nov 16) | Medium | Smallest version of F1 to F4; Later items deferred | Developer |

## 13. Sources and References

| File | What it is | Key points | Trust |
|---|---|---|---|
| `README.md` | Project pitch | Event leads to weekly per-agency conversion report in Excel; for event and agency marketing teams | Authoritative |
| Developer's private project notes (outside the repo) | Project hub, practice-run checklist, reviewed job descriptions | Stack Python + openpyxl; CLI + Data; solo; v1 by Nov 16 | Authoritative |

## 14. Working Preferences

- **Explanations:** simple language, short answers; explain each step, since this is a practice run.
- **Before acting:** always ask before committing, pushing, installing packages or deleting files. Never send, post, submit or push to a public repo without explicit go.
- **Output:** Markdown docs; Excel for reports.
- **Other:** coach mode on: end replies with the "▶ Next" footer (global `CLAUDE.md`).
