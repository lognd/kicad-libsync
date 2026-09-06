---
id: T-0016
title: 'strata V-model: point runnables at the landed test ids'
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
- text: given the landed suite, when every vmodel runnable outside tests/system is
    checked against pytest --collect-only, then all resolve
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
Implementers named tests differently from the V-model's guesses; realign runnable attrs with pytest collection.