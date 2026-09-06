"""The one property errors.py promises: variant names never collide across sets."""

from typani import ErrorSet

from kicad_libsync import errors


def _sets() -> list[type[ErrorSet]]:
    return [
        obj
        for obj in vars(errors).values()
        if isinstance(obj, type) and issubclass(obj, ErrorSet) and obj is not ErrorSet
    ]


def test_variant_names_are_unique_across_sets() -> None:
    # frob:tests src/kicad_libsync/errors.py kind="unit"
    seen: dict[str, str] = {}
    for es in _sets():
        for name in vars(es):
            if name.startswith("_"):
                continue
            assert name not in seen, f"{es.__name__}.{name} also in {seen[name]}"
            seen[name] = es.__name__
    assert len(_sets()) == 8


def test_every_pair_of_sets_unions() -> None:
    # frob:tests src/kicad_libsync/errors.py kind="unit"
    sets = _sets()
    for a in sets:
        for b in sets:
            if a is not b:
                assert a | b is not None
