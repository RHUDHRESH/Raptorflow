"use client";

import { useState, useEffect } from 'react';
import {
  BarChart3,
  TrendingUp,
  Users,
  DollarSign,
  Target,
  Calendar,
  Download,
  Filter,
  RefreshCw,
  Eye,
  ArrowUp,
  ArrowDown,
  Minus,
  MoreVertical,
  Zap,
  Mail,
  Share2,
  FileText,
  PieChart,
  Activity
} from 'lucide-react';
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { BlueprintButton } from '@/components/ui/BlueprintButton';
import { BlueprintBadge } from '@/components/ui/BlueprintBadge';
import { useEnhancedCampaignStore } from '@/stores/enhancedCampaignStore';
import { Campaign } from '@/types/campaign';
import { cn } from '@/lib/utils';
import { format, subDays, startOfDay, endOfDay } from 'date-fns';

interface CampaignAnalyticsProps {
  campaignId: string;
}

interface MetricCard {
  title: string;
  value: string | number;
  change: number;
  changeType: 'increase' | 'decrease' | 'neutral';
  icon: React.ElementType;
  format?: 'number' | 'currency' | 'percentage';
}

interface ChartData {
  date: string;
  reach: number;
  engagement: number;
  conversions: number;
  revenue: number;
}

interface FunnelData {
  stage: string;
  count: number;
  rate: number;
  color: string;
}

interface ChannelData {
  name: string;
  value: number;
  color: string;
  change: number;
}

