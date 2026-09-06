"""Locate a KiCad project and derive its project-local library paths."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel
from typani import Err, Ok, Result

from kicad_libsync.errors import ProjectError
from kicad_libsync.logging import get_logger

_log = get_logger(__name__)


# frob:doc docs/design/02-project-library-model.md#project
# frob:tests tests/unit/test_project.py::test_locate_derives_paths_from_stem
# frob:waive WIRE001 reason="consumed by importer.py" follow_up="T-0006"
class KicadProject(BaseModel):
    """The project directory plus the derived project-local library paths."""

    model_config = {}

    root: Path
    name: str
    lib_name: str
    sym_lib: Path
    fp_lib: Path
    sym_table: Path
    fp_table: Path


# frob:doc docs/design/02-project-library-model.md#project
# frob:tests tests/unit/test_project.py::test_locate_derives_paths_from_stem
# frob:waive WIRE001 reason="consumed by importer.py" follow_up="T-0006"
def locate(
    path: Path, lib_name: str | None = None
) -> Result[KicadProject, ProjectError]:
    """Resolve a directory or .kicad_pro path into a KicadProject."""
    if not path.exists():
        _log.warning("project path missing: %s", path)
        return Err(ProjectError.ProjectPathMissing)

    if path.is_file():
        root = path.parent
        pro_file = path
    else:
        candidates = sorted(path.glob("*.kicad_pro"))
        if not candidates:
            _log.warning("no .kicad_pro found under %s", path)
            return Err(ProjectError.NotAProject)
        if len(candidates) > 1:
            _log.warning(
                "ambiguous project: %d .kicad_pro under %s", len(candidates), path
            )
            return Err(ProjectError.AmbiguousProject)
        root = path
        pro_file = candidates[0]

    name = pro_file.stem
    resolved_lib_name = lib_name if lib_name is not None else name
    project = KicadProject(
        root=root,
        name=name,
        lib_name=resolved_lib_name,
        sym_lib=root / f"{resolved_lib_name}.kicad_sym",
        fp_lib=root / f"{resolved_lib_name}.pretty",
        sym_table=root / "sym-lib-table",
        fp_table=root / "fp-lib-table",
    )
    _log.info("located project %r at %s (lib_name=%s)", name, root, resolved_lib_name)
    return Ok(project)
