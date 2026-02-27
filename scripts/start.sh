#!/bin/bash
set -e

# 1. Define variables with defaults
# Syntax ${VAR:-default} uses 'default' if VAR is unset or empty
APP_HOST=${HOST:-0.0.0.0}
APP_PORT=${PORT:-8000}
RELOAD_FLAG=""

# 2. Logic for Hot Reload
# If RELOAD is set to "true", append the --reload flag
if [ "$RELOAD" = "true" ]; then
    echo "Development mode: Hot reload enabled."
    RELOAD_FLAG="--reload"
else
    echo "Production mode: Hot reload disabled."
fi

# 3. Run migrations
echo "Running migrations..."
# alembic upgrade head

# 4. Execute FastAPI
# Using 'exec' ensures the app receives Unix signals (like SIGTERM) directly
echo "Starting FastAPI on $APP_HOST:$APP_PORT..."
cd app
exec uvicorn main:app \
    --host "$APP_HOST" \
    --port "$APP_PORT" \
    $RELOAD_FLAG