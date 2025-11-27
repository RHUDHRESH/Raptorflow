// frontend/pages/strategy/ArbiterDashboard.tsx
// RaptorFlow Codex - Arbiter Lord Dashboard
// Phase 2A Week 6 - Conflict Resolution & Fair Arbitration

import React, { useState, useEffect, useCallback } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Scale, AlertCircle, CheckCircle2, MessageSquare } from 'lucide-react';

interface MetricCard {
  title: string;
  value: string | number;
  description: string;
  icon: React.ReactNode;
  color: string;
}

interface ConflictCase {
  case_id: string;
  conflict_type: string;
  title: string;
  description: string;
  severity: string;
  status: string;
  parties_involved: string[];
  created_at: string;
}

interface ResolutionProposal {
  proposal_id: string;
  case_id: string;
  proposed_solution: string;
  fairness_score: number;
  trade_offs: string[];
  status: string;
  created_at: string;
}

interface ArbitrationDecision {
  decision_id: string;
  case_id: string;
  proposal_id: string;
  decision_outcome: string;
  enforcement_method: string;
  fairness_rationale: string;
  stakeholder_satisfaction: number;
  status: string;
  created_at: string;
}

interface Appeal {
  appeal_id: string;
  decision_id: string;
  appellant_party: string;
  appeal_grounds: string[];
  status: string;
  merit_assessment: string;
  created_at: string;
}

const ArbiterDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('cases');
  const [wsConnected, setWsConnected] = useState(false);
  const [metrics, setMetrics] = useState<Record<string, any>>({
    open_cases: 0,
    fairness_score: 0,
    resolution_rate: 0,
    appeal_rate: 0,
  });

  // Conflict Cases State
  const [caseForm, setCaseForm] = useState({
    conflict_type: 'resource_allocation',
    title: '',
    description: '',
    parties_involved: [],
    conflicting_goals: [],
  });
  const [cases, setCases] = useState<ConflictCase[]>([]);
  const [caseLoading, setCaseLoading] = useState(false);

  // Resolution Proposals State
  const [proposalForm, setProposalForm] = useState({
    case_id: '',
    proposed_solution: '',
    priority_adjustment: {},
  });
  const [proposals, setProposals] = useState<ResolutionProposal[]>([]);

  // Arbitration Decisions State
  const [decisionForm, setDecisionForm] = useState({
    case_id: '',
    proposal_id: '',
    enforcement_method: 'standard',
  });
  const [decisions, setDecisions] = useState<ArbitrationDecision[]>([]);

  // Appeals State
  const [appealForm, setAppealForm] = useState({
    decision_id: '',
    appellant_party: '',
    appeal_grounds: [],
    requested_review_points: [],
  });
  const [appeals, setAppeals] = useState<Appeal[]>([]);

  // WebSocket Connection
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/lords/arbiter`);

    ws.onopen = () => {
      console.log('✅ Connected to Arbiter WebSocket');
      setWsConnected(true);
      ws.send(JSON.stringify({ type: 'subscribe', lord: 'arbiter' }));
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
      console.log('❌ Disconnected from Arbiter WebSocket');
      setWsConnected(false);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => ws.close();
  }, []);

  // Register Conflict
  const handleRegisterConflict = useCallback(async () => {
    setCaseLoading(true);
    try {
      const response = await fetch('/lords/arbiter/conflict/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(caseForm),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.data) {
          const newCase: ConflictCase = {
            case_id: result.data.case_id,
            conflict_type: caseForm.conflict_type,
            title: caseForm.title,
            description: caseForm.description,
            severity: result.data.severity,
            status: result.data.status,
            parties_involved: caseForm.parties_involved,
            created_at: new Date().toISOString(),
          };
          setCases([newCase, ...cases]);
          setCaseForm({
            conflict_type: 'resource_allocation',
            title: '',
            description: '',
            parties_involved: [],
            conflicting_goals: [],
          });
        }
      }
    } catch (error) {
      console.error('Conflict registration error:', error);
    } finally {
      setCaseLoading(false);
    }
  }, [caseForm, cases]);

  // Propose Resolution
  const handleProposeResolution = useCallback(async () => {
    try {
      const response = await fetch('/lords/arbiter/resolution/propose', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(proposalForm),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.data) {
          const newProposal: ResolutionProposal = {
            proposal_id: result.data.proposal_id,
            case_id: proposalForm.case_id,
            proposed_solution: proposalForm.proposed_solution,
            fairness_score: result.data.fairness_score,
            trade_offs: result.data.trade_offs,
            status: result.data.status,
            created_at: new Date().toISOString(),
          };
          setProposals([newProposal, ...proposals]);
          setProposalForm({
            case_id: '',
            proposed_solution: '',
            priority_adjustment: {},
          });
        }
      }
    } catch (error) {
      console.error('Resolution proposal error:', error);
    }
  }, [proposalForm, proposals]);

  // Make Arbitration Decision
  const handleMakeDecision = useCallback(async () => {
    try {
      const response = await fetch('/lords/arbiter/decision/make', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(decisionForm),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.data) {
          const newDecision: ArbitrationDecision = {
            decision_id: result.data.decision_id,
            case_id: decisionForm.case_id,
            proposal_id: decisionForm.proposal_id,
            decision_outcome: result.data.decision_outcome,
            enforcement_method: decisionForm.enforcement_method,
            fairness_rationale: result.data.fairness_rationale,
            stakeholder_satisfaction: result.data.stakeholder_satisfaction,
            status: result.data.status,
            created_at: new Date().toISOString(),
          };
          setDecisions([newDecision, ...decisions]);
          setDecisionForm({
            case_id: '',
            proposal_id: '',
            enforcement_method: 'standard',
          });
        }
      }
    } catch (error) {
      console.error('Decision making error:', error);
    }
  }, [decisionForm, decisions]);

  // Handle Appeal
  const handleAppeal = useCallback(async () => {
    try {
      const response = await fetch('/lords/arbiter/appeals/handle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(appealForm),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.data) {
          const newAppeal: Appeal = {
            appeal_id: result.data.appeal_id,
            decision_id: appealForm.decision_id,
            appellant_party: appealForm.appellant_party,
            appeal_grounds: appealForm.appeal_grounds,
            status: result.data.status,
            merit_assessment: result.data.merit_assessment,
            created_at: new Date().toISOString(),
          };
          setAppeals([newAppeal, ...appeals]);
          setAppealForm({
            decision_id: '',
            appellant_party: '',
            appeal_grounds: [],
            requested_review_points: [],
          });
        }
      }
    } catch (error) {
      console.error('Appeal handling error:', error);
    }
  }, [appealForm, appeals]);

  const getSeverityColor = (severity: string): string => {
    switch (severity) {
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

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'open':
      case 'pending':
        return 'text-yellow-400';
      case 'resolved':
      case 'approved':
        return 'text-emerald-400';
      case 'closed':
        return 'text-slate-400';
      case 'appealed':
        return 'text-blue-400';
      default:
        return 'text-slate-400';
    }
  };

  const metricCards: MetricCard[] = [
    {
      title: 'Open Cases',
      value: metrics.open_cases || 0,
      description: 'Active conflict cases',
      icon: <AlertCircle className="w-6 h-6" />,
      color: 'from-red-900 to-red-700',
    },
    {
      title: 'Fairness Score',
      value: `${(metrics.fairness_score || 0).toFixed(0)}%`,
      description: 'Decision fairness metric',
      icon: <Scale className="w-6 h-6" />,
      color: 'from-indigo-900 to-indigo-700',
    },
    {
      title: 'Resolution Rate',
      value: `${(metrics.resolution_rate || 0).toFixed(0)}%`,
      description: 'Cases successfully resolved',
      icon: <CheckCircle2 className="w-6 h-6" />,
      color: 'from-emerald-900 to-emerald-700',
    },
    {
      title: 'Appeal Rate',
      value: `${(metrics.appeal_rate || 0).toFixed(0)}%`,
      description: 'Decisions appealed',
      icon: <MessageSquare className="w-6 h-6" />,
      color: 'from-amber-900 to-amber-700',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-red-400 via-orange-400 to-yellow-400 bg-clip-text text-transparent mb-2">
                ⚖️ Arbiter Lord
              </h1>
              <p className="text-slate-400">Conflict Resolution & Fair Arbitration</p>
            </div>
            <div className="flex items-center gap-3">
              <div
                className={`w-3 h-3 rounded-full ${
                  wsConnected ? 'bg-red-500 animate-pulse' : 'bg-red-500'
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
            <TabsTrigger value="cases" className="data-[state=active]:bg-slate-700">
              Cases
            </TabsTrigger>
            <TabsTrigger value="proposals" className="data-[state=active]:bg-slate-700">
              Proposals
            </TabsTrigger>
            <TabsTrigger value="decisions" className="data-[state=active]:bg-slate-700">
              Decisions
            </TabsTrigger>
            <TabsTrigger value="appeals" className="data-[state=active]:bg-slate-700">
              Appeals
            </TabsTrigger>
          </TabsList>

          {/* Conflict Cases Tab */}
          <TabsContent value="cases" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-red-400">Register Conflict Case</CardTitle>
                <CardDescription>Register a new conflict for arbitration</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Conflict Type
                    </label>
                    <select
                      value={caseForm.conflict_type}
                      onChange={(e) =>
                        setCaseForm({ ...caseForm, conflict_type: e.target.value })
                      }
                      className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                    >
                      <option>resource_allocation</option>
                      <option>priority_dispute</option>
                      <option>goal_conflict</option>
                      <option>stakeholder_disagreement</option>
                      <option>decision_challenge</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Title
                    </label>
                    <Input
                      value={caseForm.title}
                      onChange={(e) =>
                        setCaseForm({ ...caseForm, title: e.target.value })
                      }
                      placeholder="Conflict title"
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Description
                  </label>
                  <textarea
                    value={caseForm.description}
                    onChange={(e) =>
                      setCaseForm({ ...caseForm, description: e.target.value })
                    }
                    placeholder="Detailed conflict description"
                    rows={3}
                    className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                  />
                </div>

                <Button
                  onClick={handleRegisterConflict}
                  disabled={caseLoading}
                  className="w-full bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-500 hover:to-orange-500 text-white"
                >
                  {caseLoading ? 'Registering...' : 'Register Case'}
                </Button>
              </CardContent>
            </Card>

            {/* Cases List */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-red-400">Conflict Cases</h3>
              {cases.length === 0 ? (
                <Card className="bg-slate-800/30 border-slate-700">
                  <CardContent className="pt-6">
                    <p className="text-slate-400 text-center">No conflict cases registered</p>
                  </CardContent>
                </Card>
              ) : (
                cases.map((conflictCase) => (
                  <Card key={conflictCase.case_id} className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="space-y-3">
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-semibold text-white">{conflictCase.title}</p>
                            <p className="text-sm text-slate-400">{conflictCase.conflict_type.replace('_', ' ')}</p>
                          </div>
                          <div className="flex gap-2">
                            <Badge className={getSeverityColor(conflictCase.severity)}>
                              {conflictCase.severity}
                            </Badge>
                            <Badge className={getStatusColor(conflictCase.status)}>
                              {conflictCase.status}
                            </Badge>
                          </div>
                        </div>

                        <p className="text-sm text-slate-300">{conflictCase.description}</p>

                        {conflictCase.parties_involved.length > 0 && (
                          <div>
                            <p className="text-xs text-slate-400 mb-2">Parties Involved</p>
                            <div className="flex gap-2 flex-wrap">
                              {conflictCase.parties_involved.map((party, idx) => (
                                <span key={idx} className="text-xs bg-slate-700 text-slate-200 px-2 py-1 rounded">
                                  {party}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        <p className="text-xs text-slate-500">
                          Registered: {new Date(conflictCase.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          {/* Resolution Proposals Tab */}
          <TabsContent value="proposals" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-orange-400">Propose Resolution</CardTitle>
                <CardDescription>Propose fair resolution for a conflict</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Case ID
                    </label>
                    <Input
                      value={proposalForm.case_id}
                      onChange={(e) =>
                        setProposalForm({ ...proposalForm, case_id: e.target.value })
                      }
                      placeholder="e.g., case_001"
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Proposed Solution
                  </label>
                  <textarea
                    value={proposalForm.proposed_solution}
                    onChange={(e) =>
                      setProposalForm({ ...proposalForm, proposed_solution: e.target.value })
                    }
                    placeholder="Detailed solution proposal"
                    rows={4}
                    className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                  />
                </div>

                <Button
                  onClick={handleProposeResolution}
                  className="w-full bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-white"
                >
                  Propose Resolution
                </Button>
              </CardContent>
            </Card>

            {/* Proposals List */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-orange-400">Resolution Proposals</h3>
              {proposals.length === 0 ? (
                <Card className="bg-slate-800/30 border-slate-700">
                  <CardContent className="pt-6">
                    <p className="text-slate-400 text-center">No resolution proposals yet</p>
                  </CardContent>
                </Card>
              ) : (
                proposals.map((proposal) => (
                  <Card key={proposal.proposal_id} className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="space-y-3">
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-semibold text-white">Case: {proposal.case_id}</p>
                            <p className="text-sm text-slate-300">{proposal.proposed_solution}</p>
                          </div>
                          <Badge className={getStatusColor(proposal.status)}>
                            {proposal.status}
                          </Badge>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <p className="text-xs text-slate-400 mb-1">Fairness Score</p>
                            <p className="font-semibold text-purple-400">{proposal.fairness_score.toFixed(0)}%</p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-400 mb-1">Trade-offs</p>
                            <p className="text-sm text-slate-300">{proposal.trade_offs.length} identified</p>
                          </div>
                        </div>

                        {proposal.trade_offs.length > 0 && (
                          <div>
                            <p className="text-xs text-slate-400 mb-2">Trade-offs</p>
                            <ul className="text-sm text-slate-300 space-y-1">
                              {proposal.trade_offs.map((tradeoff, idx) => (
                                <li key={idx} className="flex items-start gap-2">
                                  <span className="text-yellow-500 mt-0.5">→</span>
                                  <span>{tradeoff}</span>
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

          {/* Arbitration Decisions Tab */}
          <TabsContent value="decisions" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-yellow-400">Make Arbitration Decision</CardTitle>
                <CardDescription>Finalize conflict resolution decision</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Case ID
                    </label>
                    <Input
                      value={decisionForm.case_id}
                      onChange={(e) =>
                        setDecisionForm({ ...decisionForm, case_id: e.target.value })
                      }
                      placeholder="e.g., case_001"
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Proposal ID
                    </label>
                    <Input
                      value={decisionForm.proposal_id}
                      onChange={(e) =>
                        setDecisionForm({ ...decisionForm, proposal_id: e.target.value })
                      }
                      placeholder="e.g., prop_001"
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Enforcement Method
                  </label>
                  <select
                    value={decisionForm.enforcement_method}
                    onChange={(e) =>
                      setDecisionForm({ ...decisionForm, enforcement_method: e.target.value })
                    }
                    className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                  >
                    <option>standard</option>
                    <option>accelerated</option>
                    <option>monitored</option>
                    <option>phased</option>
                  </select>
                </div>

                <Button
                  onClick={handleMakeDecision}
                  className="w-full bg-gradient-to-r from-yellow-600 to-orange-600 hover:from-yellow-500 hover:to-orange-500 text-white"
                >
                  Make Decision
                </Button>
              </CardContent>
            </Card>

            {/* Decisions List */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-yellow-400">Arbitration Decisions</h3>
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
                      <div className="space-y-3">
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-semibold text-white">Case: {decision.case_id}</p>
                            <p className="text-sm text-slate-400">{decision.decision_outcome}</p>
                          </div>
                          <Badge className={getStatusColor(decision.status)}>
                            {decision.status}
                          </Badge>
                        </div>

                        <div className="grid grid-cols-3 gap-4">
                          <div>
                            <p className="text-xs text-slate-400 mb-1">Satisfaction Score</p>
                            <p className="font-semibold text-emerald-400">{decision.stakeholder_satisfaction.toFixed(0)}%</p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-400 mb-1">Enforcement</p>
                            <p className="text-sm text-slate-300">{decision.enforcement_method}</p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-400 mb-1">Date</p>
                            <p className="text-sm text-slate-300">{new Date(decision.created_at).toLocaleDateString()}</p>
                          </div>
                        </div>

                        <div>
                          <p className="text-sm font-medium text-slate-300 mb-2">Fairness Rationale</p>
                          <p className="text-sm text-slate-300 bg-slate-900/50 p-3 rounded">
                            {decision.fairness_rationale}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          {/* Appeals Tab */}
          <TabsContent value="appeals" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-cyan-400">Handle Appeal</CardTitle>
                <CardDescription>Process appeals within the appeal window</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Decision ID
                    </label>
                    <Input
                      value={appealForm.decision_id}
                      onChange={(e) =>
                        setAppealForm({ ...appealForm, decision_id: e.target.value })
                      }
                      placeholder="e.g., dec_001"
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Appellant Party
                    </label>
                    <Input
                      value={appealForm.appellant_party}
                      onChange={(e) =>
                        setAppealForm({ ...appealForm, appellant_party: e.target.value })
                      }
                      placeholder="Party name"
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Appeal Grounds
                  </label>
                  <textarea
                    value={appealForm.appeal_grounds.join('\n')}
                    onChange={(e) =>
                      setAppealForm({
                        ...appealForm,
                        appeal_grounds: e.target.value.split('\n'),
                      })
                    }
                    placeholder="One ground per line"
                    rows={3}
                    className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                  />
                </div>

                <Button
                  onClick={handleAppeal}
                  className="w-full bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white"
                >
                  Handle Appeal
                </Button>
              </CardContent>
            </Card>

            {/* Appeals List */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-cyan-400">Appeals</h3>
              {appeals.length === 0 ? (
                <Card className="bg-slate-800/30 border-slate-700">
                  <CardContent className="pt-6">
                    <p className="text-slate-400 text-center">No appeals filed yet</p>
                  </CardContent>
                </Card>
              ) : (
                appeals.map((appeal) => (
                  <Card key={appeal.appeal_id} className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="space-y-3">
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-semibold text-white">{appeal.appellant_party}</p>
                            <p className="text-sm text-slate-400">Decision: {appeal.decision_id}</p>
                          </div>
                          <Badge className={getStatusColor(appeal.status)}>
                            {appeal.status}
                          </Badge>
                        </div>

                        <div>
                          <p className="text-xs text-slate-400 mb-2">Merit Assessment</p>
                          <p className="text-sm text-slate-300 bg-slate-900/50 p-2 rounded">
                            {appeal.merit_assessment}
                          </p>
                        </div>

                        {appeal.appeal_grounds.length > 0 && (
                          <div>
                            <p className="text-xs text-slate-400 mb-2">Grounds</p>
                            <ul className="text-sm text-slate-300 space-y-1">
                              {appeal.appeal_grounds.map((ground, idx) => (
                                <li key={idx} className="flex items-start gap-2">
                                  <span className="text-blue-500 mt-0.5">•</span>
                                  <span>{ground}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        <p className="text-xs text-slate-500">
                          Filed: {new Date(appeal.created_at).toLocaleDateString()}
                        </p>
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

export default ArbiterDashboard;
