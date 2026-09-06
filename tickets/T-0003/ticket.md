---
id: T-0003
title: 'archive.py: recognize Ultra Librarian zips into VendorPackage'
state: in-progress
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
- src/kicad_libsync/archive.py
- tests/unit/test_archive.py
- tests/fixtures/*
- tests/integration/test_archive_fixtures.py
- docs/design/01-vendor-zip-format.md
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: tests/integration/test_archive_fixtures.py
  reason: integration test file and design doc anchors added for archive.py
  actor: logan
  at: '2026-09-05'
- op: add
  glob: docs/design/01-vendor-zip-format.md
  reason: integration test file and design doc anchors added for archive.py
  actor: logan
  at: '2026-09-05'
designated_repro_test: null
acceptance:
- text: given 2N7002NXAKR.zip, when inspected, then one symbols_text and three footprints
    are returned
  evidence: []
- text: given not-a-library.zip, when inspected, then Err(NoSymbolLibrary)
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
See docs/design/01-vendor-zip-format.md.