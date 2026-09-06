"""archive.inspect against REAL vendor zip fixtures, end to end."""

from __future__ import annotations

from pathlib import Path

import pytest

from kicad_libsync.archive import inspect

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.mark.parametrize(
    ("zip_name", "footprint_count"),
    [("2N7002NXAKR.zip", 3), ("22R336MC.zip", 1)],
)
def test_inspect_recognizes_real_vendor_zips(
    zip_name: str, footprint_count: int
) -> None:
    # frob:tests src/kicad_libsync/archive.py kind="integration"
    result = inspect(FIXTURES / zip_name)
    assert result.is_ok
    pkg = result.danger_ok
    assert pkg.symbols_text.startswith("(kicad_symbol_lib")
    assert len(pkg.footprints) == footprint_count
    assert all(text.startswith("(footprint") for text in pkg.footprints.values())
