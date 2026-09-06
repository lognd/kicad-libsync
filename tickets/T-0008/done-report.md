## Done report

wired watch/import/status CLI onto existing importer/watcher/state/project/libtable modules with layered CLI/env/file/detection config, and dropped the two stale T-0008 WIRE001 waivers now that app.py consumes them

### Changed
```
 README.md                                          |   2 +
 design/kicad-libsync.strata                        |   1 +
 docs/design/00-overview.md                         |   4 +-
 docs/design/04-cli-and-config.md                   |   8 +-
 .../registry/capability-via-ratchet.lock.json      |   5 +
 docs/index.md                                      |   9 +-
 frob-coverage.lock.json                            |   2 +-
 frob.toml                                          |  10 ++
 src/kicad_libsync/__main__.py                      |  42 +++++-
 src/kicad_libsync/app/app.py                       | 113 +++++++++++++++-
 src/kicad_libsync/app/config.py                    | 140 +++++++++++++++++--
 src/kicad_libsync/errors.py                        |   1 -
 src/kicad_libsync/libtable.py                      |   1 -
 src/kicad_libsync/state.py                         |   5 -
 src/kicad_libsync/watcher.py                       |   2 -
 tests/system/test_cli.py                           | 149 +++++++++++++++++++++
 tests/unit/test_app.py                             | 121 ++++++++++++++++-
 tests/unit/test_main.py                            |  40 +++++-
 tickets/T-0008/done-report.md                      |  33 +++++
 tickets/T-0008/ticket.md                           |  80 ++++++++++-
 20 files changed, 720 insertions(+), 48 deletions(-)
```

### Evidence
- `tests/system/test_cli.py::test_import_end_to_end` (pytest node id, verified passing when recorded)

### Captured claims
- tests: 1 passed (from 1 evidence id(s))
- gates: 0 error(s), 86 warning(s), 1 waived
- error-findings: none (measured, zero errors)
