/**
 * Kill Switch Service
 * Evaluates guardrails, triggers pauses, and logs events
 */

import { db } from '../lib/db';
import { metricsService, METRIC_DEFINITIONS, calculateRAGStatus } from './metricsService';
import type { Guardrail, GuardrailEvent, RAGStatus, Campaign, Spike } from '../types';

// =====================================================
// TYPES
// =====================================================

export interface GuardrailEvaluation {
  guardrail_id: string;
  name: string;
  is_triggered: boolean;
  metric_value: number;
  threshold: number;
  severity: 'warning' | 'critical';
  action_recommended: string;
  affected_entities?: {
    campaigns?: string[];
    moves?: string[];
  };
}

export interface KillSwitchReport {
  overall_status: 'ok' | 'warning' | 'critical';
  evaluations: GuardrailEvaluation[];
  actions_taken: string[];
  alerts: string[];
}

// =====================================================
// KILL SWITCH SERVICE CLASS
// =====================================================

export class KillSwitchService {
  /**
   * Evaluate all guardrails for a user
   */
  async evaluateAllGuardrails(userId: string): Promise<KillSwitchReport> {
    const { data: guardrails } = await db.guardrails.list(userId, { is_active: true });
    
    const evaluations: GuardrailEvaluation[] = [];
    const actionsTaken: string[] = [];
    const alerts: string[] = [];
    
    for (const guardrail of guardrails || []) {
      const evaluation = await this.evaluateGuardrail(userId, guardrail);
      evaluations.push(evaluation);
      
      if (evaluation.is_triggered) {
        // Log the event
        await db.guardrails.logEvent(userId, {
          guardrail_id: guardrail.id,
          user_id: userId,
          event_type: 'triggered',
          metric_value: evaluation.metric_value,
          threshold_value: evaluation.threshold,
          action_taken: evaluation.action_recommended,
          affected_entities: evaluation.affected_entities || {}
        });
        
        // Execute action based on guardrail configuration
        if (guardrail.action === 'auto_pause' || guardrail.action === 'pause_and_alert') {
          const paused = await this.executePause(userId, guardrail, evaluation);
          if (paused) {
            actionsTaken.push(`Auto-paused due to ${guardrail.name}: ${evaluation.action_recommended}`);
          }
        }
        
        if (guardrail.action === 'alert_only' || guardrail.action === 'pause_and_alert') {
          alerts.push(`⚠️ ${guardrail.name}: ${evaluation.metric_value} ${guardrail.operator} ${guardrail.threshold}`);
        }
        
        // Update guardrail trigger status
        await db.guardrails.update(guardrail.id, userId, {
          is_triggered: true,
          last_triggered_at: new Date().toISOString(),
          trigger_count: (guardrail.trigger_count || 0) + 1
        });
      } else if (guardrail.is_triggered) {
        // Guardrail was triggered but now resolved
        await db.guardrails.logEvent(userId, {
          guardrail_id: guardrail.id,
          user_id: userId,
          event_type: 'resolved',
          metric_value: evaluation.metric_value,
          threshold_value: evaluation.threshold,
          affected_entities: {}
        });
        
        await db.guardrails.update(guardrail.id, userId, {
          is_triggered: false
        });
      }
    }
    
    // Determine overall status
    let overallStatus: 'ok' | 'warning' | 'critical' = 'ok';
    const criticalCount = evaluations.filter(e => e.is_triggered && e.severity === 'critical').length;
    const warningCount = evaluations.filter(e => e.is_triggered && e.severity === 'warning').length;
    
    if (criticalCount > 0) {
      overallStatus = 'critical';
    } else if (warningCount > 0) {
      overallStatus = 'warning';
    }
    
    return {
      overall_status: overallStatus,
      evaluations,
      actions_taken: actionsTaken,
      alerts
    };
  }

