"""Unit tests for the minimal s-expression parser/emitter."""

from typani import Err, Ok

from kicad_libsync.errors import SexprError
from kicad_libsync.sexpr import Node, Str, dumps, parse, quoted

SAMPLE = """(kicad_symbol_lib (version 20211014) (generator kicad_symbol_editor)
  (symbol "Q1" (in_bom yes)
    (property "Footprint" "TO-236AB" (id 2) (at 0 0 0)
      (effects (font (size 1.27 1.27) italic) hide)
    )
    (property "Esc" "a \\"b\\" \\\\ c" (id 3))
  )
)
"""


def test_parse_round_trips_through_dumps() -> None:
    # frob:tests src/kicad_libsync/sexpr.py::parse kind="unit"
    # frob:tests src/kicad_libsync/sexpr.py::dumps kind="unit"
    first = parse(SAMPLE).unwrap()
    text = dumps(first)
    second = parse(text).unwrap()
    assert first == second
    assert text.startswith("(kicad_symbol_lib\n\t(version 20211014)\n")
    assert dumps(second) == text


def test_quoted_and_bare_atoms_are_distinguished() -> None:
    # frob:tests src/kicad_libsync/sexpr.py::Node.atoms kind="unit"
    # frob:tests src/kicad_libsync/sexpr.py::Node.find kind="unit"
    root = parse(SAMPLE).unwrap()
    version = root.find("version")
    assert version is not None
    assert version.atoms() == ["20211014"]
    assert not isinstance(version.atoms()[0], Str)
    symbol = root.find("symbol")
    assert symbol is not None
    assert isinstance(symbol.atoms()[0], Str)
    assert symbol.atoms()[0] == "Q1"
    # frob:tests src/kicad_libsync/sexpr.py::Node.subforms kind="unit"
    assert [n.head for n in root.subforms()] == ["version", "generator", "symbol"]


def test_find_all_is_direct_children_only() -> None:
    # frob:tests src/kicad_libsync/sexpr.py::Node.find_all kind="unit"
    root = parse(SAMPLE).unwrap()
    assert root.find_all("property") == []
    symbol = root.find("symbol")
    assert symbol is not None
    assert [p.atoms()[0] for p in symbol.find_all("property")] == ["Footprint", "Esc"]


def test_escapes_survive_round_trip() -> None:
    # frob:tests src/kicad_libsync/sexpr.py::quoted kind="unit"
    root = parse(SAMPLE).unwrap()
    symbol = root.find("symbol")
    assert symbol is not None
    esc = symbol.find_all("property")[1]
    assert esc.atoms()[1] == 'a "b" \\ c'
    assert quoted('a "b" \\ c') == '"a \\"b\\" \\\\ c"'
    assert parse(dumps(root)).unwrap() == root


def test_parse_errors_are_values() -> None:
    # frob:tests src/kicad_libsync/sexpr.py::parse kind="unit"
    assert parse("(a (b)") == Err(SexprError.UnexpectedEof)
    assert parse('(a "unterminated') == Err(SexprError.UnexpectedEof)
    assert parse("(a) (b)") == Err(SexprError.TrailingData)
    assert parse("()") == Err(SexprError.EmptyForm)
    assert parse("bare") == Err(SexprError.UnexpectedToken)
    assert parse('("quoted head")') == Err(SexprError.UnexpectedToken)


def test_dumps_of_hand_built_node() -> None:
    # frob:tests src/kicad_libsync/sexpr.py::Node kind="unit"
    node = Node(
        "lib", [Node("version", ["7"]), Node("lib", [Node("name", [Str("X")])])]
    )
    assert dumps(node) == '(lib\n\t(version 7)\n\t(lib\n\t\t(name "X")\n\t)\n)\n'
    assert isinstance(parse(dumps(node)), Ok)
