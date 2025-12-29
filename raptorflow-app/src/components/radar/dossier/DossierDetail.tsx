'use client';

import React from 'react';
import { Dossier } from '../types';
import {
  Dialog,
  DialogContent,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  ArrowLeft,
  Download,
  Share2,
  Target,
  Lightbulb,
  Quote,
  Zap,
} from 'lucide-react';

interface DossierDetailProps {
  dossier: Dossier | null;
  open: boolean;
  onClose: () => void;
  onConvertToMove?: (dossier: Dossier) => void;
}

export function DossierDetail({ dossier, open, onClose, onConvertToMove }: DossierDetailProps) {
  if (!dossier) return null;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-5xl h-[90vh] p-0 overflow-hidden flex flex-col bg-[#F8F9F7] border-[#C0C1BE]">
        <div className="flex items-center justify-between px-8 py-5 border-b border-[#E5E6E3] bg-white">
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="gap-2 -ml-2 text-[#5B5F61] hover:text-[#2D3538]"
          >
            <ArrowLeft className="h-4 w-4" />
            Return to Radar
          </Button>
          <div className="flex gap-3">
            <Button variant="outline" size="sm" className="gap-2 border-[#C0C1BE] h-10 px-5 rounded-xl">
              <Share2 className="h-4 w-4" />
              Share Brief
            </Button>
            <Button variant="outline" size="sm" className="gap-2 border-[#C0C1BE] h-10 px-5 rounded-xl">
              <Download className="h-4 w-4" />
              Export
            </Button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto px-12 py-16">
            {/* Header */}
            <div className="mb-16">
              <div className="flex items-center gap-3 mb-6">
                <Badge className="bg-[#D7C9AE]/20 text-[#A68F68] border-none px-3 py-1 text-[11px] font-bold tracking-widest uppercase">
                  Intelligence Dossier
                </Badge>
                <span className="text-sm text-[#9D9F9F] font-medium">
                  {dossier.date.toLocaleDateString('en-US', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric',
                  })}
                </span>
              </div>
              <h1 className="font-serif text-[56px] text-[#2D3538] leading-[1.1] tracking-tight mb-8">
                {dossier.title}
              </h1>
              <div className="p-8 rounded-3xl bg-white border border-[#E5E6E3] shadow-sm">
                <h3 className="text-xs font-bold text-[#5B5F61] uppercase tracking-[0.2em] mb-6">Executive Summary</h3>
                <div className="space-y-4">
                  {dossier.summary.map((point, i) => (
                    <div key={i} className="flex gap-4 items-start">
                      <div className="w-1.5 h-1.5 rounded-full bg-[#D7C9AE] mt-2.5 shrink-0" />
                      <p className="text-[#2D3538] text-[17px] leading-relaxed">
                        {point}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Strategic Intelligence Grid */}
            <div className="grid grid-cols-2 gap-12 mb-16">
              <div className="space-y-6">
                <div className="flex items-center gap-3">
                  <Lightbulb className="w-5 h-5 text-[#D7C9AE]" />
                  <h3 className="font-serif text-2xl text-[#2D3538]">Market Hypotheses</h3>
                </div>
                <div className="space-y-4">
                  {dossier.whyItMatters.impacts.map((hyp, i) => (
                    <div key={i} className="p-5 rounded-2xl bg-white border border-[#E5E6E3] text-[15px] text-[#5B5F61] leading-relaxed">
                      {hyp}
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-6">
                <div className="flex items-center gap-3">
                  <Zap className="w-5 h-5 text-[#D7C9AE]" />
                  <h3 className="font-serif text-2xl text-[#2D3538]">Recommended Experiments</h3>
                </div>
                <div className="space-y-4">
                  {dossier.whyItMatters.opportunities.map((exp, i) => (
                    <div key={i} className="p-5 rounded-2xl bg-[#2D3538] text-white text-[15px] leading-relaxed shadow-lg">
                      {exp}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Market Narrative */}
            <div className="mb-16 p-10 rounded-3xl border border-[#C0C1BE] bg-white relative overflow-hidden">
              <div className="absolute top-0 right-0 p-8 opacity-[0.03]">
                <Quote size={120} />
              </div>
              <h3 className="font-serif text-2xl text-[#2D3538] mb-8 relative">Intelligence Narrative</h3>
              <p className="text-[#2D3538] text-lg leading-relaxed italic mb-8 relative">
                "{dossier.whatChanged}"
              </p>
              <div className="grid grid-cols-3 gap-8 pt-8 border-t border-[#E5E6E3] relative">
                <div>
                  <span className="text-[10px] uppercase tracking-widest text-[#9D9F9F] font-bold block mb-3">Status Quo</span>
                  <p className="text-[15px] text-[#2D3538] font-medium leading-snug">{dossier.marketNarrative.believing}</p>
                </div>
                <div>
                  <span className="text-[10px] uppercase tracking-widest text-[#9D9F9F] font-bold block mb-3">Overhyped</span>
                  <p className="text-[15px] text-[#2D3538] font-medium leading-snug">{dossier.marketNarrative.overhyped}</p>
                </div>
                <div>
                  <span className="text-[10px] uppercase tracking-widest text-[#9D9F9F] font-bold block mb-3">Underrated</span>
                  <p className="text-[15px] text-[#2D3538] font-medium leading-snug">{dossier.marketNarrative.underrated}</p>
                </div>
              </div>
            </div>

            {/* Recommended Move */}
            <div className="mb-16">
              <div className="bg-[#1A1D1E] text-white rounded-[32px] p-12 shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-[#D7C9AE] opacity-10 rounded-full -translate-x-1/2 -translate-y-1/2 blur-3xl" />

                <div className="flex items-center gap-4 mb-10 relative">
                  <div className="w-12 h-12 rounded-2xl bg-[#D7C9AE] flex items-center justify-center">
                    <Target className="h-6 w-6 text-[#1A1D1E]" />
                  </div>
                  <h3 className="font-serif text-3xl">Strategic Recommended Move</h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-12 relative">
                  <div className="space-y-8">
                    <div>
                      <div className="text-[#9D9F9F] text-[10px] uppercase tracking-[0.2em] font-bold mb-3">Operation Objective</div>
                      <div className="text-4xl font-serif">{dossier.recommendedMove.name}</div>
                    </div>
                    <div>
                      <div className="text-[#9D9F9F] text-[10px] uppercase tracking-[0.2em] font-bold mb-3">Tactical Action</div>
                      <div className="text-xl leading-relaxed text-[#D7C9AE]">{dossier.recommendedMove.action}</div>
                    </div>
                  </div>
                  <div className="flex flex-col justify-between">
                    <div className="p-8 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-sm">
                      <div className="text-[#9D9F9F] text-[10px] uppercase tracking-[0.2em] font-bold mb-3">Target Outcome</div>
                      <div className="text-3xl font-serif text-[#D7C9AE]">{dossier.recommendedMove.target}</div>
                    </div>

                    <div className="flex gap-4 mt-8">
                      <Button
                        onClick={() => onConvertToMove?.(dossier)}
                        className="flex-1 h-14 bg-[#D7C9AE] hover:bg-[#C5B79C] text-[#1A1D1E] rounded-2xl font-bold text-[16px]"
                      >
                        Convert to Move
                      </Button>
                      <Button
                        variant="outline"
                        className="flex-1 h-14 border-white/20 hover:bg-white/5 text-white bg-transparent rounded-2xl font-bold text-[16px]"
                      >
                        Attach to Campaign
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
