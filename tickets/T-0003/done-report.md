## Done report

Implemented archive inspect and VendorPackage per design doc rules 1 to 5, verified against real fixture zips and synthetic error path zips; also dropped the now-obsolete ArchiveError WIRE001 waiver in errors.py since archive.py consumes it directly.

### Changed
```
 docs/design/01-vendor-zip-format.md        |   4 ++
 frob-coverage.lock.json                    |   3 +-
 src/kicad_libsync/archive.py               | 109 +++++++++++++++++++++++++++++
 src/kicad_libsync/errors.py                |   1 -
 tests/integration/test_archive_fixtures.py |  27 +++++++
 tests/unit/test_archive.py                 | 105 +++++++++++++++++++++++++++
 tickets/T-0003/done-report.md              |  23 ++++++
 tickets/T-0003/ticket.md                   |  30 +++++++-
 8 files changed, 297 insertions(+), 5 deletions(-)
```

### Evidence
- `tests/unit/test_archive.py::test_inspect_valid_zip_two_footprints` (pytest node id, verified passing when recorded)
- `tests/unit/test_archive.py::test_inspect_not_a_library_has_no_symbol` (pytest node id, verified passing when recorded)

### Captured claims
- tests: 2 passed (from 2 evidence id(s))
- gates: 0 error(s), 28 warning(s), 1 waived
- error-findings: none (measured, zero errors)
