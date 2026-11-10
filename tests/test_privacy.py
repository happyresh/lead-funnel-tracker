import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
EMAIL = re.compile(r"[\w.+-]+@([\w-]+\.)+[\w-]+")


def test_committed_data_uses_example_domains_only():  # QAD-F4-9
    files = [p for d in ("data", "tests/fixtures") for p in (ROOT / d).rglob("*") if p.is_file()]
    assert files
    for path in files:
        for match in EMAIL.finditer(path.read_text(encoding="utf-8")):
            assert match.group().lower().endswith(("@example.com", "@example.org")), path.name
