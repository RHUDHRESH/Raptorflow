/**
 * Database helper functions for all domain objects
 * Centralizes Supabase queries for the RaptorFlow platform
 */

import { createClient } from '@supabase/supabase-js';
import { env } from '../config/env';

// Create Supabase client
const supabaseUrl = env.SUPABASE_URL || 'https://vpwwzsanuyhpkvgorcnc.supabase.co';
const isValidKey = (key?: string) => !!key && key.split('.').length === 3;
const supabaseKey = env.SUPABASE_SERVICE_ROLE_KEY;

if (!isValidKey(supabaseKey)) {
  throw new Error('Supabase API key missing. Set SUPABASE_SERVICE_ROLE_KEY.');
}
export const supabase = createClient(
  supabaseUrl,
  supabaseKey,
  {
    auth: {
      autoRefreshToken: false,
      persistSession: false
    }
  }
);
import type {
  ICP, CreateICPInput,
  Cohort,
  Barrier, BarrierType,
  Protocol, ProtocolType,
  MoveTemplate,
  Campaign, CreateCampaignInput, CampaignStatus,
  Move, CreateMoveInput, MoveStatus,
  Asset, CreateAssetInput, AssetStatus,
  Metric, CreateMetricInput,
  Spike, CreateSpikeInput, SpikeStatus,
  Guardrail, CreateGuardrailInput,
  GuardrailEvent,
  Experiment
} from '../types';

// =====================================================
// ICP OPERATIONS
// =====================================================

export const icpDb = {
  async list(userId: string, options?: { includeArchived?: boolean }) {
    let query = supabase
      .from('icps')
      .select('*')
      .eq('user_id', userId)
      .order('priority_rank', { ascending: true });
    
    if (!options?.includeArchived) {
      query = query.eq('is_archived', false);
    }
    
    return query;
  },

  async getById(id: string, userId: string) {
    return supabase
      .from('icps')
      .select('*')
      .eq('id', id)
      .eq('user_id', userId)
      .single();
  },

  async create(userId: string, data: CreateICPInput) {
    return supabase
      .from('icps')
      .insert({
        user_id: userId,
        ...data,
        slug: data.label.toLowerCase().replace(/\s+/g, '-')
      })
      .select()
      .single();
  },

  async createMany(userId: string, icps: CreateICPInput[]) {
    const icpsWithUser = icps.map((icp, index) => ({
      user_id: userId,
      ...icp,
      slug: icp.label.toLowerCase().replace(/\s+/g, '-'),
      priority_rank: index + 1
    }));
    
    return supabase
      .from('icps')
      .insert(icpsWithUser)
      .select();
  },

  async update(id: string, userId: string, data: Partial<CreateICPInput>) {
    return supabase
      .from('icps')
      .update(data)
      .eq('id', id)
      .eq('user_id', userId)
      .select()
      .single();
  },

  async delete(id: string, userId: string) {
    return supabase
      .from('icps')
      .delete()
      .eq('id', id)
      .eq('user_id', userId);
  },

  async archive(id: string, userId: string) {
    return supabase
      .from('icps')
      .update({ is_archived: true })
      .eq('id', id)
      .eq('user_id', userId);
  },

  async updateSelection(id: string, userId: string, isSelected: boolean) {
    return supabase
      .from('icps')
      .update({ is_selected: isSelected })
      .eq('id', id)
      .eq('user_id', userId);
  },

  async updatePriority(userId: string, icpPriorities: { id: string; priority_rank: number }[]) {
    const updates = icpPriorities.map(({ id, priority_rank }) =>
      supabase
        .from('icps')
        .update({ priority_rank })
        .eq('id', id)
        .eq('user_id', userId)
    );
    
    return Promise.all(updates);
  }
};

// =====================================================
// COHORT OPERATIONS
// =====================================================

export const cohortDb = {
  async list(userId: string) {
    return supabase
      .from('cohorts')
      .select('*, icp:icps(*)')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });
  },

  async getById(id: string, userId: string) {
    return supabase
      .from('cohorts')
      .select('*, icp:icps(*)')
      .eq('id', id)
      .eq('user_id', userId)
      .single();
  },

  async create(userId: string, data: Omit<Cohort, 'id' | 'user_id' | 'created_at' | 'updated_at'>) {
    return supabase
      .from('cohorts')
      .insert({ user_id: userId, ...data })
      .select()
      .single();
  },

  async update(id: string, userId: string, data: Partial<Cohort>) {
    return supabase
      .from('cohorts')
      .update(data)
      .eq('id', id)
      .eq('user_id', userId)
      .select()
      .single();
  },

  async delete(id: string, userId: string) {
    return supabase
      .from('cohorts')
      .delete()
      .eq('id', id)
      .eq('user_id', userId);
  }
};

