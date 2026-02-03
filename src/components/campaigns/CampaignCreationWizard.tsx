"use client";

import { useState } from 'react';
import {
  ChevronLeft,
  ChevronRight,
  Save,
  X,
  Plus,
  Trash2,
  Calendar,
  DollarSign,
  Users,
  Target,
  Lightbulb
} from 'lucide-react';
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { BlueprintButton } from '@/components/ui/BlueprintButton';
import { BlueprintBadge } from '@/components/ui/BlueprintBadge';
import { useEnhancedCampaignStore } from '@/stores/enhancedCampaignStore';
import { CreateCampaignRequest, CampaignObjective } from '@/types/campaign';
import { allCampaignTemplates, getTemplateById } from '@/data/campaignTemplates';
import { cn } from '@/lib/utils';

interface CampaignCreationWizardProps {
  onClose: () => void;
  onSave?: (campaignId: string) => void;
}

interface WizardStep {
  id: number;
  title: string;
  description: string;
}

const wizardSteps: WizardStep[] = [
  {
    id: 1,
    title: 'Objective',
    description: 'What do you want to achieve?'
  },
  {
    id: 2,
    title: 'Template',
    description: 'Choose a template to get started'
  },
  {
    id: 3,
    title: 'Details',
    description: 'Campaign name and description'
  },
  {
    id: 4,
    title: 'Audience',
    description: 'Define your target audience'
  },
  {
    id: 5,
    title: 'Budget & Timeline',
    description: 'Set your budget and schedule'
  }
];

const objectives = [
  {
    value: CampaignObjective.LAUNCH,
    label: 'Product Launch',
    description: 'Launch a new product or feature',
    icon: '🚀'
  },
  {
    value: CampaignObjective.LEAD_GENERATION,
    label: 'Lead Generation',
    description: 'Generate qualified leads',
    icon: '🎯'
  },
  {
    value: CampaignObjective.CONVERSION,
    label: 'Conversion',
    description: 'Drive conversions and sales',
    icon: '💰'
  },
  {
    value: CampaignObjective.AWARENESS,
    label: 'Brand Awareness',
    description: 'Increase brand visibility',
    icon: '📢'
  },
  {
    value: CampaignObjective.RETENTION,
    label: 'Customer Retention',
    description: 'Keep customers engaged',
    icon: '🔄'
  },
  {
    value: CampaignObjective.PROMOTION,
    label: 'Promotion',
    description: 'Promote an event or offer',
    icon: '🎉'
  }
];

