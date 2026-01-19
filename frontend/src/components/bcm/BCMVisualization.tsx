"use client";

import { useMemo } from "react";
import { BarChart3, PieChart, TrendingUp, Users, Target, MessageSquare, Building } from "lucide-react";
import { useBCMStore } from "@/stores/bcmStore";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";

export function BCMVisualization() {
  const { bcm } = useBCMStore();

  if (!bcm) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <BlueprintCard className="p-8 text-center">
          <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-[var(--surface)] border border-[var(--border)] flex items-center justify-center">
            <BarChart3 size={24} className="text-[var(--muted)]" />
          </div>
          <h2 className="font-serif text-2xl text-[var(--ink)] mb-4">No Business Context to Visualize</h2>
          <p className="text-[var(--muted)]">
            Complete onboarding to generate your Business Context Model for insights and analytics.
          </p>
        </BlueprintCard>
      </div>
    );
  }

  // Calculate analytics
  const analytics = useMemo(() => {
    return {
      icpCount: bcm.icps.length,
      competitorCount: bcm.competitive.competitors.length,
      valuePropCount: bcm.messaging.value_props.length,
      brandVoiceTraits: bcm.messaging.brand_voice.tone.length,
      completeness: calculateCompleteness(bcm),
      strengths: identifyStrengths(bcm),
      gaps: identifyGaps(bcm)
    };
  }, [bcm]);

  function calculateCompleteness(bcm: any): number {
    let score = 0;
    let total = 0;

    // Foundation (30%)
    if (bcm.foundation.company) { score += 1; }
    if (bcm.foundation.mission) { score += 1; }
    if (bcm.foundation.value_prop) { score += 1; }
    total += 3;

    // ICPs (25%)
    if (bcm.icps.length > 0) { score += 1; }
    if (bcm.icps.every((icp: any) => icp.name && icp.demographics)) { score += 1; }
    total += 2;

    // Competitive (20%)
    if (bcm.competitive.competitors.length > 0) { score += 1; }
    if (bcm.competitive.differentiation) { score += 1; }
    total += 2;

    // Messaging (25%)
    if (bcm.messaging.one_liner) { score += 1; }
    if (bcm.messaging.value_props.length > 0) { score += 1; }
    if (bcm.messaging.brand_voice.tone.length > 0) { score += 1; }
    total += 3;

    return Math.round((score / total) * 100);
  }

  function identifyStrengths(bcm: any): string[] {
    const strengths = [];
    
    if (bcm.foundation.mission && bcm.foundation.mission.length > 50) {
      strengths.push('Clear mission statement');
    }
    
    if (bcm.icps.length >= 2) {
      strengths.push('Multiple well-defined ICPs');
    }
    
    if (bcm.messaging.value_props.length >= 3) {
      strengths.push('Comprehensive value propositions');
    }
    
    if (bcm.competitive.differentiation && bcm.competitive.differentiation.length > 20) {
      strengths.push('Strong competitive differentiation');
    }
    
    return strengths;
  }

  function identifyGaps(bcm: any): string[] {
    const gaps = [];
    
    if (!bcm.foundation.company || bcm.foundation.company.length < 3) {
      gaps.push('Company name needs clarity');
    }
    
    if (bcm.icps.length === 0) {
      gaps.push('No ideal customer profiles defined');
    }
    
    if (!bcm.messaging.one_liner || bcm.messaging.one_liner.length < 10) {
      gaps.push('One-liner needs refinement');
    }
    
    if (bcm.competitive.competitors.length === 0) {
      gaps.push('Competitive analysis missing');
    }
    
    return gaps;
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="font-serif text-3xl text-[var(--ink)] mb-2">Business Context Analytics</h1>
        <p className="text-[var(--muted)]">
          Insights and visualization of your business context model
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <BlueprintCard showCorners padding="lg">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[var(--blueprint)]/10 rounded-full flex items-center justify-center">
              <Users size={18} className="text-[var(--blueprint)]" />
            </div>
            <div>
              <div className="text-2xl font-bold text-[var(--ink)]">{analytics.icpCount}</div>
              <div className="text-sm text-[var(--muted)]">ICP Profiles</div>
            </div>
          </div>
        </BlueprintCard>

        <BlueprintCard showCorners padding="lg">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[var(--success)]/10 rounded-full flex items-center justify-center">
              <Target size={18} className="text-[var(--success)]" />
            </div>
            <div>
              <div className="text-2xl font-bold text-[var(--ink)]">{analytics.competitorCount}</div>
              <div className="text-sm text-[var(--muted)]">Competitors</div>
            </div>
          </div>
        </BlueprintCard>

        <BlueprintCard showCorners padding="lg">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[var(--warning)]/10 rounded-full flex items-center justify-center">
              <MessageSquare size={18} className="text-[var(--warning)]" />
            </div>
            <div>
              <div className="text-2xl font-bold text-[var(--ink)]">{analytics.valuePropCount}</div>
              <div className="text-sm text-[var(--muted)]">Value Props</div>
            </div>
          </div>
        </BlueprintCard>

        <BlueprintCard showCorners padding="lg">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[var(--ink)]/10 rounded-full flex items-center justify-center">
              <Building size={18} className="text-[var(--ink)]" />
            </div>
            <div>
              <div className="text-2xl font-bold text-[var(--ink)]">{analytics.completeness}%</div>
              <div className="text-sm text-[var(--muted)]">Completeness</div>
            </div>
          </div>
        </BlueprintCard>
      </div>

      {/* Strengths and Gaps */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <BlueprintCard showCorners padding="lg">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp size={16} className="text-[var(--success)]" />
            <h3 className="font-serif text-lg text-[var(--ink)]">Strengths</h3>
          </div>
          <div className="space-y-2">
            {analytics.strengths.length > 0 ? (
              analytics.strengths.map((strength, index) => (
                <div key={index} className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-[var(--success)] rounded-full" />
                  <span className="text-sm text-[var(--ink)]">{strength}</span>
                </div>
              ))
            ) : (
              <p className="text-sm text-[var(--muted)] italic">No strengths identified yet</p>
            )}
          </div>
        </BlueprintCard>

        <BlueprintCard showCorners padding="lg">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 size={16} className="text-[var(--warning)]" />
            <h3 className="font-serif text-lg text-[var(--ink)]">Areas for Improvement</h3>
          </div>
          <div className="space-y-2">
            {analytics.gaps.length > 0 ? (
              analytics.gaps.map((gap, index) => (
                <div key={index} className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-[var(--warning)] rounded-full" />
                  <span className="text-sm text-[var(--ink)]">{gap}</span>
                </div>
              ))
            ) : (
              <p className="text-sm text-[var(--muted)] italic">No gaps identified - well done!</p>
            )}
          </div>
        </BlueprintCard>
      </div>

      {/* Brand Voice Visualization */}
      <BlueprintCard showCorners padding="lg">
        <h3 className="font-serif text-lg text-[var(--ink)] mb-4">Brand Voice Traits</h3>
        <div className="flex flex-wrap gap-2">
          {bcm.messaging.brand_voice.tone.map((trait: string, index: number) => (
            <BlueprintBadge key={index} variant="default" size="sm">
              {trait}
            </BlueprintBadge>
          ))}
        </div>
      </BlueprintCard>

      {/* ICP Overview */}
      <BlueprintCard showCorners padding="lg">
        <h3 className="font-serif text-lg text-[var(--ink)] mb-4">Target Audience Overview</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {bcm.icps.map((icp: any, index: number) => (
            <div key={icp.id || index} className="p-4 bg-[var(--surface)] border border-[var(--border)] rounded">
              <h4 className="font-medium text-[var(--ink)] mb-2">{icp.name}</h4>
              <p className="text-sm text-[var(--muted)]">
                {icp.demographics?.role || 'Role not specified'}
              </p>
              {icp.psychographics?.values && (
                <div className="mt-2">
                  <span className="text-xs text-[var(--muted)]">Values: </span>
                  <span className="text-xs text-[var(--ink)]">
                    {Array.isArray(icp.psychographics.values) 
                      ? icp.psychographics.values.slice(0, 3).join(', ')
                      : 'Not specified'
                    }
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      </BlueprintCard>
    </div>
  );
}
