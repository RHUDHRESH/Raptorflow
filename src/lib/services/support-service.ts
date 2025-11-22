/**
 * Support Service
 * Handles support feedback and customer intelligence loop
 */

import { supabase } from '../supabase';

export interface SupportFeedback {
  id: string;
  workspace_id: string;
  type: 'ticket' | 'review' | 'nps' | 'conversation' | 'complaint';
  source: string;
  title: string;
  content: string;
  sentiment: 'positive' | 'neutral' | 'negative' | 'critical';
  extracted_tags: string[];
  related_cohort_ids: string[];
  triggers_defensive_move: boolean;
  customer_id?: string;
  created_at: string;
}

export const supportService = {
  /**
   * Get all support feedback
   */
  async getAll(filters?: {
    sentiment?: SupportFeedback['sentiment'];
    type?: SupportFeedback['type'];
    triggersDefensiveMove?: boolean;
  }): Promise<SupportFeedback[]> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return [];
    }

    let query = supabase
      .from('support_feedback')
      .select('*')
      .order('created_at', { ascending: false });

    if (filters?.sentiment) {
      query = query.eq('sentiment', filters.sentiment);
    }

    if (filters?.type) {
      query = query.eq('type', filters.type);
    }

    if (filters?.triggersDefensiveMove !== undefined) {
      query = query.eq('triggers_defensive_move', filters.triggersDefensiveMove);
    }

    const { data, error } = await query;

    if (error) {
      console.error('Error fetching support feedback:', error);
      throw error;
    }

    return data || [];
  },

  /**
   * Get feedback by ID
   */
  async getById(id: string): Promise<SupportFeedback | null> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return null;
    }

    const { data, error } = await supabase
      .from('support_feedback')
      .select('*')
      .eq('id', id)
      .single();

    if (error) {
      console.error('Error fetching support feedback:', error);
      throw error;
    }

    return data;
  },

  /**
   * Create support feedback
   */
  async create(
    feedback: Omit<SupportFeedback, 'id' | 'workspace_id' | 'created_at'>
  ): Promise<SupportFeedback> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
      .from('support_feedback')
      .insert(feedback)
      .select()
      .single();

    if (error) {
      console.error('Error creating support feedback:', error);
      throw error;
    }

    return data;
  },

  /**
   * Extract intelligence from feedback (AI integration placeholder)
   */
  async extractIntelligence(
    feedbackId: string,
    cohorts: Array<{ id: string; tags: string[] }>
  ): Promise<{
    extractedTags: string[];
    relatedCohortIds: string[];
    triggersDefensiveMove: boolean;
    suggestedAction?: string;
  }> {
    // This would call AI to analyze the feedback and:
    // 1. Extract pain/desire tags
    // 2. Match to existing cohorts
    // 3. Determine if defensive move needed
    // For now, return placeholder
    console.log('extractIntelligence called - AI integration needed');
    return {
      extractedTags: [],
      relatedCohortIds: [],
      triggersDefensiveMove: false
    };
  },

  /**
   * Update feedback with extracted intelligence
   */
  async updateIntelligence(
    id: string,
    intelligence: {
      extracted_tags?: string[];
      related_cohort_ids?: string[];
      triggers_defensive_move?: boolean;
    }
  ): Promise<SupportFeedback> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
      .from('support_feedback')
      .update(intelligence)
      .eq('id', id)
      .select()
      .single();

    if (error) {
      console.error('Error updating support feedback:', error);
      throw error;
    }

    return data;
  },

  /**
   * Get feedback by cohort
   */
  async getByCohort(cohortId: string): Promise<SupportFeedback[]> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return [];
    }

    const { data, error } = await supabase
      .from('support_feedback')
      .select('*')
      .contains('related_cohort_ids', [cohortId])
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Error fetching feedback by cohort:', error);
      return [];
    }

    return data || [];
  },

  /**
   * Get critical feedback (negative/critical sentiment or triggers defensive move)
   */
  async getCritical(): Promise<SupportFeedback[]> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return [];
    }

    const { data, error } = await supabase
      .from('support_feedback')
      .select('*')
      .or('sentiment.eq.critical,sentiment.eq.negative,triggers_defensive_move.eq.true')
      .order('created_at', { ascending: false })
      .limit(20);

    if (error) {
      console.error('Error fetching critical feedback:', error);
      return [];
    }

    return data || [];
  },

  /**
   * Get sentiment summary
   */
  async getSentimentSummary(): Promise<{
    positive: number;
    neutral: number;
    negative: number;
    critical: number;
    total: number;
  }> {
    if (!supabase) {
      return { positive: 0, neutral: 0, negative: 0, critical: 0, total: 0 };
    }

    const { data, error } = await supabase
      .from('support_feedback')
      .select('sentiment');

    if (error) {
      console.error('Error fetching sentiment summary:', error);
      return { positive: 0, neutral: 0, negative: 0, critical: 0, total: 0 };
    }

    const summary = {
      positive: 0,
      neutral: 0,
      negative: 0,
      critical: 0,
      total: data?.length || 0
    };

    data?.forEach(item => {
      if (item.sentiment) {
        summary[item.sentiment]++;
      }
    });

    return summary;
  },

  /**
   * Import feedback from external source (placeholder)
   */
  async importFromSource(
    source: string,
    feedbackItems: Array<{
      title: string;
      content: string;
      customerId?: string;
      timestamp: string;
    }>
  ): Promise<SupportFeedback[]> {
    // This would integrate with Zendesk, Intercom, etc.
    console.log(`Import from ${source} - integration needed`);
    return [];
  }
};

