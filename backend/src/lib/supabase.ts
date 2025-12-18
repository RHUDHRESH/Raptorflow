import crypto from 'crypto';
import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { env } from '../config/env';

// Create Supabase client with service role key for backend operations
const supabaseUrl = env.SUPABASE_URL || 'https://vpwwzsanuyhpkvgorcnc.supabase.co';
const isValidKey = (key?: string) => !!key && key.split('.').length === 3;
const supabaseServiceKey = env.SUPABASE_SERVICE_ROLE_KEY || env.SUPABASE_ANON_KEY;

if (!isValidKey(supabaseServiceKey)) {
  if (env.NODE_ENV === 'production') {
    throw new Error('Supabase key missing or malformed. Set SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY.');
  }
  console.warn('Supabase key missing or malformed. Set SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY.');
}

 function mapFrontendPlanToDbPlanCode(plan: string): string {
   switch ((plan || '').toLowerCase()) {
     case 'ascent':
       return 'starter';
     case 'glide':
       return 'growth';
     case 'soar':
       return 'enterprise';
     default:
       return (plan || '').toLowerCase();
   }
 }

 function mapDbPlanCodeToFrontendPlan(planCode: string): string {
   switch ((planCode || '').toLowerCase()) {
     case 'starter':
       return 'ascent';
     case 'growth':
       return 'glide';
     case 'enterprise':
       return 'soar';
     default:
       return (planCode || '').toLowerCase();
   }
 }

 function mapPaymentStatusToDb(status: string | undefined): string | undefined {
   if (!status) return status;
   const normalized = status.toLowerCase();
   if (normalized === 'completed') return 'success';
   if (normalized === 'initiated') return 'initiated';
   if (normalized === 'pending') return 'pending';
   if (normalized === 'processing') return 'processing';
   if (normalized === 'failed') return 'failed';
   if (normalized === 'success') return 'success';
   return normalized;
 }

 function mapPaymentStatusFromDb(status: string | undefined): string | undefined {
   if (!status) return status;
   const normalized = status.toLowerCase();
   if (normalized === 'success') return 'completed';
   return normalized;
 }
export const supabase: SupabaseClient = createClient(
  supabaseUrl,
  supabaseServiceKey || '',
  {
    auth: {
      autoRefreshToken: false,
      persistSession: false
    }
  }
);

