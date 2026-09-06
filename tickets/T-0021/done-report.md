## Done report

SnapMagic zips now recognized (flat .kicad_mod) and their part-name Footprint prefix is replaced with the project lib; verified by unit tests plus an end-to-end import of NAU7802KGI.zip into a scratch project

### Changed
(no changed files detected)

### Evidence
- `tests/unit/test_archive.py::test_inspect_snapmagic_flat_layout` (pytest node id, verified passing when recorded)
- `tests/unit/test_symbols.py::test_merge_into_replaces_vendor_footprint_prefix` (pytest node id, verified passing when recorded)

### Captured claims
- tests: 2 passed (from 2 evidence id(s))
- gates: 1 error(s), 89 warning(s), 1 waived
- error-findings: REF001@frob.lock
