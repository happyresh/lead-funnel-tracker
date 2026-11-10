"""Load a lead export, rejecting bad rows and collapsing duplicate lead ids."""

import csv
import re
import zipfile
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import openpyxl
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.utils.exceptions import InvalidFileException

from lead_funnel.stages import parse_stage

REQUIRED = ("lead_id", "agency", "captured_on", "stage")
_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


class LoadError(Exception):
    """A whole-file problem; the message is shown to the user after "Error: "."""


@dataclass(frozen=True)
class Lead:
    lead_id: str
    agency: str
    captured_on: date
    stage: int
    row: int


@dataclass
class LoadResult:
    leads: list[Lead]
    rows_read: int
    rejected: list[tuple[int, str, str]]
    duplicates: int
    warnings: list[str]


def load_leads(path: Path) -> LoadResult:
    """Read a .csv or .xlsx lead export into clean, unique leads plus counts of what was dropped."""
    if not path.exists():
        raise LoadError(f"{path.name} not found. Check the file name and folder.")
    readers = {".csv": _read_csv, ".xlsx": _read_xlsx}
    reader = readers.get(path.suffix.lower())
    if reader is None:
        raise LoadError("only .csv and .xlsx files are supported. Save the export as CSV UTF-8 or .xlsx.")
    name = path.name
    try:
        return _build(name, reader(path))
    except UnicodeDecodeError:
        raise LoadError(f'{name} is not UTF-8. Save it as "CSV UTF-8" and try again.') from None
    except PermissionError:
        raise LoadError(f"cannot open {name}. Close it in other programs and try again.") from None
    except csv.Error:
        msg = f"{name} could not be read as CSV: a field is too large or malformed. Re-export it from the source and try again."
        raise LoadError(msg) from None
    except (zipfile.BadZipFile, InvalidFileException):
        raise LoadError(f"{name} could not be read as .xlsx. Open and re-save it in Excel, then try again.") from None


def _read_csv(path: Path) -> Iterator[list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        yield from csv.reader(f)


def _read_xlsx(path: Path) -> Iterator[tuple[object, ...]]:
    # data_only=True returns cached values, so formulas are never evaluated.
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        yield from wb.worksheets[0].iter_rows(values_only=True)
    finally:
        wb.close()


def _build(name: str, rows: Iterable[list[object]]) -> LoadResult:
    rows = iter(rows)
    header = [_text(h).strip().lower() for h in next(rows, [])]
    if not header:
        raise LoadError(f"no leads found in {name}. Check that there are rows under the header.")
    missing = [col for col in REQUIRED if col not in header]
    if missing:
        raise LoadError(f"{name} is missing column(s): {', '.join(missing)}. Add them or check the export.")
    index = {col: header.index(col) for col in REQUIRED}

    leads: dict[str, Lead] = {}
    rejected: list[tuple[int, str, str]] = []
    warnings: list[str] = []
    rows_read = duplicates = 0
    for number, values in enumerate(rows, start=2):
        if all(_text(v).strip() == "" for v in values):
            continue
        rows_read += 1
        cell = {col: values[i] if i < len(values) else None for col, i in index.items()}
        lead_id = _text(cell["lead_id"]).strip()
        # Control characters are dropped so the grouping key matches the label Excel can store.
        agency = ILLEGAL_CHARACTERS_RE.sub("", _text(cell["agency"])).strip()
        stage = parse_stage(cell["stage"])
        captured_on = _date(cell["captured_on"])
        if not lead_id:
            rejected.append((number, "", "blank lead_id"))
        elif not agency:
            rejected.append((number, _shown_id(lead_id), "blank agency"))
        elif stage is None:
            # The cell text is never echoed: shifted columns can put a name or contact in it.
            rejected.append((number, _shown_id(lead_id), "unknown stage"))
        elif captured_on is None:
            rejected.append((number, _shown_id(lead_id), "bad date (use YYYY-MM-DD)"))
        elif lead_id in leads:
            duplicates += 1
            kept = leads[lead_id]
            if stage > kept.stage:
                # Replacing the value keeps the lead's first-appearance position in the dict.
                leads[lead_id] = Lead(lead_id, agency, captured_on, stage, number)
            winner = leads[lead_id].row
            for field, differs in (("agency", kept.agency != agency), ("captured_on", kept.captured_on != captured_on)):
                if differs:
                    warnings.append(
                        f"{_shown_id(lead_id)}: rows {kept.row} and {number} disagree on {field}; kept row {winner}"
                    )
        else:
            leads[lead_id] = Lead(lead_id, agency, captured_on, stage, number)
    if rows_read == 0:
        raise LoadError(f"no leads found in {name}. Check that there are rows under the header.")
    return LoadResult(list(leads.values()), rows_read, rejected, duplicates, warnings)


def _shown_id(lead_id: str) -> str:
    # Some exports use the email or phone as the lead id, so those are never printed.
    phone_like = sum(c.isdigit() for c in lead_id) >= 7 and all(c.isdigit() or c in " +-()." for c in lead_id)
    return "(id hidden)" if "@" in lead_id or phone_like else lead_id


def _text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _date(value: object) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = _text(value).strip()
    if not _ISO_DATE.fullmatch(text):
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None
