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
import { Plus, Trash2 } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { toast } from 'sonner';

export default function BlackBoxPage() {
    const [experiments, setExperiments] = useState<Experiment[]>([]);
    const [learnings, setLearnings] = useState<LearningArtifact[]>([]);
    const [activeCheckin, setActiveCheckin] = useState<Experiment | null>(null);
    const [activeDetail, setActiveDetail] = useState<Experiment | null>(null);
    const [activeEdit, setActiveEdit] = useState<Experiment | null>(null);
    const [showWizard, setShowWizard] = useState(false);

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

    const winner = experiments.find(e => e.status === 'checked_in' && (e.self_report?.outcome === 'great' || e.self_report?.outcome === 'worked'));
    const active = experiments.filter(e => e.status !== 'checked_in');
    const completed = experiments.filter(e => e.status === 'checked_in');

    return (
        <AppLayout>
            <div className="max-w-4xl mx-auto space-y-6 pb-16">
                {/* Header */}
                <div className="flex items-end justify-between pt-2">
                    <div>
                        <h1 className="text-3xl font-display font-semibold tracking-tight text-zinc-900 dark:text-zinc-100">
                            Black Box Z
                        </h1>
                        <p className="text-sm text-zinc-500 font-sans">
                            3 experiments. 1 winner. Every week.
                        </p>
                    </div>

                    <div className="flex items-center gap-2">
                        {experiments.length > 0 && (
                            <Button variant="ghost" onClick={handleClear} className="rounded-lg text-zinc-400 h-9 font-sans hover:text-red-500 hover:bg-red-50">
                                <Trash2 className="w-4 h-4" />
                            </Button>
                        )}
                        <Button onClick={() => setShowWizard(true)} className="rounded-lg bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-white dark:text-zinc-900 h-9 px-4 font-sans">
                            <Plus className="w-4 h-4 mr-1.5" /> New
                        </Button>
                    </div>
                </div>

                {/* Stats */}
                <StatsBar experiments={experiments} />

                {/* Results */}
                <ResultsStrip winner={winner} learnings={learnings} onRunAgain={() => winner && handleDuplicate(winner.id)} />

                {/* Active */}
                {active.length > 0 && (
                    <section className="space-y-3">
                        <h2 className="text-xs font-semibold uppercase tracking-widest text-zinc-400 font-sans">
                            Active <span className="text-zinc-300 dark:text-zinc-600">({active.length})</span>
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

                {/* Completed */}
                {completed.length > 0 && (
                    <section className="space-y-3">
                        <h2 className="text-xs font-semibold uppercase tracking-widest text-zinc-400 font-sans">
                            Completed <span className="text-zinc-300 dark:text-zinc-600">({completed.length})</span>
                        </h2>
                        <ExperimentList
                            experiments={completed}
                            onView={(id) => { const e = experiments.find(x => x.id === id); if (e) setActiveDetail(e); }}
                            onDelete={handleDelete}
                            onDuplicate={handleDuplicate}
                        />
                    </section>
                )}
            </div>

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
                <DialogContent className="max-w-md bg-white dark:bg-zinc-950">
                    <DialogHeader>
                        <DialogTitle className="font-sans">Edit Experiment</DialogTitle>
                    </DialogHeader>
                    {activeEdit && (
                        <div className="space-y-4 py-2">
                            <div className="space-y-2">
                                <label className="text-xs font-medium text-zinc-500 font-sans uppercase">Title</label>
                                <Input
                                    value={activeEdit.title}
                                    onChange={(e) => setActiveEdit({ ...activeEdit, title: e.target.value })}
                                    className="font-sans"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs font-medium text-zinc-500 font-sans uppercase">The Bet</label>
                                <Textarea
                                    value={activeEdit.bet}
                                    onChange={(e) => setActiveEdit({ ...activeEdit, bet: e.target.value })}
                                    className="font-sans resize-none"
                                    rows={3}
                                />
                            </div>
                        </div>
                    )}
                    <DialogFooter>
                        <Button variant="ghost" onClick={() => setActiveEdit(null)} className="font-sans">Cancel</Button>
                        <Button onClick={handleEditSave} className="bg-zinc-900 text-white font-sans">Save Changes</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

        </AppLayout>
    );
}