// =====================================================
// BARRIER OPERATIONS
// =====================================================

export const barrierDb = {
  async list(userId: string, filters?: { icp_id?: string; barrier_type?: BarrierType }) {
    let query = supabase
      .from('barriers')
      .select('*')
      .eq('user_id', userId);
    
    if (filters?.icp_id) {
      query = query.eq('icp_id', filters.icp_id);
    }
    if (filters?.barrier_type) {
      query = query.eq('barrier_type', filters.barrier_type);
    }
    
    return query.order('diagnosed_at', { ascending: false });
  },

  async getByICP(icpId: string, userId: string) {
    return supabase
      .from('barriers')
      .select('*')
      .eq('icp_id', icpId)
      .eq('user_id', userId)
      .order('confidence', { ascending: false });
  },

  async create(userId: string, data: Omit<Barrier, 'id' | 'user_id' | 'diagnosed_at' | 'updated_at'>) {
    return supabase
      .from('barriers')
      .insert({ user_id: userId, ...data })
      .select()
      .single();
  },

  async update(id: string, userId: string, data: Partial<Barrier>) {
    return supabase
      .from('barriers')
      .update(data)
      .eq('id', id)
      .eq('user_id', userId)
      .select()
      .single();
  },

  async delete(id: string, userId: string) {
    return supabase
      .from('barriers')
      .delete()
      .eq('id', id)
      .eq('user_id', userId);
  }
};

// =====================================================
// PROTOCOL OPERATIONS (Read-only, system data)
// =====================================================

export const protocolDb = {
  async list() {
    return supabase
      .from('protocols')
      .select('*')
      .eq('is_active', true)
      .order('display_order', { ascending: true });
  },

  async getByCode(code: ProtocolType) {
    return supabase
      .from('protocols')
      .select('*')
      .eq('code', code)
      .single();
  },

  async getByBarrier(barrier: BarrierType) {
    return supabase
      .from('protocols')
      .select('*')
      .eq('targets_barrier', barrier)
      .eq('is_active', true);
  }
};

// =====================================================
// MOVE TEMPLATE OPERATIONS (Read-only, system data)
// =====================================================

export const moveTemplateDb = {
  async list() {
    return supabase
      .from('move_templates')
      .select('*')
      .eq('is_active', true)
      .order('display_order', { ascending: true });
  },

  async getBySlug(slug: string) {
    return supabase
      .from('move_templates')
      .select('*')
      .eq('slug', slug)
      .single();
  },

  async getByProtocol(protocol: ProtocolType) {
    return supabase
      .from('move_templates')
      .select('*')
      .eq('protocol_type', protocol)
      .eq('is_active', true);
  },

  async getByBarrier(barrier: BarrierType) {
    return supabase
      .from('move_templates')
      .select('*')
      .eq('barrier_type', barrier)
      .eq('is_active', true);
  }
};

// =====================================================
// CAMPAIGN OPERATIONS
// =====================================================

export const campaignDb = {
  async list(userId: string, filters?: { status?: CampaignStatus }) {
    let query = supabase
      .from('campaigns')
      .select('*')
      .eq('user_id', userId);
    
    if (filters?.status) {
      query = query.eq('status', filters.status);
    }
    
    return query.order('created_at', { ascending: false });
  },

  async getById(id: string, userId: string) {
    return supabase
      .from('campaigns')
      .select('*')
      .eq('id', id)
      .eq('user_id', userId)
      .single();
  },

  async getWithRelations(id: string, userId: string) {
    const { data: campaign, error } = await supabase
      .from('campaigns')
      .select('*')
      .eq('id', id)
      .eq('user_id', userId)
      .single();

    if (error || !campaign) return { data: null, error };

    // Get related moves
    const { data: moves } = await supabase
      .from('moves')
      .select('*')
      .eq('campaign_id', id)
      .eq('user_id', userId);

    // Get related ICPs
    const { data: icps } = campaign.icp_ids?.length > 0
      ? await supabase
          .from('icps')
          .select('*')
          .in('id', campaign.icp_ids)
      : { data: [] };

    return {
      data: { ...campaign, moves: moves || [], icps: icps || [] },
      error: null
    };
  },

  async create(userId: string, data: CreateCampaignInput) {
    return supabase
      .from('campaigns')
      .insert({
        user_id: userId,
        ...data,
        budget_plan: data.budget_plan || { total: 0, currency: 'INR', allocation: {} },
        targets: data.targets || {}
      })
      .select()
      .single();
  },

  async update(id: string, userId: string, data: Partial<Campaign>) {
    return supabase
      .from('campaigns')
      .update(data)
      .eq('id', id)
      .eq('user_id', userId)
      .select()
      .single();
  },

  async updateStatus(id: string, userId: string, status: CampaignStatus) {
    return supabase
      .from('campaigns')
      .update({ status })
      .eq('id', id)
      .eq('user_id', userId)
      .select()
      .single();
  },

  async delete(id: string, userId: string) {
    return supabase
      .from('campaigns')
      .delete()
      .eq('id', id)
      .eq('user_id', userId);
  }
};

