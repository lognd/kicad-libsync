"""Unit tests for the processed-hash ledger."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from kicad_libsync.errors import StateError
from kicad_libsync.state import ProcessedState, key, load, save, sha256_of, state_path


def test_state_path_uses_xdg_state_home(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # frob:tests src/kicad_libsync/state.py::state_path kind="unit"
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    assert state_path() == tmp_path / "kicad-libsync" / "processed.json"


def test_state_path_falls_back_to_home(monkeypatch: pytest.MonkeyPatch) -> None:
    # frob:tests src/kicad_libsync/state.py::state_path kind="unit"
    monkeypatch.delenv("XDG_STATE_HOME", raising=False)
    assert state_path() == Path.home() / ".local" / "state" / "kicad-libsync" / (
        "processed.json"
    )


def test_load_missing_file_is_empty_state(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/state.py::load kind="unit"
    result = load(tmp_path / "nope.json")
    state = result.unwrap()
    assert state.hashes == {}
    assert state.version == 1


def test_save_then_load_round_trips(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/state.py::save kind="unit"
    # frob:tests src/kicad_libsync/state.py::load kind="unit"
    path = tmp_path / "state" / "processed.json"
    original = ProcessedState()
    original.record("abc:def", "note")
    save(path, original).unwrap()

    loaded = load(path).unwrap()
    assert loaded.hashes == {"abc:def": "note"}


def test_malformed_state_is_an_error(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/state.py::load kind="unit"
    path = tmp_path / "processed.json"
    path.write_text("not json at all {")
    result = load(path)
    assert result.unwrap_err() is StateError.StateMalformed


def test_wrong_shape_state_is_malformed(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/state.py::load kind="unit"
    path = tmp_path / "processed.json"
    path.write_text('{"hashes": "not-a-dict"}')
    result = load(path)
    assert result.unwrap_err() is StateError.StateMalformed


def test_sha256_matches_hashlib(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/state.py::sha256_of kind="unit"
    path = tmp_path / "sample.bin"
    payload = os.urandom(1 << 16)
    path.write_bytes(payload)

    result = sha256_of(path).unwrap()

    assert result == hashlib.sha256(payload).hexdigest()


def test_sha256_of_missing_file_is_an_error(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/state.py::sha256_of kind="unit"
    result = sha256_of(tmp_path / "nope.bin")
    assert result.unwrap_err() is StateError.HashFailed


def test_key_scopes_digest_to_project_root(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/state.py::key kind="unit"
    assert key("abc123", tmp_path) == f"abc123:{tmp_path}"


def test_record_and_contains_round_trip(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/state.py::ProcessedState kind="unit"
    state = ProcessedState()
    state_key = key("abc123", tmp_path)
    assert not state.contains(state_key)
    state.record(state_key, "note")
    assert state.contains(state_key)
