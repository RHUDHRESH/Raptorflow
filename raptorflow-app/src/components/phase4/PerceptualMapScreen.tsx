'use client';

import React, { useState, useRef, useEffect } from 'react';
import { ChevronRight, Move, RefreshCw, HelpCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Phase4Data,
  PerceptualMapPoint,
  PerceptualMapAxis,
} from '@/lib/foundation';
import { v4 as uuidv4 } from 'uuid';

interface PerceptualMapScreenProps {
  phase4: Phase4Data;
  onUpdate: (updates: Partial<Phase4Data>) => void;
  onContinue: () => void;
  onBack: () => void;
}

const AXIS_PRESETS: {
  x: Partial<PerceptualMapAxis>;
  y: Partial<PerceptualMapAxis>;
  label: string;
}[] = [
  {
    x: { label: 'Fragmented', minLabel: 'Fragmented', maxLabel: 'Unified' },
    y: { label: 'Manual', minLabel: 'Manual', maxLabel: 'Automated' },
    label: 'Integration vs Automation',
  },
  {
    x: { label: 'Generic', minLabel: 'Generic', maxLabel: 'Specialized' },
    y: { label: 'Complex', minLabel: 'Complex', maxLabel: 'Simple' },
    label: 'Focus vs Complexity',
  },
  {
    x: { label: 'Cheap', minLabel: 'Low Cost', maxLabel: 'Premium' },
    y: { label: 'DIY', minLabel: 'Self-Serve', maxLabel: 'Full-Service' },
    label: 'Price vs Service',
  },
];

