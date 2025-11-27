// frontend/src/components/council/CognitionDashboard.tsx
// RaptorFlow Codex - Cognition Lord Dashboard
// Phase 2A Week 4 - Learning, Synthesis, and Decision Support

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { AlertCircle, CheckCircle, TrendingUp, Brain, BookOpen, Target, Clock } from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { api } from '@/services/api';

interface Learning {
  id: string;
  type: string;
  source: string;
  key_insight: string;
  description: string;
  confidence: number;
  created_at: string;
}

interface Synthesis {
  id: string;
  type: string;
  title: string;
  description: string;
  recommendations: string[];
  confidence: number;
  supporting_learnings: number;
  created_at: string;
}

interface Decision {
  id: string;
  title: string;
  description: string;
  recommendation: string;
  confidence: number;
  impact_forecast: Record<string, number>;
  status: string;
  created_at: string;
}

interface CognitionMetrics {
  total_learnings_recorded: number;
  total_syntheses_created: number;
  total_decisions_made: number;
  learning_effectiveness_score: number;
  active_learnings: number;
  active_syntheses: number;
  active_decisions: number;
}

interface TabState {
  learnings: Learning[];
  syntheses: Synthesis[];
  decisions: Decision[];
  mentoring_result: any;
}

export const CognitionDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<CognitionMetrics | null>(null);
  const [tabData, setTabData] = useState<TabState>({
    learnings: [],
    syntheses: [],
    decisions: [],
    mentoring_result: null
  });
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'learning' | 'synthesis' | 'decision' | 'mentoring'>('learning');
  const [showNewLearningForm, setShowNewLearningForm] = useState(false);
  const [showNewSynthesisForm, setShowNewSynthesisForm] = useState(false);

  const { data: wsData, send: wsSend, isConnected } = useWebSocket(
    'ws://localhost:8000/ws/lords/cognition',
    { reconnectInterval: 3000 }
  );

  // ========================================================================
  // DATA FETCHING
  // ========================================================================

  const fetchMetrics = useCallback(async () => {
    try {
      const response = await api.get('/lords/cognition/status');
      setMetrics(response.data.performance);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  }, []);

  const fetchLearnings = useCallback(async () => {
    try {
      const response = await api.get('/lords/cognition/learning/recent?limit=20');
      setTabData(prev => ({ ...prev, learnings: response.data }));
    } catch (error) {
      console.error('Failed to fetch learnings:', error);
    }
  }, []);

  const fetchSyntheses = useCallback(async () => {
    try {
      const response = await api.get('/lords/cognition/synthesis/recent?limit=20');
      setTabData(prev => ({ ...prev, syntheses: response.data }));
    } catch (error) {
      console.error('Failed to fetch syntheses:', error);
    }
  }, []);

  const fetchDecisions = useCallback(async () => {
    try {
      const response = await api.get('/lords/cognition/decisions/recent?limit=20');
      setTabData(prev => ({ ...prev, decisions: response.data }));
    } catch (error) {
      console.error('Failed to fetch decisions:', error);
    }
  }, []);

  useEffect(() => {
    const initializeData = async () => {
      await Promise.all([fetchMetrics(), fetchLearnings(), fetchSyntheses(), fetchDecisions()]);
      setLoading(false);
    };

    initializeData();

    const interval = setInterval(fetchMetrics, 30000);
    return () => clearInterval(interval);
  }, [fetchMetrics, fetchLearnings, fetchSyntheses, fetchDecisions]);

  useEffect(() => {
    if (wsData?.type === 'learning_recorded' || wsData?.type === 'synthesis_created') {
      fetchMetrics();
      if (activeTab === 'learning') fetchLearnings();
      if (activeTab === 'synthesis') fetchSyntheses();
    }
  }, [wsData, activeTab, fetchMetrics, fetchLearnings, fetchSyntheses]);

  // ========================================================================
  // HANDLERS
  // ========================================================================

  const handleRecordLearning = async (learningType: string, source: string, insight: string, description: string) => {
    try {
      await api.post('/lords/cognition/learning/record', {
        learning_type: learningType,
        source: source,
        key_insight: insight,
        description: description,
        confidence: 0.85
      });
      setShowNewLearningForm(false);
      await fetchLearnings();
      await fetchMetrics();
    } catch (error) {
      console.error('Failed to record learning:', error);
      alert('Failed to record learning');
    }
  };

  const handleSynthesizeKnowledge = async (
    synthesisType: string,
    title: string,
    description: string,
    recommendations: string[]
  ) => {
    try {
      // In a real scenario, would select learning IDs from UI
      const learningIds = tabData.learnings.slice(0, 3).map(l => l.id);

      await api.post('/lords/cognition/synthesis/create', {
        synthesis_type: synthesisType,
        title: title,
        description: description,
        learning_ids: learningIds,
        recommendations: recommendations
      });
      setShowNewSynthesisForm(false);
      await fetchSyntheses();
      await fetchMetrics();
    } catch (error) {
      console.error('Failed to synthesize knowledge:', error);
      alert('Failed to synthesize knowledge');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <Clock className="w-12 h-12 animate-spin mx-auto mb-4" />
          <p className="text-lg font-semibold">Cognition initializing...</p>
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
              <span className="text-5xl">🧠</span>
              Cognition Lord
            </h1>
            <p className="text-slate-300 mt-2">Learning, Synthesis & Decision Support</p>
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
          icon={<BookOpen className="w-6 h-6 text-blue-400" />}
          label="Learnings Recorded"
          value={metrics?.total_learnings_recorded || 0}
          subtext={`${metrics?.active_learnings || 0} active`}
          gradient="from-blue-600 to-blue-400"
        />
        <MetricCard
          icon={<Brain className="w-6 h-6 text-purple-400" />}
          label="Syntheses Created"
          value={metrics?.total_syntheses_created || 0}
          subtext={`${metrics?.active_syntheses || 0} active`}
          gradient="from-purple-600 to-purple-400"
        />
        <MetricCard
          icon={<Target className="w-6 h-6 text-green-400" />}
          label="Decisions Made"
          value={metrics?.total_decisions_made || 0}
          subtext={`${metrics?.active_decisions || 0} active`}
          gradient="from-green-600 to-green-400"
        />
        <MetricCard
          icon={<TrendingUp className="w-6 h-6 text-yellow-400" />}
          label="Effectiveness Score"
          value={`${((metrics?.learning_effectiveness_score || 0) * 100).toFixed(1)}%`}
          subtext="Overall quality"
          gradient="from-yellow-600 to-yellow-400"
        />
      </div>

      {/* TAB NAVIGATION */}
      <div className="flex gap-4 border-b border-slate-700">
        <button
          onClick={() => setActiveTab('learning')}
          className={`px-4 py-3 font-semibold transition ${
            activeTab === 'learning'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-slate-400 hover:text-slate-300'
          }`}
        >
          📚 Learning Journal
        </button>
        <button
          onClick={() => setActiveTab('synthesis')}
          className={`px-4 py-3 font-semibold transition ${
            activeTab === 'synthesis'
              ? 'text-purple-400 border-b-2 border-purple-400'
              : 'text-slate-400 hover:text-slate-300'
          }`}
        >
          💡 Knowledge Synthesis
        </button>
        <button
          onClick={() => setActiveTab('decision')}
          className={`px-4 py-3 font-semibold transition ${
            activeTab === 'decision'
              ? 'text-green-400 border-b-2 border-green-400'
              : 'text-slate-400 hover:text-slate-300'
          }`}
        >
          🎯 Decisions
        </button>
        <button
          onClick={() => setActiveTab('mentoring')}
          className={`px-4 py-3 font-semibold transition ${
            activeTab === 'mentoring'
              ? 'text-yellow-400 border-b-2 border-yellow-400'
              : 'text-slate-400 hover:text-slate-300'
          }`}
        >
          🎓 Mentoring
        </button>
      </div>

      {/* TAB CONTENT */}
      <div>
        {activeTab === 'learning' && <LearningTab learnings={tabData.learnings} onRecord={handleRecordLearning} />}
        {activeTab === 'synthesis' && <SynthesisTab syntheses={tabData.syntheses} onSynthesize={handleSynthesizeKnowledge} />}
        {activeTab === 'decision' && <DecisionTab decisions={tabData.decisions} />}
        {activeTab === 'mentoring' && <MentoringTab />}
      </div>
    </div>
  );
};

// ============================================================================
// METRIC CARD COMPONENT
// ============================================================================

interface MetricCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  subtext: string;
  gradient: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ icon, label, value, subtext, gradient }) => (
  <Card className={`bg-gradient-to-br ${gradient} bg-opacity-10 border-0`}>
    <CardContent className="p-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-slate-400 text-sm">{label}</p>
          <p className="text-3xl font-bold text-white mt-2">{value}</p>
          <p className="text-slate-400 text-xs mt-2">{subtext}</p>
        </div>
        <div className="text-4xl opacity-20">{icon}</div>
      </div>
    </CardContent>
  </Card>
);

