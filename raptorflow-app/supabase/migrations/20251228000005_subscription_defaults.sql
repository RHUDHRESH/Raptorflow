-- Sync subscription defaults for compatibility

CREATE OR REPLACE FUNCTION subscriptions_sync_defaults()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.workspace_id IS NOT NULL AND NEW.organization_id IS NULL THEN
        NEW.organization_id := NEW.workspace_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS subscriptions_sync_defaults_trigger ON subscriptions;
CREATE TRIGGER subscriptions_sync_defaults_trigger
    BEFORE INSERT OR UPDATE ON subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION subscriptions_sync_defaults();