export function PerceptualMapScreen({
  phase4,
  onUpdate,
  onContinue,
  onBack,
}: PerceptualMapScreenProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const [draggingPoint, setDraggingPoint] = useState<string | null>(null);
  const [showJustificationPrompt, setShowJustificationPrompt] = useState(false);
  const [pendingMove, setPendingMove] = useState<{
    id: string;
    x: number;
    y: number;
  } | null>(null);

  // Get or create default map data
  const perceptualMap = phase4.visuals?.perceptualMap || {
    xAxis: {
      label: 'Generic',
      rationale: '',
      minLabel: 'Generic',
      maxLabel: 'Specialized',
    },
    yAxis: {
      label: 'Complex',
      rationale: '',
      minLabel: 'Complex',
      maxLabel: 'Simple',
    },
    points: [],
  };

  // Generate default points if none exist
  const getDefaultPoints = (): PerceptualMapPoint[] => {
    if (perceptualMap.points.length > 0) return perceptualMap.points;

    const competitors = [
      ...(phase4.competitiveAlternatives?.direct || [])
        .slice(0, 3)
        .map((c) => ({
          id: uuidv4(),
          name: c.name,
          x: Math.random() * 1.6 - 0.8,
          y: Math.random() * 1.6 - 0.8,
          isYou: false,
        })),
      {
        id: 'you',
        name: 'You',
        x: 0.6,
        y: 0.6,
        isYou: true,
      },
    ];

    return competitors.length > 1
      ? competitors
      : [
          { id: uuidv4(), name: 'Status Quo', x: -0.5, y: -0.5, isYou: false },
          { id: uuidv4(), name: 'Competitor A', x: 0.3, y: -0.2, isYou: false },
          { id: uuidv4(), name: 'Competitor B', x: -0.2, y: 0.4, isYou: false },
          { id: 'you', name: 'You', x: 0.6, y: 0.6, isYou: true },
        ];
  };

  const points = getDefaultPoints();

  const handleMouseDown = (pointId: string) => {
    setDraggingPoint(pointId);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!draggingPoint || !mapRef.current) return;

    const rect = mapRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    const y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

    // Clamp to -1 to 1
    const clampedX = Math.max(-0.9, Math.min(0.9, x));
    const clampedY = Math.max(-0.9, Math.min(0.9, y));

    const updated = points.map((p) =>
      p.id === draggingPoint ? { ...p, x: clampedX, y: clampedY } : p
    );

    onUpdate({
      visuals: {
        ...phase4.visuals!,
        perceptualMap: { ...perceptualMap, points: updated },
      },
    });
  };

  const handleMouseUp = () => {
    if (draggingPoint && !points.find((p) => p.id === draggingPoint)?.isYou) {
      setPendingMove({
        id: draggingPoint,
        x: points.find((p) => p.id === draggingPoint)?.x || 0,
        y: points.find((p) => p.id === draggingPoint)?.y || 0,
      });
      setShowJustificationPrompt(true);
    }
    setDraggingPoint(null);
  };

  const handleAxisPreset = (preset: (typeof AXIS_PRESETS)[0]) => {
    onUpdate({
      visuals: {
        ...phase4.visuals!,
        perceptualMap: {
          ...perceptualMap,
          xAxis: { ...perceptualMap.xAxis, ...preset.x },
          yAxis: { ...perceptualMap.yAxis, ...preset.y },
        },
      },
    });
  };

  const handleAxisChange = (
    axis: 'x' | 'y',
    field: 'label' | 'minLabel' | 'maxLabel',
    value: string
  ) => {
    const axisKey = axis === 'x' ? 'xAxis' : 'yAxis';
    onUpdate({
      visuals: {
        ...phase4.visuals!,
        perceptualMap: {
          ...perceptualMap,
          [axisKey]: { ...perceptualMap[axisKey], [field]: value },
        },
      },
    });
  };

  // Convert normalized coords (-1 to 1) to percentage
  const toPercent = (val: number) => ((val + 1) / 2) * 100;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-[#F3F4EE] rounded-2xl p-5 border border-[#E5E6E3]">
        <p className="text-sm text-[#5B5F61]">
          <strong>Perceptual Map:</strong> Shows how customers perceive you vs
          competitors on two key dimensions. Axes should reflect real decision
          criteria.
        </p>
      </div>

      {/* Axis Presets */}
      <div>
        <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] block mb-2">
          Quick axis presets
        </span>
        <div className="flex gap-2">
          {AXIS_PRESETS.map((preset, i) => (
            <button
              key={i}
              onClick={() => handleAxisPreset(preset)}
              className="px-3 py-2 bg-white border border-[#E5E6E3] rounded-lg text-xs text-[#5B5F61] hover:border-[#2D3538] hover:text-[#2D3538] transition-colors"
            >
              {preset.label}
            </button>
          ))}
        </div>
      </div>

      {/* Axis Editors */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white border border-[#E5E6E3] rounded-xl p-4">
          <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] block mb-2">
            X-Axis (horizontal)
          </span>
          <div className="flex gap-2">
            <input
              type="text"
              value={perceptualMap.xAxis.minLabel || ''}
              onChange={(e) =>
                handleAxisChange('x', 'minLabel', e.target.value)
              }
              placeholder="Left label"
              className="flex-1 px-3 py-2 bg-[#F3F4EE] rounded-lg text-sm border-none focus:outline-none focus:ring-1 focus:ring-[#2D3538]"
            />
            <span className="self-center text-[#9D9F9F]">→</span>
            <input
              type="text"
              value={perceptualMap.xAxis.maxLabel || ''}
              onChange={(e) =>
                handleAxisChange('x', 'maxLabel', e.target.value)
              }
              placeholder="Right label"
              className="flex-1 px-3 py-2 bg-[#F3F4EE] rounded-lg text-sm border-none focus:outline-none focus:ring-1 focus:ring-[#2D3538]"
            />
          </div>
        </div>
        <div className="bg-white border border-[#E5E6E3] rounded-xl p-4">
          <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] block mb-2">
            Y-Axis (vertical)
          </span>
          <div className="flex gap-2">
            <input
              type="text"
              value={perceptualMap.yAxis.minLabel || ''}
              onChange={(e) =>
                handleAxisChange('y', 'minLabel', e.target.value)
              }
              placeholder="Bottom label"
              className="flex-1 px-3 py-2 bg-[#F3F4EE] rounded-lg text-sm border-none focus:outline-none focus:ring-1 focus:ring-[#2D3538]"
            />
            <span className="self-center text-[#9D9F9F]">→</span>
            <input
              type="text"
              value={perceptualMap.yAxis.maxLabel || ''}
              onChange={(e) =>
                handleAxisChange('y', 'maxLabel', e.target.value)
              }
              placeholder="Top label"
              className="flex-1 px-3 py-2 bg-[#F3F4EE] rounded-lg text-sm border-none focus:outline-none focus:ring-1 focus:ring-[#2D3538]"
            />
          </div>
        </div>
      </div>

      {/* The Map */}
      <div className="relative">
        {/* Axis Labels */}
        <div className="absolute -left-2 top-1/2 -translate-y-1/2 -rotate-90 text-[10px] font-mono uppercase tracking-wider text-[#9D9F9F] whitespace-nowrap">
          {perceptualMap.yAxis.minLabel} → {perceptualMap.yAxis.maxLabel}
        </div>
        <div className="absolute left-1/2 -bottom-6 -translate-x-1/2 text-[10px] font-mono uppercase tracking-wider text-[#9D9F9F] whitespace-nowrap">
          {perceptualMap.xAxis.minLabel} → {perceptualMap.xAxis.maxLabel}
        </div>

        {/* Map Container */}
        <div
          ref={mapRef}
          className="ml-8 aspect-square bg-white border border-[#E5E6E3] rounded-2xl relative cursor-crosshair"
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        >
          {/* Grid Lines */}
          <div className="absolute inset-0 grid grid-cols-2 grid-rows-2">
            <div className="border-r border-b border-dashed border-[#E5E6E3]" />
            <div className="border-b border-dashed border-[#E5E6E3]" />
            <div className="border-r border-dashed border-[#E5E6E3]" />
            <div />
          </div>

          {/* Points */}
          {points.map((point) => (
            <div
              key={point.id}
              onMouseDown={() => handleMouseDown(point.id)}
              className={`absolute transform -translate-x-1/2 -translate-y-1/2 cursor-move transition-all ${
                draggingPoint === point.id ? 'scale-110 z-10' : ''
              }`}
              style={{
                left: `${toPercent(point.x)}%`,
                top: `${toPercent(-point.y)}%`, // Invert Y for visual
              }}
            >
              <div
                className={`rounded-full flex items-center justify-center ${
                  point.isYou
                    ? 'w-8 h-8 bg-[#2D3538] text-white shadow-lg'
                    : 'w-6 h-6 bg-[#9D9F9F] text-white'
                }`}
              >
                {point.isYou ? (
                  <span className="text-xs font-bold">Y</span>
                ) : (
                  <span className="text-[10px]">{point.name.charAt(0)}</span>
                )}
              </div>
              <div
                className={`absolute left-1/2 -translate-x-1/2 mt-1 text-[10px] whitespace-nowrap ${
                  point.isYou ? 'text-[#2D3538] font-medium' : 'text-[#5B5F61]'
                }`}
              >
                {point.name}
              </div>
            </div>
          ))}

          {/* Drag Hint */}
          <div className="absolute bottom-4 right-4 flex items-center gap-1 text-[10px] text-[#9D9F9F]">
            <Move className="w-3 h-3" /> Drag to reposition
          </div>
        </div>
      </div>

      {/* Justification Prompt */}
      {showJustificationPrompt && pendingMove && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
          <div className="flex items-start gap-3">
            <HelpCircle className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm text-amber-800 font-medium">
                What evidence supports this position?
              </p>
              <input
                type="text"
                placeholder="e.g., Based on G2 reviews showing..."
                className="w-full mt-2 px-3 py-2 bg-white border border-amber-200 rounded-lg text-sm focus:outline-none focus:border-amber-400"
              />
              <div className="flex justify-end gap-2 mt-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowJustificationPrompt(false)}
                  className="text-amber-700"
                >
                  Skip
                </Button>
                <Button
                  size="sm"
                  onClick={() => setShowJustificationPrompt(false)}
                  className="bg-amber-600 hover:bg-amber-700 text-white"
                >
                  Save
                </Button>
              </div>
            </div>
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
