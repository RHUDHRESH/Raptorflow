# 🚀 Raptorflow Security Migration Guide

## 📋 Overview
This guide provides step-by-step instructions for applying the comprehensive security overhaul to your Raptorflow Supabase database.

## 🔧 Prerequisites
- Supabase project access (Project ID: `vpwwzsanuyhpkvgorcnc`)
- Admin access to Supabase SQL Editor
- Service role key for authentication

## 📁 Migration Files
The following migration files need to be applied in order:

1. `20240115_fix_rls_function_mismatch.sql` - Critical RLS fix
2. `20240115_permissions_system.sql` - Database-driven permissions
3. `20240115_workspace_invitations.sql` - Role-based invitations
4. `20240115_enhanced_audit_logging.sql` - Comprehensive audit logging
5. `20240115_mfa_system.sql` - Multi-factor authentication
6. `20240115_oauth_system.sql` - OAuth 2.0 authorization server
7. `20240115_jwt_rotation.sql` - JWT token rotation
8. `20240115_ip_access_controls.sql` - IP-based access controls
9. `20240115_threat_detection.sql` - Advanced threat detection
10. `20240115_gdpr_compliance.sql` - GDPR compliance system

## 🎯 Application Methods

### Method 1: Supabase SQL Editor (Recommended)
1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Apply each migration file in order
4. Execute and verify each migration

### Method 2: Supabase CLI (Requires Docker)
```bash
# Install Supabase CLI
npm install -g supabase

# Login to Supabase
supabase login

# Link your project
supabase link --project-ref vpwwzsanuyhpkvgorcnc

# Apply migrations
supabase db push
```

### Method 3: Direct Database Connection
```bash
# Using psql (requires PostgreSQL client)
psql "postgresql://postgres.vpwwzsanuyhpkvgorcnc:YOUR_PASSWORD@aws-1-ap-south-1.pooler.supabase.com:5432/postgres" -f migration_file.sql
```

## 🔍 Migration Details

### 1. Critical RLS Fix
**File**: `20240115_fix_rls_function_mismatch.sql`
- Fixes critical security vulnerability in RLS function names
- Creates alias function `user_owns_workspace()` 
- **Priority**: 🔴 CRITICAL - Apply immediately

### 2. Permissions System
**File**: `20240115_permissions_system.sql`
- Implements database-driven permissions
- Replaces hardcoded role-based permissions
- Adds granular permission control

### 3. Workspace Invitations
**File**: `20240115_workspace_invitations.sql`
- Role-based workspace invitation system
- Audit logging for all invitation activities
- RLS policies for secure access

### 4. Enhanced Audit Logging
**File**: `20240115_enhanced_audit_logging.sql`
- GDPR-comprehensive audit logging
- Behavioral analysis and anomaly detection
- Data access tracking

### 5. MFA System
**File**: `20240115_mfa_system.sql`
- Multi-factor authentication (TOTP, SMS, backup codes)
- Device fingerprinting and trusted devices
- Challenge-response system

### 6. OAuth 2.0 System
**File**: `20240115_oauth_system.sql`
- Complete OAuth 2.0 authorization server
- PKCE support and token management
- Client registry and scopes

### 7. JWT Token Rotation
**File**: `20240115_jwt_rotation.sql`
- Secure token lifecycle management
- Token blacklisting and rotation
- Key management system

### 8. IP Access Controls
**File**: `20240115_ip_access_controls.sql`
- IP-based access policies
- Geofencing and reputation analysis
- Rate limiting and challenge system

### 9. Threat Detection
**File**: `20240115_threat_detection.sql`
- ML-powered behavioral analysis
- Threat intelligence integration
- Automated incident response

### 10. GDPR Compliance
**File**: `20240115_gdpr_compliance.sql`
- Data subject rights management
- Consent management and withdrawal
- Data retention and breach notification

## ✅ Verification Steps

After applying all migrations:

### 1. Check Database Schema
```sql
-- Verify tables were created
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE '%mfa%' 
OR table_name LIKE '%oauth%' 
OR table_name LIKE '%audit%'
OR table_name LIKE '%gdpr%';
```

### 2. Test RLS Policies
```sql
-- Test RLS is working
SELECT auth.uid();
SELECT * FROM users WHERE auth_user_id = auth.uid();
```

### 3. Verify Functions
```sql
-- Check functions exist
SELECT proname FROM pg_proc WHERE proname LIKE '%mfa%' OR proname LIKE '%oauth%';
```

### 4. Test Security Features
- Try accessing another user's data (should fail)
- Test MFA setup flow
- Verify audit logging is working
- Check GDPR compliance features

## 🔧 Post-Migration Configuration

### 1. Environment Variables
Add these to your `.env` file:
```env
# Security Configuration
JWT_SECRET=your-secure-jwt-secret
MFA_ISSUER=Raptorflow
OAUTH_ISSUER=https://raptorflow.in
GDPR_COMPLIANCE_ENABLED=true
```

### 2. Frontend Integration
Update your frontend to use the new security libraries:
```typescript
import { gdprClient } from '@/lib/gdpr'
import { threatDetectionClient } from '@/lib/threat-detection'
import { ipAccessControl } from '@/lib/ip-access'
```

### 3. Middleware Update
Ensure your middleware includes the new security features:
```typescript
import { ipAccessControl } from '@/lib/ip-access'
import { threatDetectionClient } from '@/lib/threat-detection'
```

## 🚨 Important Notes

### 1. Backup First
Always create a backup of your database before applying migrations:
```sql
-- Create backup
CREATE TABLE users_backup AS SELECT * FROM users;
```

### 2. Test in Staging
Apply migrations to a staging environment first if available.

### 3. Monitor Performance
Some migrations (especially audit logging) may impact performance. Monitor after deployment.

### 4. Update Application Code
Your application code needs to be updated to use the new security features.

## 🎯 Security Benefits

After applying these migrations, Raptorflow will have:

- ✅ **Enterprise-grade authentication** with MFA
- ✅ **Granular permissions** system
- ✅ **Comprehensive audit logging**
- ✅ **GDPR compliance** framework
- ✅ **Advanced threat detection**
- ✅ **IP-based access controls**
- ✅ **OAuth 2.0 authorization**
- ✅ **JWT token rotation**
- ✅ **Role-based invitations**
- ✅ **Breach notification system**

## 📞 Support

If you encounter issues:
1. Check Supabase logs
2. Verify database connection
3. Review migration syntax
4. Test individual statements

## 🔄 Rollback Plan

If needed, you can rollback by:
1. Dropping new tables
2. Restoring from backup
3. Reverting application code

---

**⚡ Ready to transform Raptorflow into an enterprise-grade secure application!**
