'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

import { useRouter } from 'next/navigation';
import { useIcpStore } from '@/lib/icp-store';
import { Icp } from '@/types/icp-types';
import { getDefaultSalesMotion } from '@/lib/icp-logic';
import WizardLayout from './wizard/WizardLayout';
import WizardQuestion from './wizard/WizardQuestion';
import StepReview from './wizard/StepReview';
import { Ban, Check } from 'lucide-react';
import confetti from 'canvas-confetti';
import { BudgetSlider } from '@/components/ui/BudgetSlider';

// ==========================================
// CONSTANTS
// ==========================================

const BUSINESS_TYPES = [
  { value: 'saas', label: 'SaaS', desc: 'Subscription software' },
  { value: 'd2c', label: 'D2C', desc: 'Direct consumer physical goods' },
  { value: 'agency', label: 'Agency', desc: 'Service provider / Consult' },
  {
    value: 'service',
    label: 'Service',
    desc: 'Local or Professional services',
  },
];

const SALES_MOTIONS = [
  { value: 'self-serve', label: 'Self-Serve', desc: 'Product-led, no humans' },
  { value: 'demo-led', label: 'Demo-Led', desc: 'Sales calls required' },
  { value: 'sales-assisted', label: 'Sales-Assisted', desc: 'Hybrid model' },
];

const COMMON_PROBLEMS = [
  { value: 'Leads are inconsistent', label: 'Leads are inconsistent' },
  { value: 'No positioning clarity', label: 'No positioning clarity' },
  { value: "Content doesn't convert", label: "Content doesn't convert" },
  {
    value: 'Founder doing marketing themselves',
    label: 'Founder doing marketing',
  },
  { value: 'Pipeline unpredictable', label: 'Pipeline unpredictable' },
  { value: 'High churn rate', label: 'High churn rate' },
  { value: 'Long sales cycles', label: 'Long sales cycles' },
  {
    value: 'Competitors winning on price',
    label: 'Competitors winning on price',
  },
];

const TRIGGER_EVENTS = [
  { value: 'New funding round', label: 'New funding round' },
  { value: 'New executive hire', label: 'New executive hire' },
  { value: 'Product launch', label: 'Product launch' },
  { value: 'Fiscal year end', label: 'Fiscal year end' },
  { value: 'Compliance audit', label: 'Compliance audit' },
  { value: 'Tech stack migration', label: 'Tech stack migration' },
  { value: 'Team expansion', label: 'Team expansion' },
  { value: 'Missed quarterly target', label: 'Missed quarterly target' },
];

const BUDGET_RANGES = [
  { value: 'low', label: '< $1k/mo', desc: 'Price Shoppers' },
  { value: 'medium', label: '$1k - $5k/mo', desc: 'Value Buyers' },
  { value: 'high', label: '$5k - $20k/mo', desc: 'Solution Buyers' },
  { value: 'enterprise', label: '$20k+/mo', desc: 'Strategic Buyers' },
];

const URGENCY_LEVELS = [
  { value: 'now', label: 'Now', desc: 'Bleeding neck (High Confidence)' },
  { value: 'soon', label: 'Soon', desc: 'Within quarter (Normal)' },
  { value: 'someday', label: 'Someday', desc: 'Exploratory (Low Confidence)' },
];

const DECISION_MAKERS = [
  { value: 'Founder / CEO', label: 'Founder / CEO' },
  { value: 'Marketing Leader', label: 'Marketing Leader' },
  { value: 'Sales Leader', label: 'Sales Leader' },
  { value: 'CTO / Product', label: 'CTO / Product' },
  { value: 'Individual Contributor', label: 'Individual Contributor' },
];

const MINDSET_TRAITS = [
  { value: 'Skeptical of agencies', label: 'Skeptical of agencies' },
  { value: 'DIY mindset', label: 'DIY mindset' },
  { value: 'Hates marketing jargon', label: 'Hates marketing jargon' },
  { value: 'Responds to numbers', label: 'Responds to numbers' },
  { value: 'Emotion-driven', label: 'Emotion-driven' },
];

