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
| CI | GitHub Actions | `.github/workflows/ci.yml` |

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
5. **Generate sample data:** `uv run lead-funnel synth --rows 500 --seed 42 --out data/sample/leads-seed42.csv`.
6. **Run a report:** `uv run lead-funnel report data/sample/leads-seed42.csv --week 2026-W46 --out reports/`.
7. **Open:** `reports/funnel-2026-W46.xlsx` in Excel.

## Everyday Commands

| Command | What it does |
|---|---|
| `uv sync` | Install or update dependencies |
| `uv run pytest` | Run tests |
| `uv run ruff check .` | Lint |
| `uv run lead-funnel --help` | Show commands and flags |

## Success Checklist

- [ ] `uv run pytest` passes.
- [ ] The report command writes an `.xlsx` that opens in Excel.

## Troubleshooting

| Problem | Fix |
|---|---|
| `uv` not found | Install uv (link above) and open a new terminal |
| Report file is locked | Close it in Excel; Windows blocks writing to an open file |

## Useful Documents

`docs/context.md`, `docs/build-guide.md`, `docs/runbook-local-dev.md`, `docs/index.md`.
