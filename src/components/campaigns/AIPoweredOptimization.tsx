"use client";

import { useState, useEffect } from 'react';
import {
  Brain,
  TrendingUp,
  Target,
  Zap,
  AlertTriangle,
  CheckCircle,
  Clock,
  BarChart3,
  DollarSign,
  Users,
  Settings,
  Play,
  Pause,
  RefreshCw,
  Download,
  Eye,
  ChevronDown,
  ChevronUp,
  Info,
  Sparkles,
  Activity,
  Lightbulb,
  ArrowUp,
  ArrowDown,
  Minus,
  X,
  Plus
} from 'lucide-react';
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { BlueprintButton } from '@/components/ui/BlueprintButton';
import { BlueprintBadge } from '@/components/ui/BlueprintBadge';
import { useEnhancedCampaignStore } from '@/stores/enhancedCampaignStore';
import { cn } from '@/lib/utils';
import { format } from 'date-fns';
import { formatDistanceToNow } from 'date-fns/formatDistanceToNow';

interface AIInsight {
  id: string;
  type: 'optimization' | 'anomaly' | 'opportunity' | 'warning';
  title: string;
  description: string;
  confidence: number;
  impact: 'high' | 'medium' | 'low';
  category: 'budget' | 'performance' | 'audience' | 'timing' | 'content';
  data: {
    currentValue?: number;
    recommendedValue?: number;
    potentialImprovement?: number;
    metric?: string;
    timeframe?: string;
  };
  actions: {
    primary: string;
    secondary?: string;
    autoApply?: boolean;
  };
  createdAt: Date;
  status: 'pending' | 'reviewed' | 'applied' | 'dismissed';
}

interface PredictiveModel {
  id: string;
  name: string;
  type: 'conversion' | 'engagement' | 'revenue' | 'churn';
  accuracy: number;
  confidence: number;
  predictions: {
    timeframe: string;
    value: number;
    range: { min: number; max: number };
    factors: string[];
  };
  lastUpdated: Date;
  status: 'active' | 'training' | 'inactive';
}

interface ABOption {
  id: string;
  name: string;
  description: string;
  variants: {
    id: string;
    name: string;
    config: Record<string, any>;
    performance: {
      conversions: number;
      revenue: number;
      engagement: number;
      confidence: number;
    };
  }[];
  status: 'draft' | 'running' | 'completed' | 'paused';
  startDate: Date;
  endDate?: Date;
  winner?: string;
}

interface SmartBudget {
  campaignId: string;
  totalBudget: number;
  allocations: {
    moveType: string;
    current: number;
    recommended: number;
    roi: number;
    efficiency: number;
  }[];
  optimization: {
    totalImprovement: number;
    potentialROI: number;
    reallocationPlan: {
      from: string;
      to: string;
      amount: number;
      reason: string;
    }[];
  };
  lastOptimized: Date;
}

