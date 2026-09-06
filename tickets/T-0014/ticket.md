---
id: T-0014
title: 'strata: narrow test-node exec/eval grants with via after tests grew past 20
  files'
state: done
kind: docs
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
- design/*
- docs/design/registry/*
- docs/design/00-overview.md
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: docs/design/registry/*
  reason: ratchet lock and doc touch
  actor: logan
  at: '2026-09-05'
- op: add
  glob: docs/design/00-overview.md
  reason: ratchet lock and doc touch
  actor: logan
  at: '2026-09-05'
evidence:
- cmd:frob check --only sys exit=0 sha256=ba70551eb2fd
designated_repro_test: null
acceptance:
- text: given design/kicad-libsync.strata, when frob check runs, then zero SELFAUDIT001
    errors
  evidence:
  - cmd:frob check --only sys exit=0 sha256=ba70551eb2fd
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
SYS107 self-audit: node tests binds 22 files with via-less exec/eval/fs. Narrow exec/eval to the system-test files that actually use them.