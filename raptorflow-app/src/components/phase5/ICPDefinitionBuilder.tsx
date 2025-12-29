'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Building2,
  Users,
  MapPin,
  Wrench,
  Globe,
  DollarSign,
  ChevronDown,
  Plus,
  X,
  Check,
  FileText,
  Quote,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ICP, ICPFirmographics, ICPTechnographics } from '@/lib/foundation';

interface ICPDefinitionBuilderProps {
  icp: ICP;
  onUpdate: (updates: Partial<ICP>) => void;
  onLock: () => void;
  evidenceQuotes?: Array<{ field: string; quote: string; source: string }>;
}

// Industry options
const INDUSTRY_OPTIONS = [
  'Technology',
  'SaaS',
  'E-commerce',
  'Healthcare',
  'Finance',
  'Education',
  'Manufacturing',
  'Retail',
  'Professional Services',
  'Media & Entertainment',
  'Real Estate',
  'Non-profit',
];

// Operating model options
const OPERATING_MODEL_OPTIONS = [
  { value: 'founder-led', label: 'Founder-led' },
  { value: 'team-led', label: 'Team-led' },
  { value: 'investor-led', label: 'Investor/Board-led' },
];

const SALES_MOTION_OPTIONS = [
  { value: 'inbound', label: 'Inbound' },
  { value: 'outbound', label: 'Outbound' },
  { value: 'product-led', label: 'Product-led' },
  { value: 'channel', label: 'Channel/Partner' },
];

