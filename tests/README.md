# Tests

Purpose

- Contains unit and integration tests, fixtures and test assets used to validate behavior.

Main components

- `conftest.py` - shared pytest fixtures and test configuration.
- `assets/` - sample files used in tests (e.g., sample notes, uploads).
- `data/`, `usecases/`, `services/` - tests organized by area under test.

Running tests

- Run `pytest -q -v` from the repository root. The test suite expects a virtualenv with project dependencies installed.
