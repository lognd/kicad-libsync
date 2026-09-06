"""The App: dispatches a resolved AppConfig to watch/import/status behavior."""

from __future__ import annotations

import asyncio

from typani import Err, Ok

from kicad_libsync import libtable, project, state
from kicad_libsync.app.config import AppConfig
from kicad_libsync.importer import import_zip
from kicad_libsync.logging import get_logger
from kicad_libsync.watcher import Watcher

_log = get_logger(__name__)


# frob:doc docs/index.md#public-api
class App:
    """Bind a resolved AppConfig and run its command when called."""

    def __init__(self, cfg: AppConfig) -> None:
        """Store cfg for the eventual __call__ dispatch."""
        self._cfg = cfg

    # frob:tests tests/unit/test_app.py::test_app_status_reports_project_state
    def __call__(self) -> int:
        """Dispatch on cfg.command; return the process exit code."""
        cfg = self._cfg
        if cfg.command == "watch":
            return self._run_watch()
        if cfg.command == "import":
            return self._run_import()
        return self._run_status()

    def _run_watch(self) -> int:
        """Locate the project, load state, and poll Downloads until interrupted."""
        cfg = self._cfg
        located = project.locate(cfg.project, cfg.lib_name)
        if isinstance(located, Err):
            _log.error("could not locate project: %s", located)
            return 1
        proj = located.danger_ok

        assert (
            cfg.downloads is not None
        )  # ConfigError.NoDownloadsDir already gated this
        state_file = state.state_path()
        loaded = state.load(state_file)
        if isinstance(loaded, Err):
            _log.error("could not load processed-state: %s", loaded)
            return 1

        watcher = Watcher(
            cfg.downloads,
            proj,
            state_file,
            overwrite=cfg.overwrite,
            backfill=cfg.backfill,
        )
        try:
            asyncio.run(watcher.run(cfg.poll_seconds))
        except KeyboardInterrupt:
            _log.info("stopped")
            return 0
        return 0  # pragma: no cover -- watcher.run never returns normally

    def _run_import(self) -> int:
        """Import each configured zip into the project; nonzero exit on any failure."""
        cfg = self._cfg
        located = project.locate(cfg.project, cfg.lib_name)
        if isinstance(located, Err):
            _log.error("could not locate project: %s", located)
            return 1
        proj = located.danger_ok

        failed = False
        for zip_path in cfg.zips:
            result = import_zip(proj, zip_path, overwrite=cfg.overwrite)
            if isinstance(result, Ok):
                _log.info(result.danger_ok.summary())
            else:
                _log.error(str(result))
                failed = True
        return 1 if failed else 0

    def _run_status(self) -> int:
        """Log the project's libraries, table entries, and processed-state count."""
        cfg = self._cfg
        located = project.locate(cfg.project, cfg.lib_name)
        if isinstance(located, Err):
            _log.error("could not locate project: %s", located)
            return 1
        proj = located.danger_ok

        _log.info("project root: %s", proj.root)
        _log.info("library name: %s", proj.lib_name)
        _log.info("sym lib exists: %s", proj.sym_lib.exists())
        _log.info("fp lib exists: %s", proj.fp_lib.exists())

        sym_entries = libtable.entries(proj.sym_table)
        _log.info(
            "sym-lib-table entries: %s",
            sym_entries.danger_ok if isinstance(sym_entries, Ok) else sym_entries,
        )
        fp_entries = libtable.entries(proj.fp_table)
        _log.info(
            "fp-lib-table entries: %s",
            fp_entries.danger_ok if isinstance(fp_entries, Ok) else fp_entries,
        )

        loaded = state.load(state.state_path())
        if isinstance(loaded, Ok):
            _log.info("processed-state keys: %d", len(loaded.danger_ok.hashes))
        else:
            _log.error("could not load processed-state: %s", loaded)

        return 0
