"""Merge vendor .kicad_sym symbols into the project's merged symbol library."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from pydantic import BaseModel
from typani import Err, Ok, Result

from kicad_libsync.errors import SymbolError
from kicad_libsync.logging import get_logger
from kicad_libsync.sexpr import Node, Str, dumps, parse

_log = get_logger(__name__)

_EMPTY_LIB_HEADER = (
    '(kicad_symbol_lib (version 20211014) (generator "kicad-libsync"))\n'
)


# frob:doc docs/design/02-project-library-model.md#symbols
# frob:tests tests/unit/test_symbols.py::test_merge_into_reports_added_names
class MergeOutcome(BaseModel):
    """Names added, skipped (already present), or replaced by a merge/copy."""

    model_config = {}

    added: list[str] = []
    skipped: list[str] = []
    replaced: list[str] = []


def _rewrite_footprint(symbol: Node, lib_name: str) -> None:
    """Rewrite a symbol's `Footprint` property to `<lib_name>:FP` in place."""
    for prop in symbol.find_all("property"):
        atoms = prop.atoms()
        if len(atoms) < 2 or atoms[0] != "Footprint":
            continue
        fp = atoms[1]
        if not fp or ":" in fp:
            continue
        new_fp = Str(f"{lib_name}:{fp}")
        # atoms are the leading non-Node children of `prop.children`; replace
        # the first matching Footprint value atom in place.
        seen_head = False
        for i, child in enumerate(prop.children):
            if isinstance(child, Node):
                break
            if not seen_head:
                seen_head = True
                continue
            prop.children[i] = new_fp
            break


def _symbol_name(symbol: Node) -> str | None:
    """First atom of a `(symbol "NAME" ...)` form, or None if malformed."""
    atoms = symbol.atoms()
    return str(atoms[0]) if atoms else None


def _load_or_create_library(lib_path: Path) -> Result[Node, SymbolError]:
    """Parse the project library, or bootstrap a fresh one if it is missing."""
    if not lib_path.exists():
        _log.info("project library %s missing; starting a new one", lib_path)
        return Ok(parse(_EMPTY_LIB_HEADER).danger_ok)
    try:
        lib_text = lib_path.read_text(encoding="utf-8")
    except OSError:
        _log.exception("failed to read project library %s", lib_path)
        return Err(SymbolError.LibraryReadFailed)
    lib_parsed = parse(lib_text)
    if isinstance(lib_parsed, Err):
        _log.warning("project .kicad_sym did not parse: %s", lib_parsed)
        return Err(SymbolError.LibraryMalformed)
    lib_root = lib_parsed.danger_ok
    version_node = lib_root.find("version")
    if version_node is not None:
        _log.debug(
            "project library %s is format version %s", lib_path, version_node.atoms()
        )
    return Ok(lib_root)


# frob:doc docs/design/02-project-library-model.md#symbols
# frob:tests tests/unit/test_symbols.py::test_merge_into_reports_added_names
def merge_into(
    lib_path: Path, lib_name: str, vendor_text: str, overwrite: bool = False
) -> Result[MergeOutcome, SymbolError]:
    """Merge vendor symbols into the project's .kicad_sym, skipping duplicates."""
    vendor_parsed = parse(vendor_text)
    if isinstance(vendor_parsed, Err):
        _log.warning("vendor .kicad_sym did not parse: %s", vendor_parsed)
        return Err(SymbolError.VendorMalformed)
    vendor_root = vendor_parsed.danger_ok
    vendor_symbols = vendor_root.find_all("symbol")

    lib_loaded = _load_or_create_library(lib_path)
    if isinstance(lib_loaded, Err):
        return Err(lib_loaded.danger_err)
    lib_root = lib_loaded.danger_ok

    existing_by_name = {
        name: sym
        for sym in lib_root.find_all("symbol")
        if (name := _symbol_name(sym)) is not None
    }

    outcome = MergeOutcome()
    for vendor_symbol in vendor_symbols:
        name = _symbol_name(vendor_symbol)
        if name is None:
            continue
        _rewrite_footprint(vendor_symbol, lib_name)
        if name in existing_by_name:
            if not overwrite:
                _log.warning("symbol %s already exists in %s; skipping", name, lib_path)
                outcome.skipped.append(name)
                continue
            _log.info("symbol %s already exists in %s; replacing", name, lib_path)
            idx = lib_root.children.index(existing_by_name[name])
            lib_root.children[idx] = vendor_symbol
            existing_by_name[name] = vendor_symbol
            outcome.replaced.append(name)
        else:
            _log.info("adding symbol %s to %s", name, lib_path)
            lib_root.children.append(vendor_symbol)
            existing_by_name[name] = vendor_symbol
            outcome.added.append(name)

    write_result = _write_atomic(lib_path, dumps(lib_root))
    if isinstance(write_result, Err):
        return Err(write_result.danger_err)
    return Ok(outcome)


def _write_atomic(path: Path, text: str) -> Result[None, SymbolError]:
    """Write text to path via a same-dir temp file plus os.replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
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
        _log.exception("failed to write project library %s", path)
        return Err(SymbolError.LibraryWriteFailed)
    return Ok(None)
