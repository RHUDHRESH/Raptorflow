import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { env } from '../config/env';

// Create Supabase client with service role key for backend operations
const supabaseUrl = env.SUPABASE_URL || 'https://vpwwzsanuyhpkvgorcnc.supabase.co';
const supabaseServiceKey = env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseServiceKey) {
  console.warn('⚠️ SUPABASE_SERVICE_ROLE_KEY not set. Using limited access.');
}

export const supabase: SupabaseClient = createClient(
  supabaseUrl,
  supabaseServiceKey || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIzOTk1OTEsImV4cCI6MjA3Nzk3NTU5MX0.-clyTrDDlCNpUGg-MEgXIki70uBt4oIFPuSA8swNuTU',
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
  async createPayment(userId: string, plan: string, amount: number, txnId: string) {
    const { data, error } = await supabase
      .from('payments')
      .insert({
        user_id: userId,
        plan,
        amount,
        phonepe_merchant_transaction_id: txnId,
        status: 'initiated'
      })
      .select()
      .single();
    return { data, error };
  },

  async updatePayment(txnId: string, updates: any) {
    const { data, error } = await supabase
      .from('payments')
      .update(updates)
      .eq('phonepe_merchant_transaction_id', txnId)
      .select()
      .single();
    return { data, error };
  },

  async getPayment(txnId: string) {
    const { data, error } = await supabase
      .from('payments')
      .select('*')
      .eq('phonepe_merchant_transaction_id', txnId)
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
    const { data, error } = await supabase
      .from('profiles')
      .update({
        plan,
        plan_status: 'active',
        plan_started_at: new Date().toISOString(),
        last_payment_id: paymentId,
        last_payment_amount: amount,
        last_payment_date: new Date().toISOString(),
        payment_status: 'completed'
      })
      .eq('id', userId)
      .select()
      .single();
    return { data, error };
  }
};

export default supabase;

