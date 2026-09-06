"""Unit tests for removing a symbol (and its orphaned footprint) from a project."""

from __future__ import annotations

from pathlib import Path

from typani import Err

from kicad_libsync.errors import SymbolError
from kicad_libsync.importer import import_zip
from kicad_libsync.project import KicadProject, locate
from kicad_libsync.remover import remove_symbols
from kicad_libsync.sexpr import parse
from kicad_libsync.symbols import merge_into

FIXTURES = Path(__file__).parent.parent / "fixtures"


def _imported_project(tmp_path: Path) -> KicadProject:
    """A tmp project with both fixture zips imported into one merged library."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "demo.kicad_pro").write_text("{}", encoding="utf-8")
    proj = locate(project_dir).unwrap()
    import_zip(proj, FIXTURES / "2N7002NXAKR.zip").unwrap()
    import_zip(proj, FIXTURES / "22R336MC.zip").unwrap()
    return proj


def test_remove_symbols_reports_removed_names(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/remover.py::remove_symbols kind="unit"
    # frob:tests src/kicad_libsync/remover.py::RemoveReport kind="unit"
    proj = _imported_project(tmp_path)
    report = remove_symbols(proj, ["2N7002NXAKR"]).unwrap()
    assert report.removed_symbols == ["2N7002NXAKR"]
    assert report.removed_footprints == ["TO-236AB_SOT23_NEX"]
    assert report.missing == []


def test_remove_symbols_deletes_only_its_own_footprint(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/remover.py::remove_symbols kind="unit"
    proj = _imported_project(tmp_path)
    remove_symbols(proj, ["2N7002NXAKR"]).unwrap()

    assert not (proj.fp_lib / "TO-236AB_SOT23_NEX.kicad_mod").exists()
    # the unrelated 22R336MC symbol and its footprint are untouched
    assert (proj.fp_lib / "IND_2200RM_MUR.kicad_mod").exists()
    root = parse(proj.sym_lib.read_text(encoding="utf-8")).unwrap()
    names = {s.atoms()[0] for s in root.find_all("symbol")}
    assert names == {"22R336MC"}


def test_remove_symbols_keeps_shared_footprint(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/remover.py::remove_symbols kind="unit"
    proj = _imported_project(tmp_path)
    # A second symbol that reuses 2N7002NXAKR's footprint.
    shared_vendor_text = """(kicad_symbol_lib (version 20211014) (generator x)
  (symbol "2N7002NXAKR_ALT" (pin_names (offset 0.254)) (in_bom yes) (on_board yes)
    (property "Footprint" "TO-236AB_SOT23_NEX" (id 2) (at 0 0 0)
      (effects (font (size 1.27 1.27) italic) hide)
    )
  )
)
"""
    merge_into(proj.sym_lib, proj.lib_name, shared_vendor_text).unwrap()

    report = remove_symbols(proj, ["2N7002NXAKR"]).unwrap()
    assert report.removed_symbols == ["2N7002NXAKR"]
    assert "TO-236AB_SOT23_NEX" not in report.removed_footprints
    assert (proj.fp_lib / "TO-236AB_SOT23_NEX.kicad_mod").exists()


def test_remove_symbols_keep_footprints_flag_keeps_all_files(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/remover.py::remove_symbols kind="unit"
    proj = _imported_project(tmp_path)
    report = remove_symbols(proj, ["2N7002NXAKR"], keep_footprints=True).unwrap()
    assert report.removed_symbols == ["2N7002NXAKR"]
    assert report.removed_footprints == []
    assert (proj.fp_lib / "TO-236AB_SOT23_NEX.kicad_mod").exists()


def test_remove_symbols_missing_name_is_reported(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/remover.py::remove_symbols kind="unit"
    proj = _imported_project(tmp_path)
    report = remove_symbols(proj, ["DOES_NOT_EXIST"]).unwrap()
    assert report.removed_symbols == []
    assert report.missing == ["DOES_NOT_EXIST"]


def test_remove_symbols_refuses_when_placed_in_schematic(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/remover.py::remove_symbols kind="unit"
    proj = _imported_project(tmp_path)
    sch = proj.root / "x.kicad_sch"
    sch.write_text(
        '(kicad_sch (version 20211123) (symbol (lib_id "demo:2N7002NXAKR") (at 0 0 0)))\n',
        encoding="utf-8",
    )
    before_sym = proj.sym_lib.read_text(encoding="utf-8")
    before_fp_files = sorted(proj.fp_lib.glob("*.kicad_mod"))

    result = remove_symbols(proj, ["2N7002NXAKR"])
    assert isinstance(result, Err)
    assert result.danger_err is SymbolError.SymbolInUse

    assert proj.sym_lib.read_text(encoding="utf-8") == before_sym
    assert sorted(proj.fp_lib.glob("*.kicad_mod")) == before_fp_files


def test_remove_symbols_force_overrides_schematic_check(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/remover.py::remove_symbols kind="unit"
    proj = _imported_project(tmp_path)
    sch = proj.root / "x.kicad_sch"
    sch.write_text(
        '(kicad_sch (version 20211123) (symbol (lib_id "demo:2N7002NXAKR") (at 0 0 0)))\n',
        encoding="utf-8",
    )
    report = remove_symbols(proj, ["2N7002NXAKR"], force=True).unwrap()
    assert report.removed_symbols == ["2N7002NXAKR"]


def test_remove_symbols_summary_reads_human(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/remover.py::RemoveReport kind="unit"
    proj = _imported_project(tmp_path)
    report = remove_symbols(proj, ["2N7002NXAKR"]).unwrap()
    assert "symbol" in report.summary()
