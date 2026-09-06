"""Unit tests for the App/AppConfig wiring."""

import argparse
from pathlib import Path

import pytest
from typani import Err, Nothing, Ok

import kicad_libsync.app.config as config_module
from kicad_libsync.app import App, AppConfig
from kicad_libsync.app.config import detect_downloads
from kicad_libsync.errors import ConfigError


def _ns(**kwargs) -> argparse.Namespace:
    base = dict(
        command="watch",
        project=None,
        downloads=None,
        lib_name=None,
        poll_seconds=None,
        backfill=None,
        overwrite=None,
        zips=None,
    )
    base.update(kwargs)
    return argparse.Namespace(**base)


def test_app_config_from_external_with_no_config_file(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/app/config.py::AppConfig.from_external kind="unit"
    result = AppConfig.from_external(
        _ns(downloads=str(tmp_path)), config_file=tmp_path / "missing.toml"
    )
    assert isinstance(result, Ok)
    assert isinstance(result.danger_ok, AppConfig)


def test_app_is_callable(tmp_path: Path) -> None:
    (tmp_path / "demo.kicad_pro").write_text("{}", encoding="utf-8")
    assert App(AppConfig(command="status", project=tmp_path))() == 0


def test_bad_poll_is_a_config_error(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/app/config.py::AppConfig.from_external kind="unit"
    result = AppConfig.from_external(
        _ns(downloads=str(tmp_path), poll_seconds=-1.0),
        config_file=tmp_path / "missing.toml",
    )
    assert isinstance(result, Err)
    assert result.danger_err is ConfigError.BadPoll


def test_no_downloads_dir_is_a_config_error_for_watch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/kicad_libsync/app/config.py::AppConfig.from_external kind="unit"
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "no-home-downloads-here")
    monkeypatch.setattr(config_module, "detect_downloads", lambda: Nothing())
    result = AppConfig.from_external(
        _ns(command="watch"), config_file=tmp_path / "missing.toml"
    )
    assert isinstance(result, Err)
    assert result.danger_err is ConfigError.NoDownloadsDir


def test_detect_downloads_excludes_system_users(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/app/config.py::detect_downloads kind="unit"
    users_root = tmp_path / "Users"
    for name in ("Public", "Default", "alice"):
        (users_root / name / "Downloads").mkdir(parents=True)
    result = detect_downloads(users_root)
    assert result.is_some
    assert result.danger_some == users_root / "alice" / "Downloads"


def test_detect_downloads_is_nothing_when_absent(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/app/config.py::detect_downloads kind="unit"
    result = detect_downloads(tmp_path / "does-not-exist")
    assert result.is_nothing


def test_cli_overrides_env_overrides_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/kicad_libsync/app/config.py::AppConfig.from_external kind="unit"
    config_file = tmp_path / "config.toml"
    config_file.write_text(
        'downloads = "/from/file"\npoll_seconds = 9.0\n', encoding="utf-8"
    )
    monkeypatch.setenv("KICAD_LIBSYNC_DOWNLOADS", "/from/env")
    monkeypatch.setenv("KICAD_LIBSYNC_POLL", "5.0")

    result = AppConfig.from_external(
        _ns(downloads=str(tmp_path), command="status"), config_file=config_file
    )
    assert isinstance(result, Ok)
    # CLI wins over env, which wins over file
    assert result.danger_ok.downloads == tmp_path


def test_bad_config_file_is_a_config_error(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/app/config.py::AppConfig.from_external kind="unit"
    config_file = tmp_path / "config.toml"
    config_file.write_text("not [ valid toml", encoding="utf-8")
    result = AppConfig.from_external(
        _ns(downloads=str(tmp_path), command="status"), config_file=config_file
    )
    assert isinstance(result, Err)
    assert result.danger_err is ConfigError.BadConfigFile


def test_app_status_reports_project_state(tmp_path: Path, caplog) -> None:
    # frob:tests src/kicad_libsync/app/app.py::App.__call__ kind="unit"
    (tmp_path / "demo.kicad_pro").write_text("{}", encoding="utf-8")
    cfg = AppConfig(command="status", project=tmp_path)
    with caplog.at_level("INFO"):
        code = App(cfg)()
    assert code == 0
    assert "project root" in caplog.text


def test_app_import_reports_failure_exit_code(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/app/app.py::App.__call__ kind="unit"
    (tmp_path / "demo.kicad_pro").write_text("{}", encoding="utf-8")
    missing_zip = tmp_path / "missing.zip"
    cfg = AppConfig(command="import", project=tmp_path, zips=[missing_zip])
    code = App(cfg)()
    assert code == 1