function EvidenceDrawer({
  quotes,
  isOpen,
  onClose,
}: {
  quotes: Array<{ field: string; quote: string; source: string }>;
  isOpen: boolean;
  onClose: () => void;
}) {
  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ x: 300, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: 300, opacity: 0 }}
      className="fixed right-0 top-0 h-full w-96 bg-white border-l border-[#E5E6E3] shadow-xl z-50 overflow-y-auto"
    >
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="font-serif text-xl text-[#2D3538]">Evidence</h3>
          <button
            onClick={onClose}
            className="p-2 hover:bg-[#F3F4EE] rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-[#9D9F9F]" />
          </button>
        </div>

        {quotes.length > 0 ? (
          <div className="space-y-4">
            {quotes.map((q, i) => (
              <div key={i} className="bg-[#FAFAF8] rounded-xl p-4">
                <span className="text-[9px] font-mono uppercase text-[#9D9F9F] mb-2 block">
                  {q.field}
                </span>
                <div className="flex gap-2">
                  <Quote className="w-4 h-4 text-[#9D9F9F] flex-shrink-0 mt-1" />
                  <p className="text-sm text-[#2D3538] italic">{q.quote}</p>
                </div>
                <span className="text-[10px] text-[#9D9F9F] mt-2 block">
                  Source: {q.source}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-[#9D9F9F]">
            <FileText className="w-10 h-10 mx-auto mb-3 opacity-40" />
            <p className="text-sm">No evidence quotes available</p>
          </div>
        )}
      </div>
    </motion.div>
  );
}

export function ICPDefinitionBuilder({
  icp,
  onUpdate,
  onLock,
  evidenceQuotes = [],
}: ICPDefinitionBuilderProps) {
  const [showEvidence, setShowEvidence] = useState(false);
  const [newIndustry, setNewIndustry] = useState('');
  const [newTool, setNewTool] = useState('');
  const [operatingModel, setOperatingModel] = useState('founder-led');
  const [salesMotion, setSalesMotion] = useState('inbound');

  const updateFirmographics = (updates: Partial<ICPFirmographics>) => {
    onUpdate({
      firmographics: { ...icp.firmographics, ...updates },
    });
  };

  const updateTechnographics = (updates: Partial<ICPTechnographics>) => {
    onUpdate({
      technographics: { ...icp.technographics, ...updates },
    });
  };

  const addIndustry = (industry: string) => {
    if (industry && !icp.firmographics.industries.includes(industry)) {
      updateFirmographics({
        industries: [...icp.firmographics.industries, industry],
      });
    }
    setNewIndustry('');
  };

  const removeIndustry = (industry: string) => {
    updateFirmographics({
      industries: icp.firmographics.industries.filter((i) => i !== industry),
    });
  };

  const addTool = (tool: string) => {
    if (tool && !icp.technographics.mustHave.includes(tool)) {
      updateTechnographics({
        mustHave: [...icp.technographics.mustHave, tool],
      });
    }
    setNewTool('');
  };

  const removeTool = (tool: string) => {
    updateTechnographics({
      mustHave: icp.technographics.mustHave.filter((t) => t !== tool),
    });
  };

  return (
    <div className="space-y-6">
      {/* Evidence Button */}
      <div className="flex justify-end">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowEvidence(true)}
          className="rounded-xl"
        >
          <FileText className="w-4 h-4 mr-2" />
          View Evidence ({evidenceQuotes.length})
        </Button>
      </div>

      {/* ICP Name */}
      <div className="bg-[#2D3538] rounded-2xl p-6">
        <label className="text-[10px] font-mono uppercase tracking-[0.15em] text-white/60 mb-3 block">
          ICP Name
        </label>
        <input
          type="text"
          value={icp.name}
          onChange={(e) => onUpdate({ name: e.target.value })}
          className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white font-serif text-xl focus:outline-none focus:border-white/40"
        />
      </div>

      {/* Firmographics */}
      <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6 space-y-6">
        <div className="flex items-center gap-3 mb-2">
          <Building2 className="w-5 h-5 text-[#9D9F9F]" />
          <h3 className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
            Firmographics
          </h3>
        </div>

        {/* Industries */}
        <div>
          <label className="text-sm font-medium text-[#2D3538] mb-3 block">
            Industries
          </label>
          <div className="flex flex-wrap gap-2 mb-3">
            {icp.firmographics.industries.map((industry) => (
              <div
                key={industry}
                className="flex items-center gap-2 bg-[#F3F4EE] rounded-xl px-3 py-2"
              >
                <span className="text-sm text-[#2D3538]">{industry}</span>
                <button onClick={() => removeIndustry(industry)}>
                  <X className="w-3 h-3 text-[#9D9F9F] hover:text-red-500" />
                </button>
              </div>
            ))}
          </div>
          <div className="flex gap-2">
            <select
              value={newIndustry}
              onChange={(e) => setNewIndustry(e.target.value)}
              className="flex-1 border border-[#E5E6E3] rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-[#2D3538]"
            >
              <option value="">Select industry...</option>
              {INDUSTRY_OPTIONS.filter(
                (i) => !icp.firmographics.industries.includes(i)
              ).map((i) => (
                <option key={i} value={i}>
                  {i}
                </option>
              ))}
            </select>
            <Button
              variant="outline"
              size="sm"
              onClick={() => addIndustry(newIndustry)}
              disabled={!newIndustry}
              className="rounded-xl"
            >
              <Plus className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Employee Range */}
        <div>
          <label className="text-sm font-medium text-[#2D3538] mb-3 block">
            Employee Range
          </label>
          <div className="flex items-center gap-4">
            <input
              type="number"
              value={icp.firmographics.companySizeMin}
              onChange={(e) =>
                updateFirmographics({
                  companySizeMin: parseInt(e.target.value) || 0,
                })
              }
              className="w-32 border border-[#E5E6E3] rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-[#2D3538]"
              placeholder="Min"
            />
            <span className="text-[#9D9F9F]">to</span>
            <input
              type="number"
              value={icp.firmographics.companySizeMax}
              onChange={(e) =>
                updateFirmographics({
                  companySizeMax: parseInt(e.target.value) || 0,
                })
              }
              className="w-32 border border-[#E5E6E3] rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-[#2D3538]"
              placeholder="Max"
            />
            <span className="text-sm text-[#5B5F61]">employees</span>
          </div>
        </div>

        {/* Revenue Range */}
        <div>
          <label className="text-sm font-medium text-[#2D3538] mb-3 block">
            Revenue Range (Optional)
          </label>
          <div className="flex items-center gap-4">
            <div className="flex items-center">
              <span className="text-[#9D9F9F] mr-2">$</span>
              <input
                type="number"
                value={icp.firmographics.revenueMin}
                onChange={(e) =>
                  updateFirmographics({
                    revenueMin: parseInt(e.target.value) || 0,
                  })
                }
                className="w-32 border border-[#E5E6E3] rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-[#2D3538]"
                placeholder="Min"
              />
            </div>
            <span className="text-[#9D9F9F]">to</span>
            <div className="flex items-center">
              <span className="text-[#9D9F9F] mr-2">$</span>
              <input
                type="number"
                value={icp.firmographics.revenueMax}
                onChange={(e) =>
                  updateFirmographics({
                    revenueMax: parseInt(e.target.value) || 0,
                  })
                }
                className="w-32 border border-[#E5E6E3] rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-[#2D3538]"
                placeholder="Max"
              />
            </div>
          </div>
        </div>

        {/* Geographies */}
        <div>
          <label className="text-sm font-medium text-[#2D3538] mb-3 block">
            Geographies
          </label>
          <div className="flex flex-wrap gap-2">
            {icp.firmographics.geographies.map((geo) => (
              <div
                key={geo}
                className="flex items-center gap-2 bg-[#F3F4EE] rounded-xl px-3 py-2"
              >
                <Globe className="w-3 h-3 text-[#9D9F9F]" />
                <span className="text-sm text-[#2D3538]">{geo}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Technographics */}
      <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6 space-y-6">
        <div className="flex items-center gap-3 mb-2">
          <Wrench className="w-5 h-5 text-[#9D9F9F]" />
          <h3 className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
            Technographics
          </h3>
        </div>

        {/* Must-Have Tools */}
        <div>
          <label className="text-sm font-medium text-[#2D3538] mb-3 block">
            Must-Have Tools
          </label>
          <div className="flex flex-wrap gap-2 mb-3">
            {icp.technographics.mustHave.map((tool) => (
              <div
                key={tool}
                className="flex items-center gap-2 bg-[#2D3538] text-white rounded-xl px-3 py-2"
              >
                <span className="text-sm">{tool}</span>
                <button onClick={() => removeTool(tool)}>
                  <X className="w-3 h-3 opacity-60 hover:opacity-100" />
                </button>
              </div>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              value={newTool}
              onChange={(e) => setNewTool(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addTool(newTool)}
              className="flex-1 border border-[#E5E6E3] rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-[#2D3538]"
              placeholder="Add tool..."
            />
            <Button
              variant="outline"
              size="sm"
              onClick={() => addTool(newTool)}
              disabled={!newTool}
              className="rounded-xl"
            >
              <Plus className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Nice-to-Have */}
        <div>
          <label className="text-sm font-medium text-[#2D3538] mb-3 block">
            Nice-to-Have Tools
          </label>
          <div className="flex flex-wrap gap-2">
            {icp.technographics.niceToHave.map((tool) => (
              <div
                key={tool}
                className="flex items-center gap-2 bg-[#F3F4EE] rounded-xl px-3 py-2"
              >
                <span className="text-sm text-[#5B5F61]">{tool}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Operating Model */}
      <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6 space-y-6">
        <div className="flex items-center gap-3 mb-2">
          <Users className="w-5 h-5 text-[#9D9F9F]" />
          <h3 className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
            Operating Model
          </h3>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-[#2D3538] mb-3 block">
              Leadership Style
            </label>
            <div className="flex flex-wrap gap-2">
              {OPERATING_MODEL_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => setOperatingModel(opt.value)}
                  className={`px-4 py-2 rounded-xl text-sm transition-all ${
                    operatingModel === opt.value
                      ? 'bg-[#2D3538] text-white'
                      : 'bg-[#F3F4EE] text-[#5B5F61] hover:bg-[#E5E6E3]'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-sm font-medium text-[#2D3538] mb-3 block">
              Sales Motion
            </label>
            <div className="flex flex-wrap gap-2">
              {SALES_MOTION_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => setSalesMotion(opt.value)}
                  className={`px-4 py-2 rounded-xl text-sm transition-all ${
                    salesMotion === opt.value
                      ? 'bg-[#2D3538] text-white'
                      : 'bg-[#F3F4EE] text-[#5B5F61] hover:bg-[#E5E6E3]'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Lock Button */}
      <div className="flex justify-end">
        <Button
          onClick={onLock}
          className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-8 py-6 rounded-2xl text-lg font-medium"
        >
          <Check className="w-5 h-5 mr-2" />
          Lock ICP Definition
        </Button>
      </div>

      {/* Evidence Drawer */}
      <EvidenceDrawer
        quotes={evidenceQuotes}
        isOpen={showEvidence}
        onClose={() => setShowEvidence(false)}
      />
    </div>
  );
}
