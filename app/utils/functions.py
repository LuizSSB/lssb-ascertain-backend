import functools
from typing import Any, Callable, TypeVar

_TReturn = TypeVar("_TReturn")


def run_once(func: Callable[[], _TReturn]) -> Callable[[], _TReturn]:
    result: _TReturn | None = None
    is_executed = False

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        nonlocal result, is_executed
        if not is_executed:
            result = func(*args, **kwargs)
            is_executed = True
        return result

    return wrapper
