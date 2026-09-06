---
id: T-0016
title: 'strata V-model: point runnables at the landed test ids'
state: done
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
evidence:
- cmd:frob check --only vmodel exit=0 sha256=239dd03d9a7e
designated_repro_test: null
acceptance:
- text: given the landed suite, when every vmodel runnable outside tests/system is
    checked against pytest --collect-only, then all resolve
  evidence:
  - cmd:frob check --only vmodel exit=0 sha256=239dd03d9a7e
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
Implementers named tests differently from the V-model's guesses; realign runnable attrs with pytest collection.