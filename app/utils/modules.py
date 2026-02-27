from pathlib import Path
from types import ModuleType


def get_module_filepaths(module: ModuleType) -> set[str]:
    """
    Recursively return dotted module paths for all .py files inside a module/package.

    Works with:
    - regular packages
    - namespace packages (PEP 420)
    - with or without __init__.py

    Rules:
    - Paths start with module.__name__
    - Components separated by "."
    - Remove ".py"
    - Omit "__init__"
    """
    if not hasattr(module, "__path__"):
        # Single file module
        return {module.__name__}

    results = set[str]()

    for base_dir in module.__path__:
        base_path = Path(base_dir)

        for path in base_path.rglob("*.py"):
            relative = path.relative_to(base_path)
            parts = list(relative.parts)

            parts[-1] = parts[-1].removesuffix(".py")

            if parts[-1] == "__init__":
                parts = parts[:-1]

            dotted = ".".join([module.__name__] + parts) if parts else module.__name__

            results.add(dotted)

    return results
