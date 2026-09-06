"""Unit tests for project.locate."""

from pathlib import Path

from kicad_libsync.errors import ProjectError
from kicad_libsync.project import locate


def test_locate_derives_paths_from_stem(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/project.py::locate kind="unit"
    # frob:tests src/kicad_libsync/project.py::KicadProject kind="unit"
    (tmp_path / "Stpone.kicad_pro").write_text("{}")
    project = locate(tmp_path).unwrap()
    assert project.root == tmp_path
    assert project.name == "Stpone"
    assert project.lib_name == "Stpone"
    assert project.sym_lib == tmp_path / "Stpone.kicad_sym"
    assert project.fp_lib == tmp_path / "Stpone.pretty"
    assert project.sym_table == tmp_path / "sym-lib-table"
    assert project.fp_table == tmp_path / "fp-lib-table"


def test_locate_accepts_a_kicad_pro_file_path(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/project.py::locate kind="unit"
    pro_file = tmp_path / "Widget.kicad_pro"
    pro_file.write_text("{}")
    project = locate(pro_file).unwrap()
    assert project.root == tmp_path
    assert project.name == "Widget"


def test_locate_respects_explicit_lib_name(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/project.py::locate kind="unit"
    (tmp_path / "Widget.kicad_pro").write_text("{}")
    project = locate(tmp_path, lib_name="Vendor").unwrap()
    assert project.lib_name == "Vendor"
    assert project.sym_lib == tmp_path / "Vendor.kicad_sym"


def test_locate_missing_path_is_an_error(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/project.py::locate kind="unit"
    result = locate(tmp_path / "nope")
    assert result.unwrap_err() is ProjectError.ProjectPathMissing


def test_locate_no_kicad_pro_is_not_a_project(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/project.py::locate kind="unit"
    result = locate(tmp_path)
    assert result.unwrap_err() is ProjectError.NotAProject


def test_locate_two_kicad_pro_is_ambiguous(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/project.py::locate kind="unit"
    (tmp_path / "A.kicad_pro").write_text("{}")
    (tmp_path / "B.kicad_pro").write_text("{}")
    result = locate(tmp_path)
    assert result.unwrap_err() is ProjectError.AmbiguousProject
