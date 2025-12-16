#!/bin/bash
set -e

# Wait for database to be ready (only if DB_HOST is set, otherwise assume cloud DB)
if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ] && [ -n "$DB_USER" ]; then
  echo "Waiting for database..."
  while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
    echo "Database is unavailable - sleeping"
    sleep 2
  done
  echo "Database is up - continuing"
elif [ -n "$DATABASE_URL" ]; then
  echo "Using DATABASE_URL for database connection (cloud/managed database)"
  # For cloud databases (like Neon), we skip pg_isready check
  # The application will handle connection retries
else
  echo "Warning: No database configuration found (DB_HOST or DATABASE_URL)"
fi

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Execute the command
exec "$@"
