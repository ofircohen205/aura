-- Create users table for authentication and authorization
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE NOT NULL,
    roles TEXT[] DEFAULT ARRAY['user'] NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Create indexes for users table
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Create unique constraints
CREATE UNIQUE INDEX IF NOT EXISTS uq_users_email ON users(email);
CREATE UNIQUE INDEX IF NOT EXISTS uq_users_username ON users(username);

-- Composite index for common query patterns (email + is_active)
-- Useful for queries filtering by email and active status
CREATE INDEX IF NOT EXISTS idx_users_email_active ON users(email, is_active);

-- Composite index for user listing queries (is_active + created_at)
-- Useful for paginated user listings with active status filter
CREATE INDEX IF NOT EXISTS idx_users_active_created ON users(is_active, created_at);

-- Note: Refresh tokens are stored in Redis, not in the database.
-- The refresh_tokens table is not needed and has been removed from this migration.
