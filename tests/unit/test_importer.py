"""Unit tests for ImportReport.summary and the importer error path."""

from __future__ import annotations

from pathlib import Path

from kicad_libsync.archive import VendorPackage
from kicad_libsync.errors import SymbolError
from kicad_libsync.importer import ImportReport, import_package
from kicad_libsync.project import locate
from kicad_libsync.symbols import MergeOutcome

FOOTPRINT_TEXT = '(footprint "X" (version 20211014) (generator pcbnew))\n'


def test_summary_reports_added_counts(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/importer.py::ImportReport kind="unit"
    report = ImportReport(
        source=tmp_path / "vendor.zip",
        symbols=MergeOutcome(added=["Q1"]),
        footprints=MergeOutcome(added=["A", "B", "C"]),
        sym_table_added=True,
        fp_table_added=False,
    )
    assert report.summary() == (
        "vendor.zip: +1 symbol, +3 footprints, sym-lib-table registered"
    )


def test_summary_reports_nothing_added(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/importer.py::ImportReport kind="unit"
    report = ImportReport(
        source=tmp_path / "vendor.zip",
        symbols=MergeOutcome(skipped=["Q1"]),
        footprints=MergeOutcome(skipped=["A"]),
        sym_table_added=False,
        fp_table_added=False,
    )
    assert report.summary() == "vendor.zip: nothing added"


def test_import_package_symbol_error_keeps_footprints(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/importer.py::import_package kind="unit"
    (tmp_path / "demo.kicad_pro").write_text("{}")
    project = locate(tmp_path).unwrap()
    pkg = VendorPackage(
        source=tmp_path / "vendor.zip",
        symbols_text="not an s-expression at all )",
        footprints={"FP_A": FOOTPRINT_TEXT},
    )

    result = import_package(project, pkg)

    assert result.unwrap_err() is SymbolError.VendorMalformed
    assert (project.fp_lib / "FP_A.kicad_mod").exists()