// Definitions for Tooltips
const DEFINITIONS: Record<string, string> = {
  PLG: 'Product-Led Growth. The product drives acquisition, retention, and expansion.',
  SLG: 'Sales-Led Growth. Driven by a dedicated sales team targeting high-value accounts.',
  ACV: 'Annual Contract Value. The average revenue per customer contract per year.',
  Churn:
    'The percentage of customers who stop using your product over a given period.',
  CAC: 'Customer Acquisition Cost. Total cost to acquire a new paying customer.',
  SaaS: 'Software as a Service. Cloud-based software delivery model.',
  Agency: 'Service-based business model providing specialized work.',
  B2B: 'Business-to-Business. Selling products or services to other companies.',
  B2C: 'Business-to-Consumer. Selling directly to individual consumers.',
  ICP: 'Ideal Customer Profile. A description of the fictional account that gets significant value from your product.',
};

const EXAMPLES: Record<string, string> = {
  business_model:
    'We are a B2B SaaS company selling primarily to mid-market tech companies.',
  sales_motion:
    'We use a self-serve PLG model for smaller teams, but a sales-assisted motion for enterprise deals.',
  primary_pains:
    'They are drowning in manual data entry and losing 10+ hours a week on spreadsheets.',
  decision_maker:
    'The VP of Marketing usually signs the check, but the Content Manager is the daily user.',
  budget:
    'They are comfortable spending $500/mo but need executive approval for anything over $2k.',
  mindset: 'They are ambitious and tech-savvy, but skeptical of AI hype.',
  proof: 'They trust G2 reviews and case studies from similar companies.',
  tone: 'We speak to them like a knowledgeable peer—direct, professional, no fluff.',
  excluded_types:
    'We do not sell to early-stage non-funded startups or agencies.',
};

const PROOF_PREFERENCES = [
  {
    value: 'case-study',
    label: 'Case Studies',
    desc: 'Narrative success stories',
  },
  { value: 'data', label: 'Hard Data', desc: 'Numbers, charts, ROI' },
  {
    value: 'authority',
    label: 'Authority',
    desc: 'Expert endorsements, awards',
  },
  { value: 'social', label: 'Social Proof', desc: 'Reviews, G2 badges' },
];

const TONE_PREFERENCES = [
  { value: 'Calm', label: 'Calm' },
  { value: 'Direct', label: 'Direct' },
  { value: 'Bold', label: 'Bold' },
  { value: 'Empathetic', label: 'Empathetic' },
  { value: 'Technical', label: 'Technical' },
  { value: 'Urgent', label: 'Urgent' },
];

const EXCLUDED_TYPES = [
  { value: 'Enterprise', label: 'Enterprise' },
  { value: 'Agencies', label: 'Agencies' },
  { value: 'Price shoppers', label: 'Price shoppers' },
  { value: 'Early hobbyists', label: 'Early hobbyists' },
  { value: 'Non-English markets', label: 'Non-English markets' },
  { value: 'Consultants', label: 'Consultants' },
];

const EXCLUDED_BEHAVIORS = [
  {
    value: 'Requires heavy customization',
    label: 'Requires heavy customization',
  },
  { value: 'Long procurement process', label: 'Long procurement process' },
  { value: 'Expects 24/7 support', label: 'Expects 24/7 support' },
  { value: 'Looking for free trials', label: 'Looking for free trials' },
  { value: 'Agency hoppers', label: 'Agency hoppers' },
];

// ==========================================
// MAIN COMPONENT
// ==========================================

const STEPS = [
  { id: 'business_model', title: 'Business Model' },
  { id: 'sales_motion', title: 'Sales Motion' },
  { id: 'primary_pains', title: 'Core Pain' },
  { id: 'triggers', title: 'Trigger Events' },
  { id: 'budget', title: 'Budget Comfort' },
  { id: 'urgency', title: 'Urgency' },
  { id: 'decision_maker', title: 'Decision Maker' },
  { id: 'mindset', title: 'Mindset' },
  { id: 'proof', title: 'Proof Preference' },
  { id: 'tone', title: 'Tone' },
  { id: 'excluded_types', title: 'Exclusions (Who)' },
  { id: 'excluded_behaviors', title: 'Exclusions (Behavior)' },
  { id: 'review', title: 'Review' },
];

