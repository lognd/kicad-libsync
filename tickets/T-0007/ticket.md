---
id: T-0007
title: 'state.py + watcher.py: processed ledger and polling loop'
state: queued
kind: feature
origin: agent
created: '2026-09-05'
priority: medium
blocked_by:
- T-0006
parent: T-0001
tier: ticket
sprint: null
runs_last: false
milestone: null
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/kicad_libsync/state.py
- src/kicad_libsync/watcher.py
- tests/unit/test_state.py
- tests/unit/test_watcher.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a new zip, when polled twice with unchanged size, then it is imported
    once and its hash recorded
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
See docs/design/03-watcher.md.