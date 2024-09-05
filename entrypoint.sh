#!/bin/sh

MIGRATION_FLAG="/app/migration_done"

if [ ! -f "$MIGRATION_FLAG" ]; then
    echo "Running database migrations..."
    poetry run alembic upgrade head
    touch "$MIGRATION_FLAG"
else
    echo "Migrations have already been run."
fi

exec poetry run uvicorn setup:app --host 0.0.0.0
