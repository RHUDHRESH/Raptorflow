"use client";

import { useState, useEffect } from 'react';
import {
  BarChart3,
  LineChart,
  PieChart,
  TrendingUp,
  TrendingDown,
  Users,
  DollarSign,
  Target,
  Calendar,
  Download,
  Filter,
  Settings,
  RefreshCw,
  Eye,
  Maximize2,
  Minimize2,
  ChevronDown,
  ChevronUp,
  ChevronRight,
  ChevronLeft,
  Zap,
  AlertTriangle,
  CheckCircle,
  Clock,
  ArrowUp,
  ArrowDown,
  MoreVertical,
  Grid,
  List,
  Activity
} from 'lucide-react';
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { BlueprintButton } from '@/components/ui/BlueprintButton';
import { BlueprintBadge } from '@/components/ui/BlueprintBadge';
import { useEnhancedCampaignStore } from '@/stores/enhancedCampaignStore';
import { cn } from '@/lib/utils';
import { format, formatDistanceToNow, subDays, startOfDay, endOfDay } from 'date-fns';

interface AnalyticsMetric {
  id: string;
  name: string;
  value: number;
  previousValue: number;
  change: number;
  changeType: 'increase' | 'decrease';
  unit: string;
  trend: number[];
  target?: number;
  status: 'good' | 'warning' | 'critical';
}

interface CampaignPerformance {
  id: string;
  name: string;
  status: 'active' | 'paused' | 'completed';
  metrics: {
    reach: number;
    engagement: number;
    conversions: number;
    revenue: number;
    roi: number;
  };
  trend: {
    reach: number[];
    engagement: number[];
    conversions: number[];
    revenue: number[];
  };
  channels: string[];
  budget: {
    allocated: number;
    spent: number;
    remaining: number;
  };
}

interface FunnelStage {
  name: string;
  value: number;
  previousValue: number;
  change: number;
  conversionRate: number;
  dropOff: number;
  color: string;
}

interface CohortAnalysis {
  cohort: string;
  size: number;
  retention: number[];
  revenue: number[];
  ltv: number;
}

interface AttributionModel {
  name: string;
  type: 'first-touch' | 'last-touch' | 'linear' | 'time-decay' | 'position-based';
  weight: number;
  conversions: number;
  revenue: number;
}

