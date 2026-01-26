import React, { useState } from 'react';
import { X, Save, Target, Users, Target as GoalIcon } from 'lucide-react';
import { usePersonaStore, PersonaBrief } from '@/stores/personaStore';
import { cn } from '@/lib/utils';

interface PersonaBriefModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function PersonaBriefModal({ isOpen, onClose }: PersonaBriefModalProps) {
  const { brief, setBrief, updateBrief } = usePersonaStore();
  const [formData, setFormData] = useState<PersonaBrief>(
    brief || {
      audience: '',
      voice: '',
      goals: [],
      guidelines: '',
    }
  );
  const [goalInput, setGoalInput] = useState('');

  const handleSave = () => {
    setBrief(formData);
    onClose();
  };

  const addGoal = () => {
    if (goalInput.trim()) {
      setFormData((prev: PersonaBrief) => ({
        ...prev,
        goals: [...prev.goals, goalInput.trim()],
      }));
      setGoalInput('');
    }
  };

  const removeGoal = (index: number) => {
    setFormData((prev: PersonaBrief) => ({
      ...prev,
      goals: prev.goals.filter((_: string, i: number) => i !== index),
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
      <div className="bg-[var(--paper)] w-full max-w-md rounded-[var(--radius)] border border-[var(--ink)] shadow-2xl p-5">
        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <h3 className="font-medium text-sm text-[var(--ink)]">Persona Brief</h3>
          <button onClick={onClose} className="p-1 hover:bg-[var(--surface)] rounded text-[var(--ink-muted)] hover:text-[var(--ink)] transition-colors">
            <X size={16} />
          </button>
        </div>

        {/* Form */}
        <div className="space-y-4">
          {/* Audience */}
          <div>
            <label className="text-[10px] font-bold text-[var(--ink-muted)] uppercase mb-2 block flex items-center gap-1">
              <Users size={12} />
              Audience
            </label>
            <input
              type="text"
              value={formData.audience}
              onChange={(e) => setFormData((prev: PersonaBrief) => ({ ...prev, audience: e.target.value }))}
              placeholder="e.g., Enterprise CTOs, SaaS founders, Marketing managers"
              className="w-full px-3 py-2 text-xs bg-[var(--surface)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)] placeholder:text-[var(--ink-ghost)]"
            />
          </div>

          {/* Voice */}
          <div>
            <label className="text-[10px] font-bold text-[var(--ink-muted)] uppercase mb-2 block flex items-center gap-1">
              <Target size={12} />
              Voice
            </label>
            <input
              type="text"
              value={formData.voice}
              onChange={(e) => setFormData((prev: PersonaBrief) => ({ ...prev, voice: e.target.value }))}
              placeholder="e.g., Confident & authoritative, Casual & friendly, Formal & professional"
              className="w-full px-3 py-2 text-xs bg-[var(--surface)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)] placeholder:text-[var(--ink-ghost)]"
            />
          </div>

          {/* Goals */}
          <div>
            <label className="text-[10px] font-bold text-[var(--ink-muted)] uppercase mb-2 block flex items-center gap-1">
              <GoalIcon size={12} />
              Goals
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={goalInput}
                onChange={(e) => setGoalInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addGoal();
                  }
                }}
                placeholder="Add a goal..."
                className="flex-1 px-3 py-2 text-xs bg-[var(--surface)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)] placeholder:text-[var(--ink-ghost)]"
              />
              <button
                onClick={addGoal}
                disabled={!goalInput.trim()}
                className="px-3 py-2 text-xs bg-[var(--ink)] text-[var(--paper)] rounded-[var(--radius)] hover:opacity-90 disabled:opacity-40 transition-opacity"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-1">
              {formData.goals.map((goal: string, index: number) => (
                <span
                  key={index}
                  className="inline-flex items-center gap-1 px-2 py-1 text-[10px] bg-[var(--blueprint-light)]/20 text-[var(--blueprint)] rounded-full"
                >
                  {goal}
                  <button
                    onClick={() => removeGoal(index)}
                    className="hover:text-[var(--destructive)] transition-colors"
                  >
                    <X size={10} />
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Guidelines */}
          <div>
            <label className="text-[10px] font-bold text-[var(--ink-muted)] uppercase mb-2 block">
              Guidelines (optional)
            </label>
            <textarea
              value={formData.guidelines || ''}
              onChange={(e) => setFormData((prev: PersonaBrief) => ({ ...prev, guidelines: e.target.value }))}
              placeholder="Any specific guidelines, phrases to avoid, or must-include elements..."
              rows={3}
              className="w-full px-3 py-2 text-xs bg-[var(--surface)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)] placeholder:text-[var(--ink-ghost)] resize-none"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-2 mt-5">
          <button
            onClick={onClose}
            className="px-3 py-1.5 text-xs text-[var(--ink-muted)] border border-[var(--structure-subtle)] rounded-[var(--radius)] hover:border-[var(--ink)] hover:text-[var(--ink)] transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={!formData.audience.trim() || !formData.voice.trim() || formData.goals.length === 0}
            className="px-3 py-1.5 text-xs bg-[var(--ink)] text-[var(--paper)] rounded-[var(--radius)] hover:opacity-90 disabled:opacity-40 transition-opacity flex items-center gap-1"
          >
            <Save size={12} />
            Save Brief
          </button>
        </div>
      </div>
    </div>
  );
}
