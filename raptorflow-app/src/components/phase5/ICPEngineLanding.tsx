'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Users,
  Target,
  Zap,
  Shield,
  AlertCircle,
  Globe,
  Building2,
  Briefcase,
  DollarSign,
  Wrench,
  ChevronRight,
  Sparkles,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  FoundationData,
  DataQualityMeter,
  EvidenceEntity,
  loadFoundationDB,
} from '@/lib/foundation';

interface ICPEngineLandingProps {
  foundation: FoundationData | null;
  onContinue: () => void;
  onBusinessTypeChange: (type: 'b2b' | 'b2c' | 'hybrid') => void;
  onGeoFocusChange: (focus: 'india' | 'global' | 'mixed') => void;
  businessType: 'b2b' | 'b2c' | 'hybrid';
  geoFocus: 'india' | 'global' | 'mixed';
}

// Calculate data quality from foundation
function calculateDataQuality(
  foundation: FoundationData | null
): DataQualityMeter {
  if (!foundation) {
    return {
      firmographic: 0,
      pain: 0,
      trigger: 0,
      proof: 0,
      constraints: 0,
      overall: 0,
    };
  }

  let firmographic = 0;
  let pain = 0;
  let trigger = 0;
  let proof = 0;
  // let constraints = 0; // Not available in current interface

  // Phase 1: Identity, offers
  if (foundation.phase1?.identity?.company) firmographic += 30;
  if (foundation.phase1?.value?.priceRangeMin) firmographic += 20;
  if (foundation.phase1?.buyerUser?.buyerRoles?.length)
    firmographic += 20;

  // Phase 3: Pains, gains, VPC
  if (foundation.phase3?.vpc?.customerProfile?.pains?.length) pain += 40;
  if (foundation.phase3?.jtbd?.strugglingMoments?.length) pain += 30;
  if (foundation.phase3?.vpc?.customerProfile?.gains?.length) pain += 30;

  // Phase 1/3: Triggers
  if (foundation.phase1?.triggers?.triggers?.length) trigger += 50;
  if (foundation.phase3?.jtbd?.switchTriggers?.length) trigger += 50;

  // Phase 3: Proof stack
  if (foundation.phase3?.proofArtifacts?.length) proof += 50;
  if (foundation.phase3?.proofStack?.length) proof += 50;

  // Phase 1: Constraints (not available in current interface)
  // if (foundation.phase1?.constraints?.constraints?.length) constraints += 40;
  // if (foundation.phase1?.constraints?.budget?.limit) constraints += 30;
  // if (foundation.phase1?.constraints?.timeline?.urgency) constraints += 30;

  const overall = Math.round(
    (firmographic + pain + trigger + proof) / 4 // Removed constraints
  );

  return {
    firmographic: Math.min(100, firmographic),
    pain: Math.min(100, pain),
    trigger: Math.min(100, trigger),
    proof: Math.min(100, proof),
    constraints: 0, // Hardcoded since data not available
    overall,
  };
}

// Extract evidence entities from foundation
function extractEvidenceEntities(
  foundation: FoundationData | null
): EvidenceEntity[] {
  if (!foundation) return [];

  const entities: EvidenceEntity[] = [];

  // Industries from Phase 4 segments
  foundation.phase4?.targetSegments?.forEach((seg) => {
    if (seg.firmographics?.industry) {
      entities.push({
        id: `ind-${seg.id}`,
        type: 'industry',
        value: seg.firmographics.industry,
        source: 'Phase 4 Segments',
        confidence: 'proven',
      });
    }
  });

  // Tools from technographics
  foundation.phase1?.currentSystem?.workflowSteps?.forEach((step, i) => {
    if (step.tool) {
      entities.push({
        id: `tool-${i}`,
        type: 'tool',
        value: step.tool,
        source: 'Phase 1 Workflow',
        confidence: 'proven',
      });
    }
  });

  // Competitors from Phase 4
  foundation.phase4?.competitiveAlternatives?.direct?.forEach((comp) => {
    entities.push({
      id: `comp-${comp.id}`,
      type: 'competitor',
      value: comp.name,
      source: 'Phase 4 Alternatives',
      confidence: 'proven',
    });
  });

  // Price from Phase 1
  if (foundation.phase1?.value?.priceRangeMin) {
    entities.push({
      id: 'price-range',
      type: 'price',
      value: `$${foundation.phase1.value.priceRangeMin} - $${foundation.phase1.value.priceRangeMax || 'N/A'}`,
      source: 'Phase 1 Value',
      confidence: 'proven',
    });
  }

  return entities;
}

