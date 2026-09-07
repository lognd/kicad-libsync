---
id: T-0022
title: 'Publishable docs: watcher configuration guide, PyPI release workflow, no local
  paths'
state: in-progress
kind: docs
origin: human
created: '2026-09-07'
priority: medium
parent: null
tier: ticket
sprint: null
runs_last: false
milestone: null
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- README.md
- docs/configuration.md
- docs/index.md
- docs/design/00-overview.md
- docs/design/04-cli-and-config.md
- docs/design/README.md
- .github/workflows/release.yml
- pyproject.toml
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
designated_repro_test: null
acceptance:
- text: given a new user, when they read the docs, then they can configure the watcher
    via config file, env vars, and CLI flags without reading source
  evidence: []
- text: given a pushed v* tag, when release.yml runs, then it verifies the tag matches
    the project version and publishes sdist+wheel to PyPI via trusted publishing
  evidence: []
- text: given the tracked docs, when searched for machine-specific absolute paths,
    then none remain
  evidence: []
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
The repo now has a public remote and is headed for PyPI. Docs still carry the author's local paths, and there is no user-facing guide to configuring the watcher.