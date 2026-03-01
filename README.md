# Ascertain Assessment (Backend)

Take-home assessment for the position of Full Stack Engineer at Ascertain. Python/FastAPI microservice for managing patients and patient notes, including file ingestion and summarization features.

What it does:

- Provides REST endpoints for CRUDing and summarizing patients and CRUDing patient notes.
- Stores data in an SQL database (PostgreSQL).
- Parses text and PDF SOAP note files (it would be trivial to add support for other formats).
- Uses OpenAI-compatible AI/LLM to summarize patient data.
- Abstracts third-party-library-dependent functions under interfaces, and provides access to them via dependency injection.
- Automated unit tests for most important parts of the code.
- Seeds database with sample data for easy testing (in dev only).

How it does it:

- Abstracts data management via repositories defined under `app/data/`.
  - Implementations use SQLModel.
- Abstracts and implements third-party, pluggable services via services under `app/services`.
  - AI/LLM requests are managed with `deepagents`.
- Encapsulates business logic with usecases defined under `usecases/`, which orchestrate the repositories and services.
- FastAPI application (`app/main.py`) exposes endpoints defined under `app/api/routes`.
- Dependency injection is managed with `dependency_injector`, using utility functions and containters in `app/ioc`.
- Uses Alembic to seed data in the database, based on sample JSON files.

## Project layout (high-level)

- `app/`: The code that's executed when the app is running
  - `main.py`: entry file; sets up FastAPI API.
  - `api/`: HTTP application layer: routes, middleware.
  - `data/`: Database adapter, repository interfaces and implementations.
  - `models/`: Domain models, DTOs, API schemas.
  - `services/`: Interfaces and implementations for specific functions using third-party libraries.
  - `usecases/`: Business logic orchestrations.
  - `utils/`: Small helper functions used across the project.
- `migrations/`: Alembic migrations and DB seeding.
- `tests/`: Unit tests and test assets.

The concept behind the codebase is:

- Cross-layer structures:
  - **Tooling interfaces** abstract/encapsulate functions used at all points of the code hierarchy (most notably, logging and DI).
  - **Models** specify the types the application is designed to handle, separating them by purpose, even at the cost of a certain repetition.
    - e.g., a `Patient` may seem identical to a `SQLPatient`, but the first represents the patient data as the application is to deal with it in general, while the second represents how patient data is stored in a SQL database.

- Layered code (top to bottom):
  - **Endpoint functions** mediate the HTTP requests with the application's usecases.
  - **Usecases classes** use repositories and services to actually do what the application is supposed to do.
  - bottom:
    - **Repositories interfaces** abstract access to the data itself, however that is done (via database, file, memory, another service, etc).
    - **Service interfaces** abstract access to third-party libraries used for specific purposes (e.g., converting files).

Check the other README.md files under the other folders for more details on the code defined there.

## Running the project

### Requirements:

- Python 3.11
- Docker
- OpenAI-compatible LLM API key
  - For testing purposes, you can get a free key on [groq](https://groq.com/):
    1. sign up
    1. in the console, select `API Keys`
    1. select button `Create API Key`

### Basic setup

1. Create and activate a virtualenv, to avoid library conflicts:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

**Note**: after installing dependencies, for some reason, it may happen that the virtualenv won't catch them. So, close the terminal window, open a new one and activate the virtualenv again to avoid issues.

3. Prepare .env files:
   - dev/prod: copy `.env.sample` as `.env` and fill variables with your own values
   - test: copy `.env.test.sample` as `.env.test` and fill variables with your own values

### Development

1. Run the app with hot reload:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

2. Open the interactive docs: http://localhost:8000/docs

**Note**: on first dev launch, sample data is seeded into the database. Check out `migrations/data/seed/*.json` for that data.

### Production

Build and run with the provided Dockerfile and `docker-compose.yml`:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

**Note**: Before deploying to prod, make sure the `ENV` variable in your .env file is either not present or set to "prod".

### Tests

Run the test suite with:

```bash
pytest -q -v
```

## Disclaimer on AI usage

The codebase architecture and most of the actual coding was done by me, "by hand". AI/LLM web chat (as well as plain-old Google Search) was used to solve the occasional question. Actual AI/LLM-assisted coding was used only when the code was suficiently mature and it seemed to me that describing to the AI what to do (and, more importantly, _how_ to do it) would be faster than doing so myself. Individual README.md files (except for this one) are mostly AI-written, with review by me.

## Areas of improvement

- Authentication - the API has no authentication.
  - The assessment description didn't mention it, not even as a stretch goal, so I chose to focus on what was actually described in there.
  - Adding authentication would have required adding a bunch more endpoints for both managing users and authenticating them, so it would definitely include a lot of code. Still, with the codebase as is, asking some AI to do these things based on the standard, conventions, and approaches already in place should yield a relatively decent result.
- Automated testing - I focused too much on the code architecture and implementations, so automated testing is only of the unit variety and doesn't cover the API part of the code.
- Database and AI/LLM flexibility - while the code allows configurable keys, credentials, and other types of value, it's designed to work only with PostgreSQL, for databases, and OpenAI-compatible LLMs.
  - Since the references to the actual database and the AI/LLM are abstracted each one by an interface, adding code to support other vendors should not require much, other than adding the vendor-specific settings and instantiating the vendor-specific implementations in the single place where they are defined.
- Full-text patient name search - the API supports only the most basic type of string matching, `LIKE '%value%'`.
  - Since this code is restricted to a single place and abstracted by an interface, adding full-text search in the interface's implementation should require more than a couple lines of code.
