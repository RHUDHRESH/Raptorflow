# Migration Governance Policy

This document establishes the rules and best practices for managing database migrations in RaptorFlow.

## Core Principles

### 1. Immutability
- **Canonical migrations** (001-004) are immutable once deployed to production
- Never modify existing migrations that have been applied to production databases
- Create new migrations to fix issues or add features

### 2. Idempotency
- All migrations MUST be idempotent (safe to run multiple times)
- Use `CREATE TABLE IF NOT EXISTS`, `DROP POLICY IF EXISTS`, etc.
- Check for existence before creating/modifying objects

### 3. Forward-Only
- Migrations move the database forward in time
- No automatic rollback mechanisms
- Rollbacks require explicit reverse migrations

### 4. Atomicity
- Each migration should be wrapped in a transaction (`BEGIN`/`COMMIT`)
- Migrations should either fully succeed or fully fail
- No partial application of changes

## Naming Conventions

### Canonical Migrations
Format: `XXX_canonical_<category>.sql`

Examples:
- `001_canonical_base_schema.sql`
- `002_canonical_auth_system.sql`
- `003_canonical_subscription_system.sql`
- `004_canonical_rls_policies.sql`

### Feature Migrations
Format: `XXX_<descriptive_name>.sql`

Examples:
- `005_add_user_preferences.sql`
- `006_create_analytics_tables.sql`
- `007_add_email_notifications.sql`

### Hotfix Migrations
Format: `XXX_fix_<issue_description>.sql`

Examples:
- `008_fix_duplicate_workspace_slugs.sql`
- `009_fix_subscription_status_constraint.sql`

### Timestamp-Based (Legacy)
Format: `YYYYMMDD_<description>.sql`

**Note**: New migrations should use sequential numbering (XXX format) instead of timestamps.

## Migration Structure

Every migration must include:

```sql
-- ============================================
-- MIGRATION TITLE
-- Brief description of what this migration does
-- Date: YYYY-MM-DD
-- Author: [Optional]
-- Ticket: [Optional reference]
-- ============================================

BEGIN;

-- Migration code here
-- Use IF NOT EXISTS / IF EXISTS for idempotency
-- Add comments explaining complex logic

COMMIT;
```

## Review Process

### Before Creating a Migration

1. **Plan the change**
   - Document what tables/columns/policies will be affected
   - Identify dependencies on existing migrations
   - Consider impact on existing data

2. **Test locally**
   - Run migration on local development database
   - Verify idempotency (run twice)
   - Test rollback scenario if applicable

3. **Peer review**
   - Have another developer review the migration
   - Check for security implications (RLS policies)
   - Verify naming conventions

### Deployment Checklist

- [ ] Migration is idempotent
- [ ] Migration is wrapped in transaction
- [ ] Migration includes comments
- [ ] Migration tested locally
- [ ] Migration peer-reviewed
- [ ] MIGRATION_ORDER.md updated
- [ ] Backup created before deployment
- [ ] Staging environment tested
- [ ] Rollback plan documented

## Execution Order

Migrations execute in **alphanumeric order** based on filename:

```
001_canonical_base_schema.sql
002_canonical_auth_system.sql
003_canonical_subscription_system.sql
004_canonical_rls_policies.sql
005_add_feature_x.sql
006_fix_issue_y.sql
```

## Dependency Management

### Explicit Dependencies
Document dependencies in migration header:

```sql
-- ============================================
-- ADD USER ANALYTICS
-- Dependencies: 001_canonical_base_schema.sql
-- ============================================
```

### Implicit Dependencies
- Migrations depend on all previous migrations in sequence
- Never skip migrations in the execution order
- Test migrations in clean database to verify dependencies

## Data Migrations

### Small Data Changes
Include in the migration file:

```sql
-- Update existing records
UPDATE users SET preferences = '{}' WHERE preferences IS NULL;
```

### Large Data Changes
Create separate data migration scripts:

```sql
-- 005_migrate_user_data.sql
-- Run separately with monitoring
```

## Security Considerations

### RLS Policies
- Always enable RLS: `ALTER TABLE x ENABLE ROW LEVEL SECURITY`
- Drop old policies before creating new ones
- Test policies with different user roles
- Document policy logic in comments

### Permissions
- Grant minimum necessary permissions
- Use `SECURITY DEFINER` carefully
- Document why elevated permissions are needed

