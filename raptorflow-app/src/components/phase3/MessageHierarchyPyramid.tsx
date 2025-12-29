'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Playfair_Display } from 'next/font/google';
import { Plus, Trash2, Triangle } from 'lucide-react';
import { cn } from '@/lib/utils';

const playfair = Playfair_Display({ subsets: ['latin'] });

interface MessageHierarchyPyramidProps {
  essence: string;
  coreMessage: string;
  pillars: Array<{ title: string; description: string; proofPoints: string[] }>;
  onChange: (field: string, value: any) => void;
}

export function MessageHierarchyPyramid({
  essence,
  coreMessage,
  pillars,
  onChange,
}: MessageHierarchyPyramidProps) {
  const addPillar = () => {
    if (pillars.length < 5) {
      onChange('pillars', [
        ...pillars,
        { title: '', description: '', proofPoints: [] },
      ]);
    }
  };

  const removePillar = (index: number) => {
    const newPillars = [...pillars];
    newPillars.splice(index, 1);
    onChange('pillars', newPillars);
  };

  const updatePillar = (index: number, field: string, value: string) => {
    const newPillars = [...pillars];
    newPillars[index] = { ...newPillars[index], [field]: value };
    onChange('pillars', newPillars);
  };

  return (
    <div className="space-y-12 py-8">
      <div className="flex flex-col items-center">
        {/* Visual Pyramid Visualization */}
        <div className="relative w-full max-w-2xl aspect-[4/3] flex flex-col items-center justify-between pointer-events-none mb-12">
          <div className="absolute inset-0 flex items-center justify-center opacity-[0.03]">
            <Triangle
              className="w-full h-full fill-[#2D3538]"
              strokeWidth={0.5}
            />
          </div>

          {/* Level 1: Essence */}
          <div className="w-[30%] h-24 border-b border-[#C0C1BE] flex flex-col items-center justify-center text-center px-4 relative z-10">
            <span className="text-[10px] font-mono uppercase tracking-[0.2em] opacity-40 mb-1">
              Level 01
            </span>
            <span className="font-serif italic text-lg opacity-80">
              Essence
            </span>
          </div>

          {/* Level 2: Core Message */}
          <div className="w-[60%] h-24 border-b border-[#C0C1BE] flex flex-col items-center justify-center text-center px-8 relative z-10">
            <span className="text-[10px] font-mono uppercase tracking-[0.2em] opacity-40 mb-1">
              Level 02
            </span>
            <span className="font-serif italic text-xl opacity-80">
              Core Message
            </span>
          </div>

          {/* Level 3: Pillars */}
          <div className="w-full h-24 flex items-center justify-center gap-4 text-center px-12 relative z-10">
            <div className="flex flex-col items-center">
              <span className="text-[10px] font-mono uppercase tracking-[0.2em] opacity-40 mb-1">
                Level 03
              </span>
              <span className="font-serif italic text-lg opacity-80">
                Supporting Pillars
              </span>
            </div>
          </div>
        </div>

        {/* Form Controls */}
        <div className="w-full space-y-12">
          {/* Essence & Core Message Inputs */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
            <div className="space-y-4">
              <label className="text-xs font-semibold uppercase tracking-widest text-[#2D3538] opacity-60">
                01 / Brand Essence (Why do you exist?)
              </label>
              <input
                type="text"
                value={essence}
                onChange={(e) => onChange('essence', e.target.value)}
                placeholder="e.g. 'Unifying the fragmented marketing stack'"
                className="w-full p-4 border-b border-[#C0C1BE] bg-transparent focus:border-[#2D3538] outline-none transition-all font-serif text-2xl placeholder:opacity-20"
              />
            </div>
            <div className="space-y-4">
              <label className="text-xs font-semibold uppercase tracking-widest text-[#2D3538] opacity-60">
                02 / Core Message (The primary takeaway)
              </label>
              <input
                type="text"
                value={coreMessage}
                onChange={(e) => onChange('coreMessage', e.target.value)}
                placeholder="e.g. 'Build systems, not just campaigns.'"
                className="w-full p-4 border-b border-[#C0C1BE] bg-transparent focus:border-[#2D3538] outline-none transition-all font-serif text-2xl placeholder:opacity-20"
              />
            </div>
          </div>

          {/* Pillars Section */}
          <div className="space-y-8">
            <div className="flex justify-between items-end border-b border-[#C0C1BE] pb-4">
              <label className="text-xs font-semibold uppercase tracking-widest text-[#2D3538] opacity-60">
                03 / Messaging Pillars ({pillars.length}/5)
              </label>
              <button
                onClick={addPillar}
                disabled={pillars.length >= 5}
                className="text-[10px] font-mono uppercase tracking-widest flex items-center gap-2 hover:opacity-60 disabled:opacity-20 transition-all"
              >
                <Plus className="w-3 h-3" /> Add Pillar
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <AnimatePresence>
                {pillars.map((pillar, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="p-6 border border-[#C0C1BE] rounded-xl bg-white relative group"
                  >
                    <button
                      onClick={() => removePillar(idx)}
                      className="absolute top-4 right-4 opacity-0 group-hover:opacity-20 hover:!opacity-100 transition-all text-[#2D3538]"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                    <div className="space-y-4">
                      <input
                        type="text"
                        value={pillar.title}
                        onChange={(e) =>
                          updatePillar(idx, 'title', e.target.value)
                        }
                        placeholder="Pillar Title"
                        className="w-full font-semibold text-sm outline-none border-b border-transparent focus:border-[#C0C1BE] pb-1 transition-all"
                      />
                      <textarea
                        value={pillar.description}
                        onChange={(e) =>
                          updatePillar(idx, 'description', e.target.value)
                        }
                        placeholder="What does this pillar promise?"
                        className="w-full text-xs text-[#5B5F61] outline-none bg-transparent resize-none h-20 leading-relaxed"
                      />
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
