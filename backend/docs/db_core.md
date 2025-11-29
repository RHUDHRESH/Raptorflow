# Core Database Schema (Canonical)

This document defines the canonical database schema for RaptorFlow.
**Do not duplicate or casually rename these tables.**
Phase 2+ features should build *on top* of this schema or add extensions, not replace it.

## Core Infrastructure Tables

| Table | Purpose | RLS Pattern |
|-------|---------|-------------|
| **profiles** | User identity & metadata. Backed by `auth.users`. | `auth.uid() = id` |
| **workspaces** | The marketing universe/tenant. | Member check via `workspace_members` |
| **workspace_members** | Many-to-many mapping of users to workspaces + roles. | `auth.uid()` matches `user_id` OR shared workspace |
| **workspace_invites** | Pending invitations for new members. | Admin/Owner only |

## Agent & System Tables

| Table | Purpose | RLS Pattern |
|-------|---------|-------------|
| **agents** | Registry of active agents in a workspace. | Member of `workspace_id` |
| **agent_runs** | Execution history and logs for agents. | Member of `workspace_id` |
| **cost_logs** | Token usage and cost tracking for LLM calls. | Member of `workspace_id` |
| **audit_logs** | System-wide audit trail for compliance. | Member of `workspace_id` |

## Business Logic Tables (Extensions)

*Any new feature tables (e.g., `campaigns`, `moves`, `cohorts`) must:*
1.  Include `workspace_id uuid not null references workspaces(id)`
2.  Enable RLS.
3.  Use the standard membership check policy:
    ```sql
    exists (
      select 1 from workspace_members wm
      where wm.workspace_id = <table_name>.workspace_id
        and wm.user_id = auth.uid()
    )
