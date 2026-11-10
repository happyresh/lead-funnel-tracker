# Lead-Funnel Tracker

Turns event leads into a weekly per-agency conversion report in Excel

**For:** Event and agency marketing teams

## Try it

Needs [uv](https://docs.astral.sh/uv/).

```text
uv sync
uv run lead-funnel synth --rows 500 --seed 42 --out .tmp/leads.csv
uv run lead-funnel check .tmp/leads.csv
uv run lead-funnel report .tmp/leads.csv --week 2026-W46 --out .tmp/reports
```

`synth` writes obviously fake leads; `check` loads a `.csv` or `.xlsx` export and reports rejected rows and duplicates; `report` writes `funnel-<week>.xlsx` with per-agency counts, conversion rates and a chart. Only synthetic data belongs in this repository.
