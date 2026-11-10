from pathlib import Path

import pytest

from lead_funnel.stages import STAGES
from lead_funnel.synth import COLUMNS, generate_leads, write_csv


def test_generates_rows_with_columns_in_order():  # QAD-F4-1
    leads = generate_leads(500, 42)
    assert len(leads) == 500
    assert all(tuple(lead) == COLUMNS for lead in leads)
    assert leads[0]["lead_id"] == "L00001" and leads[-1]["lead_id"] == "L00500"


def test_same_seed_same_data():  # QAD-F4-4
    assert generate_leads(200, 7) == generate_leads(200, 7)


def test_different_seed_different_data():  # QAD-F4-5
    assert generate_leads(200, 7) != generate_leads(200, 8)


def test_values_are_fake_and_in_range():  # QAD-F4-7, F4-8
    leads = generate_leads(500, 42)
    assert all(lead["email"].endswith("@example.com") for lead in leads)
    assert all(lead["phone"].startswith("+00 900 000 ") for lead in leads)
    assert all("2026-10-05" <= lead["captured_on"] <= "2026-11-15" for lead in leads)
    assert {lead["stage"] for lead in leads} <= set(STAGES)
    assert len({lead["agency"] for lead in leads}) == 6
    assert len({lead["event"] for lead in leads}) == 4


def test_agencies_convert_differently():
    leads = generate_leads(5000, 42)
    onboarded = {}
    for lead in leads:
        onboarded.setdefault(lead["agency"], []).append(lead["stage"] == "Onboarded")
    rates = [sum(v) / len(v) for v in onboarded.values()]
    assert max(rates) - min(rates) > 0.05


SAMPLE = Path(__file__).parent.parent / "data" / "sample" / "leads-seed42.csv"


def test_write_csv_bytes(tmp_path):
    out = tmp_path / "sub" / "leads.csv"
    write_csv(out, generate_leads(3, 1))
    data = out.read_bytes()
    assert not data.startswith(b"\xef\xbb\xbf")
    assert b"\r\n" not in data
    assert data.split(b"\n")[0] == b"lead_id,name,email,phone,company,agency,event,captured_on,stage"
    assert data.count(b"\n") == 4


def test_write_csv_refuses_overwrite(tmp_path):
    out = tmp_path / "leads.csv"
    out.write_text("keep")
    with pytest.raises(FileExistsError):
        write_csv(out, generate_leads(3, 1))
    assert out.read_text() == "keep"
    write_csv(out, generate_leads(3, 1), force=True)
    assert out.read_text().startswith("lead_id,")


def test_write_csv_leaves_no_temp_files(tmp_path):
    write_csv(tmp_path / "leads.csv", generate_leads(3, 1))
    assert [p.name for p in tmp_path.iterdir()] == ["leads.csv"]


def test_committed_sample_matches_seed_42(tmp_path):  # QAD-F4-6
    out = tmp_path / "leads.csv"
    write_csv(out, generate_leads(500, 42))
    assert out.read_bytes() == SAMPLE.read_bytes()
