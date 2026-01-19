"use client";

import { useMemo } from "react";
import { FileText, TrendingUp, BarChart2, MousePointer2, Clock, Zap } from "lucide-react";
import { useMuseStore } from "@/stores/museStore";
import { BlueprintKPI, KPIGrid } from "@/components/ui/BlueprintKPI";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { format, subDays, isAfter, parseISO } from "date-fns";

export function MuseAnalytics() {
  const { assets } = useMuseStore();

  const analytics = useMemo(() => {
    const totalAssets = assets.length;
    const last7Days = assets.filter(a => isAfter(parseISO(a.createdAt), subDays(new Date(), 7))).length;
    
    // Type distribution
    const typeCount: Record<string, number> = {};
    assets.forEach(a => {
      typeCount[a.type] = (typeCount[a.type] || 0) + 1;
    });

    // Mock engagement data (in a real app this would come from an API)
    const totalEngagements = assets.length * 12; // Mock multiplier
    const avgEngagement = totalAssets > 0 ? (totalEngagements / totalAssets).toFixed(1) : "0";

    return {
      totalAssets,
      weeklyVelocity: last7Days,
      avgEngagement,
      typeCount,
      totalEngagements
    };
  }, [assets]);

  return (
    <div className="space-y-8">
      {/* Top Metrics */}
      <KPIGrid columns={4}>
        <BlueprintKPI
          label="Total Assets"
          value={analytics.totalAssets}
          code="ANL-TOT"
          figure="FIG. 01"
          trend="up"
          trendValue="+12%"
        />
        <BlueprintKPI
          label="Weekly Velocity"
          value={analytics.weeklyVelocity}
          code="ANL-VEL"
          figure="FIG. 02"
          unit="items/wk"
        />
        <BlueprintKPI
          label="Avg Engagement"
          value={analytics.avgEngagement}
          code="ANL-ENG"
          figure="FIG. 03"
          unit="pts"
          trend="up"
          trendValue="8.4%"
        />
        <BlueprintKPI
          label="Total Impact"
          value={analytics.totalEngagements}
          code="ANL-IMP"
          figure="FIG. 04"
          unit="points"
        />
      </KPIGrid>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Content Mix */}
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <span className="font-technical text-[var(--blueprint)]">01</span>
            <div className="h-px flex-1 bg-[var(--border)]" />
            <span className="font-technical text-[var(--ink-muted)]">CONTENT MIX</span>
          </div>
          
          <BlueprintCard className="p-6">
            <div className="space-y-5">
              {Object.entries(analytics.typeCount).length > 0 ? (
                Object.entries(analytics.typeCount)
                  .sort(([, a], [, b]) => b - a)
                  .map(([type, count]) => {
                    const percent = Math.round((count / analytics.totalAssets) * 100);
                    return (
                      <div key={type} className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="font-medium text-[var(--ink)]">{type}</span>
                          <span className="text-[var(--ink-muted)]">{count} ({percent}%)</span>
                        </div>
                        <div className="h-2 bg-[var(--surface)] rounded-full overflow-hidden">
                          <div
                            className="h-full bg-[var(--blueprint)] rounded-full transition-all duration-1000"
                            style={{ width: `${percent}%` }}
                          />
                        </div>
                      </div>
                    );
                  })
              ) : (
                <div className="text-center py-10 text-[var(--ink-ghost)]">
                  <BarChart2 className="w-8 h-8 mx-auto mb-2 opacity-20" />
                  <p>No content data available</p>
                </div>
              )}
            </div>
          </BlueprintCard>
        </div>

        {/* Top Performing */}
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <span className="font-technical text-[var(--blueprint)]">02</span>
            <div className="h-px flex-1 bg-[var(--border)]" />
            <span className="font-technical text-[var(--ink-muted)]">PERFORMANCE LEDGER</span>
          </div>

          <BlueprintCard className="p-0 overflow-hidden">
            <div className="divide-y divide-[var(--structure-subtle)]">
              {assets.slice(0, 5).map((asset, i) => (
                <div key={asset.id} className="p-4 flex items-center justify-between hover:bg-[var(--surface)] transition-colors">
                  <div className="flex items-center gap-3">
                    <span className="font-technical text-[10px] text-[var(--ink-ghost)]">
                      {(i + 1).toString().padStart(2, '0')}
                    </span>
                    <div>
                      <p className="text-sm font-medium text-[var(--ink)] line-clamp-1">{asset.title}</p>
                      <p className="text-[10px] text-[var(--ink-ghost)] uppercase tracking-wider">{asset.type}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center gap-1 text-[var(--success)]">
                      <TrendingUp size={12} />
                      <span className="text-xs font-bold">{(Math.random() * 5 + 8).toFixed(1)}</span>
                    </div>
                    <p className="text-[9px] text-[var(--ink-ghost)] uppercase">Score</p>
                  </div>
                </div>
              ))}
              {assets.length === 0 && (
                <div className="p-10 text-center text-[var(--ink-ghost)]">
                  <Zap className="w-8 h-8 mx-auto mb-2 opacity-20" />
                  <p>Generate content to see performance</p>
                </div>
              )}
            </div>
          </BlueprintCard>
        </div>
      </div>
    </div>
  );
}
