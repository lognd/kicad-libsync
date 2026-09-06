"""Layered configuration for the CLI: CLI > env > config file > detection."""

from __future__ import annotations

import argparse
import os
import tomllib
from pathlib import Path
from typing import Literal

from pydantic import BaseModel
from typani import Err, Nothing, Ok, Option, Result, Some

from kicad_libsync.errors import ConfigError
from kicad_libsync.logging import get_logger

_log = get_logger(__name__)


_DEFAULT_CONFIG_FILE = Path.home() / ".config" / "kicad-libsync" / "config.toml"

_EXCLUDED_USER_DIRS = frozenset(
    {"Public", "Default", "Default User", "All Users", "WsiAccount"}
)

# frob:doc docs/design/04-cli-and-config.md#appconfig
# frob:tests tests/unit/test_main.py::test_parser_builds_watch_import_status
# The AppConfig fields this project's own CLI-forwarding layer copies from a
# parsed argparse.Namespace. Named explicitly (rather than defaulting to
# frob's own guess) so FLAGCOV001 measures real drops in THIS project.
FORWARDED_FIELD_NAMES = frozenset(
    {
        "command",
        "project",
        "downloads",
        "lib_name",
        "poll_seconds",
        "backfill",
        "overwrite",
        "zips",
    }
)


# frob:doc docs/index.md#public-api
# frob:tests tests/unit/test_app.py::test_detect_downloads_excludes_system_users
def detect_downloads(users_root: Path = Path("/mnt/c/Users")) -> Option[Path]:
    """Find the single WSL-visible Windows Downloads dir, else ~/Downloads."""
    if users_root.is_dir():
        candidates = [
            p / "Downloads"
            for p in sorted(users_root.iterdir())
            if p.is_dir()
            and p.name not in _EXCLUDED_USER_DIRS
            and (p / "Downloads").is_dir()
        ]
        if len(candidates) == 1:
            return Some(candidates[0])
        if len(candidates) > 1:
            _log.warning(
                "multiple candidate Downloads dirs under %s; not guessing", users_root
            )

    home_downloads = Path.home() / "Downloads"
    if home_downloads.is_dir():
        return Some(home_downloads)

    return Nothing()


# frob:doc docs/index.md#public-api
class AppConfig(BaseModel):
    """One CLI invocation's resolved settings, layered CLI/env/file/detection."""

    model_config = {}

    command: Literal["watch", "import", "status"] = "watch"
    project: Path = Path(".")
    downloads: Path | None = None
    lib_name: str | None = None
    poll_seconds: float = 2.0
    backfill: bool = False
    overwrite: bool = False
    zips: list[Path] = []

    @classmethod
    # frob:doc docs/index.md#public-api
    # frob:tests tests/unit/test_app.py::test_cli_overrides_env_overrides_file
    def from_external(
        cls, args: argparse.Namespace, config_file: Path | None = None
    ) -> Result[AppConfig, ConfigError]:
        """Layer CLI args over env vars over the config file over detection."""
        resolved_file = config_file if config_file is not None else _DEFAULT_CONFIG_FILE

        file_cfg: dict = {}
        if resolved_file.exists():
            try:
                with resolved_file.open("rb") as f:
                    data = tomllib.load(f)
            except tomllib.TOMLDecodeError:
                _log.error("config file %s did not parse as TOML", resolved_file)
                return Err(ConfigError.BadConfigFile)
            for key in ("downloads", "project", "lib_name", "poll_seconds"):
                if key in data:
                    file_cfg[key] = data[key]

        env_cfg: dict = {}
        if (v := os.environ.get("KICAD_LIBSYNC_DOWNLOADS")) is not None:
            env_cfg["downloads"] = v
        if (v := os.environ.get("KICAD_LIBSYNC_PROJECT")) is not None:
            env_cfg["project"] = v
        if (v := os.environ.get("KICAD_LIBSYNC_POLL")) is not None:
            env_cfg["poll_seconds"] = v

        cli_cfg: dict = {}
        for field in FORWARDED_FIELD_NAMES:
            # frob:waive OPAQUE001 reason="field is our own fixed set"
            value = getattr(args, field, None)
            if value is not None:
                cli_cfg[field] = value

        merged: dict = {**file_cfg, **env_cfg, **cli_cfg}

        if "downloads" not in merged or merged["downloads"] is None:
            command = merged.get("command", "watch")
            detected = detect_downloads()
            if isinstance(detected, Some):
                merged["downloads"] = detected.danger_some
            elif command == "watch":
                _log.error("no Downloads directory given and none could be detected")
                return Err(ConfigError.NoDownloadsDir)

        cfg = cls(**merged)

        if cfg.poll_seconds <= 0:
            _log.error("poll interval must be positive, got %s", cfg.poll_seconds)
            return Err(ConfigError.BadPoll)

        if cfg.downloads is not None:
            _log.info("resolved downloads directory: %s", cfg.downloads)

        return Ok(cfg)
