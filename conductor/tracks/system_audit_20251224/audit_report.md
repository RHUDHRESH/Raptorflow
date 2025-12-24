# Supabase Security Audit Report (2025-12-24)

## Summary
The Supabase infrastructure has Row Level Security (RLS) enabled on most tables, but the policy coverage is incomplete, leaving several tables vulnerable to cross-tenant data access or unauthorized modifications.

## Findings

### 1. Incomplete RLS Policy Coverage
The following tables have RLS enabled but NO policies defined, meaning all access is denied by default (which is safe) BUT intended access is not yet configured, or they are missing RLS entirely.

- **Missing Policies:**
    - `foundation_positioning`
    - `foundation_voice_tone`
    - `moves`
    - `move_approvals`
    - `blackbox_outcomes`
    - `ml_feature_store`
    - `agent_memory_episodic`
    - `skill_registry`
    - `skills`
    - `muse_assets`
    - `checkpoints`
    - `checkpoint_blobs`
    - `checkpoint_writes`
    - `model_lineage`
    - `knowledge_concepts`
    - `knowledge_links`

### 2. Schema Conflicts & Redundancy
- `agent_decision_audit`: Defined in two migrations with conflicting `tenant_id` types (`UUID` vs `TEXT`).
- Positioning/Voice: `foundation_positioning`/`foundation_voice_tone` vs `brand_positioning_intelligence`/`brand_voice_persona`.

### 3. Policy Weaknesses
- Most policies only use `USING` (Select/Update/Delete) and miss `WITH CHECK` (Insert).
- Lack of `service_role` vs `authenticated` role distinctions.

## Recommendations
1. Consolidate conflicting schemas.
2. Standardize `tenant_id` as `UUID`.
3. Implement a comprehensive RLS hardening migration covering all missing tables.
4. Ensure all `INSERT` operations are validated with `WITH CHECK` policies.
