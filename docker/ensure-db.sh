#!/bin/sh
set -e

# This script ensures the database exists before running Flyway migrations
# It connects to the postgres database and creates the target database if needed
# PGPASSWORD environment variable should be set for authentication

DB_NAME="${POSTGRES_DB:-aura_db}"
DB_USER="${POSTGRES_USER:-aura}"

echo "Ensuring database ${DB_NAME} exists..."

# Check if database exists, create if it doesn't
# PGPASSWORD is set via environment variable in docker-compose
psql -h postgres -U "${DB_USER}" -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '${DB_NAME}'" | grep -q 1 || \
psql -h postgres -U "${DB_USER}" -d postgres -c "CREATE DATABASE \"${DB_NAME}\""

# Also ensure database matching username exists (for default connections)
if [ "${DB_NAME}" != "${DB_USER}" ]; then
    echo "Ensuring database ${DB_USER} exists (for default connections)..."
    psql -h postgres -U "${DB_USER}" -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '${DB_USER}'" | grep -q 1 || \
    psql -h postgres -U "${DB_USER}" -d postgres -c "CREATE DATABASE \"${DB_USER}\""
fi

echo "Database ${DB_NAME} is ready."