// Database service functions
export const db = {
  // Onboarding Intake
  async getIntake(userId: string) {
    const { data, error } = await supabase
      .from('onboarding_intake')
      .select('*')
      .eq('user_id', userId)
      .single();
    return { data, error };
  },

  async createPaymentMandate(params: {
    organizationId: string;
    subscriptionId?: string;
    maxAmountPaise: number;
    provider: string;
    mandateType: 'upi_autopay' | 'card_recurring' | 'upi' | 'card' | 'netbanking' | 'wallet';
    validFrom: string;
    validUntil: string;
    status?: string;
    providerMandateId?: string;
  }) {
    const { data, error } = await supabase
      .from('payment_mandates')
      .insert({
        organization_id: params.organizationId,
        subscription_id: params.subscriptionId || null,
        mandate_type: params.mandateType,
        provider: params.provider,
        provider_mandate_id: params.providerMandateId || null,
        max_amount_paise: params.maxAmountPaise,
        valid_from: params.validFrom,
        valid_until: params.validUntil,
        status: params.status || 'pending_authorization'
      })
      .select('*')
      .single();

    return { data, error };
  },

  async linkMandateToSubscription(subscriptionId: string, mandateId: string) {
    const { data, error } = await supabase
      .from('subscriptions')
      .update({
        mandate_id: mandateId,
        autopay_enabled: false,
        updated_at: new Date().toISOString()
      })
      .eq('id', subscriptionId)
      .select('id, mandate_id, autopay_enabled')
      .single();

    return { data, error };
  },

  async getLatestMandateForOrg(organizationId: string) {
    const { data, error } = await supabase
      .from('payment_mandates')
      .select('*')
      .eq('organization_id', organizationId)
      .order('created_at', { ascending: false })
      .limit(1)
      .maybeSingle();

    return { data, error };
  },

  async markOnboardingCompleted(userId: string) {
    const { data, error } = await supabase
      .from('profiles')
      .update({
        onboarding_completed: true,
        onboarding_completed_at: new Date().toISOString()
      })
      .eq('id', userId)
      .select('id, onboarding_completed, onboarding_completed_at')
      .single();

    return { data, error };
  },

  async createIntake(userId: string) {
    const { data, error } = await supabase
      .from('onboarding_intake')
      .insert({
        user_id: userId,
        current_step: 1,
        completed_steps: [],
        mode: 'self-service'
      })
      .select()
      .single();
    return { data, error };
  },

  async updateIntake(id: string, updates: any) {
    const { data, error } = await supabase
      .from('onboarding_intake')
      .update({
        ...updates,
        updated_at: new Date().toISOString()
      })
      .eq('id', id)
      .select()
      .single();
    return { data, error };
  },

  async getOrCreateIntake(userId: string) {
    let { data, error } = await this.getIntake(userId);
    
    if (error || !data) {
      const result = await this.createIntake(userId);
      data = result.data;
      error = result.error;
    }
    
    return { data, error };
  },

  // Agent Executions
  async logAgentExecution(intakeId: string, agentName: string, input: any) {
    const { data, error } = await supabase
      .from('agent_executions')
      .insert({
        intake_id: intakeId,
        agent_name: agentName,
        input,
        status: 'running',
        started_at: new Date().toISOString()
      })
      .select()
      .single();
    return { data, error };
  },

  async updateAgentExecution(id: string, output: any, status: string, error?: string) {
    const { data, error: dbError } = await supabase
      .from('agent_executions')
      .update({
        output,
        status,
        error,
        completed_at: new Date().toISOString()
      })
      .eq('id', id)
      .select()
      .single();
    return { data, error: dbError };
  },

  // Shared Links
  async createSharedLink(intakeId: string, salesRepId: string, token: string) {
    const { data, error } = await supabase
      .from('shared_links')
      .insert({
        intake_id: intakeId,
        sales_rep_id: salesRepId,
        token,
        expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString() // 7 days
      })
      .select()
      .single();
    return { data, error };
  },

  async getSharedLink(token: string) {
    const { data, error } = await supabase
      .from('shared_links')
      .select('*, onboarding_intake(*)')
      .eq('token', token)
      .single();
    
    if (data) {
      // Increment access count
      await supabase
        .from('shared_links')
        .update({
          accessed_count: (data.accessed_count || 0) + 1,
          last_accessed_at: new Date().toISOString()
        })
        .eq('token', token);
    }
    
    return { data, error };
  },

  // Payments
  async getOrCreateCurrentOrgId(userId: string, email?: string) {
    const { data: profile, error: profileError } = await supabase
      .from('profiles')
      .select('current_org_id')
      .eq('id', userId)
      .single();

    if (profileError) {
      return { data: null, error: profileError };
    }

    if (profile?.current_org_id) {
      return { data: profile.current_org_id as string, error: null };
    }

    const slug = `org-${userId.slice(0, 8)}-${crypto.randomBytes(3).toString('hex')}`;
    const orgName = email ? `${email.split('@')[0] || 'Workspace'}` : 'Workspace';

    const { data: org, error: orgError } = await supabase
      .from('organizations')
      .insert({
        name: orgName,
        slug
      })
      .select('id')
      .single();

    if (orgError || !org) {
      return { data: null, error: orgError || new Error('Failed to create organization') };
    }

    const { error: memberError } = await supabase
      .from('organization_members')
      .insert({
        organization_id: org.id,
        user_id: userId,
        role: 'owner',
        is_active: true
      });

    if (memberError) {
      return { data: null, error: memberError };
    }

    const { error: profileUpdateError } = await supabase
      .from('profiles')
      .update({ current_org_id: org.id })
      .eq('id', userId);

    if (profileUpdateError) {
      return { data: null, error: profileUpdateError };
    }

    return { data: org.id as string, error: null };
  },

  async getOrgPlanCohortLimit(organizationId: string) {
    const { data: subscription, error: subError } = await supabase
      .from('subscriptions')
      .select('id, status, plan:plans(code, cohort_limit)')
      .eq('organization_id', organizationId)
      .is('deleted_at', null)
      .order('created_at', { ascending: false })
      .limit(1)
      .maybeSingle();

    if (subError) {
      return { data: null, error: subError };
    }

    const plan: any = (subscription as any)?.plan;
    if (plan?.cohort_limit) {
      return {
        data: {
          cohortLimit: plan.cohort_limit as number,
          planCode: plan.code as string
        },
        error: null
      };
    }

    const { data: freePlan, error: freePlanError } = await supabase
      .from('plans')
      .select('code, cohort_limit')
      .eq('code', 'free')
      .maybeSingle();

    if (freePlanError) {
      return { data: null, error: freePlanError };
    }

    return {
      data: {
        cohortLimit: (freePlan as any)?.cohort_limit || 1,
        planCode: (freePlan as any)?.code || 'free'
      },
      error: null
    };
  },

  async upsertSubscriptionForOrg(organizationId: string, planCode: string, status: string) {
    const dbPlanCode = mapFrontendPlanToDbPlanCode(planCode);
    const { data: plan, error: planError } = await supabase
      .from('plans')
      .select('id, code, price_monthly_paise')
      .eq('code', dbPlanCode)
      .maybeSingle();

    if (planError || !plan) {
      return { data: null, error: planError || new Error('Unknown plan') };
    }

    const now = new Date();
    const periodEnd = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000);

    const { data: existing, error: existingError } = await supabase
      .from('subscriptions')
      .select('id')
      .eq('organization_id', organizationId)
      .is('deleted_at', null)
      .order('created_at', { ascending: false })
      .limit(1)
      .maybeSingle();

    if (existingError) {
      return { data: null, error: existingError };
    }

    if (existing?.id) {
      const { data, error } = await supabase
        .from('subscriptions')
        .update({
          plan_id: (plan as any).id,
          amount_paise: (plan as any).price_monthly_paise,
          billing_cycle: 'monthly',
          current_period_start: now.toISOString(),
          current_period_end: periodEnd.toISOString(),
          status
        })
        .eq('id', existing.id)
        .select('id, organization_id, status, plan:plans(code)')
        .single();

      return { data, error };
    }

    const { data, error } = await supabase
      .from('subscriptions')
      .insert({
        organization_id: organizationId,
        plan_id: (plan as any).id,
        amount_paise: (plan as any).price_monthly_paise,
        currency: 'INR',
        billing_cycle: 'monthly',
        current_period_start: now.toISOString(),
        current_period_end: periodEnd.toISOString(),
        status
      })
      .select('id, organization_id, status, plan:plans(code)')
      .single();

    return { data, error };
  },

  async createPayment(userId: string, plan: string, amount: number, txnId: string, userEmail?: string) {
    const { data: organizationId, error: orgError } = await this.getOrCreateCurrentOrgId(userId, userEmail);
    if (orgError || !organizationId) {
      return { data: null, error: orgError || new Error('Organization not found') };
    }

    const { data: subscription, error: subError } = await this.upsertSubscriptionForOrg(
      organizationId,
      plan,
      'paused'
    );

    if (subError || !subscription) {
      return { data: null, error: subError || new Error('Failed to create subscription') };
    }

    const { data, error } = await supabase
      .from('payments')
      .insert({
        organization_id: organizationId,
        subscription_id: (subscription as any).id,
        amount_paise: amount,
        currency: 'INR',
        payment_method: 'upi',
        provider: 'phonepe',
        provider_order_id: txnId,
        status: 'initiated',
        idempotency_key: txnId
      })
      .select('*')
      .single();

    return { data, error };
  },

  async updatePayment(txnId: string, updates: any) {
    const next: any = { ...updates };

    if (next.phonepe_transaction_id && !next.provider_payment_id) {
      next.provider_payment_id = next.phonepe_transaction_id;
    }
    delete next.phonepe_transaction_id;
    delete next.phonepe_response;
    delete next.completed_at;

    if (next.error && !next.response_message) {
      next.response_message = next.error;
    }
    delete next.error;

    if (typeof next.status === 'string') {
      next.status = mapPaymentStatusToDb(next.status);
    }

    const allowedKeys = new Set([
      'status',
      'provider_payment_id',
      'provider_order_id',
      'response_code',
      'response_message',
      'subscription_id',
      'payment_method',
      'amount_paise',
      'currency',
      'ip_address',
      'idempotency_key'
    ]);

    const sanitized: any = {};
    for (const [key, value] of Object.entries(next)) {
      if (allowedKeys.has(key)) sanitized[key] = value;
    }

    const { data, error } = await supabase
      .from('payments')
      .update(sanitized)
      .eq('idempotency_key', txnId)
      .select('*')
      .single();

    return { data, error };
  },

  async getPayment(txnId: string) {
    const { data, error } = await supabase
      .from('payments')
      .select('*')
      .or(`idempotency_key.eq.${txnId},provider_order_id.eq.${txnId}`)
      .maybeSingle();

    if (data && (data as any).status) {
      (data as any).status = mapPaymentStatusFromDb((data as any).status);
    }

    return { data, error };
  },

  async getPaymentWithSubscriptionAndPlan(txnId: string) {
    const { data, error } = await supabase
      .from('payments')
      .select(
        '*, subscription:subscriptions(id, status, plan:plans(code, name, price_monthly_paise))'
      )
      .or(`idempotency_key.eq.${txnId},provider_order_id.eq.${txnId}`)
      .maybeSingle();

    if (data && (data as any).status) {
      (data as any).status = mapPaymentStatusFromDb((data as any).status);
    }

    return { data, error };
  },

  async activateSubscription(subscriptionId: string) {
    const now = new Date();
    const periodEnd = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000);

    const { data, error } = await supabase
      .from('subscriptions')
      .update({
        status: 'active',
        current_period_start: now.toISOString(),
        current_period_end: periodEnd.toISOString()
      })
      .eq('id', subscriptionId)
      .select('id, organization_id, status, plan:plans(code)')
      .single();

    return { data, error };
  },

  // User Profile
  async getProfile(userId: string) {
    const { data, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', userId)
      .single();
    return { data, error };
  },

  async updateProfile(userId: string, updates: any) {
    const { data, error } = await supabase
      .from('profiles')
      .update(updates)
      .eq('id', userId)
      .select()
      .single();
    return { data, error };
  },

  async activatePlan(userId: string, plan: string, paymentId: string, amount: number) {
    const { data: organizationId, error: orgError } = await this.getOrCreateCurrentOrgId(userId);
    if (orgError || !organizationId) {
      return { data: null, error: orgError || new Error('Organization not found') };
    }

    const { data: subscription, error: subError } = await this.upsertSubscriptionForOrg(
      organizationId,
      plan,
      'active'
    );

    if (subError || !subscription) {
      return { data: null, error: subError || new Error('Failed to activate subscription') };
    }

    await supabase
      .from('payments')
      .update({
        subscription_id: (subscription as any).id,
        status: 'success'
      })
      .eq('id', paymentId);

    const { data, error } = await supabase
      .from('profiles')
      .update({
        onboarding_completed: true
      })
      .eq('id', userId)
      .select()
      .single();

    return { data, error };
  },

  mapDbPlanCodeToFrontendPlan(planCode: string) {
    return mapDbPlanCodeToFrontendPlan(planCode);
  }
};

export default supabase;



