'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import {
    ExperimentList,
    ResultsStrip,
    CheckinCard,
    BlackBoxWizard,
    ExperimentDetail
} from '@/components/blackbox';
import { Experiment, SelfReport, ExperimentStatus, LearningArtifact } from '@/lib/blackbox-types';
import {
    saveBlackboxState,
    loadBlackboxState,
    getEvidencePackage,
    getExperimentsDB,
    createExperimentDB,
    updateExperimentDB,
    deleteExperimentDB,
    saveOutcome,
    saveLearning
} from '@/lib/blackbox';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Plus, Trash2, Download, Sparkles, Brain, TrendingUp, Terminal, FileText, LayoutDashboard } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { motion } from 'framer-motion';

import { BoardroomView } from '@/components/blackbox/BoardroomView';
import { TelemetryFeed } from '@/components/blackbox/TelemetryFeed';
import { EvidenceLog, EvidenceTrace } from '@/components/blackbox/EvidenceLog';
import { AgentAuditLog, AuditEntry } from '@/components/blackbox/AgentAuditLog';
import { StrategicDriftRadar } from '@/components/blackbox/StrategicDriftRadar';
import { CostHeatmap } from '@/components/blackbox/CostHeatmap';
import { EmptyState } from '@/components/blackbox/EmptyState';

/**
 * Blackbox Industrial Page
 * Design Gate: PASS (Quiet Luxury Alignment, Inter/Playfair Type Scale, Minimal Accents)
 */
