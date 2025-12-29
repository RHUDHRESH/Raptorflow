'use client';

import React, { useState } from 'react';
import {
  Plus,
  X,
  ChevronRight,
  Eye,
  EyeOff,
  AlertCircle,
  Check,
  Shield,
  Settings,
  Lightbulb,
  Layers,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Phase4Data,
  UniqueAttribute,
  AttributeType,
  Copyability,
} from '@/lib/foundation';
import { v4 as uuidv4 } from 'uuid';

interface UniqueAttributesScreenProps {
  phase4: Phase4Data;
  onUpdate: (updates: Partial<Phase4Data>) => void;
  onShowEvidence: (attributeId: string) => void;
  onContinue: () => void;
  onBack: () => void;
}

const ATTRIBUTE_TYPES: {
  value: AttributeType;
  label: string;
  icon: React.ReactNode;
}[] = [
  {
    value: 'feature',
    label: 'Feature',
    icon: <Settings className="w-3 h-3" />,
  },
  { value: 'process', label: 'Process', icon: <Layers className="w-3 h-3" /> },
  {
    value: 'data-advantage',
    label: 'Data',
    icon: <Shield className="w-3 h-3" />,
  },
  {
    value: 'workflow',
    label: 'Workflow',
    icon: <Lightbulb className="w-3 h-3" />,
  },
  {
    value: 'distribution',
    label: 'Distribution',
    icon: <Lightbulb className="w-3 h-3" />,
  },
];

const COPYABILITY_OPTIONS: {
  value: Copyability;
  label: string;
  color: string;
}[] = [
  {
    value: 'hard',
    label: 'Hard to copy',
    color: 'bg-green-100 text-green-700',
  },
  { value: 'medium', label: 'Medium', color: 'bg-amber-100 text-amber-700' },
  { value: 'easy', label: 'Easy to copy', color: 'bg-red-100 text-red-700' },
];

