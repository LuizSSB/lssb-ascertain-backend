# Ascertain

This repository contains a FastAPI application with asynchronous SQLAlchemy and Alembic migrations.

## Development setup 🚀

You can run the service locally in development mode with hot reload enabled using Docker Compose. The `docker-compose.dev.yml` file overrides the base compose configuration to:

- mount the project directory into the container (`./:/app`),
- pass `RELOAD=true` to the startup script, and
- expose port `8000`.

### Starting the app

```bash
# build the image (only needed once or when dependencies change)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# or run detached
# docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
```

Once the container is running, edit any Python file anywhere in the repo and `uvicorn` will automatically restart the server.
You no longer need to remove images or containers when changing code.

### Notes

- The start script (`scripts/start.sh`) respects the `RELOAD` environment variable and only adds the reload flag when it is set to `true`.
- The `Dockerfile` now sets `WORKDIR /app` and copies the entire repo; the development compose mounts the same path over the image, so changes are visible immediately.
- You can still run `docker-compose` without the dev override for production builds.