// =====================================================
// MOVE OPERATIONS
// =====================================================

export const moveDb = {
  async list(userId: string, filters?: { campaign_id?: string; spike_id?: string; status?: MoveStatus }) {
    let query = supabase
      .from('moves')
      .select('*, template:move_templates(*), icp:icps(*)')
      .eq('user_id', userId);
    
    if (filters?.campaign_id) {
      query = query.eq('campaign_id', filters.campaign_id);
    }
    if (filters?.spike_id) {
      query = query.eq('spike_id', filters.spike_id);
    }
    if (filters?.status) {
      query = query.eq('status', filters.status);
    }
    
    return query.order('created_at', { ascending: false });
  },

  async getById(id: string, userId: string) {
    return supabase
      .from('moves')
      .select('*, template:move_templates(*), icp:icps(*), assets(*)')
      .eq('id', id)
      .eq('user_id', userId)
      .single();
  },

  async create(userId: string, data: CreateMoveInput) {
    return supabase
      .from('moves')
      .insert({
        user_id: userId,
        ...data,
        channels: data.channels || [],
        tasks: [],
        kpis: {}
      })
      .select()
      .single();
  },

  async update(id: string, userId: string, data: Partial<Move>) {
    return supabase
      .from('moves')
      .update(data)
      .eq('id', id)
      .eq('user_id', userId)
      .select()
      .single();
  },

  async updateStatus(id: string, userId: string, status: MoveStatus) {
    const updates: Partial<Move> = { status };
    
    if (status === 'running' && !updates.actual_start) {
      updates.actual_start = new Date().toISOString();
    }
    if (status === 'completed') {
      updates.actual_end = new Date().toISOString();
      updates.progress_percentage = 100;
    }
    
    return supabase
      .from('moves')
      .update(updates)
      .eq('id', id)
      .eq('user_id', userId)
      .select()
      .single();
  },

  async updateTasks(id: string, userId: string, tasks: Move['tasks']) {
    // Calculate progress based on completed tasks
    const completedTasks = tasks.filter(t => t.status === 'completed').length;
    const progress_percentage = tasks.length > 0 
      ? Math.round((completedTasks / tasks.length) * 100)
      : 0;
    
    return supabase
      .from('moves')
      .update({ tasks, progress_percentage })
      .eq('id', id)
      .eq('user_id', userId)
      .select()
      .single();
  },

  async delete(id: string, userId: string) {
    return supabase
      .from('moves')
      .delete()
      .eq('id', id)
      .eq('user_id', userId);
  }
};

// =====================================================
// ASSET OPERATIONS
// =====================================================

export const assetDb = {
  async list(userId: string, filters?: { move_id?: string; campaign_id?: string; status?: AssetStatus; asset_type?: string }) {
    let query = supabase
      .from('assets')
      .select('*')
      .eq('user_id', userId);
    
    if (filters?.move_id) query = query.eq('move_id', filters.move_id);
    if (filters?.campaign_id) query = query.eq('campaign_id', filters.campaign_id);
    if (filters?.status) query = query.eq('status', filters.status);
    if (filters?.asset_type) query = query.eq('asset_type', filters.asset_type);
    
    return query.order('created_at', { ascending: false });
  },

  async getById(id: string, userId: string) {
    return supabase
      .from('assets')
      .select('*')
      .eq('id', id)
      .eq('user_id', userId)
      .single();
  },

  async create(userId: string, data: CreateAssetInput) {
    return supabase
      .from('assets')
      .insert({
        user_id: userId,
        ...data,
        content_format: data.content_format || 'markdown',
        variants: [],
        distribution_links: {},
        performance_data: {},
        tags: []
      })
      .select()
      .single();
  },

  async update(id: string, userId: string, data: Partial<Asset>) {
    return supabase
      .from('assets')
      .update(data)
      .eq('id', id)
      .eq('user_id', userId)
      .select()
      .single();
  },

  async updateStatus(id: string, userId: string, status: AssetStatus) {
    const updates: Partial<Asset> = { status };
    
    if (status === 'approved') {
      updates.approved_at = new Date().toISOString();
    }
    if (status === 'deployed') {
      updates.deployed_at = new Date().toISOString();
    }
    
    return supabase
      .from('assets')
      .update(updates)
      .eq('id', id)
      .eq('user_id', userId)
      .select()
      .single();
  },

  async delete(id: string, userId: string) {
    return supabase
      .from('assets')
      .delete()
      .eq('id', id)
      .eq('user_id', userId);
  }
};

