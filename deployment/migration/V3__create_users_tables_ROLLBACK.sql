-- Rollback script for V3__create_users_tables.sql
-- This script removes the users table and all related indexes/constraints
-- WARNING: This will delete all user data. Use with caution.

-- Drop indexes first
DROP INDEX IF EXISTS idx_users_email;
DROP INDEX IF EXISTS idx_users_username;
DROP INDEX IF EXISTS uq_users_email;
DROP INDEX IF EXISTS uq_users_username;

-- Drop the users table
DROP TABLE IF EXISTS users;

-- Note: This rollback is irreversible. All user data will be lost.
-- Consider backing up data before running this script.
