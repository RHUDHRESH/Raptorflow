-- Function to execute arbitrary SQL
-- This is a powerful function that should ONLY be available to the service_role
CREATE OR REPLACE FUNCTION public.exec_sql(sql_query TEXT)
RETURNS VOID AS $$
BEGIN
    EXECUTE sql_query;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission only to service_role
-- Note: In Supabase, the API usually maps to authenticated/anon roles.
-- service_role has all permissions, but for added security we are explicit.
REVOKE ALL ON FUNCTION public.exec_sql(TEXT) FROM public;
GRANT EXECUTE ON FUNCTION public.exec_sql(TEXT) TO service_role;
