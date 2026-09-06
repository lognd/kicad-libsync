"""Read and edit sym-lib-table / fp-lib-table entries, writing atomically."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from typani import Err, Ok, Result

from kicad_libsync.errors import LibTableError
from kicad_libsync.logging import get_logger
from kicad_libsync.sexpr import Node, Str, dumps, parse

_log = get_logger(__name__)

_TABLE_HEAD = {"sym": "sym_lib_table", "fp": "fp_lib_table"}


def _table_head(kind: Literal["sym", "fp"]) -> str:
    """Return the top-level form head for the given table kind."""
    return _TABLE_HEAD[kind]


def _load_or_create(
    table_path: Path, kind: Literal["sym", "fp"]
) -> Result[Node, LibTableError]:
    """Parse an existing table file, or build an empty one when missing."""
    if not table_path.exists():
        _log.info("no %s at %s; will create on write", _table_head(kind), table_path)
        return Ok(Node(_table_head(kind), [Node("version", ["7"])]))
    read = Result.catch(
        lambda: table_path.read_text(encoding="utf-8"),
        OSError,
        on_error=lambda exc: LibTableError.TableReadFailed,
    )
    if isinstance(read, Err):
        _log.error("failed to read %s: %s", table_path, read)
        return Err(read.danger_err)
    parsed = parse(read.danger_ok)
    if isinstance(parsed, Err):
        _log.error("failed to parse %s: %s", table_path, parsed)
        return Err(LibTableError.TableMalformed)
    root = parsed.danger_ok
    if root.head != _table_head(kind):
        _log.error("%s has unexpected head %r", table_path, root.head)
        return Err(LibTableError.TableMalformed)
    return Ok(root)


def _write_atomic(table_path: Path, root: Node) -> Result[None, LibTableError]:
    """Write the table's s-expression text via a same-dir temp file + replace."""
    tmp_path = table_path.with_name(f".{table_path.name}.tmp")

    def _write() -> None:
        tmp_path.write_text(dumps(root), encoding="utf-8")
        os.replace(tmp_path, table_path)

    written = Result.catch(
        _write, OSError, on_error=lambda exc: LibTableError.TableWriteFailed
    )
    if isinstance(written, Err):
        _log.error("failed to write %s: %s", table_path, written)
        return Err(written.danger_err)
    return Ok(None)


# frob:doc docs/design/02-project-library-model.md#libtable
# frob:tests tests/unit/test_libtable.py::test_ensure_entry_creates_missing_table
# frob:waive WIRE001 reason="consumed by importer.py" follow_up="T-0006"
def ensure_entry(
    table_path: Path, kind: Literal["sym", "fp"], lib_name: str, uri: str
) -> Result[bool, LibTableError]:
    """Add a (lib ...) entry for lib_name/uri unless the name is already there."""
    loaded = _load_or_create(table_path, kind)
    if isinstance(loaded, Err):
        return Err(loaded.danger_err)
    root = loaded.danger_ok

    for lib in root.find_all("lib"):
        name_form = lib.find("name")
        if name_form is None:
            continue
        existing_name = name_form.atoms()[0] if name_form.atoms() else None
        if existing_name == lib_name:
            uri_form = lib.find("uri")
            existing_uri = (
                uri_form.atoms()[0] if uri_form and uri_form.atoms() else None
            )
            if existing_uri != uri:
                _log.warning(
                    "lib %r already registered in %s with a different uri "
                    "(%r != %r); leaving it alone",
                    lib_name,
                    table_path,
                    existing_uri,
                    uri,
                )
            else:
                _log.info("lib %r already registered in %s", lib_name, table_path)
            return Ok(False)

    entry = Node(
        "lib",
        [
            Node("name", [Str(lib_name)]),
            Node("type", [Str("KiCad")]),
            Node("uri", [Str(uri)]),
            Node("options", [Str("")]),
            Node("descr", [Str("")]),
        ],
    )
    root.children.append(entry)
    written = _write_atomic(table_path, root)
    if isinstance(written, Err):
        return Err(written.danger_err)
    _log.info("registered lib %r (%s) in %s", lib_name, uri, table_path)
    return Ok(True)


# frob:doc docs/design/02-project-library-model.md#libtable
# frob:tests tests/unit/test_libtable.py::test_entries_returns_name_uri_pairs
# frob:waive WIRE001 reason="consumed by status subcommand" follow_up="T-0008"
def entries(table_path: Path) -> Result[list[tuple[str, str]], LibTableError]:
    """Return the (name, uri) pairs registered in a lib table."""
    kind: Literal["sym", "fp"] = "sym" if "sym" in table_path.name else "fp"
    loaded = _load_or_create(table_path, kind)
    if isinstance(loaded, Err):
        return Err(loaded.danger_err)
    root = loaded.danger_ok
    pairs: list[tuple[str, str]] = []
    for lib in root.find_all("lib"):
        name_form = lib.find("name")
        uri_form = lib.find("uri")
        if name_form and name_form.atoms() and uri_form and uri_form.atoms():
            pairs.append((str(name_form.atoms()[0]), str(uri_form.atoms()[0])))
    return Ok(pairs)
