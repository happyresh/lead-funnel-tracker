from datetime import date, datetime
from pathlib import Path

import openpyxl
import pytest

from lead_funnel.load import LoadError, load_leads

FIXTURES = Path(__file__).parent / "fixtures"
HEADER = "lead_id,name,email,phone,company,agency,event,captured_on,stage\n"


def write(tmp_path, text, name="leads.csv", encoding="utf-8"):
    path = tmp_path / name
    path.write_text(text, encoding=encoding, newline="")
    return path


def row(lead_id="L1", agency="Northwind Events", captured_on="2026-11-09", stage="Lead", email="a@example.com"):
    return f"{lead_id},Ana Cruz,{email},+00 900 000 0001,Bluebird Bakery,{agency},Manila Roadshow,{captured_on},{stage}\n"


def test_messy_fixture_counts():  # QAD-F1-1, F1-5, F1-9
    result = load_leads(FIXTURES / "messy.csv")
    assert result.rows_read == 8
    assert result.rejected == [(4, "L4", "unknown stage"), (6, "L6", "bad date (use YYYY-MM-DD)"), (8, "", "blank lead_id")]
    assert result.duplicates == 1
    assert [lead.lead_id for lead in result.leads] == ["L1", "L3", "L5", "L9"]
    l3 = next(lead for lead in result.leads if lead.lead_id == "L3")
    assert (l3.stage, l3.row) == (3, 7)
    assert next(lead for lead in result.leads if lead.lead_id == "L9").stage == 3
    assert result.warnings == []


def test_bom_csv_loads(tmp_path):
    path = write(tmp_path, HEADER + row(), encoding="utf-8-sig")
    assert len(load_leads(path).leads) == 1


def test_header_case_and_spaces(tmp_path):
    path = write(tmp_path, " Lead_ID , AGENCY,captured_on,Stage \nL1,Northwind Events,2026-11-09,Lead\n")
    [lead] = load_leads(path).leads
    assert (lead.lead_id, lead.agency, lead.stage, lead.row) == ("L1", "Northwind Events", 0, 2)


def test_only_required_columns_needed(tmp_path):
    path = write(tmp_path, "lead_id,agency,captured_on,stage\nL1,Northwind Events,2026-11-09,Lead\n")
    assert len(load_leads(path).leads) == 1


def test_missing_columns(tmp_path):  # QAD-F1-5
    path = write(tmp_path, "lead_id,captured_on\nL1,2026-11-09\n")
    with pytest.raises(LoadError) as err:
        load_leads(path)
    assert str(err.value) == "leads.csv is missing column(s): agency, stage. Add them or check the export."


def test_header_only_file(tmp_path):  # QAD-F1-2
    with pytest.raises(LoadError) as err:
        load_leads(write(tmp_path, HEADER))
    assert str(err.value) == "no leads found in leads.csv. Check that there are rows under the header."
    with pytest.raises(LoadError) as err:
        load_leads(write(tmp_path, HEADER + "\n\n", name="blank.csv"))
    assert str(err.value) == "no leads found in blank.csv. Check that there are rows under the header."


def test_missing_file(tmp_path):
    with pytest.raises(LoadError) as err:
        load_leads(tmp_path / "nope.csv")
    assert str(err.value) == "nope.csv not found. Check the file name and folder."


@pytest.mark.parametrize("name", ["leads.xlsm", "leads.xls", "leads.txt"])
def test_unsupported_extensions(tmp_path, name):  # QAD-F1-3
    with pytest.raises(LoadError) as err:
        load_leads(write(tmp_path, HEADER + row(), name=name))
    assert str(err.value) == "only .csv and .xlsx files are supported. Save the export as CSV UTF-8 or .xlsx."


def test_oversized_field(tmp_path):  # QAD-F1-3
    path = write(tmp_path, HEADER + row(agency="x" * 200_000))
    with pytest.raises(LoadError) as err:
        load_leads(path)
    assert str(err.value).startswith("leads.csv could not be read as CSV")


def test_rejection_never_prints_personal_data(tmp_path):  # QAD-F1-6
    path = write(tmp_path, HEADER + row(stage="Won", email="secret.person@example.com"))
    result = load_leads(path)
    assert result.rejected == [(2, "L1", "unknown stage")]
    assert "secret.person" not in repr(result)


