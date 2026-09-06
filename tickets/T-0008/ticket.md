---
id: T-0008
title: 'CLI + App + AppConfig: watch/import/status commands'
state: done
kind: feature
origin: agent
created: '2026-09-05'
priority: medium
blocked_by:
- T-0007
parent: T-0001
tier: ticket
sprint: null
runs_last: false
milestone: null
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/kicad_libsync/__main__.py
- src/kicad_libsync/app/*.py
- tests/unit/test_app.py
- tests/unit/test_main.py
- tests/system/*.py
- docs/index.md
- README.md
- frob.toml
- src/kicad_libsync/state.py
- src/kicad_libsync/watcher.py
- docs/design/04-cli-and-config.md
- tests/system/test_cli.py
- design/kicad-libsync.strata
- docs/design/00-overview.md
- docs/design/registry/capability-via-ratchet.lock.json
- src/kicad_libsync/errors.py
- src/kicad_libsync/libtable.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: frob.toml
  reason: 'wire watch/import/status commands: remove WIRE001 waivers in state.py/watcher.py
    now consumed by app.py, update the config doc to final API, add frob.toml docblocks/refs
    entries, add system CLI tests'
  actor: logan
  at: '2026-09-05'
- op: add
  glob: src/kicad_libsync/state.py
  reason: 'wire watch/import/status commands: remove WIRE001 waivers in state.py/watcher.py
    now consumed by app.py, update the config doc to final API, add frob.toml docblocks/refs
    entries, add system CLI tests'
  actor: logan
  at: '2026-09-05'
- op: add
  glob: src/kicad_libsync/watcher.py
  reason: 'wire watch/import/status commands: remove WIRE001 waivers in state.py/watcher.py
    now consumed by app.py, update the config doc to final API, add frob.toml docblocks/refs
    entries, add system CLI tests'
  actor: logan
  at: '2026-09-05'
- op: add
  glob: docs/design/04-cli-and-config.md
  reason: 'wire watch/import/status commands: remove WIRE001 waivers in state.py/watcher.py
    now consumed by app.py, update the config doc to final API, add frob.toml docblocks/refs
    entries, add system CLI tests'
  actor: logan
  at: '2026-09-05'
- op: add
  glob: tests/system/test_cli.py
  reason: 'wire watch/import/status commands: remove WIRE001 waivers in state.py/watcher.py
    now consumed by app.py, update the config doc to final API, add frob.toml docblocks/refs
    entries, add system CLI tests'
  actor: logan
  at: '2026-09-05'
- op: add
  glob: design/kicad-libsync.strata
  reason: declare env capability for new system test that copies the process environ
  actor: logan
  at: '2026-09-05'
- op: add
  glob: docs/design/00-overview.md
  reason: adding env capability to tests node needs the ratchet lock and its narrating
    overview doc touched too
  actor: logan
  at: '2026-09-05'
- op: add
  glob: docs/design/registry/capability-via-ratchet.lock.json
  reason: adding env capability to tests node needs the ratchet lock and its narrating
    overview doc touched too
  actor: logan
  at: '2026-09-05'
- op: add
  glob: src/kicad_libsync/errors.py
  reason: remove stale WIRE001 waivers now that app.py/config.py consume these symbols
  actor: logan
  at: '2026-09-05'
- op: add
  glob: src/kicad_libsync/libtable.py
  reason: remove stale WIRE001 waivers now that app.py/config.py consume these symbols
  actor: logan
  at: '2026-09-05'
evidence:
- tests/system/test_cli.py::test_import_end_to_end
designated_repro_test: null
acceptance:
- text: given python -m kicad_libsync import --project <tmp> fixture.zip, when run,
    then the project has <Lib>.kicad_sym, <Lib>.pretty and both tables
  evidence:
  - tests/system/test_cli.py::test_import_end_to_end
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
See docs/design/04-cli-and-config.md.