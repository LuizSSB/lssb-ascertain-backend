# Models

Purpose

- Defines domain models, API schemas/DTOs, exceptions, and other general types used throught the application

Main components

- `*.py` - Models representing business logic data.
- `api/` - Pydantic schemas used for request/response payloads.
- `sql/` - SQLModel schemas used for modeling SQL tables.

Responsibilities

- Centralize domain definitions and validation rules.
- Provide serializable API schema models for controllers.
- Host reusable services for business workflows (e.g., summarization, file conversion).
