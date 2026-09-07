# kicad-libsync

Watch your Downloads folder and merge vendor KiCad library zips into the
KiCad project you are working on -- footprints into `<Lib>.pretty`, symbols
into `<Lib>.kicad_sym`, both registered in the project lib tables, with the
symbol's `Footprint` property rewritten to `<Lib>:<footprint>` so KiCad
actually resolves it.

Two vendor export layouts are recognized:

- **Ultra Librarian** -- `KiCADv6/` with a `footprints.pretty/` directory
  next to the `.kicad_sym`.
- **SnapMagic** -- `.kicad_mod` files flat at the zip root next to the
  `.kicad_sym`, with the footprint reference prefixed by the part name
  (the prefix is stripped on import).

Any other zip that lands in Downloads is logged at DEBUG and ignored.

## Install

```bash
uv tool install kicad-libsync
```

## Use

```bash
kicad-libsync watch --project <kicad-project-dir>   # poll Downloads, import new zips
kicad-libsync import --project . vendor-package.zip # import specific zips now
kicad-libsync status --project .                    # libraries, table entries, processed count
kicad-libsync remove --project . SOME_PART          # drop a symbol and its orphaned footprint
```

`--project` defaults to the current directory, so from inside the project
`kicad-libsync watch` is usually enough.

## Configuring the watcher

Settings layer: **CLI flags > environment > `~/.config/kicad-libsync/config.toml` > autodetection**.

```toml
# ~/.config/kicad-libsync/config.toml
project      = "/path/to/your/kicad/project"
downloads    = "/path/to/your/Downloads"
lib_name     = "VendorParts"   # default: the .kicad_pro stem
poll_seconds = 2.0
```

Environment overrides: `KICAD_LIBSYNC_PROJECT`, `KICAD_LIBSYNC_DOWNLOADS`,
`KICAD_LIBSYNC_POLL` (a `.env` in the working directory is loaded too).

Per-run flags for `watch`: `--project`, `--downloads`, `--lib-name`,
`--poll`, `--backfill` (also import zips already sitting in Downloads at
startup), `--overwrite` (replace same-named symbols/footprints instead of
skipping them with a warning).

If `downloads` is not set anywhere, the tool looks for a single
`/mnt/c/Users/*/Downloads` (WSL, excluding the Windows system accounts) and
falls back to `~/Downloads`. The folder it settled on is logged at INFO on
every run.

Full reference, including the processed-state ledger and a troubleshooting
table: **[docs/configuration.md](docs/configuration.md)**.

## Docs

- [Configuration](docs/configuration.md)
- [Design docs](docs/design/README.md)

## Development

This is a frob-enabled project: `frob <verb>` is the interface, not a
`make` wrapper around it.

```bash
uv sync
cp .env.example .env   # fill in real values; .env is gitignored

frob test         # select and run tests for the touched set (or --all)
frob format       # ruff check --fix + ruff format
frob coverage     # refresh coverage.xml / the coverage stamp
frob check        # the aggregate gate: ruff, ty, frob cycle/dup/arch/...
```

`make install`/`make clean`/`make upload` remain for bootstrap and
build/publish -- see the Makefile.

## Releasing

Tagging `v<version>` on `main` publishes to PyPI via GitHub Actions
(`.github/workflows/release.yml`) using OIDC trusted publishing -- no API
token is stored in this repo. The workflow refuses to publish if the tag
does not match `project.version` in `pyproject.toml`.

```bash
make upload   # patch-bump pyproject.toml, commit, push, and push the v<version> tag
```

`make upload` only tags; the tag push is what publishes. For a minor or
major bump, edit `project.version` in `pyproject.toml` by hand, commit, and
push the matching tag yourself:

```bash
git commit -am "chore: bump version to 0.2.0"
git tag v0.2.0 && git push origin main v0.2.0
```

## License

MIT -- see [LICENSE](LICENSE).
