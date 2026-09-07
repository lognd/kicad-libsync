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
- LICENSE
- Makefile
- docs/design/01-vendor-zip-format.md
- docs/design/05-testing-strategy.md
- src/kicad_libsync/py.typed
- design/kicad-libsync.strata
- src/kicad_libsync/__main__.py
- src/kicad_libsync/app/app.py
- src/kicad_libsync/app/config.py
- src/kicad_libsync/errors.py
- src/kicad_libsync/logging/filter.py
- src/kicad_libsync/logging/formatter.py
- src/kicad_libsync/logging/logger.py
- frob.toml
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: LICENSE
  reason: Publishing to PyPI pulled in the packaging surface (LICENSE, py.typed, Makefile
    upload target) and the SnapMagic doc-drift fix; the src/ and strata entries are
    doc-anchor closure for the docs already in scope, not code edits.
  actor: logan
  at: '2026-09-07'
- op: add
  glob: Makefile
  reason: Publishing to PyPI pulled in the packaging surface (LICENSE, py.typed, Makefile
    upload target) and the SnapMagic doc-drift fix; the src/ and strata entries are
    doc-anchor closure for the docs already in scope, not code edits.
  actor: logan
  at: '2026-09-07'
- op: add
  glob: docs/design/01-vendor-zip-format.md
  reason: Publishing to PyPI pulled in the packaging surface (LICENSE, py.typed, Makefile
    upload target) and the SnapMagic doc-drift fix; the src/ and strata entries are
    doc-anchor closure for the docs already in scope, not code edits.
  actor: logan
  at: '2026-09-07'
- op: add
  glob: docs/design/05-testing-strategy.md
  reason: Publishing to PyPI pulled in the packaging surface (LICENSE, py.typed, Makefile
    upload target) and the SnapMagic doc-drift fix; the src/ and strata entries are
    doc-anchor closure for the docs already in scope, not code edits.
  actor: logan
  at: '2026-09-07'
- op: add
  glob: src/kicad_libsync/py.typed
  reason: Publishing to PyPI pulled in the packaging surface (LICENSE, py.typed, Makefile
    upload target) and the SnapMagic doc-drift fix; the src/ and strata entries are
    doc-anchor closure for the docs already in scope, not code edits.
  actor: logan
  at: '2026-09-07'
- op: add
  glob: design/kicad-libsync.strata
  reason: Publishing to PyPI pulled in the packaging surface (LICENSE, py.typed, Makefile
    upload target) and the SnapMagic doc-drift fix; the src/ and strata entries are
    doc-anchor closure for the docs already in scope, not code edits.
  actor: logan
  at: '2026-09-07'
- op: add
  glob: src/kicad_libsync/__main__.py
  reason: Publishing to PyPI pulled in the packaging surface (LICENSE, py.typed, Makefile
    upload target) and the SnapMagic doc-drift fix; the src/ and strata entries are
    doc-anchor closure for the docs already in scope, not code edits.
  actor: logan
  at: '2026-09-07'
- op: add
  glob: src/kicad_libsync/app/app.py
  reason: Publishing to PyPI pulled in the packaging surface (LICENSE, py.typed, Makefile
    upload target) and the SnapMagic doc-drift fix; the src/ and strata entries are
    doc-anchor closure for the docs already in scope, not code edits.
  actor: logan
  at: '2026-09-07'
- op: add
  glob: src/kicad_libsync/app/config.py
  reason: Publishing to PyPI pulled in the packaging surface (LICENSE, py.typed, Makefile
    upload target) and the SnapMagic doc-drift fix; the src/ and strata entries are
    doc-anchor closure for the docs already in scope, not code edits.
  actor: logan
  at: '2026-09-07'
- op: add
  glob: src/kicad_libsync/errors.py
  reason: Publishing to PyPI pulled in the packaging surface (LICENSE, py.typed, Makefile
    upload target) and the SnapMagic doc-drift fix; the src/ and strata entries are
    doc-anchor closure for the docs already in scope, not code edits.
  actor: logan
  at: '2026-09-07'
- op: add
  glob: src/kicad_libsync/logging/filter.py
  reason: Publishing to PyPI pulled in the packaging surface (LICENSE, py.typed, Makefile
    upload target) and the SnapMagic doc-drift fix; the src/ and strata entries are
    doc-anchor closure for the docs already in scope, not code edits.
  actor: logan
  at: '2026-09-07'
- op: add
  glob: src/kicad_libsync/logging/formatter.py
  reason: Publishing to PyPI pulled in the packaging surface (LICENSE, py.typed, Makefile
    upload target) and the SnapMagic doc-drift fix; the src/ and strata entries are
    doc-anchor closure for the docs already in scope, not code edits.
  actor: logan
  at: '2026-09-07'
- op: add
  glob: src/kicad_libsync/logging/logger.py
  reason: Publishing to PyPI pulled in the packaging surface (LICENSE, py.typed, Makefile
    upload target) and the SnapMagic doc-drift fix; the src/ and strata entries are
    doc-anchor closure for the docs already in scope, not code edits.
  actor: logan
  at: '2026-09-07'
- op: add
  glob: frob.toml
  reason: REF001 entrypoint registrations for the files this ticket adds (LICENSE,
    py.typed) plus the pre-existing frob.lock gap surfaced by the same gate run.
  actor: logan
  at: '2026-09-07'
evidence:
- cmd:bash -c "rm -rf dist && uv build && uvx twine check --strict dist/*" exit=0
  sha256=580ba7c101f4
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