export function AdvancedAnalyticsDashboard() {
  const [activeTab, setActiveTab] = useState<'overview' | 'campaigns' | 'funnel' | 'cohorts' | 'attribution'>('overview');
  const [dateRange, setDateRange] = useState<'7d' | '30d' | '90d' | 'custom'>('30d');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(['reach', 'engagement', 'conversions', 'revenue']);

  // Mock analytics metrics
  const [metrics, setMetrics] = useState<AnalyticsMetric[]>([
    {
      id: '1',
      name: 'Total Reach',
      value: 245678,
      previousValue: 198432,
      change: 23.8,
      changeType: 'increase',
      unit: 'users',
      trend: [180000, 195000, 210000, 225000, 240000, 245678],
      target: 250000,
      status: 'good'
    },
    {
      id: '2',
      name: 'Engagement Rate',
      value: 12.5,
      previousValue: 11.2,
      change: 11.6,
      changeType: 'increase',
      unit: '%',
      trend: [10.2, 10.8, 11.1, 11.5, 12.2, 12.5],
      target: 15,
      status: 'good'
    },
    {
      id: '3',
      name: 'Conversion Rate',
      value: 3.8,
      previousValue: 4.2,
      change: -9.5,
      changeType: 'decrease',
      unit: '%',
      trend: [4.5, 4.3, 4.1, 4.0, 3.9, 3.8],
      target: 5,
      status: 'warning'
    },
    {
      id: '4',
      name: 'Revenue',
      value: 124560,
      previousValue: 98320,
      change: 26.7,
      changeType: 'increase',
      unit: '$',
      trend: [85000, 92000, 98000, 105000, 115000, 124560],
      target: 150000,
      status: 'good'
    },
    {
      id: '5',
      name: 'Cost Per Acquisition',
      value: 28.50,
      previousValue: 32.10,
      change: -11.2,
      changeType: 'decrease',
      unit: '$',
      trend: [35.2, 34.1, 33.0, 31.5, 29.8, 28.5],
      target: 25,
      status: 'warning'
    },
    {
      id: '6',
      name: 'Return on Ad Spend',
      value: 4.2,
      previousValue: 3.8,
      change: 10.5,
      changeType: 'increase',
      unit: 'x',
      trend: [3.2, 3.4, 3.6, 3.9, 4.1, 4.2],
      target: 5,
      status: 'good'
    }
  ]);

  // Mock campaign performance
  const [campaignPerformance, setCampaignPerformance] = useState<CampaignPerformance[]>([
    {
      id: '1',
      name: 'Q1 Product Launch',
      status: 'active',
      metrics: {
        reach: 45000,
        engagement: 15.2,
        conversions: 680,
        revenue: 34000,
        roi: 3.4
      },
      trend: {
        reach: [20000, 25000, 30000, 35000, 40000, 45000],
        engagement: [12.1, 13.2, 14.1, 14.8, 15.0, 15.2],
        conversions: [200, 350, 450, 550, 620, 680],
        revenue: [10000, 17500, 22500, 27500, 31000, 34000]
      },
      channels: ['email', 'social', 'paid'],
      budget: {
        allocated: 15000,
        spent: 10200,
        remaining: 4800
      }
    },
    {
      id: '2',
      name: 'Holiday Sales Campaign',
      status: 'completed',
      metrics: {
        reach: 78000,
        engagement: 18.2,
        conversions: 1240,
        revenue: 62000,
        roi: 4.8
      },
      trend: {
        reach: [30000, 40000, 50000, 60000, 70000, 78000],
        engagement: [15.1, 16.2, 17.1, 17.8, 18.0, 18.2],
        conversions: [400, 600, 800, 1000, 1120, 1240],
        revenue: [20000, 30000, 40000, 50000, 56000, 62000]
      },
      channels: ['email', 'social', 'sms', 'paid'],
      budget: {
        allocated: 25000,
        spent: 25200,
        remaining: -200
      }
    }
  ]);

  // Mock funnel data
  const [funnelData, setFunnelData] = useState<FunnelStage[]>([
    {
      name: 'Awareness',
      value: 100000,
      previousValue: 85000,
      change: 17.6,
      conversionRate: 100,
      dropOff: 0,
      color: 'bg-[var(--blueprint)]'
    },
    {
      name: 'Interest',
      value: 45000,
      previousValue: 38000,
      change: 18.4,
      conversionRate: 45,
      dropOff: 55,
      color: 'bg-[var(--success)]'
    },
    {
      name: 'Consideration',
      value: 18000,
      previousValue: 15000,
      change: 20.0,
      conversionRate: 18,
      dropOff: 60,
      color: 'bg-[var(--warning)]'
    },
    {
      name: 'Conversion',
      value: 3800,
      previousValue: 3200,
      change: 18.8,
      conversionRate: 3.8,
      dropOff: 78.9,
      color: 'bg-[var(--destructive)]'
    },
    {
      name: 'Retention',
      value: 2850,
      previousValue: 2400,
      change: 18.8,
      conversionRate: 75,
      dropOff: 25,
      color: 'bg-[var(--purple)]'
    }
  ]);

  // Mock cohort analysis
  const [cohortData, setCohortData] = useState<CohortAnalysis[]>([
    {
      cohort: 'Jan 2024',
      size: 2500,
      retention: [100, 85, 72, 65, 58, 52, 48, 45],
      revenue: [2500, 4200, 5800, 7200, 8500, 9800, 11000, 12500],
      ltv: 12500
    },
    {
      cohort: 'Feb 2024',
      size: 2800,
      retention: [100, 88, 75, 68, 61, 55, 51, 48],
      revenue: [2800, 4800, 6800, 8600, 10200, 11800, 13400, 15200],
      ltv: 15200
    },
    {
      cohort: 'Mar 2024',
      size: 3200,
      retention: [100, 90, 78, 71, 64, 58, 54, 51],
      revenue: [3200, 5600, 8000, 10200, 12200, 14200, 16200, 18400],
      ltv: 18400
    }
  ]);

  // Mock attribution models
  const [attributionModels, setAttributionModels] = useState<AttributionModel[]>([
    {
      name: 'First Touch',
      type: 'first-touch',
      weight: 100,
      conversions: 380,
      revenue: 19000
    },
    {
      name: 'Last Touch',
      type: 'last-touch',
      weight: 100,
      conversions: 420,
      revenue: 21000
    },
    {
      name: 'Linear',
      type: 'linear',
      weight: 100,
      conversions: 400,
      revenue: 20000
    },
    {
      name: 'Time Decay',
      type: 'time-decay',
      weight: 100,
      conversions: 410,
      revenue: 20500
    },
    {
      name: 'Position Based',
      type: 'position-based',
      weight: 100,
      conversions: 395,
      revenue: 19750
    }
  ]);

  // Format metric value
  const formatMetricValue = (value: number, unit: string) => {
    if (unit === '$') {
      return `$${value.toLocaleString()}`;
    } else if (unit === '%') {
      return `${value.toFixed(1)}%`;
    } else if (unit === 'x') {
      return `${value.toFixed(1)}x`;
    } else {
      return value.toLocaleString();
    }
  };

  // Render overview dashboard
  const renderOverview = () => (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {metrics.map((metric) => (
          <BlueprintCard key={metric.id} className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-sm font-medium text-[var(--ink-muted)]">{metric.name}</h3>
                <div className="text-2xl font-bold text-[var(--ink)] mt-1">
                  {formatMetricValue(metric.value, metric.unit)}
                </div>
              </div>

              <div className={cn(
                "flex items-center gap-1 px-2 py-1 rounded text-xs font-medium",
                metric.changeType === 'increase' && "bg-[var(--success-light)]/10 text-[var(--success)]",
                metric.changeType === 'decrease' && "bg-[var(--destructive-light)]/10 text-[var(--destructive)]"
              )}>
                {metric.changeType === 'increase' ? <ArrowUp size={12} /> : <ArrowDown size={12} />}
                {Math.abs(metric.change)}%
              </div>
            </div>

            {/* Mini Chart */}
            <div className="h-16 mb-4">
              <div className="h-full flex items-end gap-1">
                {metric.trend.map((value, index) => (
                  <div
                    key={index}
                    className="flex-1 bg-[var(--blueprint-light)]/20 rounded-t"
                    style={{ height: `${(value / Math.max(...metric.trend)) * 100}%` }}
                  />
                ))}
              </div>
            </div>

            {/* Target and Status */}
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <Target size={12} className="text-[var(--ink-ghost)]" />
                <span className="text-[var(--ink-muted)]">
                  Target: {formatMetricValue(metric.target || 0, metric.unit)}
                </span>
              </div>

              <BlueprintBadge
                variant={metric.status === 'good' ? 'success' : metric.status === 'warning' ? 'warning' : 'error'}
                size="sm"
              >
                {metric.status}
              </BlueprintBadge>
            </div>
          </BlueprintCard>
        ))}
      </div>

      {/* Performance Trends */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <BlueprintCard className="p-6">
          <h3 className="text-lg font-semibold text-[var(--ink)] mb-4">Revenue Trend</h3>
          <div className="h-64 bg-[var(--surface)] rounded-lg flex items-center justify-center">
            <div className="text-center">
              <LineChart size={48} className="text-[var(--blueprint)] mx-auto mb-2" />
              <p className="text-sm text-[var(--ink)]">Interactive revenue chart</p>
            </div>
          </div>
        </BlueprintCard>

        <BlueprintCard className="p-6">
          <h3 className="text-lg font-semibold text-[var(--ink)] mb-4">Channel Performance</h3>
          <div className="h-64 bg-[var(--surface)] rounded-lg flex items-center justify-center">
            <div className="text-center">
              <PieChart size={48} className="text-[var(--blueprint)] mx-auto mb-2" />
              <p className="text-sm text-[var(--ink)]">Channel distribution chart</p>
            </div>
          </div>
        </BlueprintCard>
      </div>
    </div>
  );

  // Render campaign performance
  const renderCampaignPerformance = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[var(--ink)]">Campaign Performance</h2>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Detailed performance metrics for all campaigns
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1">
            <button
              onClick={() => setViewMode('grid')}
              className={cn(
                "p-2 rounded",
                viewMode === 'grid' && "bg-[var(--blueprint-light)]/10 text-[var(--blueprint)]"
              )}
            >
              <Grid size={16} />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={cn(
                "p-2 rounded",
                viewMode === 'list' && "bg-[var(--blueprint-light)]/10 text-[var(--blueprint)]"
              )}
            >
              <List size={16} />
            </button>
          </div>

          <BlueprintButton variant="secondary" className="flex items-center gap-2">
            <Filter size={16} />
            Filter
          </BlueprintButton>
        </div>
      </div>

      <div className={cn(
        viewMode === 'grid' ? "grid grid-cols-1 lg:grid-cols-2 gap-6" : "space-y-4"
      )}>
        {campaignPerformance.map((campaign) => (
          <BlueprintCard key={campaign.id} className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-[var(--ink)]">{campaign.name}</h3>
                <BlueprintBadge
                  variant={campaign.status === 'active' ? 'success' : campaign.status === 'completed' ? 'default' : 'warning'}
                  size="sm"
                >
                  {campaign.status}
                </BlueprintBadge>
              </div>

              <button className="p-1 text-[var(--ink-ghost)] hover:text-[var(--ink)]">
                <MoreVertical size={16} />
              </button>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <div className="text-sm text-[var(--ink-muted)]">Reach</div>
                <div className="text-lg font-bold text-[var(--ink)]">
                  {campaign.metrics.reach.toLocaleString()}
                </div>
              </div>
              <div>
                <div className="text-sm text-[var(--ink-muted)]">Engagement</div>
                <div className="text-lg font-bold text-[var(--blueprint)]">
                  {campaign.metrics.engagement}%
                </div>
              </div>
              <div>
                <div className="text-sm text-[var(--ink-muted)]">Conversions</div>
                <div className="text-lg font-bold text-[var(--success)]">
                  {campaign.metrics.conversions}
                </div>
              </div>
              <div>
                <div className="text-sm text-[var(--ink-muted)]">Revenue</div>
                <div className="text-lg font-bold text-[var(--success)]">
                  ${campaign.metrics.revenue.toLocaleString()}
                </div>
              </div>
            </div>

            {/* Budget Usage */}
            <div className="mb-4">
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-[var(--ink-muted)]">Budget Usage</span>
                <span className="text-[var(--ink)]">
                  ${campaign.budget.spent.toLocaleString()} / ${campaign.budget.allocated.toLocaleString()}
                </span>
              </div>
              <div className="w-full bg-[var(--structure-subtle)] rounded-full h-2">
                <div
                  className={cn(
                    "h-2 rounded-full",
                    campaign.budget.spent > campaign.budget.allocated ? "bg-[var(--destructive)]" : "bg-[var(--blueprint)]"
                  )}
                  style={{ width: `${Math.min((campaign.budget.spent / campaign.budget.allocated) * 100, 100)}%` }}
                />
              </div>
            </div>

            {/* Channels */}
            <div className="flex items-center justify-between">
              <div className="flex flex-wrap gap-1">
                {campaign.channels.map((channel) => (
                  <span key={channel} className="px-2 py-1 text-xs bg-[var(--surface)] text-[var(--ink)] rounded capitalize">
                    {channel}
                  </span>
                ))}
              </div>

              <BlueprintButton variant="secondary" size="sm">
                <Eye size={14} />
                Details
              </BlueprintButton>
            </div>
          </BlueprintCard>
        ))}
      </div>
    </div>
  );

  // Render conversion funnel
  const renderConversionFunnel = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[var(--ink)]">Conversion Funnel</h2>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Track customer journey through conversion stages
          </p>
        </div>

        <div className="flex items-center gap-2">
          <select className="px-3 py-2 bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] text-sm">
            <option>Last 30 days</option>
            <option>Last 7 days</option>
            <option>Last 90 days</option>
          </select>
        </div>
      </div>

      <BlueprintCard className="p-6">
        <div className="space-y-4">
          {funnelData.map((stage, index) => (
            <div key={stage.name} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={cn(
                    "w-4 h-4 rounded",
                    stage.color
                  )} />
                  <span className="text-sm font-medium text-[var(--ink)]">{stage.name}</span>
                  <BlueprintBadge variant="default" size="sm">
                    {stage.conversionRate}%
                  </BlueprintBadge>
                </div>

                <div className="flex items-center gap-4 text-sm">
                  <div className="text-right">
                    <div className="font-medium text-[var(--ink)]">
                      {stage.value.toLocaleString()}
                    </div>
                    <div className={cn(
                      "text-xs",
                      stage.change > 0 ? "text-[var(--success)]" : "text-[var(--destructive)]"
                    )}>
                      {stage.change > 0 ? '+' : ''}{stage.change}% vs prev
                    </div>
                  </div>

                  {stage.dropOff > 0 && (
                    <div className="text-right">
                      <div className="text-[var(--ink-muted)]">Drop-off</div>
                      <div className="font-medium text-[var(--destructive)]">
                        {stage.dropOff}%
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Funnel Bar */}
              <div className="relative">
                <div className="w-full bg-[var(--structure-subtle)] rounded-full h-8">
                  <div
                    className={cn(
                      "h-8 rounded-full transition-all",
                      stage.color
                    )}
                    style={{ width: `${stage.conversionRate}%` }}
                  />
                </div>

                {/* Drop-off indicators */}
                {index < funnelData.length - 1 && stage.dropOff > 0 && (
                  <div className="absolute top-0 right-0 h-8 flex items-center pr-2">
                    <span className="text-xs text-[var(--destructive)] font-medium">
                      -{stage.dropOff}%
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </BlueprintCard>
    </div>
  );

  // Render cohort analysis
  const renderCohortAnalysis = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[var(--ink)]">Cohort Analysis</h2>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Track customer retention and lifetime value
          </p>
        </div>

        <BlueprintButton variant="secondary" className="flex items-center gap-2">
          <Download size={16} />
          Export
        </BlueprintButton>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Retention Matrix */}
        <BlueprintCard className="p-6">
          <h3 className="text-lg font-semibold text-[var(--ink)] mb-4">Retention Matrix</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--structure-subtle)]">
                  <th className="text-left py-2 px-2">Cohort</th>
                  <th className="text-center py-2 px-2">Size</th>
                  {[0, 1, 2, 3, 4, 5, 6, 7].map(week => (
                    <th key={week} className="text-center py-2 px-2">W{week}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {cohortData.map((cohort) => (
                  <tr key={cohort.cohort} className="border-b border-[var(--structure-subtle)]">
                    <td className="py-2 px-2 font-medium">{cohort.cohort}</td>
                    <td className="text-center py-2 px-2">{cohort.size.toLocaleString()}</td>
                    {cohort.retention.map((rate, index) => (
                      <td key={index} className="text-center py-2 px-2">
                        <div className={cn(
                          "px-2 py-1 rounded text-xs font-medium",
                          rate >= 80 && "bg-[var(--success-light)]/10 text-[var(--success)]",
                          rate >= 60 && rate < 80 && "bg-[var(--warning-light)]/10 text-[var(--warning)]",
                          rate < 60 && "bg-[var(--destructive-light)]/10 text-[var(--destructive)]"
                        )}>
                          {rate}%
                        </div>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </BlueprintCard>

        {/* LTV Analysis */}
        <BlueprintCard className="p-6">
          <h3 className="text-lg font-semibold text-[var(--ink)] mb-4">Lifetime Value Analysis</h3>
          <div className="space-y-4">
            {cohortData.map((cohort) => (
              <div key={cohort.cohort} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-[var(--ink)]">{cohort.cohort}</span>
                  <span className="text-sm font-bold text-[var(--success)]">
                    ${cohort.ltv.toLocaleString()}
                  </span>
                </div>

                <div className="w-full bg-[var(--structure-subtle)] rounded-full h-2">
                  <div
                    className="bg-[var(--success)] h-2 rounded-full"
                    style={{ width: `${(cohort.ltv / 20000) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </BlueprintCard>
      </div>
    </div>
  );

  // Render attribution analysis
  const renderAttributionAnalysis = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[var(--ink)]">Attribution Analysis</h2>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Compare different attribution models
          </p>
        </div>

        <BlueprintButton className="flex items-center gap-2">
          <Settings size={16} />
          Configure Models
        </BlueprintButton>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Model Comparison */}
        <BlueprintCard className="p-6">
          <h3 className="text-lg font-semibold text-[var(--ink)] mb-4">Model Comparison</h3>
          <div className="space-y-4">
            {attributionModels.map((model) => (
              <div key={model.name} className="flex items-center justify-between p-3 bg-[var(--surface)] rounded-lg">
                <div>
                  <div className="text-sm font-medium text-[var(--ink)]">{model.name}</div>
                  <div className="text-xs text-[var(--ink-muted)] capitalize">{model.type.replace('-', ' ')}</div>
                </div>

                <div className="text-right">
                  <div className="text-sm font-medium text-[var(--ink)]">
                    {model.conversions} conv
                  </div>
                  <div className="text-xs text-[var(--success)]">
                    ${model.revenue.toLocaleString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </BlueprintCard>

        {/* Attribution Visualization */}
        <BlueprintCard className="p-6">
          <h3 className="text-lg font-semibold text-[var(--ink)] mb-4">Touchpoint Analysis</h3>
          <div className="h-64 bg-[var(--surface)] rounded-lg flex items-center justify-center">
            <div className="text-center">
              <BarChart3 size={48} className="text-[var(--blueprint)] mx-auto mb-2" />
              <p className="text-sm text-[var(--ink)]">Touchpoint attribution chart</p>
            </div>
          </div>
        </BlueprintCard>
      </div>
    </div>
  );

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-[var(--structure-subtle)]">
        <div>
          <h1 className="text-2xl font-bold text-[var(--ink)]">Advanced Analytics</h1>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Comprehensive analytics and insights
          </p>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value as any)}
            className="px-3 py-2 bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] text-sm"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="custom">Custom range</option>
          </select>

          <BlueprintButton variant="secondary" className="flex items-center gap-2">
            <RefreshCw size={16} />
            Refresh
          </BlueprintButton>

          <BlueprintButton variant="secondary" className="flex items-center gap-2">
            <Download size={16} />
            Export
          </BlueprintButton>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-6 px-6 border-b border-[var(--structure-subtle)]">
        {[
          { id: 'overview', label: 'Overview', icon: BarChart3 },
          { id: 'campaigns', label: 'Campaigns', icon: Target },
          { id: 'funnel', label: 'Funnel', icon: TrendingUp },
          { id: 'cohorts', label: 'Cohorts', icon: Users },
          { id: 'attribution', label: 'Attribution', icon: Zap }
        ].map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={cn(
                "flex items-center gap-2 py-3 px-1 text-sm font-medium border-b-2 transition-colors",
                activeTab === tab.id
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

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'campaigns' && renderCampaignPerformance()}
        {activeTab === 'funnel' && renderConversionFunnel()}
        {activeTab === 'cohorts' && renderCohortAnalysis()}
        {activeTab === 'attribution' && renderAttributionAnalysis()}
      </div>
    </div>
  );
}
