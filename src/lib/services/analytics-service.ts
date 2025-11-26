/**
 * Analytics Service
 * Handles metrics aggregation and health status calculations
 */

import { supabase } from '../supabase';

export interface MoveMetrics {
  move_id: string;
  date: string;
  impressions?: number;
  clicks?: number;
  replies?: number;
  sqls?: number;
  mqls?: number;
  demos?: number;
  closed_won?: number;
  ctr?: number;
  engagement_rate?: number;
  conversion_rate?: number;
  revenue?: number;
  cost?: number;
  roi?: number;
}

export interface HealthStatus {
  status: 'green' | 'amber' | 'red';
  score: number;
  factors: {
    name: string;
    value: number;
    weight: number;
    status: 'green' | 'amber' | 'red';
  }[];
}

export const analyticsService = {
  /**
   * Get metrics for a move
   */
  async getMoveMetrics(moveId: string): Promise<MoveMetrics[]> {
    if (!supabase) {
      console.warn('Supabase not configured, returning empty array');
      return [];
    }

    const { data, error } = await supabase
      .from('move_logs')
      .select('*')
      .eq('move_id', moveId)
      .order('date', { ascending: true });

    if (error) {
      console.error('Error fetching move metrics:', error);
      throw error;
    }

    return (data || []).map((log: any) => ({
      move_id: log.move_id,
      date: log.date,
      ...(log.metrics_snapshot || {}),
    }));
  },

  /**
   * Log daily metrics for a move
   */
  async logMetrics(moveId: string, date: string, metrics: Partial<MoveMetrics>): Promise<void> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { error } = await supabase
      .from('move_logs')
      .upsert([{
        move_id: moveId,
        date,
        metrics_snapshot: metrics,
      }], {
        onConflict: 'move_id,date',
      });

    if (error) {
      console.error('Error logging metrics:', error);
      throw error;
    }
  },

  /**
   * Calculate health status for a move
   */
  calculateHealth(move: any, metrics: MoveMetrics[]): HealthStatus {
    const factors = [];
    
    // Factor 1: Progress vs Time (30% weight)
    const daysElapsed = this.getDaysElapsed(move.start_date);
    const totalDays = this.getDaysBetween(move.start_date, move.end_date);
    const timeProgress = totalDays > 0 ? (daysElapsed / totalDays) * 100 : 0;
    const progressDelta = move.progress_percentage - timeProgress;
    
    factors.push({
      name: 'Schedule',
      value: progressDelta,
      weight: 0.3,
      status: progressDelta >= -5 ? 'green' : progressDelta >= -15 ? 'amber' : 'red',
    });

    // Factor 2: Metrics performance (40% weight)
    const latestMetrics = metrics[metrics.length - 1];
    let metricsStatus: 'green' | 'amber' | 'red' = 'green';
    let metricsValue = 100;

    if (latestMetrics) {
      // Check conversion rates, engagement, etc.
      const ctr = latestMetrics.ctr || 0;
      const engagementRate = latestMetrics.engagement_rate || 0;
      
      if (ctr < 1 || engagementRate < 2) {
        metricsStatus = 'red';
        metricsValue = 30;
      } else if (ctr < 2 || engagementRate < 4) {
        metricsStatus = 'amber';
        metricsValue = 60;
      }
    }

    factors.push({
      name: 'Performance',
      value: metricsValue,
      weight: 0.4,
      status: metricsStatus,
    });

    // Factor 3: Anomalies count (20% weight)
    const anomalyCount = move.anomalies_detected?.length || 0;
    const anomalyStatus = anomalyCount === 0 ? 'green' : anomalyCount <= 2 ? 'amber' : 'red';
    
    factors.push({
      name: 'Anomalies',
      value: Math.max(0, 100 - (anomalyCount * 20)),
      weight: 0.2,
      status: anomalyStatus,
    });

    // Factor 4: OODA progression (10% weight)
    const statusWeight = this.getStatusWeight(move.status);
    factors.push({
      name: 'OODA Progress',
      value: statusWeight,
      weight: 0.1,
      status: statusWeight > 60 ? 'green' : statusWeight > 30 ? 'amber' : 'red',
    });

    // Calculate weighted score
    const score = factors.reduce((sum, factor) => 
      sum + (factor.value * factor.weight), 0
    );

    // Determine overall status
    const status: 'green' | 'amber' | 'red' = 
      score >= 70 ? 'green' : score >= 40 ? 'amber' : 'red';

    return {
      status,
      score: Math.round(score),
      factors,
    };
  },

  /**
   * Get aggregate metrics for a sprint
   */
  async getSprintMetrics(sprintId: string): Promise<any> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return null;
    }

    // Get all moves in sprint
    const { data: moves, error } = await supabase
      .from('moves')
      .select('id')
      .eq('sprint_id', sprintId);

    if (error || !moves) {
      console.error('Error fetching sprint moves:', error);
      return null;
    }

    const moveIds = moves.map((m: any) => m.id);

    // Get all metrics for these moves
    const { data: logs, error: logsError } = await supabase
      .from('move_logs')
      .select('*')
      .in('move_id', moveIds);

    if (logsError) {
      console.error('Error fetching logs:', logsError);
      return null;
    }

    // Aggregate metrics
    const totals = (logs || []).reduce((acc: any, log: any) => {
      const metrics = log.metrics_snapshot || {};
      acc.impressions += metrics.impressions || 0;
      acc.clicks += metrics.clicks || 0;
      acc.replies += metrics.replies || 0;
      acc.sqls += metrics.sqls || 0;
      acc.demos += metrics.demos || 0;
      acc.revenue += metrics.revenue || 0;
      acc.cost += metrics.cost || 0;
      return acc;
    }, {
      impressions: 0,
      clicks: 0,
      replies: 0,
      sqls: 0,
      demos: 0,
      revenue: 0,
      cost: 0,
    });

    // Calculate derived metrics
    totals.ctr = totals.impressions > 0 ? (totals.clicks / totals.impressions) * 100 : 0;
    totals.roi = totals.cost > 0 ? ((totals.revenue - totals.cost) / totals.cost) * 100 : 0;

    return totals;
  },

  /**
   * Get trend data for a metric
   */
  async getMetricTrend(moveId: string, metricName: string, days: number = 30): Promise<any[]> {
    if (!supabase) {
      console.warn('Supabase not configured, returning empty array');
      return [];
    }

    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);

    const { data, error } = await supabase
      .from('move_logs')
      .select('date, metrics_snapshot')
      .eq('move_id', moveId)
      .gte('date', startDate.toISOString().split('T')[0])
      .order('date', { ascending: true });

    if (error) {
      console.error('Error fetching metric trend:', error);
      return [];
    }

    return (data || []).map((log: any) => ({
      date: log.date,
      value: log.metrics_snapshot?.[metricName] || 0,
    }));
  },

  /**
   * Compare move performance to baseline
   */
  detectDrift(current: MoveMetrics, baseline: MoveMetrics, threshold: number = 20): boolean {
    const metrics = ['ctr', 'engagement_rate', 'conversion_rate'];
    
    for (const metric of metrics) {
      const currentValue = (current as any)[metric] || 0;
      const baselineValue = (baseline as any)[metric] || 0;
      
      if (baselineValue > 0) {
        const percentChange = Math.abs((currentValue - baselineValue) / baselineValue) * 100;
        if (percentChange > threshold) {
          return true; // Drift detected
        }
      }
    }
    
    return false;
  },

  /**
   * Get workspace-wide metrics
   */
  async getWorkspaceMetrics(): Promise<any> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return null;
    }

    // Get all moves
    const { data: moves, error } = await supabase
      .from('moves')
      .select('id, status');

    if (error) {
      console.error('Error fetching workspace moves:', error);
      return null;
    }

    const stats = {
      total_moves: moves?.length || 0,
      active_moves: moves?.filter((m: any) => 
        m.status.includes('OODA') && m.status !== 'Complete' && m.status !== 'Killed'
      ).length || 0,
      completed_moves: moves?.filter((m: any) => m.status === 'Complete').length || 0,
      killed_moves: moves?.filter((m: any) => m.status === 'Killed').length || 0,
    };

    return stats;
  },

  // Helper functions
  getDaysElapsed(startDate: string): number {
    const start = new Date(startDate);
    const now = new Date();
    const diff = now.getTime() - start.getTime();
    return Math.floor(diff / (1000 * 60 * 60 * 24));
  },

  getDaysBetween(startDate: string, endDate: string): number {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diff = end.getTime() - start.getTime();
    return Math.floor(diff / (1000 * 60 * 60 * 24));
  },

  getStatusWeight(status: string): number {
    const weights: Record<string, number> = {
      'Planning': 10,
      'OODA_Observe': 25,
      'OODA_Orient': 50,
      'OODA_Decide': 75,
      'OODA_Act': 90,
      'Complete': 100,
      'Killed': 0,
    };
    return weights[status] || 0;
  },
};





