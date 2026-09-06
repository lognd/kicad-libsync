---
id: T-0002
title: 'errors.py + sexpr.py: ErrorSets and minimal s-expression parse/emit'
state: in-progress
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
- docs/design/02-project-library-model.md
- docs/design/00-overview.md
- docs/index.md
- frob.toml
- scripts/bump_version.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: docs/design/02-project-library-model.md
  reason: doc anchors for sexpr/errors plus gate config the first ticket has to establish
  actor: logan
  at: '2026-09-05'
- op: add
  glob: docs/design/00-overview.md
  reason: doc anchors for sexpr/errors plus gate config the first ticket has to establish
  actor: logan
  at: '2026-09-05'
- op: add
  glob: docs/index.md
  reason: doc anchors for sexpr/errors plus gate config the first ticket has to establish
  actor: logan
  at: '2026-09-05'
- op: add
  glob: frob.toml
  reason: doc anchors for sexpr/errors plus gate config the first ticket has to establish
  actor: logan
  at: '2026-09-05'
- op: add
  glob: scripts/bump_version.py
  reason: doc anchors for sexpr/errors plus gate config the first ticket has to establish
  actor: logan
  at: '2026-09-05'
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