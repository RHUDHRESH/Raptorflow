// frontend/pages/strategy/CognitionDashboard.tsx
// RaptorFlow Codex - Cognition Lord Dashboard
// Phase 2A Week 4 - Learning & Knowledge Synthesis

import React, { useState, useEffect, useCallback } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Brain, Lightbulb, CheckCircle2, Users } from 'lucide-react';

interface MetricCard {
  title: string;
  value: string | number;
  description: string;
  icon: React.ReactNode;
  color: string;
}

interface Learning {
  learning_id: string;
  type: string;
  source: string;
  insight: string;
  context: string;
  confidence: number;
  created_at: string;
}

interface Synthesis {
  synthesis_id: string;
  synthesis_type: string;
  title: string;
  insight: string;
  confidence: number;
  supporting_learnings: number;
  created_at: string;
}

interface Decision {
  decision_id: string;
  title: string;
  recommendation: string;
  confidence: number;
  rationale: string;
  status: string;
}

interface Mentoring {
  mentoring_id: string;
  agent_name: string;
  guidance: string;
  topic: string;
  effectiveness: number;
}

const CognitionDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('learning');
  const [wsConnected, setWsConnected] = useState(false);
  const [metrics, setMetrics] = useState<Record<string, any>>({
    learnings_recorded: 0,
    syntheses_created: 0,
    decisions_made: 0,
    effectiveness_score: 0,
  });

  // Learning State
  const [learningForm, setLearningForm] = useState({
    type: 'success',
    source: 'campaign_analysis',
    insight: '',
    context: '',
    confidence: 75,
  });
  const [learnings, setLearnings] = useState<Learning[]>([]);
  const [learningLoading, setLearningLoading] = useState(false);

  // Synthesis State
  const [synthesisForm, setSynthesisForm] = useState({
    synthesis_type: 'trend',
    title: '',
    insight: '',
  });
  const [syntheses, setSyntheses] = useState<Synthesis[]>([]);

  // Decision State
  const [decisionForm, setDecisionForm] = useState({
    title: '',
    recommendation: '',
    supporting_learnings: [],
  });
  const [decisions, setDecisions] = useState<Decision[]>([]);

  // Mentoring State
  const [mentoringForm, setMentoringForm] = useState({
    agent_name: '',
    topic: '',
    guidance: '',
  });
  const [mentorings, setMentorings] = useState<Mentoring[]>([]);

  // WebSocket Connection
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/lords/cognition`);

    ws.onopen = () => {
      console.log('✅ Connected to Cognition WebSocket');
      setWsConnected(true);
      ws.send(JSON.stringify({ type: 'subscribe', lord: 'cognition' }));
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
      console.log('❌ Disconnected from Cognition WebSocket');
      setWsConnected(false);
    };

    return () => ws.close();
  }, []);

  // Record Learning
  const handleRecordLearning = useCallback(async () => {
    setLearningLoading(true);
    try {
      const response = await fetch('/lords/cognition/learning/record', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(learningForm),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.data) {
          const newLearning: Learning = {
            learning_id: result.data.learning_id,
            type: learningForm.type,
            source: learningForm.source,
            insight: learningForm.insight,
            context: learningForm.context,
            confidence: learningForm.confidence,
            created_at: new Date().toISOString(),
          };
          setLearnings([newLearning, ...learnings]);
          setLearningForm({
            type: 'success',
            source: 'campaign_analysis',
            insight: '',
            context: '',
            confidence: 75,
          });
        }
      }
    } catch (error) {
      console.error('Learning recording error:', error);
    } finally {
      setLearningLoading(false);
    }
  }, [learningForm, learnings]);

  // Create Synthesis
  const handleCreateSynthesis = useCallback(async () => {
    try {
      const response = await fetch('/lords/cognition/synthesis/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(synthesisForm),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.data) {
          const newSynthesis: Synthesis = {
            synthesis_id: result.data.synthesis_id,
            synthesis_type: synthesisForm.synthesis_type,
            title: synthesisForm.title,
            insight: synthesisForm.insight,
            confidence: result.data.confidence || 80,
            supporting_learnings: result.data.supporting_learnings || 0,
            created_at: new Date().toISOString(),
          };
          setSyntheses([newSynthesis, ...syntheses]);
          setSynthesisForm({
            synthesis_type: 'trend',
            title: '',
            insight: '',
          });
        }
      }
    } catch (error) {
      console.error('Synthesis creation error:', error);
    }
  }, [synthesisForm, syntheses]);

  // Make Decision
  const handleMakeDecision = useCallback(async () => {
    try {
      const response = await fetch('/lords/cognition/decision/make', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(decisionForm),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.data) {
          const newDecision: Decision = {
            decision_id: result.data.decision_id,
            title: decisionForm.title,
            recommendation: decisionForm.recommendation,
            confidence: result.data.confidence || 75,
            rationale: result.data.rationale || '',
            status: result.data.status || 'active',
          };
          setDecisions([newDecision, ...decisions]);
          setDecisionForm({
            title: '',
            recommendation: '',
            supporting_learnings: [],
          });
        }
      }
    } catch (error) {
      console.error('Decision making error:', error);
    }
  }, [decisionForm, decisions]);

  // Provide Mentoring
  const handleProvideMentoring = useCallback(async () => {
    try {
      const response = await fetch('/lords/cognition/mentoring/provide', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mentoringForm),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.data) {
          const newMentoring: Mentoring = {
            mentoring_id: result.data.mentoring_id,
            agent_name: mentoringForm.agent_name,
            guidance: mentoringForm.guidance,
            topic: mentoringForm.topic,
            effectiveness: result.data.effectiveness || 80,
          };
          setMentorings([newMentoring, ...mentorings]);
          setMentoringForm({
            agent_name: '',
            topic: '',
            guidance: '',
          });
        }
      }
    } catch (error) {
      console.error('Mentoring provision error:', error);
    }
  }, [mentoringForm, mentorings]);

  const getTypeColor = (type: string): string => {
    switch (type) {
      case 'success':
        return 'bg-emerald-900 text-emerald-200';
      case 'failure':
        return 'bg-red-900 text-red-200';
      case 'pattern':
        return 'bg-blue-900 text-blue-200';
      case 'insight':
        return 'bg-purple-900 text-purple-200';
      default:
        return 'bg-slate-700 text-slate-200';
    }
  };

  const getSynthesisTypeColor = (type: string): string => {
    switch (type) {
      case 'trend':
        return 'bg-indigo-900 text-indigo-200';
      case 'pattern':
        return 'bg-cyan-900 text-cyan-200';
      case 'prediction':
        return 'bg-blue-900 text-blue-200';
      case 'recommendation':
        return 'bg-purple-900 text-purple-200';
      default:
        return 'bg-slate-700 text-slate-200';
    }
  };

  const metricCards: MetricCard[] = [
    {
      title: 'Learnings Recorded',
      value: metrics.learnings_recorded || 0,
      description: 'Total learning entries',
      icon: <Brain className="w-6 h-6" />,
      color: 'from-blue-900 to-blue-700',
    },
    {
      title: 'Syntheses Created',
      value: metrics.syntheses_created || 0,
      description: 'Knowledge syntheses',
      icon: <Lightbulb className="w-6 h-6" />,
      color: 'from-indigo-900 to-indigo-700',
    },
    {
      title: 'Decisions Made',
      value: metrics.decisions_made || 0,
      description: 'Strategic decisions',
      icon: <CheckCircle2 className="w-6 h-6" />,
      color: 'from-cyan-900 to-cyan-700',
    },
    {
      title: 'Effectiveness',
      value: `${(metrics.effectiveness_score || 0).toFixed(0)}%`,
      description: 'Average effectiveness',
      icon: <Users className="w-6 h-6" />,
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
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 via-indigo-400 to-cyan-400 bg-clip-text text-transparent mb-2">
                🧠 Cognition Lord
              </h1>
              <p className="text-slate-400">Learning & Knowledge Synthesis</p>
            </div>
            <div className="flex items-center gap-3">
              <div
                className={`w-3 h-3 rounded-full ${
                  wsConnected ? 'bg-blue-500 animate-pulse' : 'bg-red-500'
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
            <TabsTrigger value="learning" className="data-[state=active]:bg-slate-700">
              Learning
            </TabsTrigger>
            <TabsTrigger value="synthesis" className="data-[state=active]:bg-slate-700">
              Synthesis
            </TabsTrigger>
            <TabsTrigger value="decisions" className="data-[state=active]:bg-slate-700">
              Decisions
            </TabsTrigger>
            <TabsTrigger value="mentoring" className="data-[state=active]:bg-slate-700">
              Mentoring
            </TabsTrigger>
          </TabsList>

          {/* Learning Journal Tab */}
          <TabsContent value="learning" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-blue-400">Record Learning</CardTitle>
                <CardDescription>Document success, failure, or pattern learnings</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Learning Type
                    </label>
                    <select
                      value={learningForm.type}
                      onChange={(e) =>
                        setLearningForm({ ...learningForm, type: e.target.value })
                      }
                      className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                    >
                      <option>success</option>
                      <option>failure</option>
                      <option>pattern</option>
                      <option>insight</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Source
                    </label>
                    <select
                      value={learningForm.source}
                      onChange={(e) =>
                        setLearningForm({ ...learningForm, source: e.target.value })
                      }
                      className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                    >
                      <option>campaign_analysis</option>
                      <option>agent_execution</option>
                      <option>market_feedback</option>
                      <option>performance_data</option>
                      <option>user_interaction</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Insight
                  </label>
                  <textarea
                    value={learningForm.insight}
                    onChange={(e) =>
                      setLearningForm({ ...learningForm, insight: e.target.value })
                    }
                    placeholder="What did you learn?"
                    rows={3}
                    className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Context
                  </label>
                  <Input
                    value={learningForm.context}
                    onChange={(e) =>
                      setLearningForm({ ...learningForm, context: e.target.value })
                    }
                    placeholder="Additional context"
                    className="bg-slate-900 border-slate-700 text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Confidence: {learningForm.confidence}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={learningForm.confidence}
                    onChange={(e) =>
                      setLearningForm({
                        ...learningForm,
                        confidence: parseInt(e.target.value),
                      })
                    }
                    className="w-full"
                  />
                </div>

                <Button
                  onClick={handleRecordLearning}
                  disabled={learningLoading}
                  className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white"
                >
                  {learningLoading ? 'Recording...' : 'Record Learning'}
                </Button>
              </CardContent>
            </Card>

            {/* Learning List */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-blue-400">Learning Journal</h3>
              {learnings.length === 0 ? (
                <Card className="bg-slate-800/30 border-slate-700">
                  <CardContent className="pt-6">
                    <p className="text-slate-400 text-center">No learnings recorded yet</p>
                  </CardContent>
                </Card>
              ) : (
                learnings.map((learning) => (
                  <Card key={learning.learning_id} className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="space-y-2">
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-semibold text-white">{learning.insight}</p>
                            <p className="text-sm text-slate-400">{learning.source}</p>
                          </div>
                          <Badge className={getTypeColor(learning.type)}>
                            {learning.type}
                          </Badge>
                        </div>
                        <div className="flex justify-between">
                          <p className="text-sm text-slate-300">{learning.context}</p>
                          <p className="text-sm text-blue-400">Confidence: {learning.confidence}%</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          {/* Knowledge Synthesis Tab */}
          <TabsContent value="synthesis" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-indigo-400">Create Synthesis</CardTitle>
                <CardDescription>Synthesize learnings into knowledge</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Synthesis Type
                  </label>
                  <select
                    value={synthesisForm.synthesis_type}
                    onChange={(e) =>
                      setSynthesisForm({ ...synthesisForm, synthesis_type: e.target.value })
                    }
                    className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                  >
                    <option>trend</option>
                    <option>pattern</option>
                    <option>prediction</option>
                    <option>recommendation</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Title
                  </label>
                  <Input
                    value={synthesisForm.title}
                    onChange={(e) =>
                      setSynthesisForm({ ...synthesisForm, title: e.target.value })
                    }
                    placeholder="Synthesis title"
                    className="bg-slate-900 border-slate-700 text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Insight
                  </label>
                  <textarea
                    value={synthesisForm.insight}
                    onChange={(e) =>
                      setSynthesisForm({ ...synthesisForm, insight: e.target.value })
                    }
                    placeholder="Synthesized insight"
                    rows={3}
                    className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                  />
                </div>

                <Button
                  onClick={handleCreateSynthesis}
                  className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white"
                >
                  Create Synthesis
                </Button>
              </CardContent>
            </Card>

            {/* Synthesis List */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-indigo-400">Knowledge Syntheses</h3>
              {syntheses.length === 0 ? (
                <Card className="bg-slate-800/30 border-slate-700">
                  <CardContent className="pt-6">
                    <p className="text-slate-400 text-center">No syntheses created yet</p>
                  </CardContent>
                </Card>
              ) : (
                syntheses.map((synthesis) => (
                  <Card key={synthesis.synthesis_id} className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="space-y-2">
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-semibold text-white">{synthesis.title}</p>
                            <p className="text-sm text-slate-400">{synthesis.insight}</p>
                          </div>
                          <Badge className={getSynthesisTypeColor(synthesis.synthesis_type)}>
                            {synthesis.synthesis_type}
                          </Badge>
                        </div>
                        <div className="flex justify-between">
                          <p className="text-sm text-slate-400">
                            Supporting learnings: {synthesis.supporting_learnings}
                          </p>
                          <p className="text-sm text-indigo-400">
                            Confidence: {synthesis.confidence}%
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          {/* Decisions Tab */}
          <TabsContent value="decisions" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-cyan-400">Make Decision</CardTitle>
                <CardDescription>Generate strategic decisions from learnings</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Decision Title
                  </label>
                  <Input
                    value={decisionForm.title}
                    onChange={(e) =>
                      setDecisionForm({ ...decisionForm, title: e.target.value })
                    }
                    placeholder="What decision are you making?"
                    className="bg-slate-900 border-slate-700 text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Recommendation
                  </label>
                  <textarea
                    value={decisionForm.recommendation}
                    onChange={(e) =>
                      setDecisionForm({ ...decisionForm, recommendation: e.target.value })
                    }
                    placeholder="Recommended action"
                    rows={3}
                    className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                  />
                </div>

                <Button
                  onClick={handleMakeDecision}
                  className="w-full bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white"
                >
                  Make Decision
                </Button>
              </CardContent>
            </Card>

            {/* Decisions List */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-cyan-400">Decisions</h3>
              {decisions.length === 0 ? (
                <Card className="bg-slate-800/30 border-slate-700">
                  <CardContent className="pt-6">
                    <p className="text-slate-400 text-center">No decisions made yet</p>
                  </CardContent>
                </Card>
              ) : (
                decisions.map((decision) => (
                  <Card key={decision.decision_id} className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="space-y-2">
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-semibold text-white">{decision.title}</p>
                            <p className="text-sm text-slate-400">{decision.recommendation}</p>
                          </div>
                          <Badge className="bg-slate-700 text-slate-200">{decision.status}</Badge>
                        </div>
                        <p className="text-sm text-cyan-400">
                          Confidence: {decision.confidence}%
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          {/* Mentoring Tab */}
          <TabsContent value="mentoring" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-teal-400">Provide Mentoring</CardTitle>
                <CardDescription>Guide agents and team members</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Agent/User Name
                    </label>
                    <Input
                      value={mentoringForm.agent_name}
                      onChange={(e) =>
                        setMentoringForm({ ...mentoringForm, agent_name: e.target.value })
                      }
                      placeholder="e.g., Content Agent"
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Topic
                    </label>
                    <Input
                      value={mentoringForm.topic}
                      onChange={(e) =>
                        setMentoringForm({ ...mentoringForm, topic: e.target.value })
                      }
                      placeholder="Mentoring topic"
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Guidance
                  </label>
                  <textarea
                    value={mentoringForm.guidance}
                    onChange={(e) =>
                      setMentoringForm({ ...mentoringForm, guidance: e.target.value })
                    }
                    placeholder="Provide mentoring guidance"
                    rows={3}
                    className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                  />
                </div>

                <Button
                  onClick={handleProvideMentoring}
                  className="w-full bg-gradient-to-r from-teal-600 to-cyan-600 hover:from-teal-500 hover:to-cyan-500 text-white"
                >
                  Provide Mentoring
                </Button>
              </CardContent>
            </Card>

            {/* Mentoring List */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-teal-400">Mentoring History</h3>
              {mentorings.length === 0 ? (
                <Card className="bg-slate-800/30 border-slate-700">
                  <CardContent className="pt-6">
                    <p className="text-slate-400 text-center">No mentoring provided yet</p>
                  </CardContent>
                </Card>
              ) : (
                mentorings.map((mentoring) => (
                  <Card key={mentoring.mentoring_id} className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="space-y-2">
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-semibold text-white">{mentoring.agent_name}</p>
                            <p className="text-sm text-slate-400">{mentoring.topic}</p>
                          </div>
                          <p className="text-sm text-teal-400">
                            Effectiveness: {mentoring.effectiveness}%
                          </p>
                        </div>
                        <p className="text-sm text-slate-300">{mentoring.guidance}</p>
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

export default CognitionDashboard;