// ============================================================================
// LEARNING TAB
// ============================================================================

interface LearningTabProps {
  learnings: Learning[];
  onRecord: (type: string, source: string, insight: string, description: string) => void;
}

const LearningTab: React.FC<LearningTabProps> = ({ learnings, onRecord }) => {
  const [formData, setFormData] = useState({
    type: 'success',
    source: '',
    insight: '',
    description: ''
  });

  const handleSubmit = () => {
    if (formData.source && formData.insight) {
      onRecord(formData.type, formData.source, formData.insight, formData.description);
      setFormData({ type: 'success', source: '', insight: '', description: '' });
    }
  };

  const learningTypeColors: Record<string, string> = {
    success: 'bg-green-100 text-green-800',
    failure: 'bg-red-100 text-red-800',
    partial: 'bg-yellow-100 text-yellow-800',
    optimization: 'bg-blue-100 text-blue-800',
    pattern: 'bg-purple-100 text-purple-800',
    risk: 'bg-orange-100 text-orange-800',
    opportunity: 'bg-pink-100 text-pink-800'
  };

  return (
    <div className="space-y-4">
      {/* Recording Form */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white text-lg">Record Learning</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-slate-300 text-sm block mb-2">Learning Type</label>
              <select
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                className="w-full px-3 py-2 bg-slate-900 text-white rounded border border-slate-600 focus:border-blue-500"
              >
                <option value="success">Success</option>
                <option value="failure">Failure</option>
                <option value="partial">Partial Success</option>
                <option value="optimization">Optimization</option>
                <option value="pattern">Pattern</option>
                <option value="risk">Risk</option>
                <option value="opportunity">Opportunity</option>
              </select>
            </div>
            <div>
              <label className="text-slate-300 text-sm block mb-2">Source</label>
              <Input
                value={formData.source}
                onChange={(e) => setFormData({ ...formData, source: e.target.value })}
                placeholder="e.g., initiative_123, agent_456"
                className="bg-slate-900 border-slate-600 text-white"
              />
            </div>
          </div>
          <div>
            <label className="text-slate-300 text-sm block mb-2">Key Insight</label>
            <Input
              value={formData.insight}
              onChange={(e) => setFormData({ ...formData, insight: e.target.value })}
              placeholder="What is the key learning?"
              className="bg-slate-900 border-slate-600 text-white"
            />
          </div>
          <div>
            <label className="text-slate-300 text-sm block mb-2">Description (optional)</label>
            <Input
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Additional context..."
              className="bg-slate-900 border-slate-600 text-white"
              as="textarea"
            />
          </div>
          <Button
            onClick={handleSubmit}
            disabled={!formData.source || !formData.insight}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white"
          >
            Record Learning
          </Button>
        </CardContent>
      </Card>

      {/* Learning List */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white text-lg">Recent Learnings</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {learnings.map((learning) => (
              <div key={learning.id} className="border-l-4 border-blue-500 pl-4 py-2">
                <div className="flex items-start justify-between mb-1">
                  <h4 className="text-white font-semibold">{learning.key_insight}</h4>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${learningTypeColors[learning.type] || 'bg-gray-100 text-gray-800'}`}>
                    {learning.type}
                  </span>
                </div>
                <p className="text-slate-400 text-sm">{learning.source}</p>
                <p className="text-slate-300 text-sm mt-1">{learning.description}</p>
                <div className="flex gap-4 mt-2 text-xs text-slate-400">
                  <span>Confidence: {(learning.confidence * 100).toFixed(0)}%</span>
                  <span>{new Date(learning.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// ============================================================================
// SYNTHESIS TAB
// ============================================================================

interface SynthesisTabProps {
  syntheses: Synthesis[];
  onSynthesize: (type: string, title: string, description: string, recommendations: string[]) => void;
}

const SynthesisTab: React.FC<SynthesisTabProps> = ({ syntheses, onSynthesize }) => {
  const [formData, setFormData] = useState({
    type: 'recommendation',
    title: '',
    description: '',
    recommendations: ['']
  });

  const handleAddRecommendation = () => {
    setFormData({
      ...formData,
      recommendations: [...formData.recommendations, '']
    });
  };

  const handleRemoveRecommendation = (index: number) => {
    setFormData({
      ...formData,
      recommendations: formData.recommendations.filter((_, i) => i !== index)
    });
  };

  const handleSubmit = () => {
    if (formData.title && formData.recommendations.some(r => r.trim())) {
      onSynthesize(
        formData.type,
        formData.title,
        formData.description,
        formData.recommendations.filter(r => r.trim())
      );
      setFormData({
        type: 'recommendation',
        title: '',
        description: '',
        recommendations: ['']
      });
    }
  };

  return (
    <div className="space-y-4">
      {/* Synthesis Form */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white text-lg">Create Synthesis</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-slate-300 text-sm block mb-2">Synthesis Type</label>
            <select
              value={formData.type}
              onChange={(e) => setFormData({ ...formData, type: e.target.value })}
              className="w-full px-3 py-2 bg-slate-900 text-white rounded border border-slate-600"
            >
              <option value="trend">Trend</option>
              <option value="pattern">Pattern</option>
              <option value="prediction">Prediction</option>
              <option value="recommendation">Recommendation</option>
              <option value="warning">Warning</option>
              <option value="opportunity">Opportunity</option>
            </select>
          </div>
          <div>
            <label className="text-slate-300 text-sm block mb-2">Title</label>
            <Input
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="Synthesis title..."
              className="bg-slate-900 border-slate-600 text-white"
            />
          </div>
          <div>
            <label className="text-slate-300 text-sm block mb-2">Description</label>
            <Input
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Detailed explanation..."
              className="bg-slate-900 border-slate-600 text-white"
              as="textarea"
            />
          </div>
          <div>
            <label className="text-slate-300 text-sm block mb-2">Recommendations</label>
            <div className="space-y-2">
              {formData.recommendations.map((rec, idx) => (
                <div key={idx} className="flex gap-2">
                  <Input
                    value={rec}
                    onChange={(e) => {
                      const newRecs = [...formData.recommendations];
                      newRecs[idx] = e.target.value;
                      setFormData({ ...formData, recommendations: newRecs });
                    }}
                    placeholder="Recommendation..."
                    className="bg-slate-900 border-slate-600 text-white flex-1"
                  />
                  {formData.recommendations.length > 1 && (
                    <Button
                      onClick={() => handleRemoveRecommendation(idx)}
                      className="bg-red-600 hover:bg-red-700 text-white px-3"
                    >
                      Remove
                    </Button>
                  )}
                </div>
              ))}
            </div>
            <Button
              onClick={handleAddRecommendation}
              className="mt-2 bg-slate-700 hover:bg-slate-600 text-white w-full"
            >
              + Add Recommendation
            </Button>
          </div>
          <Button
            onClick={handleSubmit}
            disabled={!formData.title}
            className="w-full bg-purple-600 hover:bg-purple-700 text-white"
          >
            Create Synthesis
          </Button>
        </CardContent>
      </Card>

      {/* Synthesis List */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white text-lg">Recent Syntheses</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {syntheses.map((synthesis) => (
              <div key={synthesis.id} className="border-l-4 border-purple-500 pl-4 py-2">
                <div className="flex items-start justify-between mb-1">
                  <h4 className="text-white font-semibold">{synthesis.title}</h4>
                  <span className="px-2 py-1 rounded text-xs font-semibold bg-purple-100 text-purple-800">
                    {synthesis.type}
                  </span>
                </div>
                <p className="text-slate-300 text-sm">{synthesis.description}</p>
                <div className="mt-2">
                  <p className="text-slate-400 text-xs mb-1">Recommendations:</p>
                  <ul className="text-slate-300 text-sm space-y-1">
                    {synthesis.recommendations.map((rec, idx) => (
                      <li key={idx} className="flex gap-2">
                        <span className="text-green-400">✓</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="flex gap-4 mt-2 text-xs text-slate-400">
                  <span>Confidence: {(synthesis.confidence * 100).toFixed(0)}%</span>
                  <span>Based on {synthesis.supporting_learnings} learnings</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// ============================================================================
// DECISION TAB
// ============================================================================

interface DecisionTabProps {
  decisions: Decision[];
}

const DecisionTab: React.FC<DecisionTabProps> = ({ decisions }) => {
  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white text-lg flex items-center gap-2">
          <Target className="w-5 h-5 text-green-400" />
          Strategic Decisions
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {decisions.map((decision) => (
            <div key={decision.id} className="border border-slate-700 rounded-lg p-4">
              <div className="flex items-start justify-between mb-2">
                <h4 className="text-white font-semibold">{decision.title}</h4>
                <span className={`px-2 py-1 rounded text-xs font-semibold ${
                  decision.status === 'approved' ? 'bg-green-100 text-green-800' :
                  decision.status === 'rejected' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {decision.status}
                </span>
              </div>
              <p className="text-slate-300 text-sm mb-3">{decision.description}</p>
              <div className="bg-slate-900 rounded p-3 mb-3">
                <p className="text-slate-400 text-xs mb-1">Recommendation:</p>
                <p className="text-white text-sm">{decision.recommendation}</p>
              </div>
              {Object.keys(decision.impact_forecast).length > 0 && (
                <div className="text-xs text-slate-400 space-y-1">
                  <p className="font-semibold">Impact Forecast:</p>
                  {Object.entries(decision.impact_forecast).map(([key, value]) => (
                    <p key={key}>{key}: {((value as number) * 100).toFixed(0)}%</p>
                  ))}
                </div>
              )}
              <div className="flex gap-4 mt-3 text-xs text-slate-400">
                <span>Confidence: {(decision.confidence * 100).toFixed(0)}%</span>
                <span>{new Date(decision.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

// ============================================================================
// MENTORING TAB
// ============================================================================

const MentoringTab: React.FC = () => {
  const [formData, setFormData] = useState({
    agent_name: '',
    challenge: '',
    goal: ''
  });
  const [mentoringResult, setMentoringResult] = useState<any>(null);

  const handleProvideMentoring = async () => {
    if (formData.agent_name && formData.goal) {
      try {
        const response = await api.post('/lords/cognition/mentoring/provide', {
          agent_name: formData.agent_name,
          current_challenge: formData.challenge,
          agent_goal: formData.goal
        });
        setMentoringResult(response.data.data);
      } catch (error) {
        console.error('Failed to provide mentoring:', error);
        alert('Failed to provide mentoring');
      }
    }
  };

  return (
    <div className="space-y-4">
      {/* Mentoring Form */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white text-lg">Provide Mentoring</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="text-slate-300 text-sm block mb-2">Agent Name</label>
              <Input
                value={formData.agent_name}
                onChange={(e) => setFormData({ ...formData, agent_name: e.target.value })}
                placeholder="e.g., ResearchAgent1"
                className="bg-slate-900 border-slate-600 text-white"
              />
            </div>
            <div>
              <label className="text-slate-300 text-sm block mb-2">Current Challenge</label>
              <Input
                value={formData.challenge}
                onChange={(e) => setFormData({ ...formData, challenge: e.target.value })}
                placeholder="What challenge is facing?"
                className="bg-slate-900 border-slate-600 text-white"
              />
            </div>
            <div>
              <label className="text-slate-300 text-sm block mb-2">Agent Goal</label>
              <Input
                value={formData.goal}
                onChange={(e) => setFormData({ ...formData, goal: e.target.value })}
                placeholder="What is the goal?"
                className="bg-slate-900 border-slate-600 text-white"
              />
            </div>
          </div>
          <Button
            onClick={handleProvideMentoring}
            disabled={!formData.agent_name || !formData.goal}
            className="w-full bg-yellow-600 hover:bg-yellow-700 text-white"
          >
            Provide Mentoring
          </Button>
        </CardContent>
      </Card>

      {/* Mentoring Results */}
      {mentoringResult && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white text-lg">Mentoring for {mentoringResult.agent}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-slate-200 whitespace-pre-wrap text-sm">
              {mentoringResult.mentoring_summary}
            </div>
            {mentoringResult.key_points && mentoringResult.key_points.length > 0 && (
              <div>
                <h4 className="text-white font-semibold mb-2">Key Points:</h4>
                <div className="space-y-2">
                  {mentoringResult.key_points.map((point: any, idx: number) => (
                    <div key={idx} className="border-l-2 border-yellow-500 pl-3">
                      <p className="text-white text-sm font-semibold">{point.insight}</p>
                      {point.recommendations && (
                        <ul className="mt-1 space-y-1">
                          {point.recommendations.map((rec: string, ridx: number) => (
                            <li key={ridx} className="text-slate-300 text-xs flex gap-2">
                              <span className="text-yellow-400">→</span>
                              {rec}
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};