  /**
   * Evaluate a single guardrail
   */
  async evaluateGuardrail(userId: string, guardrail: Guardrail): Promise<GuardrailEvaluation> {
    // Get the metric value
    const metricValue = await this.getMetricValue(userId, guardrail);
    
    // Check if triggered
    const isTriggered = this.checkThreshold(metricValue, guardrail);
    
    // Determine severity
    const severity = this.determineSeverity(metricValue, guardrail);
    
    // Get affected entities
    const affectedEntities = await this.getAffectedEntities(userId, guardrail);
    
    return {
      guardrail_id: guardrail.id,
      name: guardrail.name,
      is_triggered: isTriggered,
      metric_value: metricValue,
      threshold: guardrail.threshold,
      severity,
      action_recommended: this.getRecommendedAction(guardrail, metricValue, severity),
      affected_entities: affectedEntities
    };
  }

  /**
   * Get metric value for a guardrail
   */
  private async getMetricValue(userId: string, guardrail: Guardrail): Promise<number> {
    let scopeType = 'business';
    let scopeId = userId;
    
    if (guardrail.spike_id) {
      scopeType = 'spike';
      scopeId = guardrail.spike_id;
    } else if (guardrail.campaign_id) {
      scopeType = 'campaign';
      scopeId = guardrail.campaign_id;
    } else if (guardrail.icp_id) {
      scopeType = 'icp';
      scopeId = guardrail.icp_id;
    }
    
    const { data: metrics } = await db.metrics.getLatest(userId, scopeType, scopeId);
    const metric = metrics?.find(m => m.metric_name === guardrail.metric);
    
    return metric?.value || 0;
  }

  /**
   * Check if threshold is breached
   */
  private checkThreshold(value: number, guardrail: Guardrail): boolean {
    switch (guardrail.operator) {
      case 'greater_than':
        return value > guardrail.threshold;
      case 'less_than':
        return value < guardrail.threshold;
      case 'equals':
        return value === guardrail.threshold;
      case 'between':
        return guardrail.threshold_upper !== undefined &&
          value >= guardrail.threshold && value <= guardrail.threshold_upper;
      default:
        return false;
    }
  }

  /**
   * Determine severity based on how far past the threshold
   */
  private determineSeverity(value: number, guardrail: Guardrail): 'warning' | 'critical' {
    const threshold = guardrail.threshold;
    let deviation: number;
    
    switch (guardrail.operator) {
      case 'greater_than':
        deviation = ((value - threshold) / threshold) * 100;
        break;
      case 'less_than':
        deviation = ((threshold - value) / threshold) * 100;
        break;
      default:
        deviation = 0;
    }
    
    // Critical if more than 50% past threshold
    return deviation > 50 ? 'critical' : 'warning';
  }

  /**
   * Get recommended action based on severity
   */
  private getRecommendedAction(guardrail: Guardrail, value: number, severity: 'warning' | 'critical'): string {
    if (severity === 'critical') {
      return `URGENT: ${guardrail.metric} at ${value} (threshold: ${guardrail.threshold}). Consider immediate pause.`;
    }
    
    return `${guardrail.metric} approaching limit at ${value} (threshold: ${guardrail.threshold}). Monitor closely.`;
  }

  /**
   * Get entities affected by this guardrail
   */
  private async getAffectedEntities(userId: string, guardrail: Guardrail): Promise<{
    campaigns?: string[];
    moves?: string[];
  }> {
    const affected: { campaigns?: string[]; moves?: string[] } = {};
    
    if (guardrail.spike_id) {
      const { data: spike } = await db.spikes.getById(guardrail.spike_id, userId);
      if (spike?.campaign_id) {
        affected.campaigns = [spike.campaign_id];
      }
      if (spike?.move_ids?.length) {
        affected.moves = spike.move_ids;
      }
    } else if (guardrail.campaign_id) {
      affected.campaigns = [guardrail.campaign_id];
      const { data: moves } = await db.moves.list(userId, { campaign_id: guardrail.campaign_id });
      if (moves?.length) {
        affected.moves = moves.map(m => m.id);
      }
    }
    
    return affected;
  }

  /**
   * Execute pause action
   */
  private async executePause(
    userId: string,
    guardrail: Guardrail,
    evaluation: GuardrailEvaluation
  ): Promise<boolean> {
    let paused = false;
    
    // Pause spike if applicable
    if (guardrail.spike_id) {
      await db.spikes.updateStatus(guardrail.spike_id, userId, 'paused');
      paused = true;
    }
    
    // Pause campaign if applicable
    if (guardrail.campaign_id) {
      await db.campaigns.updateStatus(guardrail.campaign_id, userId, 'paused');
      paused = true;
    }
    
    // Pause affected moves
    if (evaluation.affected_entities?.moves) {
      for (const moveId of evaluation.affected_entities.moves) {
        await db.moves.updateStatus(moveId, userId, 'paused');
      }
      paused = true;
    }
    
    return paused;
  }

