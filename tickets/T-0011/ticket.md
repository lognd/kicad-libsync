---
id: T-0011
title: claim divergence from T-0003's Done report (1 identit(ies))
state: queued
kind: bug
origin: agent
created: '2026-09-05'
priority: high
parent: null
tier: ticket
sprint: null
runs_last: false
milestone: null
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- tests/integration/test_archive_fixtures.py
findings:
- - TEST006
  - tests/integration/test_archive_fixtures.py
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
Deferred post-land claim-divergence check (T-2938) found that T-0003's Done report's captured gate-state claim (T-0754) no longer holds against the tree this sweep measured at 68f6291da6d3 -- reusing this sweep's own unscoped `frob check` result as both the count and the per-finding identity source, no second spawn.

Diverging (rule, file) identit(ies):
- TEST006: tests/integration/test_archive_fixtures.py

This is a report-honesty finding, not necessarily bad content on main -- the land already published; the tree itself was already covered by this land's own pre-land check plus this sweep's unscoped post-land measurement. Determine whether the claim was a stale/incorrect capture or a real self-introduced regression, fix or refresh accordingly, then dispose the quarantine entry this ticket raised.