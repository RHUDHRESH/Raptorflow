'use client';

import React from 'react';
import { QAReport, Signal7Soundbite } from '@/lib/foundation';
import {
  Eye,
  AlertTriangle,
  Check,
  RefreshCw,
  Sparkles,
  X,
} from 'lucide-react';

interface Props {
  qaReport: QAReport | undefined;
  soundbites: Signal7Soundbite[];
  onRequestRewrite: (soundbiteId: string) => void;
  onAcceptFix: (type: 'fluffy' | 'differentiation') => void;
}

export function ClarityDiffTests({
  qaReport,
  soundbites,
  onRequestRewrite,
  onAcceptFix,
}: Props) {
  if (!qaReport) {
    return (
      <div className="flex items-center justify-center h-64 bg-[#FAFAF8] rounded-2xl">
        <p className="text-[#9D9F9F]">Running QA checks...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-[#FAFAF8] border border-[#E5E6E3] rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-2">
          <Eye className="w-5 h-5 text-[#2D3538]" />
          <h3 className="font-medium text-[#2D3538]">
            Clarity & Differentiation Tests
          </h3>
        </div>
        <p className="text-sm text-[#5B5F61]">
          Auto QA to avoid shipping mush. Fix issues before locking your
          messaging.
        </p>
      </div>

      {/* 7-Second Test */}
      <div
        className={`rounded-2xl p-6 ${
          qaReport.sevenSecondTestPass
            ? 'bg-green-50 border border-green-200'
            : 'bg-amber-50 border border-amber-200'
        }`}
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center ${
                qaReport.sevenSecondTestPass ? 'bg-green-100' : 'bg-amber-100'
              }`}
            >
              {qaReport.sevenSecondTestPass ? (
                <Check className="w-5 h-5 text-green-600" />
              ) : (
                <AlertTriangle className="w-5 h-5 text-amber-600" />
              )}
            </div>
            <div>
              <span className="font-medium text-[#2D3538]">7-Second Test</span>
              <p
                className={`text-sm ${qaReport.sevenSecondTestPass ? 'text-green-700' : 'text-amber-700'}`}
              >
                {qaReport.sevenSecondTestPass
                  ? 'Pass — Message is clear at a glance'
                  : 'Needs work — Too complex for quick scanning'}
              </p>
            </div>
          </div>
          {qaReport.sevenSecondTestPass && (
            <span className="px-3 py-1 bg-green-100 text-green-700 text-xs rounded-full">
              ✓ Passed
            </span>
          )}
        </div>

        {/* Quick Preview */}
        <div className="bg-white/50 rounded-xl p-4 border border-white">
          <span className="text-[10px] font-mono uppercase text-[#9D9F9F] block mb-2">
            First Impression Preview
          </span>
          <div className="text-center py-4">
            <p className="font-serif text-xl text-[#2D3538]">
              {soundbites
                .find((s) => s.type === 'outcome')
                ?.text.split('.')[0] || 'Your headline here'}
            </p>
          </div>
        </div>
      </div>

      {/* Differentiation Score */}
      <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Sparkles className="w-5 h-5 text-[#2D3538]" />
            <span className="font-medium text-[#2D3538]">
              Differentiation Check
            </span>
          </div>
          <div
            className={`text-2xl font-medium ${
              qaReport.differentiationScore >= 70
                ? 'text-green-600'
                : qaReport.differentiationScore >= 50
                  ? 'text-amber-600'
                  : 'text-red-600'
            }`}
          >
            {qaReport.differentiationScore}%
          </div>
        </div>

        <div className="h-3 bg-[#F3F4EE] rounded-full overflow-hidden mb-4">
          <div
            className={`h-full rounded-full transition-all ${
              qaReport.differentiationScore >= 70
                ? 'bg-green-500'
                : qaReport.differentiationScore >= 50
                  ? 'bg-amber-500'
                  : 'bg-red-500'
            }`}
            style={{ width: `${qaReport.differentiationScore}%` }}
          />
        </div>

        <p className="text-sm text-[#5B5F61]">
          {qaReport.differentiationScore >= 70
            ? 'Good — Your messaging is distinct from competitors'
            : qaReport.differentiationScore >= 50
              ? 'Fair — Some lines could be more unique'
              : 'Weak — Messaging sounds too generic'}
        </p>

        {qaReport.competitorSimilarity.length > 0 && (
          <div className="mt-4 pt-4 border-t border-[#E5E6E3]">
            <span className="text-[10px] font-mono uppercase text-[#9D9F9F] block mb-2">
              Similarity Warnings
            </span>
            {qaReport.competitorSimilarity.map((sim, i) => (
              <div
                key={i}
                className="flex items-center gap-2 text-sm text-amber-700 bg-amber-50 px-3 py-2 rounded-lg mb-2"
              >
                <AlertTriangle className="w-4 h-4" />
                <span>
                  Soundbite similar to {sim.competitor} ({sim.similarity}%)
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Fluff Detector */}
      <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-500" />
            <span className="font-medium text-[#2D3538]">Fluff Detector</span>
          </div>
          <span
            className={`text-sm ${qaReport.fluffyWords.length === 0 ? 'text-green-600' : 'text-amber-600'}`}
          >
            {qaReport.fluffyWords.length === 0
              ? 'Clean!'
              : `${qaReport.fluffyWords.length} issues`}
          </span>
        </div>

        {qaReport.fluffyWords.length > 0 ? (
          <div className="space-y-2">
            {qaReport.fluffyWords.map((fluff, i) => (
              <div
                key={i}
                className="flex items-center justify-between bg-amber-50 border border-amber-200 rounded-lg p-3"
              >
                <div className="flex items-center gap-2">
                  <X className="w-4 h-4 text-amber-600" />
                  <span className="text-sm">
                    <strong className="text-amber-700">"{fluff.word}"</strong>
                    <span className="text-[#5B5F61]"> in {fluff.location}</span>
                  </span>
                </div>
                <button
                  onClick={() => onAcceptFix('fluffy')}
                  className="text-xs text-amber-700 hover:underline"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex items-center gap-2 bg-green-50 border border-green-200 rounded-lg p-4">
            <Check className="w-5 h-5 text-green-600" />
            <span className="text-sm text-green-700">
              No fluffy words detected!
            </span>
          </div>
        )}
      </div>

      {/* Claims at Risk */}
      {qaReport.claimsAtRisk.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-4">
            <AlertTriangle className="w-5 h-5 text-red-500" />
            <span className="font-medium text-red-700">Claims at Risk</span>
          </div>
          <ul className="space-y-2">
            {qaReport.claimsAtRisk.map((claim, i) => (
              <li key={i} className="flex items-center justify-between">
                <span className="text-sm text-red-700">{claim}</span>
                <button
                  onClick={() => onRequestRewrite(claim)}
                  className="flex items-center gap-1 text-xs text-red-600 hover:underline"
                >
                  <RefreshCw className="w-3 h-3" />
                  Rewrite
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
