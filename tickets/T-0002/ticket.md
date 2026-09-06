---
id: T-0002
title: 'errors.py + sexpr.py: ErrorSets and minimal s-expression parse/emit'
state: queued
kind: feature
origin: agent
created: '2026-09-05'
priority: medium
parent: T-0001
tier: ticket
sprint: null
runs_last: false
milestone: null
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/kicad_libsync/errors.py
- src/kicad_libsync/sexpr.py
- tests/unit/test_sexpr.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a KiCad .kicad_sym text, when parsed and dumped, then re-parsing yields
    an equal tree
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
See docs/design/02-project-library-model.md (sexpr section).