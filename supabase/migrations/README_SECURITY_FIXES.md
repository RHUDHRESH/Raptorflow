# Supabase Security Fixes Migration Set

## Migration Files (130-137)

This set of 8 migrations addresses all security and performance issues identified in the Supabase Database Advisor report.

### Migration Order & Dependencies

```
130_fix_critical_rls_security.sql     # CRITICAL - Must run first
131_fix_function_security.sql        # CRITICAL - Depends on 130
132_fix_extension_security.sql        # MEDIUM - Independent
133_fix_icp_rls_policies.sql         # MEDIUM - Depends on 130
134_fix_rls_performance.sql          # MEDIUM - Depends on 130,133
135_fix_foreign_key_indexes.sql      # LOW - Performance only
136_remove_unused_indexes.sql        # LOW - Performance only
137_consolidate_rls_policies.sql     # LOW - Depends on 134
```

### Critical Path (Must Apply First)
1. **130_fix_critical_rls_security.sql** - Enables RLS on exposed tables
2. **131_fix_function_security.sql** - Fixes function vulnerabilities

### Application Commands

```bash
# Apply all critical fixes first
supabase db push 130_fix_critical_rls_security.sql
supabase db push 131_fix_function_security.sql

# Apply remaining fixes in order
supabase db push 132_fix_extension_security.sql
supabase db push 133_fix_icp_rls_policies.sql
supabase db push 134_fix_rls_performance.sql
supabase db push 135_fix_foreign_key_indexes.sql
supabase db push 136_remove_unused_indexes.sql
supabase db push 137_consolidate_rls_policies.sql

# Or apply all at once
supabase db push
```

### Verification

```bash
# Check migration status
supabase migration list

# Run security advisor to verify fixes
supabase db lint --fix

# Check for any remaining issues
supabase db lint
```

### Notes
- All migrations use `CONCURRENTLY` for indexes to avoid locking
- RLS policies are optimized for performance with `(select auth.uid())`
- Unused indexes are dropped to improve write performance
- Function security is enhanced with proper search_path settings
