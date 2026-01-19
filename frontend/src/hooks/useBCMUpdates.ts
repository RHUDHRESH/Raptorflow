import { useEffect } from 'react';
import { useBCMStore } from '@/stores/bcmStore';
import { useMovesStore } from '@/stores/movesStore';
import { useCampaignStore } from '@/stores/campaignStore';

interface BCMUpdateHookProps {
  enabled?: boolean;
}

/**
 * Hook to automatically update BCM based on completed tasks
 * This ensures the Business Context Model stays current with user activities
 */
export function useBCMUpdates({ enabled = true }: BCMUpdateHookProps = {}) {
  const { bcm, updateBCM } = useBCMStore();
  const { moves } = useMovesStore();
  const { campaigns } = useCampaignStore();

  useEffect(() => {
    if (!enabled || !bcm) return;

    // Analyze completed moves and campaigns for insights
    const completedMoves = moves.filter(move => move.status === 'completed');
    const completedCampaigns = campaigns.filter(campaign => campaign.status === 'Completed');

    if (completedMoves.length === 0 && completedCampaigns.length === 0) return;

    // Extract insights from completed activities
    const insights = extractInsights(completedMoves, completedCampaigns);
    
    // Update BCM with new insights if significant
    if (insights.hasUpdates) {
      updateBCM(insights.updates);
    }
  }, [moves, campaigns, enabled, bcm, updateBCM]);

  return { isUpdating: false };
}

function extractInsights(completedMoves: any[], completedCampaigns: any[]) {
  const updates: any = {};
  let hasUpdates = false;

  // Analyze successful move categories
  if (completedMoves.length > 0) {
    const successfulCategories = completedMoves.reduce((acc: Record<string, number>, move) => {
      acc[move.category] = (acc[move.category] || 0) + 1;
      return acc;
    }, {});

    // Find most successful category
    const topCategory = Object.entries(successfulCategories)
      .sort(([,a], [,b]) => (b as number) - (a as number))[0];

    if (topCategory) {
      updates.mostSuccessfulMoveType = topCategory[0];
      hasUpdates = true;
    }
  }

  // Analyze campaign effectiveness
  if (completedCampaigns.length > 0) {
    const campaignObjectives = completedCampaigns.map(c => c.goal || c.objective);
    
    // Look for patterns in successful campaigns
    if (campaignObjectives.length > 0) {
      updates.successfulCampaignPatterns = campaignObjectives;
      hasUpdates = true;
    }
  }

  // Suggest messaging improvements based on performance
  const allCompletedActivities = [...completedMoves, ...completedCampaigns];
  if (allCompletedActivities.length >= 3) {
    // This could be enhanced with actual performance metrics
    updates.messagingInsights = {
      suggestedTone: 'Confident and results-oriented',
      recommendedFocus: 'Emphasize measurable outcomes'
    };
    hasUpdates = true;
  }

  return {
    hasUpdates,
    updates: {
      ...updates,
      meta: {
        lastActivityUpdate: new Date().toISOString(),
        activitiesAnalyzed: allCompletedActivities.length
      }
    }
  };
}

/**
 * Hook to get BCM-driven recommendations for moves and campaigns
 */
export function useBCMRecommendations() {
  const { bcm } = useBCMStore();

  const getMoveRecommendations = () => {
    if (!bcm) return [];

    const recommendations = [];
    
    // Based on ICPs, suggest relevant move types
    bcm.icps.forEach((icp: any) => {
      if (icp.demographics?.role?.includes('Founder')) {
        recommendations.push({
          type: 'content',
          reason: 'Founders respond well to thought leadership content',
          suggestedChannels: ['LinkedIn', 'Twitter']
        });
      }
      
      if (icp.demographics?.role?.includes('CTO')) {
        recommendations.push({
          type: 'technical',
          reason: 'Technical leaders value detailed implementation guides',
          suggestedChannels: ['GitHub', 'Technical Blogs']
        });
      }
    });

    // Based on competitive landscape
    if (bcm.competitive.competitors.length > 2) {
      recommendations.push({
        type: 'differentiation',
        reason: 'Crowded market - focus on clear differentiation',
        suggestedChannels: ['Direct Outreach', 'Case Studies']
      });
    }

    return recommendations;
  };

  const getCampaignRecommendations = () => {
    if (!bcm) return [];

    const recommendations = [];

    // Based on company mission
    if (bcm.foundation.mission?.includes('innovate')) {
      recommendations.push({
        objective: 'Innovation Showcase',
        duration: '90 Days',
        intensity: 'Sprint',
        reason: 'Innovation-focused missions benefit from longer showcase campaigns'
      });
    }

    // Based on value propositions
    if (bcm.messaging.value_props?.some((prop: string) => prop.includes('speed'))) {
      recommendations.push({
        objective: 'Rapid Results Campaign',
        duration: '30 Days',
        intensity: 'Sprint',
        reason: 'Speed-focused value props work well with short, intense campaigns'
      });
    }

    return recommendations;
  };

  return {
    getMoveRecommendations,
    getCampaignRecommendations
  };
}
