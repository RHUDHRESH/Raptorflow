'use client';

import React, { useState, useEffect } from 'react';
import { StrategicInput } from '../StrategicInput';
import { useGroundwork } from '../GroundworkProvider';
import { BrandEnergyData } from '@/lib/groundwork/types';
import { cn } from '@/lib/utils';

const VOICE_SAMPLES = [
  {
    id: 'professional',
    label: 'Professional & Authoritative',
    sample: 'We deliver enterprise-grade solutions that transform how teams collaborate.',
  },
  {
    id: 'friendly',
    label: 'Friendly & Approachable',
    sample: 'Hey! We built something cool that might help you save time. Want to check it out?',
  },
  {
    id: 'bold',
    label: 'Bold & Confident',
    sample: 'Stop wasting time on manual work. Automate it. Now.',
  },
  {
    id: 'casual',
    label: 'Casual & Conversational',
    sample: 'So, we made this thing that solves a problem we had. Thought you might like it too.',
  },
] as const;

export function BrandEnergySection() {
  const { state, updateSectionData } = useGroundwork();
  const sectionData = state.sections['brand-energy'].data as BrandEnergyData | null;

  const [chillBold, setChillBold] = useState(
    sectionData?.toneSliders.chillBold ?? 50
  );
  const [nerdyMassy, setNerdyMassy] = useState(
    sectionData?.toneSliders.nerdyMassy ?? 50
  );
  const [eliteApproachable, setEliteApproachable] = useState(
    sectionData?.toneSliders.eliteApproachable ?? 50
  );
  const [voiceSample, setVoiceSample] = useState(sectionData?.voiceSample || '');
  const [admiredBrands, setAdmiredBrands] = useState<string[]>(
    sectionData?.admiredBrands || ['']
  );

  useEffect(() => {
    const data: BrandEnergyData = {
      toneSliders: {
        chillBold,
        nerdyMassy,
        eliteApproachable,
      },
      voiceSample: voiceSample || undefined,
      admiredBrands: admiredBrands.filter((b) => b.trim() !== ''),
    };
    updateSectionData('brand-energy', data);
  }, [chillBold, nerdyMassy, eliteApproachable, voiceSample, admiredBrands, updateSectionData]);

  const addAdmiredBrand = () => {
    setAdmiredBrands([...admiredBrands, '']);
  };

  const updateAdmiredBrand = (index: number, value: string) => {
    setAdmiredBrands(admiredBrands.map((b, i) => (i === index ? value : b)));
  };

  const removeAdmiredBrand = (index: number) => {
    if (admiredBrands.length > 1) {
      setAdmiredBrands(admiredBrands.filter((_, i) => i !== index));
    }
  };

  const Slider = ({
    label,
    leftLabel,
    rightLabel,
    value,
    onChange,
  }: {
    label: string;
    leftLabel: string;
    rightLabel: string;
    value: number;
    onChange: (value: number) => void;
  }) => (
    <div>
      <div className="flex items-center justify-between mb-2">
        <label className="text-sm font-medium text-rf-ink">{label}</label>
        <span className="text-xs text-rf-subtle">{value}</span>
      </div>
      <div className="relative">
        <input
          type="range"
          min="0"
          max="100"
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="w-full h-2 bg-rf-cloud rounded-lg appearance-none cursor-pointer accent-rf-primary"
          style={{
            background: `linear-gradient(to right, #28295a 0%, #28295a ${value}%, #f0f2f5 ${value}%, #f0f2f5 100%)`,
          }}
        />
        <div className="flex justify-between mt-1 text-xs text-rf-subtle">
          <span>{leftLabel}</span>
          <span>{rightLabel}</span>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-8">
      <div className="space-y-6">
        <h3 className="text-sm font-medium text-rf-ink uppercase tracking-wide">
          Tone Sliders
        </h3>
        <Slider
          label="Chill vs Bold"
          leftLabel="Chill"
          rightLabel="Bold"
          value={chillBold}
          onChange={setChillBold}
        />
        <Slider
          label="Nerdy vs Massy"
          leftLabel="Nerdy"
          rightLabel="Massy"
          value={nerdyMassy}
          onChange={setNerdyMassy}
        />
        <Slider
          label="Elite vs Approachable"
          leftLabel="Elite"
          rightLabel="Approachable"
          value={eliteApproachable}
          onChange={setEliteApproachable}
        />
      </div>

      <div className="pt-6 border-t border-rf-cloud">
        <h3 className="text-sm font-medium text-rf-ink uppercase tracking-wide mb-4">
          Voice Samples
        </h3>
        <p className="text-sm text-rf-subtle mb-4">
          Which of these best matches your voice?
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {VOICE_SAMPLES.map((sample) => (
            <button
              key={sample.id}
              type="button"
              onClick={() => setVoiceSample(sample.id)}
              className={cn(
                'p-4 rounded-lg border text-left transition-all',
                voiceSample === sample.id
                  ? 'border-rf-primary bg-rf-cloud ring-1 ring-rf-primary/20'
                  : 'border-rf-cloud hover:border-rf-subtle'
              )}
            >
              <p className="text-sm font-medium text-rf-ink mb-1">{sample.label}</p>
              <p className="text-xs text-rf-subtle">{sample.sample}</p>
            </button>
          ))}
        </div>
      </div>

      <div className="pt-6 border-t border-rf-cloud">
        <h3 className="text-sm font-medium text-rf-ink uppercase tracking-wide mb-4">
          Admired Brands
        </h3>
        <p className="text-sm text-rf-subtle mb-4">
          Any brands you admire? (helps set visual and tonal benchmarks)
        </p>
        <div className="space-y-2">
          {admiredBrands.map((brand, index) => (
            <div key={index} className="flex items-center gap-2">
              <input
                type="text"
                value={brand}
                onChange={(e) => updateAdmiredBrand(index, e.target.value)}
                placeholder="e.g., Apple, Stripe, Notion"
                className="flex-1 px-4 py-2 rounded-lg border border-rf-cloud bg-rf-bg text-rf-ink placeholder:text-rf-muted focus:outline-none focus:border-rf-primary focus:ring-1 focus:ring-rf-primary/20 text-sm"
              />
              {admiredBrands.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeAdmiredBrand(index)}
                  className="p-2 text-rf-subtle hover:text-rf-error transition-colors"
                >
                  <span className="text-sm">×</span>
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            onClick={addAdmiredBrand}
            className="text-sm text-rf-subtle hover:text-rf-ink transition-colors"
          >
            + Add another brand
          </button>
        </div>
      </div>
    </div>
  );
}