// =====================================================
// METRIC OPERATIONS
// =====================================================

export const metricDb = {
  async list(userId: string, filters?: { scope_type?: string; scope_id?: string; metric_name?: string }) {
    let query = supabase
      .from('metrics')
      .select('*')
      .eq('user_id', userId);
    
    if (filters?.scope_type) query = query.eq('scope_type', filters.scope_type);
    if (filters?.scope_id) query = query.eq('scope_id', filters.scope_id);
    if (filters?.metric_name) query = query.eq('metric_name', filters.metric_name);
    
    return query.order('recorded_at', { ascending: false });
  },

  async getLatest(userId: string, scopeType: string, scopeId: string) {
    return supabase
      .from('metrics')
      .select('*')
      .eq('user_id', userId)
      .eq('scope_type', scopeType)
      .eq('scope_id', scopeId)
      .order('recorded_at', { ascending: false })
      .limit(10);
  },

  async create(userId: string, data: CreateMetricInput) {
    return supabase
      .from('metrics')
      .insert({
        user_id: userId,
        ...data,
        rag_thresholds: data.rag_thresholds || {},
        raw_data: {}
      })
      .select()
      .single();
  },

  async createMany(userId: string, metrics: CreateMetricInput[]) {
    const metricsWithUser = metrics.map(m => ({
      user_id: userId,
      ...m,
      rag_thresholds: m.rag_thresholds || {},
      raw_data: {}
    }));
    
    return supabase
      .from('metrics')
      .insert(metricsWithUser)
      .select();
  },

  async delete(id: string, userId: string) {
    return supabase
      .from('metrics')
      .delete()
      .eq('id', id)
      .eq('user_id', userId);
  }
};

// =====================================================
// SPIKE OPERATIONS
// =====================================================

export const spikeDb = {
  async list(userId: string, filters?: { status?: SpikeStatus }) {
    let query = supabase
      .from('spikes')
      .select('*, primary_icp:icps!spikes_primary_icp_id_fkey(*)')
      .eq('user_id', userId);
    
    if (filters?.status) {
      query = query.eq('status', filters.status);
    }
    
    return query.order('created_at', { ascending: false });
  },

  async getById(id: string, userId: string) {
    return supabase
      .from('spikes')
      .select('*, primary_icp:icps!spikes_primary_icp_id_fkey(*)')
      .eq('id', id)
      .eq('user_id', userId)
      .single();
  },

  async getWithRelations(id: string, userId: string) {
    const { data: spike, error } = await supabase
      .from('spikes')
      .select('*, primary_icp:icps!spikes_primary_icp_id_fkey(*)')
      .eq('id', id)
      .eq('user_id', userId)
      .single();

    if (error || !spike) return { data: null, error };

    // Get related moves
    const { data: moves } = await supabase
      .from('moves')
      .select('*')
      .eq('spike_id', id);

    // Get campaign if linked
    const { data: campaign } = spike.campaign_id
      ? await supabase
          .from('campaigns')
          .select('*')
          .eq('id', spike.campaign_id)
          .single()
      : { data: null };

    // Get guardrails
    const { data: guardrails } = await supabase
      .from('guardrails')
      .select('*')
      .eq('spike_id', id);

    return {
      data: { ...spike, moves: moves || [], campaign, guardrails: guardrails || [] },
      error: null
    };
  },

  async create(userId: string, data: CreateSpikeInput) {
    return supabase
      .from('spikes')
      .insert({
        user_id: userId,
        ...data,
        secondary_icp_ids: data.secondary_icp_ids || [],
        barriers: data.barriers || [],
        protocols: data.protocols || [],
        move_ids: [],
        results: {},
        learnings: []
      })
      .select()
      .single();
  },

  async update(id: string, userId: string, data: Partial<Spike>) {
    return supabase
      .from('spikes')
      .update(data)
      .eq('id', id)
      .eq('user_id', userId)
      .select()
      .single();
  },

  async updateStatus(id: string, userId: string, status: SpikeStatus) {
    const updates: Partial<Spike> = { status };
    
    if (status === 'completed') {
      updates.completed_at = new Date().toISOString();
    }
    
    return supabase
      .from('spikes')
      .update(updates)
      .eq('id', id)
      .eq('user_id', userId)
      .select()
      .single();
  },

  async delete(id: string, userId: string) {
    return supabase
      .from('spikes')
      .delete()
      .eq('id', id)
      .eq('user_id', userId);
  }
};

