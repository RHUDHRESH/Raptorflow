'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Playfair_Display } from 'next/font/google';
import { Sparkles, Target, Users, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

const playfair = Playfair_Display({ subsets: ['latin'] });

interface JTBDCanvasProps {
  functional: string;
  emotional: string;
  social: string;
  onChange: (
    field: 'functional' | 'emotional' | 'social',
    value: string
  ) => void;
}

interface JobInputProps {
  id: string;
  label: string;
  value: string;
  placeholder: string;
  icon: React.ReactNode;
  description: string;
  onChange: (value: string) => void;
}

function JobInput({
  id,
  label,
  value,
  placeholder,
  icon,
  description,
  onChange,
}: JobInputProps) {
  return (
    <div className="flex flex-col gap-3 group">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-[#2D3538]/5 flex items-center justify-center text-[#2D3538] group-focus-within:bg-[#2D3538] group-focus-within:text-white transition-all">
          {icon}
        </div>
        <div>
          <label
            htmlFor={id}
            className="text-sm font-semibold uppercase tracking-wider text-[#2D3538]"
          >
            {label}
          </label>
          <p className="text-xs text-[#5B5F61]">{description}</p>
        </div>
      </div>
      <textarea
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full min-h-[120px] p-5 rounded-[12px] border border-[#C0C1BE] bg-[#F3F4EE]/30 focus:bg-white focus:border-[#2D3538] focus:ring-1 focus:ring-[#2D3538] outline-none transition-all resize-none text-[16px] leading-relaxed"
      />
    </div>
  );
}

export function JTBDCanvas({
  functional,
  emotional,
  social,
  onChange,
}: JTBDCanvasProps) {
  return (
    <div className="space-y-12">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <JobInput
          id="functional"
          label="Functional Job"
          value={functional}
          description="What practical task are they completing?"
          placeholder="e.g. 'Automate the generation of personalized email sequences from a single landing page URL.'"
          icon={<Zap className="w-5 h-5" />}
          onChange={(val) => onChange('functional', val)}
        />
        <JobInput
          id="emotional"
          label="Emotional Job"
          value={emotional}
          description="How do they want to feel during/after?"
          placeholder="e.g. 'Feel like a tactical genius who is finally ahead of the market, not drowning in tools.'"
          icon={<Sparkles className="w-5 h-5" />}
          onChange={(val) => onChange('emotional', val)}
        />
        <JobInput
          id="social"
          label="Social Job"
          value={social}
          description="How do they want to be perceived by others?"
          placeholder="e.g. 'Be seen as the high-leverage founder who builds systems, not the one doing manual grunt work.'"
          icon={<Users className="w-5 h-5" />}
          onChange={(val) => onChange('social', val)}
        />
      </div>

      {/* Reflection Card */}
      <div className="bg-[#2D3538] text-white p-8 rounded-[14px] flex gap-6 items-start">
        <div className="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center flex-shrink-0">
          <Target className="w-6 h-6 text-white" />
        </div>
        <div className="space-y-2">
          <h4 className="font-medium text-lg italic opacity-90">
            The Progress Formula
          </h4>
          <p className="text-sm text-white/60 leading-relaxed max-w-2xl">
            "When I [Situation], I want to [Functional Job], so that I can
            [Emotional/Social Outcome]."
            <br />
            <span className="block mt-4 text-white/40 font-mono text-[10px] uppercase tracking-widest">
              Pro-tip: Specificity is the difference between commodity and
              luxury.
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}
