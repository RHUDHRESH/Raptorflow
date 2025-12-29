'use client';

import React, { useState } from 'react';
import { motion, Reorder } from 'framer-motion';
import {
  Lightbulb,
  AlertTriangle,
  Shield,
  FileText,
  Video,
  Award,
  Clock,
  GripVertical,
  Plus,
  X,
  Check,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { BeliefItem, ObjectionItem } from '@/lib/foundation';

interface BeliefObjectionStackProps {
  beliefs: BeliefItem[];
  objections: ObjectionItem[];
  onUpdateBelief: (id: string, updates: Partial<BeliefItem>) => void;
  onAddBelief: (belief: Omit<BeliefItem, 'id'>) => void;
  onRemoveBelief: (id: string) => void;
  onUpdateObjection: (id: string, updates: Partial<ObjectionItem>) => void;
  onReorderObjections: (objections: ObjectionItem[]) => void;
  onAddObjection: (objection: Omit<ObjectionItem, 'id'>) => void;
  onMarkDealKiller: (id: string) => void;
}

const PROOF_TYPE_CONFIG: Record<
  string,
  { icon: React.ElementType; label: string; color: string }
> = {
  'case-study': { icon: FileText, label: 'Case Study', color: '#2D3538' },
  demo: { icon: Video, label: 'Demo', color: '#64B5F6' },
  guarantee: { icon: Shield, label: 'Guarantee', color: '#81C784' },
  pilot: { icon: Clock, label: 'Pilot', color: '#FFB74D' },
  testimonial: { icon: Award, label: 'Testimonial', color: '#9575CD' },
};

const DEFAULT_BELIEFS: Omit<BeliefItem, 'id'>[] = [
  { text: 'Marketing automation can be safe and on-brand', isRequired: true },
  { text: 'A system is better than ad-hoc effort', isRequired: true },
  { text: 'This will actually get used by the team', isRequired: false },
];

const DEFAULT_OBJECTIONS: Omit<ObjectionItem, 'id'>[] = [
  {
    objection: 'Is this worth my time?',
    rootCause: 'Previous tools abandoned',
    proofTypeRequired: 'case-study',
    isDealKiller: false,
    rank: 1,
  },
  {
    objection: 'Will my team actually use it?',
    rootCause: 'Change management concern',
    proofTypeRequired: 'demo',
    isDealKiller: false,
    rank: 2,
  },
  {
    objection: 'How long until we see results?',
    rootCause: 'ROI timeline anxiety',
    proofTypeRequired: 'guarantee',
    isDealKiller: false,
    rank: 3,
  },
  {
    objection: 'Is our data secure?',
    rootCause: 'Compliance / privacy concern',
    proofTypeRequired: 'testimonial',
    isDealKiller: true,
    rank: 4,
  },
];

function BeliefCard({
  belief,
  onUpdate,
  onRemove,
}: {
  belief: BeliefItem;
  onUpdate: (updates: Partial<BeliefItem>) => void;
  onRemove: () => void;
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [text, setText] = useState(belief.text);

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className={`bg-white border rounded-xl p-4 ${
        belief.isRequired ? 'border-[#2D3538]' : 'border-[#E5E6E3]'
      }`}
    >
      <div className="flex items-start gap-3">
        <div
          className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
            belief.isRequired ? 'bg-[#2D3538]' : 'bg-[#F3F4EE]'
          }`}
        >
          <Lightbulb
            className={`w-4 h-4 ${belief.isRequired ? 'text-white' : 'text-[#9D9F9F]'}`}
          />
        </div>
        <div className="flex-1">
          {isEditing ? (
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              onBlur={() => {
                onUpdate({ text });
                setIsEditing(false);
              }}
              className="w-full border border-[#E5E6E3] rounded-lg px-3 py-2 text-sm resize-none focus:outline-none focus:border-[#2D3538]"
              rows={2}
              autoFocus
            />
          ) : (
            <p
              onClick={() => setIsEditing(true)}
              className="text-sm text-[#2D3538] cursor-pointer hover:bg-[#F3F4EE] rounded px-1 -mx-1"
            >
              {belief.text}
            </p>
          )}
          <div className="flex items-center gap-3 mt-2">
            <button
              onClick={() => onUpdate({ isRequired: !belief.isRequired })}
              className={`text-[10px] font-mono uppercase px-2 py-1 rounded ${
                belief.isRequired
                  ? 'bg-[#2D3538] text-white'
                  : 'bg-[#F3F4EE] text-[#9D9F9F] hover:bg-[#E5E6E3]'
              }`}
            >
              {belief.isRequired ? 'Required' : 'Optional'}
            </button>
            <button
              onClick={onRemove}
              className="text-[10px] text-red-500 hover:text-red-700"
            >
              Remove
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function ObjectionCard({
  objection,
  onUpdate,
  onMarkDealKiller,
}: {
  objection: ObjectionItem;
  onUpdate: (updates: Partial<ObjectionItem>) => void;
  onMarkDealKiller: () => void;
}) {
  const proofConfig = PROOF_TYPE_CONFIG[objection.proofTypeRequired];
  const ProofIcon = proofConfig?.icon || FileText;

  return (
    <Reorder.Item
      value={objection}
      className="cursor-grab active:cursor-grabbing"
    >
      <motion.div
        layout
        className={`bg-white border-2 rounded-xl overflow-hidden ${
          objection.isDealKiller ? 'border-red-500' : 'border-[#E5E6E3]'
        }`}
      >
        <div className="flex items-stretch">
          {/* Drag Handle */}
          <div className="w-10 bg-[#FAFAF8] flex items-center justify-center border-r border-[#E5E6E3]">
            <GripVertical className="w-4 h-4 text-[#9D9F9F]" />
          </div>

          {/* Content */}
          <div className="flex-1 p-4">
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono text-[#9D9F9F]">
                  #{objection.rank}
                </span>
                {objection.isDealKiller && (
                  <span className="text-[9px] font-mono uppercase bg-red-100 text-red-700 px-2 py-0.5 rounded">
                    Deal Killer
                  </span>
                )}
              </div>
              <button
                onClick={onMarkDealKiller}
                className={`text-[10px] px-2 py-1 rounded transition-colors ${
                  objection.isDealKiller
                    ? 'bg-red-100 text-red-700 hover:bg-red-200'
                    : 'bg-[#F3F4EE] text-[#9D9F9F] hover:bg-[#E5E6E3]'
                }`}
              >
                {objection.isDealKiller ? 'Unmark' : 'Mark Deal Killer'}
              </button>
            </div>

            <h4 className="font-medium text-[#2D3538] mb-1">
              {objection.objection}
            </h4>
            <p className="text-xs text-[#5B5F61] mb-3">
              <span className="text-[#9D9F9F]">Root cause:</span>{' '}
              {objection.rootCause}
            </p>

            {/* Proof Type */}
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono uppercase text-[#9D9F9F]">
                Proof Required:
              </span>
              <div
                className="flex items-center gap-1.5 px-2 py-1 rounded-lg"
                style={{ backgroundColor: proofConfig?.color + '15' }}
              >
                <ProofIcon
                  className="w-3 h-3"
                  style={{ color: proofConfig?.color }}
                />
                <span
                  className="text-xs font-medium"
                  style={{ color: proofConfig?.color }}
                >
                  {proofConfig?.label}
                </span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </Reorder.Item>
  );
}

export function BeliefObjectionStack({
  beliefs,
  objections,
  onUpdateBelief,
  onAddBelief,
  onRemoveBelief,
  onUpdateObjection,
  onReorderObjections,
  onAddObjection,
  onMarkDealKiller,
}: BeliefObjectionStackProps) {
  const [newBelief, setNewBelief] = useState('');
  const [showAddBelief, setShowAddBelief] = useState(false);

  // Use defaults if empty
  const displayBeliefs =
    beliefs.length > 0
      ? beliefs
      : DEFAULT_BELIEFS.map((b, i) => ({ ...b, id: `default-belief-${i}` }));

  const displayObjections =
    objections.length > 0
      ? objections
      : DEFAULT_OBJECTIONS.map((o, i) => ({ ...o, id: `default-obj-${i}` }));

  const handleAddBelief = () => {
    if (newBelief.trim()) {
      onAddBelief({ text: newBelief.trim(), isRequired: false });
      setNewBelief('');
      setShowAddBelief(false);
    }
  };

  const dealKillerCount = displayObjections.filter(
    (o) => o.isDealKiller
  ).length;

  return (
    <div className="space-y-8">
      {/* Beliefs Section */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#F3F4EE] rounded-xl flex items-center justify-center">
              <Lightbulb className="w-5 h-5 text-[#2D3538]" />
            </div>
            <div>
              <h3 className="font-medium text-[#2D3538]">Beliefs</h3>
              <p className="text-xs text-[#5B5F61]">
                What they must believe to buy
              </p>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowAddBelief(!showAddBelief)}
            className="rounded-xl"
          >
            <Plus className="w-4 h-4 mr-1" />
            Add
          </Button>
        </div>

        {showAddBelief && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mb-4"
          >
            <div className="flex gap-2">
              <input
                type="text"
                value={newBelief}
                onChange={(e) => setNewBelief(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddBelief()}
                placeholder="e.g., 'This tool respects brand voice'"
                className="flex-1 border border-[#E5E6E3] rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-[#2D3538]"
                autoFocus
              />
              <Button
                onClick={handleAddBelief}
                className="bg-[#2D3538] rounded-xl"
              >
                <Check className="w-4 h-4" />
              </Button>
            </div>
          </motion.div>
        )}

        <div className="space-y-3">
          {displayBeliefs.map((belief) => (
            <BeliefCard
              key={belief.id}
              belief={belief}
              onUpdate={(updates) => onUpdateBelief(belief.id, updates)}
              onRemove={() => onRemoveBelief(belief.id)}
            />
          ))}
        </div>
      </div>

      {/* Divider */}
      <div className="border-t border-[#E5E6E3]" />

      {/* Objections Section */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-50 rounded-xl flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <h3 className="font-medium text-[#2D3538]">Objections</h3>
              <p className="text-xs text-[#5B5F61]">
                Drag to rank by importance • {dealKillerCount} deal killer
                {dealKillerCount !== 1 ? 's' : ''}
              </p>
            </div>
          </div>
        </div>

        <Reorder.Group
          axis="y"
          values={displayObjections}
          onReorder={(newOrder) => {
            const updated = newOrder.map((obj, i) => ({ ...obj, rank: i + 1 }));
            onReorderObjections(updated);
          }}
          className="space-y-3"
        >
          {displayObjections.map((objection) => (
            <ObjectionCard
              key={objection.id}
              objection={objection}
              onUpdate={(updates) => onUpdateObjection(objection.id, updates)}
              onMarkDealKiller={() => onMarkDealKiller(objection.id)}
            />
          ))}
        </Reorder.Group>
      </div>

      {/* Proof Summary */}
      <div className="bg-[#FAFAF8] border border-[#E5E6E3] rounded-2xl p-5">
        <h4 className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-3">
          Proof Requirements Summary
        </h4>
        <div className="flex flex-wrap gap-3">
          {Object.entries(PROOF_TYPE_CONFIG).map(([key, config]) => {
            const count = displayObjections.filter(
              (o) => o.proofTypeRequired === key
            ).length;
            if (count === 0) return null;
            const Icon = config.icon;
            return (
              <div
                key={key}
                className="flex items-center gap-2 px-3 py-2 rounded-xl"
                style={{ backgroundColor: config.color + '15' }}
              >
                <Icon className="w-4 h-4" style={{ color: config.color }} />
                <span className="text-sm" style={{ color: config.color }}>
                  {config.label}: {count}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
