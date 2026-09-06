---
id: T-0019
title: default console level INFO; add --verbose for DEBUG
state: queued
kind: ux
origin: agent
created: '2026-09-05'
priority: low
parent: T-0001
tier: ticket
sprint: null
runs_last: false
milestone: null
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/kicad_libsync/logging/*
- src/kicad_libsync/__main__.py
- src/kicad_libsync/app/config.py
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
Every sexpr parse logs at DEBUG and the root handler is DEBUG, so a single import prints ~20 lines of parser chatter. Keep DEBUG in the config but gate the stdout handler at INFO unless --verbose.