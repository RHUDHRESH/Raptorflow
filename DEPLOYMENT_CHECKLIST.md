# RAPTORFLOW DEPLOYMENT CHECKLIST

## Pre-Deployment Checklist
- [ ] Review schema SQL in `schema_for_manual_execution.sql`
- [ ] Backup current database (if needed)
- [ ] Test SQL in development environment

## Deployment Steps
- [ ] Execute schema SQL in Supabase Dashboard
- [ ] Run verification queries
- [ ] Check table creation
- [ ] Verify RLS policies
- [ ] Test indexes

## Post-Deployment Verification
- [ ] Run `node scripts/pull_and_verify_schema.js`
- [ ] Test user registration
- [ ] Test login flow
- [ ] Test workspace creation
- [ ] Check API endpoints

## Frontend Testing
- [ ] Start development server
- [ ] Test authentication flow
- [ ] Check for redirect loops
- [ ] Verify user profile loading
- [ ] Test workspace operations

## Performance Checks
- [ ] Monitor query performance
- [ ] Check RLS policy efficiency
- [ ] Verify index usage

## Rollback Plan
- [ ] Keep backup of old schema
- [ ] Document rollback steps
- [ ] Test rollback procedure

## Monitoring
- [ ] Set up error monitoring
- [ ] Monitor authentication metrics
- [ ] Track database performance

Generated: 2026-01-23T04:52:44.889Z
