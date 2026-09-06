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
- frob.lock
- design/kicad-libsync.strata
- src/kicad_libsync/symbols.py
- tests/unit/test_symbols.py
- docs/design/02-project-library-model.md
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
- op: add
  glob: frob.lock
  reason: frob.lock rewritten by the ack; strata pulled in by the overview doc anchor
    closure
  actor: logan
  at: '2026-09-06'
- op: add
  glob: design/kicad-libsync.strata
  reason: frob.lock rewritten by the ack; strata pulled in by the overview doc anchor
    closure
  actor: logan
  at: '2026-09-06'
- op: add
  glob: src/kicad_libsync/symbols.py
  reason: SnapMagic-prefixed Footprint property must have its vendor prefix replaced
  actor: logan
  at: '2026-09-06'
- op: add
  glob: tests/unit/test_symbols.py
  reason: SnapMagic-prefixed Footprint property must have its vendor prefix replaced
  actor: logan
  at: '2026-09-06'
- op: add
  glob: docs/design/02-project-library-model.md
  reason: SnapMagic-prefixed Footprint property must have its vendor prefix replaced
  actor: logan
  at: '2026-09-06'
evidence:
- tests/unit/test_archive.py::test_inspect_snapmagic_flat_layout
- tests/unit/test_symbols.py::test_merge_into_replaces_vendor_footprint_prefix
designated_repro_test: null
acceptance:
- text: inspect() recognizes tests/fixtures/NAU7802KGI.zip with one footprint
  evidence:
  - tests/unit/test_archive.py::test_inspect_snapmagic_flat_layout
  - tests/unit/test_symbols.py::test_merge_into_replaces_vendor_footprint_prefix
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
