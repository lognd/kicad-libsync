# 02 -- Project Library Model

Covers `sexpr.py`, `project.py`, `libtable.py`, `symbols.py`,
`footprints.py`, `importer.py`.

## sexpr

(`src/kicad_libsync/sexpr.py`)

KiCad files are s-expressions. We need: parse into a tree, find nodes,
edit a string leaf, emit back. Round-trip fidelity of untouched formatting
is NOT a goal; KiCad rewrites the file on save anyway. Emit uses KiCad's
one-child-per-line style so diffs stay readable.

```python
Atom = str                 # bare token, kept verbatim (numbers are NOT converted)
class Str(str): ...        # a token that was quoted in the source
class Node:                # (head child child ...)
    head: str
    children: list[Node | Atom]
    def find_all(self, head) -> list[Node]   # direct child forms with that head
    def find(self, head) -> Node | None
    def atoms(self) -> list[Atom]            # direct child atoms
    def subforms(self) -> list[Node]         # direct child forms
def parse(text: str) -> Result[Node, SexprError]        # one top-level form
def dumps(node: Node) -> str
def quoted(s: str) -> str                               # KiCad string escaping
```

Strings keep the distinction "was quoted" vs "bare token" so `(version
20211014)` emits a bare token and `(property "Footprint" "X")` keeps its
quotes. Numbers are deliberately left as their source text: converting
`1.27` to a float and back could change KiCad's formatting for no gain.
Parse errors are `SexprError` values, never exceptions.

## project

(`src/kicad_libsync/project.py`)

```python
class KicadProject(BaseModel):
    root: Path            # directory containing the .kicad_pro
    name: str             # .kicad_pro stem
    lib_name: str         # defaults to name
    sym_lib: Path         # root / f"{lib_name}.kicad_sym"
    fp_lib: Path          # root / f"{lib_name}.pretty"
    sym_table: Path       # root / "sym-lib-table"
    fp_table: Path        # root / "fp-lib-table"

def locate(path: Path, lib_name: str | None = None) -> Result[KicadProject, ProjectError]
```

`locate` accepts a directory or a `.kicad_pro` path. A directory with zero
`.kicad_pro` -> `ProjectError.NotAProject`; more than one and no explicit
file -> `ProjectError.AmbiguousProject`.

## libtable

(`src/kicad_libsync/libtable.py`)

Both files share one grammar:

```
(sym_lib_table (version 7)
  (lib (name "X") (type "KiCad") (uri "${KIPRJMOD}/X.kicad_sym") (options "") (descr "")))
```

`ensure_entry(table_path, kind, lib_name, uri) -> Result[bool, LibTableError]`
returns `Ok(True)` when it wrote a new entry, `Ok(False)` when the name was
already registered. Missing file -> create with `(version 7)`.

`entries(table_path) -> Result[list[tuple[str, str]], LibTableError]` returns
the `(name, uri)` pairs already registered, for `status` to display later.

Name
present with a DIFFERENT uri -> leave alone, return `Ok(False)`, WARNING
(the user pointed the name somewhere on purpose).

## symbols

(`src/kicad_libsync/symbols.py`)

`merge_into(lib_path, lib_name, vendor_text, overwrite) -> Result[MergeOutcome, SymbolError]`

1. Parse vendor text; collect top-level `(symbol "NAME" ...)` children.
   Sub-units (`NAME_0_1`, `NAME_1_1`) are nested inside their parent in
   the v6 format, so only direct children of `kicad_symbol_lib` count.
2. For each symbol rewrite `(property "Footprint" "FP")` to
   `"<lib_name>:FP"` when FP is non-empty and contains no `:` already.
   Leave `ki_fp_filters` alone (it is a name filter, not a reference).
3. When `lib_path` is missing on disk, start from
   `(kicad_symbol_lib (version 20211014) (generator "kicad-libsync"))`.
   If it exists, parse it and append. Existing names: skip + WARNING, or
   replace when `overwrite`.
4. Emit atomically.

`MergeOutcome(added: list[str], skipped: list[str], replaced: list[str])`,
a pydantic model defined once in `symbols.py` and reused (imported, never
duplicated) by `footprints.py`.

## footprints

(`src/kicad_libsync/footprints.py`)

`copy_into(pretty_dir, footprints, overwrite) -> Result[MergeOutcome, FootprintError]`.
`footprints` maps a footprint stem to its `.kicad_mod` text; each entry is
written as `<stem>.kicad_mod`. Create the directory if needed. Same
skip/overwrite policy as symbols. Each file written atomically.

## importer

<!-- frob:waive DOC006 reason="future-facing: importer.py is built by T-0006" -->

(`src/kicad_libsync/importer.py`)

```python
class ImportReport(BaseModel):
    source: Path
    symbols: MergeOutcome
    footprints: MergeOutcome
    sym_table_added: bool
    fp_table_added: bool

def import_package(project, pkg, overwrite=False) -> Result[ImportReport, ImportError]
```

Order: footprints first, then symbols, then tables. A failure in a later
stage leaves earlier stages applied -- footprints on disk without a symbol
are harmless, the reverse would reference a missing footprint. `ImportError`
is the union `ArchiveError | SymbolError | FootprintError | LibTableError`.
