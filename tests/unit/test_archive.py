"""Unit tests for archive.inspect recognition rules, using zips built with zipfile."""

from __future__ import annotations

import zipfile
from pathlib import Path

from kicad_libsync.archive import VendorPackage, inspect
from kicad_libsync.errors import ArchiveError

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_inspect_valid_zip_two_footprints() -> None:
    # frob:tests src/kicad_libsync/archive.py::inspect kind="unit"
    # frob:tests src/kicad_libsync/archive.py::VendorPackage kind="unit"
    result = inspect(FIXTURES / "2N7002NXAKR.zip")
    assert result.is_ok
    pkg = result.danger_ok
    assert isinstance(pkg, VendorPackage)
    assert pkg.source == FIXTURES / "2N7002NXAKR.zip"
    assert "kicad_symbol_lib" in pkg.symbols_text
    assert len(pkg.footprints) == 3
    assert pkg.models == {}


def test_inspect_valid_zip_one_footprint() -> None:
    # frob:tests src/kicad_libsync/archive.py::inspect kind="unit"
    result = inspect(FIXTURES / "22R336MC.zip")
    assert result.is_ok
    pkg = result.danger_ok
    assert len(pkg.footprints) == 1
    assert "IND_2200RM_MUR" in pkg.footprints


def test_inspect_not_a_library_has_no_symbol() -> None:
    # frob:tests src/kicad_libsync/archive.py::inspect kind="unit"
    result = inspect(FIXTURES / "not-a-library.zip")
    assert result.is_err
    assert result.danger_err is ArchiveError.NoSymbolLibrary


def test_inspect_not_a_zip(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/archive.py::inspect kind="unit"
    bad = tmp_path / "bad.zip"
    bad.write_bytes(b"not a zip at all")
    result = inspect(bad)
    assert result.is_err
    assert result.danger_err is ArchiveError.NotAZip


def test_inspect_ambiguous_symbol_library(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/archive.py::inspect kind="unit"
    zip_path = tmp_path / "ambiguous.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("a.kicad_sym", "(kicad_symbol_lib)")
        zf.writestr("b.kicad_sym", "(kicad_symbol_lib)")
        zf.writestr("footprints.pretty/x.kicad_mod", "(footprint x)")
    result = inspect(zip_path)
    assert result.is_err
    assert result.danger_err is ArchiveError.AmbiguousSymbolLibrary


def test_inspect_no_footprints(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/archive.py::inspect kind="unit"
    zip_path = tmp_path / "nofp.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("a.kicad_sym", "(kicad_symbol_lib)")
        zf.writestr("not_pretty/x.kicad_mod", "(footprint x)")
    result = inspect(zip_path)
    assert result.is_err
    assert result.danger_err is ArchiveError.NoFootprints


def test_inspect_unsafe_path_absolute(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/archive.py::inspect kind="unit"
    zip_path = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("/etc/a.kicad_sym", "(kicad_symbol_lib)")
        zf.writestr("footprints.pretty/x.kicad_mod", "(footprint x)")
    result = inspect(zip_path)
    assert result.is_err
    assert result.danger_err is ArchiveError.UnsafePath


def test_inspect_unsafe_path_traversal(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/archive.py::inspect kind="unit"
    zip_path = tmp_path / "traversal.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("../a.kicad_sym", "(kicad_symbol_lib)")
        zf.writestr("footprints.pretty/x.kicad_mod", "(footprint x)")
    result = inspect(zip_path)
    assert result.is_err
    assert result.danger_err is ArchiveError.UnsafePath


def test_inspect_not_utf8(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/archive.py::inspect kind="unit"
    zip_path = tmp_path / "notutf8.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("a.kicad_sym", b"\xff\xfe\x00\x01")
        zf.writestr("footprints.pretty/x.kicad_mod", "(footprint x)")
    result = inspect(zip_path)
    assert result.is_err
    assert result.danger_err is ArchiveError.NotUtf8