// =====================================================
// GUARDRAIL OPERATIONS
// =====================================================

export const guardrailDb = {
  async list(userId: string, filters?: { spike_id?: string; campaign_id?: string; is_active?: boolean }) {
    let query = supabase
      .from('guardrails')
      .select('*')
      .eq('user_id', userId);
    
    if (filters?.spike_id) query = query.eq('spike_id', filters.spike_id);
    if (filters?.campaign_id) query = query.eq('campaign_id', filters.campaign_id);
    if (filters?.is_active !== undefined) query = query.eq('is_active', filters.is_active);
    
    return query.order('created_at', { ascending: false });
  },

  async getById(id: string, userId: string) {
    return supabase
      .from('guardrails')
      .select('*')
      .eq('id', id)
      .eq('user_id', userId)
      .single();
  },

  async create(userId: string, data: CreateGuardrailInput) {
    return supabase
      .from('guardrails')
      .insert({
        user_id: userId,
        ...data,
        action: data.action || 'alert_only'
      })
      .select()
      .single();
  },

  async update(id: string, userId: string, data: Partial<Guardrail>) {
    return supabase
      .from('guardrails')
      .update(data)
      .eq('id', id)
      .eq('user_id', userId)
      .select()
      .single();
  },

  async trigger(id: string, userId: string) {
    return supabase
      .from('guardrails')
      .update({
        is_triggered: true,
        last_triggered_at: new Date().toISOString(),
        trigger_count: supabase.rpc('increment_trigger_count', { row_id: id })
      })
      .eq('id', id)
      .eq('user_id', userId)
      .select()
      .single();
  },

  async delete(id: string, userId: string) {
    return supabase
      .from('guardrails')
      .delete()
      .eq('id', id)
      .eq('user_id', userId);
  },

  // Guardrail events
  async logEvent(userId: string, event: Omit<GuardrailEvent, 'id' | 'occurred_at'>) {
    return supabase
      .from('guardrail_events')
      .insert({ user_id: userId, ...event })
      .select()
      .single();
  },

  async getEvents(guardrailId: string, userId: string) {
    return supabase
      .from('guardrail_events')
      .select('*')
      .eq('guardrail_id', guardrailId)
      .eq('user_id', userId)
      .order('occurred_at', { ascending: false });
  }
};

// =====================================================
// EXPERIMENT OPERATIONS
// =====================================================

export const experimentDb = {
  async list(userId: string, filters?: { spike_id?: string; status?: string }) {
    let query = supabase
      .from('experiments')
      .select('*')
      .eq('user_id', userId);
    
    if (filters?.spike_id) query = query.eq('spike_id', filters.spike_id);
    if (filters?.status) query = query.eq('status', filters.status);
    
    return query.order('created_at', { ascending: false });
  },

  async create(userId: string, data: Omit<Experiment, 'id' | 'user_id' | 'created_at'>) {
    // Calculate EV score
    const ev_score = data.expected_impact && data.probability && data.effort
      ? (data.expected_impact * (data.probability / 100)) / data.effort
      : null;
    
    return supabase
      .from('experiments')
      .insert({ user_id: userId, ...data, ev_score })
      .select()
      .single();
  },

  async update(id: string, userId: string, data: Partial<Experiment>) {
    return supabase
      .from('experiments')
      .update(data)
      .eq('id', id)
      .eq('user_id', userId)
      .select()
      .single();
  },

  async delete(id: string, userId: string) {
    return supabase
      .from('experiments')
      .delete()
      .eq('id', id)
      .eq('user_id', userId);
  }
};

// Export all database modules
export const db = {
  icps: icpDb,
  cohorts: cohortDb,
  barriers: barrierDb,
  protocols: protocolDb,
  moveTemplates: moveTemplateDb,
  campaigns: campaignDb,
  moves: moveDb,
  assets: assetDb,
  metrics: metricDb,
  spikes: spikeDb,
  guardrails: guardrailDb,
  experiments: experimentDb
};


