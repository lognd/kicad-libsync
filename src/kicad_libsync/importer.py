"""Orchestrate a vendor package into a project's libraries and lib tables."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel
from typani import Ok, Result, propagate

from kicad_libsync import archive, footprints, libtable, symbols
from kicad_libsync.archive import VendorPackage
from kicad_libsync.errors import (
    ArchiveError,
    FootprintError,
    LibTableError,
    SymbolError,
)
from kicad_libsync.logging import get_logger
from kicad_libsync.project import KicadProject
from kicad_libsync.symbols import MergeOutcome

_log = get_logger(__name__)


# frob:doc docs/design/02-project-library-model.md#importer
# frob:tests tests/integration/test_importer.py::test_import_twice_skips_everything
# Trailing underscore avoids shadowing the builtin ImportError.
ImportError_ = ArchiveError | SymbolError | FootprintError | LibTableError


# frob:doc docs/design/02-project-library-model.md#importer
# frob:tests tests/unit/test_importer.py::test_summary_reports_added_counts
class ImportReport(BaseModel):
    """Everything a single import wrote into the project: outcomes and table edits."""

    model_config = {}

    source: Path
    symbols: MergeOutcome
    footprints: MergeOutcome
    sym_table_added: bool
    fp_table_added: bool

    # frob:doc docs/design/02-project-library-model.md#importer
    # frob:tests tests/unit/test_importer.py::test_summary_reports_added_counts
    def summary(self) -> str:
        """One human-readable line summarizing what this import changed."""
        parts: list[str] = []
        if self.symbols.added:
            parts.append(f"+{len(self.symbols.added)} symbol")
        if self.footprints.added:
            parts.append(f"+{len(self.footprints.added)} footprints")
        if self.sym_table_added:
            parts.append("sym-lib-table registered")
        if self.fp_table_added:
            parts.append("fp-lib-table registered")
        if not parts:
            parts.append("nothing added")
        return f"{self.source.name}: {', '.join(parts)}"


# frob:doc docs/design/02-project-library-model.md#importer
# frob:tests tests/integration/test_importer.py::test_import_twice_skips_everything
@propagate
def import_package(
    project: KicadProject, pkg: VendorPackage, overwrite: bool = False
) -> Result[ImportReport, ImportError_]:
    """Copy footprints, merge symbols, then register both libraries in the tables."""
    _log.info("importing %s into project %s", pkg.source, project.name)

    fp_outcome = (
        footprints.copy_into(project.fp_lib, pkg.footprints, overwrite)
        .note(f"while copying footprints from {pkg.source}")
        .unwrap()
    )
    _log.info(
        "footprints: +%d/-%d/~%d",
        len(fp_outcome.added),
        len(fp_outcome.skipped),
        len(fp_outcome.replaced),
    )

    sym_outcome = (
        symbols.merge_into(
            project.sym_lib, project.lib_name, pkg.symbols_text, overwrite
        )
        .note(f"while merging symbols from {pkg.source}")
        .unwrap()
    )
    _log.info(
        "symbols: +%d/-%d/~%d",
        len(sym_outcome.added),
        len(sym_outcome.skipped),
        len(sym_outcome.replaced),
    )

    sym_table_added = (
        libtable.ensure_entry(
            project.sym_table,
            "sym",
            project.lib_name,
            f"${{KIPRJMOD}}/{project.lib_name}.kicad_sym",
        )
        .note(f"while registering {project.lib_name} in {project.sym_table}")
        .unwrap()
    )
    _log.info("sym-lib-table entry added: %s", sym_table_added)

    fp_table_added = (
        libtable.ensure_entry(
            project.fp_table,
            "fp",
            project.lib_name,
            f"${{KIPRJMOD}}/{project.lib_name}.pretty",
        )
        .note(f"while registering {project.lib_name} in {project.fp_table}")
        .unwrap()
    )
    _log.info("fp-lib-table entry added: %s", fp_table_added)

    return Ok(
        ImportReport(
            source=pkg.source,
            symbols=sym_outcome,
            footprints=fp_outcome,
            sym_table_added=sym_table_added,
            fp_table_added=fp_table_added,
        )
    )


# frob:doc docs/design/02-project-library-model.md#importer
# frob:tests tests/integration/test_importer.py::test_import_twice_skips_everything
@propagate
def import_zip(
    project: KicadProject, zip_path: Path, overwrite: bool = False
) -> Result[ImportReport, ImportError_]:
    """Inspect zip_path as a vendor package and import it into the project."""
    pkg = archive.inspect(zip_path).note(f"while inspecting {zip_path}").unwrap()
    return Ok(import_package(project, pkg, overwrite).unwrap())
