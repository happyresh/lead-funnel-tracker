import time
from datetime import date
from pathlib import Path

import pytest

from lead_funnel.load import Lead, load_leads
from lead_funnel.metrics import AgencyFunnel, default_week, parse_week, weekly_funnel
from lead_funnel.stages import parse_stage
from lead_funnel.synth import generate_leads

WEEK46 = Path(__file__).parent / "fixtures" / "week46.csv"


def test_parse_week():
    assert parse_week("2026-W46") == (date(2026, 11, 9), date(2026, 11, 15))
    assert parse_week("2026-W01") == (date(2025, 12, 29), date(2026, 1, 4))


@pytest.mark.parametrize("text", ["2026-W60", "2026-W00", "2026-46", "lastweek", "2026-w46", " 2026-W46", "2026-W4", "9999-W52"])
def test_parse_week_rejects(text):
    with pytest.raises(ValueError):
        parse_week(text)


def test_week_53():  # Review Focus 1
    assert parse_week("2026-W53") == (date(2026, 12, 28), date(2027, 1, 3))
    with pytest.raises(ValueError):
        parse_week("2025-W53")
    assert default_week(date(2027, 1, 5)) == "2026-W53"


def test_default_week():
    assert default_week(date(2026, 11, 10)) == "2026-W45"  # Tuesday of W46
    assert default_week(date(2026, 11, 9)) == "2026-W45"  # Monday of W46
    assert default_week(date(2026, 11, 15)) == "2026-W45"  # Sunday of W46
    assert default_week(date(2026, 1, 12)) == "2026-W02"
    assert default_week(date(2026, 1, 5)) == "2026-W01"  # ISO year 2026 starts in calendar 2025.


def _rows(report):
    return [(a.agency, a.reached) for a in report.agencies]


def test_week46_fixture():  # QAD-F2-1, F2-4, F2-5
    report = weekly_funnel(load_leads(WEEK46).leads, "2026-W46")
    assert (report.week, report.start, report.end) == ("2026-W46", date(2026, 11, 9), date(2026, 11, 15))
    assert _rows(report) == [
        ("Bluepeak Media", (6, 4, 2, 2)),
        ("Northwind Events", (4, 3, 2, 1)),
        ("Harborlight Agency", (2, 0, 0, 0)),
        ("Kestrel Promotions", (0, 0, 0, 0)),
    ]
    bluepeak, northwind = report.agencies[0], report.agencies[1]
    assert bluepeak.step_rates == pytest.approx((4 / 6, 2 / 4, 2 / 2))
    assert bluepeak.overall == pytest.approx(2 / 6)
    assert northwind.step_rates == pytest.approx((0.75, 2 / 3, 0.5))
    assert northwind.overall == pytest.approx(0.25)
    assert report.total == AgencyFunnel("Total", (12, 7, 4, 3))
    assert report.total.step_rates == pytest.approx((7 / 12, 4 / 7, 3 / 4))
    assert report.total.overall == pytest.approx(0.25)
    assert report.leads_in_week == 12


def test_lead_only_agency():  # QAD-F2-2
    harborlight = weekly_funnel(load_leads(WEEK46).leads, "2026-W46").agencies[2]
    assert harborlight.step_rates == (0.0, None, None)
    assert harborlight.overall == 0.0


def test_zero_contacted_is_none():  # QAD-F2-7
    empty = AgencyFunnel("A", (0, 0, 0, 0))
    assert empty.step_rates == (None, None, None)
    assert empty.overall is None


def test_no_leads_in_week():  # QAD-F2-9
    report = weekly_funnel(load_leads(WEEK46).leads, "2026-W40")
    assert len(report.agencies) == 4
    assert all(a.reached == (0, 0, 0, 0) for a in report.agencies)
    assert report.total.reached == (0, 0, 0, 0)
    assert report.leads_in_week == 0


def test_no_leads_at_all():  # Review Focus 5
    report = weekly_funnel([], "2026-W46")
    assert report.agencies == []
    assert report.total.reached == (0, 0, 0, 0)


def test_tie_order_is_alphabetical():
    leads = [Lead("1", "Zeta", date(2026, 11, 9), 0, 2), Lead("2", "Alpha", date(2026, 11, 9), 0, 3)]
    assert [a.agency for a in weekly_funnel(leads, "2026-W46").agencies] == ["Alpha", "Zeta"]


def test_100k_leads_under_10s():  # QAD-F2-3
    leads = [
        Lead(r["lead_id"], r["agency"], date.fromisoformat(r["captured_on"]), parse_stage(r["stage"]), i)
        for i, r in enumerate(generate_leads(100_000, 1), start=2)
    ]
    started = time.perf_counter()
    report = weekly_funnel(leads, "2026-W46")
    assert time.perf_counter() - started < 10
    start, end = parse_week("2026-W46")
    assert report.total.reached[0] == sum(start <= lead.captured_on <= end for lead in leads)
