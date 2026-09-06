"""sexpr against REAL vendor files pulled from the fixture zips, not hand-written samples."""

import zipfile
from pathlib import Path

import pytest

from kicad_libsync.errors import SexprError
from kicad_libsync.sexpr import Str, dumps, parse

FIXTURES = Path(__file__).parent.parent / "fixtures"


def _members(zip_name: str, suffix: str) -> list[str]:
    with zipfile.ZipFile(FIXTURES / zip_name) as z:
        return [z.read(n).decode() for n in z.namelist() if n.endswith(suffix)]


@pytest.mark.parametrize("zip_name", ["2N7002NXAKR.zip", "22R336MC.zip"])
def test_vendor_symbol_library_round_trips(zip_name: str) -> None:
    # frob:tests src/kicad_libsync/sexpr.py kind="integration"
    (text,) = _members(zip_name, ".kicad_sym")
    root = parse(text).unwrap()
    assert root.head == "kicad_symbol_lib"
    symbols = root.find_all("symbol")
    assert len(symbols) == 1
    fp = next(p for p in symbols[0].find_all("property") if p.atoms()[0] == "Footprint")
    assert isinstance(fp.atoms()[1], Str) and fp.atoms()[1]
    assert parse(dumps(root)).unwrap() == root


@pytest.mark.parametrize("zip_name", ["2N7002NXAKR.zip", "22R336MC.zip"])
def test_vendor_footprints_round_trip(zip_name: str) -> None:
    # frob:tests src/kicad_libsync/sexpr.py kind="integration"
    for text in _members(zip_name, ".kicad_mod"):
        root = parse(text).unwrap()
        assert root.head == "footprint"
        assert parse(dumps(root)).unwrap() == root


def test_error_sets_render_for_users() -> None:
    # frob:tests src/kicad_libsync/errors.py kind="integration"
    assert "UnexpectedEof" in str(parse("(").unwrap_err())
    assert parse("(").unwrap_err() is SexprError.UnexpectedEof
