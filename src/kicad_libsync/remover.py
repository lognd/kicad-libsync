"""Remove a symbol (and its orphaned footprint) from the project library."""

from __future__ import annotations

from pydantic import BaseModel
from typani import Err, Ok, Result

from kicad_libsync import footprints, symbols
from kicad_libsync.errors import FootprintError, SymbolError
from kicad_libsync.logging import get_logger
from kicad_libsync.project import KicadProject
from kicad_libsync.sexpr import Node, parse

_log = get_logger(__name__)

# frob:doc docs/design/02-project-library-model.md#remover
# frob:tests tests/unit/test_remover.py::test_remove_symbols_reports_removed_names
RemoveError_ = SymbolError | FootprintError


# frob:doc docs/design/02-project-library-model.md#remover
# frob:tests tests/unit/test_remover.py::test_remove_symbols_reports_removed_names
class RemoveReport(BaseModel):
    """What a single `remove` invocation dropped from the project library."""

    model_config = {}

    removed_symbols: list[str] = []
    removed_footprints: list[str] = []
    missing: list[str] = []

    # frob:doc docs/design/02-project-library-model.md#remover
    # frob:tests tests/unit/test_remover.py::test_remove_symbols_reports_removed_names
    def summary(self) -> str:
        """One human-readable line summarizing what this removal changed."""
        parts: list[str] = []
        if self.removed_symbols:
            parts.append(f"-{len(self.removed_symbols)} symbol")
        if self.removed_footprints:
            parts.append(f"-{len(self.removed_footprints)} footprints")
        if self.missing:
            parts.append(f"{len(self.missing)} not found")
        if not parts:
            parts.append("nothing removed")
        return f"remove: {', '.join(parts)}"


def _find_schematics_using(
    project: KicadProject, lib_name: str, names: list[str]
) -> str | None:
    """Scan every *.kicad_sch under project.root for a `(lib_id "lib:NAME")` use.

    Returns the path of the first schematic found referencing any of
    `names`, or None if none do.
    """
    wanted = {f"{lib_name}:{name}" for name in names}
    for sch_path in sorted(project.root.rglob("*.kicad_sch")):
        try:
            text = sch_path.read_text(encoding="utf-8")
        except OSError:
            _log.exception("failed to read schematic %s while checking usage", sch_path)
            continue
        parsed = parse(text)
        if isinstance(parsed, Err):
            _log.debug("schematic %s did not parse; skipping usage scan", sch_path)
            continue
        root = parsed.danger_ok
        for lib_id in _find_lib_ids(root):
            if lib_id in wanted:
                _log.warning("symbol %s is placed in schematic %s", lib_id, sch_path)
                return str(sch_path)
    return None


def _find_lib_ids(node: Node) -> list[str]:
    """Recursively collect every `(lib_id "...")` value under node."""
    found: list[str] = []
    lib_id_node = node.find("lib_id")
    if lib_id_node is not None:
        atoms = lib_id_node.atoms()
        if atoms:
            found.append(str(atoms[0]))
    for child in node.subforms():
        # frob:invariant terminates reason="tree depth shrinks" measure="depth(child)"
        found.extend(_find_lib_ids(child))
    return found


# frob:doc docs/design/02-project-library-model.md#remover
# frob:tests tests/unit/test_remover.py::test_remove_symbols_reports_removed_names
def remove_symbols(
    project: KicadProject,
    names: list[str],
    keep_footprints: bool = False,
    force: bool = False,
) -> Result[RemoveReport, RemoveError_]:
    """Delete named symbols from the project library and their orphaned footprints."""
    _log.info("removing %s from project %s", names, project.name)

    if not force:
        in_use = _find_schematics_using(project, project.lib_name, names)
        if in_use is not None:
            return Err(SymbolError.SymbolInUse).note(f"placed in {in_use}")

    removed_result = symbols.remove_from(project.sym_lib, names)
    if isinstance(removed_result, Err):
        return Err(removed_result.danger_err)
    removed, missing, footprint_refs = removed_result.danger_ok
    _log.info("removed symbols: %s (missing: %s)", removed, missing)

    removed_footprints: list[str] = []
    if not keep_footprints and footprint_refs:
        still_referenced_result = symbols.footprints_still_referenced(project.sym_lib)
        if isinstance(still_referenced_result, Err):
            return Err(still_referenced_result.danger_err)
        still_referenced = still_referenced_result.danger_ok
        orphans_result = footprints.remove_orphans(
            project.fp_lib, sorted(set(footprint_refs)), still_referenced
        )
        if isinstance(orphans_result, Err):
            return Err(orphans_result.danger_err)
        removed_footprints = orphans_result.danger_ok
        _log.info("removed orphaned footprints: %s", removed_footprints)

    return Ok(
        RemoveReport(
            removed_symbols=removed,
            removed_footprints=removed_footprints,
            missing=missing,
        )
    )
