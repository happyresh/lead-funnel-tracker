"""Weekly per-agency funnel counts and conversion rates."""

import re
from dataclasses import dataclass
from datetime import date, timedelta

from lead_funnel.load import Lead
from lead_funnel.stages import STAGES

_WEEK = re.compile(r"(\d{4})-W(\d{2})", re.ASCII)


@dataclass(frozen=True)
class AgencyFunnel:
    agency: str
    reached: tuple[int, int, int, int]

    @property
    def step_rates(self) -> tuple[float | None, float | None, float | None]:
        """Share of leads at each stage that reached the next one; None when no lead reached the stage."""
        return tuple(_rate(self.reached[i + 1], self.reached[i]) for i in range(3))

    @property
    def overall(self) -> float | None:
        return _rate(self.reached[3], self.reached[0])


@dataclass(frozen=True)
class FunnelReport:
    week: str
    start: date
    end: date
    agencies: list[AgencyFunnel]
    total: AgencyFunnel
    leads_in_week: int


def parse_week(text: str) -> tuple[date, date]:
    """Return the Monday and Sunday of an ISO week written as YYYY-Www, or raise ValueError."""
    match = _WEEK.fullmatch(text)
    if not match:
        raise ValueError(text)
    monday = date.fromisocalendar(int(match[1]), int(match[2]), 1)
    return monday, monday + timedelta(days=6)


def default_week(today: date) -> str:
    """Return the last complete ISO week before `today`."""
    year, week, _ = (today - timedelta(days=7)).isocalendar()
    return f"{year}-W{week:02d}"


def weekly_funnel(leads: list[Lead], week: str) -> FunnelReport:
    """Count, per agency, the leads captured in `week` that reached each stage."""
    start, end = parse_week(week)
    counts: dict[str, list[int]] = {}
    for lead in leads:
        reached = counts.setdefault(lead.agency, [0] * len(STAGES))
        if start <= lead.captured_on <= end:
            for stage in range(lead.stage + 1):
                reached[stage] += 1
    agencies = sorted((AgencyFunnel(a, tuple(r)) for a, r in counts.items()), key=lambda f: (-f.reached[0], f.agency))
    total = AgencyFunnel("Total", tuple(sum(f.reached[i] for f in agencies) for i in range(len(STAGES))))
    return FunnelReport(week, start, end, agencies, total, total.reached[0])


def _rate(part: int, whole: int) -> float | None:
    return part / whole if whole else None
