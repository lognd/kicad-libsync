"""System tests: drive the real CLI via subprocess, exactly as a user would."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

FIXTURES = Path(__file__).parent.parent / "fixtures"
REPO_ROOT = Path(__file__).parent.parent.parent


def _run(
    args: list[str], env: dict[str, str], timeout: float = 30.0
) -> subprocess.CompletedProcess:
    """Invoke `python -m kicad_libsync <args>` from the repo root with env."""
    return subprocess.run(
        [sys.executable, "-m", "kicad_libsync", *args],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _base_env(tmp_path: Path) -> dict[str, str]:
    """A clean env with per-test XDG state, so the real state file is untouched."""
    import os

    env = dict(os.environ)
    env["XDG_STATE_HOME"] = str(tmp_path / "xdg-state")
    env.pop("KICAD_LIBSYNC_DOWNLOADS", None)
    env.pop("KICAD_LIBSYNC_PROJECT", None)
    env.pop("KICAD_LIBSYNC_POLL", None)
    return env


def test_import_end_to_end(tmp_path: Path) -> None:
    # frob:tests tests/system/test_cli.py::test_import_end_to_end
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "demo.kicad_pro").write_text("{}", encoding="utf-8")

    result = _run(
        ["import", "--project", str(project_dir), str(FIXTURES / "2N7002NXAKR.zip")],
        env=_base_env(tmp_path),
    )
    assert result.returncode == 0, result.stderr

    assert (project_dir / "demo.kicad_sym").exists()
    assert (project_dir / "demo.pretty").is_dir()
    mod_files = sorted((project_dir / "demo.pretty").glob("*.kicad_mod"))
    assert len(mod_files) == 3
    assert (project_dir / "sym-lib-table").exists()
    assert (project_dir / "fp-lib-table").exists()


def test_import_registers_project_local_libraries(tmp_path: Path) -> None:
    # frob:tests tests/system/test_cli.py::test_import_registers_project_local_libraries
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "demo.kicad_pro").write_text("{}", encoding="utf-8")

    result = _run(
        ["import", "--project", str(project_dir), str(FIXTURES / "2N7002NXAKR.zip")],
        env=_base_env(tmp_path),
    )
    assert result.returncode == 0, result.stderr

    sym_table = (project_dir / "sym-lib-table").read_text(encoding="utf-8")
    fp_table = (project_dir / "fp-lib-table").read_text(encoding="utf-8")
    assert "${KIPRJMOD}/demo.kicad_sym" in sym_table
    assert "${KIPRJMOD}/demo.pretty" in fp_table


def test_second_import_is_a_no_op(tmp_path: Path) -> None:
    # frob:tests tests/system/test_cli.py::test_second_import_is_a_no_op
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "demo.kicad_pro").write_text("{}", encoding="utf-8")
    env = _base_env(tmp_path)
    args = ["import", "--project", str(project_dir), str(FIXTURES / "2N7002NXAKR.zip")]

    first = _run(args, env=env)
    assert first.returncode == 0, first.stderr

    before = {p: p.read_bytes() for p in project_dir.rglob("*") if p.is_file()}

    second = _run(args, env=env)
    assert second.returncode == 0, second.stderr

    after = {p: p.read_bytes() for p in project_dir.rglob("*") if p.is_file()}
    assert before == after


def test_remove_end_to_end(tmp_path: Path) -> None:
    # frob:tests tests/system/test_cli.py::test_remove_end_to_end
    # frob:tests src/kicad_libsync/remover.py kind="integration"
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "demo.kicad_pro").write_text("{}", encoding="utf-8")
    env = _base_env(tmp_path)

    imported = _run(
        ["import", "--project", str(project_dir), str(FIXTURES / "2N7002NXAKR.zip")],
        env=env,
    )
    assert imported.returncode == 0, imported.stderr
    imported_second = _run(
        ["import", "--project", str(project_dir), str(FIXTURES / "22R336MC.zip")],
        env=env,
    )
    assert imported_second.returncode == 0, imported_second.stderr

    # A schematic placing the symbol blocks removal without --force.
    sch = project_dir / "x.kicad_sch"
    sch.write_text(
        '(kicad_sch (version 20211123) (symbol (lib_id "demo:2N7002NXAKR") (at 0 0 0)))\n',
        encoding="utf-8",
    )
    blocked = _run(["remove", "--project", str(project_dir), "2N7002NXAKR"], env=env)
    assert blocked.returncode == 1
    assert (project_dir / "demo.pretty" / "TO-236AB_SOT23_NEX.kicad_mod").exists()

    sch.unlink()
    removed = _run(["remove", "--project", str(project_dir), "2N7002NXAKR"], env=env)
    assert removed.returncode == 0, removed.stderr
    assert not (project_dir / "demo.pretty" / "TO-236AB_SOT23_NEX.kicad_mod").exists()
    assert (project_dir / "demo.pretty" / "IND_2200RM_MUR.kicad_mod").exists()


def test_watch_backfill_imports_once(tmp_path: Path) -> None:
    # frob:tests tests/system/test_cli.py::test_watch_backfill_imports_once
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "demo.kicad_pro").write_text("{}", encoding="utf-8")

    downloads_dir = tmp_path / "Downloads"
    downloads_dir.mkdir()
    (downloads_dir / "2N7002NXAKR.zip").write_bytes(
        (FIXTURES / "2N7002NXAKR.zip").read_bytes()
    )

    env = _base_env(tmp_path)
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "kicad_libsync",
            "watch",
            "--project",
            str(project_dir),
            "--downloads",
            str(downloads_dir),
            "--backfill",
            "--poll",
            "0.2",
        ],
        cwd=REPO_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        time.sleep(3.0)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10.0)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10.0)

    assert (project_dir / "demo.kicad_sym").exists()
    assert (project_dir / "demo.pretty").is_dir()

    import json

    state_file = tmp_path / "xdg-state" / "kicad-libsync" / "processed.json"
    assert state_file.exists()
    state_data = json.loads(state_file.read_text(encoding="utf-8"))
    assert len(state_data["hashes"]) == 1
