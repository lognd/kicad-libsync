"""Integration test: Watcher.run against real fixture zips and real state."""

# frob:tests src/kicad_libsync/watcher.py kind="integration"
# frob:tests src/kicad_libsync/state.py kind="integration"

from __future__ import annotations

import asyncio
import shutil
from pathlib import Path

import pytest

from kicad_libsync.project import locate
from kicad_libsync.state import load
from kicad_libsync.watcher import Watcher

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_run_imports_two_fixtures(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/watcher.py::Watcher.run kind="integration"
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "demo.kicad_pro").write_text("{}")
    project = locate(project_dir).unwrap()
    state_path = tmp_path / "state.json"

    shutil.copy(FIXTURES / "2N7002NXAKR.zip", downloads / "2N7002NXAKR.zip")
    shutil.copy(FIXTURES / "22R336MC.zip", downloads / "22R336MC.zip")

    watcher = Watcher(downloads, project, state_path, backfill=True)

    iterations = 0

    async def fake_sleep(_seconds: float) -> None:
        """Advance the run loop a fixed number of times, then stop it."""
        nonlocal iterations
        iterations += 1
        if iterations >= 3:
            raise StopAsyncIteration

    with pytest.raises(StopAsyncIteration):
        asyncio.run(watcher.run(poll_seconds=0.0, sleep=fake_sleep))

    state = load(state_path).unwrap()
    assert len(state.hashes) == 2
    assert project.sym_lib.exists()
