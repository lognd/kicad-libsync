"""Unit tests for merging vendor symbols into the project's .kicad_sym."""

from __future__ import annotations

import zipfile
from pathlib import Path

from kicad_libsync.sexpr import parse
from kicad_libsync.symbols import footprints_still_referenced, merge_into, remove_from

FIXTURES = Path(__file__).parent.parent / "fixtures"

VENDOR_TEXT = """(kicad_symbol_lib (version 20211014) (generator kicad_symbol_editor)
  (symbol "2N7002NXAKR" (pin_names (offset 0.254)) (in_bom yes) (on_board yes)
    (property "Reference" "Q" (id 0) (at 0 0 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "TO-236AB_SOT23_NEX" (id 2) (at 0 0 0)
      (effects (font (size 1.27 1.27) italic) hide)
    )
    (property "ki_fp_filters" "TO-236AB_SOT23_NEX" (id 6) (at 0 0 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (symbol "2N7002NXAKR_0_1"
      (circle (center 0 0) (radius 1)
        (stroke (width 0.5) (type default) (color 0 0 0 0))
        (fill (type none))
      )
    )
  )
)
"""


def _load_vendor_zip_text(name: str) -> str:
    with zipfile.ZipFile(FIXTURES / name) as z:
        [member] = [n for n in z.namelist() if n.endswith(".kicad_sym")]
        return z.read(member).decode("utf-8")


def test_merge_into_reports_added_names(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/symbols.py::merge_into kind="unit"
    # frob:tests src/kicad_libsync/symbols.py::MergeOutcome kind="unit"
    lib_path = tmp_path / "Proj.kicad_sym"
    outcome = merge_into(lib_path, "Proj", VENDOR_TEXT).unwrap()
    assert outcome.added == ["2N7002NXAKR"]
    assert outcome.skipped == []
    assert outcome.replaced == []
    assert lib_path.exists()

    root = parse(lib_path.read_text(encoding="utf-8")).unwrap()
    symbols = root.find_all("symbol")
    assert len(symbols) == 1
    fp_prop = [
        p for p in symbols[0].find_all("property") if p.atoms()[0] == "Footprint"
    ][0]
    assert fp_prop.atoms()[1] == "Proj:TO-236AB_SOT23_NEX"


def test_merge_into_only_counts_direct_children(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/symbols.py::merge_into kind="unit"
    lib_path = tmp_path / "Proj.kicad_sym"
    outcome = merge_into(lib_path, "Proj", VENDOR_TEXT).unwrap()
    assert "2N7002NXAKR_0_1" not in outcome.added


def test_merge_into_skips_existing_without_overwrite(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/symbols.py::merge_into kind="unit"
    lib_path = tmp_path / "Proj.kicad_sym"
    merge_into(lib_path, "Proj", VENDOR_TEXT).unwrap()
    outcome = merge_into(lib_path, "Proj", VENDOR_TEXT).unwrap()
    assert outcome.skipped == ["2N7002NXAKR"]
    assert outcome.added == []
    assert outcome.replaced == []


def test_merge_into_replaces_existing_with_overwrite(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/symbols.py::merge_into kind="unit"
    lib_path = tmp_path / "Proj.kicad_sym"
    merge_into(lib_path, "Proj", VENDOR_TEXT).unwrap()
    outcome = merge_into(lib_path, "Proj", VENDOR_TEXT, overwrite=True).unwrap()
    assert outcome.replaced == ["2N7002NXAKR"]
    assert outcome.added == []
    assert outcome.skipped == []

    root = parse(lib_path.read_text(encoding="utf-8")).unwrap()
    assert len(root.find_all("symbol")) == 1


def test_merge_into_creates_missing_library(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/symbols.py::merge_into kind="unit"
    lib_path = tmp_path / "does_not_yet_exist.kicad_sym"
    assert not lib_path.exists()
    outcome = merge_into(lib_path, "Proj", VENDOR_TEXT).unwrap()
    assert outcome.added == ["2N7002NXAKR"]
    root = parse(lib_path.read_text(encoding="utf-8")).unwrap()
    assert root.head == "kicad_symbol_lib"


def test_merge_into_real_fixture_zip(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/symbols.py::merge_into kind="unit"
    vendor_text = _load_vendor_zip_text("2N7002NXAKR.zip")
    lib_path = tmp_path / "Proj.kicad_sym"
    outcome = merge_into(lib_path, "Proj", vendor_text).unwrap()
    assert outcome.added == ["2N7002NXAKR"]
    root = parse(lib_path.read_text(encoding="utf-8")).unwrap()
    symbol = root.find_all("symbol")[0]
    fp_prop = [p for p in symbol.find_all("property") if p.atoms()[0] == "Footprint"][0]
    assert fp_prop.atoms()[1] == "Proj:TO-236AB_SOT23_NEX"


_SECOND_SYMBOL = """(kicad_symbol_lib (version 20211014) (generator kicad_symbol_editor)
  (symbol "OTHER_PART" (pin_names (offset 0.254)) (in_bom yes) (on_board yes)
    (property "Reference" "Q" (id 0) (at 0 0 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "Proj:TO-236AB_SOT23_NEX" (id 2) (at 0 0 0)
      (effects (font (size 1.27 1.27) italic) hide)
    )
  )
)
"""


def test_remove_from_deletes_top_level_symbol(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/symbols.py::remove_from kind="unit"
    lib_path = tmp_path / "Proj.kicad_sym"
    merge_into(lib_path, "Proj", VENDOR_TEXT).unwrap()
    removed, missing, fp_refs = remove_from(lib_path, ["2N7002NXAKR"]).unwrap()
    assert removed == ["2N7002NXAKR"]
    assert missing == []
    assert fp_refs == ["TO-236AB_SOT23_NEX"]
    root = parse(lib_path.read_text(encoding="utf-8")).unwrap()
    assert root.find_all("symbol") == []


def test_remove_from_reports_missing_names(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/symbols.py::remove_from kind="unit"
    lib_path = tmp_path / "Proj.kicad_sym"
    merge_into(lib_path, "Proj", VENDOR_TEXT).unwrap()
    removed, missing, fp_refs = remove_from(lib_path, ["DOES_NOT_EXIST"]).unwrap()
    assert removed == []
    assert missing == ["DOES_NOT_EXIST"]
    assert fp_refs == []


def test_footprints_still_referenced(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/symbols.py::footprints_still_referenced kind="unit"
    lib_path = tmp_path / "Proj.kicad_sym"
    merge_into(lib_path, "Proj", VENDOR_TEXT).unwrap()
    merge_into(lib_path, "Proj", _SECOND_SYMBOL).unwrap()
    remove_from(lib_path, ["2N7002NXAKR"]).unwrap()
    still_referenced = footprints_still_referenced(lib_path).unwrap()
    assert still_referenced == {"TO-236AB_SOT23_NEX"}
