// frontend/src/components/council/ArchitectDashboard.tsx
// RaptorFlow Codex - Architect Lord Dashboard
// Phase 2A Week 4 - Council of Lords Frontend

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, CheckCircle, Clock, TrendingUp, Zap } from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { api } from '@/services/api';

interface StrategicInitiative {
  id: string;
  name: string;
  description: string;
  objectives: string[];
  target_guilds: string[];
  timeline_weeks: number;
  status: 'proposed' | 'designing' | 'designed' | 'approved' | 'executing' | 'complete';
  design: any;
  approval_status: Record<string, boolean | null>;
  created_at: string;
  updated_at: string;
}

interface ArchitectMetrics {
  initiatives_designed: number;
  initiatives_approved: number;
  architecture_decisions: number;
  guild_guidance_provided: number;
  supported_guilds: string[];
}

interface InitiativeFormData {
  name: string;
  objectives: string[];
  target_guilds: string[];
  timeline_weeks: number;
  current_objective: string;
  current_guild: string;
}

export const ArchitectDashboard: React.FC = () => {
  const [initiatives, setInitiatives] = useState<StrategicInitiative[]>([]);
  const [metrics, setMetrics] = useState<ArchitectMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'initiatives' | 'analysis' | 'guidance'>('initiatives');
  const [selectedInitiative, setSelectedInitiative] = useState<StrategicInitiative | null>(null);
  const [showNewInitiativeForm, setShowNewInitiativeForm] = useState(false);
  const [formData, setFormData] = useState<InitiativeFormData>({
    name: '',
    objectives: [],
    target_guilds: [],
    timeline_weeks: 4,
    current_objective: '',
    current_guild: ''
  });

  const { data: wsData, send: wsSend, isConnected } = useWebSocket(
    'ws://localhost:8000/ws/lords/architect',
    { reconnectInterval: 3000 }
  );

  // ========================================================================
  // DATA FETCHING
  // ========================================================================

  const fetchInitiatives = useCallback(async () => {
    try {
      const response = await api.get('/lords/architect/initiatives');
      setInitiatives(response.data);
    } catch (error) {
      console.error('Failed to fetch initiatives:', error);
    }
  }, []);

  const fetchMetrics = useCallback(async () => {
    try {
      const response = await api.get('/lords/architect/status');
      setMetrics(response.data.performance);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInitiatives();
    fetchMetrics();

    const interval = setInterval(() => {
      fetchMetrics();
    }, 30000); // Refresh metrics every 30 seconds

    return () => clearInterval(interval);
  }, [fetchInitiatives, fetchMetrics]);

  // Real-time WebSocket updates
  useEffect(() => {
    if (wsData?.type === 'initiative_updated') {
      fetchInitiatives();
      fetchMetrics();
    }
  }, [wsData, fetchInitiatives, fetchMetrics]);

  // ========================================================================
  // HANDLERS
  // ========================================================================

  const handleAddObjective = () => {
    if (formData.current_objective.trim()) {
      setFormData(prev => ({
        ...prev,
        objectives: [...prev.objectives, prev.current_objective],
        current_objective: ''
      }));
    }
  };

  const handleRemoveObjective = (index: number) => {
    setFormData(prev => ({
      ...prev,
      objectives: prev.objectives.filter((_, i) => i !== index)
    }));
  };

  const handleAddGuild = () => {
    if (formData.current_guild.trim() && !formData.target_guilds.includes(formData.current_guild)) {
      setFormData(prev => ({
        ...prev,
        target_guilds: [...prev.target_guilds, prev.current_guild],
        current_guild: ''
      }));
    }
  };

  const handleRemoveGuild = (index: number) => {
    setFormData(prev => ({
      ...prev,
      target_guilds: prev.target_guilds.filter((_, i) => i !== index)
    }));
  };

  const handleSubmitInitiative = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name || formData.objectives.length === 0 || formData.target_guilds.length === 0) {
      alert('Please fill in all required fields');
      return;
    }

    try {
      const response = await api.post('/lords/architect/initiatives/design', {
        name: formData.name,
        objectives: formData.objectives,
        target_guilds: formData.target_guilds,
        timeline_weeks: formData.timeline_weeks
      });

      alert(`Initiative "${formData.name}" designed successfully!`);
      setShowNewInitiativeForm(false);
      setFormData({
        name: '',
        objectives: [],
        target_guilds: [],
        timeline_weeks: 4,
        current_objective: '',
        current_guild: ''
      });

      await fetchInitiatives();
      await fetchMetrics();
    } catch (error) {
      console.error('Failed to create initiative:', error);
      alert('Failed to create initiative');
    }
  };

  const handleApproveInitiative = async (initiativeId: string, approver: string) => {
    try {
      await api.post(`/lords/architect/initiatives/${initiativeId}/approve`, { approver });
      await fetchInitiatives();
    } catch (error) {
      console.error('Failed to approve initiative:', error);
      alert('Failed to approve initiative');
    }
  };

  // ========================================================================
  // STATUS BADGE COLORS
  // ========================================================================

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'proposed':
        return 'bg-gray-100 text-gray-800';
      case 'designing':
        return 'bg-blue-100 text-blue-800';
      case 'designed':
        return 'bg-yellow-100 text-yellow-800';
      case 'approved':
        return 'bg-green-100 text-green-800';
      case 'executing':
        return 'bg-purple-100 text-purple-800';
      case 'complete':
        return 'bg-emerald-100 text-emerald-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <Clock className="w-12 h-12 animate-spin mx-auto mb-4" />
          <p className="text-lg font-semibold">Architect initializing...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 min-h-screen">
      {/* HEADER */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-white flex items-center gap-3">
              <span className="text-5xl">👑</span>
              Architect Lord
            </h1>
            <p className="text-slate-300 mt-2">Strategic Planning & System Architecture</p>
          </div>
          <div className="text-right">
            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg ${isConnected ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'}`}>
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'} animate-pulse`}></div>
              {isConnected ? 'Connected' : 'Disconnected'}
            </div>
          </div>
        </div>
      </div>

      {/* METRICS CARDS */}
      <div className="grid grid-cols-4 gap-4">
        <MetricCard
          icon={<TrendingUp className="w-6 h-6" />}
          label="Initiatives Designed"
          value={metrics?.initiatives_designed || 0}
          color="from-blue-600 to-blue-400"
        />
        <MetricCard
          icon={<CheckCircle className="w-6 h-6" />}
          label="Approved"
          value={metrics?.initiatives_approved || 0}
          color="from-green-600 to-green-400"
        />
        <MetricCard
          icon={<Zap className="w-6 h-6" />}
          label="Architecture Decisions"
          value={metrics?.architecture_decisions || 0}
          color="from-yellow-600 to-yellow-400"
        />
        <MetricCard
          icon={<AlertCircle className="w-6 h-6" />}
          label="Guidance Provided"
          value={metrics?.guild_guidance_provided || 0}
          color="from-purple-600 to-purple-400"
        />
      </div>

      {/* TABS */}
      <div className="border-b border-slate-700">
        <div className="flex gap-4">
          {(['initiatives', 'analysis', 'guidance'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-3 font-semibold transition-all ${
                activeTab === tab
                  ? 'border-b-2 border-blue-500 text-blue-400'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {tab === 'initiatives' && '📋 Initiatives'}
              {tab === 'analysis' && '🔍 Analysis'}
              {tab === 'guidance' && '📖 Guidance'}
            </button>
          ))}
        </div>
      </div>

      {/* TAB CONTENT */}
      <div>
        {/* INITIATIVES TAB */}
        {activeTab === 'initiatives' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-white">Strategic Initiatives</h2>
              <Button
                onClick={() => setShowNewInitiativeForm(!showNewInitiativeForm)}
                className="bg-blue-600 hover:bg-blue-700 text-white"
              >
                {showNewInitiativeForm ? '✕ Cancel' : '+ New Initiative'}
              </Button>
            </div>

            {/* NEW INITIATIVE FORM */}
            {showNewInitiativeForm && (
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Design New Initiative</CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmitInitiative} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Initiative Name *
                      </label>
                      <Input
                        placeholder="e.g., Q2 Market Expansion"
                        value={formData.name}
                        onChange={e => setFormData(prev => ({ ...prev, name: e.target.value }))}
                        className="bg-slate-700 border-slate-600 text-white placeholder-slate-400"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Objectives *
                      </label>
                      <div className="flex gap-2 mb-2">
                        <Input
                          placeholder="Add objective"
                          value={formData.current_objective}
                          onChange={e => setFormData(prev => ({ ...prev, current_objective: e.target.value }))}
                          className="bg-slate-700 border-slate-600 text-white placeholder-slate-400"
                          onKeyPress={e => {
                            if (e.key === 'Enter') {
                              e.preventDefault();
                              handleAddObjective();
                            }
                          }}
                        />
                        <Button
                          type="button"
                          onClick={handleAddObjective}
                          className="bg-slate-700 hover:bg-slate-600"
                        >
                          Add
                        </Button>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {formData.objectives.map((obj, idx) => (
                          <Badge
                            key={idx}
                            variant="secondary"
                            className="bg-blue-900 text-blue-200 cursor-pointer"
                            onClick={() => handleRemoveObjective(idx)}
                          >
                            {obj} ×
                          </Badge>
                        ))}
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Target Guilds *
                      </label>
                      <div className="flex gap-2 mb-2">
                        <select
                          value={formData.current_guild}
                          onChange={e => setFormData(prev => ({ ...prev, current_guild: e.target.value }))}
                          className="bg-slate-700 border border-slate-600 text-white px-3 py-2 rounded"
                        >
                          <option value="">Select guild</option>
                          <option value="research">Research Guild</option>
                          <option value="muse">Muse Guild</option>
                          <option value="matrix">Matrix Guild</option>
                          <option value="guardian">Guardian Guild</option>
                        </select>
                        <Button
                          type="button"
                          onClick={handleAddGuild}
                          className="bg-slate-700 hover:bg-slate-600"
                        >
                          Add
                        </Button>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {formData.target_guilds.map((guild, idx) => (
                          <Badge
                            key={idx}
                            variant="secondary"
                            className="bg-green-900 text-green-200 cursor-pointer"
                            onClick={() => handleRemoveGuild(idx)}
                          >
                            {guild} ×
                          </Badge>
                        ))}
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Timeline (weeks)
                      </label>
                      <Input
                        type="number"
                        min="1"
                        max="52"
                        value={formData.timeline_weeks}
                        onChange={e => setFormData(prev => ({ ...prev, timeline_weeks: parseInt(e.target.value) }))}
                        className="bg-slate-700 border-slate-600 text-white"
                      />
                    </div>

                    <Button
                      type="submit"
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold"
                    >
                      Design Initiative
                    </Button>
                  </form>
                </CardContent>
              </Card>
            )}

            {/* INITIATIVES LIST */}
            <div className="grid grid-cols-1 gap-4">
              {initiatives.length === 0 ? (
                <Card className="bg-slate-800 border-slate-700">
                  <CardContent className="text-center py-8">
                    <p className="text-slate-400">No initiatives yet. Create one to get started!</p>
                  </CardContent>
                </Card>
              ) : (
                initiatives.map(initiative => (
                  <InitiativeCard
                    key={initiative.id}
                    initiative={initiative}
                    onApprove={handleApproveInitiative}
                    onClick={() => setSelectedInitiative(initiative)}
                  />
                ))
              )}
            </div>
          </div>
        )}

        {/* ANALYSIS TAB */}
        {activeTab === 'analysis' && (
          <ArchitectureAnalysisTab />
        )}

        {/* GUIDANCE TAB */}
        {activeTab === 'guidance' && (
          <GuidanceTab guilds={metrics?.supported_guilds || []} />
        )}
      </div>

      {/* SELECTED INITIATIVE DETAIL */}
      {selectedInitiative && (
        <InitiativeDetailModal
          initiative={selectedInitiative}
          onClose={() => setSelectedInitiative(null)}
          onApprove={handleApproveInitiative}
        />
      )}
    </div>
  );
};

