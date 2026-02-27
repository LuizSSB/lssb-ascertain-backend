from typing import Any, Iterable, TypeVar, cast

_T = TypeVar("_T")


def flatten(array: Iterable[list[_T] | _T]) -> list[_T]:
    all = list[_T]()
    for item in array:
        if isinstance(item, list):
            all.extend(cast(Any, item))
        else:
            all.append(item)
    return all