### Sensitive Data
- Never include production data in migrations
- Use placeholder data for testing
- Encrypt sensitive configuration values

## Rollback Procedures

### Creating Rollback Migrations

If a migration needs to be reversed:

1. Create a new migration (don't modify the original)
2. Name it clearly: `XXX_rollback_<original_migration>.sql`
3. Reverse the changes in the correct order
4. Test thoroughly before production deployment

Example:
```sql
-- 007_rollback_006_add_analytics.sql
BEGIN;

DROP TABLE IF EXISTS analytics_events CASCADE;
DROP FUNCTION IF EXISTS track_analytics_event();

COMMIT;
```

### Emergency Rollback

For critical production issues:

1. Create database backup immediately
2. Identify the problematic migration
3. Create and test rollback migration
4. Deploy during maintenance window
5. Document incident and lessons learned

## Archive Management

### When to Archive

Archive migrations when:
- They are superseded by canonical migrations
- They are no longer relevant to current schema
- They were experimental/temporary fixes

### Archive Process

1. Move file to `supabase/migrations/archive/`
2. Update `MIGRATION_ORDER.md` to mark as archived
3. Document why it was archived
4. Keep for historical reference (never delete)

### Archive Structure

```
supabase/migrations/archive/
├── superseded/
│   ├── 000_base_schema.sql
│   └── 005_subscriptions.sql
├── experimental/
│   └── 999_test_feature.sql
└── hotfixes/
    └── 20260126_fix_duplicate_plans.sql
```

## Version Control

### Git Practices

- Commit migrations in separate commits
- Use descriptive commit messages
- Tag major migration milestones
- Never force-push migration changes

### Commit Message Format

```
feat(db): add user analytics tables

- Creates analytics_events table
- Adds tracking function
- Implements RLS policies

Migration: 005_add_user_analytics.sql
```

## Documentation Requirements

### Migration Documentation

Each migration should include:
- Purpose and rationale
- Tables/columns affected
- Dependencies
- Breaking changes (if any)
- Verification queries

### Schema Documentation

Update these files when migrations change schema:
- `DATABASE_SCHEMA.md` - Overall schema documentation
- `MIGRATION_ORDER.md` - Execution order and dependencies
- API documentation (if schema changes affect APIs)

## Testing Requirements

### Unit Tests

Test migrations in isolation:
```bash
# Reset database
supabase db reset

# Run single migration
psql -f supabase/migrations/005_new_feature.sql

# Verify changes
psql -c "SELECT * FROM new_table;"
```

### Integration Tests

Test migration sequences:
```bash
# Run all migrations
supabase db reset

# Run application tests
npm test
```

### Performance Tests

For migrations affecting large tables:
- Test on production-sized dataset
- Measure execution time
- Monitor resource usage
- Plan maintenance window accordingly

## Monitoring and Alerts

### Post-Deployment Monitoring

After deploying migrations:
- Monitor error logs for 24 hours
- Check application metrics
- Verify RLS policies are working
- Monitor query performance

### Alert Thresholds

Set up alerts for:
- Migration execution failures
- RLS policy violations
- Slow queries (>1s)
- Unexpected table locks

## Compliance and Audit

### Audit Trail

Maintain audit trail of:
- Who created the migration
- When it was deployed
- What environments it's been applied to
- Any issues encountered

### Compliance Requirements

For regulated environments:
- Document data retention policies
- Implement audit logging
- Maintain change approval records
- Regular security reviews

## Best Practices

### DO

✅ Use transactions for all migrations
✅ Make migrations idempotent
✅ Test on staging before production
✅ Document breaking changes
✅ Create backups before deployment
✅ Use descriptive names
✅ Add comments explaining complex logic
✅ Follow naming conventions

### DON'T

❌ Modify deployed migrations
❌ Skip migrations in sequence
❌ Deploy without testing
❌ Include production data
❌ Use hardcoded credentials
❌ Create circular dependencies
❌ Ignore RLS policies
❌ Deploy during peak hours (without planning)

## Contact and Support

For migration-related questions:
- Review this governance document
- Check `MIGRATION_ORDER.md` for execution order
- Consult team lead for complex migrations
- Document decisions in migration comments

## Revision History

- **2026-01-30**: Initial governance policy created
- **2026-01-30**: Canonical migrations (001-004) established