export default function ICPWizard() {
  const router = useRouter();
  const createIcp = useIcpStore((state) => state.createIcp);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const isFirstStep = currentStepIndex === 0;
  const isLastStep = currentStepIndex === STEPS.length - 1;

  // Initial Data
  const [formData, setFormData] = useState<Partial<Icp>>({
    name: 'New Ideal Customer Profile',
    firmographics: {
      companyType: [],
      geography: [],
      salesMotion: [],
      budgetComfort: [],
      decisionMaker: [],
    },
    painMap: {
      primaryPains: [],
      secondaryPains: [],
      triggerEvents: [],
      urgencyLevel: 'soon',
    },
    psycholinguistics: {
      mindsetTraits: [],
      emotionalTriggers: [],
      tonePreference: [],
      wordsToUse: [],
      wordsToAvoid: [],
      proofPreference: [],
      ctaStyle: [],
    },
    disqualifiers: {
      excludedCompanyTypes: [],
      excludedGeographies: [],
      excludedBehaviors: [],
    },
  });

  // History for Undo/Redo
  const [history, setHistory] = useState<Partial<Icp>[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);

  // Helpers to update deeper state with history tracking
  const updateWithHistory = (updater: (prev: Partial<Icp>) => Partial<Icp>) => {
    setFormData((prev) => {
      const newState = updater(prev);
      // Add to history
      const newHistory = history.slice(0, historyIndex + 1);
      newHistory.push(newState);
      setHistory(newHistory);
      setHistoryIndex(newHistory.length - 1);
      return newState;
    });
  };

  // Undo/Redo Handlers
  const handleUndo = () => {
    if (historyIndex > 0) {
      setHistoryIndex((curr) => curr - 1);
      setFormData(history[historyIndex - 1]);
    }
  };

  // Bind Ctrl+Z
  useEffect(() => {
    const handleKeys = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'z') {
        e.preventDefault();
        handleUndo();
      }
    };
    window.addEventListener('keydown', handleKeys);
    return () => window.removeEventListener('keydown', handleKeys);
  }, [historyIndex, history]);

  // Initial history
  useEffect(() => {
    if (history.length === 0) {
      setHistory([formData]);
      setHistoryIndex(0);
    }
  }, []);

  // Helper wrappers
  const updateFirmo = (key: string, val: any) =>
    updateWithHistory((prev) => ({
      ...prev,
      firmographics: { ...prev.firmographics!, [key]: val },
    }));

  const updatePain = (key: string, val: any) =>
    updateWithHistory((prev) => ({
      ...prev,
      painMap: { ...prev.painMap!, [key]: val },
    }));

  const updatePsycho = (key: string, val: any) =>
    updateWithHistory((prev) => ({
      ...prev,
      psycholinguistics: { ...prev.psycholinguistics!, [key]: val },
    }));

  const updateDisqual = (key: string, val: any) =>
    updateWithHistory((prev) => ({
      ...prev,
      disqualifiers: { ...prev.disqualifiers!, [key]: val },
    }));

  // Legacy setters (if any direct use needed, but we should use wrappers)
  // ...

  const [direction, setDirection] = useState(0);
  const [isSuccess, setIsSuccess] = useState(false);

  const handleNext = () => {
    if (!isLastStep) {
      setDirection(1);
      setCurrentStepIndex((curr) => curr + 1);
    } else {
      // Success State
      createIcp(formData);
      setIsSuccess(true);

      // Task 59: Confetti Cannon
      const duration = 3000;
      const animationEnd = Date.now() + duration;
      const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };

      const randomInRange = (min: number, max: number) =>
        Math.random() * (max - min) + min;

      const interval: any = setInterval(function () {
        const timeLeft = animationEnd - Date.now();

        if (timeLeft <= 0) {
          return clearInterval(interval);
        }

        const particleCount = 50 * (timeLeft / duration);

        // since particles fall down, start a bit higher than random
        confetti({
          ...defaults,
          particleCount,
          origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 },
        });
        confetti({
          ...defaults,
          particleCount,
          origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 },
        });
      }, 250);

      setTimeout(() => {
        router.push('/target');
      }, 3000);
    }
  };

  // Smart Defaults Logic
  useEffect(() => {
    // If Company Type is 'saas' and Sales Motion is empty, suggest 'demo-led' or 'self-serve' (implied defaulting)
    // Since we can't assume, we just leave it for now or implement a softer nudge if needed.
    const type = formData.firmographics?.companyType?.[0];
    const motion = formData.firmographics?.salesMotion;

    const defaultMotion = getDefaultSalesMotion(type);
    if (defaultMotion && (!motion || motion.length === 0)) {
      updateFirmo('salesMotion', defaultMotion);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formData.firmographics?.companyType]);

  const handleBack = () => {
    if (!isFirstStep) {
      setDirection(-1);
      setCurrentStepIndex((curr) => curr - 1);
    }
  };

  const toggleSelection = (
    currentList: string[],
    item: string,
    setter: (val: any) => void
  ) => {
    // Safety check if list is undefined
    const safeList = currentList || [];
    const newList = safeList.includes(item)
      ? safeList.filter((i) => i !== item)
      : [...safeList, item];
    setter(newList);
  };

  const setSingleSelection = (item: string, setter: (val: any) => void) => {
    // For single select, we might store as array[1] or string depending on type
    // The store types seem to mostly use string[] even for things that could be single
    // But let's check: salesMotion is array, budgetComfort is array.
    // Urgency is string.
    setter([item]);
  };

  // Variants for slide animation
  const variants = {
    enter: (direction: number) => ({
      x: direction > 0 ? 50 : -50,
      opacity: 0,
    }),
    center: {
      zIndex: 1,
      x: 0,
      opacity: 1,
    },
    exit: (direction: number) => ({
      zIndex: 0,
      x: direction < 0 ? 50 : -50,
      opacity: 0,
    }),
  };

  // State for validation
  const [isNextDisabled, setIsNextDisabled] = useState(true);

  // Validation Effect
  useEffect(() => {
    const step = STEPS[currentStepIndex];
    let valid = false;

    switch (step.id) {
      case 'business_model':
        valid = (formData.firmographics?.companyType?.length || 0) > 0;
        break;
      case 'sales_motion':
        valid = (formData.firmographics?.salesMotion?.length || 0) > 0;
        break;
      case 'primary_pains':
        valid = (formData.painMap?.primaryPains?.length || 0) > 0;
        break;
      case 'budget':
        valid = (formData.firmographics?.budgetComfort?.length || 0) > 0;
        break;
      case 'urgency':
        valid = !!formData.painMap?.urgencyLevel;
        break;
      case 'decision_maker':
        valid = (formData.firmographics?.decisionMaker?.length || 0) > 0;
        break;
      case 'review':
        valid = !!formData.name;
        break;
      default:
        valid = true; // Optional steps or multi-selects where 0 is allowed?
        // Let's enforce 1 selection for most traits unless optional
        if (step.id === 'mindset')
          valid = (formData.psycholinguistics?.mindsetTraits?.length || 0) > 0;
        if (step.id === 'proof')
          valid =
            (formData.psycholinguistics?.proofPreference?.length || 0) > 0;
        if (step.id === 'tone')
          valid = (formData.psycholinguistics?.tonePreference?.length || 0) > 0;
        // Exclusions optional? Let's say yes for now.
        if (step.id.startsWith('excluded')) valid = true;
        if (step.id === 'triggers') valid = true; // Optional per UI text
    }
    setIsNextDisabled(!valid);
  }, [formData, currentStepIndex]);

  // Local Storage Persistence
  useEffect(() => {
    const saved = localStorage.getItem('icp_draft');
    if (saved) {
      try {
        // simple merge or full replace
        // For now, let's not overwrite if we already have state (which we don't on mount)
        // Actually mount is tricky with React.strictMode.
        // Let's just say if we are at step 0 and empty, load it.
      } catch (e) {}
    }
  }, []);

  useEffect(() => {
    // Save to local storage on change
    const timeout = setTimeout(() => {
      localStorage.setItem('icp_draft', JSON.stringify(formData));
    }, 1000);
    return () => clearTimeout(timeout);
  }, [formData]);

  // Keyboard Navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter' && !isNextDisabled) {
        handleNext();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isNextDisabled, currentStepIndex]); // Re-bind when validation changes

  // Flags for "Unsure"
  const [unsureSteps, setUnsureSteps] = useState<Record<string, boolean>>({});

  const toggleUnsure = (stepId: string) => {
    setUnsureSteps((prev) => ({ ...prev, [stepId]: !prev[stepId] }));
  };

  const isStepUnsure = (stepId: string) => !!unsureSteps[stepId];

  // RENDER STEP CONTENT
  const renderStepContent = () => {
    const step = STEPS[currentStepIndex];
    const content = (() => {
      switch (step.id) {
        case 'business_model':
          return (
            <WizardQuestion
              title="Business Context."
              subtitle="What is their business model?"
              whyWeAsk="Your business model dictates the types of pains you solve. A SaaS company solves efficiency pains; an Agency solves capacity pains."
              options={BUSINESS_TYPES}
              selectedValues={formData.firmographics?.companyType || []}
              onSelect={(val) =>
                setSingleSelection(val, (d) => updateFirmo('companyType', d))
              }
              autoAdvance
              onAutoAdvance={handleNext}
              cols={2}
              isUnsure={isStepUnsure('business_model')}
              onToggleUnsure={() => toggleUnsure('business_model')}
              definitions={DEFINITIONS}
              example={EXAMPLES['business_model']}
            />
          );

        case 'sales_motion':
          return (
            <WizardQuestion
              title="Sales Motion."
              subtitle={`Since you are a ${formData.firmographics?.companyType?.[0] || 'business'}, how do you acquire customers?`}
              whyWeAsk="Sales-led motions need logical arguments. Product-led motions need emotional hooks."
              options={SALES_MOTIONS}
              selectedValues={formData.firmographics?.salesMotion || []}
              onSelect={(val) =>
                setSingleSelection(val, (d) => updateFirmo('salesMotion', d))
              }
              autoAdvance
              onAutoAdvance={handleNext}
              cols={3}
              isUnsure={isStepUnsure('sales_motion')}
              onToggleUnsure={() => toggleUnsure('sales_motion')}
              definitions={DEFINITIONS}
              example={EXAMPLES['sales_motion']}
            />
          );

        case 'primary_pains':
          return (
            <WizardQuestion
              title="Problem Gravity."
              subtitle={`For a ${formData.firmographics?.salesMotion?.[0] || ''} model, what is the bleeding neck problem?`}
              whyWeAsk="People buy to stop pain, not to gain pleasure. We need the sharpest rock in their shoe."
              options={COMMON_PROBLEMS}
              selectedValues={formData.painMap?.primaryPains || []}
              multiSelect
              maxSelections={2}
              onSelect={(val) =>
                toggleSelection(formData.painMap?.primaryPains!, val, (d) =>
                  updatePain('primaryPains', d)
                )
              }
              cols={2}
              isUnsure={isStepUnsure('primary_pains')}
              onToggleUnsure={() => toggleUnsure('primary_pains')}
              definitions={DEFINITIONS}
              example={EXAMPLES['primary_pains']}
            />
          );

        case 'triggers':
          return (
            <WizardQuestion
              title="Trigger Events."
              subtitle="What happens right before they buy? (Optional)"
              options={TRIGGER_EVENTS}
              selectedValues={formData.painMap?.triggerEvents || []}
              multiSelect
              onSelect={(val) =>
                toggleSelection(formData.painMap?.triggerEvents!, val, (d) =>
                  updatePain('triggerEvents', d)
                )
              }
              cols={2}
              isUnsure={isStepUnsure('triggers')}
              onToggleUnsure={() => toggleUnsure('triggers')}
              definitions={DEFINITIONS}
            />
          );

        case 'budget':
          return (
            <WizardQuestion
              title="Buyer Reality Check."
              subtitle="Who is signing the check, and can they actually afford you?"
              whyWeAsk="If they can't afford you, they aren't an ICP. They are a fan."
              isUnsure={isStepUnsure('budget')}
              onToggleUnsure={() => toggleUnsure('budget')}
              definitions={DEFINITIONS}
              example={EXAMPLES['budget']}
              selectedValues={[]}
              onSelect={() => {}}
              // Render Budget Slider as children or override
            >
              <BudgetSlider
                value={
                  formData.firmographics?.budgetComfort?.[0] ||
                  BUDGET_RANGES[0].label
                }
                ranges={BUDGET_RANGES.map((r) => r.label)}
                onChange={(val) =>
                  setSingleSelection(val, (d) =>
                    updateFirmo('budgetComfort', d)
                  )
                }
              />
            </WizardQuestion>
          );

        case 'urgency':
          return (
            <WizardQuestion
              title="Urgency Level."
              subtitle="How fast does this problem need solving?"
              options={URGENCY_LEVELS}
              selectedValues={
                formData.painMap?.urgencyLevel
                  ? [formData.painMap.urgencyLevel]
                  : []
              }
              onSelect={(val) => updatePain('urgencyLevel', val)} // Urgency is specific string in type
              autoAdvance
              onAutoAdvance={handleNext}
              cols={3}
              isUnsure={isStepUnsure('urgency')}
              onToggleUnsure={() => toggleUnsure('urgency')}
              definitions={DEFINITIONS}
              example={EXAMPLES['secondary_pains']}
            />
          );

        case 'decision_maker':
          return (
            <WizardQuestion
              title="Primary Decision Maker."
              subtitle="Who puts their neck on the line?"
              options={DECISION_MAKERS}
              selectedValues={formData.firmographics?.decisionMaker || []}
              onSelect={(val) =>
                setSingleSelection(val, (d) => updateFirmo('decisionMaker', d))
              }
              autoAdvance
              onAutoAdvance={handleNext}
              cols={2}
              isUnsure={isStepUnsure('decision_maker')}
              onToggleUnsure={() => toggleUnsure('decision_maker')}
              definitions={DEFINITIONS}
              example={EXAMPLES['decision_maker']}
            />
          );

        case 'mindset':
          return (
            <WizardQuestion
              title="Psychographics & Mindset."
              subtitle="Pick 3-5 traits that describe their mental state."
              options={MINDSET_TRAITS}
              selectedValues={formData.psycholinguistics?.mindsetTraits || []}
              multiSelect
              onSelect={(val) =>
                toggleSelection(
                  formData.psycholinguistics?.mindsetTraits!,
                  val,
                  (d) => updatePsycho('mindsetTraits', d)
                )
              }
              cols={3}
              isUnsure={isStepUnsure('mindset')}
              onToggleUnsure={() => toggleUnsure('mindset')}
              definitions={DEFINITIONS}
              example={EXAMPLES['mindset']}
            />
          );

        case 'proof':
          return (
            <WizardQuestion
              title="Proof Preference."
              subtitle="What convinces them to trust you?"
              options={PROOF_PREFERENCES}
              selectedValues={formData.psycholinguistics?.proofPreference || []}
              multiSelect
              onSelect={(val) =>
                toggleSelection(
                  formData.psycholinguistics?.proofPreference!,
                  val,
                  (d) => updatePsycho('proofPreference', d)
                )
              }
              cols={2}
              isUnsure={isStepUnsure('proof')}
              onToggleUnsure={() => toggleUnsure('proof')}
              definitions={DEFINITIONS}
              example={EXAMPLES['proof']}
            />
          );

        case 'tone':
          return (
            <WizardQuestion
              title="Tone Preference."
              subtitle="How should we speak to them?"
              options={TONE_PREFERENCES}
              selectedValues={formData.psycholinguistics?.tonePreference || []}
              multiSelect
              onSelect={(val) =>
                toggleSelection(
                  formData.psycholinguistics?.tonePreference!,
                  val,
                  (d) => updatePsycho('tonePreference', d)
                )
              }
              cols={3}
              isUnsure={isStepUnsure('tone')}
              onToggleUnsure={() => toggleUnsure('tone')}
              definitions={DEFINITIONS}
              example={EXAMPLES['tone']}
            />
          );

        case 'excluded_types':
          return (
            <WizardQuestion
              title={
                <span className="flex items-center justify-center gap-2">
                  Who to{' '}
                  <span className="text-red-700 font-serif italic">Ignore</span>
                  .
                </span>
              }
              subtitle="Disqualifiers. Who wastes your time? (Company Types)"
              options={EXCLUDED_TYPES}
              selectedValues={
                formData.disqualifiers?.excludedCompanyTypes || []
              }
              multiSelect
              onSelect={(val) =>
                toggleSelection(
                  formData.disqualifiers?.excludedCompanyTypes!,
                  val,
                  (d) => updateDisqual('excludedCompanyTypes', d)
                )
              }
              cols={3}
              isUnsure={isStepUnsure('excluded_types')}
              onToggleUnsure={() => toggleUnsure('excluded_types')}
              definitions={DEFINITIONS}
              example={EXAMPLES['excluded_types']}
            />
          );

        case 'excluded_behaviors':
          return (
            <WizardQuestion
              title={
                <span className="flex items-center justify-center gap-2">
                  Red Flags <Ban className="w-8 h-8 text-red-500" />
                </span>
              }
              subtitle="Behaviors that signal a bad customer."
              options={EXCLUDED_BEHAVIORS}
              selectedValues={formData.disqualifiers?.excludedBehaviors || []}
              multiSelect
              onSelect={(val) =>
                toggleSelection(
                  formData.disqualifiers?.excludedBehaviors!,
                  val,
                  (d) => updateDisqual('excludedBehaviors', d)
                )
              }
              cols={2}
              isUnsure={isStepUnsure('excluded_behaviors')}
              onToggleUnsure={() => toggleUnsure('excluded_behaviors')}
              definitions={DEFINITIONS}
              example={EXAMPLES['excluded_behaviors']}
            />
          );

        case 'review':
          return (
            <StepReview
              data={formData}
              onChange={(d) => setFormData((prev) => ({ ...prev, ...d }))}
              onJumpToStep={(stepId) => {
                const idx = STEPS.findIndex((s) => s.id === stepId);
                if (idx !== -1) setCurrentStepIndex(idx);
              }}
            />
          );

        default:
          return null;
      }
    })();

    return (
      <AnimatePresence custom={direction} mode="wait">
        <motion.div
          key={currentStepIndex}
          custom={direction}
          variants={variants}
          initial="enter"
          animate="center"
          exit="exit"
          transition={{
            x: { type: 'spring', stiffness: 300, damping: 30 },
            opacity: { duration: 0.2 },
          }}
          className="w-full"
        >
          {content}
        </motion.div>
      </AnimatePresence>
    );
  };

  if (isSuccess) {
    return (
      <div className="min-h-screen bg-[#2D3538] text-[#F3F4EE] flex items-center justify-center">
        <div className="text-center space-y-6 max-w-md px-6">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5, type: 'spring' }}
            className="w-24 h-24 bg-[#F3F4EE] rounded-full mx-auto flex items-center justify-center text-[#2D3538] relative"
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
              className="absolute inset-0 border-4 border-[#F3F4EE]/30 border-t-[#F3F4EE] rounded-full"
            />
            <Check className="w-10 h-10" />
          </motion.div>

          <div className="space-y-2">
            <h1 className="font-serif text-3xl md:text-4xl animate-pulse">
              Calibrating RaptorFlow...
            </h1>
            <div className="h-1 w-full bg-[#FFFFFF]/10 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: '0%' }}
                animate={{ width: '100%' }}
                transition={{ duration: 2.5, ease: 'easeInOut' }}
                className="h-full bg-[#D7C9AE]"
              />
            </div>
            <p className="text-[#9D9F9F] text-sm font-mono pt-2">
              Analyzing firmographics &bull; Mapping pain points &bull; Locking
              profile
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Dynamic Hints based on logic
  const getStepHint = () => {
    const stepId = STEPS[currentStepIndex].id;
    const { firmographics } = formData;

    if (
      stepId === 'sales_motion' &&
      firmographics?.companyType.includes('saas')
    ) {
      return 'Because you selected SaaS, this choice defines your Go-to-Market velocity.';
    }
    if (
      stepId === 'primary_pains' &&
      firmographics?.salesMotion.includes('sales-assisted')
    ) {
      return 'For Sales-Assisted deals, pains must be urgent enough to justify a meeting.';
    }
    if (
      stepId === 'decision_maker' &&
      firmographics?.companyType.includes('agency')
    ) {
      return 'Agencies often sell to founders or marketing heads directly.';
    }

    return undefined;
  };

  const getStepLabel = () => {
    const step = STEPS[currentStepIndex];
    // Dynamic mapping based on ID or index
    const map: Record<string, string> = {
      business_model: 'Establishing Context...',
      sales_motion: 'Sales Physics...',
      primary_pains: 'Mapping Pain Points...',
      secondary_pains: 'Depth & Triggers...',
      budget: 'Financial Qualification...',
      decision_maker: 'Buying Committee...',
      mindset: 'Psychographics...',
      tone: 'Voice Calibration...',
      review: 'Final Polish',
    };
    return map[step.id] || `Step ${currentStepIndex + 1}`;
  };

  const getTimeRemaining = () => {
    const remaining = STEPS.length - currentStepIndex - 1;
    if (remaining <= 0) return 'Almost done';
    return `~${Math.ceil(remaining * 0.5)} min left`;
  };

  return (
    <WizardLayout
      currentStep={currentStepIndex + 1}
      totalSteps={STEPS.length}
      canGoBack={!isFirstStep}
      onBack={handleBack}
      onNext={handleNext}
      isLastStep={isLastStep}
      isNextDisabled={isNextDisabled}
      stepLabel={getStepLabel()}
      timeRemaining={getTimeRemaining()}
      hint={getStepHint()}
    >
      {renderStepContent()}
    </WizardLayout>
  );
}
