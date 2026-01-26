-- IP Whitelisting Database Schema
-- Migration: 20260116_ip_whitelisting.sql
-- Implements IP restrictions, geo-fencing, and VPN detection

-- Create ip_whitelist_rules table
CREATE TABLE IF NOT EXISTS public.ip_whitelist_rules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  workspace_id UUID REFERENCES public.workspaces(id) ON DELETE CASCADE,
  ip_address INET,
  ip_range_start INET,
  ip_range_end INET,
  description TEXT NOT NULL,
  rule_type TEXT NOT NULL CHECK (rule_type IN ('allow', 'deny')),
  priority INTEGER NOT NULL DEFAULT 100,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_by UUID REFERENCES auth.users(id) ON DELETE CASCADE
);

-- Create geo_fence_rules table
CREATE TABLE IF NOT EXISTS public.geo_fence_rules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  workspace_id UUID REFERENCES public.workspaces(id) ON DELETE CASCADE,
  country_code TEXT NOT NULL,
  region TEXT,
  city TEXT,
  postal_code TEXT,
  rule_type TEXT NOT NULL CHECK (rule_type IN ('allow', 'deny')),
  priority INTEGER NOT NULL DEFAULT 100,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_by UUID REFERENCES auth.users(id) ON DELETE CASCADE
);

-- Create vpn_providers table
CREATE TABLE IF NOT EXISTS public.vpn_providers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  ip_ranges TEXT[] NOT NULL,
  detection_methods TEXT[] NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create ip_access_logs table
CREATE TABLE IF NOT EXISTS public.ip_access_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  ip_address INET NOT NULL,
  country_code TEXT,
  region TEXT,
  city TEXT,
  is_vpn BOOLEAN NOT NULL DEFAULT false,
  vpn_provider TEXT,
  risk_score INTEGER NOT NULL DEFAULT 0,
  action_taken TEXT NOT NULL CHECK (action_taken IN ('allow', 'deny', 'challenge')),
  rule_matched TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_ip_whitelist_rules_user_id ON public.ip_whitelist_rules(user_id);
CREATE INDEX IF NOT EXISTS idx_ip_whitelist_rules_workspace_id ON public.ip_whitelist_rules(workspace_id);
CREATE INDEX IF NOT EXISTS idx_ip_whitelist_rules_ip_address ON public.ip_whitelist_rules(ip_address);
CREATE INDEX IF NOT EXISTS idx_ip_whitelist_rules_range_start ON public.ip_whitelist_rules(ip_range_start);
CREATE INDEX IF NOT EXISTS idx_ip_whitelist_rules_range_end ON public.ip_whitelist_rules(ip_range_end);
CREATE INDEX IF NOT EXISTS idx_ip_whitelist_rules_priority ON public.ip_whitelist_rules(priority);
CREATE INDEX IF NOT EXISTS idx_ip_whitelist_rules_active ON public.ip_whitelist_rules(is_active);
CREATE INDEX IF NOT EXISTS idx_ip_whitelist_rules_created_at ON public.ip_whitelist_rules(created_at);

CREATE INDEX IF NOT EXISTS idx_geo_fence_rules_user_id ON public.geo_fence_rules(user_id);
CREATE INDEX IF NOT EXISTS idx_geo_fence_rules_workspace_id ON public.geo_fence_rules(workspace_id);
CREATE INDEX IF NOT EXISTS idx_geo_fence_rules_country_code ON public.geo_fence_rules(country_code);
CREATE INDEX IF NOT EXISTS idx_geo_fence_rules_region ON public.geo_fence_rules(region);
CREATE IF NOT EXISTS idx_geo_fence_rules_city ON public.geo_fence_rules(city);
CREATE INDEX IF NOT EXISTS idx_geo_fence_rules_priority ON public.geo_fence_rules(priority);
CREATE INDEX IF NOT EXISTS idx_geo_fence_rules_active ON public.geo_fence_rules(is_active);
CREATE INDEX IF NOT EXISTS idx_geo_fence_rules_created_at ON public.geo_fence_rules(created_at);

CREATE INDEX IF NOT EXISTS idx_vpn_providers_name ON public.vpn_providers(name);
CREATE INDEX IF NOT EXISTS idx_vpn_providers_active ON public.vpn_providers(is_active);
CREATE INDEX IF NOT EXISTS idx_vpn_providers_created_at ON public.vpn_providers(created_at);

