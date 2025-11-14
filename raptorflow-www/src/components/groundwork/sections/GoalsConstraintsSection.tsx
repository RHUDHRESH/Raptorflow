'use client';

import React, { useState, useEffect } from 'react';
import { StrategicInput } from '../StrategicInput';
import { useGroundwork } from '../GroundworkProvider';
import { GoalsConstraintsData } from '@/lib/groundwork/types';

const GOAL_OPTIONS = [
  { value: 'reach', label: 'Reach & Awareness' },
  { value: 'trust', label: 'Build Trust & Credibility' },
  { value: 'sales', label: 'Drive Sales & Conversions' },
  { value: 'awareness', label: 'Brand Awareness' },
  { value: 'custom', label: 'Custom Goal' },
] as const;

const PAIN_POINT_OPTIONS = [
  'Not knowing what to post',
  'Lack of time',
  'No clear strategy',
  'Inconsistent messaging',
  'Low engagement',
  'Difficulty measuring ROI',
  'Content creation is overwhelming',
  'Don\'t know which channels to focus on',
] as const;

export function GoalsConstraintsSection() {
  const { state, updateSectionData } = useGroundwork();
  const sectionData = state.sections['goals-constraints'].data as GoalsConstraintsData | null;

  const [primaryGoal, setPrimaryGoal] = useState<GoalsConstraintsData['primaryGoal']>(
    sectionData?.primaryGoal || 'reach'
  );
  const [customGoal, setCustomGoal] = useState(sectionData?.customGoal || '');
  const [successMetric, setSuccessMetric] = useState(sectionData?.successMetric || '');
  const [targetValue, setTargetValue] = useState(sectionData?.targetValue || 0);
  const [timeframe, setTimeframe] = useState<GoalsConstraintsData['timeframe']>(
    sectionData?.timeframe || 30
  );
  const [showUpFrequency, setShowUpFrequency] = useState<
    GoalsConstraintsData['showUpFrequency']
  >(sectionData?.showUpFrequency || 'weekly');
  const [marketingPainPoints, setMarketingPainPoints] = useState<string[]>(
    sectionData?.marketingPainPoints || []
  );
  const [teamSize, setTeamSize] = useState<GoalsConstraintsData['teamSize']>(
    sectionData?.teamSize || 'solo'
  );

  useEffect(() => {
    const data: GoalsConstraintsData = {
      primaryGoal,
      customGoal: primaryGoal === 'custom' ? customGoal : undefined,
      successMetric,
      targetValue,
      timeframe,
      showUpFrequency,
      marketingPainPoints,
      teamSize,
    };
    updateSectionData('goals-constraints', data);
  }, [
    primaryGoal,
    customGoal,
    successMetric,
    targetValue,
    timeframe,
    showUpFrequency,
    marketingPainPoints,
    teamSize,
    updateSectionData,
  ]);

  const togglePainPoint = (point: string) => {
    setMarketingPainPoints((prev) =>
      prev.includes(point) ? prev.filter((p) => p !== point) : [...prev, point]
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-rf-ink mb-2">
          Primary Marketing Goal
        </label>
        <select
          value={primaryGoal}
          onChange={(e) =>
            setPrimaryGoal(e.target.value as GoalsConstraintsData['primaryGoal'])
          }
          className="w-full px-4 py-3 rounded-lg border border-rf-cloud bg-rf-bg text-rf-ink focus:outline-none focus:border-rf-primary focus:ring-1 focus:ring-rf-primary/20 text-sm"
        >
          {GOAL_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {primaryGoal === 'custom' && (
          <div className="mt-3">
            <StrategicInput
              value={customGoal}
              onChange={setCustomGoal}
              placeholder="Describe your custom goal..."
              minHeight={60}
            />
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-rf-ink mb-2">
            Success Metric
          </label>
          <input
            type="text"
            value={successMetric}
            onChange={(e) => setSuccessMetric(e.target.value)}
            placeholder="e.g., New leads, Website visits, Sign-ups"
            className="w-full px-4 py-3 rounded-lg border border-rf-cloud bg-rf-bg text-rf-ink placeholder:text-rf-muted focus:outline-none focus:border-rf-primary focus:ring-1 focus:ring-rf-primary/20 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-rf-ink mb-2">
            Target Value
          </label>
          <input
            type="number"
            value={targetValue}
            onChange={(e) => setTargetValue(Number(e.target.value))}
            placeholder="e.g., 100, 1000, 50"
            className="w-full px-4 py-3 rounded-lg border border-rf-cloud bg-rf-bg text-rf-ink placeholder:text-rf-muted focus:outline-none focus:border-rf-primary focus:ring-1 focus:ring-rf-primary/20 text-sm"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-rf-ink mb-2">
            Timeframe
          </label>
          <select
            value={timeframe}
            onChange={(e) => setTimeframe(Number(e.target.value) as GoalsConstraintsData['timeframe'])}
            className="w-full px-4 py-3 rounded-lg border border-rf-cloud bg-rf-bg text-rf-ink focus:outline-none focus:border-rf-primary focus:ring-1 focus:ring-rf-primary/20 text-sm"
          >
            <option value={7}>7 days</option>
            <option value={14}>14 days</option>
            <option value={30}>30 days</option>
            <option value={60}>60 days</option>
            <option value={90}>90 days</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-rf-ink mb-2">
            How often can you show up online?
          </label>
          <select
            value={showUpFrequency}
            onChange={(e) =>
              setShowUpFrequency(e.target.value as GoalsConstraintsData['showUpFrequency'])
            }
            className="w-full px-4 py-3 rounded-lg border border-rf-cloud bg-rf-bg text-rf-ink focus:outline-none focus:border-rf-primary focus:ring-1 focus:ring-rf-primary/20 text-sm"
          >
            <option value="daily">Daily</option>
            <option value="3x-week">3x per week</option>
            <option value="weekly">Weekly</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-rf-ink mb-3">
          What do you hate doing in marketing?
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {PAIN_POINT_OPTIONS.map((point) => (
            <label
              key={point}
              className="flex items-center gap-2 p-3 rounded-lg border border-rf-cloud hover:bg-rf-cloud cursor-pointer transition-colors"
            >
              <input
                type="checkbox"
                checked={marketingPainPoints.includes(point)}
                onChange={() => togglePainPoint(point)}
                className="w-4 h-4 text-rf-primary border-rf-cloud rounded focus:ring-rf-primary/20"
              />
              <span className="text-sm text-rf-ink">{point}</span>
            </label>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-rf-ink mb-2">
          Team Size
        </label>
        <select
          value={teamSize}
          onChange={(e) => setTeamSize(e.target.value as GoalsConstraintsData['teamSize'])}
          className="w-full px-4 py-3 rounded-lg border border-rf-cloud bg-rf-bg text-rf-ink focus:outline-none focus:border-rf-primary focus:ring-1 focus:ring-rf-primary/20 text-sm"
        >
          <option value="solo">Just me (solo)</option>
          <option value="small-team">Small team (2-5 people)</option>
          <option value="agency">Agency or larger team</option>
        </select>
      </div>
    </div>
  );
}

