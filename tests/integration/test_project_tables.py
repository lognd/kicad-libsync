"""Locate a synthetic project and register its lib tables end to end."""

from pathlib import Path

from kicad_libsync.libtable import ensure_entry, entries
from kicad_libsync.project import locate


def test_locate_and_register_libs_are_idempotent(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/project.py kind="integration"
    # frob:tests src/kicad_libsync/libtable.py kind="integration"
    (tmp_path / "Stpone.kicad_pro").write_text("{}")
    project = locate(tmp_path).unwrap()

    sym_uri = f"${{KIPRJMOD}}/{project.lib_name}.kicad_sym"
    fp_uri = f"${{KIPRJMOD}}/{project.lib_name}.pretty"

    for _ in range(2):
        ensure_entry(project.sym_table, "sym", project.lib_name, sym_uri).unwrap()
        ensure_entry(project.fp_table, "fp", project.lib_name, fp_uri).unwrap()

    assert entries(project.sym_table).unwrap() == [(project.lib_name, sym_uri)]
    assert entries(project.fp_table).unwrap() == [(project.lib_name, fp_uri)]
