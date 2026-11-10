import pytest

from lead_funnel import files
from lead_funnel.files import atomic_write


def _write_x(p):
    p.write_text("x")


def test_atomic_write_creates_folders(tmp_path):
    out = tmp_path / "sub" / "a.txt"
    atomic_write(out, False, _write_x)
    assert out.read_text() == "x"


def test_atomic_write_refuses_overwrite(tmp_path):
    out = tmp_path / "a.txt"
    out.write_text("keep")
    with pytest.raises(FileExistsError):
        atomic_write(out, False, _write_x)
    assert out.read_text() == "keep"
    atomic_write(out, True, _write_x)
    assert out.read_text() == "x"


def test_atomic_write_leaves_no_temp_on_write_error(tmp_path):
    def fail(p):
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        atomic_write(tmp_path / "a.txt", False, fail)
    assert list(tmp_path.iterdir()) == []


def test_atomic_write_cleans_up_on_replace_error(tmp_path, monkeypatch):  # Review Focus 3
    def locked(src, dst):
        raise PermissionError("locked")

    monkeypatch.setattr(files.os, "replace", locked)
    with pytest.raises(PermissionError):
        atomic_write(tmp_path / "a.txt", False, _write_x)
    assert list(tmp_path.iterdir()) == []
