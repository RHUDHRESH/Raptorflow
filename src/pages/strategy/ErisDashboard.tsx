// frontend/pages/strategy/ErisDashboard.tsx
// Chaos Engineering & Wargaming Dashboard

import React, { useState, useEffect, useCallback } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Flame, ShieldAlert, Skull, Activity, Zap } from 'lucide-react';
import { LuxeEmptyState, LuxeSkeleton } from '../../components/ui/PremiumUI';
import erisApi, { ChaosEvent, WargameResponse } from '../../api/eris';

interface MetricCard {
  title: string;
  value: string | number;
  description: string;
  icon: React.ReactNode;
  color: string;
}

const ErisDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('chaos');
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState<ChaosEvent[]>([]);
  
  // Forms
  const [chaosForm, setChaosForm] = useState({
    domain: 'market',
    severity: 'medium'
  });
  
  const [wargameForm, setWargameForm] = useState({
    strategyId: '',
    description: '',
    numEvents: 3
  });

  // State for results
  const [lastChaosEvent, setLastChaosEvent] = useState<ChaosEvent | null>(null);
  const [lastWargame, setLastWargame] = useState<WargameResponse | null>(null);

  // Load history
  useEffect(() => {
    const loadHistory = async () => {
        try {
            const result = await erisApi.getHistory();
            if (Array.isArray(result)) {
                setHistory(result);
            }
        } catch (e) {
            console.error("Failed to load history", e);
        }
    };
    loadHistory();
  }, []);

  const handleGenerateChaos = useCallback(async () => {
    setIsLoading(true);
    try {
        const result = await erisApi.generateChaos(chaosForm.domain, chaosForm.severity);
        if (result) {
            // Adapter for raw result to ChaosEvent if needed, assuming result matches
            const event = result as ChaosEvent;
            setLastChaosEvent(event);
            setHistory(prev => [event, ...prev]);
        }
    } catch (e) {
        console.error("Chaos generation failed", e);
    } finally {
        setIsLoading(false);
    }
  }, [chaosForm]);

  const handleRunWargame = useCallback(async () => {
    setIsLoading(true);
    try {
        const result = await erisApi.runWargame(
            wargameForm.strategyId || 'current-strategy', 
            { description: wargameForm.description },
            wargameForm.numEvents
        );
        if (result) {
            setLastWargame(result as WargameResponse);
        }
    } catch (e) {
        console.error("Wargame failed", e);
    } finally {
        setIsLoading(false);
    }
  }, [wargameForm]);

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
        case 'critical': return 'bg-red-900 text-red-200 border-red-700';
        case 'high': return 'bg-orange-900 text-orange-200 border-orange-700';
        case 'medium': return 'bg-yellow-900 text-yellow-200 border-yellow-700';
        case 'low': return 'bg-blue-900 text-blue-200 border-blue-700';
        default: return 'bg-slate-800';
    }
  };

  const metricCards: MetricCard[] = [
    {
      title: 'Chaos Events',
      value: history.length,
      description: 'Total events generated',
      icon: <Flame className="w-6 h-6" />,
      color: 'from-red-900 to-orange-900',
    },
    {
      title: 'Resilience Score',
      value: lastWargame ? Math.round(lastWargame.resilience_score.overall_score) : '-',
      description: 'Last wargame result',
      icon: <ShieldAlert className="w-6 h-6" />,
      color: 'from-blue-900 to-cyan-900',
    },
    {
      title: 'Active Scenarios',
      value: lastWargame ? 1 : 0,
      description: 'Simulations running',
      icon: <Activity className="w-6 h-6" />,
      color: 'from-purple-900 to-pink-900',
    },
    {
      title: 'Entropy Level',
      value: 'Low',
      description: 'System noise level',
      icon: <Zap className="w-6 h-6" />,
      color: 'from-green-900 to-emerald-900',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-slate-950 to-red-950/20 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-red-500 via-orange-500 to-yellow-500 bg-clip-text text-transparent mb-2 flex items-center gap-3">
                <Skull className="w-10 h-10 text-red-500" />
                Project Eris
              </h1>
              <p className="text-slate-400">Chaos Engineering & Strategic Wargaming</p>
            </div>
          </div>

          {/* Metric Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {metricCards.map((card, index) => (
              <Card
                key={index}
                className={`bg-gradient-to-br ${card.color} border-slate-800 text-white overflow-hidden`}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium opacity-90">{card.title}</CardTitle>
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

        {/* Main Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3 bg-slate-900/50 border border-slate-800">
            <TabsTrigger value="chaos" className="data-[state=active]:bg-red-950/50 data-[state=active]:text-red-200">
              Chaos Generator
            </TabsTrigger>
            <TabsTrigger value="wargame" className="data-[state=active]:bg-orange-950/50 data-[state=active]:text-orange-200">
              Wargame Simulator
            </TabsTrigger>
            <TabsTrigger value="history" className="data-[state=active]:bg-slate-800">
              Event History
            </TabsTrigger>
          </TabsList>

          {/* Chaos Generator Tab */}
          <TabsContent value="chaos" className="space-y-6 mt-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="bg-slate-900/50 border-slate-800">
                    <CardHeader>
                        <CardTitle className="text-red-400">Inject Chaos</CardTitle>
                        <CardDescription>Generate a random disruption event</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-2">Target Domain</label>
                            <select 
                                className="w-full bg-slate-950 border border-slate-700 text-white px-3 py-2 rounded"
                                value={chaosForm.domain}
                                onChange={(e) => setChaosForm({...chaosForm, domain: e.target.value})}
                            >
                                <option value="market">Market Conditions</option>
                                <option value="reputation">Brand Reputation</option>
                                <option value="competitor">Competitor Action</option>
                                <option value="regulatory">Regulatory Change</option>
                                <option value="technical">Technical Failure</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-2">Severity</label>
                            <select 
                                className="w-full bg-slate-950 border border-slate-700 text-white px-3 py-2 rounded"
                                value={chaosForm.severity}
                                onChange={(e) => setChaosForm({...chaosForm, severity: e.target.value})}
                            >
                                <option value="low">Low (Annoyance)</option>
                                <option value="medium">Medium (Disruption)</option>
                                <option value="high">High (Crisis)</option>
                                <option value="critical">Critical (Existential)</option>
                            </select>
                        </div>
                        <Button 
                            onClick={handleGenerateChaos}
                            disabled={isLoading}
                            className="w-full bg-red-600 hover:bg-red-700 text-white font-bold"
                        >
                            {isLoading ? 'Summoning Eris...' : 'GENERATE CHAOS'}
                        </Button>
                    </CardContent>
                </Card>

                {/* Result Display */}
                <Card className="bg-slate-900/50 border-slate-800">
                    <CardHeader>
                        <CardTitle className="text-slate-200">Event Monitor</CardTitle>
                    </CardHeader>
                    <CardContent>
                        {lastChaosEvent ? (
                            <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
                                <div className="flex justify-between items-start">
                                    <h3 className="text-xl font-bold text-white">{lastChaosEvent.name}</h3>
                                    <Badge className={getSeverityColor(lastChaosEvent.severity)}>
                                        {lastChaosEvent.severity.toUpperCase()}
                                    </Badge>
                                </div>
                                <div className="bg-slate-950 p-4 rounded border border-slate-800">
                                    <p className="text-slate-300">{lastChaosEvent.description}</p>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <span className="text-xs text-slate-500 uppercase">Type</span>
                                        <p className="text-slate-200">{lastChaosEvent.type}</p>
                                    </div>
                                    <div>
                                        <span className="text-xs text-slate-500 uppercase">Time</span>
                                        <p className="text-slate-200">{new Date().toLocaleTimeString()}</p>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <LuxeEmptyState 
                                icon={Activity}
                                title="Systems Nominal"
                                description="No active chaos events detected. Inject chaos to begin."
                                className="bg-transparent border-0"
                            />
                        )}
                    </CardContent>
                </Card>
            </div>
          </TabsContent>

          {/* Wargame Tab */}
          <TabsContent value="wargame" className="space-y-6 mt-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Config */}
                <Card className="bg-slate-900/50 border-slate-800 lg:col-span-1">
                    <CardHeader>
                        <CardTitle className="text-orange-400">Wargame Configuration</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-2">Strategy ID</label>
                            <Input 
                                value={wargameForm.strategyId}
                                onChange={(e) => setWargameForm({...wargameForm, strategyId: e.target.value})}
                                placeholder="e.g. Q4-Launch-Alpha"
                                className="bg-slate-950 border-slate-700 text-white"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-2">Context/Description</label>
                            <Input 
                                value={wargameForm.description}
                                onChange={(e) => setWargameForm({...wargameForm, description: e.target.value})}
                                placeholder="Brief description of strategy"
                                className="bg-slate-950 border-slate-700 text-white"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-2">Number of Events</label>
                            <Input 
                                type="number"
                                value={wargameForm.numEvents}
                                onChange={(e) => setWargameForm({...wargameForm, numEvents: parseInt(e.target.value)})}
                                className="bg-slate-950 border-slate-700 text-white"
                            />
                        </div>
                        <Button 
                            onClick={handleRunWargame}
                            disabled={isLoading}
                            className="w-full bg-orange-600 hover:bg-orange-700 text-white font-bold"
                        >
                            {isLoading ? 'Simulating...' : 'START WARGAME'}
                        </Button>
                    </CardContent>
                </Card>

                {/* Wargame Results */}
                <Card className="bg-slate-900/50 border-slate-800 lg:col-span-2">
                    <CardHeader>
                        <CardTitle className="text-slate-200">Simulation Results</CardTitle>
                    </CardHeader>
                    <CardContent>
                        {lastWargame ? (
                            <div className="space-y-6">
                                {/* Score */}
                                <div className="flex items-center justify-center p-6 bg-slate-950 rounded border border-slate-800">
                                    <div className="text-center">
                                        <span className="text-sm text-slate-400 uppercase tracking-widest">Survival Probability</span>
                                        <div className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400 mt-2">
                                            {Math.round(lastWargame.resilience_score.overall_score)}%
                                        </div>
                                    </div>
                                </div>

                                {/* Events */}
                                <div>
                                    <h4 className="text-sm font-bold text-slate-400 uppercase mb-3">Scenario Timeline</h4>
                                    <div className="space-y-3">
                                        {lastWargame.scenario.events.map((ev, i) => (
                                            <div key={i} className="flex gap-4 p-3 bg-slate-950/50 rounded border border-slate-800/50">
                                                <div className="mt-1"><Flame className="w-4 h-4 text-red-500" /></div>
                                                <div>
                                                    <p className="font-bold text-slate-200">{ev.name}</p>
                                                    <p className="text-sm text-slate-400">{ev.description}</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Weaknesses */}
                                <div>
                                    <h4 className="text-sm font-bold text-red-400 uppercase mb-3">Vulnerabilities Detected</h4>
                                    <ul className="space-y-2">
                                        {lastWargame.resilience_score.weaknesses_exposed.map((w, i) => (
                                            <li key={i} className="flex items-center gap-2 text-slate-300 text-sm">
                                                <ShieldAlert className="w-4 h-4 text-red-500" />
                                                {w}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        ) : (
                            <LuxeEmptyState 
                                icon={Skull}
                                title="Awaiting Simulation"
                                description="Configure and launch a wargame to test strategy resilience."
                                className="bg-transparent border-0"
                            />
                        )}
                    </CardContent>
                </Card>
            </div>
          </TabsContent>

          {/* History Tab */}
          <TabsContent value="history" className="space-y-6 mt-6">
            <div className="space-y-4">
                {history.map((event, idx) => (
                    <Card key={idx} className="bg-slate-900/50 border-slate-800 hover:border-slate-700 transition-colors">
                        <CardContent className="p-4">
                            <div className="flex justify-between items-start">
                                <div>
                                    <h4 className="font-bold text-white">{event.name}</h4>
                                    <p className="text-sm text-slate-400 mt-1">{event.description}</p>
                                </div>
                                <Badge className={getSeverityColor(event.severity)}>{event.severity}</Badge>
                            </div>
                            <div className="mt-3 flex gap-4 text-xs text-slate-500">
                                <span>{event.type}</span>
                                <span>{new Date(event.timestamp).toLocaleString()}</span>
                            </div>
                        </CardContent>
                    </Card>
                ))}
                {history.length === 0 && (
                    <p className="text-center text-slate-500 py-10">No history available.</p>
                )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ErisDashboard;
