"""Track which vendor zips have already been imported into which projects."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

from pydantic import BaseModel, ValidationError
from typani import Err, Ok, Result

from kicad_libsync.errors import StateError
from kicad_libsync.logging import get_logger

_log = get_logger(__name__)

_CHUNK_SIZE = 1 << 20


# frob:doc docs/design/03-watcher.md#state
# frob:tests tests/unit/test_state.py::test_load_missing_file_is_empty_state
class ProcessedState(BaseModel):
    """The persisted set of already-imported (zip hash, project root) pairs."""

    model_config = {}

    version: int = 1
    hashes: dict[str, str] = {}

    # frob:doc docs/design/03-watcher.md#state
    # frob:tests tests/unit/test_state.py::test_record_and_contains_round_trip
    def record(self, key: str, note: str) -> None:
        """Mark key as processed, storing note (name/time/project) for humans."""
        _log.info("recording processed key %s: %s", key, note)
        self.hashes[key] = note

    # frob:doc docs/design/03-watcher.md#state
    # frob:tests tests/unit/test_state.py::test_record_and_contains_round_trip
    def contains(self, key: str) -> bool:
        """Whether key has already been recorded as processed."""
        return key in self.hashes


# frob:doc docs/design/03-watcher.md#state
# frob:tests tests/unit/test_state.py::test_state_path_uses_xdg_state_home
# frob:waive WIRE001 reason="consumed by app/app.py" follow_up="T-0008"
def state_path() -> Path:
    """Return the per-user processed-state file path, honoring XDG_STATE_HOME."""
    base = os.environ.get("XDG_STATE_HOME")
    root = Path(base) if base else Path.home() / ".local" / "state"
    return root / "kicad-libsync" / "processed.json"


# frob:doc docs/design/03-watcher.md#state
# frob:tests tests/unit/test_state.py::test_malformed_state_is_an_error
# frob:waive WIRE001 reason="consumed by app/app.py" follow_up="T-0008"
def load(path: Path) -> Result[ProcessedState, StateError]:
    """Load ProcessedState from path; a missing file is an empty, fresh state."""
    if not path.exists():
        _log.info("no processed-state file at %s; starting empty", path)
        return Ok(ProcessedState())

    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        _log.exception("failed to read processed-state file %s", path)
        return Err(StateError.StateReadFailed)

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        _log.exception("processed-state file %s is not valid JSON", path)
        return Err(StateError.StateMalformed)

    try:
        state = ProcessedState.model_validate(data)
    except ValidationError:
        _log.exception("processed-state file %s has an unexpected shape", path)
        return Err(StateError.StateMalformed)

    _log.info("loaded processed-state from %s: %d entries", path, len(state.hashes))
    return Ok(state)


# frob:doc docs/design/03-watcher.md#state
# frob:tests tests/unit/test_state.py::test_save_then_load_round_trips
# frob:waive WIRE001 reason="consumed by watcher.py" follow_up="T-0008"
def save(path: Path, state: ProcessedState) -> Result[None, StateError]:
    """Write state to path atomically (same-dir temp file plus os.replace)."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        _log.exception("failed to create state dir %s", path.parent)
        return Err(StateError.StateWriteFailed)

    try:
        fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(state.model_dump_json(indent=2))
            os.replace(tmp_name, path)
        except OSError:
            os.unlink(tmp_name)
            raise
    except OSError:
        _log.exception("failed to write processed-state file %s", path)
        return Err(StateError.StateWriteFailed)

    _log.info("saved processed-state to %s: %d entries", path, len(state.hashes))
    return Ok(None)


# frob:doc docs/design/03-watcher.md#state
# frob:tests tests/unit/test_state.py::test_sha256_matches_hashlib
# frob:waive WIRE001 reason="consumed by watcher.py" follow_up="T-0008"
def sha256_of(path: Path) -> Result[str, StateError]:
    """Compute the SHA-256 hex digest of path's contents, reading in chunks."""
    digest = hashlib.sha256()
    try:
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(_CHUNK_SIZE), b""):
                digest.update(chunk)
    except OSError:
        _log.exception("failed to hash %s", path)
        return Err(StateError.HashFailed)
    return Ok(digest.hexdigest())


# frob:doc docs/design/03-watcher.md#state
# frob:tests tests/unit/test_state.py::test_record_and_contains_round_trip
# frob:waive WIRE001 reason="consumed by watcher.py" follow_up="T-0008"
def key(digest: str, project_root: Path) -> str:
    """Build the state key: a zip's hash scoped to the project it was imported into."""
    return f"{digest}:{project_root}"
