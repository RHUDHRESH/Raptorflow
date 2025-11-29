// frontend/pages/strategy/ArchitectDashboard.tsx
// Strategic Architecture Dashboard

import React, { useState, useEffect, useCallback } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Building2, Zap, Target, Users, Plus } from 'lucide-react';
import { LuxeEmptyState, LuxeSkeleton } from '../../components/ui/PremiumUI';
import architectApi, { InitiativeRequest } from '../../api/architect';
import useArchitectSocket from '../../hooks/useArchitectSocket';

interface MetricCard {
  title: string;
  value: string | number;
  description: string;
  icon: React.ReactNode;
  color: string;
}

interface StrategicInitiative {
  initiative_id: string;
  title: string;
  description: string;
  status: string;
  timeline_weeks: number;
  priority: string;
  expected_impact: number;
  created_at: string;
}

interface ArchitectureAnalysis {
  analysis_id: string;
  component_type: string;
  performance_score: number;
  latency_ms: number;
  throughput_rps: number;
  error_rate: number;
  status: string;
  recommendations: string[];
}

interface OptimizationResult {
  optimization_id: string;
  component_type: string;
  improvement_percentage: number;
  estimated_impact: string;
  complexity: string;
  timeframe_days: number;
}

interface GuildGuidance {
  guidance_id: string;
  guild_name: string;
  title: string;
  recommendations: string[];
  implementation_notes: string;
  priority_level: string;
}

const ArchitectDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('initiatives');
  const { status: wsStatus, messages: wsMessages } = useArchitectSocket();
  const [metrics, setMetrics] = useState<Record<string, any>>({
    initiatives_designed: 0,
    initiatives_approved: 0,
    architecture_decisions: 0,
    guild_guidance_given: 0,
  });

  // Initiative State
  const [initiativeForm, setInitiativeForm] = useState({
    title: '',
    description: '',
    timeline_weeks: 8,
    priority: 'high',
  });
  const [initiatives, setInitiatives] = useState<StrategicInitiative[]>([]);
  const [initiativeLoading, setInitiativeLoading] = useState(false);

  // Architecture Analysis State
  const [analysisForm, setAnalysisForm] = useState({
    component_type: 'api_gateway',
    component_name: '',
  });
  const [analyses, setAnalyses] = useState<ArchitectureAnalysis[]>([]);

  // Optimization State
  const [optimizationForm, setOptimizationForm] = useState({
    component_type: 'database',
  });
  const [optimizations, setOptimizations] = useState<OptimizationResult[]>([]);

  // Guild Guidance State
  const [guidanceForm, setGuidanceForm] = useState({
    guild_name: '',
    title: '',
  });
  const [guidances, setGuidances] = useState<GuildGuidance[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Handle WebSocket Messages
  useEffect(() => {
    if (wsMessages.length > 0) {
      const lastMessage = wsMessages[wsMessages.length - 1];
      if (lastMessage.type === 'status_update') {
        setMetrics(lastMessage.data?.metrics || {});
      }
    }
  }, [wsMessages]);

  // Initial Load
  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      try {
        const status = await architectApi.getStatus();
        if (status?.performance) {
          // Map performance data to metrics if needed
        }
      } catch (error) {
        console.error('Failed to load architect data', error);
      } finally {
        setIsLoading(false);
      }
    };
    loadData();
  }, []);

  // Design Initiative
  const handleDesignInitiative = useCallback(async () => {
    setInitiativeLoading(true);
    try {
      const requestData: InitiativeRequest = {
        name: initiativeForm.title,
        objectives: [initiativeForm.description],
        target_guilds: [],
        timeline_weeks: initiativeForm.timeline_weeks,
        success_metrics: {}
      };

      const result = await architectApi.designInitiative(requestData);

      if (result.data) {
          const newInitiative: StrategicInitiative = {
            initiative_id: result.data.initiative_id || 'temp-id',
            title: initiativeForm.title,
            description: initiativeForm.description,
            status: result.data.status || 'planned',
            timeline_weeks: initiativeForm.timeline_weeks,
            priority: initiativeForm.priority,
            expected_impact: result.data.expected_impact || 75,
            created_at: new Date().toISOString(),
          };
          setInitiatives([newInitiative, ...initiatives]);
          setInitiativeForm({
            title: '',
            description: '',
            timeline_weeks: 8,
            priority: 'high',
          });
      }
    } catch (error) {
      console.error('Initiative design error:', error);
    } finally {
      setInitiativeLoading(false);
    }
  }, [initiativeForm, initiatives]);

  // Analyze Architecture
  const handleAnalyzeArchitecture = useCallback(async () => {
    try {
      const result = await architectApi.analyzeArchitecture({
        component: analysisForm.component_name,
        metrics: {} 
      });

      if (result.analysis) {
          const newAnalysis: ArchitectureAnalysis = {
            analysis_id: result.analysis.analysis_id || 'temp-id',
            component_type: analysisForm.component_type,
            performance_score: result.analysis.performance_score || 78,
            latency_ms: result.analysis.latency_ms || 45,
            throughput_rps: result.analysis.throughput_rps || 5000,
            error_rate: result.analysis.error_rate || 0.02,
            status: result.analysis.status || 'completed',
            recommendations: result.analysis.recommendations || [],
          };
          setAnalyses([newAnalysis, ...analyses]);
          setAnalysisForm({
            component_type: 'api_gateway',
            component_name: '',
          });
      }
    } catch (error) {
      console.error('Architecture analysis error:', error);
    }
  }, [analysisForm, analyses]);

  // Optimize Component
  const handleOptimizeComponent = useCallback(async () => {
    try {
      const result = await architectApi.optimizeComponent({
        component_type: optimizationForm.component_type,
        current_metrics: {}
      });

      if (result.optimization_plan) {
          const newOptimization: OptimizationResult = {
            optimization_id: result.optimization_plan.optimization_id || 'temp-id',
            component_type: optimizationForm.component_type,
            improvement_percentage: result.optimization_plan.improvement_percentage || 35,
            estimated_impact: result.optimization_plan.estimated_impact || 'High',
            complexity: result.optimization_plan.complexity || 'Medium',
            timeframe_days: result.optimization_plan.timeframe_days || 14,
          };
          setOptimizations([newOptimization, ...optimizations]);
      }
    } catch (error) {
      console.error('Optimization error:', error);
    }
  }, [optimizationForm, optimizations]);

  // Provide Guild Guidance
  const handleProvideGuidance = useCallback(async () => {
    try {
      const result = await architectApi.provideGuidance({
        guild_name: guidanceForm.guild_name,
        topic: guidanceForm.title
      });

      if (result.guidance) {
          const newGuidance: GuildGuidance = {
            guidance_id: result.guidance.guidance_id || 'temp-id',
            guild_name: guidanceForm.guild_name,
            title: guidanceForm.title,
            recommendations: result.guidance.recommendations || [],
            implementation_notes: result.guidance.implementation_notes || '',
            priority_level: result.guidance.priority_level || 'high',
          };
          setGuidances([newGuidance, ...guidances]);
          setGuidanceForm({
            guild_name: '',
            title: '',
          });
      }
    } catch (error) {
      console.error('Guidance provision error:', error);
    }
  }, [guidanceForm, guidances]);

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

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'approved':
      case 'completed':
        return 'text-emerald-400';
      case 'in_progress':
        return 'text-yellow-400';
      case 'proposed':
        return 'text-blue-400';
      case 'rejected':
        return 'text-red-400';
      default:
        return 'text-slate-400';
    }
  };

  const metricCards: MetricCard[] = [
    {
      title: 'Initiatives Designed',
      value: metrics.initiatives_designed || 0,
      description: 'Total strategic initiatives',
      icon: <Building2 className="w-6 h-6" />,
      color: 'from-purple-900 to-purple-700',
    },
    {
      title: 'Approved',
      value: metrics.initiatives_approved || 0,
      description: 'Approved initiatives',
      icon: <Target className="w-6 h-6" />,
      color: 'from-indigo-900 to-indigo-700',
    },
    {
      title: 'Architecture Decisions',
      value: metrics.architecture_decisions || 0,
      description: 'Total decisions made',
      icon: <Zap className="w-6 h-6" />,
      color: 'from-pink-900 to-pink-700',
    },
    {
      title: 'Guild Guidance',
      value: metrics.guild_guidance_given || 0,
      description: 'Guild recommendations',
      icon: <Users className="w-6 h-6" />,
      color: 'from-violet-900 to-violet-700',
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
                Strategic Architecture
              </h1>
              <p className="text-slate-400">System Design & Strategic Initiatives</p>
            </div>
            <div className="flex items-center gap-3">
              <div
                className={`w-3 h-3 rounded-full ${
                  wsStatus === 'connected' ? 'bg-purple-500 animate-pulse' : 'bg-red-500'
                }`}
              />
              <span className="text-sm text-slate-400">
                {wsStatus === 'connected' ? 'Connected' : 'Disconnected'}
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
            <TabsTrigger value="initiatives" className="data-[state=active]:bg-slate-700">
              Initiatives
            </TabsTrigger>
            <TabsTrigger value="analysis" className="data-[state=active]:bg-slate-700">
              Architecture
            </TabsTrigger>
            <TabsTrigger value="optimization" className="data-[state=active]:bg-slate-700">
              Optimization
            </TabsTrigger>
            <TabsTrigger value="guidance" className="data-[state=active]:bg-slate-700">
              Guild Guidance
            </TabsTrigger>
          </TabsList>

          {/* Initiatives Tab */}
          <TabsContent value="initiatives" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-purple-400">Design Strategic Initiative</CardTitle>
                <CardDescription>Create new strategic planning initiative</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Initiative Title
                  </label>
                  <Input
                    value={initiativeForm.title}
                    onChange={(e) =>
                      setInitiativeForm({ ...initiativeForm, title: e.target.value })
                    }
                    placeholder="e.g., Microservices Migration"
                    className="bg-slate-900 border-slate-700 text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Description
                  </label>
                  <textarea
                    value={initiativeForm.description}
                    onChange={(e) =>
                      setInitiativeForm({ ...initiativeForm, description: e.target.value })
                    }
                    placeholder="Detailed description of the initiative"
                    rows={3}
                    className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Timeline (weeks)
                    </label>
                    <Input
                      type="number"
                      value={initiativeForm.timeline_weeks}
                      onChange={(e) =>
                        setInitiativeForm({
                          ...initiativeForm,
                          timeline_weeks: parseInt(e.target.value),
                        })
                      }
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Priority
                    </label>
                    <select
                      value={initiativeForm.priority}
                      onChange={(e) =>
                        setInitiativeForm({ ...initiativeForm, priority: e.target.value })
                      }
                      className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                    >
                      <option>critical</option>
                      <option>high</option>
                      <option>normal</option>
                      <option>low</option>
                    </select>
                  </div>
                </div>

                <Button
                  onClick={handleDesignInitiative}
                  disabled={initiativeLoading}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white"
                >
                  {initiativeLoading ? 'Designing...' : 'Design Initiative'}
                </Button>
              </CardContent>
            </Card>

            {/* Initiatives List */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-purple-400">Recent Initiatives</h3>
              {isLoading ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <LuxeSkeleton key={i} className="h-24 w-full bg-slate-800/50" />
                  ))}
                </div>
              ) : initiatives.length === 0 ? (
                <LuxeEmptyState
                  icon={Building2}
                  title="No Initiatives Yet"
                  description="Start by designing a new strategic initiative above."
                  className="bg-slate-800/30 border-slate-700 text-slate-300"
                />
              ) : (
                initiatives.map((init) => (
                  <Card key={init.initiative_id} className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="space-y-2">
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-semibold text-white">{init.title}</p>
                            <p className="text-sm text-slate-400">{init.description}</p>
                          </div>
                          <Badge className={getPriorityColor(init.priority)}>
                            {init.priority}
                          </Badge>
                        </div>
                        <div className="grid grid-cols-3 gap-2">
                          <div>
                            <p className="text-xs text-slate-400">Timeline</p>
                            <p className="font-semibold text-slate-200">{init.timeline_weeks}w</p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-400">Impact</p>
                            <p className="font-semibold text-purple-400">{init.expected_impact}%</p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-400">Status</p>
                            <p className={`font-semibold ${getStatusColor(init.status)}`}>
                              {init.status}
                            </p>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          {/* Architecture Analysis Tab */}
          <TabsContent value="analysis" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-indigo-400">Analyze Architecture</CardTitle>
                <CardDescription>Analyze system component performance</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Component Type
                    </label>
                    <select
                      value={analysisForm.component_type}
                      onChange={(e) =>
                        setAnalysisForm({ ...analysisForm, component_type: e.target.value })
                      }
                      className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                    >
                      <option>api_gateway</option>
                      <option>database</option>
                      <option>cache_layer</option>
                      <option>message_queue</option>
                      <option>load_balancer</option>
                      <option>service_mesh</option>
                      <option>storage</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Component Name
                    </label>
                    <Input
                      value={analysisForm.component_name}
                      onChange={(e) =>
                        setAnalysisForm({ ...analysisForm, component_name: e.target.value })
                      }
                      placeholder="e.g., primary-api"
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                </div>

                <Button
                  onClick={handleAnalyzeArchitecture}
                  className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white"
                >
                  Analyze Architecture
                </Button>
              </CardContent>
            </Card>

            {/* Analysis Results */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-indigo-400">Analysis Results</h3>
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
                      <div className="space-y-2">
                        <p className="font-semibold text-white">{analysis.component_type}</p>
                        <div className="grid grid-cols-4 gap-2">
                          <div>
                            <p className="text-xs text-slate-400">Performance</p>
                            <p className="font-semibold text-slate-200">{analysis.performance_score}%</p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-400">Latency</p>
                            <p className="font-semibold text-slate-200">{analysis.latency_ms}ms</p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-400">Throughput</p>
                            <p className="font-semibold text-slate-200">{analysis.throughput_rps} rps</p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-400">Errors</p>
                            <p className="font-semibold text-red-400">{(analysis.error_rate * 100).toFixed(2)}%</p>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          {/* Optimization Tab */}
          <TabsContent value="optimization" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-pink-400">Component Optimization</CardTitle>
                <CardDescription>Get optimization recommendations</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Component to Optimize
                  </label>
                  <select
                    value={optimizationForm.component_type}
                    onChange={(e) =>
                      setOptimizationForm({ ...optimizationForm, component_type: e.target.value })
                    }
                    className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                  >
                    <option>api_gateway</option>
                    <option>database</option>
                    <option>cache_layer</option>
                    <option>message_queue</option>
                    <option>load_balancer</option>
                  </select>
                </div>

                <Button
                  onClick={handleOptimizeComponent}
                  className="w-full bg-gradient-to-r from-pink-600 to-orange-600 hover:from-pink-500 hover:to-orange-500 text-white"
                >
                  Generate Optimization Plan
                </Button>
              </CardContent>
            </Card>

            {/* Optimization List */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-pink-400">Optimization Plans</h3>
              {optimizations.length === 0 ? (
                <Card className="bg-slate-800/30 border-slate-700">
                  <CardContent className="pt-6">
                    <p className="text-slate-400 text-center">No optimization plans yet</p>
                  </CardContent>
                </Card>
              ) : (
                optimizations.map((opt) => (
                  <Card key={opt.optimization_id} className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="space-y-2">
                        <p className="font-semibold text-white">{opt.component_type} Optimization</p>
                        <div className="grid grid-cols-4 gap-2">
                          <div>
                            <p className="text-xs text-slate-400">Improvement</p>
                            <p className="font-semibold text-emerald-400">+{opt.improvement_percentage}%</p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-400">Impact</p>
                            <p className="font-semibold text-slate-200">{opt.estimated_impact}</p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-400">Complexity</p>
                            <p className="font-semibold text-slate-200">{opt.complexity}</p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-400">Timeframe</p>
                            <p className="font-semibold text-slate-200">{opt.timeframe_days}d</p>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          {/* Guild Guidance Tab */}
          <TabsContent value="guidance" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-violet-400">Provide Guild Guidance</CardTitle>
                <CardDescription>Give strategic guidance to guilds</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Guild Name
                    </label>
                    <Input
                      value={guidanceForm.guild_name}
                      onChange={(e) =>
                        setGuidanceForm({ ...guidanceForm, guild_name: e.target.value })
                      }
                      placeholder="e.g., Architects Guild"
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Guidance Title
                    </label>
                    <Input
                      value={guidanceForm.title}
                      onChange={(e) =>
                        setGuidanceForm({ ...guidanceForm, title: e.target.value })
                      }
                      placeholder="Guidance topic"
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                </div>

                <Button
                  onClick={handleProvideGuidance}
                  className="w-full bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500 text-white"
                >
                  Provide Guidance
                </Button>
              </CardContent>
            </Card>

            {/* Guidance List */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-violet-400">Guild Guidance</h3>
              {guidances.length === 0 ? (
                <Card className="bg-slate-800/30 border-slate-700">
                  <CardContent className="pt-6">
                    <p className="text-slate-400 text-center">No guidance provided yet</p>
                  </CardContent>
                </Card>
              ) : (
                guidances.map((guid) => (
                  <Card key={guid.guidance_id} className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="space-y-2">
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-semibold text-white">{guid.guild_name}</p>
                            <p className="text-sm text-slate-400">{guid.title}</p>
                          </div>
                          <Badge className={getPriorityColor(guid.priority_level)}>
                            {guid.priority_level}
                          </Badge>
                        </div>
                        {guid.recommendations.length > 0 && (
                          <div>
                            <p className="text-xs text-slate-400 mb-2">Recommendations</p>
                            <ul className="text-sm text-slate-300 space-y-1">
                              {guid.recommendations.map((rec, idx) => (
                                <li key={idx} className="flex items-start gap-2">
                                  <span className="text-purple-500 mt-0.5">→</span>
                                  <span>{rec}</span>
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

export default ArchitectDashboard;
