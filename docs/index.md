# kicad-libsync

Watch a Downloads folder and merge vendor KiCad library zips (Ultra Librarian `KiCADv6/` exports) into the KiCad project you are working on. Design: [docs/design/](design/README.md).

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

`main` parses CLI args, builds an `AppConfig` from CLI/TOML, and runs `App`.
The `logging` subpackage provides `get_logger`, wired per the house
logging convention (stdout for DEBUG/INFO, stderr for WARNING+).
