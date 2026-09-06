"""Recognize Ultra Librarian and SnapMagic vendor zip exports as a VendorPackage."""

from __future__ import annotations

import zipfile
from pathlib import Path, PurePosixPath

from pydantic import BaseModel
from typani import Err, Ok, Result

from kicad_libsync.errors import ArchiveError
from kicad_libsync.logging import get_logger

_log = get_logger(__name__)


# frob:doc docs/design/01-vendor-zip-format.md#vendorpackage
# frob:tests tests/unit/test_archive.py::test_inspect_valid_zip_two_footprints
class VendorPackage(BaseModel):
    """The pieces of a recognized vendor export: a symbol library and its footprints."""

    model_config = {}
    source: Path
    symbols_text: str
    footprints: dict[str, str]
    models: dict[str, bytes] = {}


def _is_unsafe(name: str) -> bool:
    """Whether a zip member name is absolute or escapes its extraction root."""
    pure = PurePosixPath(name)
    return pure.is_absolute() or ".." in pure.parts


# frob:doc docs/design/01-vendor-zip-format.md#inspect
# frob:tests tests/unit/test_archive.py::test_inspect_valid_zip_two_footprints
# frob:boundary b_archive_inspect
def inspect(zip_path: Path) -> Result[VendorPackage, ArchiveError]:
    """Recognize an Ultra Librarian or SnapMagic export in zip_path, in memory."""
    try:
        zf = zipfile.ZipFile(zip_path)
    except (zipfile.BadZipFile, OSError) as exc:
        _log.warning("archive %s is not a readable zip: %s", zip_path, exc)
        return Err(ArchiveError.NotAZip)

    with zf:
        names = zf.namelist()

        unsafe = [n for n in names if _is_unsafe(n)]
        if unsafe:
            _log.warning("archive %s has unsafe member paths: %s", zip_path, unsafe)
            return Err(ArchiveError.UnsafePath)

        sym_names = [n for n in names if n.endswith(".kicad_sym")]
        if len(sym_names) == 0:
            _log.debug("archive %s has no .kicad_sym; not a vendor library", zip_path)
            return Err(ArchiveError.NoSymbolLibrary)
        if len(sym_names) > 1:
            _log.warning(
                "archive %s has ambiguous symbol libraries: %s", zip_path, sym_names
            )
            return Err(ArchiveError.AmbiguousSymbolLibrary)

        # Ultra Librarian nests footprints under a .pretty dir; SnapMagic puts
        # them at the zip root. Location does not matter, only the extension.
        mod_names = [n for n in names if n.endswith(".kicad_mod")]
        if len(mod_names) == 0:
            _log.debug("archive %s has no .kicad_mod members", zip_path)
            return Err(ArchiveError.NoFootprints)

        decoded = _read_utf8_members(zf, zip_path, [sym_names[0], *mod_names])
        if isinstance(decoded, Err):
            return Err(decoded.danger_err)
        texts = decoded.danger_ok

        symbols_text = texts[sym_names[0]]
        footprints = {PurePosixPath(n).stem: texts[n] for n in mod_names}

    _log.debug(
        "archive %s recognized: 1 symbol library, %d footprints",
        zip_path,
        len(footprints),
    )
    return Ok(
        VendorPackage(source=zip_path, symbols_text=symbols_text, footprints=footprints)
    )


def _read_utf8_members(
    zf: zipfile.ZipFile, zip_path: Path, names: list[str]
) -> Result[dict[str, str], ArchiveError]:
    """Read and UTF-8 decode each named member from an open zip, in memory only."""
    texts: dict[str, str] = {}
    for name in names:
        try:
            raw = zf.read(name)
        except (KeyError, zipfile.BadZipFile, OSError) as exc:
            _log.warning("failed to read %s from %s: %s", name, zip_path, exc)
            return Err(ArchiveError.MemberReadFailed)
        try:
            texts[name] = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            _log.warning("member %s in %s is not utf-8: %s", name, zip_path, exc)
            return Err(ArchiveError.NotUtf8)
    return Ok(texts)
