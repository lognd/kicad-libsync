---
id: T-0006
title: 'importer.py: orchestrate package -> project with ImportReport'
state: in-progress
kind: feature
origin: agent
created: '2026-09-05'
priority: medium
blocked_by:
- T-0003
- T-0004
- T-0005
parent: T-0001
tier: ticket
sprint: null
runs_last: false
milestone: null
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/kicad_libsync/importer.py
- tests/integration/test_importer.py
- src/kicad_libsync/archive.py
- src/kicad_libsync/project.py
- src/kicad_libsync/libtable.py
- src/kicad_libsync/symbols.py
- src/kicad_libsync/footprints.py
- docs/design/02-project-library-model.md
- tests/unit/test_importer.py
- tests/__init__.py
- tests/unit/__init__.py
- tests/integration/__init__.py
- tests/system/__init__.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: src/kicad_libsync/archive.py
  reason: importer wires them, drop satisfied waivers
  actor: logan
  at: '2026-09-05'
- op: add
  glob: src/kicad_libsync/project.py
  reason: importer wires them, drop satisfied waivers
  actor: logan
  at: '2026-09-05'
- op: add
  glob: src/kicad_libsync/libtable.py
  reason: importer wires them, drop satisfied waivers
  actor: logan
  at: '2026-09-05'
- op: add
  glob: src/kicad_libsync/symbols.py
  reason: importer wires them, drop satisfied waivers
  actor: logan
  at: '2026-09-05'
- op: add
  glob: src/kicad_libsync/footprints.py
  reason: importer wires them, drop satisfied waivers
  actor: logan
  at: '2026-09-05'
- op: add
  glob: docs/design/02-project-library-model.md
  reason: importer wires them, drop satisfied waivers
  actor: logan
  at: '2026-09-05'
- op: add
  glob: tests/integration/test_importer.py
  reason: importer wires them, drop satisfied waivers
  actor: logan
  at: '2026-09-05'
- op: add
  glob: tests/unit/test_importer.py
  reason: unit tests for importer
  actor: logan
  at: '2026-09-05'
- op: add
  glob: tests/__init__.py
  reason: package inits needed to disambiguate same-named test modules
  actor: logan
  at: '2026-09-05'
- op: add
  glob: tests/unit/__init__.py
  reason: package inits needed to disambiguate same-named test modules
  actor: logan
  at: '2026-09-05'
- op: add
  glob: tests/integration/__init__.py
  reason: package inits needed to disambiguate same-named test modules
  actor: logan
  at: '2026-09-05'
- op: add
  glob: tests/system/__init__.py
  reason: package inits needed to disambiguate same-named test modules
  actor: logan
  at: '2026-09-05'
designated_repro_test: null
acceptance:
- text: given a fixture zip and an empty project dir, when imported twice, then the
    second report skips everything
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
See docs/design/02-project-library-model.md (importer section).