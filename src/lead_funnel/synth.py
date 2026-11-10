"""Seeded generator of obviously fake lead data."""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

from lead_funnel.files import atomic_write
from lead_funnel.stages import STAGES

COLUMNS = ("lead_id", "name", "email", "phone", "company", "agency", "event", "captured_on", "stage")

AGENCIES = (
    "Northwind Events",
    "Bluepeak Media",
    "Harborlight Agency",
    "Kestrel Promotions",
    "Saltwater Creative",
    "Tamarind Marketing",
)
EVENTS = ("Manila Roadshow", "Cebu Roadshow", "Davao Workshop", "Clark Roadshow")
FIRST_NAMES = ("Ana", "Ben", "Cara", "Dan", "Eva", "Fay", "Gil", "Hana", "Ivo", "Jun")
LAST_NAMES = ("Reyes", "Cruz", "Lim", "Uy", "Tan", "Go", "Sy", "Ramos", "Dela Paz", "Bautista")
COMPANIES = (
    "Bluebird Bakery",
    "Corner Cafe",
    "Sunny Side Diner",
    "Tidewater Tours",
    "Pine Hill Pharmacy",
    "Lantern Books",
    "Mango Grove Spa",
    "Iron Gate Gym",
)
FIRST_DAY = date(2026, 10, 5)
DAYS = 42  # 2026-10-05 to 2026-11-15 inclusive, ISO weeks 41 to 46.


def generate_leads(rows: int, seed: int) -> list[dict[str, str]]:
    """Return `rows` fake leads; the same seed always gives the same leads."""
    rng = random.Random(seed)
    # Draw order is fixed so the output bytes depend only on the seed.
    probs = {agency: [rng.uniform(0.3, 0.8) for _ in range(3)] for agency in AGENCIES}
    leads = []
    for i in range(1, rows + 1):
        first, last = rng.choice(FIRST_NAMES), rng.choice(LAST_NAMES)
        company, agency, event = rng.choice(COMPANIES), rng.choice(AGENCIES), rng.choice(EVENTS)
        captured_on = FIRST_DAY + timedelta(days=rng.randrange(DAYS))
        stage = 0
        while stage < 3 and rng.random() < probs[agency][stage]:
            stage += 1
        leads.append({
            "lead_id": f"L{i:05d}",
            "name": f"{first} {last}",
            "email": f"{first}.{last.replace(' ', '')}{i}@example.com".lower(),
            "phone": f"+00 900 000 {i % 10000:04d}",
            "company": company,
            "agency": agency,
            "event": event,
            "captured_on": captured_on.isoformat(),
            "stage": STAGES[stage],
        })
    return leads


def write_csv(path: Path, leads: list[dict[str, str]], force: bool = False) -> None:
    """Write leads as UTF-8 CSV with LF endings via a temp file, refusing to overwrite unless forced."""
    atomic_write(path, force, lambda tmp: _write_rows(tmp, leads))


def _write_rows(path: Path, leads: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(leads)
