// frontend/pages/strategy/SeerDashboard.tsx
// RaptorFlow Codex - Seer Lord Dashboard
// Phase 2A Week 6 - Trend Prediction & Market Intelligence

import React, { useState, useEffect, useCallback } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, Eye, BarChart3, Lightbulb, AlertTriangle } from 'lucide-react';

interface MetricCard {
  title: string;
  value: string | number;
  description: string;
  icon: React.ReactNode;
  color: string;
}

interface TrendPrediction {
  prediction_id: string;
  metric_name: string;
  current_value: number;
  trend_direction: string;
  confidence: number;
  forecast_type: string;
  predicted_values: number[];
  created_at: string;
}

interface MarketIntelligence {
  intelligence_id: string;
  intelligence_type: string;
  title: string;
  summary: string;
  impact_score: number;
  relevance_score: number;
  threat_level: string;
  key_insights: string[];
  action_items: string[];
  created_at: string;
}

interface PerformanceAnalysis {
  analysis_id: string;
  scope: string;
  scope_id: string;
  performance_score: number;
  trend_analysis: Record<string, string>;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
}

interface StrategicRecommendation {
  recommendation_id: string;
  title: string;
  description: string;
  priority: string;
  expected_impact: number;
  implementation_effort: number;
  success_probability: number;
  supporting_insights: string[];
}

const SeerDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('trends');
  const [wsConnected, setWsConnected] = useState(false);
  const [metrics, setMetrics] = useState<Record<string, any>>({
    predictions_made: 0,
    intelligence_gathered: 0,
    recommendations_generated: 0,
    average_confidence: 0,
  });

  // Trend Prediction State
  const [trendForm, setTrendForm] = useState({
    metric_name: '',
    historical_values: [50, 55, 60, 65, 70],
    forecast_period_days: 30,
    forecast_type: 'linear',
  });
  const [predictions, setPredictions] = useState<TrendPrediction[]>([]);
  const [trendLoading, setTrendLoading] = useState(false);

  // Market Intelligence State
  const [intelligenceForm, setIntelligenceForm] = useState({
    intelligence_type: 'market_trend',
    title: '',
    summary: '',
    source: 'internal_analysis',
    key_insights: [],
  });
  const [intelligence, setIntelligence] = useState<MarketIntelligence[]>([]);

  // Performance Analysis State
  const [analysisForm, setAnalysisForm] = useState({
    scope: 'campaign',
    scope_id: '',
    metrics: { engagement: 75, reach: 85, conversion: 65, roi: 80 },
  });
  const [analyses, setAnalyses] = useState<PerformanceAnalysis[]>([]);

  // Recommendation State
  const [recommendationForm, setRecommendationForm] = useState({
    title: '',
    description: '',
    priority: 'normal',
    supporting_insights: [],
    required_resources: {},
  });
  const [recommendations, setRecommendations] = useState<StrategicRecommendation[]>([]);

  // WebSocket Connection
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/lords/seer`);

    ws.onopen = () => {
      console.log('✅ Connected to Seer WebSocket');
      setWsConnected(true);
      ws.send(JSON.stringify({ type: 'subscribe', lord: 'seer' }));
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.type === 'status_update') {
          setMetrics(message.data?.metrics || {});
        }
      } catch (error) {
        console.error('WebSocket message error:', error);
      }
    };

    ws.onclose = () => {
      console.log('❌ Disconnected from Seer WebSocket');
      setWsConnected(false);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => ws.close();
  }, []);

  // Predict Trend
  const handlePredictTrend = useCallback(async () => {
    setTrendLoading(true);
    try {
      const response = await fetch('/lords/seer/predict-trend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(trendForm),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.data) {
          const newPrediction: TrendPrediction = {
            prediction_id: result.data.prediction_id,
            metric_name: result.data.metric_name,
            current_value: result.data.current_value,
            trend_direction: result.data.trend_direction,
            confidence: result.data.confidence,
            forecast_type: result.data.forecast_type,
            predicted_values: result.data.predicted_values,
            created_at: new Date().toISOString(),
          };
          setPredictions([newPrediction, ...predictions]);
        }
      }
    } catch (error) {
      console.error('Trend prediction error:', error);
    } finally {
      setTrendLoading(false);
    }
  }, [trendForm, predictions]);

  // Gather Intelligence
  const handleGatherIntelligence = useCallback(async () => {
    try {
      const response = await fetch('/lords/seer/intelligence/gather', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(intelligenceForm),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.data) {
          const newIntel: MarketIntelligence = {
            intelligence_id: result.data.intelligence_id,
            intelligence_type: result.data.intelligence_type,
            title: result.data.title,
            summary: intelligenceForm.summary,
            impact_score: result.data.impact_score,
            relevance_score: result.data.relevance_score,
            threat_level: result.data.threat_level,
            key_insights: result.data.key_insights,
            action_items: result.data.action_items,
            created_at: new Date().toISOString(),
          };
          setIntelligence([newIntel, ...intelligence]);
        }
      }
    } catch (error) {
      console.error('Intelligence gathering error:', error);
    }
  }, [intelligenceForm, intelligence]);

  // Analyze Performance
  const handleAnalyzePerformance = useCallback(async () => {
    try {
      const response = await fetch('/lords/seer/analysis/performance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(analysisForm),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.data) {
          const newAnalysis: PerformanceAnalysis = {
            analysis_id: result.data.analysis_id,
            scope: result.data.scope,
            scope_id: result.data.scope_id,
            performance_score: result.data.performance_score,
            trend_analysis: result.data.trend_analysis,
            strengths: result.data.strengths,
            weaknesses: result.data.weaknesses,
            recommendations: result.data.recommendations,
          };
          setAnalyses([newAnalysis, ...analyses]);
        }
      }
    } catch (error) {
      console.error('Performance analysis error:', error);
    }
  }, [analysisForm, analyses]);

  // Generate Recommendation
  const handleGenerateRecommendation = useCallback(async () => {
    try {
      const response = await fetch('/lords/seer/recommendations/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(recommendationForm),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.data) {
          const newRec: StrategicRecommendation = {
            recommendation_id: result.data.recommendation_id,
            title: result.data.title,
            description: recommendationForm.description,
            priority: result.data.priority,
            expected_impact: result.data.expected_impact,
            implementation_effort: result.data.implementation_effort,
            success_probability: result.data.success_probability,
            supporting_insights: result.data.supporting_insights,
          };
          setRecommendations([newRec, ...recommendations]);
        }
      }
    } catch (error) {
      console.error('Recommendation generation error:', error);
    }
  }, [recommendationForm, recommendations]);

  const getTrendColor = (direction: string): string => {
    switch (direction) {
      case 'strongly_up':
        return 'text-emerald-500';
      case 'up':
        return 'text-green-500';
      case 'stable':
        return 'text-blue-500';
      case 'down':
        return 'text-amber-500';
      case 'strongly_down':
        return 'text-red-500';
      default:
        return 'text-slate-400';
    }
  };

  const getTrendIcon = (direction: string) => {
    switch (direction) {
      case 'strongly_up':
      case 'up':
        return '📈';
      case 'stable':
        return '➡️';
      case 'down':
      case 'strongly_down':
        return '📉';
      default:
        return '❓';
    }
  };

  const getPriorityColor = (priority: string): string => {
    switch (priority) {
      case 'critical':
        return 'bg-red-900 text-red-200';
      case 'high':
        return 'bg-orange-900 text-orange-200';
      case 'normal':
        return 'bg-blue-900 text-blue-200';
      case 'low':
        return 'bg-green-900 text-green-200';
      default:
        return 'bg-slate-700 text-slate-200';
    }
  };

  const getThreatColor = (threat: string): string => {
    switch (threat) {
      case 'critical':
        return 'bg-red-900 text-red-200';
      case 'high':
        return 'bg-orange-900 text-orange-200';
      case 'medium':
        return 'bg-yellow-900 text-yellow-200';
      case 'low':
        return 'bg-green-900 text-green-200';
      default:
        return 'bg-slate-700 text-slate-200';
    }
  };

  const metricCards: MetricCard[] = [
    {
      title: 'Predictions Made',
      value: metrics.predictions_made || 0,
      description: 'Total trend predictions',
      icon: <TrendingUp className="w-6 h-6" />,
      color: 'from-purple-900 to-purple-700',
    },
    {
      title: 'Intelligence Gathered',
      value: metrics.intelligence_gathered || 0,
      description: 'Market intelligence reports',
      icon: <Eye className="w-6 h-6" />,
      color: 'from-indigo-900 to-indigo-700',
    },
    {
      title: 'Recommendations',
      value: metrics.recommendations_generated || 0,
      description: 'Strategic recommendations',
      icon: <Lightbulb className="w-6 h-6" />,
      color: 'from-amber-900 to-amber-700',
    },
    {
      title: 'Avg Confidence',
      value: `${(metrics.average_confidence || 0).toFixed(0)}%`,
      description: 'Prediction confidence level',
      icon: <BarChart3 className="w-6 h-6" />,
      color: 'from-teal-900 to-teal-700',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-indigo-400 bg-clip-text text-transparent mb-2">
                🔮 Seer Lord
              </h1>
              <p className="text-slate-400">Trend Prediction & Market Intelligence</p>
            </div>
            <div className="flex items-center gap-3">
              <div
                className={`w-3 h-3 rounded-full ${
                  wsConnected ? 'bg-purple-500 animate-pulse' : 'bg-red-500'
                }`}
              />
              <span className="text-sm text-slate-400">
                {wsConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>

          {/* Metric Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {metricCards.map((card, index) => (
              <Card
                key={index}
                className={`bg-gradient-to-br ${card.color} border-0 text-white overflow-hidden`}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium">{card.title}</CardTitle>
                    <div className="opacity-80">{card.icon}</div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold mb-2">{card.value}</div>
                  <p className="text-xs opacity-80">{card.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4 bg-slate-800/50 border border-slate-700">
            <TabsTrigger value="trends" className="data-[state=active]:bg-slate-700">
              Trend Prediction
            </TabsTrigger>
            <TabsTrigger value="intelligence" className="data-[state=active]:bg-slate-700">
              Market Intelligence
            </TabsTrigger>
            <TabsTrigger value="analysis" className="data-[state=active]:bg-slate-700">
              Performance
            </TabsTrigger>
            <TabsTrigger value="recommendations" className="data-[state=active]:bg-slate-700">
              Recommendations
            </TabsTrigger>
          </TabsList>

          {/* Trend Prediction Tab */}
          <TabsContent value="trends" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-purple-400">Trend Prediction Form</CardTitle>
                <CardDescription>Predict market and metric trends</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Metric Name
                    </label>
                    <Input
                      value={trendForm.metric_name}
                      onChange={(e) =>
                        setTrendForm({ ...trendForm, metric_name: e.target.value })
                      }
                      placeholder="e.g., market_growth"
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Forecast Type
                    </label>
                    <select
                      value={trendForm.forecast_type}
                      onChange={(e) =>
                        setTrendForm({ ...trendForm, forecast_type: e.target.value })
                      }
                      className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                    >
                      <option>linear</option>
                      <option>exponential</option>
                      <option>polynomial</option>
                      <option>seasonal</option>
                      <option>cyclical</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Forecast Period (days)
                  </label>
                  <Input
                    type="number"
                    value={trendForm.forecast_period_days}
                    onChange={(e) =>
                      setTrendForm({
                        ...trendForm,
                        forecast_period_days: parseInt(e.target.value),
                      })
                    }
                    className="bg-slate-900 border-slate-700 text-white"
                  />
                </div>

                <Button
                  onClick={handlePredictTrend}
                  disabled={trendLoading}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white"
                >
                  {trendLoading ? 'Predicting...' : 'Predict Trend'}
                </Button>
              </CardContent>
            </Card>

            {/* Predictions List */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-purple-400">Recent Predictions</h3>
              {predictions.length === 0 ? (
                <Card className="bg-slate-800/30 border-slate-700">
                  <CardContent className="pt-6">
                    <p className="text-slate-400 text-center">No predictions yet</p>
                  </CardContent>
                </Card>
              ) : (
                predictions.map((pred) => (
                  <Card key={pred.prediction_id} className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="space-y-3">
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-semibold text-white">{pred.metric_name}</p>
                            <p className="text-sm text-slate-400">{pred.forecast_type} forecast</p>
                          </div>
                          <div className="text-right">
                            <p className={`text-2xl mb-1 ${getTrendColor(pred.trend_direction)}`}>
                              {getTrendIcon(pred.trend_direction)}
                            </p>
                            <Badge className="bg-slate-700 text-slate-200">
                              {pred.trend_direction.replace('_', ' ')}
                            </Badge>
                          </div>
                        </div>

                        <div className="grid grid-cols-3 gap-4">
                          <div>
                            <p className="text-xs text-slate-400 mb-1">Current Value</p>
                            <p className="font-semibold text-white">{pred.current_value.toFixed(2)}</p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-400 mb-1">Confidence</p>
                            <p className="font-semibold text-purple-400">{pred.confidence.toFixed(0)}%</p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-400 mb-1">Period</p>
                            <p className="font-semibold text-white">{pred.forecast_period_days}d</p>
                          </div>
                        </div>

                        {pred.predicted_values.length > 0 && (
                          <div>
                            <p className="text-xs text-slate-400 mb-2">Forecast Values</p>
                            <div className="flex gap-1 flex-wrap">
                              {pred.predicted_values.slice(0, 10).map((val, idx) => (
                                <span key={idx} className="text-xs bg-slate-700 text-slate-200 px-2 py-1 rounded">
                                  {val.toFixed(1)}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          {/* Market Intelligence Tab */}
          <TabsContent value="intelligence" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-indigo-400">Gather Market Intelligence</CardTitle>
                <CardDescription>Collect competitive and market insights</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Intelligence Type
                    </label>
                    <select
                      value={intelligenceForm.intelligence_type}
                      onChange={(e) =>
                        setIntelligenceForm({
                          ...intelligenceForm,
                          intelligence_type: e.target.value,
                        })
                      }
                      className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                    >
                      <option>competitive</option>
                      <option>market_trend</option>
                      <option>customer_behavior</option>
                      <option>technology</option>
                      <option>regulatory</option>
                      <option>economic</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Title
                    </label>
                    <Input
                      value={intelligenceForm.title}
                      onChange={(e) =>
                        setIntelligenceForm({ ...intelligenceForm, title: e.target.value })
                      }
                      placeholder="Intelligence title"
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Summary
                  </label>
                  <textarea
                    value={intelligenceForm.summary}
                    onChange={(e) =>
                      setIntelligenceForm({ ...intelligenceForm, summary: e.target.value })
                    }
                    placeholder="Detailed summary of intelligence"
                    rows={3}
                    className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                  />
                </div>

                <Button
                  onClick={handleGatherIntelligence}
                  className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white"
                >
                  Gather Intelligence
                </Button>
              </CardContent>
            </Card>

            {/* Intelligence List */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-indigo-400">Recent Intelligence</h3>
              {intelligence.length === 0 ? (
                <Card className="bg-slate-800/30 border-slate-700">
                  <CardContent className="pt-6">
                    <p className="text-slate-400 text-center">No intelligence gathered yet</p>
                  </CardContent>
                </Card>
              ) : (
                intelligence.map((intel) => (
                  <Card key={intel.intelligence_id} className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="space-y-3">
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-semibold text-white">{intel.title}</p>
                            <p className="text-sm text-slate-400">{intel.intelligence_type.replace('_', ' ')}</p>
                          </div>
                          <Badge className={getThreatColor(intel.threat_level)}>
                            {intel.threat_level}
                          </Badge>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <p className="text-xs text-slate-400 mb-1">Impact Score</p>
                            <p className="font-semibold text-orange-400">{intel.impact_score.toFixed(0)}/100</p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-400 mb-1">Relevance</p>
                            <p className="font-semibold text-blue-400">{intel.relevance_score.toFixed(0)}/100</p>
                          </div>
                        </div>

                        {intel.key_insights.length > 0 && (
                          <div>
                            <p className="text-sm font-medium text-slate-300 mb-2">Key Insights</p>
                            <ul className="text-sm text-slate-300 space-y-1">
                              {intel.key_insights.map((insight, idx) => (
                                <li key={idx} className="flex items-start gap-2">
                                  <span className="text-yellow-500 mt-0.5">→</span>
                                  <span>{insight}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          {/* Performance Analysis Tab */}
          <TabsContent value="analysis" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-teal-400">Performance Analysis</CardTitle>
                <CardDescription>Analyze campaign, guild, or organizational performance</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Scope
                    </label>
                    <select
                      value={analysisForm.scope}
                      onChange={(e) =>
                        setAnalysisForm({ ...analysisForm, scope: e.target.value })
                      }
                      className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                    >
                      <option>campaign</option>
                      <option>guild</option>
                      <option>organization</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Scope ID
                    </label>
                    <Input
                      value={analysisForm.scope_id}
                      onChange={(e) =>
                        setAnalysisForm({ ...analysisForm, scope_id: e.target.value })
                      }
                      placeholder="e.g., camp_001"
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Performance Metrics
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    {Object.entries(analysisForm.metrics).map(([key, value]) => (
                      <div key={key}>
                        <label className="block text-xs text-slate-400 mb-1 capitalize">
                          {key}
                        </label>
                        <Input
                          type="number"
                          min="0"
                          max="100"
                          value={value}
                          onChange={(e) =>
                            setAnalysisForm({
                              ...analysisForm,
                              metrics: {
                                ...analysisForm.metrics,
                                [key]: parseFloat(e.target.value),
                              },
                            })
                          }
                          className="bg-slate-900 border-slate-700 text-white text-sm"
                        />
                      </div>
                    ))}
                  </div>
                </div>

                <Button
                  onClick={handleAnalyzePerformance}
                  className="w-full bg-gradient-to-r from-teal-600 to-cyan-600 hover:from-teal-500 hover:to-cyan-500 text-white"
                >
                  Analyze Performance
                </Button>
              </CardContent>
            </Card>

            {/* Analysis Results */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-teal-400">Analysis Results</h3>
              {analyses.length === 0 ? (
                <Card className="bg-slate-800/30 border-slate-700">
                  <CardContent className="pt-6">
                    <p className="text-slate-400 text-center">No analyses performed yet</p>
                  </CardContent>
                </Card>
              ) : (
                analyses.map((analysis) => (
                  <Card key={analysis.analysis_id} className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-semibold text-white">
                              {analysis.scope} - {analysis.scope_id}
                            </p>
                          </div>
                          <p className={`text-2xl font-bold ${
                            analysis.performance_score >= 75
                              ? 'text-emerald-500'
                              : analysis.performance_score >= 50
                              ? 'text-yellow-500'
                              : 'text-red-500'
                          }`}>
                            {analysis.performance_score.toFixed(0)}
                          </p>
                        </div>

                        {analysis.strengths.length > 0 && (
                          <div>
                            <p className="text-sm font-medium text-emerald-400 mb-1">Strengths</p>
                            <ul className="text-sm text-slate-300 space-y-1">
                              {analysis.strengths.map((strength, idx) => (
                                <li key={idx} className="flex items-start gap-2">
                                  <span className="text-emerald-500 mt-0.5">✓</span>
                                  <span>{strength}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {analysis.weaknesses.length > 0 && (
                          <div>
                            <p className="text-sm font-medium text-red-400 mb-1">Weaknesses</p>
                            <ul className="text-sm text-slate-300 space-y-1">
                              {analysis.weaknesses.map((weakness, idx) => (
                                <li key={idx} className="flex items-start gap-2">
                                  <span className="text-red-500 mt-0.5">✗</span>
                                  <span>{weakness}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          {/* Recommendations Tab */}
          <TabsContent value="recommendations" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-amber-400">Generate Recommendation</CardTitle>
                <CardDescription>Create strategic recommendations based on analysis</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Title
                  </label>
                  <Input
                    value={recommendationForm.title}
                    onChange={(e) =>
                      setRecommendationForm({ ...recommendationForm, title: e.target.value })
                    }
                    placeholder="Recommendation title"
                    className="bg-slate-900 border-slate-700 text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Description
                  </label>
                  <textarea
                    value={recommendationForm.description}
                    onChange={(e) =>
                      setRecommendationForm({
                        ...recommendationForm,
                        description: e.target.value,
                      })
                    }
                    placeholder="Detailed description"
                    rows={3}
                    className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Priority
                  </label>
                  <select
                    value={recommendationForm.priority}
                    onChange={(e) =>
                      setRecommendationForm({
                        ...recommendationForm,
                        priority: e.target.value,
                      })
                    }
                    className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                  >
                    <option>critical</option>
                    <option>high</option>
                    <option>normal</option>
                    <option>low</option>
                  </select>
                </div>

                <Button
                  onClick={handleGenerateRecommendation}
                  className="w-full bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white"
                >
                  Generate Recommendation
                </Button>
              </CardContent>
            </Card>

            {/* Recommendations List */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-amber-400">Strategic Recommendations</h3>
              {recommendations.length === 0 ? (
                <Card className="bg-slate-800/30 border-slate-700">
                  <CardContent className="pt-6">
                    <p className="text-slate-400 text-center">No recommendations yet</p>
                  </CardContent>
                </Card>
              ) : (
                recommendations.map((rec) => (
                  <Card key={rec.recommendation_id} className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="space-y-3">
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-semibold text-white">{rec.title}</p>
                            <p className="text-sm text-slate-400">{rec.description}</p>
                          </div>
                          <Badge className={getPriorityColor(rec.priority)}>
                            {rec.priority}
                          </Badge>
                        </div>

                        <div className="grid grid-cols-3 gap-4">
                          <div>
                            <p className="text-xs text-slate-400 mb-1">Impact</p>
                            <p className="font-semibold text-emerald-400">{rec.expected_impact.toFixed(0)}%</p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-400 mb-1">Effort</p>
                            <p className="font-semibold text-yellow-400">{rec.implementation_effort.toFixed(0)}%</p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-400 mb-1">Success Prob.</p>
                            <p className="font-semibold text-blue-400">{rec.success_probability.toFixed(0)}%</p>
                          </div>
                        </div>

                        {rec.supporting_insights.length > 0 && (
                          <div>
                            <p className="text-sm font-medium text-slate-300 mb-1">Supporting Insights</p>
                            <ul className="text-sm text-slate-300 space-y-1">
                              {rec.supporting_insights.map((insight, idx) => (
                                <li key={idx} className="flex items-start gap-2">
                                  <span className="text-blue-500 mt-0.5">💡</span>
                                  <span>{insight}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default SeerDashboard;
