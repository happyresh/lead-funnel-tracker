import re
import zipfile
from datetime import date, datetime
from pathlib import Path

import openpyxl
import pytest

from lead_funnel.load import Lead, LoadResult, load_leads
from lead_funnel.metrics import weekly_funnel
from lead_funnel.report import HEADERS, write_report

WEEK46 = Path(__file__).parent / "fixtures" / "week46.csv"
GENERATED = datetime(2026, 11, 17, 9, 30)


def _write(tmp_path, leads=None, source="week46.csv", force=False):
    load = load_leads(WEEK46)
    if leads is not None:
        load = LoadResult(leads, len(leads), [], 0, [])
    report = weekly_funnel(load.leads, "2026-W46")
    return write_report(report, load, source, tmp_path, force, GENERATED)


def _leads(*agencies):
    return [Lead(f"X{i}", a, date(2026, 11, 10), 1, i + 2) for i, a in enumerate(agencies)]


def test_funnel_sheet_layout(tmp_path):  # QAD-F3-1
    path = _write(tmp_path)
    assert path == tmp_path / "funnel-2026-W46.xlsx"
    wb = openpyxl.load_workbook(path)
    assert wb.sheetnames == ["Funnel", "About"]
    ws = wb["Funnel"]
    assert ws["A1"].value == "Lead funnel 2026-W46 (2026-11-09 to 2026-11-15)"
    assert ws["A1"].font.b
    assert tuple(c.value for c in ws[3]) == HEADERS
    assert all(c.font.b for c in ws[3])
    assert ws.freeze_panes == "A4"
    agencies = ["Bluepeak Media", "Northwind Events", "Harborlight Agency", "Kestrel Promotions"]
    assert [ws.cell(r, 1).value for r in range(4, 8)] == agencies
    assert [c.value for c in ws[8]][:5] == ["Total", 12, 7, 4, 3]
    assert ws["A8"].font.b
    assert ws.max_row == 8


def test_number_formats_and_na(tmp_path):
    ws = openpyxl.load_workbook(_write(tmp_path))["Funnel"]
    assert all(ws.cell(4, c).number_format == "#,##0" for c in range(2, 6))
    assert ws["F4"].value == pytest.approx(4 / 6) and ws["F4"].number_format == "0.0%"
    assert ws["I8"].value == pytest.approx(0.25)
    harborlight_intro = ws["G6"]
    assert harborlight_intro.value == "n/a"
    assert harborlight_intro.alignment.horizontal == "right"
    assert [ws.cell(7, c).value for c in range(6, 10)] == ["n/a"] * 4


def test_about_sheet(tmp_path):
    ws = openpyxl.load_workbook(_write(tmp_path))["About"]
    about = {row[0]: row[1] for row in ws.iter_rows(values_only=True)}
    assert about["Input file"] == "week46.csv"
    assert about["Rows read"] == 14
    assert about["Rows rejected"] == 0
    assert about["Duplicates removed"] == 0
    assert about["Week"] == "2026-W46"
    assert about["Date range"] == "2026-11-09 to 2026-11-15"
    assert about["Leads in week"] == 12
    assert about["Generated"] == "2026-11-17 09:30"
    assert re.fullmatch(r"\d+\.\d+\.\d+", about["Tool version"])


def test_report_has_no_personal_data(tmp_path):
    wb = openpyxl.load_workbook(_write(tmp_path))
    values = [v for ws in wb for row in ws.iter_rows(values_only=True) for v in row if isinstance(v, str)]
    assert not any(re.fullmatch(r"L\d+", v) or "@" in v for v in values)


def test_long_agency_name(tmp_path):  # QAD-F3-2
    name = "A" * 200
    ws = openpyxl.load_workbook(_write(tmp_path, _leads(name)))["Funnel"]
    assert ws["A4"].value == name
    assert ws.column_dimensions["A"].width <= 40


def test_non_ascii_agency(tmp_path):  # Review Focus 4
    ws = openpyxl.load_workbook(_write(tmp_path, _leads("Café Events", "Ñandú Media")))["Funnel"]
    assert {ws["A4"].value, ws["A5"].value} == {"Café Events", "Ñandú Media"}


def test_existing_report_needs_force(tmp_path):
    _write(tmp_path)
    with pytest.raises(FileExistsError):
        _write(tmp_path)
    _write(tmp_path, force=True)


def test_chart_present(tmp_path):
    with zipfile.ZipFile(_write(tmp_path)) as z:
        charts = [n for n in z.namelist() if n.startswith("xl/charts/chart")]
        assert len(charts) == 1
        xml = z.read(charts[0]).decode()
    assert re.search(r'<(c:)?barDir val="col"', xml) and re.search(r'<(c:)?grouping val="clustered"', xml)
    assert len(re.findall(r"<(c:)?ser>", xml)) == 4
    assert "$A$4:$A$7" in xml  # Agencies only; the Total row is left out.


def test_no_chart_without_agencies(tmp_path):
    with zipfile.ZipFile(_write(tmp_path, [])) as z:
        assert not any(n.startswith("xl/charts/") for n in z.namelist())


def test_agency_names_never_formulas(tmp_path):  # QAD-F3-4 to F3-6
    names = ["Acme Events", "-Minus Media", "+Plus PR", "@At Agency", '=HYPERLINK("http://x","click")']
    path = _write(tmp_path, _leads(*names))
    ws = openpyxl.load_workbook(path)["Funnel"]
    cells = [ws.cell(r, 1) for r in range(4, 9)]
    assert sorted(c.value for c in cells) == sorted(names)
    assert all(c.data_type == "s" for c in cells)
    with zipfile.ZipFile(path) as z:
        for sheet in ("xl/worksheets/sheet1.xml", "xl/worksheets/sheet2.xml"):
            assert "<f>" not in z.read(sheet).decode()


def test_source_name_formula_guard(tmp_path):
    ws = openpyxl.load_workbook(_write(tmp_path, source="=evil.csv"))["About"]
    cell = next(row[1] for row in ws.iter_rows() if row[0].value == "Input file")
    assert cell.value == "=evil.csv" and cell.data_type == "s"


def test_interrupted_save_leaves_no_file(tmp_path, monkeypatch):  # QAD-F3-3
    def boom(self, filename):
        raise RuntimeError("disk full")

    monkeypatch.setattr(openpyxl.Workbook, "save", boom)
    with pytest.raises(RuntimeError):
        _write(tmp_path)
    assert list(tmp_path.iterdir()) == []
