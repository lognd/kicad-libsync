# Configuring the watcher

`kicad-libsync watch` polls a Downloads folder and merges every new vendor
KiCad library zip into one KiCad project. It needs to know two things --
**which folder to watch** and **which project to merge into** -- plus a few
optional knobs. This page covers every way to supply them.

## Precedence

Settings are layered. Highest wins:

1. **CLI flags** (`--downloads`, `--project`, ...)
2. **Environment variables** (`KICAD_LIBSYNC_*`, including anything in a
   `.env` file in the working directory -- it is loaded at startup)
3. **Config file** (`~/.config/kicad-libsync/config.toml`)
4. **Autodetection** (Downloads folder only)

So a config file gives you the everyday defaults, and a flag overrides it
for one run without editing anything.

## Quick start

```bash
mkdir -p ~/.config/kicad-libsync
cat > ~/.config/kicad-libsync/config.toml <<'EOF'
project      = "/mnt/c/Users/<you>/Projects/<board>"
downloads    = "/mnt/c/Users/<you>/Downloads"
poll_seconds = 2.0
EOF

kicad-libsync watch
```

Leave that running in a terminal. Download a part from Ultra Librarian or
SnapMagic; a few seconds after the zip finishes writing, its footprints and
symbols are in your project and registered in the project lib tables.

## Config file

Path: `~/.config/kicad-libsync/config.toml`. It is optional; a missing file
is not an error. The path is fixed -- there is no `--config` flag. If the
file exists but is not valid TOML, the run exits 2 with
`ConfigError.BadConfigFile` rather than silently ignoring it.

Only these four keys are read from the file. Anything else in it is
ignored, so you can keep comments and notes there freely.

| Key | Type | Default | Meaning |
|---|---|---|---|
| `project` | string (path) | `"."` | Root of the KiCad project to merge into -- the directory containing the `.kicad_pro`. |
| `downloads` | string (path) | autodetected | Folder to poll for new vendor zips. |
| `lib_name` | string | the `.kicad_pro` stem | Name of the project-local library, i.e. `<lib_name>.kicad_sym` and `<lib_name>.pretty`. |
| `poll_seconds` | float | `2.0` | Seconds between polls. Must be `> 0`; a non-positive value exits 2 with `ConfigError.BadPoll`. |

A full example:

```toml
# The KiCad project to merge parts into. Relative paths resolve against
# the current working directory, so an absolute path is safer here.
project = "/mnt/c/Users/<you>/Projects/<board>"

# Where the browser drops vendor zips. Omit this to let the tool detect it.
downloads = "/mnt/c/Users/<you>/Downloads"

# Library name. Omit to use the .kicad_pro stem, which is usually right.
lib_name = "VendorParts"

# Poll interval. 2s is responsive without being busy; raise it on a slow
# network mount.
poll_seconds = 2.0
```

The boolean switches (`backfill`, `overwrite`) are deliberately **not**
config-file keys -- both change or re-do existing files, so they are
per-run flags you opt into explicitly.

## Environment variables

Useful for per-shell or per-project overrides, and for CI. These are read
from the real environment and from a `.env` file in the working directory
(loaded via `python-dotenv` at startup).

| Variable | Overrides |
|---|---|
| `KICAD_LIBSYNC_PROJECT` | `project` |
| `KICAD_LIBSYNC_DOWNLOADS` | `downloads` |
| `KICAD_LIBSYNC_POLL` | `poll_seconds` |

```bash
KICAD_LIBSYNC_PROJECT=~/boards/psu kicad-libsync watch
```

There is no env var for `lib_name` or for the boolean flags; use the config
file or a flag.

## CLI flags

```
kicad-libsync watch [--project P] [--downloads D] [--lib-name L] [--poll S] [--backfill] [--overwrite]
```

