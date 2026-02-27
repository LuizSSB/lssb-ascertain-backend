from abc import ABC
from typing import TypeVar

_T = TypeVar("_T")


def is_abstract(clazz: type) -> bool:
    return ABC in clazz.__bases__


def get_all_subclasses(clazz: type[_T], *, depth: int | None = None, includes_abc: bool = True) -> set[type[_T]]:
    subclasses = set(c for c in clazz.__subclasses__())

    if depth == 0:
        return subclasses

    for subclass in list(subclasses):
        if depth is None:
            subclasses.update(get_all_subclasses(subclass, depth=None))
        else:
            subclasses.update(get_all_subclasses(subclass, depth=depth - 1))

    if not includes_abc:
        return {s for s in subclasses if not is_abstract(s)}

    return subclasses


def unpack(value: _T | None, default: _T | None = None) -> _T:
    if value is not None:
        return value
    if default is not None:
        return default
    raise Exception("Trying to unpack nil value, with no fallback")
