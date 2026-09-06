"""Unit test for the CLI entry point."""

import sys

import pytest

from kicad_libsync.__main__ import main


def test_main_prints_help_and_exits_cleanly(monkeypatch: pytest.MonkeyPatch) -> None:
    # frob:tests src/kicad_libsync/__main__.py::main kind="unit"
    monkeypatch.setattr(sys, "argv", ["kicad-libsync", "--help"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0