const ENTITY_ICONS: Record<string, React.ElementType> = {
  industry: Building2,
  title: Briefcase,
  tool: Wrench,
  competitor: Target,
  price: DollarSign,
  trigger: Zap,
  outcome: Sparkles,
};

export function ICPEngineLanding({
  foundation,
  onContinue,
  onBusinessTypeChange,
  onGeoFocusChange,
  businessType,
  geoFocus,
}: ICPEngineLandingProps) {
  const [dataQuality, setDataQuality] = useState<DataQualityMeter>({
    firmographic: 0,
    pain: 0,
    trigger: 0,
    proof: 0,
    constraints: 0,
    overall: 0,
  });
  const [evidenceEntities, setEvidenceEntities] = useState<EvidenceEntity[]>(
    []
  );

  useEffect(() => {
    setDataQuality(calculateDataQuality(foundation));
    setEvidenceEntities(extractEvidenceEntities(foundation));
  }, [foundation]);

  const qualityBars = [
    {
      label: 'Firmographic',
      value: dataQuality.firmographic,
      color: '#2D3538',
    },
    { label: 'Pain Signals', value: dataQuality.pain, color: '#2D3538' },
    { label: 'Triggers', value: dataQuality.trigger, color: '#2D3538' },
    { label: 'Proof', value: dataQuality.proof, color: '#2D3538' },
    { label: 'Constraints', value: dataQuality.constraints, color: '#2D3538' },
  ];

  return (
    <div className="space-y-8">
      {/* Hero Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-[#2D3538] rounded-3xl p-10 text-white"
      >
        <div className="flex items-start gap-6">
          <div className="w-16 h-16 bg-white/10 rounded-2xl flex items-center justify-center flex-shrink-0">
            <Users className="w-8 h-8 text-white" />
          </div>
          <div className="flex-1">
            <h2 className="font-serif text-3xl mb-3">ICP Engine</h2>
            <p className="text-white/70 text-lg leading-relaxed mb-6">
              We will generate{' '}
              <span className="text-white font-medium">3 ICP candidates</span> +
              <span className="text-white font-medium"> 1 negative ICP</span>{' '}
              based on everything collected so far. No more questioning — just
              confirm and adjust.
            </p>
            <div className="flex flex-wrap gap-3">
              <div className="flex items-center gap-2 bg-white/10 rounded-xl px-4 py-2">
                <Target className="w-4 h-4 text-white/60" />
                <span className="text-sm">Buying Group Mapping</span>
              </div>
              <div className="flex items-center gap-2 bg-white/10 rounded-xl px-4 py-2">
                <Zap className="w-4 h-4 text-white/60" />
                <span className="text-sm">Trigger Detection</span>
              </div>
              <div className="flex items-center gap-2 bg-white/10 rounded-xl px-4 py-2">
                <Shield className="w-4 h-4 text-white/60" />
                <span className="text-sm">Disqualifier List</span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Configuration Toggles */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-2 gap-4"
      >
        {/* Business Type */}
        <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6">
          <label className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] block mb-3">
            Business Type
          </label>
          <div className="flex gap-2">
            {(['b2b', 'b2c', 'hybrid'] as const).map((type) => (
              <button
                key={type}
                onClick={() => onBusinessTypeChange(type)}
                className={`flex-1 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                  businessType === type
                    ? 'bg-[#2D3538] text-white'
                    : 'bg-[#F3F4EE] text-[#5B5F61] hover:bg-[#E5E6E3]'
                }`}
              >
                {type.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Geography Focus */}
        <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6">
          <label className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] block mb-3">
            Geography Focus
          </label>
          <div className="flex gap-2">
            {(['india', 'global', 'mixed'] as const).map((geo) => (
              <button
                key={geo}
                onClick={() => onGeoFocusChange(geo)}
                className={`flex-1 px-4 py-3 rounded-xl text-sm font-medium transition-all capitalize ${
                  geoFocus === geo
                    ? 'bg-[#2D3538] text-white'
                    : 'bg-[#F3F4EE] text-[#5B5F61] hover:bg-[#E5E6E3]'
                }`}
              >
                {geo === 'india'
                  ? '🇮🇳 India'
                  : geo === 'global'
                    ? '🌍 Global'
                    : '🔀 Mixed'}
              </button>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Data Quality Meter */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white border border-[#E5E6E3] rounded-2xl p-6"
      >
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-1">
              Data Quality Meter
            </h3>
            <p className="text-sm text-[#5B5F61]">
              Coverage of required signals for ICP generation
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div
              className={`w-3 h-3 rounded-full ${
                dataQuality.overall >= 70
                  ? 'bg-green-500'
                  : dataQuality.overall >= 40
                    ? 'bg-yellow-500'
                    : 'bg-red-500'
              }`}
            />
            <span className="font-mono text-lg font-medium text-[#2D3538]">
              {dataQuality.overall}%
            </span>
          </div>
        </div>

        <div className="space-y-4">
          {qualityBars.map((bar, i) => (
            <div key={bar.label} className="flex items-center gap-4">
              <span className="text-sm text-[#5B5F61] w-28 flex-shrink-0">
                {bar.label}
              </span>
              <div className="flex-1 h-2 bg-[#F3F4EE] rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${bar.value}%` }}
                  transition={{ delay: 0.3 + i * 0.1, duration: 0.5 }}
                  className="h-full rounded-full"
                  style={{ backgroundColor: bar.color }}
                />
              </div>
              <span className="text-xs font-mono text-[#9D9F9F] w-10 text-right">
                {bar.value}%
              </span>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Evidence Chips */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-[#FAFAF8] border border-[#E5E6E3] rounded-2xl p-6"
      >
        <h3 className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">
          Auto-Detected Evidence ({evidenceEntities.length} entities)
        </h3>

        {evidenceEntities.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {evidenceEntities.map((entity) => {
              const Icon = ENTITY_ICONS[entity.type] || Target;
              return (
                <div
                  key={entity.id}
                  className="flex items-center gap-2 bg-white border border-[#E5E6E3] rounded-xl px-3 py-2"
                >
                  <Icon className="w-3.5 h-3.5 text-[#9D9F9F]" />
                  <span className="text-sm text-[#2D3538]">{entity.value}</span>
                  <span className="text-[9px] font-mono uppercase text-[#9D9F9F] bg-[#F3F4EE] px-1.5 py-0.5 rounded">
                    {entity.type}
                  </span>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="flex items-center gap-3 text-[#9D9F9F]">
            <AlertCircle className="w-5 h-5" />
            <span className="text-sm">
              No evidence entities extracted yet. Complete earlier phases for
              richer ICPs.
            </span>
          </div>
        )}
      </motion.div>

      {/* Disclaimer */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="flex items-start gap-3 p-4 bg-[#F3F4EE] rounded-xl"
      >
        <AlertCircle className="w-5 h-5 text-[#9D9F9F] flex-shrink-0 mt-0.5" />
        <p className="text-sm text-[#5B5F61] leading-relaxed">
          <strong className="text-[#2D3538]">Why this matters:</strong> B2B
          purchases involve 6–10 stakeholders, and buyers spend only ~17% of the
          journey talking to suppliers. If you don't map the buying group and
          their "buying jobs," you're building fantasy marketing.
        </p>
      </motion.div>
    </div>
  );
}
