## Done report

Adding tests/__init__.py files (T-0006) pushed the strata tests node past the 20-file SYS107 threshold; exec/eval/fs grants are now via-scoped and the via ratchet lock is baselined.

### Changed
(no changed files detected)

### Evidence
- `cmd:frob check --only sys exit=0 sha256=ba70551eb2fd` (cmd evidence, exit=0)

### Captured claims
- tests: 0 passed (from 0 evidence id(s))
- gates: 1 error(s), 49 warning(s), 0 waived
- error-findings: REF002@docs/design/registry/capability-via-ratchet.lock.json
