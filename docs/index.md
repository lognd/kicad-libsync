# kicad-libsync

Watch a Downloads folder and merge vendor KiCad library zips (Ultra Librarian `KiCADv6/` exports and SnapMagic flat-root exports) into the KiCad project you are working on. Configuration: [configuration.md](configuration.md). Design: [docs/design/](design/README.md).

## Public API

<!-- frob:describes src/kicad_libsync/__main__.py::main -->
<!-- frob:describes src/kicad_libsync/app/app.py::App -->
<!-- frob:describes src/kicad_libsync/app/config.py::AppConfig -->
<!-- frob:describes src/kicad_libsync/app/config.py::AppConfig.from_external -->
<!-- frob:describes src/kicad_libsync/logging/logger.py::get_logger -->
<!-- frob:describes src/kicad_libsync/logging/formatter.py::SimpleFormatter -->
<!-- frob:describes src/kicad_libsync/logging/formatter.py::SimpleFormatter.format -->
<!-- frob:describes src/kicad_libsync/logging/filter.py::BelowLevelFilter -->
<!-- frob:describes src/kicad_libsync/logging/filter.py::BelowLevelFilter.filter -->

`main` parses CLI args (`watch`/`import`/`status`/`remove` subcommands),
builds an `AppConfig` via `from_external` (CLI over env over the config
file over Downloads detection), and runs `App`, which dispatches on
`AppConfig.command` and returns the process exit code. `remove` drops a
symbol (and its orphaned footprint) from the project library; see
docs/design/02-project-library-model.md#remover. The `logging` subpackage
provides `get_logger`, wired per the house logging convention (stdout for
DEBUG/INFO, stderr for WARNING+).

## Design docs

Module-by-module specs live in [design/](design/README.md):
[00-overview](design/00-overview.md), [01-vendor-zip-format](design/01-vendor-zip-format.md),
[02-project-library-model](design/02-project-library-model.md), [03-watcher](design/03-watcher.md),
[04-cli-and-config](design/04-cli-and-config.md), [05-testing-strategy](design/05-testing-strategy.md).

<!-- frob:external-reader dir=".github" reason="GitHub Actions reads the workflows; nothing in src references the directory" -->
<!-- frob:external-reader dir="invariants" reason="frob's own INV gates read invariants/; empty placeholder from the scaffold" -->
