"""Copy vendor .kicad_mod footprints into the project's .pretty directory."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from typani import Err, Ok, Result

from kicad_libsync.errors import FootprintError
from kicad_libsync.logging import get_logger
from kicad_libsync.symbols import MergeOutcome

_log = get_logger(__name__)


# frob:doc docs/design/02-project-library-model.md#footprints
# frob:tests tests/unit/test_footprints.py::test_copy_into_reports_added_names
def copy_into(
    pretty_dir: Path, footprints: dict[str, str], overwrite: bool = False
) -> Result[MergeOutcome, FootprintError]:
    """Write each footprint's text as `<stem>.kicad_mod`, skipping duplicates."""
    try:
        pretty_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        _log.exception("failed to create footprint dir %s", pretty_dir)
        return Err(FootprintError.FootprintWriteFailed)

    outcome = MergeOutcome()
    for stem, text in footprints.items():
        dest = pretty_dir / f"{stem}.kicad_mod"
        if dest.exists():
            if not overwrite:
                _log.warning(
                    "footprint %s already exists in %s; skipping", stem, pretty_dir
                )
                outcome.skipped.append(stem)
                continue
            _log.info("footprint %s already exists in %s; replacing", stem, pretty_dir)
            write_result = _write_atomic(dest, text)
            if isinstance(write_result, Err):
                return Err(write_result.danger_err)
            outcome.replaced.append(stem)
        else:
            _log.info("adding footprint %s to %s", stem, pretty_dir)
            write_result = _write_atomic(dest, text)
            if isinstance(write_result, Err):
                return Err(write_result.danger_err)
            outcome.added.append(stem)

    return Ok(outcome)


# frob:doc docs/design/02-project-library-model.md#remover
# frob:tests tests/unit/test_footprints.py::test_remove_orphans_keeps_shared_footprint
def remove_orphans(
    pretty_dir: Path, candidates: list[str], still_referenced: set[str]
) -> Result[list[str], FootprintError]:
    """Delete each candidate's .kicad_mod unless a remaining symbol still uses it."""
    removed: list[str] = []
    for stem in candidates:
        if stem in still_referenced:
            _log.info(
                "footprint %s still referenced by a remaining symbol; keeping", stem
            )
            continue
        dest = pretty_dir / f"{stem}.kicad_mod"
        if not dest.exists():
            _log.debug("footprint %s already absent from %s", stem, pretty_dir)
            continue
        try:
            dest.unlink()
        except OSError:
            _log.exception("failed to remove orphaned footprint %s", dest)
            return Err(FootprintError.FootprintWriteFailed)
        _log.info("removed orphaned footprint %s from %s", stem, pretty_dir)
        removed.append(stem)
    return Ok(removed)


def _write_atomic(path: Path, text: str) -> Result[None, FootprintError]:
    """Write text to path via a same-dir temp file plus os.replace."""
    try:
        fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(text)
            os.replace(tmp_name, path)
        except OSError:
            os.unlink(tmp_name)
            raise
    except OSError:
        _log.exception("failed to write footprint %s", path)
        return Err(FootprintError.FootprintWriteFailed)
    return Ok(None)
