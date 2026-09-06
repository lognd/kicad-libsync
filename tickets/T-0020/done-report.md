## Done report

Adds the kicad-libsync remove subcommand. It deletes a top-level symbol from the project .kicad_sym and, unless keep_footprints is set, any footprint file it uniquely owned, refusing with exit code 1 and SymbolInUse when a schematic still places it unless force is set.

Filed: none

### Changed
```
 README.md                               |   1 +
 design/kicad-libsync.strata             |   4 +
 docs/design/00-overview.md              |   5 +-
 docs/design/02-project-library-model.md |  29 +++++++
 docs/design/04-cli-and-config.md        |  18 ++++-
 docs/index.md                           |  14 ++--
 frob-coverage.lock.json                 |   3 +-
 src/kicad_libsync/__main__.py           |   8 ++
 src/kicad_libsync/app/app.py            |  22 ++++++
 src/kicad_libsync/app/config.py         |   8 +-
 src/kicad_libsync/errors.py             |   1 +
 src/kicad_libsync/footprints.py         |  27 +++++++
 src/kicad_libsync/remover.py            | 131 ++++++++++++++++++++++++++++++++
 src/kicad_libsync/symbols.py            |  70 +++++++++++++++++
 tests/system/test_cli.py                |  36 +++++++++
 tests/unit/test_app.py                  |  27 +++++++
 tests/unit/test_footprints.py           |  30 +++++++-
 tests/unit/test_main.py                 |   5 ++
 tests/unit/test_remover.py              | 125 ++++++++++++++++++++++++++++++
 tests/unit/test_symbols.py              |  47 +++++++++++-
 tickets/T-0020/done-report.md           |  40 ++++++++++
 tickets/T-0020/ticket.md                |  24 +++++-
 22 files changed, 656 insertions(+), 19 deletions(-)
```

### Evidence
- `tests/unit/test_remover.py::test_remove_symbols_deletes_only_its_own_footprint` (pytest node id, verified passing when recorded)
- `tests/unit/test_remover.py::test_remove_symbols_keeps_shared_footprint` (pytest node id, verified passing when recorded)
- `tests/unit/test_remover.py::test_remove_symbols_refuses_when_placed_in_schematic` (pytest node id, verified passing when recorded)
- `tests/system/test_cli.py::test_remove_end_to_end` (pytest node id, verified passing when recorded)

### Captured claims
- tests: 4 passed (from 4 evidence id(s))
- gates: 2 error(s), 91 warning(s), 1 waived
- error-findings: WIRE001@src/kicad_libsync/footprints.py, WIRE001@src/kicad_libsync/symbols.py
