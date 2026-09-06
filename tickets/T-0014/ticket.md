---
id: T-0014
title: 'strata: narrow test-node exec/eval grants with via after tests grew past 20
  files'
state: queued
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
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given design/kicad-libsync.strata, when frob check runs, then zero SELFAUDIT001
    errors
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
SYS107 self-audit: node tests binds 22 files with via-less exec/eval/fs. Narrow exec/eval to the system-test files that actually use them.