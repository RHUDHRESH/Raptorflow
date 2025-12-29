'use client';

import React from 'react';
import {
  Check,
  Lock,
  Download,
  ArrowRight,
  FileText,
  BarChart3,
  Grid3X3,
  Lightbulb,
  Target,
  Package,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Phase3Data } from '@/lib/foundation';
import { toast } from 'sonner';

interface Phase3ReviewProps {
  phase3: Phase3Data;
  onLock: () => void;
  onBack: () => void;
}

// Summary card component
function SummaryCard({
  icon: Icon,
  title,
  status,
  items,
}: {
  icon: React.ElementType;
  title: string;
  status: 'complete' | 'incomplete' | 'warning';
  items: string[];
}) {
  const statusColors = {
    complete: { bg: 'bg-[#22C55E]/10', icon: 'text-[#22C55E]' },
    incomplete: { bg: 'bg-[#EF4444]/10', icon: 'text-[#EF4444]' },
    warning: { bg: 'bg-[#F59E0B]/10', icon: 'text-[#F59E0B]' },
  };

  const colors = statusColors[status];

  return (
    <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div
            className={`w-10 h-10 rounded-xl flex items-center justify-center ${colors.bg}`}
          >
            <Icon className={`w-5 h-5 ${colors.icon}`} />
          </div>
          <h3 className="font-medium text-[#2D3538]">{title}</h3>
        </div>
        {status === 'complete' && (
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-[#22C55E]/10 text-[#22C55E] text-[10px] font-mono uppercase">
            <Check className="w-3 h-3" />
            Done
          </span>
        )}
      </div>

      <ul className="space-y-2">
        {items.slice(0, 3).map((item, index) => (
          <li
            key={index}
            className="text-[13px] text-[#5B5F61] flex items-start gap-2"
          >
            <span className="text-[#C0C1BE]">•</span>
            <span className="line-clamp-1">{item}</span>
          </li>
        ))}
        {items.length > 3 && (
          <li className="text-[12px] text-[#9D9F9F]">
            +{items.length - 3} more
          </li>
        )}
        {items.length === 0 && (
          <li className="text-[13px] text-[#9D9F9F] italic">No items</li>
        )}
      </ul>
    </div>
  );
}

export function Phase3Review({ phase3, onLock, onBack }: Phase3ReviewProps) {
  const handleExportJSON = () => {
    const dataStr = JSON.stringify(phase3, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'phase3-value-pack.json';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    toast.success('Value Pack exported!');
  };

  // Extract summary data
  const primaryJob =
    phase3.jtbd?.jobs?.find((j) => j.isPrimary)?.statement || 'Not defined';
  const topPains =
    phase3.vpc?.customerProfile?.pains?.slice(0, 3).map((p) => p.text) || [];
  const topGains =
    phase3.vpc?.customerProfile?.gains?.slice(0, 3).map((g) => g.text) || [];

  const vpcItems = [
    `${phase3.vpc?.customerProfile?.jobs?.length || 0} jobs`,
    `${phase3.vpc?.customerProfile?.pains?.length || 0} pains`,
    `${phase3.vpc?.customerProfile?.gains?.length || 0} gains`,
    `${phase3.vpc?.fitCoverage?.score || 0}% fit coverage`,
  ];

  const proofItems = phase3.proofArtifacts?.map((a) => a.title) || [];

  const canvasFactors =
    phase3.strategyCanvas?.factors?.map((f) => f.name) || [];

  const errcItems = [
    ...(phase3.errc?.eliminate?.map((e) => `Eliminate: ${e.factor}`) || []),
    ...(phase3.errc?.create?.map((c) => `Create: ${c.factor}`) || []),
  ];

  // Check completeness
  const hasJTBD = phase3.jtbd?.jobs?.some((j) => j.isPrimary);
  const hasVPC = (phase3.vpc?.customerProfile?.pains?.length || 0) > 0;
  const hasProof = (phase3.proofArtifacts?.length || 0) > 0;
  const hasCanvas = (phase3.strategyCanvas?.factors?.length || 0) > 0;
  const hasERRC = (phase3.errc?.create?.length || 0) > 0;
  const hasUVP = phase3.uvpDrafts?.some((d) => d.isPrimary);

  const isComplete = hasJTBD && hasVPC && hasCanvas && hasERRC && hasUVP;

  return (
    <div className="space-y-8">
      {/* Value Pack Header */}
      <div className="bg-[#2D3538] rounded-3xl p-8 text-white text-center">
        <h2 className="font-serif text-[32px] mb-2">Value Pack</h2>
        <p className="text-white/60 text-[15px]">
          Your complete Phase 3 outputs — ready to power positioning.
        </p>
      </div>

      {/* Summary Cards Grid */}
      <div className="grid grid-cols-2 gap-4">
        <SummaryCard
          icon={Target}
          title="JTBD Progress Statement"
          status={hasJTBD ? 'complete' : 'incomplete'}
          items={[primaryJob]}
        />

        <SummaryCard
          icon={FileText}
          title="VPC Fit Map"
          status={hasVPC ? 'complete' : 'incomplete'}
          items={vpcItems}
        />

        <SummaryCard
          icon={BarChart3}
          title="Proof Stack"
          status={
            hasProof
              ? 'complete'
              : proofItems.length === 0
                ? 'warning'
                : 'complete'
          }
          items={
            proofItems.length > 0
              ? proofItems
              : ['No proof added (claims will be unproven)']
          }
        />

        <SummaryCard
          icon={Grid3X3}
          title="Strategy Canvas"
          status={hasCanvas ? 'complete' : 'incomplete'}
          items={canvasFactors}
        />

        <SummaryCard
          icon={Lightbulb}
          title="ERRC Grid"
          status={hasERRC ? 'complete' : 'incomplete'}
          items={errcItems}
        />

        <SummaryCard
          icon={Package}
          title="Offer Profile"
          status={phase3.offerProfile ? 'complete' : 'warning'}
          items={
            phase3.offerProfile
              ? [
                  `Delivery: ${phase3.offerProfile.deliveryMode}`,
                  `TTFV: ${phase3.offerProfile.timeToFirstValue} days`,
                  `Risk: ${phase3.offerProfile.riskPolicy || 'None'}`,
                ]
              : ['Not configured']
          }
        />
      </div>

      {/* Primary Claims */}
      <div className="bg-[#FAFAF8] rounded-2xl p-6">
        <h3 className="text-[11px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">
          Primary Claims
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white rounded-xl p-4 border border-[#E5E6E3]">
            <span className="text-[10px] font-mono uppercase text-[#9D9F9F] block mb-2">
              UVP
            </span>
            <p className="text-[14px] text-[#2D3538]">
              {phase3.uvpDrafts?.find((d) => d.isPrimary)?.text ||
                'Not selected'}
            </p>
          </div>
          <div className="bg-white rounded-xl p-4 border border-[#E5E6E3]">
            <span className="text-[10px] font-mono uppercase text-[#9D9F9F] block mb-2">
              USP
            </span>
            <p className="text-[14px] text-[#2D3538]">
              {phase3.uspDrafts?.find((d) => d.isPrimary)?.text ||
                'Not selected'}
            </p>
          </div>
        </div>

        {phase3.mechanismLine && (
          <div className="mt-4 bg-white rounded-xl p-4 border border-[#E5E6E3]">
            <span className="text-[10px] font-mono uppercase text-[#9D9F9F] block mb-2">
              Mechanism
            </span>
            <p className="text-[14px] text-[#2D3538]">
              We do it by: {phase3.mechanismLine}
            </p>
          </div>
        )}
      </div>

      {/* Completeness Warning */}
      {!isComplete && (
        <div className="flex items-center gap-3 bg-[#F59E0B]/10 rounded-xl px-5 py-4">
          <Lock className="w-5 h-5 text-[#F59E0B] flex-shrink-0" />
          <p className="text-[14px] text-[#5B5F61]">
            Some sections are incomplete. You can still lock, but results may be
            limited.
          </p>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between pt-8 border-t border-[#E5E6E3]">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            onClick={onBack}
            className="text-[#5B5F61] hover:text-[#2D3538]"
          >
            ← Back
          </Button>
          <Button
            variant="outline"
            onClick={handleExportJSON}
            className="text-[#5B5F61] border-[#C0C1BE]"
          >
            <Download className="w-4 h-4 mr-2" />
            Export JSON
          </Button>
        </div>
        <Button
          onClick={onLock}
          className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-10 py-6 rounded-2xl text-[15px] font-medium"
        >
          <Lock className="w-4 h-4 mr-2" />
          Lock Phase 3 Outputs
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </div>
    </div>
  );
}
