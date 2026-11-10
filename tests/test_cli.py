from datetime import date
from pathlib import Path

import pytest

from lead_funnel import cli
from lead_funnel.cli import main

ROOT = Path(__file__).parent.parent
MESSY = ROOT / "tests" / "fixtures" / "messy.csv"
SAMPLE = ROOT / "data" / "sample" / "leads-seed42.csv"


def test_synth_writes_file(tmp_path, capsys):
    p = tmp_path / "out.csv"
    assert main(["synth", "--out", str(p), "--rows", "5", "--seed", "3"]) == 0
    assert capsys.readouterr().out == f"Wrote 5 leads to {p} (seed 3)\n"
    assert len(p.read_text(encoding="utf-8").splitlines()) == 6


def test_synth_refuses_overwrite(tmp_path, capsys):
    p = tmp_path / "out.csv"
    main(["synth", "--out", str(p), "--rows", "5"])
    capsys.readouterr()
    assert main(["synth", "--out", str(p), "--rows", "5"]) == 1
    assert capsys.readouterr().err == f"Error: {p} already exists. Use --force to replace it.\n"
    assert main(["synth", "--out", str(p), "--rows", "5", "--force"]) == 0


@pytest.mark.parametrize("rows", ["0", "-5", "100001"])
def test_synth_rows_limits(tmp_path, capsys, rows):  # QAD-F4-2, F4-3
    with pytest.raises(SystemExit) as exc:
        main(["synth", "--out", str(tmp_path / "x.csv"), "--rows", rows])
    assert exc.value.code == 2
    assert "must be between 1 and 100000" in capsys.readouterr().err


def test_synth_rows_not_a_number(tmp_path, capsys):
    with pytest.raises(SystemExit) as exc:
        main(["synth", "--out", str(tmp_path / "x.csv"), "--rows", "abc"])
    assert exc.value.code == 2
    assert "must be between 1 and 100000" in capsys.readouterr().err


def test_synth_permission_error_exits_1(tmp_path, capsys, monkeypatch):  # Review Focus 2
    def locked(*args, **kwargs):
        raise PermissionError("locked")

    monkeypatch.setattr(cli, "write_csv", locked)
    p = tmp_path / "out.csv"
    assert main(["synth", "--out", str(p)]) == 1
    assert capsys.readouterr().err == f"Error: cannot write {p}. Close it in other programs and try again.\n"


def test_check_messy_fixture(capsys):
    assert main(["check", str(MESSY)]) == 0
    out, err = capsys.readouterr()
    assert out == (
        "Read 8 rows from messy.csv\n"
        "Rejected 3 rows (blank lead_id: 1, unknown stage: 1, bad date: 1)\n"
        "Removed 1 duplicate lead ids\n"
        "Kept 4 leads across 2 agencies\n"
    )
    assert err.splitlines() == ["Row 4 (L4): unknown stage", "Row 6 (L6): bad date (use YYYY-MM-DD)", "Row 8: blank lead_id"]


def test_check_load_error_exits_1(tmp_path, capsys):
    p = tmp_path / "leads.csv"
    p.write_text("lead_id,captured_on,stage\nL1,2026-11-09,Lead\n", encoding="utf-8")
    assert main(["check", str(p)]) == 1
    assert capsys.readouterr().err == "Error: leads.csv is missing column(s): agency. Add them or check the export.\n"


def test_check_caps_detail_lines(tmp_path, capsys):
    p = tmp_path / "leads.csv"
    rows = "".join(f"L{i},Northwind Events,2026-11-09,Won\n" for i in range(25))
    p.write_text("lead_id,agency,captured_on,stage\n" + rows, encoding="utf-8")
    assert main(["check", str(p)]) == 0
    err = capsys.readouterr().err.splitlines()
    assert len(err) == 21
    assert err[-1] == "...and 5 more"


