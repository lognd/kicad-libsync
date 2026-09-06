## Done report

importer.py orchestrates footprints, then symbols, then lib tables into ImportReport, wiring archive.inspect, project.locate, libtable.ensure_entry, symbols.merge_into and footprints.copy_into and dropping their satisfied T-0006 WIRE001 waivers. Added frob:boundary b_archive_inspect on archive.inspect.

### Changed
```
 docs/design/02-project-library-model.md |  17 ++--
 frob-coverage.lock.json                 |   3 +-
 src/kicad_libsync/archive.py            |   3 +-
 src/kicad_libsync/footprints.py         |   1 -
 src/kicad_libsync/importer.py           | 143 ++++++++++++++++++++++++++++++++
 src/kicad_libsync/libtable.py           |   1 -
 src/kicad_libsync/project.py            |   2 -
 src/kicad_libsync/symbols.py            |   2 -
 tests/__init__.py                       |   0
 tests/integration/__init__.py           |   0
 tests/integration/test_importer.py      |  57 +++++++++++++
 tests/system/__init__.py                |   0
 tests/unit/__init__.py                  |   0
 tests/unit/test_importer.py             |  55 ++++++++++++
 tickets/T-0006/ticket.md                |  79 +++++++++++++++++-
 15 files changed, 347 insertions(+), 16 deletions(-)
```

### Evidence
- `tests/integration/test_importer.py::test_import_twice_skips_everything` (pytest node id, verified passing when recorded)

### Captured claims
- tests: 1 passed (from 1 evidence id(s))
- gates: 1 error(s), 56 warning(s), 2 waived
- error-findings: SELFAUDIT001@design