// ============================================================================
// COMPONENTS
// ============================================================================

interface MetricCardProps {
  icon: React.ReactNode;
  label: string;
  value: number;
  color: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ icon, label, value, color }) => (
  <Card className={`bg-gradient-to-br ${color} border-none shadow-lg`}>
    <CardContent className="pt-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-white/80 text-sm">{label}</p>
          <p className="text-3xl font-bold text-white mt-2">{value}</p>
        </div>
        <div className="text-white/40 text-3xl">{icon}</div>
      </div>
    </CardContent>
  </Card>
);

interface InitiativeCardProps {
  initiative: StrategicInitiative;
  onApprove: (id: string, approver: string) => Promise<void>;
  onClick: () => void;
}

const InitiativeCard: React.FC<InitiativeCardProps> = ({ initiative, onApprove, onClick }) => {
  const getProgressWidth = () => {
    const statuses = ['proposed', 'designing', 'designed', 'approved', 'executing', 'complete'];
    const currentIndex = statuses.indexOf(initiative.status);
    return ((currentIndex + 1) / statuses.length) * 100;
  };

  return (
    <Card
      className="bg-slate-800 border-slate-700 cursor-pointer hover:border-slate-500 transition-all"
      onClick={onClick}
    >
      <CardHeader className="pb-3">
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-white text-xl">{initiative.name}</CardTitle>
            <p className="text-slate-400 text-sm mt-1">{initiative.description}</p>
          </div>
          <Badge className={getStatusColor(initiative.status)}>
            {initiative.status}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <div className="flex justify-between items-center mb-2">
            <p className="text-slate-400 text-sm">Progress</p>
            <p className="text-white text-sm font-semibold">{Math.round(getProgressWidth())}%</p>
          </div>
          <div className="bg-slate-700 rounded-full h-2 overflow-hidden">
            <div
              className="bg-gradient-to-r from-blue-500 to-blue-400 h-full rounded-full transition-all duration-500"
              style={{ width: `${getProgressWidth()}%` }}
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-slate-400">Objectives</p>
            <p className="text-white font-semibold">{initiative.objectives.length}</p>
          </div>
          <div>
            <p className="text-slate-400">Guilds</p>
            <p className="text-white font-semibold">{initiative.target_guilds.length}</p>
          </div>
        </div>

        {initiative.status === 'designed' && (
          <div className="flex gap-2 pt-2">
            {['architecture', 'cognition', 'strategos'].map(approver => (
              <Button
                key={approver}
                size="sm"
                onClick={e => {
                  e.stopPropagation();
                  onApprove(initiative.id, approver);
                }}
                disabled={initiative.approval_status[approver] === true}
                className={`flex-1 ${
                  initiative.approval_status[approver] === true
                    ? 'bg-green-900 text-green-200'
                    : 'bg-slate-700 hover:bg-slate-600 text-white'
                }`}
              >
                {initiative.approval_status[approver] === true ? '✓' : 'Approve'} {approver}
              </Button>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

interface InitiativeDetailModalProps {
  initiative: StrategicInitiative;
  onClose: () => void;
  onApprove: (id: string, approver: string) => Promise<void>;
}

const InitiativeDetailModal: React.FC<InitiativeDetailModalProps> = ({
  initiative,
  onClose,
  onApprove
}) => (
  <div
    className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    onClick={onClose}
  >
    <Card
      className="bg-slate-800 border-slate-700 w-full max-w-4xl max-h-[90vh] overflow-y-auto"
      onClick={e => e.stopPropagation()}
    >
      <CardHeader>
        <div className="flex justify-between items-start">
          <CardTitle className="text-white text-2xl">{initiative.name}</CardTitle>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white text-2xl"
          >
            ×
          </button>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <div>
          <h3 className="text-white font-semibold mb-3">Objectives</h3>
          <ul className="list-disc list-inside text-slate-300 space-y-2">
            {initiative.objectives.map((obj, idx) => (
              <li key={idx}>{obj}</li>
            ))}
          </ul>
        </div>

        <div>
          <h3 className="text-white font-semibold mb-3">Involved Guilds</h3>
          <div className="flex flex-wrap gap-2">
            {initiative.target_guilds.map((guild, idx) => (
              <Badge key={idx} className="bg-blue-900 text-blue-200">
                {guild}
              </Badge>
            ))}
          </div>
        </div>

        {initiative.design && Object.keys(initiative.design).length > 0 && (
          <div>
            <h3 className="text-white font-semibold mb-3">Design</h3>
            <pre className="bg-slate-900 text-slate-300 p-4 rounded overflow-auto text-sm">
              {JSON.stringify(initiative.design, null, 2)}
            </pre>
          </div>
        )}
      </CardContent>
    </Card>
  </div>
);

// ARCHITECTURE ANALYSIS TAB
interface ArchitectureAnalysisState {
  component: string;
  metrics: {
    latency_ms: number;
    throughput_rps: number;
    error_rate: number;
    cpu_percent: number;
    memory_percent: number;
  };
  analysis: any;
  loading: boolean;
  submitted: boolean;
}

const ArchitectureAnalysisTab: React.FC = () => {
  const [state, setState] = useState<ArchitectureAnalysisState>({
    component: '',
    metrics: {
      latency_ms: 0,
      throughput_rps: 0,
      error_rate: 0,
      cpu_percent: 0,
      memory_percent: 0
    },
    analysis: null,
    loading: false,
    submitted: false
  });

  const componentTypes = ['api', 'database', 'message_bus', 'agent_system', 'knowledge_base', 'cache', 'monitoring'];

  const handleMetricChange = (key: keyof typeof state.metrics, value: number) => {
    setState(prev => ({
      ...prev,
      metrics: { ...prev.metrics, [key]: value }
    }));
  };

  const handleAnalyze = async () => {
    if (!state.component) {
      alert('Please select a component');
      return;
    }

    setState(prev => ({ ...prev, loading: true }));
    try {
      const response = await api.post('/lords/architect/architecture/analyze', {
        component: state.component,
        metrics: state.metrics
      });
      setState(prev => ({
        ...prev,
        analysis: response.data.analysis,
        submitted: true
      }));
    } catch (error) {
      console.error('Analysis failed:', error);
      alert('Failed to analyze architecture');
    } finally {
      setState(prev => ({ ...prev, loading: false }));
    }
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        {/* Component Selection */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white text-lg">Component</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <select
              value={state.component}
              onChange={(e) => setState(prev => ({ ...prev, component: e.target.value }))}
              className="w-full px-3 py-2 bg-slate-900 text-white rounded border border-slate-600 focus:border-blue-500"
            >
              <option value="">Select a component...</option>
              {componentTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </CardContent>
        </Card>

        {/* Quick Metrics */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white text-lg">Performance Metrics</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div>
              <label className="text-slate-300 text-sm">Latency (ms)</label>
              <Input
                type="number"
                value={state.metrics.latency_ms}
                onChange={(e) => handleMetricChange('latency_ms', Number(e.target.value))}
                className="bg-slate-900 border-slate-600 text-white"
              />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Metrics */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white text-lg">System Metrics</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-5 gap-4">
          <div>
            <label className="text-slate-300 text-sm block mb-1">Throughput (rps)</label>
            <Input
              type="number"
              value={state.metrics.throughput_rps}
              onChange={(e) => handleMetricChange('throughput_rps', Number(e.target.value))}
              className="bg-slate-900 border-slate-600 text-white"
            />
          </div>
          <div>
            <label className="text-slate-300 text-sm block mb-1">Error Rate (%)</label>
            <Input
              type="number"
              value={state.metrics.error_rate}
              onChange={(e) => handleMetricChange('error_rate', Number(e.target.value))}
              className="bg-slate-900 border-slate-600 text-white"
              step="0.1"
            />
          </div>
          <div>
            <label className="text-slate-300 text-sm block mb-1">CPU (%)</label>
            <Input
              type="number"
              value={state.metrics.cpu_percent}
              onChange={(e) => handleMetricChange('cpu_percent', Number(e.target.value))}
              className="bg-slate-900 border-slate-600 text-white"
            />
          </div>
          <div>
            <label className="text-slate-300 text-sm block mb-1">Memory (%)</label>
            <Input
              type="number"
              value={state.metrics.memory_percent}
              onChange={(e) => handleMetricChange('memory_percent', Number(e.target.value))}
              className="bg-slate-900 border-slate-600 text-white"
            />
          </div>
          <div className="flex items-end">
            <Button
              onClick={handleAnalyze}
              disabled={state.loading || !state.component}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
            >
              {state.loading ? 'Analyzing...' : 'Analyze'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {state.submitted && state.analysis && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white text-lg flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-blue-400" />
              Analysis Results
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {state.analysis.issues && state.analysis.issues.length > 0 && (
              <div>
                <h4 className="text-white font-semibold mb-2 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-red-400" />
                  Issues Found
                </h4>
                <ul className="space-y-2">
                  {state.analysis.issues.map((issue: string, idx: number) => (
                    <li key={idx} className="text-slate-300 text-sm flex gap-2">
                      <span className="text-red-400">●</span>
                      {issue}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {state.analysis.recommendations && (
              <div>
                <h4 className="text-white font-semibold mb-2 flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-400" />
                  Recommendations
                </h4>
                <ul className="space-y-2">
                  {state.analysis.recommendations.map((rec: string, idx: number) => (
                    <li key={idx} className="text-slate-300 text-sm flex gap-2">
                      <span className="text-green-400">✓</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

// GUILD GUIDANCE TAB
interface GuidanceState {
  selectedGuild: string;
  topic: string;
  guidance: any;
  loading: boolean;
  submitted: boolean;
  allGuidance: Record<string, any>;
}

const GuidanceTab: React.FC<{ guilds: string[] }> = ({ guilds }) => {
  const [state, setState] = useState<GuidanceState>({
    selectedGuild: '',
    topic: '',
    guidance: null,
    loading: false,
    submitted: false,
    allGuidance: {}
  });

  const topics = ['research', 'creative', 'execution'];

  const handleProvideGuidance = async () => {
    if (!state.selectedGuild || !state.topic) {
      alert('Please select a guild and topic');
      return;
    }

    setState(prev => ({ ...prev, loading: true }));
    try {
      const response = await api.post('/lords/architect/guidance/provide', {
        guild_name: state.selectedGuild,
        topic: state.topic
      });
      setState(prev => ({
        ...prev,
        guidance: response.data.guidance,
        submitted: true,
        allGuidance: {
          ...prev.allGuidance,
          [state.selectedGuild]: response.data.guidance
        }
      }));
    } catch (error) {
      console.error('Guidance provision failed:', error);
      alert('Failed to provide guidance');
    } finally {
      setState(prev => ({ ...prev, loading: false }));
    }
  };

  return (
    <div className="space-y-4">
      {/* Guidance Selection */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white text-lg">Provide Guidance</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-3 gap-4">
          <div>
            <label className="text-slate-300 text-sm block mb-2">Select Guild</label>
            <select
              value={state.selectedGuild}
              onChange={(e) => setState(prev => ({ ...prev, selectedGuild: e.target.value }))}
              className="w-full px-3 py-2 bg-slate-900 text-white rounded border border-slate-600 focus:border-blue-500"
            >
              <option value="">Choose a guild...</option>
              {guilds.map(guild => (
                <option key={guild} value={guild}>{guild}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-slate-300 text-sm block mb-2">Topic</label>
            <select
              value={state.topic}
              onChange={(e) => setState(prev => ({ ...prev, topic: e.target.value }))}
              className="w-full px-3 py-2 bg-slate-900 text-white rounded border border-slate-600 focus:border-blue-500"
            >
              <option value="">Choose topic...</option>
              {topics.map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <Button
              onClick={handleProvideGuidance}
              disabled={state.loading || !state.selectedGuild || !state.topic}
              className="w-full bg-green-600 hover:bg-green-700 text-white"
            >
              {state.loading ? 'Generating...' : 'Generate Guidance'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Current Guidance */}
      {state.submitted && state.guidance && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white text-lg">Guidance for {state.selectedGuild}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-slate-200 whitespace-pre-wrap">{state.guidance}</div>
          </CardContent>
        </Card>
      )}

      {/* All Guidance */}
      {Object.keys(state.allGuidance).length > 0 && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white text-lg">Guidance History</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(state.allGuidance).map(([guild, guidance]) => (
                <div key={guild} className="border-l-2 border-blue-500 pl-4">
                  <h4 className="text-white font-semibold mb-2">{guild}</h4>
                  <p className="text-slate-300 text-sm">{guidance}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