export function CampaignCreationWizard({ onClose, onSave }: CampaignCreationWizardProps) {
  const createCampaign = useEnhancedCampaignStore(state => state.createCampaign);

  const [currentStep, setCurrentStep] = useState(1);
  const [selectedObjective, setSelectedObjective] = useState<CampaignObjective | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [campaignData, setCampaignData] = useState<Partial<CreateCampaignRequest>>({});

  // Update campaign data
  const updateData = (field: keyof CreateCampaignRequest, value: any) => {
    setCampaignData(prev => ({ ...prev, [field]: value }));
  };

  // Handle step navigation
  const canGoNext = () => {
    switch (currentStep) {
      case 1:
        return selectedObjective !== null;
      case 2:
        return selectedTemplate !== null;
      case 3:
        return campaignData.name && campaignData.description;
      case 4:
        return typeof campaignData.targetAudience === 'string'
          ? campaignData.targetAudience
          : campaignData.targetAudience?.name;
      case 5:
        const budgetTotal = typeof campaignData.budget === 'number'
          ? campaignData.budget
          : campaignData.budget?.total;
        return budgetTotal && campaignData.timeline?.startDate;
      default:
        return false;
    }
  };

  const handleNext = () => {
    if (canGoNext() && currentStep < wizardSteps.length) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleSave = async () => {
    try {
      const request: CreateCampaignRequest = {
        name: campaignData.name || '',
        description: campaignData.description || '',
        objective: selectedObjective!,
        targetAudience: campaignData.targetAudience || {
          name: 'Default Audience',
          criteria: {}
        },
        budget: campaignData.budget || { total: 0, currency: 'USD' },
        timeline: campaignData.timeline || {}
      };

      const campaignId = await createCampaign(request);
      onSave?.(campaignId);
      onClose();
    } catch (error) {
      console.error('Failed to create campaign:', error);
    }
  };

  // Render step content
  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              {objectives.map((objective) => (
                <button
                  key={objective.value}
                  onClick={() => setSelectedObjective(objective.value)}
                  className={cn(
                    "p-4 border rounded-[var(--radius)] text-left transition-all",
                    selectedObjective === objective.value
                      ? "border-[var(--blueprint)] bg-[var(--blueprint-light)]/10"
                      : "border-[var(--structure-subtle)] hover:border-[var(--ink)]"
                  )}
                >
                  <div className="text-2xl mb-2">{objective.icon}</div>
                  <h3 className="font-semibold text-[var(--ink)] mb-1">
                    {objective.label}
                  </h3>
                  <p className="text-sm text-[var(--ink-muted)]">
                    {objective.description}
                  </p>
                </button>
              ))}
            </div>
          </div>
        );

      case 2:
        const templates = selectedObjective
          ? allCampaignTemplates.filter(t => t.objective === selectedObjective)
          : allCampaignTemplates;

        return (
          <div className="space-y-4">
            <div className="grid grid-cols-1 gap-4">
              {templates.map((template) => (
                <button
                  key={template.id}
                  onClick={() => setSelectedTemplate(template.id)}
                  className={cn(
                    "p-4 border rounded-[var(--radius)] text-left transition-all",
                    selectedTemplate === template.id
                      ? "border-[var(--blueprint)] bg-[var(--blueprint-light)]/10"
                      : "border-[var(--structure-subtle)] hover:border-[var(--ink)]"
                  )}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-[var(--ink)] mb-1">
                        {template.name}
                      </h3>
                      <p className="text-sm text-[var(--ink-muted)] mb-2">
                        {template.description}
                      </p>
                      <div className="flex items-center gap-2">
                        <BlueprintBadge variant="blueprint" size="sm">
                          {template.category}
                        </BlueprintBadge>
                        <span className="text-xs text-[var(--ink-ghost)]">
                          {template.usageCount} uses • {template.rating}★
                        </span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <div className="text-xs text-[var(--ink-muted)] mb-1">Phases</div>
                      <div className="text-sm font-medium text-[var(--ink)]">
                        {template.structure?.phases.length ?? 0}
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        );

      case 3:
        const template = selectedTemplate ? getTemplateById(selectedTemplate) : null;

        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[var(--ink)] mb-2">
                Campaign Name
              </label>
              <input
                type="text"
                value={campaignData.name || ''}
                onChange={(e) => updateData('name', e.target.value)}
                placeholder={template?.name || 'Enter campaign name'}
                className="w-full px-3 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--ink)] mb-2">
                Description
              </label>
              <textarea
                value={campaignData.description || ''}
                onChange={(e) => updateData('description', e.target.value)}
                placeholder={template?.description || 'Describe your campaign...'}
                rows={4}
                className="w-full px-3 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)] resize-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--ink)] mb-2">
                Tags
              </label>
              <input
                type="text"
                value={(campaignData as any).tags?.join(', ') || ''}
                onChange={(e) => updateData('tags' as any, e.target.value.split(', ').map(t => t.trim()).filter(Boolean))}
                placeholder="e.g. product-launch, q4-2024, b2b"
                className="w-full px-3 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]"
              />
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[var(--ink)] mb-2">
                Audience Name
              </label>
              <input
                type="text"
                value={(typeof campaignData.targetAudience === 'object' ? campaignData.targetAudience?.name : campaignData.targetAudience) || ''}
                onChange={(e) => updateData('targetAudience', {
                  name: e.target.value,
                  criteria: {}
                })}
                placeholder="e.g. B2B Decision Makers"
                className="w-full px-3 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--ink)] mb-2">
                Demographics
              </label>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-[var(--ink-muted)] mb-1">Age Range</label>
                  <select className="w-full px-3 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]">
                    <option>18-24</option>
                    <option>25-34</option>
                    <option>35-44</option>
                    <option>45-54</option>
                    <option>55+</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-[var(--ink-muted)] mb-1">Location</label>
                  <input
                    type="text"
                    placeholder="e.g. United States"
                    className="w-full px-3 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]"
                  />
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--ink)] mb-2">
                Firmographics (B2B)
              </label>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-[var(--ink-muted)] mb-1">Company Size</label>
                  <select className="w-full px-3 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]">
                    <option>1-10</option>
                    <option>11-50</option>
                    <option>51-200</option>
                    <option>201-500</option>
                    <option>500+</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-[var(--ink-muted)] mb-1">Industry</label>
                  <select className="w-full px-3 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]">
                    <option>Technology</option>
                    <option>Healthcare</option>
                    <option>Finance</option>
                    <option>Education</option>
                    <option>Other</option>
                  </select>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--ink)] mb-2">
                Estimated Reach
              </label>
              <input
                type="number"
                value={(typeof campaignData.targetAudience === 'object' ? campaignData.targetAudience?.estimatedReach : '') || ''}
                onChange={(e) => updateData('targetAudience', {
                  name: '',
                  criteria: {},
                  estimatedReach: parseInt(e.target.value) || 0
                })}
                placeholder="e.g. 10000"
                className="w-full px-3 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]"
              />
            </div>
          </div>
        );

      case 5:
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[var(--ink)] mb-2">
                Total Budget
              </label>
              <div className="relative">
                <DollarSign size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[var(--ink-ghost)]" />
                <input
                  type="number"
                  value={(typeof campaignData.budget === 'object' ? campaignData.budget?.total : campaignData.budget) || ''}
                  onChange={(e) => updateData('budget', {
                    total: parseInt(e.target.value) || 0,
                    currency: 'USD'
                  })}
                  placeholder="10000"
                  className="w-full pl-10 pr-3 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--ink)] mb-2">
                Currency
              </label>
              <select
                value={(typeof campaignData.budget === 'object' ? campaignData.budget?.currency : 'USD') || 'USD'}
                onChange={(e) => updateData('budget', {
                  total: 0,
                  currency: e.target.value
                })}
                className="w-full px-3 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]"
              >
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
                <option value="GBP">GBP</option>
                <option value="JPY">JPY</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-[var(--ink)] mb-2">
                  Start Date
                </label>
                <input
                  type="date"
                  value={campaignData.timeline?.startDate ? new Date(campaignData.timeline.startDate).toISOString().split('T')[0] : ''}
                  onChange={(e) => updateData('timeline', {
                    ...campaignData.timeline,
                    startDate: new Date(e.target.value)
                  })}
                  className="w-full px-3 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--ink)] mb-2">
                  End Date
                </label>
                <input
                  type="date"
                  value={campaignData.timeline?.endDate ? new Date(campaignData.timeline.endDate).toISOString().split('T')[0] : ''}
                  onChange={(e) => updateData('timeline', {
                    ...campaignData.timeline,
                    endDate: new Date(e.target.value)
                  })}
                  className="w-full px-3 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]"
                />
              </div>
            </div>

            <div className="p-4 bg-[var(--blueprint-light)]/10 rounded-[var(--radius)]">
              <div className="flex items-start gap-2">
                <Lightbulb size={16} className="text-[var(--blueprint)] mt-0.5" />
                <div className="text-sm">
                  <p className="font-medium text-[var(--ink)] mb-1">Budget Allocation Tip</p>
                  <p className="text-[var(--ink-muted)]">
                    Consider allocating 40% to content creation, 30% to paid promotion,
                    20% to email marketing, and 10% to analytics and optimization.
                  </p>
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <BlueprintCard className="w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-[var(--structure-subtle)]">
          <div>
            <h2 className="text-xl font-bold text-[var(--ink)]">Create Campaign</h2>
            <p className="text-sm text-[var(--ink-muted)] mt-1">
              Step {currentStep} of {wizardSteps.length}: {wizardSteps[currentStep - 1].title}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-[var(--surface)] rounded text-[var(--ink-muted)]"
          >
            <X size={20} />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="px-6 py-4 border-b border-[var(--structure-subtle)]">
          <div className="flex items-center justify-between mb-2">
            {wizardSteps.map((step, index) => (
              <div
                key={step.id}
                className={cn(
                  "flex items-center",
                  index < wizardSteps.length - 1 && "flex-1"
                )}
              >
                <div
                  className={cn(
                    "w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium transition-colors",
                    step.id <= currentStep
                      ? "bg-[var(--blueprint)] text-white"
                      : "bg-[var(--surface)] text-[var(--ink-muted)]"
                  )}
                >
                  {step.id}
                </div>
                {index < wizardSteps.length - 1 && (
                  <div
                    className={cn(
                      "flex-1 h-0.5 mx-2 transition-colors",
                      step.id < currentStep
                        ? "bg-[var(--blueprint)]"
                        : "bg-[var(--structure-subtle)]"
                    )}
                  />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-between">
            {wizardSteps.map((step) => (
              <span
                key={step.id}
                className={cn(
                  "text-xs",
                  step.id === currentStep
                    ? "text-[var(--ink)] font-medium"
                    : step.id < currentStep
                      ? "text-[var(--blueprint)]"
                      : "text-[var(--ink-ghost)]"
                )}
              >
                {step.title}
              </span>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-[var(--ink)] mb-1">
              {wizardSteps[currentStep - 1].title}
            </h3>
            <p className="text-sm text-[var(--ink-muted)]">
              {wizardSteps[currentStep - 1].description}
            </p>
          </div>

          {renderStepContent()}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-[var(--structure-subtle)]">
          <BlueprintButton
            variant="secondary"
            onClick={handlePrevious}
            disabled={currentStep === 1}
          >
            Previous
          </BlueprintButton>

          <div className="flex items-center gap-2">
            {currentStep === wizardSteps.length ? (
              <BlueprintButton
                onClick={handleSave}
                disabled={!canGoNext()}
                className="flex items-center gap-2"
              >
                <Save size={16} />
                Create Campaign
              </BlueprintButton>
            ) : (
              <BlueprintButton
                onClick={handleNext}
                disabled={!canGoNext()}
                className="flex items-center gap-2"
              >
                Next
                <ChevronRight size={16} />
              </BlueprintButton>
            )}
          </div>
        </div>
      </BlueprintCard>
    </div>
  );
}
