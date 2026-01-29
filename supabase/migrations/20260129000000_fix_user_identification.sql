-- Fix User Identification System
-- Add unique identification numbers for users

BEGIN;

-- Add identification_number column to users table
ALTER TABLE users ADD COLUMN identification_number VARCHAR(20) UNIQUE;

-- Create sequence for generating unique IDs
CREATE SEQUENCE IF NOT EXISTS user_identification_seq
    START 100000
    INCREMENT 1
    MINVALUE 100000
    MAXVALUE 999999
    CACHE 1;

-- Function to generate next identification number
CREATE OR REPLACE FUNCTION generate_identification_number()
RETURNS TEXT AS $$
DECLARE
    next_id BIGINT;
BEGIN
    -- Get next value from sequence
    next_id := nextval('user_identification_seq');

    -- Return formatted ID with 'U' prefix
    RETURN 'U' || LPAD(next_id::TEXT, 6, '0');
END;
$$ LANGUAGE plpgsql;

-- Update existing users with identification numbers
UPDATE users
SET identification_number = generate_identification_number()
WHERE identification_number IS NULL;

-- Set default value for new users
ALTER TABLE users ALTER COLUMN identification_number
SET DEFAULT generate_identification_number();

-- Add not null constraint after setting defaults
ALTER TABLE users ALTER COLUMN identification_number SET NOT NULL;

-- Create index for identification_number
CREATE INDEX IF NOT EXISTS idx_users_identification_number ON users(identification_number);

-- Update RLS policies to include identification_number
CREATE POLICY "Users can view own identification" ON users
FOR SELECT USING (auth_user_id = auth.uid());

-- Grant usage on sequence to authenticated users
GRANT USAGE ON SEQUENCE user_identification_seq TO authenticated;
GRANT SELECT ON user_identification_seq TO authenticated;

COMMIT;