@pytest.mark.parametrize("cell", ["Won", "Ana Cruz", "x" * 50])
def test_unknown_stage_never_echoes_cell_text(tmp_path, cell):  # review run 20261110-2200, privacy
    result = load_leads(write(tmp_path, HEADER + row(stage=cell)))
    assert result.rejected == [(2, "L1", "unknown stage")]


@pytest.mark.parametrize("lead_id", ["ana@example.com", "+00 900 000 1234", "09171234567"])
def test_contact_like_lead_id_is_hidden(tmp_path, lead_id):  # review run 20261110-2200, privacy
    text = HEADER + row(lead_id=lead_id, agency=" ") + row(lead_id=lead_id, agency="A") + row(lead_id=lead_id, agency="B")
    result = load_leads(write(tmp_path, text))
    assert result.rejected == [(2, "(id hidden)", "blank agency")]
    assert result.warnings == ["(id hidden): rows 3 and 4 disagree on agency; kept row 3"]
    assert result.leads[0].lead_id == lead_id


@pytest.mark.parametrize("lead_id", ["L00007", "1001", "100001", "CRM-2026-0042"])
def test_normal_lead_ids_still_shown(tmp_path, lead_id):
    result = load_leads(write(tmp_path, HEADER + row(lead_id=lead_id, agency=" ")))
    assert result.rejected == [(2, lead_id, "blank agency")]


def test_blank_agency_rejected(tmp_path):
    result = load_leads(write(tmp_path, HEADER + row(agency="  ")))
    assert result.rejected == [(2, "L1", "blank agency")]


def test_blank_lead_ids_rejected_individually(tmp_path):  # QAD-F1-9
    result = load_leads(write(tmp_path, HEADER + row(lead_id="") + row(lead_id=" ") + row(lead_id="L2")))
    assert result.rejected == [(2, "", "blank lead_id"), (3, "", "blank lead_id")]
    assert [lead.lead_id for lead in result.leads] == ["L2"]


def test_non_utf8_csv_is_load_error(tmp_path):  # Review Focus 1
    path = write(tmp_path, HEADER + row(agency="Café Events"), encoding="cp1252")
    with pytest.raises(LoadError) as err:
        load_leads(path)
    assert str(err.value) == 'leads.csv is not UTF-8. Save it as "CSV UTF-8" and try again.'


def test_permission_error_is_load_error(tmp_path, monkeypatch):  # Review Focus 2
    path = write(tmp_path, HEADER + row())

    def locked(*args, **kwargs):
        raise PermissionError("locked")

    monkeypatch.setattr(Path, "open", locked)
    with pytest.raises(LoadError) as err:
        load_leads(path)
    assert str(err.value) == "cannot open leads.csv. Close it in other programs and try again."


def test_semicolon_csv_reports_missing_columns(tmp_path):  # Review Focus 4
    path = write(tmp_path, "lead_id;agency;captured_on;stage\nL1;Northwind Events;2026-11-09;Lead\n")
    with pytest.raises(LoadError) as err:
        load_leads(path)
    assert str(err.value).startswith("leads.csv is missing column(s): lead_id")


def test_repeated_id_counted_once(tmp_path):  # QAD-F1-7
    result = load_leads(write(tmp_path, HEADER + row() + row()))
    assert len(result.leads) == 1
    assert (result.duplicates, result.warnings) == (1, [])


def test_furthest_stage_wins(tmp_path):  # QAD-F1-8
    result = load_leads(write(tmp_path, HEADER + row(stage="Onboarded") + row(stage="Contacted")))
    [lead] = result.leads
    assert (lead.stage, lead.row) == (3, 2)


def test_tie_keeps_earliest_row(tmp_path):
    result = load_leads(write(tmp_path, HEADER + row(captured_on="2026-11-09") + row(captured_on="2026-11-10")))
    [lead] = result.leads
    assert lead.row == 2
    assert result.warnings == ["L1: rows 2 and 3 disagree on captured_on; kept row 2"]


def test_conflicting_agency_warns(tmp_path):
    text = HEADER + row(agency="Northwind Events") + row(agency="Bluepeak Media", stage="Onboarded")
    result = load_leads(write(tmp_path, text))
    [lead] = result.leads
    assert (lead.agency, lead.row) == ("Bluepeak Media", 3)
    assert result.warnings == ["L1: rows 2 and 3 disagree on agency; kept row 3"]


