---
id: T-0020
title: 'remove subcommand: drop a symbol (and its orphaned footprint) from the project
  library'
state: done
kind: feature
origin: human
created: '2026-09-06'
priority: high
parent: T-0001
tier: ticket
sprint: null
runs_last: false
milestone: null
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/kicad_libsync/symbols.py
- src/kicad_libsync/footprints.py
- src/kicad_libsync/remover.py
- src/kicad_libsync/app/*.py
- src/kicad_libsync/__main__.py
- src/kicad_libsync/errors.py
- tests/unit/test_remover.py
- tests/unit/test_symbols.py
- tests/unit/test_footprints.py
- tests/unit/test_app.py
- tests/unit/test_main.py
- tests/system/test_cli.py
- docs/design/02-project-library-model.md
- docs/design/04-cli-and-config.md
- docs/index.md
- README.md
- design/*
- docs/design/00-overview.md
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: docs/design/00-overview.md
  reason: SymbolError gained SymbolInUse and AFFECT001 requires touching its doc anchor
  actor: logan
  at: '2026-09-06'
evidence:
- tests/unit/test_remover.py::test_remove_symbols_deletes_only_its_own_footprint
- tests/unit/test_remover.py::test_remove_symbols_keeps_shared_footprint
- tests/unit/test_remover.py::test_remove_symbols_refuses_when_placed_in_schematic
- tests/system/test_cli.py::test_remove_end_to_end
designated_repro_test: null
acceptance:
- text: given a library with TSR_1-2433 and TSR_1-2433E sharing nothing, when remove
    TSR_1-2433 runs, then only TSR_1-2433 and TSR1-SINGLE_TRP.kicad_mod are gone
  evidence:
  - tests/unit/test_remover.py::test_remove_symbols_deletes_only_its_own_footprint
- text: given two symbols sharing a footprint, when one is removed, then the footprint
    file stays
  evidence:
  - tests/unit/test_remover.py::test_remove_symbols_keeps_shared_footprint
- text: given a schematic placing the symbol, when remove runs without --force, then
    exit 1 and nothing changes
  evidence:
  - tests/unit/test_remover.py::test_remove_symbols_refuses_when_placed_in_schematic
  - tests/system/test_cli.py::test_remove_end_to_end
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
kicad-libsync remove --project P NAME [NAME...] [--keep-footprints] [--force]: delete the top-level (symbol NAME ...) from <Lib>.kicad_sym; delete each footprint file the removed symbol's Footprint property referenced in <Lib>.pretty when no remaining symbol references it; refuse (exit 1, SymbolInUse) if any .kicad_sch under the project root contains (lib_id "<Lib>:NAME") unless --force.