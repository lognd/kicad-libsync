---
id: T-0005
title: 'symbols.py + footprints.py: merge symbols and copy footprints with skip/overwrite'
state: queued
kind: feature
origin: agent
created: '2026-09-05'
priority: medium
blocked_by:
- T-0002
parent: T-0001
tier: ticket
sprint: null
runs_last: false
milestone: null
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/kicad_libsync/symbols.py
- src/kicad_libsync/footprints.py
- tests/unit/test_symbols.py
- tests/unit/test_footprints.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a vendor symbol with bare Footprint X, when merged into lib L, then
    the property reads L:X
  evidence: []
- text: given an existing symbol of the same name, when merged without overwrite,
    then it is skipped
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
See docs/design/02-project-library-model.md.