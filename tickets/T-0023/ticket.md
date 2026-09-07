---
id: T-0023
title: 'FLAGCOV001: frob cannot import kicad_libsync, so flag coverage is UNMEASURED'
state: queued
kind: bug
origin: agent
created: '2026-09-07'
priority: low
parent: null
tier: ticket
sprint: null
runs_last: false
milestone: null
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- frob.toml
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a clean tree, when frob check runs, then gate:FLAGCOV reports 0 unresolved
    instead of 'could not resolve parser'
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
gate:FLAGCOV resolves docblocks.commands parser 'kicad_libsync.__main__:_build_parser' inside frob's own uv-tool venv, which has no kicad_libsync on sys.path ('No module named kicad_libsync'), so flag coverage for the whole CLI tree is unmeasured rather than clean. Pre-existing; observed while working T-0022. Fix is to give the gate an import path into the project venv (or run the resolution as a subprocess under the project interpreter).