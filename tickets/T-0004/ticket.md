---
id: T-0004
title: 'project.py + libtable.py: locate project, ensure lib table entries'
state: done
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
- src/kicad_libsync/project.py
- src/kicad_libsync/libtable.py
- tests/unit/test_project.py
- tests/unit/test_libtable.py
- tests/integration/test_project_tables.py
- docs/design/02-project-library-model.md
- src/kicad_libsync/errors.py
- src/kicad_libsync/sexpr.py
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: tests/integration/test_project_tables.py
  reason: integration test + doc update required for T-0004 deliverables
  actor: logan
  at: '2026-09-05'
- op: add
  glob: docs/design/02-project-library-model.md
  reason: integration test + doc update required for T-0004 deliverables
  actor: logan
  at: '2026-09-05'
- op: remove
  glob: docs/design/02-project-library-model.md
  reason: release lease so T-0005 can close; re-added after T-0005 lands
  actor: logan
  at: '2026-09-05'
- op: add
  glob: docs/design/02-project-library-model.md
  reason: re-add doc; drop waivers satisfied by project.py/libtable.py
  actor: logan
  at: '2026-09-05'
- op: add
  glob: src/kicad_libsync/errors.py
  reason: re-add doc; drop waivers satisfied by project.py/libtable.py
  actor: logan
  at: '2026-09-05'
- op: add
  glob: src/kicad_libsync/sexpr.py
  reason: re-add doc; drop waivers satisfied by project.py/libtable.py
  actor: logan
  at: '2026-09-05'
evidence:
- tests/unit/test_project.py::test_locate_derives_paths_from_stem
- tests/unit/test_libtable.py::test_ensure_entry_twice_yields_one_entry
designated_repro_test: null
acceptance:
- text: given a dir with one .kicad_pro, when located, then lib paths derive from
    the stem
  evidence:
  - tests/unit/test_project.py::test_locate_derives_paths_from_stem
- text: given no fp-lib-table, when ensure_entry runs twice, then the file has exactly
    one entry
  evidence:
  - tests/unit/test_libtable.py::test_ensure_entry_twice_yields_one_entry
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
See docs/design/02-project-library-model.md.