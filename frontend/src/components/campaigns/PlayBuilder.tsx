"use client";

import { useState, useCallback } from 'react';
import {
  Plus,
  Settings,
  Play,
  Pause,
  Save,
  X,
  Zap,
  GitBranch,
  Clock,
  Target,
  BarChart3,
  ChevronDown,
  Eye,
  Edit,
  Trash2,
  Copy,
  TestTube
} from 'lucide-react';
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { BlueprintButton } from '@/components/ui/BlueprintButton';
import { BlueprintBadge } from '@/components/ui/BlueprintBadge';
import { Play as PlayType, MoveConfig, MoveType, PlayStep, PlayCondition, PlayConfig, PlayCategory } from '@/types/campaign';

interface TestResult {
  step: string;
  success: boolean;
  message: string;
  metrics?: Record<string, number>;
}
import { allMoves } from '@/data/moveLibrary';
import { useEnhancedCampaignStore } from '@/stores/enhancedCampaignStore';
import { cn } from '@/lib/utils';

interface PlayBuilderProps {
  onSave?: (play: PlayType) => void;
  initialPlay?: PlayType;
  readOnly?: boolean;
}



export function PlayBuilder({ onSave, initialPlay, readOnly = false }: PlayBuilderProps) {
  const createPlay = useEnhancedCampaignStore(state => state.createPlay);
  const updatePlay = useEnhancedCampaignStore(state => state.updatePlay);
  const moves = useEnhancedCampaignStore(state => state.moves);

  const [play, setPlay] = useState<Partial<PlayType>>(initialPlay || {
    name: '',
    description: '',
    category: PlayCategory.CUSTOM,
    moves: [],
    tags: [],
    rating: 0,
    usageCount: 0,
    config: {
      steps: [],
      triggers: [],
      conditions: []
    }
  });

  const [steps, setSteps] = useState<PlayStep[]>(
    initialPlay?.config?.steps || [
      {
        id: 'step-1',
        name: 'Initial Step',
        moves: [],
        parallel: false
      }
    ]
  );

  const [selectedMoves, setSelectedMoves] = useState<string[]>(
    initialPlay?.moves || []
  );

  const [showMoveLibrary, setShowMoveLibrary] = useState(false);
  const [editingStep, setEditingStep] = useState<string | null>(null);
  const [previewMode, setPreviewMode] = useState(false);
  const [testMode, setTestMode] = useState(false);
  const [testResults, setTestResults] = useState<TestResult[]>([]);

  // Add new step
  const addStep = useCallback(() => {
    const newStep: PlayStep = {
      id: `step-${Date.now()}`,
      name: `Step ${steps.length + 1}`,
      moves: [],
      parallel: false
    };

    setSteps(prev => [...prev, newStep]);
  }, [steps.length]);

  // Update step
  const updateStep = useCallback((stepId: string, updates: Partial<PlayStep>) => {
    setSteps(prev => prev.map(step =>
      step.id === stepId ? { ...step, ...updates } : step
    ));
  }, []);

  // Delete step
  const deleteStep = useCallback((stepId: string) => {
    setSteps(prev => prev.filter(step => step.id !== stepId));
  }, []);

  // Add move to step
  const addMoveToStep = useCallback((stepId: string, moveId: string) => {
    updateStep(stepId, {
      moves: [...steps.find(s => s.id === stepId)?.moves || [], moveId]
    });
    setSelectedMoves(prev => [...prev, moveId]);
  }, [steps, updateStep]);

  // Remove move from step
  const removeMoveFromStep = useCallback((stepId: string, moveId: string) => {
    updateStep(stepId, {
      moves: steps.find(s => s.id === stepId)?.moves.filter(id => id !== moveId) || []
    });
    setSelectedMoves(prev => prev.filter(id => id !== moveId));
  }, [steps, updateStep]);

  // Add condition to step
  const addCondition = useCallback((stepId: string) => {
    const condition: PlayCondition = {
      type: 'move_status',
      operator: 'equals',
      value: 'completed'
    };

    updateStep(stepId, {
      conditions: [...(steps.find(s => s.id === stepId)?.conditions || []), condition]
    });
  }, [steps, updateStep]);

  // Test the play
  const testPlay = useCallback(async () => {
    setTestMode(true);
    setTestResults([]);

    // Simulate test execution
    for (const step of steps) {
      await new Promise(resolve => setTimeout(resolve, 1000));

      const result: TestResult = {
        step: step.name,
        success: Math.random() > 0.2, // 80% success rate
        message: Math.random() > 0.2
          ? `Step executed successfully with ${step.moves.length} moves`
          : 'Step failed: Missing required configuration',
        metrics: step.moves.length > 0 ? {
          movesExecuted: step.moves.length,
          duration: Math.floor(Math.random() * 5000)
        } : undefined
      };

      setTestResults(prev => [...prev, result]);
    }

    setTestMode(false);
  }, [steps]);

  // Save play
  const handleSave = useCallback(async () => {
    const playData: PlayType = {
      id: initialPlay?.id || '',
      name: play.name || 'Untitled Play',
      description: play.description || '',
      category: play.category || PlayCategory.CUSTOM,
      moves: selectedMoves,
      config: {
        steps,
        triggers: play.config?.triggers || [],
        conditions: play.config?.conditions || []
      },
      isActive: false,
      createdAt: initialPlay?.createdAt || new Date(),
      updatedAt: new Date(),
      createdBy: 'current_user',
      tags: play.tags || [],
      usageCount: initialPlay?.usageCount || 0,
      rating: initialPlay?.rating || 0
    };

    if (initialPlay?.id) {
      await updatePlay(initialPlay.id, playData);
    } else {
      const id = await createPlay(playData);
      playData.id = id;
    }

    onSave?.(playData);
  }, [play, steps, selectedMoves, initialPlay, createPlay, updatePlay, onSave]);

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-[var(--structure-subtle)]">
        <div>
          <h2 className="text-lg font-semibold text-[var(--ink)]">Play Builder</h2>
          <p className="text-sm text-[var(--ink-muted)]">
            Create automated sequences with conditional logic
          </p>
        </div>

        <div className="flex items-center gap-2">
          <BlueprintButton
            variant="secondary"
            size="sm"
            onClick={() => setTestMode(!testMode)}
            className="flex items-center gap-2"
            disabled={steps.length === 0}
          >
            <TestTube size={16} />
            {testMode ? 'Testing...' : 'Test'}
          </BlueprintButton>

          <BlueprintButton
            variant="secondary"
            size="sm"
            onClick={() => setPreviewMode(!previewMode)}
            className="flex items-center gap-2"
          >
            <Eye size={16} />
            {previewMode ? 'Edit' : 'Preview'}
          </BlueprintButton>

          {!readOnly && (
            <BlueprintButton
              size="sm"
              onClick={handleSave}
              className="flex items-center gap-2"
              disabled={!play.name}
            >
              <Save size={16} />
              Save
            </BlueprintButton>
          )}
        </div>
      </div>

      {/* Play Configuration */}
      <div className="p-4 border-b border-[var(--structure-subtle)]">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-[var(--ink)] mb-2">
              Play Name
            </label>
            <input
              type="text"
              value={play.name || ''}
              onChange={(e) => setPlay(prev => ({ ...prev, name: e.target.value }))}
              placeholder="Enter play name"
              className="w-full px-3 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]"
              disabled={readOnly}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--ink)] mb-2">
              Category
            </label>
            <select
              value={play.category || 'custom'}
              onChange={(e) => setPlay(prev => ({ ...prev, category: e.target.value as PlayCategory }))}
              className="w-full px-3 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]"
              disabled={readOnly}
            >
              <option value="custom">Custom</option>
              <option value="onboarding">Onboarding</option>
              <option value="nurturing">Nurturing</option>
              <option value="conversion">Conversion</option>
              <option value="retention">Retention</option>
            </select>
          </div>
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium text-[var(--ink)] mb-2">
            Description
          </label>
          <textarea
            value={play.description || ''}
            onChange={(e) => setPlay(prev => ({ ...prev, description: e.target.value }))}
            placeholder="Describe what this play does..."
            rows={2}
            className="w-full px-3 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)] resize-none"
            disabled={readOnly}
          />
        </div>
      </div>

      {/* Steps Builder */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-[var(--ink)]">Play Steps</h3>
          {!readOnly && (
            <BlueprintButton
              variant="secondary"
              size="sm"
              onClick={addStep}
              className="flex items-center gap-2"
            >
              <Plus size={16} />
              Add Step
            </BlueprintButton>
          )}
        </div>

        {steps.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <GitBranch size={48} className="text-[var(--ink-ghost)] mb-4" />
            <h3 className="text-lg font-semibold text-[var(--ink)] mb-2">No steps yet</h3>
            <p className="text-sm text-[var(--ink-muted)] mb-4">
              Add steps to build your play sequence
            </p>
            <BlueprintButton onClick={addStep}>
              Add Your First Step
            </BlueprintButton>
          </div>
        ) : (
          <div className="space-y-4">
            {steps.map((step, index) => (
              <BlueprintCard key={step.id} className="p-4">
                {/* Step Header */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-[var(--blueprint-light)]/10 flex items-center justify-center text-sm font-semibold text-[var(--blueprint)]">
                      {index + 1}
                    </div>

                    {editingStep === step.id ? (
                      <input
                        type="text"
                        value={step.name}
                        onChange={(e) => updateStep(step.id, { name: e.target.value })}
                        className="px-2 py-1 text-sm bg-[var(--surface)] border border-[var(--structure-subtle)] rounded focus:outline-none focus:border-[var(--blueprint)]"
                      />
                    ) : (
                      <h4 className="text-sm font-semibold text-[var(--ink)]">
                        {step.name}
                      </h4>
                    )}

                    {step.parallel && (
                      <BlueprintBadge variant="blueprint" size="sm">
                        Parallel
                      </BlueprintBadge>
                    )}

                    {step.delay && (
                      <BlueprintBadge variant="default" size="sm" className="flex items-center gap-1">
                        <Clock size={12} />
                        {step.delay}h
                      </BlueprintBadge>
                    )}
                  </div>

                  {!readOnly && !previewMode && (
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => setEditingStep(editingStep === step.id ? null : step.id)}
                        className="p-1.5 text-[var(--ink-muted)] hover:bg-[var(--surface)] rounded transition-colors"
                      >
                        {editingStep === step.id ? <Save size={14} /> : <Edit size={14} />}
                      </button>

                      <button
                        onClick={() => deleteStep(step.id)}
                        className="p-1.5 text-[var(--destructive)] hover:bg-[var(--destructive-light)]/10 rounded transition-colors"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  )}
                </div>

                {/* Step Configuration */}
                <div className="space-y-3">
                  {/* Moves in Step */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-xs font-medium text-[var(--ink-muted)] uppercase tracking-wide">
                        Moves ({step.moves.length})
                      </label>
                      {!readOnly && (
                        <BlueprintButton
                          variant="ghost"
                          size="sm"
                          onClick={() => setShowMoveLibrary(true)}
                        >
                          <Plus size={12} />
                          Add
                        </BlueprintButton>
                      )}
                    </div>

                    {step.moves.length === 0 ? (
                      <div className="p-3 border border-dashed border-[var(--structure-subtle)] rounded-[var(--radius)] text-center">
                        <p className="text-xs text-[var(--ink-muted)]">No moves added</p>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        {step.moves.map(moveId => {
                          const move = moves[moveId];
                          return (
                            <div
                              key={moveId}
                              className="flex items-center justify-between p-2 bg-[var(--surface)] rounded"
                            >
                              <div className="flex items-center gap-2">
                                <div className="w-6 h-6 rounded bg-[var(--blueprint-light)]/10 flex items-center justify-center">
                                  <Zap size={12} className="text-[var(--blueprint)]" />
                                </div>
                                <span className="text-sm text-[var(--ink)]">
                                  {move?.name || 'Unknown Move'}
                                </span>
                              </div>

                              {!readOnly && !previewMode && (
                                <button
                                  onClick={() => removeMoveFromStep(step.id, moveId)}
                                  className="p-1 text-[var(--ink-ghost)] hover:text-[var(--destructive)]"
                                >
                                  <X size={14} />
                                </button>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>

                  {/* Conditions */}
                  {step.conditions && step.conditions.length > 0 && (
                    <div>
                      <label className="text-xs font-medium text-[var(--ink-muted)] uppercase tracking-wide">
                        Conditions
                      </label>
                      <div className="mt-2 space-y-1">
                        {step.conditions.map((condition, idx) => (
                          <div key={idx} className="text-xs text-[var(--ink-muted)] p-2 bg-[var(--surface)] rounded">
                            Execute when {condition.type} {condition.operator} {condition.value}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Step Options */}
                  {!readOnly && !previewMode && (
                    <div className="flex items-center gap-4 pt-2 border-t border-[var(--structure-subtle)]">
                      <label className="flex items-center gap-2 text-xs">
                        <input
                          type="checkbox"
                          checked={step.parallel || false}
                          onChange={(e) => updateStep(step.id, { parallel: e.target.checked })}
                          className="rounded border-[var(--structure-subtle)] text-[var(--blueprint)]"
                        />
                        Execute moves in parallel
                      </label>

                      <div className="flex items-center gap-2">
                        <label className="text-xs text-[var(--ink-muted)]">Delay after step:</label>
                        <input
                          type="number"
                          value={step.delay || 0}
                          onChange={(e) => updateStep(step.id, { delay: parseInt(e.target.value) || 0 })}
                          className="w-16 px-2 py-1 text-xs bg-[var(--surface)] border border-[var(--structure-subtle)] rounded focus:outline-none focus:border-[var(--blueprint)]"
                        />
                        <span className="text-xs text-[var(--ink-muted)]">hours</span>
                      </div>

                      <BlueprintButton
                        variant="ghost"
                        size="sm"
                        onClick={() => addCondition(step.id)}
                      >
                        <Target size={12} />
                        Add Condition
                      </BlueprintButton>
                    </div>
                  )}
                </div>
              </BlueprintCard>
            ))}
          </div>
        )}

        {/* Test Results */}
        {testResults.length > 0 && (
          <div className="mt-6 p-4 bg-[var(--surface)] rounded-[var(--radius)]">
            <h3 className="text-sm font-semibold text-[var(--ink)] mb-3 flex items-center gap-2">
              <TestTube size={16} />
              Test Results
            </h3>
            <div className="space-y-2">
              {testResults.map((result, index) => (
                <div
                  key={index}
                  className={cn(
                    "flex items-center justify-between p-2 rounded",
                    result.success ? "bg-[var(--success-light)]/10" : "bg-[var(--destructive-light)]/10"
                  )}
                >
                  <div className="flex items-center gap-2">
                    <div className={cn(
                      "w-2 h-2 rounded-full",
                      result.success ? "bg-[var(--success)]" : "bg-[var(--destructive)]"
                    )} />
                    <span className="text-sm text-[var(--ink)]">{result.step}</span>
                  </div>
                  <span className={cn(
                    "text-xs",
                    result.success ? "text-[var(--success)]" : "text-[var(--destructive)]"
                  )}>
                    {result.message}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Move Library Modal */}
      {showMoveLibrary && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <BlueprintCard className="w-full max-w-2xl max-h-[80vh] overflow-hidden">
            <div className="p-4 border-b border-[var(--structure-subtle)]">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-[var(--ink)]">Select Moves</h3>
                <button
                  onClick={() => setShowMoveLibrary(false)}
                  className="p-1 hover:bg-[var(--surface)] rounded text-[var(--ink-muted)]"
                >
                  <X size={16} />
                </button>
              </div>
            </div>

            <div className="p-4 overflow-y-auto max-h-96">
              <div className="grid grid-cols-1 gap-2">
                {allMoves.map(move => (
                  <button
                    key={move.id}
                    onClick={() => {
                      // Add to last step or create new step
                      const lastStep = steps[steps.length - 1];
                      if (lastStep) {
                        addMoveToStep(lastStep.id, move.id);
                      }
                      setShowMoveLibrary(false);
                    }}
                    className="p-3 text-left border border-[var(--structure-subtle)] rounded-[var(--radius)] hover:border-[var(--blueprint)] transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="text-2xl">{move.icon}</div>
                      <div className="flex-1">
                        <h4 className="text-sm font-medium text-[var(--ink)]">{move.name}</h4>
                        <p className="text-xs text-[var(--ink-muted)]">{move.description}</p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </BlueprintCard>
        </div>
      )}
    </div>
  );
}
