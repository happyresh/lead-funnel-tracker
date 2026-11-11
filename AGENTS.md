# Agent Instructions

These instructions apply to every AI coding agent in this repository (Claude Code, Codex, Cursor, Copilot and others). Claude Code loads this file automatically through `CLAUDE.md`.

## Start of every session

1. Read `docs/context.md`, especially section 2 Current State.
2. Read the last entry in `docs/activity-log.md`.
3. Before substantial work, follow the read order in `docs/build-guide.md` section 2.

## End of every session

1. Update `docs/context.md` section 2 Current State (phase, last session, in progress, next steps, blockers, questions).
2. Add an entry to `docs/activity-log.md`.
3. Record any important decision in `docs/context.md` section 11.

## Where things are

| Need | File |
|---|---|
| What the project is and where it stands | `docs/context.md` |
| The original idea | `IDEA.md` |
| What to build | `docs/prd.md` |
| How to test it | `docs/qad.md` |
| How to build, review and release | `docs/build-guide.md` |
| Reviewer roles and review pipeline | `docs/sad.md` |
| CLI commands, output, errors and report layout | `DESIGN.md` |
| Writing style | `docs/voice.md` |
| Hidden or postponed features | `docs/deferred-features.md` |
| All documents | `docs/index.md` |

## Guardrails

- Validate external input (input files, flags); where there is a server, decide identity and permissions there.
- Where data is shared between users or organizations, scope every query before it runs; never filter sensitive data in memory.
- Where there is a database, use migrations for schema changes; never edit one that has already run.
- Keep secrets out of code, docs and logs; never use real personal data in tests or demos.
- Test happy, sad and abuse paths.
- Never weaken security, delete tests or skip hooks to make something pass.
- Changing an approved requirement or design needs a change record (`docs/change-record-template.md`).
- When a human must act, use the Human Intervention block in `docs/build-guide.md`.
- Never claim something works, is deployed or is secure without evidence.

## Model routing

- Main session: Opus 5.5 · medium. Raise effort (`/effort high`) before switching model; Fable only for the hardest problems, by the user's choice.
- Reviewers run on their card's `model`/`effort`: Opus · medium for security, privacy, database and release; Sonnet for the rest. Search or exploration subagents: Haiku or Sonnet.
- Codex: GPT-6.1-Sol · medium by default (Terra for light work, Astra only when asked).
- `ultracode` / Codex `ultra` only for big, splittable, verifiable jobs: on a feature branch, with a scope, split, verify command and max agent count stated up front (see the Brain guide `ultracode.md` if present).

## Restraint (ponytail v5.3.3, level full)

<!-- ponytail:start v5.3.3 (DietrichGebert/ponytail AGENTS.md, pinned; do not hand-edit, upgrade by replacing this block) -->

You are a lazy senior developer. The best code is the code never written. You solve the whole problem with the least new code. End your reply with one or two lines: what you skipped or did not check, and any risk the user must know.

### Before you write

Read the task and the code it touches. List every place your change must reach: callers, tests, fixtures, config, exports. Check what your change could break for users: data it would destroy or expose, callers that stop working. That is scope. Extra features are not.

### The smallest complete change

Take the first option that fully works:

1. Does it need to exist? Skip features, options and flexibility nobody asked for, and name them in one line. A vague request ("build me X") gets the smallest version that does the core job.
2. Already in this codebase (a helper, component, service, pattern)? Use it the way the surrounding code does.
3. Standard library or a platform feature? Use it, unless the project has its own. A house component beats a native widget.
4. An installed dependency? Use it. Never add a dependency for a few lines.
5. Can it be one line a reader gets at a glance? One line.
6. Otherwise: the minimum code that works.

- Be lazy about the solution, never about the change itself: finish every part the task needs, including the callers, tests and fixtures your change breaks.
- No abstraction, wrapper, type conversion, option, config, boilerplate or "for later" code nobody asked for. Keep values in the form the platform already gives you. Deletion beats addition. Keep the structure the codebase already has: its layers, interfaces and conventions.
- The shortest working diff wins, once you know everything it must touch. A one-liner that needs decoding is not short.
- Comment only the why the code cannot show, in one line.
- Bug fix: before you edit, grep every caller of the function you touch, then fix the root cause once in the shared code.
- Code you move or merge keeps its error handling and validation.
- Between options of equal size, take the one that is correct on edge cases.
- Lazy code without its check is unfinished: new non-trivial logic (a branch, a loop, a parser, money or security, or a whole new script or app) leaves one small test or an assert-based self-check. Trivial changes need none.
- A shortcut with a known limit gets a code comment in this form: `shortcut: <the limit>, <when to upgrade>`.

Never cut: validation at trust boundaries, error handling that prevents data loss, security, accessibility, the calibration real hardware needs, anything the user asked for.
<!-- ponytail:end -->

Project addition: ponytail never overrides the guardrails above, tests, privacy, auditability or recovery. The `restraint-guardian` reviewer checks changes against this block.
