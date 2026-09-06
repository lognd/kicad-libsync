# 04 -- CLI and Config

## Commands

```
kicad-libsync watch  [--project P] [--downloads D] [--lib-name L] [--poll S] [--backfill] [--overwrite]
kicad-libsync import [--project P] [--lib-name L] [--overwrite] ZIP [ZIP ...]
kicad-libsync status [--project P]        # libs, table entries, processed count
```

`--project` defaults to the current working directory.

## Config precedence (highest first)

CLI args > environment (`KICAD_LIBSYNC_DOWNLOADS`, `KICAD_LIBSYNC_PROJECT`,
`KICAD_LIBSYNC_POLL`) > `~/.config/kicad-libsync/config.toml` > detection.

Downloads detection when nothing is configured: the single directory
matching `/mnt/c/Users/*/Downloads` after excluding `Public`, `Default`,
`Default User`, `All Users`, `WsiAccount`; else `~/Downloads`; else
`ConfigError.NoDownloadsDir`. The detected value is logged at INFO so the
user can see which folder is watched.

## AppConfig

```python
class AppConfig(BaseModel):
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
    def from_external(cls, args, config_file=None) -> Result[AppConfig, ConfigError]
```

`App.__call__` dispatches on `command`; `watch` runs `asyncio.run` and
never returns, `import`/`status` return after printing. Exit code 1 when
any import in `import` mode failed; the failure reason is printed once via
`str(result)` (typani notes included).
