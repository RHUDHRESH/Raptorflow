"use client";

import { useState, useEffect } from "react";
import { Edit3, Save, Download, Upload, CheckCircle, AlertCircle, RefreshCw, Zap, TrendingUp, History } from "lucide-react";
import { useBCMStore, BusinessContext } from "@/stores/bcmStore";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";

export function BCMEditor() {
  const { bcm, setBCM, updateBCM, validateBCM, exportBCM, importBCM, syncWithEvolution, refineBCM, isLoading, error } = useBCMStore();
  const [editingSection, setEditingSection] = useState<string | null>(null);
  const [tempData, setTempData] = useState<Partial<BusinessContext>>({});
  const [validation, setValidation] = useState<{ isValid: boolean; errors: string[] }>({ isValid: true, errors: [] });

  useEffect(() => {
    if (bcm) {
      const validation = validateBCM(bcm);
      setValidation(validation);
    }
  }, [bcm, validateBCM]);

  const handleRefine = async () => {
    if (bcm?.foundation.company) {
      // Use company name as a base for UCID or get it from meta if stored
      await refineBCM('RF-PROJECTED');
    }
  };

  const handleSectionEdit = (section: string) => {
    setEditingSection(section);
    if (bcm) {
      setTempData(bcm);
    }
  };

  const handleSave = () => {
    if (editingSection && tempData) {
      updateBCM(tempData);
      setEditingSection(null);
      setTempData({});
    }
  };

  const handleCancel = () => {
    setEditingSection(null);
    setTempData({});
  };

  const handleExport = () => {
    const jsonString = exportBCM();
    if (jsonString) {
      const blob = new Blob([jsonString], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'business-context.json';
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const jsonString = e.target?.result as string;
        const result = importBCM(jsonString);
        if (!result.success) {
          alert(result.error);
        }
      };
      reader.readAsText(file);
    }
  };

  if (!bcm) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <BlueprintCard className="p-8 text-center">
          <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-[var(--surface)] border border-[var(--border)] flex items-center justify-center">
            <Edit3 size={24} className="text-[var(--muted)]" />
          </div>
          <h2 className="font-serif text-2xl text-[var(--ink)] mb-4">No Business Context</h2>
          <p className="text-[var(--muted)] mb-6">
            Complete onboarding to generate your Business Context Model, or import an existing one.
          </p>
          <div className="flex items-center justify-center gap-4">
            <SecondaryButton onClick={handleImport} className="flex items-center gap-2">
              <Upload size={14} />
              Import BCM
            </SecondaryButton>
          </div>
        </BlueprintCard>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="font-serif text-3xl text-[var(--ink)] mb-2">Business Context Model</h1>
          <div className="flex items-center gap-4">
            <BlueprintBadge variant={validation.isValid ? 'success' : 'warning'}>
              {validation.isValid ? <CheckCircle size={10} className="mr-1" /> : <AlertCircle size={10} className="mr-1" />}
              {validation.isValid ? 'Valid' : 'Issues Found'}
            </BlueprintBadge>
            <span className="text-sm text-[var(--muted)]">
              Version {bcm.meta.version} • Last updated {new Date(bcm.meta.updated_at).toLocaleDateString()}
            </span>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <SecondaryButton onClick={handleExport} className="flex items-center gap-2">
            <Download size={14} />
            Export
          </SecondaryButton>
          <label className="cursor-pointer">
            <SecondaryButton className="flex items-center gap-2" asChild>
              <span>
                <Upload size={14} />
                Import
              </span>
            </SecondaryButton>
            <input type="file" accept=".json" onChange={handleImport} className="hidden" />
          </label>
          <BlueprintButton onClick={() => handleSectionEdit('all')} className="flex items-center gap-2">
            <RefreshCw size={14} />
            Regenerate
          </BlueprintButton>
        </div>
      </div>

      {/* Validation Errors */}
      {!validation.isValid && (
        <BlueprintCard className="p-4 border-[var(--warning)] bg-[var(--warning)]/5">
          <div className="flex items-start gap-3">
            <AlertCircle size={16} className="text-[var(--warning)] mt-0.5" />
            <div>
              <h3 className="font-medium text-[var(--ink)] mb-2">Validation Issues</h3>
              <ul className="space-y-1">
                {validation.errors.map((error, index) => (
                  <li key={index} className="text-sm text-[var(--muted)]">• {error}</li>
                ))}
              </ul>
            </div>
          </div>
        </BlueprintCard>
      )}

      {/* Evolutionary Intelligence Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <BlueprintCard showCorners padding="md" className="border-[var(--accent)]/30">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xs font-technical text-[var(--muted)] uppercase tracking-wider flex items-center gap-2">
              <Zap size={12} className="text-[var(--accent)]" />
              Evolution Index
            </h3>
          </div>
          <div className="text-4xl font-serif text-[var(--ink)] mb-1">
            {bcm.evolution?.index || '1.0'}<span className="text-lg text-[var(--muted)]">/10</span>
          </div>
          <p className="text-xs text-[var(--muted)]">Strategic maturity score based on ledger interactions.</p>
        </BlueprintCard>

        <BlueprintCard showCorners padding="md">
          <h3 className="text-xs font-technical text-[var(--muted)] uppercase tracking-wider mb-4 flex items-center gap-2">
            <TrendingUp size={12} />
            Evolved Insights
          </h3>
          <div className="space-y-2">
            {bcm.evolution?.insights && bcm.evolution.insights.length > 0 ? (
              bcm.evolution.insights.map((insight, i) => (
                <div key={i} className="text-sm text-[var(--ink)] flex items-start gap-2">
                  <span className="text-[var(--accent)] mt-1">•</span>
                  {insight}
                </div>
              ))
            ) : (
              <p className="text-sm text-[var(--muted)] italic">No evolved insights yet. Run refinement to analyze history.</p>
            )}
          </div>
        </BlueprintCard>

        <BlueprintCard showCorners padding="md">
          <h3 className="text-xs font-technical text-[var(--muted)] uppercase tracking-wider mb-4 flex items-center gap-2">
            <History size={12} />
            Strategic History
          </h3>
          <div className="text-2xl font-serif text-[var(--ink)] mb-1">
            {bcm.history?.total_events || 0} <span className="text-sm text-[var(--muted)] font-sans">events</span>
          </div>
          <div className="text-xs text-[var(--muted)] truncate">
            Last milestone: {bcm.history?.milestones?.[0] || 'Onboarding'}
          </div>
          <div className="mt-4">
            <BlueprintButton size="sm" onClick={handleRefine} disabled={isLoading} className="w-full text-xs">
              {isLoading ? 'Refining...' : 'Refine with AI'}
            </BlueprintButton>
          </div>
        </BlueprintCard>
      </div>

      {/* Foundation Section */}
      <BlueprintCard showCorners padding="lg">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="font-serif text-xl text-[var(--ink)]">Foundation</h2>
            <p className="text-sm text-[var(--muted)] mt-1">Core business identity and positioning</p>
          </div>
          <BlueprintButton 
            size="sm" 
            onClick={() => handleSectionEdit('foundation')}
            disabled={editingSection !== null}
          >
            <Edit3 size={14} />
          </BlueprintButton>
        </div>

        {editingSection === 'foundation' ? (
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-technical text-[var(--muted)] mb-2">Company Name</label>
              <input
                type="text"
                value={tempData.foundation?.company || bcm.foundation.company}
                onChange={(e) => setTempData(prev => ({
                  ...prev,
                  foundation: { ...prev.foundation, company: e.target.value }
                }))}
                className="w-full px-3 py-2 bg-[var(--surface)] border border-[var(--border)] rounded text-sm text-[var(--ink)] focus:outline-none focus:border-[var(--ink)]"
              />
            </div>
            <div>
              <label className="block text-xs font-technical text-[var(--muted)] mb-2">Mission Statement</label>
              <textarea
                value={tempData.foundation?.mission || bcm.foundation.mission}
                onChange={(e) => setTempData(prev => ({
                  ...prev,
                  foundation: { ...prev.foundation, mission: e.target.value }
                }))}
                rows={3}
                className="w-full px-3 py-2 bg-[var(--surface)] border border-[var(--border)] rounded text-sm text-[var(--ink)] focus:outline-none focus:border-[var(--ink)]"
              />
            </div>
            <div>
              <label className="block text-xs font-technical text-[var(--muted)] mb-2">Value Proposition</label>
              <textarea
                value={tempData.foundation?.value_prop || bcm.foundation.value_prop}
                onChange={(e) => setTempData(prev => ({
                  ...prev,
                  foundation: { ...prev.foundation, value_prop: e.target.value }
                }))}
                rows={2}
                className="w-full px-3 py-2 bg-[var(--surface)] border border-[var(--border)] rounded text-sm text-[var(--ink)] focus:outline-none focus:border-[var(--ink)]"
              />
            </div>
            <div className="flex items-center gap-2 pt-2">
              <BlueprintButton size="sm" onClick={handleSave}>
                <Save size={14} />
                Save
              </BlueprintButton>
              <SecondaryButton size="sm" onClick={handleCancel}>
                Cancel
              </SecondaryButton>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <div>
              <span className="text-xs font-technical text-[var(--muted)]">Company</span>
              <p className="text-[var(--ink)]">{bcm.foundation.company}</p>
            </div>
            <div>
              <span className="text-xs font-technical text-[var(--muted)]">Mission</span>
              <p className="text-[var(--ink)]">{bcm.foundation.mission}</p>
            </div>
            <div>
              <span className="text-xs font-technical text-[var(--muted)]">Value Proposition</span>
              <p className="text-[var(--ink)]">{bcm.foundation.value_prop}</p>
            </div>
          </div>
        )}
      </BlueprintCard>

      {/* Messaging Section */}
      <BlueprintCard showCorners padding="lg">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="font-serif text-xl text-[var(--ink)]">Messaging</h2>
            <p className="text-sm text-[var(--muted)] mt-1">Brand voice and communication strategy</p>
          </div>
          <BlueprintButton 
            size="sm" 
            onClick={() => handleSectionEdit('messaging')}
            disabled={editingSection !== null}
          >
            <Edit3 size={14} />
          </BlueprintButton>
        </div>

        {editingSection === 'messaging' ? (
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-technical text-[var(--muted)] mb-2">One-Liner</label>
              <input
                type="text"
                value={tempData.messaging?.one_liner || bcm.messaging.one_liner}
                onChange={(e) => setTempData(prev => ({
                  ...prev,
                  messaging: { ...prev.messaging, one_liner: e.target.value }
                }))}
                className="w-full px-3 py-2 bg-[var(--surface)] border border-[var(--border)] rounded text-sm text-[var(--ink)] focus:outline-none focus:border-[var(--ink)]"
              />
            </div>
            <div>
              <label className="block text-xs font-technical text-[var(--muted)] mb-2">Brand Voice Tone</label>
              <input
                type="text"
                value={tempData.messaging?.brand_voice?.tone?.join(', ') || bcm.messaging.brand_voice.tone.join(', ')}
                onChange={(e) => setTempData(prev => ({
                  ...prev,
                  messaging: { 
                    ...prev.messaging, 
                    brand_voice: { 
                      ...prev.messaging?.brand_voice, 
                      tone: e.target.value.split(',').map(t => t.trim()).filter(t => t)
                    }
                  }
                }))}
                className="w-full px-3 py-2 bg-[var(--surface)] border border-[var(--border)] rounded text-sm text-[var(--ink)] focus:outline-none focus:border-[var(--ink)]"
                placeholder="Calm, Precise, Confident"
              />
            </div>
            <div className="flex items-center gap-2 pt-2">
              <BlueprintButton size="sm" onClick={handleSave}>
                <Save size={14} />
                Save
              </BlueprintButton>
              <SecondaryButton size="sm" onClick={handleCancel}>
                Cancel
              </SecondaryButton>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <div>
              <span className="text-xs font-technical text-[var(--muted)]">One-Liner</span>
              <p className="text-[var(--ink)] font-medium">{bcm.messaging.one_liner}</p>
            </div>
            <div>
              <span className="text-xs font-technical text-[var(--muted)]">Brand Voice</span>
              <div className="flex flex-wrap gap-2 mt-1">
                {bcm.messaging.brand_voice.tone.map((tone, index) => (
                  <BlueprintBadge key={index} variant="default" size="sm">
                    {tone}
                  </BlueprintBadge>
                ))}
              </div>
            </div>
          </div>
        )}
      </BlueprintCard>

      {/* ICPs Section */}
      <BlueprintCard showCorners padding="lg">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="font-serif text-xl text-[var(--ink)]">Ideal Customer Profiles</h2>
            <p className="text-sm text-[var(--muted)] mt-1">Target audience segments and personas</p>
          </div>
          <BlueprintButton 
            size="sm" 
            onClick={() => handleSectionEdit('icps')}
            disabled={editingSection !== null}
          >
            <Edit3 size={14} />
          </BlueprintButton>
        </div>

        <div className="space-y-4">
          {bcm.icps.map((icp, index) => (
            <div key={icp.id} className="p-4 bg-[var(--surface)] border border-[var(--border)] rounded">
              <h4 className="font-medium text-[var(--ink)]">{icp.name}</h4>
              <p className="text-sm text-[var(--muted)] mt-1">
                {icp.demographics?.role || 'No role specified'}
              </p>
            </div>
          ))}
        </div>
      </BlueprintCard>

      {/* Competitive Section */}
      <BlueprintCard showCorners padding="lg">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="font-serif text-xl text-[var(--ink)]">Competitive Landscape</h2>
            <p className="text-sm text-[var(--muted)] mt-1">Market positioning and differentiation</p>
          </div>
          <BlueprintButton 
            size="sm" 
            onClick={() => handleSectionEdit('competitive')}
            disabled={editingSection !== null}
          >
            <Edit3 size={14} />
          </BlueprintButton>
        </div>

        <div className="space-y-3">
          <div>
            <span className="text-xs font-technical text-[var(--muted)]">Competitors</span>
            <div className="flex flex-wrap gap-2 mt-1">
              {bcm.competitive.competitors.map((competitor, index) => (
                <BlueprintBadge key={index} variant="default" size="sm">
                  {competitor}
                </BlueprintBadge>
              ))}
            </div>
          </div>
          <div>
            <span className="text-xs font-technical text-[var(--muted)]">Differentiation</span>
            <p className="text-[var(--ink)]">{bcm.competitive.differentiation}</p>
          </div>
        </div>
      </BlueprintCard>
    </div>
  );
}
