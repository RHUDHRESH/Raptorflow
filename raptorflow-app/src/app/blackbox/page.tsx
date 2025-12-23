'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import {
    ExperimentList,
    ResultsStrip,
    CheckinCard,
    BlackBoxWizard,
    StatsBar,
    ExperimentDetail
} from '@/components/blackbox';
import { Experiment, SelfReport, ExperimentStatus, LearningArtifact } from '@/lib/blackbox-types';
import { saveBlackboxState, loadBlackboxState, updateExperiment, addLearning } from '@/lib/blackbox';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Plus, Trash2, Download } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { toast } from 'sonner';

import { BoardroomView } from '@/components/blackbox/BoardroomView';
import { TelemetryFeed } from '@/components/blackbox/TelemetryFeed';
import { EvidenceLog, EvidenceTrace } from '@/components/blackbox/EvidenceLog';
import { AgentAuditLog, AuditEntry } from '@/components/blackbox/AgentAuditLog';
import { Sparkles, Brain, TrendingUp, Terminal } from 'lucide-react';

export default function BlackBoxPage() {
    const [experiments, setExperiments] = useState<Experiment[]>([]);
    const [learnings, setLearnings] = useState<LearningArtifact[]>([]);
    const [activeCheckin, setActiveCheckin] = useState<Experiment | null>(null);
    const [activeDetail, setActiveDetail] = useState<Experiment | null>(null);
    const [activeEdit, setActiveEdit] = useState<Experiment | null>(null);
    const [showWizard, setShowWizard] = useState(false);
    const [evidenceTraces, setEvidenceTraces] = useState<EvidenceTrace[]>([]);
    const [showEvidence, setShowEvidence] = useState(false);
    const [auditEntries, setAuditEntries] = useState<AuditEntry[]>([]);
    const [showAudit, setShowAudit] = useState(false);

    useEffect(() => {
        const state = loadBlackboxState();
        setExperiments(state.experiments);
        setLearnings(state.learnings);
    }, []);

    const saveExperiments = (newExperiments: Experiment[]) => {
        setExperiments(newExperiments);
        const state = loadBlackboxState();
        saveBlackboxState({ ...state, experiments: newExperiments });
    };

    const handleWizardComplete = useCallback((newExps: Experiment[]) => {
        const updated = [...newExps, ...experiments];
        saveExperiments(updated);
        toast.success('3 experiments created');
    }, [experiments]);

    const handleLaunch = useCallback((id: string) => {
        const updated = experiments.map(e =>
            e.id === id ? { ...e, status: 'launched' as ExperimentStatus, launched_at: new Date().toISOString() } : e
        );
        saveExperiments(updated);
        toast.success('Experiment launched');
    }, [experiments]);

    const handleCheckin = useCallback((report: SelfReport) => {
        if (!activeCheckin) return;

        const updatedExps = experiments.map(e =>
            e.id === activeCheckin.id ? { ...e, status: 'checked_in' as ExperimentStatus, self_report: report } : e
        );
        saveExperiments(updatedExps);

        const learning: LearningArtifact = {
            summary: report.outcome === 'great' || report.outcome === 'worked'
                ? `"${activeCheckin.title}" worked for ${activeCheckin.goal}.`
                : `"${activeCheckin.title}" underperformed.`,
            skill_weight_deltas: []
        };
        addLearning(learning);
        setLearnings(prev => [learning, ...prev]);
        setActiveCheckin(null);
        toast.success('Check-in recorded');
    }, [activeCheckin, experiments]);

    const handleDelete = useCallback((id: string) => {
        const updated = experiments.filter(e => e.id !== id);
        saveExperiments(updated);
        toast.success('Experiment deleted');
    }, [experiments]);

    const handleDuplicate = useCallback((id: string) => {
        const exp = experiments.find(e => e.id === id);
        if (!exp) return;
        const dup = { ...exp, id: `exp-${Date.now()}`, status: 'draft' as ExperimentStatus, created_at: new Date().toISOString(), launched_at: undefined, self_report: undefined };
        const updated = [dup, ...experiments];
        saveExperiments(updated);
        toast.success('Experiment duplicated');
    }, [experiments]);

    const handleMove = useCallback((id: string, direction: 'up' | 'down') => {
        const index = experiments.findIndex(e => e.id === id);
        if (index === -1) return;

        const newExperiments = [...experiments];
        const targetIndex = direction === 'up' ? index - 1 : index + 1;

        if (targetIndex >= 0 && targetIndex < newExperiments.length) {
            [newExperiments[index], newExperiments[targetIndex]] = [newExperiments[targetIndex], newExperiments[index]];
            saveExperiments(newExperiments);
        }
    }, [experiments]);

    const handleEditSave = () => {
        if (!activeEdit) return;
        const updated = experiments.map(e => e.id === activeEdit.id ? activeEdit : e);
        saveExperiments(updated);
        setActiveEdit(null);
        toast.success('Experiment updated');
    };

    const handleClear = useCallback(() => {
        if (confirm('Are you sure you want to delete all experiments?')) {
            saveExperiments([]);
            setLearnings([]);
            saveBlackboxState({ experiments: [], learnings: [], skill_weights: {} });
            toast.success('All cleared');
        }
    }, []);

    const handleViewEvidence = () => {
        // Mock data for evidence traces (Task 81)
        const mockTraces: EvidenceTrace[] = [
            {
                id: 'tr-1',
                agent_id: 'researcher_scraper',
                trace: { output: { url: 'https://www.linkedin.com/pulse/b2b-marketing-trends-2025' } },
                latency: 1.2,
                timestamp: new Date().toISOString()
            },
            {
                id: 'tr-2',
                agent_id: 'researcher_search',
                trace: { output: { url: 'https://hbr.org/2024/05/the-new-linkedin-algorithm' } },
                latency: 0.8,
                timestamp: new Date().toISOString()
            }
        ];
        setEvidenceTraces(mockTraces);
        setShowEvidence(true);
    };

    const handleViewAuditLog = () => {
        // ... mock entries ...
        setAuditEntries(mockEntries);
        setShowAudit(true);
    };

    const handleExportPDF = () => {
        toast.promise(
            new Promise((resolve) => setTimeout(resolve, 1500)),
            {
                loading: 'Generating Strategic Summary PDF...',
                success: 'Blackbox_Summary_Dec2025.pdf exported successfully',
                error: 'Failed to export PDF',
            }
        );
        // In a real app, this would use a library like jspdf or a server-side PDF generator
        window.print();
    };

    const winner = experiments.find(e => e.status === 'checked_in' && (e.self_report?.outcome === 'great' || e.self_report?.outcome === 'worked'));
    const active = experiments.filter(e => e.status !== 'checked_in');
    const completed = experiments.filter(e => e.status === 'checked_in');

    return (
        <AppLayout>
            <div className="max-w-6xl mx-auto space-y-10 pb-20">
                {/* Executive Header */}
                <div className="flex items-end justify-between border-b border-border pb-6 pt-2">
                    <div>
                        <h1 className="text-4xl font-display font-semibold tracking-tight text-foreground flex items-center gap-3">
                            Blackbox <span className="text-accent/50 italic font-medium text-3xl px-2 py-0.5 rounded bg-accent/5 border border-accent/10">Industrial</span>
                        </h1>
                        <p className="text-sm text-muted-foreground font-sans mt-2 max-w-md">
                            The industrial intelligence engine. Outcomes tracked, insights extracted, strategy hardened by evidence.
                        </p>
                    </div>

                    <div className="flex items-center gap-3">
                        <Button
                            variant="outline"
                            onClick={handleExportPDF}
                            className="rounded-lg text-muted-foreground h-10 px-4 font-sans hover:text-accent hover:bg-accent/5"
                        >
                            <Download className="w-4 h-4 mr-2" /> Export Summary
                        </Button>
                        {experiments.length > 0 && (
                            <Button variant="ghost" onClick={handleClear} className="rounded-lg text-muted-foreground h-10 font-sans hover:text-red-500 hover:bg-red-50/10">
                                <Trash2 className="w-4 h-4" />
                            </Button>
                        )}
                        <Button onClick={() => setShowWizard(true)} className="rounded-xl bg-foreground text-background hover:bg-foreground/90 h-10 px-6 font-sans font-medium tracking-tight">
                            <Plus className="w-4 h-4 mr-2" /> New Experiment
                        </Button>
                    </div>
                </div>

                {/* SOTA Stats Grid */}
                <BoardroomView />

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Left: Experimental Flywheel */}
                    <div className="lg:col-span-2 space-y-8">
                        {/* Results Strip (Hero learning) */}
                        <ResultsStrip winner={winner} learnings={learnings} onRunAgain={() => winner && handleDuplicate(winner.id)} />

                        {/* Strategic Insights / Pivots (Task 78) */}
                        <section className="space-y-4">
                            <div className="flex items-center gap-2 mb-2">
                                <Sparkles className="h-4 w-4 text-accent" />
                                <h2 className="text-sm font-semibold uppercase tracking-widest text-muted-foreground font-sans">
                                    Strategic Pivots
                                </h2>
                            </div>
                            <div className="grid gap-4">
                                <div className="p-6 rounded-2xl border border-accent/20 bg-accent/5 backdrop-blur-sm relative overflow-hidden group">
                                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                                        <Brain size={80} />
                                    </div>
                                    <div className="flex items-start gap-4">
                                        <div className="h-10 w-10 rounded-full bg-accent flex items-center justify-center text-accent-foreground shrink-0 shadow-lg shadow-accent/20">
                                            <TrendingUp size={20} />
                                        </div>
                                        <div className="space-y-1">
                                            <h3 className="font-semibold text-lg font-sans">Scale B2B SaaS Reach via LinkedIn</h3>
                                            <p className="text-sm text-muted-foreground font-sans leading-relaxed">
                                                Based on the last 4 experiments, LinkedIn Organic outreach has 3.2x higher conversion than cold email.
                                                Recommendation: Shift 40% of email budget to LinkedIn Content Engine.
                                            </p>
                                            <div className="pt-4 flex items-center gap-3">
                                                <Button size="sm" className="rounded-lg h-8 bg-foreground text-background px-4 font-sans text-xs">Apply Pivot</Button>
                                                <Button
                                                    size="sm"
                                                    variant="outline"
                                                    className="rounded-lg h-8 px-4 font-sans text-xs border-border"
                                                    onClick={handleViewEvidence}
                                                >
                                                    View Evidence
                                                </Button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </section>

                        {/* Active Experiments */}
                        {active.length > 0 && (
                            <section className="space-y-4 pt-4">
                                <h2 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground font-sans px-1">
                                    Active Flywheel <span className="text-muted-foreground/40 font-mono ml-1">[{active.length}]</span>
                                </h2>
                                <ExperimentList
                                    experiments={active}
                                    onLaunch={handleLaunch}
                                    onSwap={() => toast('Swap coming soon')}
                                    onCheckin={(id) => { const e = experiments.find(x => x.id === id); if (e) setActiveCheckin(e); }}
                                    onView={(id) => { const e = experiments.find(x => x.id === id); if (e) setActiveDetail(e); }}
                                    onDelete={handleDelete}
                                    onDuplicate={handleDuplicate}
                                    onMove={handleMove}
                                    onEdit={(id) => setActiveEdit(experiments.find(e => e.id === id) || null)}
                                />
                            </section>
                        )}
                    </div>

                    {/* Right: Monitoring & Logs */}
                    <div className="space-y-8">
                        {/* Live Telemetry (Task 74) */}
                        <div className="space-y-4">
                            <div className="flex items-center justify-between px-1">
                                <h2 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground font-sans">
                                    Live Telemetry
                                </h2>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    className="h-6 px-2 text-[10px] font-mono text-muted-foreground hover:text-accent"
                                    onClick={handleViewAuditLog}
                                >
                                    <Terminal size={12} className="mr-1" /> View Audit Log
                                </Button>
                            </div>
                            <TelemetryFeed />
                        </div>

                        {/* Completed Experiments */}
                        {completed.length > 0 && (
                            <section className="space-y-4">
                                <h2 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground font-sans px-1">
                                    History
                                </h2>
                                <div className="opacity-80 scale-95 origin-top">
                                    <ExperimentList
                                        experiments={completed}
                                        onView={(id) => { const e = experiments.find(x => x.id === id); if (e) setActiveDetail(e); }}
                                        onDelete={handleDelete}
                                        onDuplicate={handleDuplicate}
                                    />
                                </div>
                            </section>
                        )}
                    </div>
                </div>
            </div>

            {/* Modals & Wizards */}
            <BlackBoxWizard open={showWizard} onOpenChange={setShowWizard} onComplete={handleWizardComplete} />

            <ExperimentDetail
                experiment={activeDetail}
                open={!!activeDetail}
                onOpenChange={(o) => !o && setActiveDetail(null)}
                onLaunch={handleLaunch}
                onCheckin={(id) => { const e = experiments.find(x => x.id === id); if (e) { setActiveDetail(null); setActiveCheckin(e); } }}
            />

            {/* Check-in Modal */}
            <Dialog open={!!activeCheckin} onOpenChange={(o) => !o && setActiveCheckin(null)}>
                <DialogContent className="p-0 bg-transparent border-none shadow-none max-w-md">
                    {activeCheckin && <CheckinCard experiment={activeCheckin} onSubmit={handleCheckin} onCancel={() => setActiveCheckin(null)} />}
                </DialogContent>
            </Dialog>

            {/* Edit Modal */}
            <Dialog open={!!activeEdit} onOpenChange={(o) => !o && setActiveEdit(null)}>
                <DialogContent className="max-w-md bg-background border-border">
                    <DialogHeader>
                        <DialogTitle className="font-sans font-semibold">Edit Experiment</DialogTitle>
                    </DialogHeader>
                    {activeEdit && (
                        <div className="space-y-4 py-2">
                            <div className="space-y-2">
                                <label className="text-xs font-semibold text-muted-foreground font-sans uppercase tracking-tighter">Title</label>
                                <Input
                                    value={activeEdit.title}
                                    onChange={(e) => setActiveEdit({ ...activeEdit, title: e.target.value })}
                                    className="font-sans rounded-lg border-border"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs font-semibold text-muted-foreground font-sans uppercase tracking-tighter">The Bet</label>
                                <Textarea
                                    value={activeEdit.bet}
                                    onChange={(e) => setActiveEdit({ ...activeEdit, bet: e.target.value })}
                                    className="font-sans resize-none rounded-lg border-border"
                                    rows={3}
                                />
                            </div>
                        </div>
                    )}
                    <DialogFooter>
                        <Button variant="ghost" onClick={() => setActiveEdit(null)} className="font-sans rounded-lg">Cancel</Button>
                        <Button onClick={handleEditSave} className="bg-foreground text-background font-sans font-semibold rounded-lg tracking-tight">Save Changes</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Evidence Dialog (Task 81) */}
            <Dialog open={showEvidence} onOpenChange={setShowEvidence}>
                <DialogContent className="max-w-2xl bg-background border-border overflow-hidden flex flex-col max-h-[80vh]">
                    <DialogHeader className="pb-4">
                        <DialogTitle className="font-sans font-semibold flex items-center gap-2">
                            <FileText className="h-5 w-5 text-accent" />
                            Strategic Evidence
                        </DialogTitle>
                        <p className="text-sm text-muted-foreground font-sans">
                            Raw intelligence retrieved by agents to support this pivot.
                        </p>
                    </DialogHeader>
                    <div className="flex-1 overflow-y-auto pr-2 -mr-2">
                        <EvidenceLog traces={evidenceTraces} />
                    </div>
                    <DialogFooter className="pt-4 border-t border-border mt-2">
                        <Button variant="ghost" onClick={() => setShowEvidence(false)} className="font-sans rounded-lg">Close</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Audit Log Dialog (Task 82) */}
            <Dialog open={showAudit} onOpenChange={setShowAudit}>
                <DialogContent className="max-w-4xl bg-background border-border overflow-hidden flex flex-col h-[85vh]">
                    <DialogHeader className="pb-4">
                        <DialogTitle className="font-sans font-semibold flex items-center gap-2">
                            <Terminal className="h-5 w-5 text-accent" />
                            Agent Audit Log
                        </DialogTitle>
                        <p className="text-sm text-muted-foreground font-sans">
                            Deep inspection of raw agent inputs, tool calls, and LLM responses.
                        </p>
                    </DialogHeader>
                    <div className="flex-1 overflow-y-auto pr-2 -mr-2">
                        <AgentAuditLog entries={auditEntries} />
                    </div>
                    <DialogFooter className="pt-4 border-t border-border mt-2">
                        <Button variant="ghost" onClick={() => setShowAudit(false)} className="font-sans rounded-lg">Close Audit Log</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

        </AppLayout>
    );
}
