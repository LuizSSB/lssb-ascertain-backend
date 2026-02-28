from types import ModuleType
from typing import cast

from app.ioc.containers import BaseAppContainer
from app.ioc.containers.default import DefaultAppContainer
from app.utils.collections import flatten
from app.utils.modules import get_module_filepaths

_active_container: tuple[type[BaseAppContainer], BaseAppContainer] | None = None


def _prepare_container():
    global _active_container

    if not _active_container:
        container_type = DefaultAppContainer
        container = container_type()
        _active_container = cast(tuple[type[BaseAppContainer], BaseAppContainer], (container_type, container))

    return _active_container


def ioc_setup_root(*, inject_packages: set[ModuleType]):
    container = _prepare_container()[1]
    container.wire(modules=flatten(get_module_filepaths(p) for p in inject_packages))


async def ioc_setup_lifecycle():
    container_type, container = _prepare_container()
    await container_type.lifecycle_setup(container)


def ioc_container_type():
    return _prepare_container()[0]


def ioc_container():
    return _prepare_container()[1]
