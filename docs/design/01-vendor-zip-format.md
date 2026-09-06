# 01 -- Vendor Zip Format (`archive.py`)

## Recognized layout (Ultra Librarian, KiCad v6+ export)

Observed in real downloads (see `tests/fixtures/`):

```
KiCADv6/2026-07-27_13-15-44.kicad_sym
KiCADv6/footprints.pretty/TO-236AB_SOT23_NEX.kicad_mod
KiCADv6/footprints.pretty/TO-236AB_SOT23_NEX-M.kicad_mod
KiCADv6/footprints.pretty/TO-236AB_SOT23_NEX-L.kicad_mod
```

Facts the parser relies on:

- Exactly one `*.kicad_sym` somewhere in the archive, one or more
  `*.kicad_mod` under a directory whose name ends in `.pretty`.
- The `.kicad_sym` is named after a timestamp, never after the part. The
  part name is the top-level `(symbol "NAME" ...)` inside it.
- Each symbol's `Footprint` property is the BARE footprint name
  (`TO-236AB_SOT23_NEX`), matching a `.kicad_mod` stem. `ki_fp_filters`
  lists the alternates (`-M`, `-L` density variants).
- Symbol file version is `20211014`; properties carry `(id N)` tokens that
  newer KiCad writers omit. KiCad 10 still reads them.
- Optional `3D/*.step` (not present in the sampled zips).

## Recognition rules

### inspect

`inspect(zip_path) -> Result[VendorPackage, ArchiveError]`

1. Not a valid zip -> `ArchiveError.NotAZip`.
2. Zero `.kicad_sym` entries -> `ArchiveError.NoSymbolLibrary`.
   More than one -> `ArchiveError.AmbiguousSymbolLibrary`.
3. Zero `.kicad_mod` entries under a `*.pretty/` directory ->
   `ArchiveError.NoFootprints`.
4. Any entry path that escapes (absolute or contains `..`) ->
   `ArchiveError.UnsafePath`. Never extract to disk; read members into
   memory only.
5. Members are decoded as UTF-8; failure -> `ArchiveError.NotUtf8`.

Directory prefix (`KiCADv6/`) is NOT required: the rules match on suffixes
so a future SnapEDA/SamacSys export that happens to ship the same two
pieces is accepted, and a zip of photos is rejected at rule 2.

## Output model

### VendorPackage

```python
class VendorPackage(BaseModel):
    model_config = {}
    source: Path  # the zip
    symbols_text: str  # the whole .kicad_sym
    footprints: dict[str, str]  # stem -> .kicad_mod text
    models: dict[str, bytes] = {}  # stem -> STEP bytes (reserved, T-3D)
```

The watcher calls `inspect` on every zip; a rejection at rule 2 or 3 is
the normal "not for us" outcome and is logged at DEBUG, everything else at
WARNING.
