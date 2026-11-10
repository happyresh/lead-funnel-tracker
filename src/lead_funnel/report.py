"""Write the weekly funnel workbook: a Funnel sheet with a chart and an About sheet."""

from datetime import datetime
from importlib.metadata import version
from pathlib import Path

from openpyxl import Workbook
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

from lead_funnel.files import atomic_write
from lead_funnel.load import LoadResult
from lead_funnel.metrics import AgencyFunnel, FunnelReport
from lead_funnel.stages import STAGES

HEADERS = ("Agency", *STAGES, "Lead→Contacted", "Contacted→Intro", "Intro→Onboarded", "Overall")
MAX_WIDTH = 40
_BOLD = Font(bold=True)
_RIGHT = Alignment(horizontal="right")
_FORMULA_START = ("=", "+", "-", "@", "\t", "\r")


def write_report(
    report: FunnelReport, load: LoadResult, source_name: str, out_dir: Path, force: bool, generated_at: datetime
) -> Path:
    """Save funnel-<week>.xlsx in `out_dir` and return its path; raises FileExistsError unless forced."""
    wb = Workbook()
    _funnel_sheet(wb.active, report)
    _about_sheet(wb.create_sheet("About"), report, load, source_name, generated_at)
    path = report_path(out_dir, report.week)
    atomic_write(path, force, wb.save)
    return path


def report_path(out_dir: Path, week: str) -> Path:
    """Return where the report for `week` is written; the name never comes from input text."""
    return out_dir / f"funnel-{week}.xlsx"


def _funnel_sheet(ws, report: FunnelReport) -> None:
    ws.title = "Funnel"
    _text(ws, 1, 1, f"Lead funnel {report.week} ({report.start} to {report.end})").font = _BOLD
    for col, header in enumerate(HEADERS, start=1):
        _text(ws, 3, col, header).font = _BOLD
    for row, funnel in enumerate([*report.agencies, report.total], start=4):
        _funnel_row(ws, row, funnel)
    total_row = 4 + len(report.agencies)
    for cell in ws[total_row]:
        cell.font = _BOLD
    ws.freeze_panes = "A4"
    for col in range(1, len(HEADERS) + 1):
        longest = max(len(str(ws.cell(r, col).value or "")) for r in range(3, total_row + 1))
        ws.column_dimensions[get_column_letter(col)].width = min(MAX_WIDTH, longest + 2)
    if report.agencies:
        ws.add_chart(_chart(ws, total_row - 1), "K3")


def _funnel_row(ws, row: int, funnel: AgencyFunnel) -> None:
    _text(ws, row, 1, funnel.agency)
    for col, count in enumerate(funnel.reached, start=2):
        ws.cell(row, col, count).number_format = "#,##0"
    for col, rate in enumerate([*funnel.step_rates, funnel.overall], start=6):
        if rate is None:
            _text(ws, row, col, "n/a").alignment = _RIGHT
        else:
            ws.cell(row, col, rate).number_format = "0.0%"


def _chart(ws, last_agency_row: int) -> BarChart:
    chart = BarChart(type="col", grouping="clustered")
    chart.title = "Leads reached per stage"
    chart.y_axis.title = "Leads"
    chart.x_axis.delete = chart.y_axis.delete = False  # openpyxl hides both axes by default.
    chart.add_data(Reference(ws, min_col=2, max_col=5, min_row=3, max_row=last_agency_row), titles_from_data=True)
    chart.set_categories(Reference(ws, min_col=1, min_row=4, max_row=last_agency_row))
    chart.width, chart.height = 20, 10
    return chart


def _about_sheet(ws, report: FunnelReport, load: LoadResult, source_name: str, generated_at: datetime) -> None:
    rows = (
        ("Input file", source_name),
        ("Rows read", load.rows_read),
        ("Rows rejected", len(load.rejected)),
        ("Duplicates removed", load.duplicates),
        ("Week", report.week),
        ("Date range", f"{report.start} to {report.end}"),
        ("Leads in week", report.leads_in_week),
        ("Generated", generated_at.strftime("%Y-%m-%d %H:%M")),
        ("Tool version", version("lead-funnel")),
    )
    for row, (label, value) in enumerate(rows, start=1):
        _text(ws, row, 1, label).font = _BOLD
        if isinstance(value, str):
            _text(ws, row, 2, value)
        else:
            ws.cell(row, 2, value).number_format = "#,##0"
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = min(MAX_WIDTH, max(len(str(v)) for _, v in rows) + 2)


def _text(ws, row: int, col: int, value: str):
    """Write text that Excel must never run as a formula (input text can start with = + - @)."""
    # Control characters from exports are dropped because the xlsx format cannot store them.
    cell = ws.cell(row, col, ILLEGAL_CHARACTERS_RE.sub("", value))
    if value.startswith(_FORMULA_START):
        cell.data_type = "s"
    return cell
