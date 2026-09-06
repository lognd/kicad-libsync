"""CLI entry point: argparse -> AppConfig.from_external -> App."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv
from typani import Err

from kicad_libsync.app import App, AppConfig
from kicad_libsync.logging import get_logger

_log = get_logger(__name__)

# frob:tests tests/system/test_cli.py::test_import_end_to_end kind="e2e"


# frob:tests tests/unit/test_main.py::test_parser_builds_watch_import_status
def _build_parser() -> argparse.ArgumentParser:
    """Build the watch/import/status subcommand parser tree."""
    p = argparse.ArgumentParser(prog="kicad-libsync")
    sub = p.add_subparsers(dest="command", required=True)

    watch = sub.add_parser("watch", help="poll Downloads and import new vendor zips")
    watch.add_argument("--project", type=Path, default=Path("."))
    watch.add_argument("--downloads", type=Path, default=None)
    watch.add_argument("--lib-name", dest="lib_name", default=None)
    watch.add_argument("--poll", dest="poll_seconds", type=float, default=None)
    watch.add_argument("--backfill", action="store_true", default=None)
    watch.add_argument("--overwrite", action="store_true", default=None)

    imp = sub.add_parser("import", help="import one or more vendor zips")
    imp.add_argument("--project", type=Path, default=Path("."))
    imp.add_argument("--lib-name", dest="lib_name", default=None)
    imp.add_argument("--overwrite", action="store_true", default=None)
    imp.add_argument("zips", metavar="ZIP", type=Path, nargs="+")

    status = sub.add_parser("status", help="show project libraries and table state")
    status.add_argument("--project", type=Path, default=Path("."))

    return p


# frob:doc docs/index.md#public-api
def main() -> None:
    """Parse argv, resolve AppConfig, and run App(); exit 2 on a config error."""
    load_dotenv()
    args = _build_parser().parse_args()
    result = AppConfig.from_external(args)
    if isinstance(result, Err):
        _log.error("configuration error: %s", result)
        sys.exit(2)
    sys.exit(App(result.danger_ok)())


if __name__ == "__main__":
    main()
