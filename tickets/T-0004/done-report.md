## Done report

Changed:
src/kicad_libsync/project.py::KicadProject
src/kicad_libsync/project.py::locate
src/kicad_libsync/libtable.py::ensure_entry
src/kicad_libsync/libtable.py::entries
docs/design/02-project-library-model.md#project
docs/design/02-project-library-model.md#libtable
src/kicad_libsync/errors.py::ProjectError (dropped satisfied frob:waive WIRE001)
src/kicad_libsync/errors.py::LibTableError (dropped satisfied frob:waive WIRE001)
src/kicad_libsync/sexpr.py (dropped satisfied module-level frob:waive REF002)
src/kicad_libsync/sexpr.py::dumps (dropped satisfied frob:waive WIRE001)

Evidence: tests/unit/test_project.py::test_locate_derives_paths_from_stem (acceptance 1); tests/unit/test_libtable.py::test_ensure_entry_twice_yields_one_entry (acceptance 2); full suite in tests/unit/test_project.py, tests/unit/test_libtable.py, tests/integration/test_project_tables.py

Filed: none (a successor ticket T-0012 was filed and later dropped once the coordinator authorized deleting the waivers directly under T-0004, after T-0005 landed on main and released its lease on errors.py)

Gates: frob check --ticket T-0004 clean -- 0 errors, warnings only (SCOPE002/TICK014/PII012/EXHAUST/LANG/PERF pre-existing and repo-wide, TEST005 branch-coverage warnings repo-wide, FLAGCOV001 unresolved -- project-wide, unmeasured CLI surface)

### Changed
```
 docs/design/02-project-library-model.md  |  13 +--
 frob-coverage.lock.json                  |   4 +-
 src/kicad_libsync/errors.py              |   2 -
 src/kicad_libsync/libtable.py            | 137 +++++++++++++++++++++++++++++++
 src/kicad_libsync/project.py             |  72 ++++++++++++++++
 src/kicad_libsync/sexpr.py               |   3 -
 tests/integration/test_project_tables.py |  23 ++++++
 tests/unit/test_libtable.py              |  77 +++++++++++++++++
 tests/unit/test_project.py               |  57 +++++++++++++
 tickets/T-0004/done-report.md            |  40 +++++++++
 tickets/T-0004/ticket.md                 |  19 ++++-
 11 files changed, 434 insertions(+), 13 deletions(-)
```

### Evidence
- `tests/unit/test_project.py::test_locate_derives_paths_from_stem` (pytest node id, verified passing when recorded)
- `tests/unit/test_libtable.py::test_ensure_entry_twice_yields_one_entry` (pytest node id, verified passing when recorded)

### Captured claims
- tests: 2 passed (from 2 evidence id(s))
- gates: 0 error(s), 50 warning(s), 3 waived
- error-findings: none (measured, zero errors)
