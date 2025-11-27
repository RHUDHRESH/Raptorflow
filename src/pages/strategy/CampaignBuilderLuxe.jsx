/**
 * Campaign Builder (Luxe Edition)
 * 
 * The strategic campaign creation and management center.
 */

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, useNavigate, useParams } from 'react-router-dom';
import {
  Target,
  Users,
  Megaphone,
  Zap,
  ArrowLeft,
  Save,
  RefreshCw,
  Clock,
  CheckCircle2,
  Mail,
  MessageSquare,
  Globe,
  Phone,
  Instagram,
  Linkedin,
  Twitter,
  AlertCircle
} from 'lucide-react';
import { cn } from '../../utils/cn';
import { LuxeHeading, LuxeButton, LuxeCard, LuxeInput, LuxeBadge } from '../../components/ui/PremiumUI';
import { pageTransition, fadeInUp, staggerContainer } from '../../utils/animations';

// =============================================================================
// CONSTANTS & MOCK DATA
// =============================================================================

const CAMPAIGN_OBJECTIVES = [
  {
    id: 'awareness',
    label: 'Awareness',
    description: 'Get on their radar',
    icon: Megaphone,
    color: 'purple',
    metrics: ['Impressions', 'Reach', 'Brand mentions', 'Share of voice'],
    recommended_duration: '4-8 weeks',
  },
  {
    id: 'consideration',
    label: 'Consideration',
    description: 'Get them evaluating you',
    icon: Target,
    color: 'blue',
    metrics: ['Website visits', 'Content engagement', 'Email signups', 'Time on site'],
    recommended_duration: '4-6 weeks',
  },
  {
    id: 'conversion',
    label: 'Conversion',
    description: 'Get them to act',
    icon: Zap,
    color: 'green',
    metrics: ['Demo requests', 'Trial signups', 'Purchases', 'SQLs'],
    recommended_duration: '2-4 weeks',
  },
  {
    id: 'retention',
    label: 'Retention',
    description: 'Keep them engaged',
    icon: RefreshCw,
    color: 'amber',
    metrics: ['Churn rate', 'NPS', 'Feature adoption', 'Support tickets'],
    recommended_duration: 'Ongoing',
  },
  {
    id: 'advocacy',
    label: 'Advocacy',
    description: 'Get them promoting you',
    icon: Users,
    color: 'pink',
    metrics: ['Referrals', 'Reviews', 'Case studies', 'Social shares'],
    recommended_duration: 'Ongoing',
  },
];

const MOCK_POSITIONING = {
  id: 'pos-1',
  name: 'Primary Positioning',
  category_frame: 'RaptorFlow is the strategic marketing command center',
  differentiator: 'that turns scattered activities into coordinated campaigns',
  reason_to_believe: 'because we combine AI-powered cohort intelligence with battle-tested frameworks',
};

const MOCK_MESSAGE_ARCH = {
  id: 'ma-1',
  primary_claim: 'Ship campaigns 3x faster with half the chaos',
  proof_points: [
    { id: 'pp-1', claim: 'AI-powered cohort intelligence', priority: 1 },
    { id: 'pp-2', claim: 'Battle-tested campaign frameworks', priority: 2 },
    { id: 'pp-3', claim: 'Real-time performance insights', priority: 3 },
  ],
};