export function AIPoweredOptimization() {
  const campaigns = useEnhancedCampaignStore(state => state.campaigns);
  const updateCampaign = useEnhancedCampaignStore(state => state.updateCampaign);

  const [activeTab, setActiveTab] = useState<'insights' | 'predictions' | 'abtesting' | 'budget'>('insights');
  const [selectedInsight, setSelectedInsight] = useState<AIInsight | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [autoOptimization, setAutoOptimization] = useState(true);

  // Mock AI insights
  const [insights, setInsights] = useState<AIInsight[]>([
    {
      id: '1',
      type: 'optimization',
      title: 'Email Subject Line Optimization',
      description: 'AI analysis suggests that personalizing subject lines with recipient names could increase open rates by 23%',
      confidence: 87,
      impact: 'high',
      category: 'content',
      data: {
        currentValue: 32,
        recommendedValue: 39,
        potentialImprovement: 23,
        metric: 'open_rate',
        timeframe: '2 weeks'
      },
      actions: {
        primary: 'Apply personalization',
        secondary: 'Run A/B test',
        autoApply: true
      },
      createdAt: new Date(Date.now() - 3600000),
      status: 'pending'
    },
    {
      id: '2',
      type: 'anomaly',
      title: 'Unusual Drop in Engagement',
      description: 'Detected 40% drop in social media engagement over the last 48 hours, significantly below expected patterns',
      confidence: 92,
      impact: 'high',
      category: 'performance',
      data: {
        currentValue: 2.1,
        recommendedValue: 3.5,
        potentialImprovement: -40,
        metric: 'engagement_rate',
        timeframe: '48 hours'
      },
      actions: {
        primary: 'Investigate cause',
        secondary: 'Pause social campaigns'
      },
      createdAt: new Date(Date.now() - 7200000),
      status: 'pending'
    },
    {
      id: '3',
      type: 'opportunity',
      title: 'Cross-Sell Opportunity',
      description: 'AI identifies high-propensity customers for premium upgrade based on recent behavior patterns',
      confidence: 78,
      impact: 'medium',
      category: 'audience',
      data: {
        currentValue: 0,
        recommendedValue: 15,
        potentialImprovement: 15,
        metric: 'upgrade_rate',
        timeframe: '1 month'
      },
      actions: {
        primary: 'Create upgrade campaign',
        secondary: 'Review audience segments'
      },
      createdAt: new Date(Date.now() - 10800000),
      status: 'reviewed'
    }
  ]);

  // Mock predictive models
  const [predictiveModels, setPredictiveModels] = useState<PredictiveModel[]>([
    {
      id: '1',
      name: 'Conversion Probability Model',
      type: 'conversion',
      accuracy: 94,
      confidence: 89,
      predictions: {
        timeframe: '30 days',
        value: 1250,
        range: { min: 1100, max: 1400 },
        factors: ['email_engagement', 'website_visits', 'content_interaction', 'time_of_day']
      },
      lastUpdated: new Date(Date.now() - 86400000),
      status: 'active'
    },
    {
      id: '2',
      name: 'Revenue Forecast Model',
      type: 'revenue',
      accuracy: 91,
      confidence: 85,
      predictions: {
        timeframe: 'Q1 2024',
        value: 250000,
        range: { min: 220000, max: 280000 },
        factors: ['seasonal_trends', 'market_conditions', 'campaign_performance', 'competitor_activity']
      },
      lastUpdated: new Date(Date.now() - 172800000),
      status: 'active'
    },
    {
      id: '3',
      name: 'Customer Churn Prediction',
      type: 'churn',
      accuracy: 88,
      confidence: 82,
      predictions: {
        timeframe: '90 days',
        value: 8.5,
        range: { min: 6.2, max: 10.8 },
        factors: ['usage_frequency', 'support_tickets', 'feature_adoption', 'payment_history']
      },
      lastUpdated: new Date(Date.now() - 259200000),
      status: 'active'
    }
  ]);

  // Mock A/B tests
  const [abTests, setAbTests] = useState<ABOption[]>([
    {
      id: '1',
      name: 'Email Subject Line Test',
      description: 'Testing personalized vs generic subject lines',
      variants: [
        {
          id: 'v1',
          name: 'Personalized',
          config: { subject: 'Hi {firstName}, check this out!' },
          performance: { conversions: 45, revenue: 2250, engagement: 32, confidence: 78 }
        },
        {
          id: 'v2',
          name: 'Generic',
          config: { subject: 'Check out our latest offer!' },
          performance: { conversions: 32, revenue: 1600, engagement: 28, confidence: 82 }
        }
      ],
      status: 'running',
      startDate: new Date(Date.now() - 604800000)
    },
    {
      id: '2',
      name: 'Landing Page CTA Test',
      description: 'Testing different call-to-action button colors and text',
      variants: [
        {
          id: 'v1',
          name: 'Blue Button',
          config: { color: 'blue', text: 'Get Started Now' },
          performance: { conversions: 28, revenue: 1400, engagement: 45, confidence: 71 }
        },
        {
          id: 'v2',
          name: 'Green Button',
          config: { color: 'green', text: 'Start Free Trial' },
          performance: { conversions: 35, revenue: 1750, engagement: 52, confidence: 74 }
        }
      ],
      status: 'completed',
      startDate: new Date(Date.now() - 1209600000),
      endDate: new Date(Date.now() - 604800000),
      winner: 'v2'
    }
  ]);

  // Mock smart budget
  const [smartBudget, setSmartBudget] = useState<SmartBudget>({
    campaignId: 'campaign-1',
    totalBudget: 50000,
    allocations: [
      {
        moveType: 'email',
        current: 20000,
        recommended: 25000,
        roi: 4.2,
        efficiency: 0.85
      },
      {
        moveType: 'social',
        current: 15000,
        recommended: 12000,
        roi: 3.1,
        efficiency: 0.72
      },
      {
        moveType: 'content',
        current: 10000,
        recommended: 8000,
        roi: 2.8,
        efficiency: 0.68
      },
      {
        moveType: 'paid',
        current: 5000,
        recommended: 5000,
        roi: 5.5,
        efficiency: 0.91
      }
    ],
    optimization: {
      totalImprovement: 18.5,
      potentialROI: 23400,
      reallocationPlan: [
        {
          from: 'social',
          to: 'email',
          amount: 3000,
          reason: 'Email marketing shows higher ROI and efficiency'
        },
        {
          from: 'content',
          to: 'paid',
          amount: 2000,
          reason: 'Paid advertising has the highest efficiency score'
        }
      ]
    },
    lastOptimized: new Date(Date.now() - 86400000)
  });

  // Handle insight action
  const handleInsightAction = async (insight: AIInsight, action: 'primary' | 'secondary') => {
    const actionText = action === 'primary' ? insight.actions.primary : insight.actions.secondary;
    console.log(`Executing action: ${actionText}`);

    // Update insight status
    setInsights(prev => prev.map(i =>
      i.id === insight.id
        ? { ...i, status: 'applied' as const }
        : i
    ));

    // If auto-apply is available, simulate applying the optimization
    if (action === 'primary' && insight.actions.autoApply) {
      setIsAnalyzing(true);
      setTimeout(() => {
        setIsAnalyzing(false);
        console.log('Auto-optimization applied successfully');
      }, 2000);
    }
  };

  // Handle insight dismissal
  const handleDismissInsight = (insightId: string) => {
    setInsights(prev => prev.map(i =>
      i.id === insightId
        ? { ...i, status: 'dismissed' as const }
        : i
    ));
  };

  // Run AI analysis
  const runAIAnalysis = async () => {
    setIsAnalyzing(true);

    // Simulate AI analysis
    setTimeout(() => {
      const newInsight: AIInsight = {
        id: Date.now().toString(),
        type: 'optimization',
        title: 'New AI Insight',
        description: 'AI has identified a new optimization opportunity based on recent campaign performance',
        confidence: 85,
        impact: 'medium',
        category: 'performance',
        data: {
          currentValue: 100,
          recommendedValue: 120,
          potentialImprovement: 20,
          metric: 'conversion_rate',
          timeframe: '1 week'
        },
        actions: {
          primary: 'Apply optimization',
          autoApply: true
        },
        createdAt: new Date(),
        status: 'pending'
      };

      setInsights(prev => [newInsight, ...prev]);
      setIsAnalyzing(false);
    }, 3000);
  };

  // Render AI insights
  const renderAIInsights = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[var(--ink)]">AI Insights</h2>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            AI-powered recommendations to optimize your campaigns
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={autoOptimization}
                onChange={(e) => setAutoOptimization(e.target.checked)}
                className="rounded border-[var(--structure-subtle)] text-[var(--blueprint)]"
              />
              Auto-apply optimizations
            </label>
          </div>

          <BlueprintButton
            onClick={runAIAnalysis}
            disabled={isAnalyzing}
            className="flex items-center gap-2"
          >
            <Brain size={16} className={cn(isAnalyzing && 'animate-pulse')} />
            {isAnalyzing ? 'Analyzing...' : 'Run Analysis'}
          </BlueprintButton>
        </div>
      </div>

      {/* Insights List */}
      <div className="space-y-4">
        {insights.map((insight) => (
          <BlueprintCard key={insight.id} className={cn(
            "p-4 transition-all",
            insight.status === 'applied' && "border-[var(--success)] bg-[var(--success-light)]/5",
            insight.status === 'dismissed' && "opacity-50"
          )}>
            <div className="flex items-start gap-4">
              {/* Icon */}
              <div className={cn(
                "w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0",
                insight.type === 'optimization' && "bg-[var(--blueprint-light)]/10",
                insight.type === 'anomaly' && "bg-[var(--warning-light)]/10",
                insight.type === 'opportunity' && "bg-[var(--success-light)]/10",
                insight.type === 'warning' && "bg-[var(--destructive-light)]/10"
              )}>
                {insight.type === 'optimization' && <Zap size={20} className="text-[var(--blueprint)]" />}
                {insight.type === 'anomaly' && <AlertTriangle size={20} className="text-[var(--warning)]" />}
                {insight.type === 'opportunity' && <Lightbulb size={20} className="text-[var(--success)]" />}
                {insight.type === 'warning' && <AlertTriangle size={20} className="text-[var(--destructive)]" />}
              </div>

              {/* Content */}
              <div className="flex-1">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h3 className="text-sm font-semibold text-[var(--ink)]">{insight.title}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      <BlueprintBadge
                        variant="default"
                        size="sm"
                        className={cn(
                          insight.impact === 'high' && "border-[var(--destructive)] text-[var(--destructive)]",
                          insight.impact === 'medium' && "border-[var(--warning)] text-[var(--warning)]",
                          insight.impact === 'low' && "border-[var(--success)] text-[var(--success)]"
                        )}
                      >
                        {insight.impact} impact
                      </BlueprintBadge>

                      <BlueprintBadge variant="default" size="sm">
                        {insight.category}
                      </BlueprintBadge>

                      <span className="text-xs text-[var(--ink-muted)]">
                        {insight.confidence}% confidence
                      </span>
                    </div>
                  </div>

                  {/* Status */}
                  <div className="flex items-center gap-2">
                    {insight.status === 'applied' && (
                      <CheckCircle size={16} className="text-[var(--success)]" />
                    )}
                    {insight.status === 'dismissed' && (
                      <X size={16} className="text-[var(--ink-ghost)]" />
                    )}
                    <span className="text-xs text-[var(--ink-muted)]">
                      {formatDistanceToNow(insight.createdAt, { addSuffix: true })}
                    </span>
                  </div>
                </div>

                <p className="text-sm text-[var(--ink-muted)] mb-3">{insight.description}</p>

                {/* Data Visualization */}
                {insight.data && (
                  <div className="mb-3 p-3 bg-[var(--surface)] rounded-lg">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-[var(--ink-muted)]">
                        {insight.data.metric?.replace('_', ' ').toUpperCase()}
                      </span>
                      <div className="flex items-center gap-2">
                        <span className="text-[var(--ink)]">
                          {insight.data.currentValue}
                        </span>
                        <ArrowUp size={12} className="text-[var(--success)]" />
                        <span className="text-[var(--success)] font-medium">
                          {insight.data.recommendedValue}
                        </span>
                        <span className="text-[var(--ink-muted)]">
                          (+{insight.data.potentialImprovement}%)
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center gap-2">
                  <BlueprintButton
                    size="sm"
                    onClick={() => handleInsightAction(insight, 'primary')}
                    disabled={insight.status === 'applied'}
                    className="flex items-center gap-2"
                  >
                    <Play size={14} />
                    {insight.actions.primary}
                  </BlueprintButton>

                  {insight.actions.secondary && (
                    <BlueprintButton
                      variant="secondary"
                      size="sm"
                      onClick={() => handleInsightAction(insight, 'secondary')}
                    >
                      {insight.actions.secondary}
                    </BlueprintButton>
                  )}

                  <BlueprintButton
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDismissInsight(insight.id)}
                    className="text-[var(--ink-ghost)] hover:text-[var(--destructive)]"
                  >
                    Dismiss
                  </BlueprintButton>
                </div>
              </div>
            </div>
          </BlueprintCard>
        ))}
      </div>
    </div>
  );

  // Render predictive analytics
  const renderPredictiveAnalytics = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[var(--ink)]">Predictive Analytics</h2>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            AI-powered forecasts and predictions for campaign performance
          </p>
        </div>

        <BlueprintButton className="flex items-center gap-2">
          <RefreshCw size={16} />
          Retrain Models
        </BlueprintButton>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Predictive Models */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-[var(--ink)]">Active Models</h3>

          {predictiveModels.map((model) => (
            <BlueprintCard key={model.id} className="p-4">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h4 className="text-sm font-semibold text-[var(--ink)]">{model.name}</h4>
                  <div className="flex items-center gap-2 mt-1">
                    <BlueprintBadge variant="default" size="sm">
                      {model.type.replace('_', ' ')}
                    </BlueprintBadge>

                    <BlueprintBadge
                      variant="default"
                      size="sm"
                    >
                      {model.status}
                    </BlueprintBadge>
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-xs text-[var(--ink-muted)]">Accuracy</div>
                  <div className="text-lg font-bold text-[var(--success)]">{model.accuracy}%</div>
                </div>
              </div>

              <div className="space-y-3">
                <div>
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="text-[var(--ink-muted)]">Prediction</span>
                    <span className="text-[var(--ink)]">{model.predictions.timeframe}</span>
                  </div>
                  <div className="text-2xl font-bold text-[var(--ink)]">
                    {model.predictions.value.toLocaleString()}
                  </div>
                  <div className="text-xs text-[var(--ink-muted)]">
                    Range: {model.predictions.range.min.toLocaleString()} - {model.predictions.range.max.toLocaleString()}
                  </div>
                </div>

                <div>
                  <div className="text-xs font-medium text-[var(--ink-muted)] mb-2">Key Factors</div>
                  <div className="flex flex-wrap gap-1">
                    {model.predictions.factors.map((factor, index) => (
                      <span key={index} className="px-2 py-1 text-xs bg-[var(--surface)] text-[var(--ink)] rounded">
                        {factor.replace('_', ' ')}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex items-center justify-between pt-3 border-t border-[var(--structure-subtle)]">
                  <span className="text-xs text-[var(--ink-muted)]">
                    Updated {formatDistanceToNow(model.lastUpdated, { addSuffix: true })}
                  </span>

                  <BlueprintButton variant="secondary" size="sm">
                    View Details
                  </BlueprintButton>
                </div>
              </div>
            </BlueprintCard>
          ))}
        </div>

        {/* Forecast Visualization */}
        <BlueprintCard className="p-6">
          <h3 className="text-lg font-semibold text-[var(--ink)] mb-4">Revenue Forecast</h3>

          <div className="h-64 bg-[var(--surface)] rounded-lg flex items-center justify-center mb-4">
            <div className="text-center">
              <TrendingUp size={48} className="text-[var(--blueprint)] mx-auto mb-2" />
              <p className="text-sm text-[var(--ink)]">Interactive forecast chart</p>
              <p className="text-xs text-[var(--ink-muted)]">Shows predicted revenue over time</p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-[var(--success)]">$250K</div>
              <div className="text-xs text-[var(--ink-muted)]">Q1 Forecast</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-[var(--blueprint)]">91%</div>
              <div className="text-xs text-[var(--ink-muted)]">Confidence</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-[var(--warning)]">±12%</div>
              <div className="text-xs text-[var(--ink-muted)]">Margin of Error</div>
            </div>
          </div>
        </BlueprintCard>
      </div>
    </div>
  );

  // Render A/B testing
  const renderABTesting = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[var(--ink)]">Automated A/B Testing</h2>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            AI-powered testing to optimize campaign performance
          </p>
        </div>

        <BlueprintButton className="flex items-center gap-2">
          <Plus size={16} />
          New Test
        </BlueprintButton>
      </div>

      <div className="space-y-4">
        {abTests.map((test) => (
          <BlueprintCard key={test.id} className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-[var(--ink)]">{test.name}</h3>
                <p className="text-sm text-[var(--ink-muted)]">{test.description}</p>
              </div>

              <BlueprintBadge
                variant={test.status === 'running' ? 'default' : test.status === 'completed' ? 'success' : 'default'}
                size="sm"
              >
                {test.status}
              </BlueprintBadge>
            </div>

            {/* Variants Comparison */}
            <div className="grid grid-cols-2 gap-4 mb-4">
              {test.variants.map((variant, index) => (
                <div key={variant.id} className={cn(
                  "p-4 border rounded-lg",
                  test.winner === variant.id && "border-[var(--success)] bg-[var(--success-light)]/5"
                )}>
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-sm font-medium text-[var(--ink)]">{variant.name}</h4>
                    {test.winner === variant.id && (
                      <BlueprintBadge variant="default" size="sm" className="bg-[var(--success)]">
                        Winner
                      </BlueprintBadge>
                    )}
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-[var(--ink-muted)]">Conversions</span>
                      <span className="font-medium">{variant.performance.conversions}</span>
                    </div>

                    <div className="flex items-center justify-between text-sm">
                      <span className="text-[var(--ink-muted)]">Revenue</span>
                      <span className="font-medium">${variant.performance.revenue.toLocaleString()}</span>
                    </div>

                    <div className="flex items-center justify-between text-sm">
                      <span className="text-[var(--ink-muted)]">Engagement</span>
                      <span className="font-medium">{variant.performance.engagement}%</span>
                    </div>

                    <div className="flex items-center justify-between text-sm">
                      <span className="text-[var(--ink-muted)]">Confidence</span>
                      <div className="flex items-center gap-1">
                        <div className="w-full bg-[var(--structure-subtle)] rounded-full h-2 max-w-[60px]">
                          <div
                            className="bg-[var(--blueprint)] h-2 rounded-full"
                            style={{ width: `${variant.performance.confidence}%` }}
                          />
                        </div>
                        <span className="text-xs">{variant.performance.confidence}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Test Actions */}
            <div className="flex items-center justify-between pt-4 border-t border-[var(--structure-subtle)]">
              <div className="text-sm text-[var(--ink-muted)]">
                Running since {formatDistanceToNow(test.startDate, { addSuffix: true })}
                {test.endDate && (
                  <span> • Completed {formatDistanceToNow(test.endDate, { addSuffix: true })}</span>
                )}
              </div>

              <div className="flex items-center gap-2">
                {test.status === 'running' && (
                  <BlueprintButton variant="blueprint" size="sm">
                    <Pause size={14} />
                    Pause
                  </BlueprintButton>
                )}

                <BlueprintButton variant="blueprint" size="sm">
                  <Eye size={14} />
                  View Details
                </BlueprintButton>
              </div>
            </div>
          </BlueprintCard>
        ))}
      </div>
    </div>
  );

  // Render smart budget optimization
  const renderSmartBudget = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[var(--ink)]">Smart Budget Optimization</h2>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            AI-powered budget allocation for maximum ROI
          </p>
        </div>

        <BlueprintButton className="flex items-center gap-2">
          <RefreshCw size={16} />
          Optimize Now
        </BlueprintButton>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Current Allocations */}
        <BlueprintCard className="p-6">
          <h3 className="text-lg font-semibold text-[var(--ink)] mb-4">Budget Allocations</h3>

          <div className="space-y-4">
            {smartBudget.allocations.map((allocation) => (
              <div key={allocation.moveType} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-[var(--ink)] capitalize">
                    {allocation.moveType} Marketing
                  </span>
                  <span className="text-sm text-[var(--ink-muted)]">
                    ROI: {allocation.roi}x
                  </span>
                </div>

                <div className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-[var(--ink-muted)]">Current</span>
                    <span className="text-[var(--ink)]">${allocation.current.toLocaleString()}</span>
                  </div>

                  <div className="flex items-center justify-between text-xs">
                    <span className="text-[var(--ink-muted)]">Recommended</span>
                    <div className="flex items-center gap-2">
                      <span className="text-[var(--blueprint)] font-medium">
                        ${allocation.recommended.toLocaleString()}
                      </span>
                      {allocation.recommended > allocation.current && (
                        <ArrowUp size={12} className="text-[var(--success)]" />
                      )}
                      {allocation.recommended < allocation.current && (
                        <ArrowDown size={12} className="text-[var(--destructive)]" />
                      )}
                    </div>
                  </div>

                  <div className="w-full bg-[var(--structure-subtle)] rounded-full h-2">
                    <div
                      className="bg-[var(--blueprint)] h-2 rounded-full transition-all"
                      style={{ width: `${(allocation.recommended / smartBudget.totalBudget) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </BlueprintCard>

        {/* Optimization Plan */}
        <BlueprintCard className="p-6">
          <h3 className="text-lg font-semibold text-[var(--ink)] mb-4">Optimization Plan</h3>

          <div className="space-y-4">
            <div className="p-4 bg-[var(--success-light)]/10 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles size={20} className="text-[var(--success)]" />
                <h4 className="text-sm font-semibold text-[var(--success)]">Potential Improvement</h4>
              </div>
              <div className="text-2xl font-bold text-[var(--success)]">
                +{smartBudget.optimization.totalImprovement}%
              </div>
              <p className="text-sm text-[var(--ink-muted)]">
                Additional ${smartBudget.optimization.potentialROI.toLocaleString()} in revenue
              </p>
            </div>

            <div>
              <h4 className="text-sm font-medium text-[var(--ink)] mb-3">Reallocation Plan</h4>
              <div className="space-y-2">
                {smartBudget.optimization.reallocationPlan.map((plan, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-[var(--surface)] rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-[var(--destructive-light)]/10 flex items-center justify-center">
                        <ArrowDown size={16} className="text-[var(--destructive)]" />
                      </div>
                      <div>
                        <div className="text-sm font-medium text-[var(--ink)]">
                          {plan.from} → {plan.to}
                        </div>
                        <div className="text-xs text-[var(--ink-muted)]">
                          ${plan.amount.toLocaleString()}
                        </div>
                      </div>
                    </div>

                    <div className="text-right">
                      <p className="text-xs text-[var(--ink-muted)] max-w-[200px]">
                        {plan.reason}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-4 border-t border-[var(--structure-subtle)]">
              <div className="flex items-center justify-between text-xs text-[var(--ink-muted)]">
                <span>Last optimized</span>
                <span>{formatDistanceToNow(smartBudget.lastOptimized, { addSuffix: true })}</span>
              </div>
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
          <h1 className="text-2xl font-bold text-[var(--ink)]">AI-Powered Optimization</h1>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Advanced AI tools for campaign optimization and automation
          </p>
        </div>

        <div className="flex items-center gap-2">
          <BlueprintButton variant="secondary" className="flex items-center gap-2">
            <Download size={16} />
            Export Report
          </BlueprintButton>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-6 px-6 border-b border-[var(--structure-subtle)]">
        {[
          { id: 'insights', label: 'AI Insights', icon: Brain },
          { id: 'predictions', label: 'Predictive Analytics', icon: TrendingUp },
          { id: 'abtesting', label: 'A/B Testing', icon: Activity },
          { id: 'budget', label: 'Smart Budget', icon: DollarSign }
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
        {activeTab === 'insights' && renderAIInsights()}
        {activeTab === 'predictions' && renderPredictiveAnalytics()}
        {activeTab === 'abtesting' && renderABTesting()}
        {activeTab === 'budget' && renderSmartBudget()}
      </div>
    </div>
  );
}