  /**
   * Override a triggered guardrail
   */
  async overrideGuardrail(
    userId: string,
    guardrailId: string,
    reason: string
  ): Promise<boolean> {
    // Log override event
    await db.guardrails.logEvent(userId, {
      guardrail_id: guardrailId,
      user_id: userId,
      event_type: 'overridden',
      override_reason: reason,
      overridden_by: userId,
      affected_entities: {}
    });
    
    // Temporarily deactivate the guardrail
    await db.guardrails.update(guardrailId, userId, {
      is_triggered: false
    });
    
    return true;
  }

  /**
   * Get guardrail history
   */
  async getGuardrailHistory(
    userId: string,
    guardrailId: string
  ): Promise<GuardrailEvent[]> {
    const { data: events } = await db.guardrails.getEvents(guardrailId, userId);
    return events || [];
  }

  /**
   * Create default guardrails for a spike
   */
  async createDefaultGuardrails(
    userId: string,
    spikeId: string,
    targets: { cac_ceiling?: number; max_payback_months?: number }
  ): Promise<Guardrail[]> {
    const guardrails = [];
    
    // CAC guardrail
    if (targets.cac_ceiling) {
      const { data: cacGuardrail } = await db.guardrails.create(userId, {
        spike_id: spikeId,
        name: 'CAC Ceiling',
        description: 'Pause if CAC exceeds ceiling',
        metric: 'cac',
        operator: 'greater_than',
        threshold: targets.cac_ceiling,
        action: 'pause_and_alert'
      });
      if (cacGuardrail) guardrails.push(cacGuardrail);
    }
    
    // Payback guardrail
    if (targets.max_payback_months) {
      const { data: paybackGuardrail } = await db.guardrails.create(userId, {
        spike_id: spikeId,
        name: 'Payback Period',
        description: 'Alert if payback exceeds target',
        metric: 'payback_months',
        operator: 'greater_than',
        threshold: targets.max_payback_months,
        action: 'alert_only'
      });
      if (paybackGuardrail) guardrails.push(paybackGuardrail);
    }
    
    // Conversion rate guardrail (default)
    const { data: conversionGuardrail } = await db.guardrails.create(userId, {
      spike_id: spikeId,
      name: 'Demo Conversion Floor',
      description: 'Alert if demo conversion drops significantly',
      metric: 'demo_conversion_rate',
      operator: 'less_than',
      threshold: 10,
      action: 'alert_only'
    });
    if (conversionGuardrail) guardrails.push(conversionGuardrail);
    
    return guardrails;
  }

  /**
   * Get kill switch dashboard data
   */
  async getDashboard(userId: string): Promise<{
    active_guardrails: number;
    triggered_guardrails: number;
    critical_alerts: number;
    recent_events: GuardrailEvent[];
  }> {
    const { data: guardrails } = await db.guardrails.list(userId, { is_active: true });
    
    const activeCount = guardrails?.length || 0;
    const triggeredCount = guardrails?.filter(g => g.is_triggered).length || 0;
    
    // Get recent events
    let recentEvents: GuardrailEvent[] = [];
    for (const guardrail of (guardrails || []).slice(0, 5)) {
      const { data: events } = await db.guardrails.getEvents(guardrail.id, userId);
      if (events?.length) {
        recentEvents = [...recentEvents, ...events.slice(0, 2)];
      }
    }
    
    // Sort by date and take top 10
    recentEvents = recentEvents
      .sort((a, b) => new Date(b.occurred_at).getTime() - new Date(a.occurred_at).getTime())
      .slice(0, 10);
    
    const criticalCount = guardrails?.filter(g => 
      g.is_triggered && g.action === 'auto_pause'
    ).length || 0;
    
    return {
      active_guardrails: activeCount,
      triggered_guardrails: triggeredCount,
      critical_alerts: criticalCount,
      recent_events: recentEvents
    };
  }
}

export const killSwitchService = new KillSwitchService();

