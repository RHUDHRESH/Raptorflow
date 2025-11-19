'use client';

import React, { useState, useEffect } from 'react';
import { Plus, X, Trash2 } from 'lucide-react';
import { StrategicInput } from '../StrategicInput';
import { useGroundwork } from '../GroundworkProvider';
import { AudienceICPData, ICPData } from '@/lib/groundwork/types';
import { cn } from '@/lib/utils';

export function AudienceICPSection() {
  const { state, updateSectionData } = useGroundwork();
  const sectionData = state.sections['audience-icp'].data as AudienceICPData | null;

  const [icps, setIcps] = useState<ICPData[]>(
    sectionData?.icps || [
      {
        id: `icp-${Date.now()}`,
        name: '',
        role: '',
        industry: '',
        painPoints: [''],
        buyingBehavior: undefined,
      },
    ]
  );

  useEffect(() => {
    const data: AudienceICPData = { icps };
    updateSectionData('audience-icp', data);
  }, [icps, updateSectionData]);

  const addICP = () => {
    setIcps([
      ...icps,
      {
        id: `icp-${Date.now()}`,
        name: '',
        role: '',
        industry: '',
        painPoints: [''],
        buyingBehavior: undefined,
      },
    ]);
  };

  const removeICP = (id: string) => {
    if (icps.length > 1) {
      setIcps(icps.filter((icp) => icp.id !== id));
    }
  };

  const updateICP = (id: string, updates: Partial<ICPData>) => {
    setIcps(icps.map((icp) => (icp.id === id ? { ...icp, ...updates } : icp)));
  };

  const addPainPoint = (icpId: string) => {
    setIcps(
      icps.map((icp) =>
        icp.id === icpId
          ? { ...icp, painPoints: [...icp.painPoints, ''] }
          : icp
      )
    );
  };

  const removePainPoint = (icpId: string, index: number) => {
    setIcps(
      icps.map((icp) =>
        icp.id === icpId
          ? { ...icp, painPoints: icp.painPoints.filter((_, i) => i !== index) }
          : icp
      )
    );
  };

  const updatePainPoint = (icpId: string, index: number, value: string) => {
    setIcps(
      icps.map((icp) =>
        icp.id === icpId
          ? {
              ...icp,
              painPoints: icp.painPoints.map((pp, i) => (i === index ? value : pp)),
            }
          : icp
      )
    );
  };

  return (
    <div className="space-y-6">
      {icps.map((icp, icpIndex) => (
        <div
          key={icp.id}
          className={cn(
            'p-6 rounded-lg border border-rf-cloud bg-rf-bg',
            icpIndex > 0 && 'mt-8'
          )}
        >
          {icpIndex > 0 && (
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-sm font-medium text-rf-subtle uppercase tracking-wide">
                ICP #{icpIndex + 1}
              </h4>
              <button
                type="button"
                onClick={() => removeICP(icp.id)}
                className="p-1 text-rf-subtle hover:text-rf-error transition-colors"
                aria-label="Remove ICP"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-rf-ink mb-2">
                ICP Name or Nickname
              </label>
              <input
                type="text"
                value={icp.name}
                onChange={(e) => updateICP(icp.id, { name: e.target.value })}
                placeholder="e.g., Startup Steve, Marketing Mary"
                className="w-full px-4 py-3 rounded-lg border border-rf-cloud bg-rf-bg text-rf-ink placeholder:text-rf-muted focus:outline-none focus:border-rf-primary focus:ring-1 focus:ring-rf-primary/20 text-sm"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-rf-ink mb-2">
                  Role or Segment
                </label>
                <input
                  type="text"
                  value={icp.role || ''}
                  onChange={(e) => updateICP(icp.id, { role: e.target.value })}
                  placeholder="e.g., VP Marketing, Small business owner"
                  className="w-full px-4 py-3 rounded-lg border border-rf-cloud bg-rf-bg text-rf-ink placeholder:text-rf-muted focus:outline-none focus:border-rf-primary focus:ring-1 focus:ring-rf-primary/20 text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-rf-ink mb-2">
                  Industry
                </label>
                <input
                  type="text"
                  value={icp.industry || ''}
                  onChange={(e) => updateICP(icp.id, { industry: e.target.value })}
                  placeholder="e.g., B2B SaaS, E-commerce"
                  className="w-full px-4 py-3 rounded-lg border border-rf-cloud bg-rf-bg text-rf-ink placeholder:text-rf-muted focus:outline-none focus:border-rf-primary focus:ring-1 focus:ring-rf-primary/20 text-sm"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-rf-ink mb-2">
                Pain Points
              </label>
              <div className="space-y-2">
                {icp.painPoints.map((painPoint, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <input
                      type="text"
                      value={painPoint}
                      onChange={(e) => updatePainPoint(icp.id, index, e.target.value)}
                      placeholder="What problem do they face?"
                      className="flex-1 px-4 py-2 rounded-lg border border-rf-cloud bg-rf-bg text-rf-ink placeholder:text-rf-muted focus:outline-none focus:border-rf-primary focus:ring-1 focus:ring-rf-primary/20 text-sm"
                    />
                    {icp.painPoints.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removePainPoint(icp.id, index)}
                        className="p-2 text-rf-subtle hover:text-rf-error transition-colors"
                        aria-label="Remove pain point"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                ))}
                <button
                  type="button"
                  onClick={() => addPainPoint(icp.id)}
                  className="flex items-center gap-2 text-sm text-rf-subtle hover:text-rf-ink transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  Add pain point
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-rf-ink mb-2">
                Buying Behavior
              </label>
              <select
                value={icp.buyingBehavior || ''}
                onChange={(e) =>
                  updateICP(icp.id, {
                    buyingBehavior: e.target.value as ICPData['buyingBehavior'],
                  })
                }
                className="w-full px-4 py-3 rounded-lg border border-rf-cloud bg-rf-bg text-rf-ink focus:outline-none focus:border-rf-primary focus:ring-1 focus:ring-rf-primary/20 text-sm"
              >
                <option value="">Select buying behavior...</option>
                <option value="fast">Fast decision (impulse buy)</option>
                <option value="slow">Slow decision (thorough research)</option>
                <option value="comparison">Comparison shopping</option>
                <option value="impulse">Impulse purchase</option>
              </select>
            </div>
          </div>
        </div>
      ))}

      <button
        type="button"
        onClick={addICP}
        className="flex items-center gap-2 px-4 py-3 border border-rf-cloud rounded-lg text-sm font-medium text-rf-ink hover:bg-rf-cloud transition-colors"
      >
        <Plus className="w-4 h-4" />
        Add another ICP
      </button>
    </div>
  );
}

