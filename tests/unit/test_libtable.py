"""Unit tests for libtable.ensure_entry and libtable.entries."""

from pathlib import Path

from kicad_libsync.libtable import ensure_entry, entries

SAMPLE_FP_TABLE = """(fp_lib_table
  (version 7)
  (lib (name "Arduino_MountingHole")(type "KiCad")(uri "${KIPRJMOD}/Arduino_MountingHole.pretty")(options "")(descr ""))
)
"""


def test_ensure_entry_creates_missing_table(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/libtable.py::ensure_entry kind="unit"
    table = tmp_path / "fp-lib-table"
    added = ensure_entry(table, "fp", "Widget", "${KIPRJMOD}/Widget.pretty").unwrap()
    assert added is True
    assert table.exists()
    text = table.read_text()
    assert text.startswith("(fp_lib_table")
    assert "(version 7)" in text
    assert "Widget" in text


def test_ensure_entry_twice_yields_one_entry(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/libtable.py::ensure_entry kind="unit"
    table = tmp_path / "fp-lib-table"
    first = ensure_entry(table, "fp", "Widget", "${KIPRJMOD}/Widget.pretty").unwrap()
    second = ensure_entry(table, "fp", "Widget", "${KIPRJMOD}/Widget.pretty").unwrap()
    assert first is True
    assert second is False
    pairs = entries(table).unwrap()
    assert pairs == [("Widget", "${KIPRJMOD}/Widget.pretty")]


def test_ensure_entry_appends_to_existing_table(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/libtable.py::ensure_entry kind="unit"
    table = tmp_path / "fp-lib-table"
    table.write_text(SAMPLE_FP_TABLE)
    added = ensure_entry(table, "fp", "Widget", "${KIPRJMOD}/Widget.pretty").unwrap()
    assert added is True
    pairs = entries(table).unwrap()
    assert ("Arduino_MountingHole", "${KIPRJMOD}/Arduino_MountingHole.pretty") in pairs
    assert ("Widget", "${KIPRJMOD}/Widget.pretty") in pairs
    assert len(pairs) == 2


def test_ensure_entry_same_name_different_uri_warns_and_skips(
    tmp_path: Path, caplog
) -> None:
    # frob:tests src/kicad_libsync/libtable.py::ensure_entry kind="unit"
    table = tmp_path / "fp-lib-table"
    ensure_entry(table, "fp", "Widget", "${KIPRJMOD}/Widget.pretty").unwrap()
    with caplog.at_level("WARNING"):
        added = ensure_entry(table, "fp", "Widget", "${KIPRJMOD}/Other.pretty").unwrap()
    assert added is False
    pairs = entries(table).unwrap()
    assert pairs == [("Widget", "${KIPRJMOD}/Widget.pretty")]
    assert any("different uri" in record.message for record in caplog.records)


def test_entries_returns_name_uri_pairs(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/libtable.py::entries kind="unit"
    table = tmp_path / "fp-lib-table"
    table.write_text(SAMPLE_FP_TABLE)
    pairs = entries(table).unwrap()
    assert pairs == [
        ("Arduino_MountingHole", "${KIPRJMOD}/Arduino_MountingHole.pretty")
    ]


def test_entries_on_missing_table_is_empty(tmp_path: Path) -> None:
    # frob:tests src/kicad_libsync/libtable.py::entries kind="unit"
    table = tmp_path / "sym-lib-table"
    pairs = entries(table).unwrap()
    assert pairs == []
