## Done report

Implements symbols.merge_into and footprints.copy_into per docs/design/02-project-library-model.md, with unit tests (including real fixture zips) and an integration test merging both fixture zips end-to-end. Cleaned up obsolete WIRE001 waivers in errors.py (symbols.py/footprints.py now consume SymbolError/FootprintError) and in sexpr.py (symbols.py now calls Node.find), shrank merge_into under the ARCH001 line threshold, and clarified the design doc's MergeOutcome-reuse and footprint-mapping notes.

### Changed
```
 docs/design/02-project-library-model.md  |  13 ++-
 frob-coverage.lock.json                  |   6 +-
 src/kicad_libsync/errors.py              |   2 -
 src/kicad_libsync/footprints.py          |  70 ++++++++++++++
 src/kicad_libsync/sexpr.py               |   1 -
 src/kicad_libsync/symbols.py             | 156 +++++++++++++++++++++++++++++++
 tests/integration/test_merge_fixtures.py |  55 +++++++++++
 tests/unit/test_footprints.py            |  46 +++++++++
 tests/unit/test_symbols.py               | 109 +++++++++++++++++++++
 tickets/T-0005/done-report.md            |  26 ++++++
 tickets/T-0005/ticket.md                 |  39 +++++++-
 11 files changed, 508 insertions(+), 15 deletions(-)
```

### Evidence
- `tests/unit/test_symbols.py::test_merge_into_reports_added_names` (pytest node id, verified passing when recorded)
- `tests/unit/test_symbols.py::test_merge_into_skips_existing_without_overwrite` (pytest node id, verified passing when recorded)
- `tests/unit/test_footprints.py::test_copy_into_skips_existing_without_overwrite` (pytest node id, verified passing when recorded)
- `tests/unit/test_footprints.py::test_copy_into_replaces_existing_with_overwrite` (pytest node id, verified passing when recorded)

### Captured claims
- tests: 4 passed (from 4 evidence id(s))
- gates: 0 error(s), 38 warning(s), 2 waived
- error-findings: none (measured, zero errors)