def test_unexpected_error_exits_3(capsys, monkeypatch):
    def boom(path):
        raise RuntimeError("boom")

    monkeypatch.setattr(cli, "load_leads", boom)
    assert main(["check", str(MESSY)]) == 3
    err = capsys.readouterr().err
    assert err == "Error: something went wrong. Run with --debug for details.\n"
    assert main(["--debug", "check", str(MESSY)]) == 3
    err = capsys.readouterr().err
    assert "Traceback" in err and "boom" in err


def test_debug_flag_after_subcommand(capsys, monkeypatch):  # review run 20261110-2200, cli-ux
    def boom(path):
        raise RuntimeError("boom")

    monkeypatch.setattr(cli, "load_leads", boom)
    assert main(["check", str(MESSY), "--debug"]) == 3
    assert "Traceback" in capsys.readouterr().err


WEEK46 = ROOT / "tests" / "fixtures" / "week46.csv"


def test_report_week46(tmp_path, capsys):  # QAD-F2-1 via the CLI
    assert main(["report", str(WEEK46), "--week", "2026-W46", "--out", str(tmp_path)]) == 0
    path = tmp_path / "funnel-2026-W46.xlsx"
    assert capsys.readouterr().out == (
        "Read 14 rows from week46.csv\n"
        "Rejected 0 rows\n"
        "Removed 0 duplicate lead ids\n"
        "Week 2026-W46: 12 leads across 3 agencies\n"
        f"Wrote {path}\n"
    )
    assert path.exists()


