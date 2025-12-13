/**
 * Context Bridge
 *
 * Enables state sharing between V1 and V2 systems for unified orchestration
 */

import { redisMemory } from '../services/redisMemory';

// =====================================================
// CONTEXT BRIDGE
// =====================================================

export class ContextBridge {
  private readonly CONTEXT_PREFIX = 'context_bridge';
  private readonly TTL_SECONDS = 3600; // 1 hour

  /**
   * Share context from one system to another
   */
  async shareContext(fromSystem: 'v1' | 'v2', context: any): Promise<void> {
    const key = `${this.CONTEXT_PREFIX}:${fromSystem}:shared`;

    try {
      await redisMemory.store(key, {
        fromSystem,
        context,
        sharedAt: new Date().toISOString(),
        ttl: this.TTL_SECONDS
      }, this.TTL_SECONDS);

      console.log(`✅ Context shared from ${fromSystem}:`, Object.keys(context));
    } catch (error) {
      console.error(`❌ Failed to share context from ${fromSystem}:`, error);
      throw error;
    }
  }

  /**
   * Get shared context for a target system
   */
  async getSharedContext(forSystem: 'v1' | 'v2'): Promise<any> {
    const sourceSystem = forSystem === 'v1' ? 'v2' : 'v1';
    const key = `${this.CONTEXT_PREFIX}:${sourceSystem}:shared`;

    try {
      const sharedData = await redisMemory.retrieve(key);

      if (sharedData) {
        console.log(`📥 Context retrieved for ${forSystem} from ${sourceSystem}`);
        return this.adaptContext(sharedData.context, forSystem);
      }

      return {};
    } catch (error) {
      console.error(`❌ Failed to retrieve shared context for ${forSystem}:`, error);
      return {};
    }
  }

  /**
   * Synchronize state between systems
   */
  async synchronizeState(): Promise<void> {
    try {
      // Get current state from both systems
      const v1State = await this.getSystemState('v1');
      const v2State = await this.getSystemState('v2');

      // Create unified state
      const unifiedState = {
        v1: v1State,
        v2: v2State,
        synchronizedAt: new Date().toISOString(),
        version: '1.0'
      };

      // Store unified state
      const key = `${this.CONTEXT_PREFIX}:unified_state`;
      await redisMemory.store(key, unifiedState, this.TTL_SECONDS);

      console.log('🔄 Systems state synchronized');
    } catch (error) {
      console.error('❌ Failed to synchronize system state:', error);
      throw error;
    }
  }

  /**
   * Store execution context for cross-system reference
   */
  async storeExecutionContext(executionId: string, context: any): Promise<void> {
    const key = `${this.CONTEXT_PREFIX}:execution:${executionId}`;

    try {
      await redisMemory.store(key, {
        executionId,
        context,
        storedAt: new Date().toISOString()
      }, this.TTL_SECONDS * 24); // Keep execution context longer

      console.log(`💾 Execution context stored: ${executionId}`);
    } catch (error) {
      console.error(`❌ Failed to store execution context ${executionId}:`, error);
      throw error;
    }
  }

  /**
   * Retrieve execution context
   */
  async getExecutionContext(executionId: string): Promise<any> {
    const key = `${this.CONTEXT_PREFIX}:execution:${executionId}`;

    try {
      const context = await redisMemory.retrieve(key);
      return context || {};
    } catch (error) {
      console.error(`❌ Failed to retrieve execution context ${executionId}:`, error);
      return {};
    }
  }

  /**
   * Bridge V1 insights to V2 campaign context
   */
  adaptV1ToV2Context(v1Results: any): any {
    const adapted = {
      business_intelligence: {
        icp: v1Results.icp || {},
        market_analysis: v1Results.market_analysis || {},
        competitor_insights: v1Results.competitor_insights || {},
        customer_segments: v1Results.customer_segments || []
      },
      strategic_context: {
        goals: v1Results.goals || [],
        challenges: v1Results.challenges || [],
        opportunities: v1Results.opportunities || [],
        positioning: v1Results.positioning || {}
      },
      derived_insights: this.deriveV2Insights(v1Results)
    };

    return adapted;
  }

