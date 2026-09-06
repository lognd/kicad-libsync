"""Poll a Downloads directory for new, stable vendor zips and import them."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from pathlib import Path

from typani import Err
from typani.unreachable import Unreachable

from kicad_libsync import archive, state
from kicad_libsync.archive import ArchiveError
from kicad_libsync.importer import ImportReport, import_zip
from kicad_libsync.logging import get_logger
from kicad_libsync.project import KicadProject

_log = get_logger(__name__)

_NOT_A_LIBRARY = (ArchiveError.NoSymbolLibrary, ArchiveError.NoFootprints)


# frob:doc docs/design/03-watcher.md#watcher
# frob:tests tests/unit/test_watcher.py::test_zip_is_imported_once_after_it_stabilizes
class Watcher:
    """Polling loop: new+stable zips in Downloads get hashed, checked, imported."""

    def __init__(
        self,
        downloads: Path,
        project: KicadProject,
        state_path: Path,
        overwrite: bool = False,
        backfill: bool = False,
    ) -> None:
        """Bind the Downloads dir, target project, and state file for this loop."""
        self.downloads = downloads
        self.project = project
        self.state_path = state_path
        self.overwrite = overwrite
        self.backfill = backfill
        self.pending: dict[str, tuple[int, float]] = {}
        self.seen: set[str] = set()
        self.ignored: set[str] = set()

    # frob:doc docs/design/03-watcher.md#watcher
    # frob:tests tests/unit/test_watcher.py::test_backfill_imports_pre_existing_zips
    def prime(self) -> None:
        """Mark pre-existing zips as already seen, unless backfill is requested."""
        if self.backfill:
            _log.info("backfill requested; existing zips will be processed")
            return
        for candidate in sorted(self.downloads.glob("*.zip")):
            _log.info("priming: treating pre-existing zip %s as seen", candidate.name)
            self.seen.add(candidate.name)

    # frob:doc docs/design/03-watcher.md#watcher
    # frob:tests tests/unit/test_watcher.py::test_unstable_file_is_not_imported
    def poll_once(self) -> list[ImportReport]:
        """Run one poll: find new zips, check stability, import stable ones."""
        reports: list[ImportReport] = []
        for candidate in sorted(self.downloads.glob("*.zip")):
            name = candidate.name
            if name.startswith("~") or name.endswith((".crdownload", ".part")):
                continue
            if name in self.seen or name in self.ignored:
                continue

            try:
                stat = candidate.stat()
            except OSError:
                _log.warning("could not stat %s; skipping this poll", name)
                continue
            fingerprint = (stat.st_size, stat.st_mtime)

            previous = self.pending.get(name)
            if previous is None:
                _log.info("new candidate zip: %s", name)
                self.pending[name] = fingerprint
                continue
            if previous != fingerprint:
                _log.debug("%s still changing; not stable yet", name)
                self.pending[name] = fingerprint
                continue

            _log.info("%s is stable; hashing", name)
            report = self._process_stable(candidate)
            if report is not None:
                reports.append(report)

        return reports

    def _process_stable(self, candidate: Path) -> ImportReport | None:
        """Hash, dedupe against state, inspect, and import one stable zip."""
        name = candidate.name
        self.seen.add(name)
        self.pending.pop(name, None)

        hash_result = state.sha256_of(candidate)
        if isinstance(hash_result, Err):
            _log.error("failed to hash %s: %s", name, hash_result.danger_err)
            return None
        digest = hash_result.danger_ok

        loaded = state.load(self.state_path)
        if isinstance(loaded, Err):
            _log.error(
                "failed to load processed-state for %s: %s",
                name,
                loaded.danger_err,
            )
            return None
        processed = loaded.danger_ok

        state_key = state.key(digest, self.project.root)
        if processed.contains(state_key):
            _log.info("%s already processed for %s; skipping", name, self.project.name)
            return None

        inspected = archive.inspect(candidate)
        if isinstance(inspected, Err):
            if inspected.danger_err in _NOT_A_LIBRARY:
                _log.debug("%s is not a library zip: %s", name, inspected.danger_err)
                self.ignored.add(name)
            else:
                _log.error("failed to inspect %s: %s", name, inspected.danger_err)
            return None

        imported = import_zip(self.project, candidate, self.overwrite)
        if isinstance(imported, Err):
            _log.error("failed to import %s: %s", name, imported.danger_err)
            return None
        report = imported.danger_ok

        processed.record(state_key, f"{name} @ now -> {self.project.root}")
        saved = state.save(self.state_path, processed)
        if isinstance(saved, Err):
            _log.error(
                "failed to save processed-state after importing %s: %s",
                name,
                saved.danger_err,
            )
            return None

        return report

    # frob:doc docs/design/03-watcher.md#watcher
    # frob:tests tests/integration/test_watcher_state.py::test_run_imports_two_fixtures
    async def run(
        self,
        poll_seconds: float,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> Unreachable:
        """Prime once, then poll and sleep forever, logging each report summary."""
        self.prime()
        while True:
            for report in self.poll_once():
                _log.info(report.summary())
            await sleep(poll_seconds)
        return Unreachable()  # pragma: no cover
