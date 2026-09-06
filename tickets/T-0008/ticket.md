---
id: T-0008
title: 'CLI + App + AppConfig: watch/import/status commands'
state: queued
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
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given python -m kicad_libsync import --project <tmp> fixture.zip, when run,
    then the project has <Lib>.kicad_sym, <Lib>.pretty and both tables
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
See docs/design/04-cli-and-config.md.