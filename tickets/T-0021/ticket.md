---
id: T-0021
title: 'Accept SnapMagic exports: .kicad_mod at zip root, no .pretty dir'
state: queued
kind: feature
origin: human
created: '2026-09-06'
priority: medium
parent: null
tier: ticket
sprint: null
runs_last: false
milestone: null
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/kicad_libsync/archive.py
- src/kicad_libsync/errors.py
- tests/unit/test_archive.py
- tests/fixtures/NAU7802KGI.zip
- docs/design/01-vendor-zip-format.md
- .gitignore
- docs/design/00-overview.md
- tests/unit/test_errors.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: .gitignore
  reason: ignore .serena scratch dir; errors.py doc/test closure pulled in by the
    NoFootprints message change
  actor: logan
  at: '2026-09-06'
- op: add
  glob: docs/design/00-overview.md
  reason: ignore .serena scratch dir; errors.py doc/test closure pulled in by the
    NoFootprints message change
  actor: logan
  at: '2026-09-06'
- op: add
  glob: tests/unit/test_errors.py
  reason: ignore .serena scratch dir; errors.py doc/test closure pulled in by the
    NoFootprints message change
  actor: logan
  at: '2026-09-06'
designated_repro_test: null
acceptance:
- text: inspect() recognizes tests/fixtures/NAU7802KGI.zip with one footprint
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
