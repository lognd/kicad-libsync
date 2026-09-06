# kicad-libsync

Watch your Downloads folder and merge vendor KiCad library zips (Ultra
Librarian `KiCADv6/` exports: `footprints.pretty/` + a `.kicad_sym`) into
the KiCad project you are working on -- footprints into `<Lib>.pretty`,
symbols into `<Lib>.kicad_sym`, both registered in the project lib tables.

```bash
uv tool install /home/logan/projects/kicad-libsync
kicad-libsync watch --project /mnt/c/Users/logan/Projects/LLC/stpone-schematic
kicad-libsync import --project . vendor-package.zip
kicad-libsync status --project .
kicad-libsync remove --project . SOME_PART
```

Design docs: [docs/design/](docs/design/README.md).

## Quick start

```bash
uv sync
cp .env.example .env   # fill in real values; .env is gitignored
frob check              # lint + typecheck + test + the full frob gate
```

## Development

This is a frob-enabled project: `frob <verb>` is the interface, not a
`make` wrapper around it.

```bash
frob test        # select and run tests for the touched set (or --all)
frob format       # ruff check --fix + ruff format
frob coverage     # refresh coverage.xml / the coverage stamp
frob check        # the aggregate gate: ruff, ty, frob cycle/dup/arch/...
```

`make install`/`make clean`/`make upload` remain (bootstrap and
build/publish -- see the Makefile).