export function CampaignAnalytics({ campaignId }: CampaignAnalyticsProps) {
  const campaign = useEnhancedCampaignStore(state => state.campaigns[campaignId]);
  const refreshAnalytics = useEnhancedCampaignStore(state => state.refreshAnalytics);

  const [dateRange, setDateRange] = useState<'7d' | '30d' | '90d' | 'custom'>('30d');
  const [customDateRange, setCustomDateRange] = useState<{ start: Date; end: Date } | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedMetric, setSelectedMetric] = useState<'overview' | 'funnel' | 'channels' | 'trends'>('overview');

  if (!campaign) return null;

  // Mock data generation
  const generateChartData = (): ChartData[] => {
    const days = dateRange === '7d' ? 7 : dateRange === '30d' ? 30 : 90;
    const data: ChartData[] = [];

    for (let i = days - 1; i >= 0; i--) {
      const date = subDays(new Date(), i);
      data.push({
        date: format(date, 'MMM d'),
        reach: Math.floor(Math.random() * 1000) + 500,
        engagement: Math.floor(Math.random() * 200) + 50,
        conversions: Math.floor(Math.random() * 50) + 10,
        revenue: Math.floor(Math.random() * 5000) + 1000
      });
    }

    return data;
  };

  const [chartData, setChartData] = useState<ChartData[]>(generateChartData());

  // Mock funnel data
  const funnelData: FunnelData[] = [
    { stage: 'Awareness', count: 10000, rate: 100, color: 'bg-blue-500' },
    { stage: 'Interest', count: 5000, rate: 50, color: 'bg-purple-500' },
    { stage: 'Consideration', count: 2500, rate: 25, color: 'bg-pink-500' },
    { stage: 'Intent', count: 1000, rate: 10, color: 'bg-orange-500' },
    { stage: 'Conversion', count: 250, rate: 2.5, color: 'bg-green-500' }
  ];

  // Mock channel data
  const channelData: ChannelData[] = [
    { name: 'Email', value: 45, color: 'bg-blue-500', change: 12 },
    { name: 'Social Media', value: 30, color: 'bg-purple-500', change: -5 },
    { name: 'Content', value: 15, color: 'bg-green-500', change: 8 },
    { name: 'Paid Ads', value: 10, color: 'bg-orange-500', change: 15 }
  ];

  // Metrics cards
  const metrics: MetricCard[] = [
    {
      title: 'Total Reach',
      value: campaign.analytics?.overview?.totalReach ?? 0,
      change: 15.3,
      changeType: 'increase',
      icon: Users,
      format: 'number'
    },
    {
      title: 'Engagement',
      value: campaign.analytics?.overview?.totalEngagement ?? 0,
      change: 8.7,
      changeType: 'increase',
      icon: Activity,
      format: 'number'
    },
    {
      title: 'Conversions',
      value: campaign.analytics?.overview?.totalConversions ?? 0,
      change: -2.4,
      changeType: 'decrease',
      icon: Target,
      format: 'number'
    },
    {
      title: 'Revenue',
      value: campaign.analytics?.overview?.totalRevenue ?? 0,
      change: 23.1,
      changeType: 'increase',
      icon: DollarSign,
      format: 'currency'
    },
    {
      title: 'ROI',
      value: campaign.analytics?.overview?.roi ?? 0,
      change: 5.2,
      changeType: 'increase',
      icon: TrendingUp,
      format: 'percentage'
    },
    {
      title: 'Cost per Acquisition',
      value: campaign.analytics?.roi?.cac ?? 45,
      change: -8.3,
      changeType: 'increase', // Lower CPA is good
      icon: DollarSign,
      format: 'currency'
    }
  ];

  // Format value based on type
  const formatValue = (value: number, format?: string): string => {
    switch (format) {
      case 'currency':
        return `$${value.toLocaleString()}`;
      case 'percentage':
        return `${value}%`;
      case 'number':
      default:
        return value.toLocaleString();
    }
  };

  // Handle refresh
  const handleRefresh = async () => {
    setIsLoading(true);
    await refreshAnalytics(campaignId);
    setChartData(generateChartData());
    setIsLoading(false);
  };

  // Export data
  const handleExport = (format: 'csv' | 'pdf') => {
    console.log(`Exporting data as ${format}`);
    // Implementation would go here
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-[var(--structure-subtle)]">
        <div>
          <h1 className="text-2xl font-bold text-[var(--ink)]">Campaign Analytics</h1>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            {campaign.name} • Performance insights and metrics
          </p>
        </div>

        <div className="flex items-center gap-2">
          <BlueprintButton
            variant="secondary"
            size="sm"
            onClick={() => handleExport('csv')}
            className="flex items-center gap-2"
          >
            <Download size={16} />
            Export CSV
          </BlueprintButton>

          <BlueprintButton
            variant="secondary"
            size="sm"
            onClick={handleRefresh}
            disabled={isLoading}
            className="flex items-center gap-2"
          >
            <RefreshCw size={16} className={cn(isLoading && 'animate-spin')} />
            Refresh
          </BlueprintButton>
        </div>
      </div>

      {/* Date Range Selector */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--structure-subtle)]">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Calendar size={16} className="text-[var(--ink-ghost)]" />
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value as any)}
              className="px-3 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
              <option value="custom">Custom range</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <Filter size={16} className="text-[var(--ink-ghost)]" />
            <select className="px-3 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]">
              <option>All channels</option>
              <option>Email</option>
              <option>Social Media</option>
              <option>Content</option>
              <option>Paid Ads</option>
            </select>
          </div>
        </div>

        <div className="text-sm text-[var(--ink-muted)]">
          Last updated: {format(new Date(), 'MMM d, h:mm a')}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {/* Metrics Overview */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          {metrics.map((metric, index) => {
            const Icon = metric.icon;
            return (
              <BlueprintCard key={index} className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-[var(--ink-muted)] uppercase tracking-wide">
                    {metric.title}
                  </span>
                  <Icon size={16} className="text-[var(--ink-ghost)]" />
                </div>

                <div className="flex items-end justify-between">
                  <p className="text-2xl font-bold text-[var(--ink)]">
                    {formatValue(metric.value as number, metric.format)}
                  </p>

                  <div className={cn(
                    "flex items-center gap-1 text-xs",
                    metric.changeType === 'increase' ? "text-[var(--success)]" :
                      metric.changeType === 'decrease' ? "text-[var(--destructive)]" :
                        "text-[var(--ink-muted)]"
                  )}>
                    {metric.changeType === 'increase' && <ArrowUp size={12} />}
                    {metric.changeType === 'decrease' && <ArrowDown size={12} />}
                    {metric.changeType === 'neutral' && <Minus size={12} />}
                    {Math.abs(metric.change)}%
                  </div>
                </div>
              </BlueprintCard>
            );
          })}
        </div>

        {/* Metric Tabs */}
        <div className="flex items-center gap-6 mb-6 border-b border-[var(--structure-subtle)]">
          {[
            { id: 'overview', label: 'Overview', icon: BarChart3 },
            { id: 'funnel', label: 'Conversion Funnel', icon: Target },
            { id: 'channels', label: 'Channel Performance', icon: PieChart },
            { id: 'trends', label: 'Trends', icon: TrendingUp }
          ].map(tab => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setSelectedMetric(tab.id as any)}
                className={cn(
                  "flex items-center gap-2 py-3 px-1 text-sm font-medium border-b-2 transition-colors",
                  selectedMetric === tab.id
                    ? "text-[var(--ink)] border-[var(--ink)]"
                    : "text-[var(--ink-muted)] border-transparent hover:text-[var(--ink)]"
                )}
              >
                <Icon size={16} />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Metric Content */}
        {selectedMetric === 'overview' && (
          <div className="space-y-6">
            {/* Performance Chart */}
            <BlueprintCard className="p-6">
              <h3 className="text-sm font-semibold text-[var(--ink)] mb-4">Performance Overview</h3>
              <div className="h-80 bg-[var(--surface)] rounded-[var(--radius)] flex items-center justify-center">
                <p className="text-sm text-[var(--ink-muted)]">Line chart showing reach, engagement, conversions, and revenue over time</p>
              </div>
            </BlueprintCard>

            {/* Top Performing Moves */}
            <BlueprintCard className="p-6">
              <h3 className="text-sm font-semibold text-[var(--ink)] mb-4">Top Performing Moves</h3>
              <div className="space-y-3">
                {[
                  { name: 'Welcome Email Series', conversions: 450, revenue: 22500, roi: 450 },
                  { name: 'Social Media Campaign', conversions: 320, revenue: 16000, roi: 320 },
                  { name: 'Content Marketing', conversions: 280, revenue: 14000, roi: 280 },
                  { name: 'Paid Ads', conversions: 200, revenue: 10000, roi: 200 }
                ].map((move, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-[var(--surface)] rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-[var(--blueprint-light)]/10 flex items-center justify-center">
                        <Zap size={16} className="text-[var(--blueprint)]" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-[var(--ink)]">{move.name}</p>
                        <p className="text-xs text-[var(--ink-muted)]">
                          {move.conversions} conversions • ${move.revenue.toLocaleString()} revenue
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-[var(--success)]">{move.roi}% ROI</p>
                    </div>
                  </div>
                ))}
              </div>
            </BlueprintCard>
          </div>
        )}

        {selectedMetric === 'funnel' && (
          <div className="grid grid-cols-2 gap-6">
            {/* Funnel Visualization */}
            <BlueprintCard className="p-6">
              <h3 className="text-sm font-semibold text-[var(--ink)] mb-4">Conversion Funnel</h3>
              <div className="space-y-2">
                {funnelData.map((stage, index) => (
                  <div key={index} className="relative">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-[var(--ink)]">{stage.stage}</span>
                      <span className="text-sm text-[var(--ink-muted)]">
                        {stage.count.toLocaleString()} ({stage.rate}%)
                      </span>
                    </div>
                    <div className="w-full bg-[var(--surface)] rounded-full h-8 overflow-hidden">
                      <div
                        className={cn("h-full transition-all duration-500", stage.color)}
                        style={{ width: `${stage.rate * 10}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </BlueprintCard>

            {/* Conversion Rates */}
            <BlueprintCard className="p-6">
              <h3 className="text-sm font-semibold text-[var(--ink)] mb-4">Stage Conversion Rates</h3>
              <div className="space-y-3">
                {funnelData.slice(0, -1).map((stage, index) => {
                  const nextStage = funnelData[index + 1];
                  const rate = nextStage ? ((nextStage.count / stage.count) * 100) : 0;

                  return (
                    <div key={index} className="flex items-center justify-between p-3 bg-[var(--surface)] rounded-lg">
                      <div>
                        <p className="text-sm font-medium text-[var(--ink)]">
                          {stage.stage} → {nextStage?.stage}
                        </p>
                        <p className="text-xs text-[var(--ink-muted)]">
                          {nextStage?.count.toLocaleString()} / {stage.count.toLocaleString()}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className={cn(
                          "text-sm font-semibold",
                          rate > 20 ? "text-[var(--success)]" :
                            rate > 10 ? "text-[var(--warning)]" :
                              "text-[var(--destructive)]"
                        )}>
                          {rate.toFixed(1)}%
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </BlueprintCard>
          </div>
        )}

        {selectedMetric === 'channels' && (
          <div className="grid grid-cols-2 gap-6">
            {/* Channel Distribution */}
            <BlueprintCard className="p-6">
              <h3 className="text-sm font-semibold text-[var(--ink)] mb-4">Channel Distribution</h3>
              <div className="h-64 bg-[var(--surface)] rounded-[var(--radius)] flex items-center justify-center">
                <p className="text-sm text-[var(--ink-muted)]">Pie chart showing channel distribution</p>
              </div>
            </BlueprintCard>

            {/* Channel Performance */}
            <BlueprintCard className="p-6">
              <h3 className="text-sm font-semibold text-[var(--ink)] mb-4">Channel Performance</h3>
              <div className="space-y-3">
                {channelData.map((channel, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-[var(--surface)] rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className={cn("w-3 h-3 rounded-full", channel.color)} />
                      <div>
                        <p className="text-sm font-medium text-[var(--ink)]">{channel.name}</p>
                        <p className="text-xs text-[var(--ink-muted)]">{channel.value}% of total</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className={cn(
                        "flex items-center gap-1 text-xs",
                        channel.change > 0 ? "text-[var(--success)]" : "text-[var(--destructive)]"
                      )}>
                        {channel.change > 0 ? <ArrowUp size={12} /> : <ArrowDown size={12} />}
                        {Math.abs(channel.change)}%
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </BlueprintCard>
          </div>
        )}

        {selectedMetric === 'trends' && (
          <div className="space-y-6">
            {/* Trend Analysis */}
            <BlueprintCard className="p-6">
              <h3 className="text-sm font-semibold text-[var(--ink)] mb-4">Trend Analysis</h3>
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <h4 className="text-sm font-medium text-[var(--ink)] mb-3">Growth Trends</h4>
                  <div className="space-y-2">
                    {[
                      { metric: 'Weekly Growth', value: '+12.5%', trend: 'up' },
                      { metric: 'Monthly Growth', value: '+45.2%', trend: 'up' },
                      { metric: 'Quarterly Growth', value: '+123.8%', trend: 'up' }
                    ].map((item, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-[var(--surface)] rounded">
                        <span className="text-sm text-[var(--ink)]">{item.metric}</span>
                        <span className="text-sm font-medium text-[var(--success)]">{item.value}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-[var(--ink)] mb-3">Predictions</h4>
                  <div className="space-y-2">
                    {[
                      { metric: 'Next Week', value: '2,450 reach', confidence: '85%' },
                      { metric: 'Next Month', value: '10,200 reach', confidence: '78%' },
                      { metric: 'Next Quarter', value: '35,000 reach', confidence: '72%' }
                    ].map((item, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-[var(--surface)] rounded">
                        <div>
                          <span className="text-sm text-[var(--ink)]">{item.metric}</span>
                          <p className="text-xs text-[var(--ink-muted)]">{item.confidence} confidence</p>
                        </div>
                        <span className="text-sm font-medium text-[var(--blueprint)]">{item.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </BlueprintCard>

            {/* Recommendations */}
            <BlueprintCard className="p-6">
              <h3 className="text-sm font-semibold text-[var(--ink)] mb-4">AI Recommendations</h3>
              <div className="space-y-3">
                {[
                  {
                    type: 'optimization',
                    title: 'Optimize Email Send Times',
                    description: 'Best performance observed at 10 AM EST on Tuesdays',
                    impact: 'High'
                  },
                  {
                    type: 'budget',
                    title: 'Reallocate Budget to Social',
                    description: 'Social media showing 3x better ROI than paid ads',
                    impact: 'Medium'
                  },
                  {
                    type: 'content',
                    title: 'Create More Video Content',
                    description: 'Video posts have 2.5x higher engagement rate',
                    impact: 'High'
                  }
                ].map((rec, index) => (
                  <div key={index} className="flex items-start gap-3 p-3 bg-[var(--surface)] rounded-lg">
                    <div className={cn(
                      "w-2 h-2 rounded-full mt-2",
                      rec.impact === 'High' ? "bg-[var(--success)]" :
                        rec.impact === 'Medium' ? "bg-[var(--warning)]" :
                          "bg-[var(--ink-ghost)]"
                    )} />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-[var(--ink)]">{rec.title}</p>
                      <p className="text-xs text-[var(--ink-muted)] mt-1">{rec.description}</p>
                    </div>
                    <BlueprintBadge variant={rec.impact === 'High' ? "success" : "default"} size="sm">
                      {rec.type}
                    </BlueprintBadge>
                  </div>
                ))}
              </div>
            </BlueprintCard>
          </div>
        )}
      </div>
    </div>
  );
}
