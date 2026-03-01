# Migrations

Purpose

- Database migration scripts and Alembic configuration.

Main components

- `env.py`, `script.py.mako`: Alembic environment and templating files.
- `versions/`: Migration scripts;
- `data/seed`: holds seed data JSON files.

Responsibilities

- Version and evolve the database schema. Use Alembic commands to create/apply migrations.
