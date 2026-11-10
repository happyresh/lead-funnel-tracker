# Setup Guide

> How a new developer (or you, on a new computer) gets the project running. Commands are planned until the first feature creates `pyproject.toml`.

## Overview

Lead-Funnel Tracker is a command-line tool that turns an export of event leads into a weekly per-agency conversion report in Excel. It is for event and agency marketing teams.

## Tech Stack

| Part | Technology | Version source |
|---|---|---|
| Language | Python 3.12 | `pyproject.toml` (`requires-python`), once created |
| Package manager | uv | installed tool |
| Excel output | openpyxl | `pyproject.toml` / `uv.lock` |
| Tests and lint | pytest, ruff | `pyproject.toml` dev dependencies |
| Checks before push | git pre-push hook (ruff + pytest) | `.githooks/pre-push` |

## Prerequisites

- Git: https://git-scm.com
- Python 3.12: https://www.python.org/downloads/
- uv: https://docs.astral.sh/uv/getting-started/installation/
- VS Code (optional): https://code.visualstudio.com

## Step-by-step Setup

1. **Clone:** `git clone https://github.com/happyresh/lead-funnel-tracker.git` and `cd lead-funnel-tracker`.
2. **Open in VS Code.**
3. **Environment file:** none needed.
4. **Install dependencies:** `uv sync`.
5. **Turn on the pre-push check (once per clone):** `git config core.hooksPath .githooks`. From then on every `git push` runs ruff and pytest first and stops if either fails. This replaces hosted CI.
6. **Generate sample data:** `uv run lead-funnel synth --rows 500 --seed 42 --out .tmp/leads.csv`.
7. **Check it:** `uv run lead-funnel check .tmp/leads.csv`.
8. **Report:** `uv run lead-funnel report .tmp/leads.csv --week 2026-W46 --out .tmp/reports`, then open `.tmp/reports/funnel-2026-W46.xlsx` in Excel.

## Everyday Commands

| Command | What it does |
|---|---|
| `uv sync` | Install or update dependencies |
| `uv run pytest` | Run tests |
| `uv run ruff check .` | Lint |
| `uv run lead-funnel --help` | Show commands and flags |

## Success Checklist

- [ ] `uv run pytest` passes.
- [ ] `git config core.hooksPath` prints `.githooks`.
- [ ] `uv run lead-funnel check .tmp/leads.csv` prints a summary with 0 rejected rows.
- [ ] `uv run lead-funnel report .tmp/leads.csv --week 2026-W46 --out .tmp/reports` writes `funnel-2026-W46.xlsx` and it opens in Excel without a repair warning.

## Troubleshooting

| Problem | Fix |
|---|---|
| `uv` not found | Install uv (link above) and open a new terminal |
| Report file is locked | Close it in Excel; Windows blocks writing to an open file |
| Push stopped with "pre-push: checks failed" | Run `uv run ruff check .` and `uv run pytest`, fix what fails, then push again |

## Useful Documents

`docs/context.md`, `docs/build-guide.md`, `docs/runbook-local-dev.md`, `docs/index.md`.
