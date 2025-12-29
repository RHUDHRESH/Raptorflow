'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowRight,
  ArrowLeft,
  Sparkles,
  Target,
  Zap,
  BrainCircuit,
  CheckCircle2,
  AlertTriangle,
  TrendingUp,
  ChevronDown,
  ChevronUp,
  X,
  Loader2,
  Edit2,
  Trash2,
  Calendar,
  History,
  Quote,
  XCircle,
} from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import {
  generateCouncilPlan,
  persistCouncilCampaign,
  persistCouncilMoves,
} from '@/lib/api';
import { CouncilResponse, CouncilMoveSuggestion } from '@/lib/campaigns-types';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { EXPERTS } from '../council/CouncilChamber';

// ==========================================
// Types
// ==========================================

type WizardType = 'move' | 'campaign';

interface MoveCampaignWizardProps {
  open?: boolean; // Optional to support conditional rendering from parent
  onClose: () => void;
  onSuccess?: () => void;
}

// ==========================================
// Main Component
// ==========================================

export function MoveCampaignWizard({
  open = true, // Default to true if not provided (legacy behavior)
  onClose,
  onSuccess,
}: MoveCampaignWizardProps) {
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [type, setType] = useState<WizardType>('move');

  // Form State
  const [objective, setObjective] = useState('');
  const [context, setContext] = useState('');

  // API State
  const [isLoading, setIsLoading] = useState(false);
  const [councilResponse, setCouncilResponse] =
    useState<CouncilResponse | null>(null);
  const [editedMoves, setEditedMoves] = useState<CouncilMoveSuggestion[]>([]);
  const [rawPlan, setRawPlan] = useState<any>(null);

  // Step 1: Selection
  const handleTypeSelect = (selected: WizardType) => {
    setType(selected);
  };

  // Step 2: Validation
  const canProceedToPreview =
    objective.trim().length > 5 && context.trim().length > 5;

  // Step 2 -> 3: Generate
  const handleGenerate = async () => {
    if (!canProceedToPreview) return;

    setIsLoading(true);
    setStep(3);

    try {
      const plan = await generateCouncilPlan({
        type,
        objective,
        context,
      });
      setCouncilResponse(plan.view);
      setRawPlan(plan.raw);
      if (plan.view.moves) setEditedMoves(plan.view.moves);
      if (plan.view.campaignMoves) setEditedMoves(plan.view.campaignMoves);
    } catch (error) {
      console.error(error);
      toast.error('The Council is silent. Please try again.');
      setStep(2);
    } finally {
      setIsLoading(false);
    }
  };

  // Step 3 Actions
  const handleUpdateMove = (
    id: string,
    updates: Partial<CouncilMoveSuggestion>
  ) => {
    setEditedMoves((prev) =>
      prev.map((m) => (m.id === id ? { ...m, ...updates } : m))
    );
  };

  const handleDeleteMove = (id: string) => {
    setEditedMoves((prev) => prev.filter((m) => m.id !== id));
  };

  const handleConfirm = async () => {
    setIsLoading(true);
    try {
      if (!rawPlan) {
        throw new Error('Council plan missing.');
      }
      if (type === 'move') {
        await persistCouncilMoves(rawPlan, editedMoves);
        toast.success('Strategy Executed', {
          description: `${editedMoves.length} moves queued for execution.`,
        });
      } else {
        await persistCouncilCampaign(rawPlan, editedMoves);
        toast.success('Campaign Initialized', {
          description: 'Strategic arc locked. Phase 1 active.',
        });
      }
      if (onSuccess) onSuccess();
      onClose();
    } catch (error) {
      toast.error('Failed to execute decree.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="w-full max-w-4xl max-h-[90vh] bg-canvas border border-borders rounded-2xl shadow-2xl overflow-hidden flex flex-col"
          >
            {/* Header */}
            <div className="px-8 py-5 border-b border-borders bg-surface flex items-center justify-between shrink-0">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-background border border-borders rounded-lg">
                  <Sparkles className="w-4 h-4 text-ink" />
                </div>
                <div>
                  <h2 className="text-sm font-bold uppercase tracking-widest text-ink">
                    Mission Control
                  </h2>
                  <p className="text-xs text-secondary-text">
                    Step {step} of 3 • {type === 'move' ? 'Move' : 'Campaign'} Generator
                  </p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 text-muted-foreground hover:text-ink hover:bg-muted/50 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-8 bg-canvas">
              <AnimatePresence mode="wait">
                {step === 1 && (
                  <StepTypeSelection
                    key="step1"
                    selected={type}
                    onSelect={handleTypeSelect}
                    onNext={() => setStep(2)}
                  />
                )}
                {step === 2 && (
                  <StepInput
                    key="step2"
                    type={type}
                    objective={objective}
                    context={context}
                    setObjective={setObjective}
                    setContext={setContext}
                    onNext={handleGenerate}
                    onBack={() => setStep(1)}
                    isValid={canProceedToPreview}
                  />
                )}
                {step === 3 && (
                  <StepCouncilPreview
                    key="step3"
                    type={type}
                    isLoading={isLoading}
                    data={councilResponse}
                    moves={editedMoves}
                    onUpdateMove={handleUpdateMove}
                    onDeleteMove={handleDeleteMove}
                    onConfirm={handleConfirm}
                    onBack={() => setStep(2)}
                  />
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}

// ==========================================
// Sub-Components
// ==========================================

function StepTypeSelection({
  selected,
  onSelect,
  onNext,
}: {
  selected: WizardType;
  onSelect: (t: WizardType) => void;
  onNext: () => void;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="max-w-2xl mx-auto space-y-10"
    >
      <div className="text-center space-y-3">
        <h1 className="text-3xl md:text-4xl font-serif text-ink">
          Choose Your Initiative
        </h1>
        <p className="text-secondary-text text-lg font-light">
          Are you executing a tactical strike or orchestrating a war?
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <button
          onClick={() => onSelect('move')}
          className={cn(
            'relative p-8 rounded-2xl border-2 text-left transition-all duration-300 group overflow-hidden',
            selected === 'move'
              ? 'border-ink bg-surface shadow-lg'
              : 'border-borders bg-white hover:border-ink/30'
          )}
        >
          <div className="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity">
            <Zap className="w-24 h-24 text-ink/5 -rotate-12 translate-x-4 -translate-y-4" />
          </div>

          <div className="relative z-10 space-y-4">
            <div className={cn(
              "w-12 h-12 rounded-xl border flex items-center justify-center transition-colors",
              selected === 'move'
                ? "bg-ink border-ink text-white"
                : "bg-surface border-borders text-ink"
            )}>
              <Zap className="w-6 h-6" />
            </div>

            <div>
              <h3 className="text-xl font-bold text-ink mb-2">Single Move</h3>
              <p className="text-sm text-secondary-text leading-relaxed">
                A focused, tactical sprint (7-14 days). Best for testing a single hypothesis or executing a discrete outcome.
              </p>
            </div>

            <div className="pt-2 flex flex-wrap gap-2 pointer-events-none">
              <span className="text-[10px] font-mono uppercase px-2 py-1 bg-muted rounded text-muted-foreground">Quick Win</span>
              <span className="text-[10px] font-mono uppercase px-2 py-1 bg-muted rounded text-muted-foreground">High Velocity</span>
            </div>
          </div>
        </button>

        <button
          onClick={() => onSelect('campaign')}
          className={cn(
            'relative p-8 rounded-2xl border-2 text-left transition-all duration-300 group overflow-hidden',
            selected === 'campaign'
              ? 'border-ink bg-surface shadow-lg'
              : 'border-borders bg-white hover:border-ink/30'
          )}
        >
          <div className="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity">
            <Target className="w-24 h-24 text-ink/5 -rotate-12 translate-x-4 -translate-y-4" />
          </div>

          <div className="relative z-10 space-y-4">
            <div className={cn(
              "w-12 h-12 rounded-xl border flex items-center justify-center transition-colors",
              selected === 'campaign'
                ? "bg-ink border-ink text-white"
                : "bg-surface border-borders text-ink"
            )}>
              <Target className="w-6 h-6" />
            </div>

            <div>
              <h3 className="text-xl font-bold text-ink mb-2">Full Campaign</h3>
              <p className="text-sm text-secondary-text leading-relaxed">
                A multi-phase strategic arc (4-12 weeks). Coordinates multiple moves to achieve a major business objective.
              </p>
            </div>

            <div className="pt-2 flex flex-wrap gap-2 pointer-events-none">
              <span className="text-[10px] font-mono uppercase px-2 py-1 bg-muted rounded text-muted-foreground">Deep Strategy</span>
              <span className="text-[10px] font-mono uppercase px-2 py-1 bg-muted rounded text-muted-foreground">Compound Growth</span>
            </div>
          </div>
        </button>
      </div>

      <div className="flex justify-end pt-8">
        <Button
          onClick={onNext}
          className="h-12 px-8 rounded-xl bg-ink text-white font-medium text-base hover:bg-ink/90 transition-all shadow-md hover:shadow-lg hover:-translate-y-0.5"
        >
          Next Step <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </div>
    </motion.div>
  );
}

function StepInput({
  type,
  objective,
  context,
  setObjective,
  setContext,
  onNext,
  onBack,
  isValid,
}: {
  type: WizardType;
  objective: string;
  context: string;
  setObjective: (v: string) => void;
  setContext: (v: string) => void;
  onNext: () => void;
  onBack: () => void;
  isValid: boolean;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="max-w-2xl mx-auto space-y-8"
    >
      <div className="space-y-2">
        <h2 className="text-3xl font-serif text-ink">
          {type === 'move' ? 'Define Your Move' : 'Architect the Campaign'}
        </h2>
        <p className="text-secondary-text">
          Provide high-level directives. The Council will handle the strategy.
        </p>
      </div>

      <div className="space-y-8">
        <div className="space-y-3">
          <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground">
            {type === 'move'
              ? 'Primary Objective'
              : 'North Star Objective'}
          </label>
          <Input
            value={objective}
            onChange={(e) => setObjective(e.target.value)}
            placeholder={
              type === 'move'
                ? 'e.g., Generate 10 qualified leads for the Enterprise tier this week'
                : 'e.g., Establish market dominance in the AI-legal sector within Q1'
            }
            className="h-14 px-4 bg-surface border-borders text-lg font-medium focus:ring-1 focus:ring-ink transition-all"
          />
        </div>

        <div className="space-y-3">
          <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground">
            {type === 'move'
              ? 'Context & Constraints'
              : 'Target Audience & Market Context'}
          </label>
          <Textarea
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="e.g., Targeting Series A founders who are struggling with [problem]. Budget is tight, so prioritizing organic channels. We have a strong whitepaper we can leverage."
            className="min-h-[200px] p-4 bg-surface border-borders text-base leading-relaxed focus:ring-1 focus:ring-ink transition-all resize-none"
          />
        </div>
      </div>

      <div className="flex justify-between pt-8 border-t border-borders/50">
        <Button
          variant="ghost"
          onClick={onBack}
          className="text-secondary-text hover:text-ink hover:bg-transparent"
        >
          <ArrowLeft className="w-4 h-4 mr-2" /> Back
        </Button>
        <Button
          onClick={onNext}
          disabled={!isValid}
          className="h-12 px-8 rounded-xl bg-ink text-white font-medium text-base hover:bg-black transition-all shadow-md disabled:opacity-50"
        >
          Summon Council <BrainCircuit className="w-4 h-4 ml-2" />
        </Button>
      </div>
    </motion.div>
  );
}

function StepCouncilPreview({
  type,
  isLoading,
  data,
  moves,
  onUpdateMove,
  onDeleteMove,
  onConfirm,
  onBack,
}: {
  type: WizardType;
  isLoading: boolean;
  data: CouncilResponse | null;
  moves: CouncilMoveSuggestion[];
  onUpdateMove: (id: string, updates: Partial<CouncilMoveSuggestion>) => void;
  onDeleteMove: (id: string) => void;
  onConfirm: () => void;
  onBack: () => void;
}) {
  const [showDebate, setShowDebate] = useState(false);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-[500px] space-y-8">
        <div className="relative">
          <div className="absolute inset-0 bg-accent/20 rounded-full blur-xl animate-pulse" />
          <Loader2 className="w-16 h-16 text-ink animate-spin relative z-10" />
        </div>

        <div className="text-center space-y-2">
          <p className="font-serif text-2xl text-ink animate-pulse">
            The Council is Deliberating...
          </p>
          <p className="text-secondary-text max-w-sm mx-auto">
            Analyzing market signals, competitor movements, and historical performance data.
          </p>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      className="max-w-3xl mx-auto pb-10 space-y-12"
    >
      {/* Header / Decree */}
      <section className="space-y-4">
        <div className="flex items-center gap-2 mb-2">
          <BrainCircuit className="w-5 h-5 text-accent-foreground" />
          <span className="text-xs font-bold uppercase tracking-widest text-secondary-text">Strategic Decree</span>
        </div>

        <div className="bg-surface p-8 rounded-2xl border border-borders shadow-sm relative overflow-hidden">
          <Quote className="absolute top-4 right-6 w-10 h-10 text-borders/50" />
          <div className="relative z-10 space-y-6">
            <h3 className="font-serif text-2xl md:text-3xl text-ink italic leading-relaxed">
              "{data.strategicDecree}"
            </h3>

            <div className="flex flex-wrap items-center gap-6 pt-2">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-50 border border-green-100">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                <span className="text-xs font-bold text-green-800 tracking-wide">
                  {data.confidence}% CONFIDENCE
                </span>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-50 border border-amber-100">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                <span className="text-xs font-bold text-amber-800 tracking-wide">
                  {data.risks.length} RISKS DETECTED
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Campaign Arc (Campaign Only) */}
      {type === 'campaign' && data.campaignArc && (
        <section className="space-y-6">
          <div className="flex items-center gap-2 border-b border-borders pb-2">
            <Calendar className="w-4 h-4 text-secondary-text" />
            <h4 className="text-xs font-bold uppercase tracking-widest text-secondary-text">
              Campaign Timeline
            </h4>
          </div>

          <div className="relative pl-8 space-y-8 before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-[2px] before:bg-borders">
            {data.campaignArc.phases.map((phase, i) => (
              <div key={i} className="relative">
                <div className="absolute -left-[29px] top-1.5 w-6 h-6 rounded-full bg-surface border-2 border-ink flex items-center justify-center z-10">
                  <div className="w-2 h-2 rounded-full bg-ink" />
                </div>
                <div className="bg-surface border border-borders p-5 rounded-xl hover:border-ink/30 transition-colors">
                  <div className="flex justify-between items-start mb-2">
                    <h5 className="font-bold text-ink text-lg">{phase.name}</h5>
                    <span className="text-xs font-mono text-secondary-text bg-muted px-2 py-1 rounded">Weeks {phase.weeks.join('-')}</span>
                  </div>
                  <p className="text-sm text-secondary-text">Focus: <span className="text-ink font-medium">{phase.focus}</span></p>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Debate Section (Collapsible) */}
      <section className="space-y-4">
        <button
          onClick={() => setShowDebate(!showDebate)}
          className="flex items-center justify-between w-full group py-2"
        >
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-secondary-text group-hover:text-ink transition-colors">
            <BrainCircuit className="w-4 h-4" />
            Council Debate Transcript
          </div>
          {showDebate ? (
            <ChevronUp className="w-4 h-4 text-secondary-text group-hover:text-ink" />
          ) : (
            <ChevronDown className="w-4 h-4 text-secondary-text group-hover:text-ink" />
          )}
        </button>

        <AnimatePresence>
          {showDebate && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden"
            >
              <div className="grid gap-3 pt-2">
                {data.debateTranscript.map((entry, i) => (
                  <div key={i} className="flex gap-4 p-4 rounded-xl bg-surface/50 border border-borders/50">
                    <Avatar className="h-8 w-8 shrink-0">
                      <AvatarFallback className="bg-muted text-xs font-bold text-muted-foreground">
                        {entry.role.charAt(0)}
                      </AvatarFallback>
                    </Avatar>
                    <div className="space-y-1">
                      <p className="text-xs font-bold text-ink uppercase tracking-wider">{entry.role}</p>
                      <p className="text-sm text-secondary-text italic font-serif">"{entry.argument}"</p>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </section>

      {/* Rejected Paths */}
      {data.rejectedPaths && data.rejectedPaths.length > 0 && (
        <section className="space-y-4 pt-4 border-t border-borders">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-muted-foreground">
            <XCircle className="w-4 h-4" />
            Discarded Alternatives
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.rejectedPaths.map((path, i) => (
              <div key={i} className="p-4 rounded-xl bg-red-50/50 border border-red-100/50 flex flex-col gap-1">
                <span className="font-semibold text-ink text-sm">{path.path}</span>
                <span className="text-xs text-secondary-text">{path.reason}</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Moves List (Editable) */}
      <section className="space-y-6 pt-6 border-t border-borders">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-bold uppercase tracking-widest text-ink">
            {type === 'move' ? 'Proposed Execution Plan' : 'Phase 1: Moves'}
          </h4>
          <span className="text-xs text-secondary-text bg-muted px-2 py-1 rounded-full">
            {moves.length} steps generated
          </span>
        </div>

        <div className="grid grid-cols-1 gap-4">
          {moves.map((move) => (
            <MovePreviewCard
              key={move.id}
              move={move}
              onUpdate={(updates) => onUpdateMove(move.id, updates)}
              onDelete={() => onDeleteMove(move.id)}
            />
          ))}
        </div>
      </section>

      {/* Actions */}
      <div className="sticky bottom-0 pt-6 pb-2 bg-gradient-to-t from-canvas to-canvas/95 backdrop-blur-sm border-t border-borders flex justify-end gap-3 z-20">
        <Button
          variant="ghost"
          onClick={onBack}
          className="text-secondary-text hover:text-ink"
        >
          Revise Inputs
        </Button>
        <Button
          onClick={onConfirm}
          className="h-12 px-8 rounded-xl bg-ink text-white font-medium text-base hover:bg-ink/90 transition-all shadow-md"
        >
          {type === 'move' ? 'Approve & Execute' : 'Initialize Campaign'}
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </div>
    </motion.div>
  );
}

function MovePreviewCard({
  move,
  onUpdate,
  onDelete,
}: {
  move: CouncilMoveSuggestion;
  onUpdate: (updates: Partial<CouncilMoveSuggestion>) => void;
  onDelete: () => void;
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(move.title);
  const [editDesc, setEditDesc] = useState(move.description);

  const handleSave = () => {
    onUpdate({ title: editTitle, description: editDesc });
    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <div className="bg-surface p-6 rounded-xl border border-ink shadow-lg space-y-4 animate-in fade-in zoom-in-95 duration-200">
        <div className="space-y-2">
          <Input
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            className="font-bold text-ink text-base bg-white"
            placeholder="Move Title"
            autoFocus
          />
          <Textarea
            value={editDesc}
            onChange={(e) => setEditDesc(e.target.value)}
            className="text-sm text-secondary-text min-h-[80px] bg-white resize-none"
            placeholder="Description"
          />
        </div>
        <div className="flex justify-end gap-2">
          <Button size="sm" variant="ghost" onClick={() => setIsEditing(false)}>
            Cancel
          </Button>
          <Button
            size="sm"
            onClick={handleSave}
            className="bg-ink text-white"
          >
            Save Changes
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="group relative bg-surface p-6 rounded-xl border border-borders shadow-sm hover:border-ink/50 hover:shadow-md transition-all duration-300">
      <div className="flex justify-between items-start mb-3">
        <div className="flex items-center gap-3">
          <span className="px-2.5 py-0.5 rounded-md bg-muted text-ink text-[10px] font-bold uppercase tracking-wide">
            {move.type}
          </span>
          <span className="text-[10px] text-muted-foreground font-mono">
            Confidence: {move.confidenceScore}%
          </span>
        </div>
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity translate-x-2 group-hover:translate-x-0">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsEditing(true)}
            className="h-8 w-8 text-muted-foreground hover:text-ink hover:bg-muted"
          >
            <Edit2 className="w-4 h-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={onDelete}
            className="h-8 w-8 text-muted-foreground hover:text-red-600 hover:bg-red-50"
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <h4 className="font-bold text-ink text-lg mb-2 leading-tight">{move.title}</h4>
      <p className="text-sm text-secondary-text mb-4 leading-relaxed line-clamp-2 md:line-clamp-none">
        {move.description}
      </p>

      <div className="flex flex-wrap gap-2">
        {move.toolRequirements.map((tool) => (
          <span
            key={tool}
            className="text-[10px] text-muted-foreground border border-borders bg-background px-2 py-0.5 rounded flex items-center gap-1"
          >
            <div className="w-1 h-1 rounded-full bg-muted-foreground/50" />
            {tool}
          </span>
        ))}
      </div>
    </div>
  );
}
