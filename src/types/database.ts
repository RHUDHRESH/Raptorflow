// Database type definitions for Supabase
export type Database = {
  public: {
    Tables: {
      users: {
        Row: {
          id: string
          auth_user_id: string
          email: string
          full_name: string | null
          avatar_url: string | null
          phone: string | null
          onboarding_status: 'pending_workspace' | 'pending_storage' | 'pending_plan_selection' | 'pending_payment' | 'active' | 'suspended' | 'cancelled'
          role: 'user' | 'admin' | 'super_admin' | 'support' | 'billing_admin'
          is_active: boolean
          is_banned: boolean
          ban_reason: string | null
          banned_at: string | null
          banned_by: string | null
          notes: string | null
          created_at: string
          updated_at: string
          last_login_at: string | null
        }
        Insert: Omit<Database['public']['Tables']['users']['Row'], 'id' | 'created_at' | 'updated_at'>
        Update: Partial<Database['public']['Tables']['users']['Row']>
      }
      workspaces: {
        Row: {
          id: string
          user_id: string
          name: string
          slug: string
          gcs_bucket_name: string | null
          gcs_folder_path: string | null
          storage_quota_bytes: number
          storage_used_bytes: number
          status: 'provisioning' | 'active' | 'suspended' | 'deleted'
          created_at: string
          updated_at: string
        }
        Insert: Omit<Database['public']['Tables']['workspaces']['Row'], 'id' | 'created_at' | 'updated_at'>
        Update: Partial<Database['public']['Tables']['workspaces']['Row']>
      }
      permissions: {
        Row: {
          id: string
          name: string
          resource: string
          action: string
          description: string | null
          category: string
          is_system: boolean
          created_at: string
          updated_at: string
        }
        Insert: Omit<Database['public']['Tables']['permissions']['Row'], 'id' | 'created_at' | 'updated_at'>
        Update: Partial<Database['public']['Tables']['permissions']['Row']>
      }
      role_permissions: {
        Row: {
          role: string
          permission_id: string
          granted_at: string
          granted_by: string | null
          granted_reason: string | null
        }
        Insert: Omit<Database['public']['Tables']['role_permissions']['Row'], 'granted_at'>
        Update: Partial<Database['public']['Tables']['role_permissions']['Row']>
      }
      user_permissions: {
        Row: {
          id: string
          user_id: string
          permission_id: string
          granted: boolean
          granted_at: string
          granted_by: string | null
          granted_reason: string | null
          expires_at: string | null
          is_active: boolean
        }
        Insert: Omit<Database['public']['Tables']['user_permissions']['Row'], 'id' | 'granted_at'>
        Update: Partial<Database['public']['Tables']['user_permissions']['Row']>
      }
      permission_groups: {
        Row: {
          id: string
          name: string
          description: string | null
          is_system: boolean
          created_at: string
        }
        Insert: Omit<Database['public']['Tables']['permission_groups']['Row'], 'id' | 'created_at'>
        Update: Partial<Database['public']['Tables']['permission_groups']['Row']>
      }
      permission_group_memberships: {
        Row: {
          group_id: string
          permission_id: string
          added_at: string
        }
        Insert: Omit<Database['public']['Tables']['permission_group_memberships']['Row'], 'added_at'>
        Update: Partial<Database['public']['Tables']['permission_group_memberships']['Row']>
      }
      role_permission_groups: {
        Row: {
          role: string
          group_id: string
          assigned_at: string
          assigned_by: string | null
        }
        Insert: Omit<Database['public']['Tables']['role_permission_groups']['Row'], 'assigned_at'>
        Update: Partial<Database['public']['Tables']['role_permission_groups']['Row']>
      }
      audit_logs: {
        Row: {
          id: string
          actor_id: string | null
          actor_cin: string | null
          actor_role: string | null
          action: string
          action_category: string
          description: string | null
          target_type: string | null
          target_id: string | null
          target_cin: string | null
          changes: any | null
          status: string | null
          error_message: string | null
          ip_address: string | null
          user_agent: string | null
          created_at: string
        }
        Insert: Omit<Database['public']['Tables']['audit_logs']['Row'], 'id' | 'created_at'>
        Update: Partial<Database['public']['Tables']['audit_logs']['Row']>
      }
      security_events: {
        Row: {
          id: string
          event_type: string
          severity: 'info' | 'warning' | 'critical'
          user_id: string | null
          user_cin: string | null
          user_email: string | null
          description: string | null
          details: any | null
          ip_address: string | null
          user_agent: string | null
          created_at: string
        }
        Insert: Omit<Database['public']['Tables']['security_events']['Row'], 'id' | 'created_at'>
        Update: Partial<Database['public']['Tables']['security_events']['Row']>
      }
      user_sessions: {
        Row: {
          id: string
          user_id: string
          session_token: string
          ip_address: string | null
          user_agent: string | null
          device_fingerprint: string | null
          is_active: boolean
          revoked_at: string | null
          revoked_reason: string | null
          created_at: string
          last_accessed_at: string
          expires_at: string
        }
        Insert: Omit<Database['public']['Tables']['user_sessions']['Row'], 'id' | 'created_at' | 'last_accessed_at'>
        Update: Partial<Database['public']['Tables']['user_sessions']['Row']>
      }
      icp_profiles: {
        Row: {
          id: string
          workspace_id: string
          name: string
          description: string | null
          created_at: string
          updated_at: string
        }
        Insert: Omit<Database['public']['Tables']['icp_profiles']['Row'], 'id' | 'created_at' | 'updated_at'>
        Update: Partial<Database['public']['Tables']['icp_profiles']['Row']>
      }
      campaigns: {
        Row: {
          id: string
          workspace_id: string
          name: string
          description: string | null
          status: string
          created_at: string
          updated_at: string
        }
        Insert: Omit<Database['public']['Tables']['campaigns']['Row'], 'id' | 'created_at' | 'updated_at'>
        Update: Partial<Database['public']['Tables']['campaigns']['Row']>
      }
      subscriptions: {
        Row: {
          id: string
          user_id: string
          plan_id: string
          plan_name: string
          price_monthly_paise: number
          billing_cycle: 'monthly' | 'yearly'
          phonepe_subscription_id: string | null
          phonepe_customer_id: string | null
          phonepe_transaction_id: string | null
          status: 'pending' | 'active' | 'past_due' | 'cancelled' | 'expired'
          current_period_start: string | null
          current_period_end: string | null
          cancelled_at: string | null
          trial_end: string | null
          created_at: string
          updated_at: string
        }
        Insert: Omit<Database['public']['Tables']['subscriptions']['Row'], 'id' | 'created_at' | 'updated_at'>
        Update: Partial<Database['public']['Tables']['subscriptions']['Row']>
      }
      payment_transactions: {
        Row: {
          id: string
          user_id: string
          transaction_id: string
          amount_paise: number
          currency: string
          subscription_id: string | null
          plan_id: string | null
          billing_cycle: 'monthly' | 'yearly' | null
          status: 'initiated' | 'pending' | 'completed' | 'failed' | 'refunded' | 'cancelled'
          phonepe_response: any | null
          refund_amount_paise: number
          refund_id: string | null
          refund_reason: string | null
          metadata: any | null
          created_at: string
          updated_at: string
          completed_at: string | null
        }
        Insert: Omit<Database['public']['Tables']['payment_transactions']['Row'], 'id' | 'created_at' | 'updated_at' | 'completed_at'>
        Update: Partial<Database['public']['Tables']['payment_transactions']['Row']>
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      user_has_permission: {
        Args: {
          p_user_id: string
          p_permission_name: string
          p_workspace_id?: string
        }
        Returns: boolean
      }
      current_user_has_permission: {
        Args: {
          p_permission_name: string
        }
        Returns: boolean
      }
      get_user_permissions: {
        Args: {
          p_user_id: string
        }
        Returns: {
          permission_name: string
          resource: string
          action: string
          description: string | null
          category: string
          granted_at: string
          expires_at: string | null
          is_user_specific: boolean
        }[]
      }
      grant_user_permission: {
        Args: {
          p_user_id: string
          p_permission_name: string
          p_granted?: boolean
          p_expires_at?: string
          p_reason?: string
        }
        Returns: boolean
      }
      user_owns_workspace: {
        Args: {
          workspace_uuid: string
        }
        Returns: boolean
      }
      is_workspace_owner: {
        Args: {
          workspace_id: string
        }
        Returns: boolean
      }
      verify_rls_protection: {
        Args: Record<PropertyKey, never>
        Returns: {
          table_name: string
          rls_enabled: boolean
          policy_count: number
          status: string
        }[]
      }
      security_audit_report: {
        Args: Record<PropertyKey, never>
        Returns: {
          check_name: string
          status: string
          details: any
          severity: string
        }[]
      }
    }
    Enums: {
      onboarding_status: 'pending_workspace' | 'pending_storage' | 'pending_plan_selection' | 'pending_payment' | 'active' | 'suspended' | 'cancelled'
      subscription_status: 'pending' | 'active' | 'past_due' | 'cancelled' | 'expired'
      billing_cycle: 'monthly' | 'yearly'
    }
  }
}