export function UniqueAttributesScreen({
  phase4,
  onUpdate,
  onShowEvidence,
  onContinue,
  onBack,
}: UniqueAttributesScreenProps) {
  const [newAttributeText, setNewAttributeText] = useState('');
  const [showConfidential, setShowConfidential] = useState(true);

  const attributes = phase4.uniqueAttributes || [];

  // Generate default attributes from differentiators if none exist
  const displayAttributes =
    attributes.length > 0
      ? attributes
      : [
          {
            id: uuidv4(),
            attribute: 'Integrated AI-powered positioning engine',
            proof: '',
            differentiator: '',
            type: 'feature' as AttributeType,
            copyability: 'hard' as Copyability,
            requiresProof: true,
            source: 'derived' as const,
            isConfidential: false,
            evidenceIds: [],
          },
          {
            id: uuidv4(),
            attribute: 'Evidence-first claim validation',
            proof: '',
            differentiator: '',
            type: 'process' as AttributeType,
            copyability: 'medium' as Copyability,
            requiresProof: true,
            source: 'derived' as const,
            isConfidential: false,
            evidenceIds: [],
          },
          {
            id: uuidv4(),
            attribute: 'Dunford positioning framework built-in',
            proof: '',
            differentiator: '',
            type: 'workflow' as AttributeType,
            copyability: 'medium' as Copyability,
            requiresProof: false,
            source: 'derived' as const,
            isConfidential: false,
            evidenceIds: [],
          },
        ];

  const handleAddAttribute = () => {
    if (!newAttributeText.trim()) return;
    const newAttr: UniqueAttribute = {
      id: uuidv4(),
      attribute: newAttributeText.trim(),
      proof: '',
      differentiator: '',
      type: 'feature',
      copyability: 'medium',
      requiresProof: true,
      source: 'user-claimed',
      isConfidential: false,
      evidenceIds: [],
    };
    onUpdate({ uniqueAttributes: [...displayAttributes, newAttr] as UniqueAttribute[] });
    setNewAttributeText('');
  };

  const handleRemoveAttribute = (id: string) => {
    onUpdate({
      uniqueAttributes: displayAttributes.filter((a) => a.id !== id),
    });
  };

  const handleUpdateAttribute = <K extends keyof UniqueAttribute>(
    id: string,
    field: K,
    value: UniqueAttribute[K]
  ) => {
    const updated = displayAttributes.map((a) =>
      a.id === id ? { ...a, [field]: value } : a
    );
    onUpdate({ uniqueAttributes: updated as UniqueAttribute[] });
  };

  const handleToggleConfidential = (id: string) => {
    const attr = displayAttributes.find((a) => a.id === id);
    if (attr) {
      handleUpdateAttribute(id, 'isConfidential', !attr.isConfidential);
    }
  };

  const filteredAttributes = showConfidential
    ? displayAttributes
    : displayAttributes.filter((a) => !a.isConfidential);

  const proofRequired = displayAttributes.filter(
    (a) => a.requiresProof && (a.evidenceIds?.length || 0) === 0
  );

  return (
    <div className="space-y-6">
      {/* Header Info */}
      <div className="bg-[#F3F4EE] rounded-2xl p-5 border border-[#E5E6E3]">
        <p className="text-sm text-[#5B5F61]">
          <strong>Dunford Step:</strong> List what you have that others don't —
          without judging value yet. We're cataloging capabilities, not making
          claims.
        </p>
      </div>

      {/* Show/Hide Confidential */}
      <div className="flex items-center justify-between">
        <span className="text-sm text-[#5B5F61]">
          {displayAttributes.length} attributes • {proofRequired.length} need
          proof
        </span>
        <button
          onClick={() => setShowConfidential(!showConfidential)}
          className="flex items-center gap-2 text-sm text-[#5B5F61] hover:text-[#2D3538]"
        >
          {showConfidential ? (
            <Eye className="w-4 h-4" />
          ) : (
            <EyeOff className="w-4 h-4" />
          )}
          {showConfidential ? 'Hide confidential' : 'Show confidential'}
        </button>
      </div>

      {/* Attributes Table */}
      <div className="bg-white border border-[#E5E6E3] rounded-2xl overflow-hidden">
        {/* Header */}
        <div className="grid grid-cols-12 gap-4 px-5 py-3 bg-[#F3F4EE] text-[10px] font-mono uppercase tracking-wider text-[#9D9F9F]">
          <div className="col-span-5">Attribute</div>
          <div className="col-span-2">Type</div>
          <div className="col-span-2">Copyability</div>
          <div className="col-span-1">Proof</div>
          <div className="col-span-1">Source</div>
          <div className="col-span-1"></div>
        </div>

        {/* Rows */}
        <div className="divide-y divide-[#E5E6E3]">
          {filteredAttributes.map((attr) => (
            <div
              key={attr.id}
              className={`grid grid-cols-12 gap-4 px-5 py-4 items-center ${
                attr.isConfidential ? 'bg-amber-50/50' : ''
              }`}
            >
              {/* Attribute Text */}
              <div className="col-span-5 flex items-start gap-2">
                {attr.isConfidential && (
                  <Shield className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />
                )}
                <input
                  type="text"
                  value={attr.attribute}
                  onChange={(e) =>
                    handleUpdateAttribute(attr.id, 'attribute', e.target.value)
                  }
                  className="w-full text-sm text-[#2D3538] bg-transparent border-none focus:outline-none focus:underline"
                />
              </div>

              {/* Type Dropdown */}
              <div className="col-span-2">
                <select
                  value={attr.type}
                  onChange={(e) =>
                    handleUpdateAttribute(
                      attr.id,
                      'type',
                      e.target.value as AttributeType
                    )
                  }
                  className="w-full text-xs bg-[#F3F4EE] px-2 py-1.5 rounded-lg border-none focus:outline-none focus:ring-1 focus:ring-[#2D3538] cursor-pointer"
                >
                  {ATTRIBUTE_TYPES.map((t) => (
                    <option key={t.value} value={t.value}>
                      {t.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Copyability */}
              <div className="col-span-2">
                <select
                  value={attr.copyability}
                  onChange={(e) =>
                    handleUpdateAttribute(
                      attr.id,
                      'copyability',
                      e.target.value as Copyability
                    )
                  }
                  className={`w-full text-xs px-2 py-1.5 rounded-lg border-none focus:outline-none cursor-pointer ${
                    COPYABILITY_OPTIONS.find(
                      (c) => c.value === attr.copyability
                    )?.color || 'bg-[#F3F4EE]'
                  }`}
                >
                  {COPYABILITY_OPTIONS.map((c) => (
                    <option key={c.value} value={c.value}>
                      {c.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Proof Required */}
              <div className="col-span-1 flex justify-center">
                <button
                  onClick={() =>
                    handleUpdateAttribute(
                      attr.id,
                      'requiresProof',
                      !attr.requiresProof
                    )
                  }
                  className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                    attr.requiresProof
                      ? (attr.evidenceIds?.length || 0) > 0
                        ? 'bg-green-500 border-green-500 text-white'
                        : 'bg-amber-500 border-amber-500 text-white'
                      : 'border-[#C0C1BE]'
                  }`}
                  title={
                    attr.requiresProof ? 'Proof required' : 'No proof needed'
                  }
                >
                  {attr.requiresProof &&
                    ((attr.evidenceIds?.length || 0) > 0 ? (
                      <Check className="w-3 h-3" />
                    ) : (
                      <AlertCircle className="w-3 h-3" />
                    ))}
                </button>
              </div>

              {/* Source */}
              <div className="col-span-1">
                <span
                  className={`text-[10px] uppercase font-mono ${
                    attr.source === 'derived'
                      ? 'text-[#5B5F61]'
                      : 'text-blue-600'
                  }`}
                >
                  {attr.source === 'derived' ? 'Auto' : 'User'}
                </span>
              </div>

              {/* Actions */}
              <div className="col-span-1 flex items-center gap-1 justify-end">
                <button
                  onClick={() => handleToggleConfidential(attr.id)}
                  className="p-1.5 hover:bg-[#F3F4EE] rounded-lg transition-colors"
                  title={
                    attr.isConfidential ? 'Make visible' : 'Mark confidential'
                  }
                >
                  {attr.isConfidential ? (
                    <EyeOff className="w-3.5 h-3.5 text-amber-500" />
                  ) : (
                    <Shield className="w-3.5 h-3.5 text-[#9D9F9F]" />
                  )}
                </button>
                <button
                  onClick={() => onShowEvidence(attr.id)}
                  className="p-1.5 hover:bg-[#F3F4EE] rounded-lg transition-colors"
                  title="Attach evidence"
                >
                  <Eye className="w-3.5 h-3.5 text-[#9D9F9F]" />
                </button>
                <button
                  onClick={() => handleRemoveAttribute(attr.id)}
                  className="p-1.5 hover:bg-red-50 rounded-lg transition-colors"
                  title="Delete"
                >
                  <X className="w-3.5 h-3.5 text-[#9D9F9F] hover:text-red-500" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Add New */}
      <div className="flex gap-2">
        <input
          type="text"
          value={newAttributeText}
          onChange={(e) => setNewAttributeText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleAddAttribute()}
          placeholder="Add unique attribute..."
          className="flex-1 px-4 py-3 bg-white border border-[#E5E6E3] rounded-xl text-sm focus:outline-none focus:border-[#2D3538]"
        />
        <Button
          onClick={handleAddAttribute}
          variant="outline"
          className="border-[#2D3538] text-[#2D3538]"
        >
          <Plus className="w-4 h-4 mr-1" /> Add
        </Button>
      </div>

      {/* Missing Proof Warning */}
      {proofRequired.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm text-amber-800 font-medium">
              {proofRequired.length} attribute
              {proofRequired.length > 1 ? 's' : ''} need proof
            </p>
            <p className="text-xs text-amber-700 mt-1">
              These will be marked as "hypothesis" in your positioning pack
              until evidence is attached.
            </p>
          </div>
        </div>
      )}

      {/* Navigation */}
      <div className="flex justify-between pt-6 border-t border-[#E5E6E3]">
        <Button variant="ghost" onClick={onBack} className="text-[#5B5F61]">
          Back
        </Button>
        <Button
          onClick={onContinue}
          className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-8"
        >
          Continue <ChevronRight className="w-4 h-4 ml-1" />
        </Button>
      </div>
    </div>
  );
}