const MOCK_COHORTS = [
  {
    id: 'c1',
    name: 'Enterprise CTOs',
    description: 'Tech leaders at large companies',
    health_score: 85,
    journey_distribution: {
      unaware: 0.2,
      problem_aware: 0.3,
      solution_aware: 0.25,
      product_aware: 0.15,
      most_aware: 0.1,
    },
  },
  {
    id: 'c2',
    name: 'Startup Founders',
    description: 'Early-stage company builders',
    health_score: 72,
    journey_distribution: {
      unaware: 0.4,
      problem_aware: 0.25,
      solution_aware: 0.2,
      product_aware: 0.1,
      most_aware: 0.05,
    },
  },
  {
    id: 'c3',
    name: 'Marketing Directors',
    description: 'Marketing leaders at mid-market',
    health_score: 91,
    journey_distribution: {
      unaware: 0.15,
      problem_aware: 0.25,
      solution_aware: 0.3,
      product_aware: 0.2,
      most_aware: 0.1,
    },
  },
];

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function CampaignBuilderLuxe() {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEditing = !!id;

  // Wizard state
  const [currentStep, setCurrentStep] = useState(1);
  const totalSteps = 5;

  // Campaign data
  const [campaign, setCampaign] = useState({
    name: '',
    description: '',
    positioning_id: MOCK_POSITIONING.id,
    message_architecture_id: MOCK_MESSAGE_ARCH.id,
    objective: '',
    objective_statement: '',
    success_definition: '',
    primary_metric: '',
    target_value: '',
    secondary_metrics: [],
    budget: '',
    start_date: '',
    end_date: '',
    target_cohorts: [],
    channel_strategy: [],
    status: 'draft',
  });

  // UI state
  const [saving, setSaving] = useState(false);

  // Validation
  const stepValidation = useMemo(() => ({
    1: !!campaign.positioning_id && !!campaign.message_architecture_id,
    2: !!campaign.objective && !!campaign.objective_statement && !!campaign.primary_metric,
    3: campaign.target_cohorts.length > 0 && campaign.target_cohorts.some(c => c.priority === 'primary'),
    4: campaign.channel_strategy.length > 0, // Simplified for now
    5: !!campaign.name && !!campaign.start_date && !!campaign.end_date,
  }), [campaign]);

  const canProceed = stepValidation[currentStep];
  const overallProgress = Object.values(stepValidation).filter(Boolean).length / totalSteps * 100;

  // Handlers
  const updateCampaign = (updates) => {
    setCampaign(prev => ({ ...prev, ...updates }));
  };

  const addCohort = (cohortId, priority = 'secondary') => {
    const cohort = MOCK_COHORTS.find(c => c.id === cohortId);
    if (!cohort) return;

    // If setting as primary, demote existing primary
    let updatedCohorts = [...campaign.target_cohorts];
    if (priority === 'primary') {
      updatedCohorts = updatedCohorts.map(c => ({ ...c, priority: 'secondary' }));
    }

    // Check if already added
    const existing = updatedCohorts.find(c => c.cohort_id === cohortId);
    if (existing) {
      updatedCohorts = updatedCohorts.map(c =>
        c.cohort_id === cohortId ? { ...c, priority } : c
      );
    } else {
      updatedCohorts.push({
        cohort_id: cohortId,
        priority,
        journey_stage_current: 'problem_aware',
        journey_stage_target: 'product_aware',
      });
    }

    updateCampaign({ target_cohorts: updatedCohorts });
  };

  const removeCohort = (cohortId) => {
    updateCampaign({
      target_cohorts: campaign.target_cohorts.filter(c => c.cohort_id !== cohortId)
    });
  };

  const handleSave = async () => {
    setSaving(true);
    // TODO: Implement actual save
    await new Promise(resolve => setTimeout(resolve, 1000));
    setSaving(false);
    navigate('/campaigns');
  };

  // ==========================================================================
  // RENDER
  // ==========================================================================

  return (
    <motion.div
      className="min-h-screen bg-neutral-50"
      initial="initial"
      animate="animate"
      exit="exit"
      variants={pageTransition}
    >
      {/* Header */}
      <div className="border-b border-neutral-200 bg-white sticky top-0 z-20">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <Link
                to="/campaigns"
                className="flex items-center gap-2 text-neutral-500 hover:text-neutral-900 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
              </Link>
              <div className="h-6 w-px bg-neutral-200" />
              <div>
                <LuxeHeading level={4} className="text-lg">
                  {isEditing ? 'Edit Campaign' : 'New Campaign'}
                </LuxeHeading>
                <p className="text-xs text-neutral-500">
                  Step {currentStep} of {totalSteps}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* Progress indicator */}
              <div className="hidden md:flex items-center gap-2">
                <div className="w-32 h-2 bg-neutral-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-neutral-900 transition-all duration-500"
                    style={{ width: `${overallProgress}%` }}
                  />
                </div>
                <span className="text-xs text-neutral-500">{Math.round(overallProgress)}%</span>
              </div>

              <LuxeButton
                onClick={handleSave}
                isLoading={saving}
                icon={Save}
              >
                Save Draft
              </LuxeButton>
            </div>
          </div>

          {/* Step indicators */}
          <div className="flex gap-1 overflow-x-auto pb-2 scrollbar-hide">
            {[
              { step: 1, label: 'Strategy' },
              { step: 2, label: 'Objective' },
              { step: 3, label: 'Cohorts' },
              { step: 4, label: 'Channels' },
              { step: 5, label: 'Launch' },
            ].map(({ step, label }) => (
              <button
                key={step}
                onClick={() => setCurrentStep(step)}
                className={cn(
                  "flex-1 py-2 px-3 text-xs font-medium rounded-lg transition-colors flex items-center justify-center gap-1.5 whitespace-nowrap",
                  currentStep === step
                    ? "bg-neutral-900 text-white shadow-md"
                    : stepValidation[step]
                      ? "bg-green-50 text-green-700 border border-green-200"
                      : "bg-transparent text-neutral-500 hover:bg-neutral-100"
                )}
              >
                {label}
                {stepValidation[step] && currentStep !== step && (
                  <CheckCircle2 className="w-3 h-3 inline ml-1" />
                )}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-6 py-8">
        <AnimatePresence mode="wait">
          {/* Step 1: Strategic Foundation */}
          {currentStep === 1 && (
            <motion.div
              key="step1"
              variants={staggerContainer}
              initial="hidden"
              animate="show"
              exit="hidden"
              className="space-y-8"
            >
              <motion.div variants={fadeInUp}>
                <LuxeHeading level={2}>Strategic Foundation</LuxeHeading>
                <p className="text-neutral-600">Link this campaign to your positioning and message architecture.</p>
              </motion.div>

              {/* Positioning Selection */}
              <motion.div variants={fadeInUp}>
                <LuxeCard className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="font-semibold text-neutral-900">Positioning Statement</h3>
                      <p className="text-sm text-neutral-500">The strategic foundation for this campaign</p>
                    </div>
                    <Link to="/strategy/positioning" className="text-sm text-neutral-500 hover:text-neutral-900">
                      Edit →
                    </Link>
                  </div>

                  <div className="bg-neutral-50 rounded-lg p-4 border border-neutral-100">
                    <p className="font-serif text-neutral-900 leading-relaxed">
                      {MOCK_POSITIONING.category_frame} {MOCK_POSITIONING.differentiator}, {MOCK_POSITIONING.reason_to_believe}.
                    </p>
                  </div>

                  <div className="mt-4 flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                    <span className="text-sm text-green-700">Positioning linked</span>
                  </div>
                </LuxeCard>
              </motion.div>

              {/* Message Architecture Selection */}
              <motion.div variants={fadeInUp}>
                <LuxeCard className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="font-semibold text-neutral-900">Message Architecture</h3>
                      <p className="text-sm text-neutral-500">The message hierarchy for campaign content</p>
                    </div>
                    <Link to="/strategy/positioning" className="text-sm text-neutral-500 hover:text-neutral-900">
                      Edit →
                    </Link>
                  </div>

                  <div className="space-y-3">
                    <div className="bg-neutral-900 text-white rounded-lg p-4 shadow-sm">
                      <span className="text-xs uppercase tracking-wider text-neutral-400">Primary Claim</span>
                      <p className="font-semibold mt-1 text-lg">{MOCK_MESSAGE_ARCH.primary_claim}</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                      {MOCK_MESSAGE_ARCH.proof_points.map((pp, i) => (
                        <div key={pp.id} className="bg-neutral-50 rounded-lg p-3 border border-neutral-100">
                          <span className="text-xs text-neutral-500">Proof Point {i + 1}</span>
                          <p className="text-sm font-medium text-neutral-900 mt-1">{pp.claim}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="mt-4 flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                    <span className="text-sm text-green-700">Message architecture linked</span>
                  </div>
                </LuxeCard>
              </motion.div>
            </motion.div>
          )}

          {/* Step 2: Objective */}
          {currentStep === 2 && (
            <motion.div
              key="step2"
              variants={staggerContainer}
              initial="hidden"
              animate="show"
              exit="hidden"
              className="space-y-8"
            >
              <motion.div variants={fadeInUp}>
                <LuxeHeading level={2}>Campaign Objective</LuxeHeading>
                <p className="text-neutral-600">Define what this campaign should achieve.</p>
              </motion.div>

              {/* Objective Selection */}
              <motion.div variants={fadeInUp} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {CAMPAIGN_OBJECTIVES.map((obj) => {
                  const Icon = obj.icon;
                  const isSelected = campaign.objective === obj.id;

                  return (
                    <LuxeCard
                      key={obj.id}
                      onClick={() => updateCampaign({
                        objective: obj.id,
                        primary_metric: obj.metrics[0]
                      })}
                      className={cn(
                        "cursor-pointer transition-all",
                        isSelected
                          ? "ring-2 ring-neutral-900 bg-neutral-50"
                          : "hover:border-neutral-400"
                      )}
                    >
                      <div className={cn(
                        "w-10 h-10 rounded-lg flex items-center justify-center mb-3 transition-colors",
                        isSelected ? "bg-neutral-900 text-white" : "bg-neutral-100 text-neutral-600"
                      )}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <h3 className="font-semibold text-neutral-900 mb-1">{obj.label}</h3>
                      <p className="text-sm text-neutral-600 mb-3">{obj.description}</p>
                      <div className="flex items-center gap-2 text-xs text-neutral-500">
                        <Clock className="w-3 h-3" />
                        {obj.recommended_duration}
                      </div>
                    </LuxeCard>
                  );
                })}
              </motion.div>

              {/* Objective Statement */}
              {campaign.objective && (
                <motion.div variants={fadeInUp}>
                  <LuxeCard className="p-6 space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-2">
                        Objective Statement
                      </label>
                      <textarea
                        value={campaign.objective_statement}
                        onChange={(e) => updateCampaign({ objective_statement: e.target.value })}
                        placeholder={`e.g., "Increase demo requests from Enterprise CTOs by 40% in Q1"`}
                        rows={2}
                        className="w-full px-4 py-3 border border-neutral-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-neutral-900 resize-none bg-neutral-50"
                      />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-neutral-700 mb-2">
                          Primary Metric
                        </label>
                        <select
                          value={campaign.primary_metric}
                          onChange={(e) => updateCampaign({ primary_metric: e.target.value })}
                          className="w-full px-4 py-3 border border-neutral-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-neutral-900 bg-neutral-50"
                        >
                          {CAMPAIGN_OBJECTIVES.find(o => o.id === campaign.objective)?.metrics.map(m => (
                            <option key={m} value={m}>{m}</option>
                          ))}
                        </select>
                      </div>

                      <LuxeInput
                        label="Target Value"
                        value={campaign.target_value}
                        onChange={(e) => updateCampaign({ target_value: e.target.value })}
                        placeholder="e.g., 50 demos, 1000 signups"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-2">
                        Success Definition
                      </label>
                      <textarea
                        value={campaign.success_definition}
                        onChange={(e) => updateCampaign({ success_definition: e.target.value })}
                        placeholder="What does winning look like? How will you know this campaign succeeded?"
                        rows={2}
                        className="w-full px-4 py-3 border border-neutral-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-neutral-900 resize-none bg-neutral-50"
                      />
                    </div>
                  </LuxeCard>
                </motion.div>
              )}
            </motion.div>
          )}

          {/* Step 3: Target Cohorts */}
          {currentStep === 3 && (
            <motion.div
              key="step3"
              variants={staggerContainer}
              initial="hidden"
              animate="show"
              exit="hidden"
              className="space-y-8"
            >
              <motion.div variants={fadeInUp}>
                <LuxeHeading level={2}>Target Cohorts</LuxeHeading>
                <p className="text-neutral-600">Select the cohorts this campaign will target and define journey goals.</p>
              </motion.div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Available Cohorts */}
                <motion.div variants={fadeInUp}>
                  <h3 className="font-semibold text-neutral-900 mb-4">Available Cohorts</h3>
                  <div className="space-y-3">
                    {MOCK_COHORTS.map((cohort) => {
                      const isAdded = campaign.target_cohorts.some(c => c.cohort_id === cohort.id);
                      const targetCohort = campaign.target_cohorts.find(c => c.cohort_id === cohort.id);

                      return (
                        <LuxeCard
                          key={cohort.id}
                          className={cn(
                            "p-4 transition-all",
                            isAdded ? "ring-2 ring-neutral-900 bg-neutral-50" : ""
                          )}
                        >
                          <div className="flex items-start justify-between mb-3">
                            <div>
                              <div className="flex items-center gap-2">
                                <h4 className="font-semibold text-neutral-900">{cohort.name}</h4>
                                {targetCohort?.priority === 'primary' && (
                                  <LuxeBadge variant="dark">PRIMARY</LuxeBadge>
                                )}
                              </div>
                              <p className="text-sm text-neutral-600">{cohort.description}</p>
                            </div>
                            <LuxeBadge variant={
                              cohort.health_score >= 80 ? "dark" :
                                cohort.health_score >= 60 ? "neutral" : "danger"
                            }>
                              {cohort.health_score}% health
                            </LuxeBadge>
                          </div>

                          {!isAdded ? (
                            <div className="flex gap-2 mt-4">
                              <LuxeButton
                                size="sm"
                                onClick={() => addCohort(cohort.id, 'primary')}
                                className="flex-1"
                              >
                                Add as Primary
                              </LuxeButton>
                              <LuxeButton
                                size="sm"
                                variant="secondary"
                                onClick={() => addCohort(cohort.id, 'secondary')}
                                className="flex-1"
                              >
                                Add as Secondary
                              </LuxeButton>
                            </div>
                          ) : (
                            <LuxeButton
                              size="sm"
                              variant="danger"
                              onClick={() => removeCohort(cohort.id)}
                              className="w-full mt-4"
                            >
                              Remove
                            </LuxeButton>
                          )}
                        </LuxeCard>
                      );
                    })}
                  </div>
                </motion.div>

                {/* Selected Cohorts with Journey Configuration */}
                <motion.div variants={fadeInUp}>
                  <h3 className="font-semibold text-neutral-900 mb-4">Journey Configuration</h3>
                  {campaign.target_cohorts.length === 0 ? (
                    <div className="border-2 border-dashed border-neutral-200 rounded-xl p-8 text-center bg-neutral-50/50">
                      <Users className="w-8 h-8 text-neutral-300 mx-auto mb-3" />
                      <p className="text-neutral-500 text-sm">Select cohorts to configure their journey goals</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {campaign.target_cohorts.map((tc) => {
                        const cohort = MOCK_COHORTS.find(c => c.id === tc.cohort_id);
                        if (!cohort) return null;

                        return (
                          <LuxeCard key={tc.cohort_id} className="p-4">
                            <div className="flex items-center justify-between mb-4">
                              <div className="flex items-center gap-2">
                                <h4 className="font-semibold text-neutral-900">{cohort.name}</h4>
                                {tc.priority === 'primary' && <LuxeBadge variant="dark">PRIMARY</LuxeBadge>}
                              </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                              <div>
                                <label className="text-xs font-bold uppercase tracking-wider text-neutral-500 mb-1 block">From Stage</label>
                                <select className="w-full px-3 py-2 border border-neutral-200 rounded-lg text-sm bg-neutral-50">
                                  <option>Problem Aware</option>
                                </select>
                              </div>
                              <div>
                                <label className="text-xs font-bold uppercase tracking-wider text-neutral-500 mb-1 block">To Stage</label>
                                <select className="w-full px-3 py-2 border border-neutral-200 rounded-lg text-sm bg-neutral-50">
                                  <option>Solution Aware</option>
                                </select>
                              </div>
                            </div>
                          </LuxeCard>
                        );
                      })}
                    </div>
                  )}
                </motion.div>
              </div>
            </motion.div>
          )}

          {/* Placeholder for other steps */}
          {currentStep > 3 && (
            <motion.div
              key="placeholder"
              variants={fadeInUp}
              initial="hidden"
              animate="show"
              exit="hidden"
              className="text-center py-12"
            >
              <LuxeHeading level={2}>Coming Soon</LuxeHeading>
              <p className="text-neutral-600">Steps 4 and 5 are under construction in this Luxe refactor.</p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Navigation */}
        <div className="flex justify-between mt-8 pt-6 border-t border-neutral-200">
          <LuxeButton
            variant="ghost"
            onClick={() => setCurrentStep(prev => Math.max(1, prev - 1))}
            disabled={currentStep === 1}
            icon={ArrowLeft}
          >
            Previous
          </LuxeButton>

          {currentStep < 5 && (
            <LuxeButton
              onClick={() => setCurrentStep(prev => Math.min(totalSteps, prev + 1))}
              disabled={!canProceed}
              icon={ArrowLeft}
              className="flex-row-reverse" // Hack to put icon on right
            >
              Next
            </LuxeButton>
          )}
        </div>
      </div>
    </motion.div>
  );
}