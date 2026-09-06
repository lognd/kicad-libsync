"""Unit tests for the Downloads polling loop and its stability check."""

from __future__ import annotations

import shutil
from pathlib import Path

from kicad_libsync.project import locate
from kicad_libsync.state import load
from kicad_libsync.watcher import Watcher

FIXTURES = Path(__file__).parent.parent / "fixtures"


def _make_project(tmp_path: Path) -> Path:
    """Write a minimal .kicad_pro under tmp_path and return the project dir."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "demo.kicad_pro").write_text("{}")
    return project_dir


def test_unstable_file_is_not_imported(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/watcher.py::Watcher.poll_once kind="unit"
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    project = locate(_make_project(tmp_path)).unwrap()
    watcher = Watcher(downloads, project, tmp_path / "state.json")

    shutil.copy(FIXTURES / "2N7002NXAKR.zip", downloads / "2N7002NXAKR.zip")

    reports = watcher.poll_once()

    assert reports == []
    assert not project.sym_lib.exists()


def test_zip_is_imported_once_after_it_stabilizes(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/watcher.py::Watcher.poll_once kind="unit"
    # frob:tests src/kicad_libsync/watcher.py::Watcher kind="unit"
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    project = locate(_make_project(tmp_path)).unwrap()
    state_path = tmp_path / "state.json"
    watcher = Watcher(downloads, project, state_path)

    shutil.copy(FIXTURES / "2N7002NXAKR.zip", downloads / "2N7002NXAKR.zip")
    watcher.poll_once()

    second = watcher.poll_once()
    assert len(second) == 1
    assert project.sym_lib.exists()

    third = watcher.poll_once()
    assert third == []

    state = load(state_path).unwrap()
    assert len(state.hashes) == 1


def test_not_a_library_zip_is_ignored(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/watcher.py::Watcher.poll_once kind="unit"
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    project = locate(_make_project(tmp_path)).unwrap()
    watcher = Watcher(downloads, project, tmp_path / "state.json")

    dest = downloads / "not-a-library.zip"
    shutil.copy(FIXTURES / "not-a-library.zip", dest)

    watcher.poll_once()  # first poll: pending
    reports = watcher.poll_once()  # second poll: stable, inspected, ignored

    assert reports == []
    assert "not-a-library.zip" in watcher.ignored

    # A third poll must not re-inspect an ignored name.
    reports_again = watcher.poll_once()
    assert reports_again == []


def test_prime_marks_existing_zips_seen_without_backfill(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/watcher.py::Watcher.prime kind="unit"
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    project = locate(_make_project(tmp_path)).unwrap()
    shutil.copy(FIXTURES / "2N7002NXAKR.zip", downloads / "2N7002NXAKR.zip")

    watcher = Watcher(downloads, project, tmp_path / "state.json")
    watcher.prime()

    assert "2N7002NXAKR.zip" in watcher.seen
    # A pre-existing zip marked seen at startup must never be imported.
    reports = watcher.poll_once()
    reports += watcher.poll_once()
    assert reports == []
    assert not project.sym_lib.exists()


def test_backfill_imports_pre_existing_zips(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/watcher.py::Watcher.prime kind="unit"
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    project = locate(_make_project(tmp_path)).unwrap()
    dest = downloads / "2N7002NXAKR.zip"
    shutil.copy(FIXTURES / "2N7002NXAKR.zip", dest)

    watcher = Watcher(downloads, project, tmp_path / "state.json", backfill=True)
    watcher.prime()

    assert "2N7002NXAKR.zip" not in watcher.seen
    watcher.poll_once()
    reports = watcher.poll_once()

    assert len(reports) == 1
    assert project.sym_lib.exists()
