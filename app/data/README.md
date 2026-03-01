# Data layer

Purpose

- Implements database adapters and repository classes that perform persistence and retrieval operations.

Main components

- `sqldatabase.py` - Database connection helpers and adapters, using SQLAlchemy/SQLModel.
- `patient/` and `patient_note/` - interfaces and SQLAlchemy/SQLModel-specifics implementation for repositories to manage different types of app data.

Responsibilities

- Translate domain operations into SQL queries and ORM operations.
- Provide repository interfaces consumed by use-cases.
- Manage connections and sessions to the underlying database.