def test_report_default_week(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(cli, "_today", lambda: date(2026, 11, 17))
    assert main(["report", str(WEEK46), "--out", str(tmp_path)]) == 0
    assert "Week 2026-W46 (last complete week): 12 leads across 3 agencies\n" in capsys.readouterr().out


def test_usage_error_format(capsys):  # review run 20261110-1900, cli-ux (DESIGN.md section 3)
    with pytest.raises(SystemExit) as exc:
        main(["report", str(WEEK46), "--week", "9999-W52"])
    assert exc.value.code == 2
    assert capsys.readouterr().err == "Error: --week must look like 2026-W46. Run lead-funnel report --help for usage.\n"


def test_out_inside_a_file(tmp_path, capsys):  # review run 20261110-1900, design-qa
    notes = tmp_path / "notes.txt"
    notes.write_text("x")
    out = notes / "sub"
    assert main(["report", str(WEEK46), "--week", "2026-W46", "--out", str(out), "--force"]) == 1
    assert capsys.readouterr().err == f"Error: --out {out} is inside {notes}, which is a file, not a folder. Give a folder path.\n"
    assert main(["synth", "--out", str(out / "x.csv"), "--force"]) == 1
    err = capsys.readouterr().err
    assert err == f"Error: --out {out / 'x.csv'} is inside {notes}, which is a file, not a folder. Give another path.\n"
    assert [p.name for p in tmp_path.iterdir()] == ["notes.txt"]


def test_synth_out_is_a_folder(tmp_path, capsys):  # review run 20261110-1900, design-qa S5
    for extra in ([], ["--force"]):
        assert main(["synth", "--out", str(tmp_path), *extra]) == 1
        expected = f"Error: --out {tmp_path} is a folder, not a file. Give a file path like {tmp_path / 'leads.csv'}.\n"
        assert capsys.readouterr().err == expected
    assert list(tmp_path.iterdir()) == []


def test_unknown_command(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["nope"])
    assert exc.value.code == 2
    err = capsys.readouterr().err
    # Newer Python patch releases quote the choices, so only the stable parts are checked.
    assert err.startswith("Error: unknown command 'nope'. Choose from ") and "report" in err


@pytest.mark.parametrize("week", ["2026-W60", "lastweek"])
def test_report_bad_week(tmp_path, capsys, week):  # QAD-F2-6
    with pytest.raises(SystemExit) as exc:
        main(["report", str(WEEK46), "--week", week, "--out", str(tmp_path)])
    assert exc.value.code == 2
    assert "must look like 2026-W46" in capsys.readouterr().err


def test_report_empty_week(tmp_path, capsys):  # QAD-F2-8
    assert main(["report", str(WEEK46), "--week", "2026-W40", "--out", str(tmp_path)]) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[3:] == ["No leads in 2026-W40; wrote an empty report", f"Wrote {tmp_path / 'funnel-2026-W40.xlsx'}"]


def test_report_creates_out(tmp_path):  # QAD-F3-7
    out = tmp_path / "new" / "reports"
    assert main(["report", str(WEEK46), "--week", "2026-W46", "--out", str(out)]) == 0
    assert [p.name for p in out.iterdir()] == ["funnel-2026-W46.xlsx"]


def test_report_existing_needs_force(tmp_path, capsys):  # QAD-F3-8
    args = ["report", str(WEEK46), "--week", "2026-W46", "--out", str(tmp_path)]
    main(args)
    capsys.readouterr()
    assert main(args) == 1
    path = tmp_path / "funnel-2026-W46.xlsx"
    assert capsys.readouterr().err == f"Error: {path} already exists. Use --force to replace it.\n"
    assert main([*args, "--force"]) == 0


def test_report_permission_error(tmp_path, capsys, monkeypatch):  # Review Focus 3
    def locked(*args, **kwargs):
        raise PermissionError("locked")

    monkeypatch.setattr(cli, "write_report", locked)
    assert main(["report", str(WEEK46), "--week", "2026-W46", "--out", str(tmp_path)]) == 1
    path = tmp_path / "funnel-2026-W46.xlsx"
    assert capsys.readouterr().err == f"Error: cannot write {path}. Close it in Excel and try again.\n"


def test_report_out_is_a_file(tmp_path, capsys):  # Review Focus 2
    out = tmp_path / "reports"
    out.write_text("not a folder")
    assert main(["report", str(WEEK46), "--week", "2026-W46", "--out", str(out)]) == 1
    assert capsys.readouterr().err == f"Error: --out {out} is a file, not a folder. Give a folder path.\n"


def test_report_all_rows_rejected(tmp_path, capsys):  # Review Focus 5
    p = tmp_path / "leads.csv"
    p.write_text("lead_id,agency,captured_on,stage\nL1,Acme,2026-11-10,Won\n", encoding="utf-8")
    assert main(["report", str(p), "--week", "2026-W46", "--out", str(tmp_path / "r")]) == 0
    assert "No leads in 2026-W46; wrote an empty report" in capsys.readouterr().out
    assert (tmp_path / "r" / "funnel-2026-W46.xlsx").exists()


def test_report_debug_after_subcommand(tmp_path, capsys, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(cli, "write_report", boom)
    assert main(["report", str(WEEK46), "--week", "2026-W46", "--out", str(tmp_path), "--debug"]) == 3
    assert "Traceback" in capsys.readouterr().err


@pytest.mark.parametrize("command", ["synth", "check", "report"])
def test_help_shows_examples(capsys, command):
    with pytest.raises(SystemExit) as exc:
        main([command, "--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "Example:" in out


def test_help_avoids_banned_words(capsys):  # review run 20261110-2200, design-qa (docs/voice.md)
    for args in (["--help"], ["synth", "--help"], ["check", "--help"], ["report", "--help"]):
        with pytest.raises(SystemExit):
            main(args)
        out = capsys.readouterr().out.lower()
        assert not any(word in out for word in ("demo", "mock", "prototype"))


def test_check_sample(capsys):
    assert main(["check", str(SAMPLE)]) == 0
    assert capsys.readouterr().out == (
        "Read 500 rows from leads-seed42.csv\n"
        "Rejected 0 rows\n"
        "Removed 0 duplicate lead ids\n"
        "Kept 500 leads across 6 agencies\n"
    )
