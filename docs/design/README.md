# Design Docs Index -- kicad-libsync

Entry point for design documentation. Each document is self-contained: an
agent assigned to a ticket reads only the document(s) that ticket names,
not the whole set. If a doc and the root README conflict, the root README's
intent wins -- file a note in the doc and ask the human.

## Reading map

| If you are building...                                   | Read |
|----------------------------------------------------------|------|
| Anything (repo layout, locked decisions, module tree)    | [00-overview.md](00-overview.md) |
| Zip recognition / extraction (`archive.py`)              | [01-vendor-zip-format.md](01-vendor-zip-format.md) |
| Symbol/footprint merge, lib tables (`sexpr.py`, `symbols.py`, `footprints.py`, `libtable.py`, `project.py`) | [02-project-library-model.md](02-project-library-model.md) |
| The Downloads watcher and processed-state (`watcher.py`, `state.py`) | [03-watcher.md](03-watcher.md) |
| CLI, config precedence, App wiring (`__main__.py`, `app/`) | [04-cli-and-config.md](04-cli-and-config.md) |
| The strata system model / V-model graph                  | [design/kicad-libsync.strata](../../design/kicad-libsync.strata) via [00-overview.md](00-overview.md#system-model-and-v-model-designkicad-libsyncstrata) |
| Tests for any module                                     | [05-testing-strategy.md](05-testing-strategy.md) |

## Locked decisions (do not re-litigate without asking the human)

- Libraries are PROJECT-LOCAL, one merged `<Lib>.kicad_sym` plus one
  `<Lib>.pretty` next to the `.kicad_pro`, registered via `${KIPRJMOD}` in
  the project `sym-lib-table` / `fp-lib-table`. Not the global tables.
- The watcher POLLS. `/mnt/c` (DrvFs) does not deliver inotify events.
- Idempotency is by zip content hash, recorded in a per-user state file.
- Only the Ultra Librarian `KiCADv6/` layout is recognized in v0.1; every
  other zip is logged at DEBUG and ignored.

See [00-overview.md](00-overview.md) for the reasoning behind each.