CREATE INDEX IF NOT EXISTS idx_ip_access_logs_user_id ON public.ip_access_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_ip_access_logs_ip_address ON public.ip_access_logs(ip_address);
CREATE INDEX IF NOT EXISTS idx_ip_access_logs_country_code ON public.ip_access_logs(country_code);
CREATE INDEX IF NOT EXISTS idx_ip_access_logs_is_vpn ON public.ip_access_logs(is_vpn);
CREATE INDEX IF NOT EXISTS idx_ip_access_logs_risk_score ON public.ip_access_logs(risk_score);
CREATE INDEX IF NOT EXISTS idx_ip_access_logs_action_taken ON public.ip_access_logs(action_taken);
CREATE INDEX IF NOT EXISTS idx_ip_access_logs_created_at ON public.ip_access_logs(created_at);

-- Enable RLS on all tables
ALTER TABLE public.ip_whitelist_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.geo_fence_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vpn_providers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ip_access_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for ip_whitelist_rules
CREATE POLICY "ip_whitelist_select_own" ON public.ip_whitelist_rules
  FOR SELECT
  USING (
    user_id = auth.uid()
    OR (user_id IS NULL AND workspace_id IS NULL)
  );

CREATE POLICY "ip_whitelist_insert_admin" ON public.ip_whitelist_rules
  FOR INSERT
  WITH CHECK (
    user_id = auth.uid()
    OR (user_id IS NULL AND workspace_id IS NULL)
  );

CREATE POLICY "ip_whitelist_update_own" ON public.ip_whitelist_rules
  FOR UPDATE
  USING (
    user_id = auth.uid()
    OR (user_id IS NULL AND workspace_id IS NULL)
  );

CREATE POLICY "ip_whitelist_delete_own" ON public.ip_whitelist_rules
  FOR DELETE
  USING (
    user_id = auth.uid()
    OR (user_id IS NULL AND workspace_id IS NULL)
  );

-- RLS Policies for geo_fence_rules
CREATE POLICY "geo_fence_rules_select_own" ON public.geo_fence_rules
  FOR SELECT
  USING (
    user_id = auth.uid()
    OR (user_id IS NULL AND workspace_id IS NULL)
  );

CREATE POLICY "geo_fence_insert_admin" ON public.geo_fence_rules
  FOR INSERT
  WITH CHECK (
    user_id = auth.uid()
    OR (user_id IS NULL AND workspace_id IS NULL)
  );

CREATE POLICY "geo_fence_rules_update_own" ON public.geo_fence_rules
  FOR UPDATE
  USING (
    user_id = auth.uid()
    OR (user_id IS NULL AND workspace_id IS NULL)
  );

CREATE POLICY "geo_fence_rules_delete_own" ON public.geo_fence_rules
  FOR DELETE
  USING (
    user_id = auth.uid()
    OR (user_id IS NULL AND workspace_id IS NULL)
  );

-- RLS Policies for vpn_providers
CREATE POLICY "vpn_providers_select_all" ON public.vpn_providers
  FOR SELECT
  USING (is_active = true);

CREATE POLICY "vpn_providers_insert_admin" ON public.vpn_providers
  FOR INSERT
  WITH CHECK (is_active = true);

CREATE POLICY "vpn_providers_update_admin" ON public.vpn_providers
  FOR UPDATE
  USING (is_active = true);

CREATE POLICY "vpn_providers_delete_admin" ON public.vpn_providers
  FOR DELETE
  USING (is_active = true);

-- RLS Policies for ip_access_logs
CREATE POLICY "ip_access_logs_select_own" ON public.ip_access_logs
  FOR SELECT
  USING (user_id = auth.uid())
    OR (user_id IS NULL AND user_id IS NULL)
  );

CREATE POLICY "ip_access_logs_insert_authenticated" ON public.ip_access_logs
  WITH CHECK (
    user_id = auth.uid()
    OR (user_id IS NULL AND user_id IS NULL)
  );

-- Create triggers for updated_at timestamps
CREATE TRIGGER ip_whitelist_rules_updated_at
    BEFORE UPDATE ON public.ip_whitelist_rules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER geo_fence_rules_updated_at
    BEFORE UPDATE ON public.geo_fence_rules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER vpn_providers_updated_at
    BEFORE UPDATE ON public.vpn_providers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create function to check IP whitelist
