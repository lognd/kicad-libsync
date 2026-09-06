## Done report

Implemented state.py and watcher.py per the design doc and wired the waived importer and errors symbols into the watcher.

### Changed
```
 docs/design/03-watcher.md               |  25 ++++-
 frob-coverage.lock.json                 |   6 +-
 src/kicad_libsync/errors.py             |   1 -
 src/kicad_libsync/importer.py           |   3 -
 src/kicad_libsync/state.py              | 136 +++++++++++++++++++++++++++
 src/kicad_libsync/watcher.py            | 162 ++++++++++++++++++++++++++++++++
 tests/integration/test_watcher_state.py |  50 ++++++++++
 tests/unit/test_state.py                |  95 +++++++++++++++++++
 tests/unit/test_watcher.py              | 116 +++++++++++++++++++++++
 tickets/T-0007/ticket.md                |  32 ++++++-
 10 files changed, 613 insertions(+), 13 deletions(-)
```

### Evidence
- `tests/unit/test_watcher.py::test_zip_is_imported_once_after_it_stabilizes` (pytest node id, verified passing when recorded)

### Captured claims
- tests: 1 passed (from 1 evidence id(s))
- gates: 1 error(s), 74 warning(s), 7 waived
- error-findings: SELFAUDIT001@design