def test_three_copies(tmp_path):
    result = load_leads(write(tmp_path, HEADER + row() + row() + row()))
    assert result.duplicates == 2


XLSX_HEADER = ["lead_id", "name", "email", "phone", "company", "agency", "event", "captured_on", "stage"]


def xlsx(tmp_path, rows, name="leads.xlsx", extra_sheet=None):
    wb = openpyxl.Workbook()
    for r in rows:
        wb.active.append(r)
    if extra_sheet:
        other = wb.create_sheet("Other")
        for r in extra_sheet:
            other.append(r)
    path = tmp_path / name
    wb.save(path)
    return path


def xrow(lead_id="L1", captured_on="2026-11-09", stage="Lead", agency="Northwind Events"):
    return [lead_id, "Ana Cruz", "a@example.com", "+00 900 000 0001", "Bluebird Bakery", agency, "Manila Roadshow", captured_on, stage]


def test_xlsx_loads(tmp_path):  # QAD-F1-1
    path = xlsx(tmp_path, [XLSX_HEADER, xrow("L1", datetime(2026, 11, 9, 14, 30)), xrow("L2", "2026-11-10"), xrow("L3")])
    result = load_leads(path)
    assert [lead.lead_id for lead in result.leads] == ["L1", "L2", "L3"]
    assert result.leads[0].captured_on == date(2026, 11, 9)
    assert result.leads[1].captured_on == date(2026, 11, 10)


def test_xlsx_first_sheet_only(tmp_path):
    path = xlsx(tmp_path, [XLSX_HEADER, xrow("L1")], extra_sheet=[XLSX_HEADER, xrow("L2"), xrow("L3")])
    assert [lead.lead_id for lead in load_leads(path).leads] == ["L1"]


def test_xlsx_formula_cell_not_evaluated(tmp_path):
    result = load_leads(xlsx(tmp_path, [XLSX_HEADER, xrow(stage="=1+1")]))
    assert result.leads == []
    assert result.rejected == [(2, "L1", "unknown stage")]


def test_numeric_lead_id_cells(tmp_path):  # Review Focus 3
    result = load_leads(xlsx(tmp_path, [XLSX_HEADER, xrow(1001), xrow(1001.0)]))
    assert [lead.lead_id for lead in result.leads] == ["1001"]
    assert result.duplicates == 1


def test_xlsx_title_row_reports_missing_columns(tmp_path):  # Review Focus 5
    path = xlsx(tmp_path, [["Weekly leads"], XLSX_HEADER, xrow()])
    with pytest.raises(LoadError) as err:
        load_leads(path)
    assert str(err.value).startswith("leads.xlsx is missing column(s): lead_id")


def test_corrupt_xlsx_is_load_error(tmp_path):
    path = write(tmp_path, "not a zip", name="leads.xlsx")
    with pytest.raises(LoadError) as err:
        load_leads(path)
    assert str(err.value) == "leads.xlsx could not be read as .xlsx. Open and re-save it in Excel, then try again."


def test_bad_date_reason_shows_expected_format(tmp_path):  # final review Important 2
    result = load_leads(write(tmp_path, HEADER + row(captured_on="10/5/2026")))
    assert result.rejected == [(2, "L1", "bad date (use YYYY-MM-DD)")]


@pytest.mark.parametrize("cell", ["ana@example.com", "+00 900 000 1234", "09171234567"])
def test_unknown_stage_never_echoes_contact_like_text(tmp_path, cell):  # final review Minor 5, re-graded Important
    result = load_leads(write(tmp_path, "lead_id,agency,captured_on,stage\nL1,Northwind Events,2026-11-09," + cell + "\n"))
    assert result.rejected == [(2, "L1", "unknown stage")]


def test_csv_error_message_has_fix(tmp_path):
    path = write(tmp_path, HEADER + row(agency="x" * 200_000))
    with pytest.raises(LoadError) as err:
        load_leads(path)
    assert str(err.value).endswith(". Re-export it from the source and try again.")


def test_agency_control_characters(tmp_path):  # review run 20261110-1900, data-quality S5
    text = HEADER + row("L1", "Acme") + row("L2", "Acme\x01") + row("L3", "\x01")
    result = load_leads(write(tmp_path, text))
    assert [lead.agency for lead in result.leads] == ["Acme", "Acme"]
    assert result.rejected == [(4, "L3", "blank agency")]