  /**
   * Bridge V2 results to V1 strategic context
   */
  adaptV2ToV1Context(v2Results: any): any {
    const adapted = {
      marketing_execution: {
        campaigns: v2Results.campaigns || [],
        content_assets: v2Results.content_assets || [],
        automation_workflows: v2Results.automation_workflows || []
      },
      performance_metrics: {
        engagement: v2Results.engagement_metrics || {},
        conversion: v2Results.conversion_metrics || {},
        roi: v2Results.roi_analysis || {}
      },
      optimization_opportunities: v2Results.optimization_recommendations || []
    };

    return adapted;
  }

  // =====================================================
  // PRIVATE METHODS
  // =====================================================

  /**
   * Adapt context for target system
   */
  private adaptContext(context: any, forSystem: 'v1' | 'v2'): any {
    if (forSystem === 'v2') {
      return this.adaptV1ToV2Context(context);
    } else {
      return this.adaptV2ToV1Context(context);
    }
  }

  /**
   * Get current state of a system
   */
  private async getSystemState(system: 'v1' | 'v2'): Promise<any> {
    try {
      // This would integrate with system monitoring
      // For now, return basic state
      return {
        status: 'active',
        active_executions: 0,
        last_updated: new Date().toISOString(),
        system
      };
    } catch (error) {
      console.error(`Failed to get ${system} system state:`, error);
      return { status: 'unknown', system };
    }
  }

  /**
   * Derive V2-relevant insights from V1 results
   */
  private deriveV2Insights(v1Results: any): any {
    const insights = {
      target_audience: this.extractAudienceInsights(v1Results),
      messaging_angles: this.extractMessagingInsights(v1Results),
      channel_priorities: this.extractChannelInsights(v1Results),
      content_themes: this.extractContentInsights(v1Results),
      competitive_advantages: this.extractCompetitiveInsights(v1Results)
    };

    return insights;
  }

  /**
   * Extract audience insights for V2 campaigns
   */
  private extractAudienceInsights(v1Results: any): any {
    const icp = v1Results.icp || {};
    const cohorts = v1Results.cohorts || [];

    return {
      demographics: icp.demographics || {},
      psychographics: icp.psychographics || {},
      pain_points: icp.pain_points || [],
      aspirations: icp.aspirations || [],
      segments: cohorts.map((cohort: any) => ({
        name: cohort.name,
        size: cohort.size,
        characteristics: cohort.characteristics
      }))
    };
  }

  /**
   * Extract messaging insights for V2 content
   */
  private extractMessagingInsights(v1Results: any): string[] {
    const positioning = v1Results.positioning || {};
    const jtbd = v1Results.jtbd_analysis || {};

    const angles = [];

    if (positioning.unique_value_proposition) {
      angles.push(positioning.unique_value_proposition);
    }

    if (jtbd.jobs_to_be_done) {
      angles.push(...jtbd.jobs_to_be_done);
    }

    return angles.slice(0, 5); // Limit to top 5
  }

  /**
   * Extract channel insights for V2 distribution
   */
  private extractChannelInsights(v1Results: any): any {
    const market = v1Results.market_analysis || {};

    return {
      recommended_channels: market.recommended_channels || [],
      audience_preferences: market.audience_preferences || {},
      competitive_channels: market.competitive_channels || [],
      budget_allocation: market.channel_budget_suggestions || {}
    };
  }

  /**
   * Extract content insights for V2 creative
   */
  private extractContentInsights(v1Results: any): string[] {
    const trends = v1Results.trends || [];
    const competitor_content = v1Results.competitor_content_analysis || {};

    const themes = [
      ...trends.map((t: any) => t.theme),
      ...Object.keys(competitor_content)
    ];

    return [...new Set(themes)].slice(0, 10);
  }

  /**
   * Extract competitive insights for V2 strategy
   */
  private extractCompetitiveInsights(v1Results: any): any {
    const competitors = v1Results.competitors || [];

    return {
      unique_selling_points: v1Results.unique_selling_points || [],
      competitive_advantages: competitors.flatMap((c: any) => c.weaknesses || []),
      market_gaps: v1Results.market_gaps || [],
      differentiation_opportunities: v1Results.differentiation_opportunities || []
    };
  }
}

// Singleton instance
export const contextBridge = new ContextBridge();


