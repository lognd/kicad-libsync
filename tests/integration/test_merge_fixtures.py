"""Merge BOTH real vendor fixture zips into one project library end to end."""

from __future__ import annotations

import zipfile
from pathlib import Path

from kicad_libsync.footprints import copy_into
from kicad_libsync.sexpr import parse
from kicad_libsync.symbols import merge_into

FIXTURES = Path(__file__).parent.parent / "fixtures"
ZIP_NAMES = ["2N7002NXAKR.zip", "22R336MC.zip"]


def _read_package(zip_name: str) -> tuple[str, dict[str, str]]:
    """Return (vendor .kicad_sym text, {stem: footprint text}) from a vendor zip."""
    with zipfile.ZipFile(FIXTURES / zip_name) as z:
        names = z.namelist()
        [sym_member] = [n for n in names if n.endswith(".kicad_sym")]
        vendor_text = z.read(sym_member).decode("utf-8")
        footprints = {
            Path(n).stem: z.read(n).decode("utf-8")
            for n in names
            if n.endswith(".kicad_mod")
        }
        return vendor_text, footprints


def test_merge_both_fixture_zips_into_one_project_library(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/symbols.py kind="integration"
    # frob:tests src/kicad_libsync/footprints.py kind="integration"
    lib_name = "Proj"
    lib_path = tmp_path / f"{lib_name}.kicad_sym"
    pretty_dir = tmp_path / f"{lib_name}.pretty"

    for zip_name in ZIP_NAMES:
        vendor_text, footprints = _read_package(zip_name)
        fp_outcome = copy_into(pretty_dir, footprints).unwrap()
        assert fp_outcome.added
        sym_outcome = merge_into(lib_path, lib_name, vendor_text).unwrap()
        assert sym_outcome.added

    root = parse(lib_path.read_text(encoding="utf-8")).unwrap()
    symbols = root.find_all("symbol")
    assert len(symbols) == 2

    for symbol in symbols:
        fp_prop = next(
            p for p in symbol.find_all("property") if p.atoms()[0] == "Footprint"
        )
        fp_value = str(fp_prop.atoms()[1])
        assert fp_value.startswith(f"{lib_name}:")
        _, fp_name = fp_value.split(":", 1)
        assert (pretty_dir / f"{fp_name}.kicad_mod").exists()
