# Services

Purpose

- Contains higher-level, reusable services reliant on external integrations.

Main components

- `file_conversion/` - Interface and implementation of service to convert files to formats useful to the application.
- `summarization/` - Interface and implementaion of service to generate summaries of application data.

Responsibilities

- Provide pluggable service implementations used by use-cases.
- Isolate third-party integration details (PDF parsing, LLMs, etc.) behind clear interfaces.
