#!/bin/bash
set -e

# This script ensures the database exists
# It runs when PostgreSQL container is first initialized

# Default to aura_db if not set
POSTGRES_DB="${POSTGRES_DB:-aura_db}"
POSTGRES_USER="${POSTGRES_USER:-aura}"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres <<-EOSQL
    -- Create main database if it doesn't exist
    SELECT 'CREATE DATABASE "$POSTGRES_DB"'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$POSTGRES_DB')\gexec

    -- Create database matching username (for default connections)
    -- This prevents "database does not exist" errors when connecting without specifying dbname
    SELECT 'CREATE DATABASE "$POSTGRES_USER"'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$POSTGRES_USER')\gexec

    -- Grant privileges on both databases
    GRANT ALL PRIVILEGES ON DATABASE "$POSTGRES_DB" TO "$POSTGRES_USER";
    GRANT ALL PRIVILEGES ON DATABASE "$POSTGRES_USER" TO "$POSTGRES_USER";
EOSQL

# Enable pgvector extension in the main database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Enable pgvector extension for vector similarity search
    CREATE EXTENSION IF NOT EXISTS vector;
EOSQL

# Also enable pgvector in the user database (for consistency)
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_USER" <<-EOSQL
    -- Enable pgvector extension for vector similarity search
    CREATE EXTENSION IF NOT EXISTS vector;
EOSQL
