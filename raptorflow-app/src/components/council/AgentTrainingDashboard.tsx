'use client';

import React, { useState } from 'react';
import { EXPERTS } from './CouncilChamber';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Brain,
  Zap,
  Shield,
  Target,
  Plus,
  Search,
  Edit3,
  Trash2,
  Check,
  X,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

export function AgentTrainingDashboard() {
  const [selectedExpert, setSelectedExpert] = useState(EXPERTS[0].id);
  const [editingHeuristic, setEditingHeuristic] = useState<string | null>(null);
  const [editValue, setEditValue] = useState('');

  // Mock heuristics and exploits data
  const [mockSkills, setMockSkills] = useState({
    brand_philosopher: {
      heuristics: [
        {
          id: 'h1',
          type: 'never',
          content: 'Never use exclamation marks in headlines.',
        },
        {
          id: 'h2',
          type: 'always',
          content: 'Always use serif fonts for display titles.',
        },
        {
          id: 'h3',
          type: 'always',
          content: "Maintain a 'Quiet Luxury' aesthetic in all visual assets.",
        },
      ],
      exploits: [
        {
          id: 'e1',
          title: 'Identity Pivot 2024',
          roi: '4.5x',
          status: 'active',
        },
      ],
    },
    data_quant: {
      heuristics: [
        {
          id: 'h4',
          type: 'always',
          content:
            'Calculate 95% confidence intervals for all lead projections.',
        },
      ],
      exploits: [],
    },
  });

  const currentSkills = mockSkills[
    selectedExpert as keyof typeof mockSkills
  ] || { heuristics: [], exploits: [] };

  const saveEdit = () => {
    if (editingHeuristic === 'new') {
      const newH = {
        id: Math.random().toString(),
        type: 'always',
        content: editValue,
      };
      setMockSkills((prev) => ({
        ...prev,
        [selectedExpert]: {
          ...currentSkills,
          heuristics: [...currentSkills.heuristics, newH],
        },
      }));
      toast.success('New heuristic added.');
    } else {
      setMockSkills((prev) => ({
        ...prev,
        [selectedExpert]: {
          ...currentSkills,
          heuristics: currentSkills.heuristics.map((h) =>
            h.id === editingHeuristic ? { ...h, content: editValue } : h
          ),
        },
      }));
      toast.success('Heuristic updated.');
    }
    setEditingHeuristic(null);
  };

  return (
    <div className="space-y-8">
      <header className="flex justify-between items-end">
        <div>
          <h3 className="text-2xl font-serif italic text-ink">
            Agent Training Dashboard
          </h3>
          <p className="text-sm text-secondary-text mt-1">
            Configure individual expert DNA and learned behaviors.
          </p>
        </div>
        <div className="flex gap-2">
          <button className="flex items-center gap-2 px-4 py-2 rounded-xl border border-borders bg-white text-xs font-medium hover:bg-canvas transition-colors">
            <Search className="h-3.5 w-3.5" />
            Search DNA
          </button>
          <button
            onClick={() => {
              setEditingHeuristic('new');
              setEditValue('');
            }}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-ink text-white text-xs font-medium hover:bg-ink/90 transition-colors"
          >
            <Plus className="h-3.5 w-3.5" />
            New Rule
          </button>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar: Expert Selector */}
        <aside className="lg:col-span-1 space-y-2">
          <h4 className="text-[10px] font-bold uppercase tracking-widest text-muted-fill mb-4">
            The 12 Experts
          </h4>
          {EXPERTS.map((expert) => (
            <button
              key={expert.id}
              onClick={() => setSelectedExpert(expert.id)}
              className={cn(
                'w-full flex items-center gap-3 p-3 rounded-xl transition-all text-left',
                selectedExpert === expert.id
                  ? 'bg-accent/10 border border-accent/20 text-accent'
                  : 'hover:bg-surface/50 text-secondary-text'
              )}
            >
              <expert.icon
                className={cn(
                  'h-4 w-4',
                  selectedExpert === expert.id ? 'text-accent' : 'opacity-50'
                )}
              />
              <span className="text-xs font-medium">{expert.name}</span>
            </button>
          ))}
        </aside>

        {/* Main: Skill Editor */}
        <main className="lg:col-span-3 space-y-6">
          <div className="p-6 rounded-3xl bg-surface border border-borders/50 shadow-sm">
            <div className="flex items-center gap-4 mb-8">
              <div className="p-4 rounded-2xl bg-canvas border border-borders/30">
                {React.createElement(
                  EXPERTS.find((e) => e.id === selectedExpert)?.icon || Brain,
                  {
                    className: cn(
                      'h-8 w-8',
                      EXPERTS.find((e) => e.id === selectedExpert)?.color
                    ),
                  }
                )}
              </div>
              <div>
                <h4 className="text-xl font-serif text-ink">
                  {EXPERTS.find((e) => e.id === selectedExpert)?.name}
                </h4>
                <p className="text-xs text-secondary-text">
                  {EXPERTS.find((e) => e.id === selectedExpert)?.role}
                </p>
              </div>
            </div>

            <Tabs defaultValue="heuristics" className="space-y-6">
              <TabsList className="bg-canvas/50 p-1 rounded-xl">
                <TabsTrigger value="heuristics" className="rounded-lg text-xs">
                  Heuristics (DNA)
                </TabsTrigger>
                <TabsTrigger value="exploits" className="rounded-lg text-xs">
                  Proven Exploits
                </TabsTrigger>
                <TabsTrigger value="history" className="rounded-lg text-xs">
                  Training History
                </TabsTrigger>
              </TabsList>

              <TabsContent value="heuristics" className="space-y-4">
                {editingHeuristic === 'new' && (
                  <div className="p-4 rounded-2xl bg-accent/5 border border-accent/30 flex flex-col gap-3">
                    <textarea
                      autoFocus
                      value={editValue}
                      onChange={(e) => setEditValue(e.target.value)}
                      placeholder="Enter new rule... e.g. Always use data to back up claims."
                      className="w-full bg-white border border-borders rounded-xl p-3 text-sm focus:outline-none focus:ring-1 ring-accent"
                      rows={3}
                    />
                    <div className="flex justify-end gap-2">
                      <button
                        onClick={() => setEditingHeuristic(null)}
                        className="p-2 text-secondary-text hover:bg-white rounded-lg"
                      >
                        <X className="h-4 w-4" />
                      </button>
                      <button
                        onClick={saveEdit}
                        className="px-4 py-1.5 bg-ink text-white rounded-lg text-xs font-medium"
                      >
                        Add Rule
                      </button>
                    </div>
                  </div>
                )}

                {currentSkills.heuristics.length > 0 ? (
                  currentSkills.heuristics.map((h) => (
                    <div
                      key={h.id}
                      className="group flex items-start justify-between p-4 rounded-2xl bg-canvas/30 border border-borders/30 hover:border-borders transition-all"
                    >
                      <div className="flex gap-4 flex-1">
                        <div
                          className={cn(
                            'mt-1 p-1.5 rounded-md shrink-0 h-fit',
                            h.type === 'never'
                              ? 'bg-red-500/10 text-red-500'
                              : 'bg-green-500/10 text-green-500'
                          )}
                        >
                          {h.type === 'never' ? (
                            <Shield className="h-3.5 w-3.5" />
                          ) : (
                            <Zap className="h-3.5 w-3.5" />
                          )}
                        </div>
                        <div className="flex-1">
                          {editingHeuristic === h.id ? (
                            <div className="space-y-3">
                              <textarea
                                autoFocus
                                value={editValue}
                                onChange={(e) => setEditValue(e.target.value)}
                                className="w-full bg-white border border-borders rounded-xl p-3 text-sm focus:outline-none"
                                rows={2}
                              />
                              <div className="flex justify-end gap-2">
                                <button
                                  onClick={() => setEditingHeuristic(null)}
                                  className="p-1 text-secondary-text hover:bg-white rounded-md"
                                >
                                  <X className="h-3.5 w-3.5" />
                                </button>
                                <button
                                  onClick={saveEdit}
                                  className="p-1 text-accent hover:bg-white rounded-md"
                                >
                                  <Check className="h-3.5 w-3.5" />
                                </button>
                              </div>
                            </div>
                          ) : (
                            <>
                              <p className="text-sm text-primary-text leading-relaxed font-medium">
                                {h.content}
                              </p>
                              <p className="text-[10px] text-secondary-text mt-1 uppercase tracking-widest font-mono">
                                Type: {h.type} Rule
                              </p>
                            </>
                          )}
                        </div>
                      </div>
                      {!editingHeuristic && (
                        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={() => {
                              setEditingHeuristic(h.id);
                              setEditValue(h.content);
                            }}
                            className="p-2 hover:bg-white rounded-lg transition-colors text-secondary-text"
                          >
                            <Edit3 className="h-3.5 w-3.5" />
                          </button>
                          <button className="p-2 hover:bg-white hover:text-red-500 rounded-lg transition-colors text-secondary-text">
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <div className="py-12 text-center space-y-2">
                    <Brain className="h-8 w-8 mx-auto text-borders" />
                    <p className="text-xs text-secondary-text italic">
                      No heuristics found for this expert.
                    </p>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="exploits" className="space-y-4">
                {currentSkills.exploits.length > 0 ? (
                  currentSkills.exploits.map((e) => (
                    <div
                      key={e.id}
                      className="p-4 rounded-2xl bg-accent/5 border border-accent/20 flex justify-between items-center"
                    >
                      <div className="flex gap-4 items-center">
                        <div className="p-2 rounded-full bg-accent/10 text-accent">
                          <Target className="h-4 w-4" />
                        </div>
                        <div>
                          <p className="text-sm font-bold text-ink">
                            {e.title}
                          </p>
                          <p className="text-[10px] text-secondary-text">
                            Precedent identified via industrial audit.
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-mono font-bold text-accent">
                          {e.roi}
                        </p>
                        <p className="text-[10px] text-secondary-text uppercase tracking-widest">
                          ROI Benchmark
                        </p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="py-12 text-center space-y-2">
                    <Zap className="h-8 w-8 mx-auto text-borders" />
                    <p className="text-xs text-secondary-text italic">
                      No proven exploits recorded for this expert.
                    </p>
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </div>
        </main>
      </div>
    </div>
  );
}
