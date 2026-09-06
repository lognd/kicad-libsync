"""Integration tests for importing a real vendor zip into a synthetic project."""

from __future__ import annotations

from pathlib import Path

from kicad_libsync.importer import import_zip
from kicad_libsync.libtable import entries
from kicad_libsync.project import locate
from kicad_libsync.sexpr import parse

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_import_zip_writes_symbol_and_footprints(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/importer.py::import_zip kind="integration"
    (tmp_path / "demo.kicad_pro").write_text("{}")
    project = locate(tmp_path).unwrap()

    report = import_zip(project, FIXTURES / "2N7002NXAKR.zip").unwrap()

    assert report.symbols.added == ["2N7002NXAKR"]
    assert project.sym_lib.exists()
    lib_root = parse(project.sym_lib.read_text(encoding="utf-8")).unwrap()
    [symbol] = lib_root.find_all("symbol")
    footprint_prop = next(
        p for p in symbol.find_all("property") if p.atoms()[0] == "Footprint"
    )
    assert footprint_prop.atoms()[1] == "demo:TO-236AB_SOT23_NEX"

    mod_files = sorted(project.fp_lib.glob("*.kicad_mod"))
    assert len(mod_files) == 3

    assert ("demo", "${KIPRJMOD}/demo.kicad_sym") in entries(project.sym_table).unwrap()
    assert ("demo", "${KIPRJMOD}/demo.pretty") in entries(project.fp_table).unwrap()


def test_import_twice_skips_everything(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/importer.py kind="integration"
    (tmp_path / "demo.kicad_pro").write_text("{}")
    project = locate(tmp_path).unwrap()
    zip_path = FIXTURES / "2N7002NXAKR.zip"

    first = import_zip(project, zip_path).unwrap()
    assert first.symbols.added == ["2N7002NXAKR"]
    assert len(first.footprints.added) == 3
    assert first.sym_table_added is True
    assert first.fp_table_added is True

    second = import_zip(project, zip_path).unwrap()

    assert second.symbols.added == []
    assert second.symbols.skipped == ["2N7002NXAKR"]
    assert second.footprints.added == []
    assert len(second.footprints.skipped) == 3
    assert second.sym_table_added is False
    assert second.fp_table_added is False
