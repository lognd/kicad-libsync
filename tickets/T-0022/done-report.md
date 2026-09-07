## Done report

The repo now has a public remote and is headed for PyPI, so the docs had to stop being a private notebook.

Three things were wrong. (1) There was no user-facing answer to 'how do I configure the watcher' -- the precedence chain, the four config-file keys, the three env vars, and the autodetection rules only existed in the design docs and in from_external itself. docs/configuration.md now states all of it as a contract, including the deliberate omission of backfill/overwrite from the config file (both re-do or replace existing files, so they stay per-run opt-ins) and a troubleshooting table keyed to the actual ConfigError variants. (2) The README claimed Ultra Librarian only, which T-0021 made false -- SnapMagic flat-root exports have been supported since then, and the same stale claim was repeated in docs/index.md, docs/design/README.md, 01-vendor-zip-format.md and 05-testing-strategy.md. (3) The design docs carried the author's absolute paths and private board names.

release.yml existed but published whatever a tag pointed at. PyPI filenames are immutable, so a tag that disagrees with pyproject.toml cannot be taken back; the workflow now verifies tag == project.version before anything is built, re-runs the full gate against the tagged tree rather than trusting that main was green when the tag was cut, twine-checks metadata (otherwise invalid metadata is only discovered mid-upload), and publishes a built artifact via OIDC. make upload was a second, token-bearing publish path for the same artifact, so it now only bumps and pushes the tag -- one publish path, in CI.

Packaging metadata was also unpublishable: empty description, no urls/classifiers/authors, no LICENSE, and a py.typed declared in package-data that did not exist, so 'Typing :: Typed' would have shipped without the marker.

FLAGCOV001 remains unresolved repo-wide (frob's uv-tool venv cannot import kicad_libsync); pre-existing, filed as T-0023 rather than papered over.

### Changed
(no changed files detected)

### Evidence
(no evidence recorded)

### Captured claims
- tests: 0 passed (from 0 evidence id(s))
- gates: 0 error(s), 91 warning(s), 1 waived
- error-findings: none (measured, zero errors)
