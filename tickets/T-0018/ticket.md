---
id: T-0018
title: state note should record an ISO timestamp, not the literal 'now'
state: queued
kind: bug
origin: agent
created: '2026-09-05'
priority: low
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
- tests/unit/test_watcher.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
processed.json entries read 'B5B_XH_A.zip @ now -> <root>'; use datetime.now(UTC).isoformat().