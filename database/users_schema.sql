-- Users table for authentication and authorization
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role user_role_enum NOT NULL,
    vsa_id VARCHAR(50) REFERENCES organizations(id),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    phone VARCHAR(50),
    position VARCHAR(100),
    department VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- Create user_role_enum if it doesn't exist
DO $$ BEGIN
    CREATE TYPE user_role_enum AS ENUM ('VA_ADMIN', 'VSA_ADMIN', 'VSA_USER');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_vsa_id ON users(vsa_id);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

-- Add relationship to organizations table
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS users relationship;

-- Create a default VA admin user (password: admin123)
INSERT INTO users (
    id, username, email, hashed_password, full_name, role, is_active, is_verified
) VALUES (
    'va-admin-001',
    'va_admin',
    'va.admin@va.gov',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK8O', -- admin123
    'VA System Administrator',
    'VA_ADMIN',
    TRUE,
    TRUE
) ON CONFLICT (id) DO NOTHING;
