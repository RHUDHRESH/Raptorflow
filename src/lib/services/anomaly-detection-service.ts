/**
 * Anomaly Detection Service
 * AI-powered detection of issues in moves
 */

import { moveService } from './move-service';
import { icpService } from './icp-service';
import { analyticsService } from './analytics-service';

export interface AnomalyDetection {
  type: 'Tone_Clash' | 'Fatigue' | 'Drift' | 'Rule_Violation' | 'Capacity_Overload';
  severity: number; // 1-5
  description: string;
  recommendation?: string;
  affectedMoveId?: string;
}

export const anomalyDetectionService = {
  /**
   * Detect tone clash between content and ICP
   */
  async detectToneClash(content: string, icpId: string): Promise<AnomalyDetection | null> {
    try {
      const icp = await icpService.getById(icpId);
      if (!icp) return null;

      const targetTone = icp.communication?.tone || '';
      if (!targetTone) return null;

      // Simple heuristic-based detection
      // In production, call Vertex AI for sophisticated analysis
      const toneKeywords = {
        'professional': ['expertise', 'analysis', 'methodology', 'framework'],
        'casual': ['hey', 'awesome', 'cool', 'stuff'],
        'formal': ['therefore', 'furthermore', 'accordingly', 'pursuant'],
        'friendly': ['we', 'together', 'help', 'support'],
      };

      const contentLower = content.toLowerCase();
      const targetKeywords = toneKeywords[targetTone.toLowerCase()] || [];
      const matches = targetKeywords.filter(kw => contentLower.includes(kw)).length;
      
      // If content doesn't match target tone
      if (matches === 0 && content.length > 100) {
        return {
          type: 'Tone_Clash',
          severity: 3,
          description: `Content tone may not align with ${icp.name}'s preferred ${targetTone} communication style.`,
          recommendation: `Review content to match ${targetTone} tone. Use keywords like: ${targetKeywords.join(', ')}.`,
        };
      }

      return null;
    } catch (error) {
      console.error('Error detecting tone clash:', error);
      return null;
    }
  },

  /**
   * Detect content fatigue (repetition)
   */
  async detectFatigue(moveId: string): Promise<AnomalyDetection | null> {
    try {
      const metrics = await analyticsService.getMoveMetrics(moveId);
      if (metrics.length < 7) return null; // Need at least a week of data

      // Check for declining engagement
      const recentMetrics = metrics.slice(-7);
      const engagementRates = recentMetrics
        .map(m => m.engagement_rate || 0)
        .filter(r => r > 0);

      if (engagementRates.length < 3) return null;

      // Check if engagement is declining
      const avgFirst = engagementRates.slice(0, 3).reduce((a, b) => a + b, 0) / 3;
      const avgLast = engagementRates.slice(-3).reduce((a, b) => a + b, 0) / 3;
      const decline = ((avgFirst - avgLast) / avgFirst) * 100;

      if (decline > 30) {
        return {
          type: 'Fatigue',
          severity: 4,
          description: `Audience engagement has declined ${Math.round(decline)}% over the past week.`,
          recommendation: 'Switch up content format, topics, or channels to refresh audience interest.',
          affectedMoveId: moveId,
        };
      }

      return null;
    } catch (error) {
      console.error('Error detecting fatigue:', error);
      return null;
    }
  },

  /**
   * Detect performance drift
   */
  async detectDrift(moveId: string): Promise<AnomalyDetection | null> {
    try {
      const metrics = await analyticsService.getMoveMetrics(moveId);
      if (metrics.length < 10) return null;

      // Calculate baseline from first 5 days
      const baseline = metrics.slice(0, 5);
      const recent = metrics.slice(-5);

      const baselineAvg = baseline.reduce((sum, m) => 
        sum + (m.conversion_rate || 0), 0
      ) / baseline.length;

      const recentAvg = recent.reduce((sum, m) => 
        sum + (m.conversion_rate || 0), 0
      ) / recent.length;

      if (baselineAvg === 0) return null;

      const driftPercentage = Math.abs(((recentAvg - baselineAvg) / baselineAvg) * 100);

      if (driftPercentage > 25) {
        const isNegative = recentAvg < baselineAvg;
        return {
          type: 'Drift',
          severity: isNegative ? 4 : 2,
          description: `Conversion rate has ${isNegative ? 'dropped' : 'improved'} ${Math.round(driftPercentage)}% from baseline.`,
          recommendation: isNegative 
            ? 'Investigate recent changes. Review targeting, messaging, or channel performance.'
            : 'Positive drift detected! Document what\'s working to replicate success.',
          affectedMoveId: moveId,
        };
      }

      return null;
    } catch (error) {
      console.error('Error detecting drift:', error);
      return null;
    }
  },

  /**
   * Detect capacity overload
   */
  async detectCapacityOverload(workspaceId: string): Promise<AnomalyDetection | null> {
    try {
      const moves = await moveService.getMoves(workspaceId);
      const activeMoves = moves.filter(m => 
        m.status.includes('OODA') && m.status !== 'Complete' && m.status !== 'Killed'
      );

      // Simple rule: more than 8 active moves is overload
      if (activeMoves.length > 8) {
        return {
          type: 'Capacity_Overload',
          severity: 5,
          description: `You have ${activeMoves.length} active moves. This may lead to scattered focus and poor execution.`,
          recommendation: 'Review active moves. Complete, kill, or pause underperforming ones to improve focus.',
        };
      }

      // Check for moves with red health
      const unhealthyMoves = activeMoves.filter(m => m.health_status === 'red').length;
      if (unhealthyMoves >= 3) {
        return {
          type: 'Capacity_Overload',
          severity: 4,
          description: `${unhealthyMoves} moves have red health status. Team may be overextended.`,
          recommendation: 'Reduce active move count or allocate more resources to struggling moves.',
        };
      }

      return null;
    } catch (error) {
      console.error('Error detecting capacity overload:', error);
      return null;
    }
  },

  /**
   * Detect rule violations (OODA stuck, missing data, etc.)
   */
  async detectRuleViolations(moveId: string): Promise<AnomalyDetection[]> {
    try {
      const move = await moveService.getMove(moveId);
      if (!move) return [];

      const violations: AnomalyDetection[] = [];

      // Check if move is stuck in a phase too long
      const daysInPhase = this.getDaysInCurrentPhase(move);
      if (daysInPhase > 7 && move.status.includes('OODA')) {
        violations.push({
          type: 'Rule_Violation',
          severity: 3,
          description: `Move has been in ${move.status.replace('OODA_', '')} phase for ${daysInPhase} days.`,
          recommendation: 'Progress to next OODA phase or reassess move viability.',
          affectedMoveId: moveId,
        });
      }

      // Check for missing OODA configuration
      const oodaConfig = move.ooda_config || {};
      if (!oodaConfig.observe_sources || oodaConfig.observe_sources.length === 0) {
        violations.push({
          type: 'Rule_Violation',
          severity: 2,
          description: 'Move is missing observation data sources.',
          recommendation: 'Configure data sources in OODA configuration to track performance.',
          affectedMoveId: moveId,
        });
      }

      // Check for overdue moves
      if (move.end_date) {
        const endDate = new Date(move.end_date);
        const now = new Date();
        if (endDate < now && move.status !== 'Complete' && move.status !== 'Killed') {
          const daysOverdue = Math.floor((now.getTime() - endDate.getTime()) / (1000 * 60 * 60 * 24));
          violations.push({
            type: 'Rule_Violation',
            severity: daysOverdue > 7 ? 4 : 3,
            description: `Move is ${daysOverdue} days overdue.`,
            recommendation: 'Complete the move, extend the deadline, or kill it if no longer viable.',
            affectedMoveId: moveId,
          });
        }
      }

      return violations;
    } catch (error) {
      console.error('Error detecting rule violations:', error);
      return [];
    }
  },

  /**
   * Run all anomaly checks for a move
   */
  async detectAllAnomalies(moveId: string, icpId?: string): Promise<AnomalyDetection[]> {
    const anomalies: AnomalyDetection[] = [];

    try {
      // Fatigue detection
      const fatigueAnomaly = await this.detectFatigue(moveId);
      if (fatigueAnomaly) anomalies.push(fatigueAnomaly);

      // Drift detection
      const driftAnomaly = await this.detectDrift(moveId);
      if (driftAnomaly) anomalies.push(driftAnomaly);

      // Rule violations
      const violations = await this.detectRuleViolations(moveId);
      anomalies.push(...violations);

      // Tone clash (if content provided)
      // This would need actual content - placeholder for now
      
    } catch (error) {
      console.error('Error detecting anomalies:', error);
    }

    return anomalies;
  },

  /**
   * Run workspace-level checks
   */
  async detectWorkspaceAnomalies(workspaceId: string): Promise<AnomalyDetection[]> {
    const anomalies: AnomalyDetection[] = [];

    try {
      // Capacity overload
      const capacityAnomaly = await this.detectCapacityOverload(workspaceId);
      if (capacityAnomaly) anomalies.push(capacityAnomaly);

      // Check all moves for individual anomalies
      const moves = await moveService.getMoves(workspaceId);
      for (const move of moves.slice(0, 10)) { // Limit to avoid performance issues
        const moveAnomalies = await this.detectAllAnomalies(move.id, move.primary_icp_id);
        anomalies.push(...moveAnomalies);
      }
    } catch (error) {
      console.error('Error detecting workspace anomalies:', error);
    }

    return anomalies;
  },

  /**
   * Store detected anomaly in database
   */
  async logAnomaly(anomaly: AnomalyDetection): Promise<void> {
    if (!anomaly.affectedMoveId) return;

    try {
      await moveService.createAnomaly({
        move_id: anomaly.affectedMoveId,
        type: anomaly.type,
        severity: anomaly.severity,
        description: anomaly.description,
        status: 'Open',
      });
    } catch (error) {
      console.error('Error logging anomaly:', error);
    }
  },

  // Helper functions
  getDaysInCurrentPhase(move: any): number {
    // Simplified calculation - in production, track phase change timestamps
    const now = new Date();
    const updated = move.updated_at ? new Date(move.updated_at) : now;
    return Math.floor((now.getTime() - updated.getTime()) / (1000 * 60 * 60 * 24));
  },
};