| Flag | Default | Meaning |
|---|---|---|
| `--project P` | `.` | Root of the KiCad project to merge into. |
| `--downloads D` | autodetected | Folder to poll. |
| `--lib-name L` | `.kicad_pro` stem | Project library name. |
| `--poll S` | `2.0` | Seconds between polls; must be positive. |
| `--backfill` | off | On startup, run every zip already sitting in Downloads through the importer once. Without it, pre-existing zips are marked seen and skipped, and only zips that appear *after* startup are imported. |
| `--overwrite` | off | Replace an existing symbol or footprint of the same name instead of skipping it with a warning. Overwrites hand-edited symbols, so it is off by default. |

The sibling commands take the same `--project` and share the config file
and env layering:

```
kicad-libsync import [--project P] [--lib-name L] [--overwrite] ZIP [ZIP ...]
kicad-libsync status [--project P]
kicad-libsync remove [--project P] [--keep-footprints] [--force] NAME [NAME ...]
```

## Downloads autodetection

If no `downloads` is given anywhere, the tool tries to find one:

1. Each `/mnt/c/Users/*/Downloads` that exists, excluding the Windows
   system accounts `Public`, `Default`, `Default User`, `All Users`, and
   `WsiAccount`. If **exactly one** remains, it is used. If several do, the
   tool refuses to guess and logs a warning.
2. Otherwise `~/Downloads`, if it exists.
3. Otherwise `watch` exits 2 with `ConfigError.NoDownloadsDir`. (The
   `import`, `status`, and `remove` commands do not need a Downloads
   folder, so they proceed.)

Step 1 only helps under WSL with a Windows-side browser. On a native Linux
or Windows install, detection falls through to `~/Downloads`.

The folder that was actually resolved is logged at INFO on every run, so
the first line of `watch` output tells you what is being watched.

## What the watcher does per poll

Each tick globs `*.zip` in the Downloads folder and skips names starting
with `~` or ending in `.crdownload`/`.part`. A new zip is not touched until
its `(size, mtime)` is unchanged across two consecutive polls -- that is
the "download finished" signal, since a browser writes the file
incrementally. A stable zip is hashed; if that hash has already been merged
into this project it is skipped, otherwise it is inspected, and if it is a
recognized vendor export it is imported and a one-line report is printed.
A zip that is not a library export is logged at DEBUG and ignored. An
import error is logged at ERROR with the zip name and the loop continues --
one bad zip never kills the watcher.

Stop the watcher with Ctrl-C.

## Processed state

Idempotency is by zip content hash, keyed by project root, in a per-user
ledger:

```
$XDG_STATE_HOME/kicad-libsync/processed.json    # or ~/.local/state/... if unset
```

Because the key includes the project root, importing the same zip into a
second project is a legitimate re-import, not a duplicate. To force a
re-import into the same project, delete that zip's entry from the ledger
(or the whole file -- it is a cache, not a source of truth) and re-run with
`--backfill`.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| Exits 2 immediately, "no Downloads directory given and none could be detected" | Autodetection found nothing. Set `downloads` in the config file or pass `--downloads`. |
| Exits 2, "config file ... did not parse as TOML" | Syntax error in `~/.config/kicad-libsync/config.toml`. |
| Exits 2, "poll interval must be positive" | `poll_seconds` / `--poll` is zero or negative. |
| "multiple candidate Downloads dirs" warning, then exit 2 | More than one Windows user profile has a Downloads folder. Name the one you want explicitly. |
| Zips land but nothing is imported | They were already in the folder at startup -- restart with `--backfill`, or check DEBUG logs for "not a library zip". |
| A symbol is skipped with a warning | A symbol of that name already exists. Re-run that zip with `import --overwrite` if you really want to replace it. |
| Nothing happens on a network or DrvFs mount | Raise `poll_seconds`; the stability check needs two polls to agree, so a slow write takes at least two intervals. |

## See also

- [design/04-cli-and-config.md](design/04-cli-and-config.md) -- the config
  layering and `AppConfig` as a spec.
- [design/03-watcher.md](design/03-watcher.md) -- the poll loop and
  processed-state design.
