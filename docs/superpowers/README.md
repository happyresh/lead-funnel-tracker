# Superpowers

Superpowers is a Claude Code plugin by Jesse Vincent (obra) that gives Claude disciplined skills for designing, planning, testing, debugging and finishing work. Its skills start on their own when the task matches, and they save design specs and task plans in this folder.

## Install (once per computer)

In Claude Code, run `/plugin`, open the Discover tab, search for **superpowers**, and install it. Or run these two commands:

```text
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

Restart Claude Code afterwards.

## The Skills You Will Use

| Skill | When it runs | What it produces |
|---|---|---|
| brainstorming | Before any new feature or design change | Questions to you, then a design spec in `specs/` |
| using-git-worktrees | Before implementing a plan | A separate working folder and branch, so `dev` stays clean |
| writing-plans | After a spec is approved | A task-by-task plan in `plans/` |
| subagent-driven-development | Running a plan (recommended) | A fresh helper per task, reviewed between tasks |
| executing-plans | Running a plan in batches | Tasks done in order with checkpoints |
| test-driven-development | While writing code | A failing test first, then the code, then refactor |
| systematic-debugging | When something breaks | Root cause before any fix |
| requesting-code-review | After a task or branch | A review against the plan |
| verification-before-completion | Before saying "done" | Commands run and evidence shown |
| finishing-a-development-branch | When the work is complete | Choice to merge, open a pull request, or keep the branch |

## Folder Rules

- `specs/YYYY-MM-DD-<topic>-design.md`: one design per change. Start from `specs/spec-template.md`.
- `plans/YYYY-MM-DD-<topic>.md`: one plan per spec. Start from `plans/plan-template.md`.
- Every spec names its change record (if one exists); every plan names its spec.
- Register each spec and plan in `docs/index.md` with its status (Draft, Approved, In progress, Executed, Integrated).

## How It Fits the Rest of the Workflow

- A **change record** decides what and why; a **spec** designs how; a **plan** lists the tasks. See `docs/change-workflow.md`.
- Superpowers' own code review is per task; the **SAD review** (`claude --agent review-orchestrator`) is the safety gate before merge. Run both.
- Superpowers keeps discipline inside a task; `docs/context.md` and `docs/activity-log.md` keep memory between sessions.