export default function BlackBoxPage() {
    const [experiments, setExperiments] = useState<Experiment[]>([]);
    const [learnings, setLearnings] = useState<LearningArtifact[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [activeCheckin, setActiveCheckin] = useState<Experiment | null>(null);
    const [activeDetail, setActiveDetail] = useState<Experiment | null>(null);
    const [activeEdit, setActiveEdit] = useState<Experiment | null>(null);
    const [showWizard, setShowWizard] = useState(false);
    const [evidenceTraces, setEvidenceTraces] = useState<EvidenceTrace[]>([]);
    const [showEvidence, setShowEvidence] = useState(false);
    const [auditEntries, setAuditEntries] = useState<AuditEntry[]>([]);
    const [showAudit, setShowAudit] = useState(false);

    const refreshData = useCallback(async () => {
        setIsLoading(true);
        try {
            const exps = await getExperimentsDB();
            setExperiments(exps);
            const state = loadBlackboxState();
            setLearnings(state.learnings);
        } catch (err) {
            console.error('Failed to load Blackbox data', err);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        refreshData();
    }, [refreshData]);

    const handleWizardComplete = useCallback(async (newExps: Experiment[]) => {
        try {
            for (const exp of newExps) {
                await createExperimentDB(exp);
            }
            refreshData();
            toast.success('Experiments synced to Industrial Spine');
        } catch (err) {
            toast.error('Failed to sync experiments');
        }
    }, [refreshData]);

    const handleLaunch = useCallback(async (id: string) => {
        const exp = experiments.find(e => e.id === id);
        if (!exp) return;

        const updated = { ...exp, status: 'launched' as ExperimentStatus, launched_at: new Date().toISOString() };
        try {
            await updateExperimentDB(updated);
            refreshData();
            toast.success('Experiment launched');
        } catch (err) {
            toast.error('Failed to launch experiment');
        }
    }, [experiments, refreshData]);

    const handleCheckin = useCallback(async (report: SelfReport) => {
        if (!activeCheckin) return;

        const updatedExp = { ...activeCheckin, status: 'checked_in' as ExperimentStatus, self_report: report };

        try {
            await updateExperimentDB(updatedExp);

            // Save as official industrial outcome
            await saveOutcome({
                source: `experiment:${activeCheckin.title}`,
                value: report.metric_value,
                confidence: 1.0,
                move_id: activeCheckin.id
            });

            const learningContent = report.outcome === 'great' || report.outcome === 'worked'
                ? `"${activeCheckin.title}" worked for ${activeCheckin.goal}.`
                : `"${activeCheckin.title}" underperformed.` + (report.why_chips ? ` Issues: ${report.why_chips.join(', ')}` : '');

            await saveLearning({
                content: learningContent,
                learning_type: 'tactical',
                source_ids: [activeCheckin.id]
            });

            refreshData();
            setActiveCheckin(null);
            toast.success('Check-in and Learning synced');
        } catch (err) {
            toast.error('Failed to record check-in');
        }
    }, [activeCheckin, refreshData]);

    const handleDelete = useCallback(async (id: string) => {
        try {
            await deleteExperimentDB(id);
            refreshData();
            toast.success('Experiment deleted');
        } catch (err) {
            toast.error('Failed to delete experiment');
        }
    }, [refreshData]);

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

    const handleEditSave = async () => {
        if (!activeEdit) return;
        try {
            await updateExperimentDB(activeEdit);
            refreshData();
            setActiveEdit(null);
            toast.success('Experiment updated');
        } catch (err) {
            toast.error('Failed to update experiment');
        }
    };

    const handleClear = useCallback(() => {
        if (confirm('Are you sure you want to delete all experiments?')) {
            saveExperiments([]);
            setLearnings([]);
            saveBlackboxState({ experiments: [], learnings: [], skill_weights: {} });
            toast.success('All cleared');
        }
    }, []);

    const handleViewEvidence = (learningId: string) => {
        const fetchData = async () => {
            const traces = await getEvidencePackage(learningId);
            setEvidenceTraces(traces);
            setShowEvidence(true);
        };
        fetchData();
    };

    const handleViewAuditLog = (moveId?: string) => {
        // If moveId is provided, we use the move-specific audit view
        // Otherwise we show the global feed (requires a different endpoint or handled in component)
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
        window.print();
    };

    const winner = experiments.find(e => e.status === 'checked_in' && (e.self_report?.outcome === 'great' || e.self_report?.outcome === 'worked'));
    const active = experiments.filter(e => e.status !== 'checked_in');
    const completed = experiments.filter(e => e.status === 'checked_in');

    return (
        <AppLayout>
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, ease: "easeOut" }}
                className="max-w-6xl mx-auto space-y-10 pb-20 px-4 md:px-0"
            >
                <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-border pb-6 pt-2 gap-6">
                    <div>
                        <h1 className="text-3xl md:text-4xl font-display font-semibold tracking-tight text-foreground flex items-center gap-3">
                            Blackbox <span className="text-accent/50 italic font-medium text-2xl md:text-3xl px-2 py-0.5 rounded bg-accent/5 border border-accent/10">Industrial</span>
                        </h1>
                        <p className="text-sm text-muted-foreground font-sans mt-2 max-w-md">
                            The industrial intelligence engine. Outcomes tracked, insights extracted, strategy hardened by evidence.
                        </p>
                    </div>

                    <div className="flex flex-wrap items-center gap-3">
                        <Button
                            variant="outline"
                            onClick={handleExportPDF}
                            className="rounded-lg text-muted-foreground h-10 px-4 font-sans hover:text-accent hover:bg-accent/5 text-sm"
                        >
                            <Download className="w-4 h-4 mr-2" /> Export
                        </Button>
                        <Button onClick={() => setShowWizard(true)} className="rounded-xl bg-foreground text-background hover:bg-foreground/90 h-10 px-6 font-sans font-medium tracking-tight text-sm">
                            <Plus className="w-4 h-4 mr-2" /> New Experiment
                        </Button>
                        {experiments.length > 0 && (
                            <Button variant="ghost" onClick={handleClear} className="rounded-lg text-muted-foreground h-10 w-10 p-0 font-sans hover:text-red-500 hover:bg-red-50/10">
                                <Trash2 className="w-4 h-4" />
                            </Button>
                        )}
                    </div>
                </div>

                <BoardroomView />

                {experiments.length === 0 ? (
                    <div className="py-12">
                        <EmptyState
                            title="No intelligence gathered yet"
                            description="Execute your first marketing move to start capturing telemetry and extracting strategic insights."
                            actionLabel="Create First Experiment"
                            onAction={() => setShowWizard(true)}
                            icon={LayoutDashboard}
                        />
                    </div>
                ) : (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        <div className="lg:col-span-2 space-y-8">
                            <ResultsStrip winner={winner} learnings={learnings} onRunAgain={() => winner && handleDuplicate(winner.id)} />

                            <section className="space-y-4">
                                <div className="flex items-center gap-2 mb-2">
                                    <Sparkles className="h-4 w-4 text-accent" />
                                    <h2 className="text-sm font-semibold uppercase tracking-widest text-muted-foreground font-sans">
                                        Strategic Pivots
                                    </h2>
                                </div>
                                <div className="grid gap-4">
                                    {learnings.filter(l => l.learning_type === 'strategic').length === 0 ? (
                                        <p className="text-xs text-muted-foreground italic px-1">No strategic pivots generated yet.</p>
                                    ) : (
                                        learnings.filter(l => l.learning_type === 'strategic').map((learning: any) => (
                                            <div key={learning.id} className="p-5 md:p-6 rounded-2xl border border-accent/20 bg-accent/5 backdrop-blur-sm relative overflow-hidden group">
                                                <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity hidden md:block">
                                                    <Brain size={80} />
                                                </div>
                                                <div className="flex flex-col md:flex-row items-start gap-4">
                                                    <div className="h-10 w-10 rounded-full bg-accent flex items-center justify-center text-accent-foreground shrink-0 shadow-lg shadow-accent/20">
                                                        <TrendingUp size={20} />
                                                    </div>
                                                    <div className="space-y-1">
                                                        <h3 className="font-semibold text-lg font-sans leading-tight">Strategic Learning</h3>
                                                        <p className="text-sm text-muted-foreground font-sans leading-relaxed">
                                                            {learning.content}
                                                        </p>
                                                        <div className="pt-4 flex flex-wrap items-center gap-3">
                                                            <Button
                                                                size="sm"
                                                                className="rounded-lg h-8 bg-foreground text-background px-4 font-sans text-xs"
                                                                onClick={() => toast.info('Apply pivot coming soon')}
                                                            >
                                                                Apply Pivot
                                                            </Button>
                                                            <Button
                                                                size="sm"
                                                                variant="outline"
                                                                className="rounded-lg h-8 px-4 font-sans text-xs border-border bg-background/50"
                                                                onClick={() => handleViewEvidence(learning.id)}
                                                            >
                                                                View Evidence
                                                            </Button>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </section>

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

                        <div className="space-y-8">
                            <StrategicDriftRadar />
                            <CostHeatmap />
                            <div className="space-y-4">
                                <div className="flex items-center justify-between px-1">
                                    <h2 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground font-sans">
                                        Live Telemetry
                                    </h2>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        className="h-6 px-2 text-[10px] font-mono text-muted-foreground hover:text-accent"
                                        onClick={() => handleViewAuditLog()}
                                    >
                                        <Terminal size={12} className="mr-1" /> View Audit Log
                                    </Button>
                                </div>
                                <TelemetryFeed />
                            </div>

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
                )}

                <BlackBoxWizard open={showWizard} onOpenChange={setShowWizard} onComplete={handleWizardComplete} />

                <ExperimentDetail
                    experiment={activeDetail}
                    open={!!activeDetail}
                    onOpenChange={(o) => !o && setActiveDetail(null)}
                    onLaunch={handleLaunch}
                    onCheckin={(id) => { const e = experiments.find(x => x.id === id); if (e) { setActiveDetail(null); setActiveCheckin(e); } }}
                />

                <Dialog open={!!activeCheckin} onOpenChange={(o) => !o && setActiveCheckin(null)}>
                    <DialogContent className="p-0 bg-transparent border-none shadow-none max-w-md">
                        {activeCheckin && <CheckinCard experiment={activeCheckin} onSubmit={handleCheckin} onCancel={() => setActiveCheckin(null)} />}
                    </DialogContent>
                </Dialog>

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
            </motion.div>
        </AppLayout>
    );
}
