"""Unit tests for copying vendor .kicad_mod footprints into the .pretty dir."""

from __future__ import annotations

from pathlib import Path

from kicad_libsync.footprints import copy_into, remove_orphans

FOOTPRINT_TEXT = '(footprint "X" (version 20211014) (generator pcbnew))\n'


def test_copy_into_reports_added_names(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/footprints.py::copy_into kind="unit"
    pretty_dir = tmp_path / "Proj.pretty"
    outcome = copy_into(pretty_dir, {"FP_A": FOOTPRINT_TEXT}).unwrap()
    assert outcome.added == ["FP_A"]
    assert (pretty_dir / "FP_A.kicad_mod").exists()
    assert (pretty_dir / "FP_A.kicad_mod").read_text(encoding="utf-8") == FOOTPRINT_TEXT


def test_copy_into_creates_missing_dir(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/footprints.py::copy_into kind="unit"
    pretty_dir = tmp_path / "nested" / "Proj.pretty"
    assert not pretty_dir.exists()
    outcome = copy_into(pretty_dir, {"FP_A": FOOTPRINT_TEXT}).unwrap()
    assert outcome.added == ["FP_A"]
    assert pretty_dir.is_dir()


def test_copy_into_skips_existing_without_overwrite(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/footprints.py::copy_into kind="unit"
    pretty_dir = tmp_path / "Proj.pretty"
    copy_into(pretty_dir, {"FP_A": FOOTPRINT_TEXT}).unwrap()
    outcome = copy_into(pretty_dir, {"FP_A": "different text\n"}).unwrap()
    assert outcome.skipped == ["FP_A"]
    assert (pretty_dir / "FP_A.kicad_mod").read_text(encoding="utf-8") == FOOTPRINT_TEXT


def test_copy_into_replaces_existing_with_overwrite(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/footprints.py::copy_into kind="unit"
    pretty_dir = tmp_path / "Proj.pretty"
    copy_into(pretty_dir, {"FP_A": FOOTPRINT_TEXT}).unwrap()
    new_text = "different text\n"
    outcome = copy_into(pretty_dir, {"FP_A": new_text}, overwrite=True).unwrap()
    assert outcome.replaced == ["FP_A"]
    assert (pretty_dir / "FP_A.kicad_mod").read_text(encoding="utf-8") == new_text


def test_remove_orphans_deletes_unreferenced_footprint(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/footprints.py::remove_orphans kind="unit"
    pretty_dir = tmp_path / "Proj.pretty"
    copy_into(pretty_dir, {"FP_A": FOOTPRINT_TEXT}).unwrap()
    removed = remove_orphans(pretty_dir, ["FP_A"], still_referenced=set()).unwrap()
    assert removed == ["FP_A"]
    assert not (pretty_dir / "FP_A.kicad_mod").exists()


def test_remove_orphans_keeps_shared_footprint(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/footprints.py::remove_orphans kind="unit"
    pretty_dir = tmp_path / "Proj.pretty"
    copy_into(pretty_dir, {"FP_A": FOOTPRINT_TEXT}).unwrap()
    removed = remove_orphans(pretty_dir, ["FP_A"], still_referenced={"FP_A"}).unwrap()
    assert removed == []
    assert (pretty_dir / "FP_A.kicad_mod").exists()


def test_remove_orphans_missing_file_is_a_noop(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/footprints.py::remove_orphans kind="unit"
    pretty_dir = tmp_path / "Proj.pretty"
    pretty_dir.mkdir()
    removed = remove_orphans(
        pretty_dir, ["NEVER_EXISTED"], still_referenced=set()
    ).unwrap()
    assert removed == []
