-- supabase/migrations/004_password_reset_tokens.sql
-- Create password reset tokens table

-- Drop existing if exists
DROP TABLE IF EXISTS public.password_reset_tokens CASCADE;

-- Create password reset tokens table
CREATE TABLE IF NOT EXISTS public.password_reset_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  token TEXT UNIQUE NOT NULL,
  email TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  used_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_password_reset_tokens_token ON public.password_reset_tokens(token);
CREATE INDEX idx_password_reset_tokens_email ON public.password_reset_tokens(email);
CREATE INDEX idx_password_reset_tokens_expires ON public.password_reset_tokens(expires_at);

-- Enable RLS
ALTER TABLE public.password_reset_tokens ENABLE ROW LEVEL SECURITY;

-- RLS Policies
-- Users can only access their own tokens via email
CREATE POLICY "password_reset_tokens_select_own" ON public.password_reset_tokens
  FOR SELECT
  USING (email = auth.email());

-- System can insert tokens (via API)
CREATE POLICY "password_reset_tokens_insert_system" ON public.password_reset_tokens
  FOR INSERT
  WITH CHECK (true);

-- Users can update their own tokens (mark as used)
CREATE POLICY "password_reset_tokens_update_own" ON public.password_reset_tokens
  FOR UPDATE
  USING (email = auth.email());

-- Function to clean up expired tokens
CREATE OR REPLACE FUNCTION public.cleanup_expired_tokens()
RETURNS void AS $$
BEGIN
  DELETE FROM public.password_reset_tokens
  WHERE expires_at < NOW() OR (used_at IS NOT NULL AND used_at < NOW() - INTERVAL '1 hour');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Updated_at trigger
CREATE OR REPLACE FUNCTION public.update_password_reset_token_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER password_reset_tokens_updated_at
  BEFORE UPDATE ON public.password_reset_tokens
  FOR EACH ROW EXECUTE FUNCTION public.update_password_reset_token_updated_at();
