"""Minimal KiCad s-expression tree: parse, query, and emit in KiCad's line style."""

from __future__ import annotations

from dataclasses import dataclass, field

from typani import Err, Ok, Result

from kicad_libsync.errors import SexprError
from kicad_libsync.logging import get_logger

_log = get_logger(__name__)


# frob:doc docs/design/02-project-library-model.md#sexpr
# frob:tests tests/unit/test_sexpr.py::test_quoted_and_bare_atoms_are_distinguished
class Str(str):
    """A string that was quoted in the source and must be re-quoted on emit."""

    __slots__ = ()


# frob:doc docs/design/02-project-library-model.md#sexpr
# frob:tests tests/unit/test_sexpr.py::test_quoted_and_bare_atoms_are_distinguished
Atom = str  # a bare token; a quoted one is the Str subclass


# frob:doc docs/design/02-project-library-model.md#sexpr
# frob:tests tests/unit/test_sexpr.py::test_dumps_of_hand_built_node
@dataclass
class Node:
    """One parenthesized form: a bare head token followed by atoms and sub-forms."""

    head: str
    children: list[Node | Atom] = field(default_factory=list)

    # frob:doc docs/design/02-project-library-model.md#sexpr
    # frob:tests tests/unit/test_sexpr.py::test_find_all_is_direct_children_only
    def find_all(self, head: str) -> list[Node]:
        """Direct child forms whose head matches; never recursive."""
        return [c for c in self.children if isinstance(c, Node) and c.head == head]

    # frob:doc docs/design/02-project-library-model.md#sexpr
    # frob:tests tests/unit/test_sexpr.py::test_quoted_and_bare_atoms_are_distinguished
    def find(self, head: str) -> Node | None:
        """First direct child form with that head, or None."""
        found = self.find_all(head)
        return found[0] if found else None

    # frob:doc docs/design/02-project-library-model.md#sexpr
    # frob:tests tests/unit/test_sexpr.py::test_quoted_and_bare_atoms_are_distinguished
    def atoms(self) -> list[Atom]:
        """Direct child atoms in order (strings, quoted or bare)."""
        return [c for c in self.children if not isinstance(c, Node)]

    # frob:doc docs/design/02-project-library-model.md#sexpr
    # frob:tests tests/unit/test_sexpr.py::test_quoted_and_bare_atoms_are_distinguished
    def subforms(self) -> list[Node]:
        """Direct child forms in order."""
        return [c for c in self.children if isinstance(c, Node)]


_ESCAPES = {"n": "\n", "r": "\r", "t": "\t", '"': '"', "\\": "\\"}

_OPEN = "("
_CLOSE = ")"


# frob:doc docs/design/02-project-library-model.md#sexpr
# frob:tests tests/unit/test_sexpr.py::test_escapes_survive_round_trip
def quoted(s: str) -> str:
    """Wrap a string in KiCad quotes, escaping backslash, quote and newlines."""
    out = s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{out}"'


def _read_quoted(text: str, i: int) -> Result[tuple[Str, int], SexprError]:
    """Read a quoted string starting just past the opening quote."""
    n = len(text)
    buf: list[str] = []
    while i < n:
        c = text[i]
        if c == "\\":
            if i + 1 >= n:
                return Err(SexprError.UnexpectedEof)
            buf.append(_ESCAPES.get(text[i + 1], text[i + 1]))
            i += 2
        elif c == '"':
            return Ok((Str("".join(buf)), i + 1))
        else:
            buf.append(c)
            i += 1
    return Err(SexprError.UnexpectedEof)


def _tokenize(text: str) -> Result[list[str], SexprError]:
    tokens: list[str] = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch.isspace():
            i += 1
        elif ch in "()":
            tokens.append(ch)
            i += 1
        elif ch == '"':
            read = _read_quoted(text, i + 1)
            if isinstance(read, Err):
                return Err(read.danger_err)
            tok, i = read.danger_ok
            tokens.append(tok)
        else:
            j = i
            while j < n and not text[j].isspace() and text[j] not in '()"':
                j += 1
            tokens.append(text[i:j])
            i = j
    return Ok(tokens)


def _is_paren(tok: str, which: str) -> bool:
    return tok == which and not isinstance(tok, Str)


def _parse_form(tokens: list[str], pos: int) -> Result[tuple[Node, int], SexprError]:
    """Parse one form; pos points just past its opening paren."""
    if pos >= len(tokens):
        return Err(SexprError.UnexpectedEof)
    head = tokens[pos]
    if _is_paren(head, _CLOSE):
        return Err(SexprError.EmptyForm)
    if isinstance(head, Str) or _is_paren(head, _OPEN):
        return Err(SexprError.UnexpectedToken)
    node = Node(head)
    pos += 1
    while pos < len(tokens):
        tok = tokens[pos]
        if _is_paren(tok, _CLOSE):
            return Ok((node, pos + 1))
        if _is_paren(tok, _OPEN):
            # frob:invariant terminates reason="pos grows" measure="len(tokens)-pos"
            sub = _parse_form(tokens, pos + 1)
            if isinstance(sub, Err):
                return Err(sub.danger_err)
            child, pos = sub.danger_ok
            node.children.append(child)
        else:
            node.children.append(tok)
            pos += 1
    return Err(SexprError.UnexpectedEof)


# frob:doc docs/design/02-project-library-model.md#sexpr
# frob:tests tests/unit/test_sexpr.py::test_parse_round_trips_through_dumps
def parse(text: str) -> Result[Node, SexprError]:
    """Parse one top-level form; bare tokens stay str, quoted ones become Str."""
    tokenized = _tokenize(text)
    if isinstance(tokenized, Err):
        _log.debug("sexpr tokenize failed: %s", tokenized)
        return Err(tokenized.danger_err)
    tokens = tokenized.danger_ok
    if not tokens or not _is_paren(tokens[0], _OPEN):
        return Err(SexprError.UnexpectedToken)
    parsed = _parse_form(tokens, 1)
    if isinstance(parsed, Err):
        _log.debug("sexpr parse failed: %s", parsed)
        return Err(parsed.danger_err)
    node, end = parsed.danger_ok
    if end != len(tokens):
        return Err(SexprError.TrailingData)
    _log.debug("sexpr parsed %r with %d children", node.head, len(node.children))
    return Ok(node)


def _emit_atom(a: Atom) -> str:
    return quoted(a) if isinstance(a, Str) else a


def _emit(node: Node, depth: int, out: list[str]) -> None:
    """Children keep their source order: atoms before the first sub-form ride
    on the head line, later atoms get their own line so `(effects (font ..) hide)`
    round-trips instead of silently reordering to `(effects hide (font ..))`."""
    indent = "\t" * depth
    leading: list[str] = [node.head]
    rest: list[Node | Atom] = []
    for child in node.children:
        if rest or isinstance(child, Node):
            rest.append(child)
        else:
            leading.append(_emit_atom(child))
    head = " ".join(leading)
    if not rest:
        out.append(f"{indent}({head})")
        return
    out.append(f"{indent}({head}")
    for child in rest:
        if isinstance(child, Node):
            _emit(child, depth + 1, out)
        else:
            out.append(f"{indent}\t{_emit_atom(child)}")
    out.append(f"{indent})")


# frob:doc docs/design/02-project-library-model.md#sexpr
# frob:tests tests/unit/test_sexpr.py::test_parse_round_trips_through_dumps
def dumps(node: Node) -> str:
    """Emit KiCad-style text: atoms inline, one sub-form per tab-indented line."""
    out: list[str] = []
    _emit(node, 0, out)
    return "\n".join(out) + "\n"
