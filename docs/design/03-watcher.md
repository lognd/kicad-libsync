# 03 -- Watcher and Processed State

## state.py

```python
class ProcessedState(BaseModel):
    model_config = {}
    version: int = 1
    hashes: dict[str, str] = {}   # sha256 -> "<zip name> @ <iso time> -> <project root>"

def state_path() -> Path        # $XDG_STATE_HOME or ~/.local/state, /kicad-libsync/processed.json
def load(path) -> Result[ProcessedState, StateError]   # missing file -> empty state
def save(path, state) -> Result[None, StateError]      # atomic
def sha256_of(path) -> Result[str, StateError]
```

State is per-user, not per-project: a zip merged into project A and then
wanted in project B is a legitimate re-import, so the hash key includes
the project root (`sha256 + ":" + str(project.root)`).

## watcher.py

`watch(cfg, project, state) -> Unreachable` (async, `asyncio.run` from App).

Loop every `poll_seconds` (default 2):

1. `Downloads.glob("*.zip")`, skip names starting with `~` or ending in
   `.crdownload`/`.part` (browser temp names are not `.zip`, but the
   glob is cheap insurance).
2. For each candidate not already processed or pending: record
   `(size, mtime)`. A candidate is STABLE when the pair is unchanged since
   the previous poll -- the download has finished.
3. For a stable candidate: hash; if `hash:project` is in the state, mark
   seen and skip. Otherwise `archive.inspect`; on
   `NoSymbolLibrary`/`NoFootprints` log DEBUG "not a library zip", record
   in an in-memory `ignored` set (do not hash-record: the file might be
   replaced), continue. On success `importer.import_package`, then
   `state.record`, print the report.
4. On startup, existing zips are treated as already-seen unless
   `--backfill` is given, in which case each is run through step 3 once.

Every poll that finds a new name logs it at INFO. Errors from import are
logged at ERROR with the zip name and the loop continues.

## Why not watchfiles / inotify

DrvFs mounts (`/mnt/c`) do not forward Windows change notifications to
Linux inotify. `watchfiles` falls back to polling internally but hides the
stability check; a hand-rolled loop is ~60 lines and fully testable with
`tmp_path`.