CREATE OR REPLACE FUNCTION is_ip_whitelisted(
    ip_param INET,
    user_uuid UUID DEFAULT NULL,
    workspace_uuid UUID DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    is_allowed BOOLEAN DEFAULT false;
BEGIN
    -- Check global allow rules first
    SELECT 1 INTO is_allowed
    FROM public.ip_whitelist_rules
    WHERE (user_id IS NULL AND workspace_id IS NULL)
      AND is_active = true
      AND (
        (ip_param = ip_address)
        OR (ip_param >= ip_range_start AND ip_param <= ip_range_end)
      )
      AND rule_type = 'allow'
      ORDER BY priority DESC
      LIMIT 1;

    -- If not allowed globally, check user-specific rules
    IF NOT is_allowed AND user_uuid IS NOT NULL THEN
      SELECT 1 INTO is_allowed
      FROM public.ip_whitelist_rules
      WHERE user_id = user_uuid
        AND is_active = true
        AND (
          (ip_param = ip_address)
          OR (ip_param >= ip_range_start AND ip_param <= ip_range_end)
        )
        AND rule_type = 'allow'
        ORDER BY priority DESC
        LIMIT 1;
    END IF;

    -- If still not allowed, check workspace-specific rules
    IF NOT is_allowed AND workspace_uuid IS NOT NULL THEN
      SELECT 1 INTO is_allowed
      FROM public.ip_whitelist_rules
      WHERE workspace_id = workspace_uuid
        AND is_active = true
        AND (
          (ip_param = ip_address)
          OR (ip_param >= ip_range_start AND ip_param <= ip_range_end)
        )
        AND rule_type = 'allow'
        ORDER BY priority DESC
        LIMIT 1;
    END IF;

    RETURN is_allowed;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to check geofence
CREATE OR REPLACE FUNCTION is_geo_allowed(
    country_code TEXT,
    user_uuid UUID DEFAULT NULL,
    workspace_uuid UUID DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    is_allowed BOOLEAN DEFAULT false;
BEGIN
    -- Check global allow rules first
    SELECT 1 INTO is_allowed
    FROM public.geo_fence_rules
    WHERE (user_id IS NULL AND workspace_id IS NULL)
      AND is_active = true
      AND (
        country_code = country_code
        OR (region = country_code)
        OR (city = country_code)
      )
      AND rule_type = 'allow'
      ORDER BY priority DESC
      LIMIT 1;

    -- If not allowed globally, check user-specific rules
    IF NOT is_allowed AND user_uuid IS NOT NULL THEN
      SELECT 1 INTO is_allowed
      FROM public.geo_fence_rules
      WHERE user_id = user_uuid
        AND is_active = true
        AND (
          country_code = country_code
          OR (region = country_code)
          OR (city = country_code)
        )
      AND rule_type = 'allow'
      ORDER BY priority DESC
      LIMIT 1;
    END IF;

    -- If still not allowed, check workspace-specific rules
    IF NOT is_allowed AND workspace_uuid IS NOT NULL THEN
      SELECT 1 INTO is_allowed
      FROM public.geo_fence_rules
      WHERE workspace_id = workspace_uuid
        AND is_active = true
        AND (
          country_code = country_code
          OR (region = country_code)
          OR (city = country_code)
        )
      AND rule_type = 'allow'
      ORDER BY priority DESC
      LIMIT 1;
    END IF;

    RETURN is_allowed;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to check VPN usage
CREATE OR REPLACE FUNCTION is_vpn_provider(
    ip_param INET,
    user_agent_param TEXT DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    is_vpn BOOLEAN DEFAULT FALSE;
    provider_name TEXT;
BEGIN
    -- Check against known VPN providers
    SELECT 1 INTO is_vpn, provider_name
    FROM public.vpn_providers
    WHERE is_active = true
      AND (
        ip_param >= ANY(ip_ranges)
      )
      ORDER BY priority DESC
      LIMIT 1;

    -- Check user agent for VPN indicators
    IF NOT is_vpn AND user_agent_param IS NOT NULL THEN
      SELECT 1 INTO is_vpn
      FROM public.vpn_providers
      WHERE detection_methods @> ARRAY['user_agent']
        AND is_active = true
        ORDER BY priority DESC
        LIMIT 1;
    END IF;

    RETURN is_vpn;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to log IP access attempt
CREATE OR REPLACE FUNCTION log_ip_access_attempt(
    user_uuid UUID,
    ip_param INET,
    country_code_param TEXT DEFAULT NULL,
    region_param TEXT DEFAULT NULL,
    city_param TEXT DEFAULT NULL,
    is_vpn_param BOOLEAN DEFAULT FALSE,
    provider_name TEXT DEFAULT NULL,
    risk_score_param INTEGER DEFAULT 0,
    action_param TEXT,
    rule_matched TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    event_id UUID;
BEGIN
    INSERT INTO public.ip_access_logs (
        user_id,
        ip_address,
        country_code: country_code_param,
        region: region_param,
        city: city_param,
        is_vpn: is_vpn_param,
        vpn_provider: provider_name,
        risk_score: risk_score_param,
        action_taken: action_param,
        rule_matched: rule_matched,
        created_at: NOW()
    ) VALUES (
        user_uuid,
        ip_param,
        country_code_param,
        region_param,
        city_param,
        is_vpn_param,
        provider_name,
        risk_score_param,
        action_param,
        rule_matched,
        NOW()
    )
    RETURNING id INTO event_id;
END;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to get IP location
CREATE OR REPLACE FUNCTION get_ip_location(
    ip_param INET
)
RETURNS JSONB AS $$
DECLARE
    location JSONB;
BEGIN
    -- Try to get location from IP
    BEGIN
      SELECT jsonb_build_object(
        'country_code': country_code,
        'region': region,
        'city': city,
        'latitude': latitude,
        'longitude': longitude,
        'timezone': timezone
      ) INTO location
      FROM (
        SELECT country_code, region, city, latitude, longitude, timezone
        FROM (
          SELECT
            country_code,
            region,
            city,
            latitude,
            longitude,
            timezone
          FROM (
            SELECT
              country_code,
              region,
              city,
              latitude,
              longitude,
              timezone
            FROM (
              SELECT
                country_code,
                region,
                city,
                latitude,
                longitude,
                timezone
              FROM (
                  SELECT
                    country_code,
                    region,
                    city,
                    latitude,
                    longitude,
                    timezone
                  FROM (
                    SELECT
                      country_code,
                      region,
                      city,
                      latitude,
                      longitude,
                      timezone
                    FROM (
                      SELECT
                        country_code,
                        region,
                        city,
                        latitude,
                        longitude,
                        timezone
                      FROM (
                        SELECT
                          country_code,
                          region,
                          city,
                          latitude,
                          longitude,
                          timezone
                        FROM (
                          SELECT
                            country_code,
                            region,
                            city,
                            latitude,
                            longitude,
                            timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          FROM (
                            SELECT
                              country_code,
                              region,
                              city,
                              latitude,
                              longitude,
                              timezone
                          )
                        )
                      )
                    )
                  )
              )
            )
        )
      )
    END IF location IS NOT NULL THEN
        RETURN location;
    END IF;

    RETURN jsonb_build_object(
      'country_code': 'Unknown',
      'region': 'Unknown',
      'city': 'Unknown',
      'latitude': null,
      'longitude': null,
      'timezone': 'UTC'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT SELECT ON public.ip_whitelist_rules TO authenticated;
GRANT SELECT ON public.geo_fence_rules TO authenticated;
GRANT SELECT ON public.vpn_providers TO authenticated;
GRANT SELECT ON public.ip_access_logs TO authenticated;

GRANT EXECUTE ON FUNCTION is_ip_whitelisted TO authenticated;
GRANT EXECUTE FUNCTION is_geo_allowed TO authenticated;
GRANT EXECUTE FUNCTION is_vpn_provider TO authenticated;
GRANT EXECUTE FUNCTION log_ip_access_attempt TO authenticated;
GRANT EXECUTE FUNCTION get_ip_location TO authenticated;

-- Add comments for documentation
COMMENT ON TABLE public.ip_whitelist_rules IS 'IP whitelist/blacklist rules for access control';
COMMENT ON TABLE public.geo_fence_rules IS 'Geofencing rules for country/region access control';
COMMENT ON TABLE public.vpn_providers IS 'Known VPN providers and their IP ranges';
COMMENT ON TABLE public.ip_access_logs IS 'Audit log of all IP access attempts';

COMMENT ON FUNCTION is_ip_whitelisted IS 'Check if IP is whitelisted';
COMMENT ON FUNCTION is_geo_allowed IS 'Check if country is allowed by geofence rules';
COMMENT ON FUNCTION is_vpn_provider IS 'Check if IP belongs to known VPN provider';
COMMENT ON FUNCTION log_ip_access_attempt IS 'Log IP access attempt for security monitoring';
COMMENT ON FUNCTION get_ip_location IS 'Get location information for IP address';

-- Create function to increment access count
CREATE OR REPLACE FUNCTION increment_access_count(
    log_id UUID
)
RETURNS VOID AS $$
BEGIN
    UPDATE public.ip_access_logs
    SET access_count = access_count + 1
    WHERE id = log_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger for incrementing access count
CREATE TRIGGER increment_ip_access_count
    BEFORE UPDATE ON public.ip_access_logs
    FOR EACH ROW
    WHEN (NEW.created_at > OLD.created_at)
    EXECUTE FUNCTION increment_access_count(NEW.id);

-- Grant permission for increment function
GRANT EXECUTE ON FUNCTION increment_access_count TO authenticated;

-- Add comments for documentation
COMMENT ON FUNCTION increment_access_count IS 'Increment access count for IP access logging';
