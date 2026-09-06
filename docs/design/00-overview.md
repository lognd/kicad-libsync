# 00 -- Overview and Repo Layout

Read this first. It is the only doc with cross-cutting context.

## What this tool is

`kicad-libsync` is a global `uv tool` CLI. You point it at the KiCad
project you are currently working on and at a Downloads folder. Every time
a new zip lands in Downloads it checks whether the zip is a vendor KiCad
library export (a `footprints.pretty/` directory plus a `.kicad_sym`
schematic symbol library), and if so it copies the footprints into the
project's footprint library, merges the symbols into the project's symbol
library, fixes the symbol's `Footprint` property to point at that
library, and registers both libraries in the project lib tables. No more
doing it by hand.

Typical use (WSL, KiCad on Windows):

```bash
uv tool install /home/logan/projects/kicad-libsync
kicad-libsync watch --project /mnt/c/Users/logan/Projects/LLC/stpone-schematic
kicad-libsync import --project ... /mnt/c/Users/logan/Downloads/2N7002NXAKR.zip
```

## Locked decisions

| Decision | Choice | Why |
|---|---|---|
| Library location | Project-local `<Lib>.kicad_sym` + `<Lib>.pretty` next to the `.kicad_pro`, `${KIPRJMOD}` URIs in the project lib tables | The project is self-contained and portable (git clone works on any machine). The existing projects already do this (`Stpone.kicad_sym`, `Arduino_MountingHole.pretty`). The one-lib-per-part global userlibs approach that predates this tool pollutes the global tables and does not travel with the project. |
| Library name | Defaults to the `.kicad_pro` stem, overridable with `--lib-name` | One place to look; matches KiCad's own "project library" convention. |
| One merged symbol library | All vendor symbols are appended into the single project `.kicad_sym` | Ultra Librarian names each `.kicad_sym` after a timestamp, so keeping them separate produces meaningless library names. |
| Footprint reference rewrite | The symbol `Footprint` property becomes `<Lib>:<footprint>` | Vendor exports write a bare footprint name; KiCad needs `LIB:NAME` to resolve it. |
| Conflict policy | Existing symbol/footprint with the same name is SKIPPED with a WARNING unless `--overwrite` | Silently replacing a hand-edited symbol is worse than a warning. |
| Watching | Polling loop with a stability check (size unchanged across two polls) | DrvFs (`/mnt/c`) never delivers inotify events; a browser writes the zip incrementally. |
| Idempotency | SHA-256 of the zip recorded in `$XDG_STATE_HOME/kicad-libsync/processed.json` | The same zip must never be merged twice; re-downloads get a new mtime but the same hash. |
| Errors | typani `Result[T, E]` with `ErrorSet` variants; exceptions only for bugs | House rule. One malformed zip must not kill the watcher. |
| Runtime | Python 3.11+, stdlib `zipfile` + own s-expression parser, no KiCad Python API | The tool runs on WSL where `pcbnew` is not importable; `kicad-cli` is optional and never required. |

## Repo layout

```
kicad-libsync/
  src/kicad_libsync/
    __main__.py        argparse: watch | import | status   (04)
    app/
      app.py           App(cfg)() dispatch                 (04)
      config.py        AppConfig.from_external            (04)
    errors.py          every ErrorSet in one home
    sexpr.py           minimal s-expression parse/emit     (02)
    archive.py         zip -> VendorPackage               (01)
    project.py         KicadProject: paths + lib name     (02)
    libtable.py        sym-lib-table / fp-lib-table edit  (02)
    symbols.py         merge symbols into <Lib>.kicad_sym (02)
    footprints.py      copy .kicad_mod into <Lib>.pretty  (02)
    importer.py        archive -> project, ImportReport   (02)
    state.py           processed-hash ledger              (03)
    watcher.py         polling loop over Downloads        (03)
    logging/           house logging (get_logger)
  tests/
    unit/  integration/  system/                          (05)
    fixtures/           real vendor zips (small, checked in)
  docs/design/         these docs
  docs/index.md        frob doc anchors for the public API
```

## System model and V-model (`design/kicad-libsync.strata`)

`design/kicad-libsync.strata` is the machine-checked half of this plan:
the runtime topology (a foreign `downloads` store, the trusted `libsync`
process, the `project` and `state` stores, and the `archive.inspect`
trust boundary between them) plus the V-model spec graph. Every
`vmodel_node` on the left (requirement -> requirement-specification ->
system-specification -> system-design -> component-design) carries a
`code_ref` into `src/`, every `test` node on the right carries the pytest
node id that verifies its paired level, and `frob check` (VMOD001) refuses
an orphan requirement, an unjustified design element, or an artifact with
no paired-level test. `frob sys audit` checks the topology's capability
declarations against what the code actually does. The test harness is
its own `tests` node; its `exec`/`eval`/`fs`/`env` grants are `via`-scoped
to the files that use them, with the accepted site counts ratcheted in
`docs/design/registry/capability-via-ratchet.lock.json`.

## Data flow

```
Downloads/*.zip --(watcher: new + stable + not in state)--> archive.inspect
   --> VendorPackage{symbols: str, footprints: {name: str}}
   --> importer.import_package(project, pkg)
         footprints.copy_into(<Lib>.pretty)          -> added/skipped names
         symbols.merge_into(<Lib>.kicad_sym, lib)    -> added/skipped names
         libtable.ensure(sym-lib-table, fp-lib-table)
   --> ImportReport (logged at INFO, printed by the CLI)
   --> state.record(hash)
```

## Cross-cutting rules

- Every module gets a module logger via `kicad_libsync.logging.get_logger`.
  Log every zip seen, every recognition decision, every symbol/footprint
  added or skipped, every table edit, every state write.
- All writes to the project are atomic: write to a sibling temp file, then
  `os.replace`. KiCad may have the file open.
- Never touch files outside the project directory and the state file.

## errors

(`src/kicad_libsync/errors.py`)

One `ErrorSet` per module boundary: `SexprError`, `ArchiveError`,
`ProjectError`, `LibTableError`, `SymbolError`, `FootprintError`,
`StateError`, `ConfigError`. `SymbolError.SymbolInUse` is what `remove`
returns (docs/design/02-project-library-model.md#remover) when a
schematic still places the symbol and `--force` was not given. Variant
names are unique across ALL sets
because typani refuses to union two sets sharing a name, and
`importer.import_package` returns the union
`ArchiveError | SymbolError | FootprintError | LibTableError`. Every
variant string is the user-facing explanation; the CLI prints `str(err)`
plus any typani notes, nothing else.
