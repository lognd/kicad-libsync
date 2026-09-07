# 05 -- Testing Strategy

Three layers, all under `tests/`, all bound with `frob:tests` directives.

| Layer | Dir | What | I/O |
|---|---|---|---|
| unit | `tests/unit/` | one module at a time: sexpr round-trip, archive rules, merge policy, lib table edit, state hashing, watcher stability logic | `tmp_path` only |
| integration | `tests/integration/` | `importer.import_package` against a synthetic project dir built from a fixture zip; then a second import of the same zip skips everything | real filesystem under `tmp_path` |
| system | `tests/system/` | `python -m kicad_libsync import --project <tmp> <fixture.zip>` via subprocess, then assert the project files exist and the tables reference them; `watch --backfill` with a short poll against a `tmp_path` Downloads and a timeout | subprocess |

## Fixtures

`tests/fixtures/` holds REAL vendor zips (`2N7002NXAKR.zip`,
`22R336MC.zip`; 20 KB total) plus one `not-a-library.zip` containing a
text file. Never mock `zipfile`.

## Watcher testing

The poll loop takes an injectable `clock`/`sleep` so unit tests drive
polls synchronously: create a zip, poll once (unstable), poll again
(stable, imported), assert state recorded.

## Coverage floors

frob.toml starts at 50% and is ratcheted up once the suite exists.
