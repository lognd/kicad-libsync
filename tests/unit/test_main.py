"""Unit tests for the CLI entry point."""

import sys
from pathlib import Path

import pytest

from kicad_libsync.__main__ import _build_parser, main


def test_main_prints_help_and_exits_cleanly(monkeypatch: pytest.MonkeyPatch) -> None:
    # frob:tests src/kicad_libsync/__main__.py::main kind="unit"
    monkeypatch.setattr(sys, "argv", ["kicad-libsync", "--help"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0


def test_parser_requires_a_subcommand() -> None:
    # frob:tests tests/unit/test_main.py::test_parser_requires_a_subcommand
    parser = _build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_parser_builds_watch_import_status() -> None:
    # frob:tests tests/unit/test_main.py::test_parser_builds_watch_import_status
    parser = _build_parser()
    watch_args = parser.parse_args(["watch", "--poll", "3.0", "--backfill"])
    assert watch_args.command == "watch"
    assert watch_args.poll_seconds == 3.0
    assert watch_args.backfill is True

    import_args = parser.parse_args(["import", "a.zip", "b.zip"])
    assert import_args.command == "import"
    assert import_args.zips == [Path("a.zip"), Path("b.zip")]

    status_args = parser.parse_args(["status"])
    assert status_args.command == "status"

    remove_args = parser.parse_args(["remove", "NAME_A", "NAME_B", "--force"])
    assert remove_args.command == "remove"
    assert remove_args.names == ["NAME_A", "NAME_B"]
    assert remove_args.force is True


def test_bad_poll_exits_with_code_2(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    # frob:tests src/kicad_libsync/__main__.py::main kind="unit"
    monkeypatch.setattr(
        sys,
        "argv",
        ["kicad-libsync", "watch", "--poll", "-1", "--downloads", str(tmp_path)],
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
