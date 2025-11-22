import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, ArrowRight, ArrowLeft, CheckCircle2, Target,
  TrendingUp, Zap, MapPin, DollarSign, Shield, Rocket, Building2, Loader2
} from 'lucide-react';
import { cn } from '../utils/cn';
import { strategyService } from '../lib/services/strategy-service';
import { MoveService } from '../lib/services/move-service';
import { sprintService } from '../lib/services/sprint-service';
import { 
  Step4Markets, 
  Step5CenterOfGravity, 
  Step6Goal, 
  Step7Constitution, 
  Step8Launch 
} from './StrategyWizardSteps';

const steps = [
  { id: 1, title: 'Welcome', description: 'Set the foundation', icon: Sparkles },
  { id: 2, title: 'Business Context', description: 'Tell us about your business', icon: Building2 },
  { id: 3, title: 'Offers', description: 'What do you sell?', icon: DollarSign },
  { id: 4, title: 'Markets & Channels', description: 'Where do you play?', icon: MapPin },
  { id: 5, title: 'Center of Gravity', description: 'Your strategic focus', icon: Target },
  { id: 6, title: '90-Day Goal', description: 'What does success look like?', icon: TrendingUp },
  { id: 7, title: 'Constitution', description: 'Your operational rules', icon: Shield },
  { id: 8, title: 'Launch', description: 'Your campaign awaits', icon: Rocket },
];

const INDUSTRIES = [
  'SaaS', 'E-commerce', 'Healthcare', 'Finance', 'Education',
  'Manufacturing', 'Retail', 'Real Estate', 'Consulting', 'Marketing',
  'Technology', 'Media', 'Other'
];

const COMPANY_STAGES = [
  'Pre-launch', 'Launch', 'Early Growth', 'Growth', 'Scale', 'Mature'
];

const TEAM_SIZES = [
  '1 (Solo)', '2-5', '6-10', '11-25', '26-50', '51-100', '100+'
];

const CHANNELS = [
  'Email', 'LinkedIn', 'Twitter/X', 'Instagram', 'Facebook', 
  'Events', 'Webinars', 'Content Marketing', 'SEO', 'Paid Ads',
  'Partnerships', 'Referrals', 'Cold Outreach', 'Other'
];

// Step 1: Welcome
const Step1Welcome = ({ onNext }) => {
  return (
    <div className="w-full max-w-4xl mx-auto text-center animate-in fade-in slide-in-from-bottom-12 duration-1000">
      <div className="mb-12">
        <Sparkles className="w-20 h-20 mx-auto mb-8 text-neutral-900" strokeWidth={1.5} />
        <h1 className="font-serif text-6xl md:text-7xl mb-6 text-neutral-900 tracking-tight">
          Strategy<br />Wizard
        </h1>
        <p className="text-xl text-neutral-600 max-w-2xl mx-auto leading-relaxed">
          In the next <strong>30 minutes</strong>, we'll craft your complete strategy execution framework. 
          No buzzwords. No fluff. Just a battle-tested system for turning strategy into results.
        </p>
      </div>

      <div className="runway-card p-8 max-w-2xl mx-auto text-left mb-8">
        <h3 className="font-serif text-2xl mb-6">What we'll build together:</h3>
        <div className="space-y-4">
          <div className="flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-neutral-500 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-semibold text-neutral-900">Your Strategic Position</p>
              <p className="text-sm text-neutral-600">Market positioning, center of gravity, and competitive stance</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-neutral-500 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-semibold text-neutral-900">90-Day Campaign</p>
              <p className="text-sm text-neutral-600">Clear goal, initial moves, and execution framework</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-neutral-500 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-semibold text-neutral-900">Operational Constitution</p>
              <p className="text-sm text-neutral-600">Rules of engagement, brand guidelines, constraints</p>
            </div>
          </div>
        </div>
      </div>

      <button
        onClick={onNext}
        className="runway-button-primary px-8 py-4 text-lg"
      >
        Begin Strategy Session
        <ArrowRight className="w-5 h-5 ml-2" />
      </button>
    </div>
  );
};

// Step 2: Business Context
const Step2BusinessContext = ({ data, onChange, onNext, onBack }) => {
  const [errors, setErrors] = useState({});

  const validate = () => {
    const newErrors = {};
    if (!data.company_name) newErrors.company_name = 'Required';
    if (!data.industry) newErrors.industry = 'Required';
    if (!data.stage) newErrors.stage = 'Required';
    if (!data.team_size) newErrors.team_size = 'Required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validate()) {
      onNext();
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div className="mb-8">
        <h2 className="font-serif text-4xl mb-3">Business Context</h2>
        <p className="text-neutral-600">Let's start with the basics</p>
      </div>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-semibold text-neutral-900 mb-2">
            Company Name
          </label>
          <input
            type="text"
            value={data.company_name || ''}
            onChange={(e) => onChange({ company_name: e.target.value })}
            className={cn(
              "w-full px-4 py-3 border-2 border-neutral-200 rounded-lg focus:outline-none focus:border-neutral-900 transition-colors",
              errors.company_name && "border-red-500"
            )}
            placeholder="Acme Inc."
          />
          {errors.company_name && (
            <p className="text-sm text-red-600 mt-1">{errors.company_name}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-semibold text-neutral-900 mb-2">
            Industry
          </label>
          <select
            value={data.industry || ''}
            onChange={(e) => onChange({ industry: e.target.value })}
            className={cn(
              "w-full px-4 py-3 border-2 border-neutral-200 rounded-lg focus:outline-none focus:border-neutral-900 transition-colors",
              errors.industry && "border-red-500"
            )}
          >
            <option value="">Select industry...</option>
            {INDUSTRIES.map(ind => (
              <option key={ind} value={ind}>{ind}</option>
            ))}
          </select>
          {errors.industry && (
            <p className="text-sm text-red-600 mt-1">{errors.industry}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-semibold text-neutral-900 mb-2">
            Stage
          </label>
          <select
            value={data.stage || ''}
            onChange={(e) => onChange({ stage: e.target.value })}
            className={cn(
              "w-full px-4 py-3 border-2 border-neutral-200 rounded-lg focus:outline-none focus:border-neutral-900 transition-colors",
              errors.stage && "border-red-500"
            )}
          >
            <option value="">Select stage...</option>
            {COMPANY_STAGES.map(stage => (
              <option key={stage} value={stage}>{stage}</option>
            ))}
          </select>
          {errors.stage && (
            <p className="text-sm text-red-600 mt-1">{errors.stage}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-semibold text-neutral-900 mb-2">
            Team Size
          </label>
          <select
            value={data.team_size || ''}
            onChange={(e) => onChange({ team_size: e.target.value })}
            className={cn(
              "w-full px-4 py-3 border-2 border-neutral-200 rounded-lg focus:outline-none focus:border-neutral-900 transition-colors",
              errors.team_size && "border-red-500"
            )}
          >
            <option value="">Select team size...</option>
            {TEAM_SIZES.map(size => (
              <option key={size} value={size}>{size}</option>
            ))}
          </select>
          {errors.team_size && (
            <p className="text-sm text-red-600 mt-1">{errors.team_size}</p>
          )}
        </div>
      </div>

      <div className="flex gap-3 mt-8">
        <button onClick={onBack} className="runway-button-secondary px-6 py-3">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </button>
        <button onClick={handleNext} className="runway-button-primary px-6 py-3 flex-1">
          Continue
          <ArrowRight className="w-4 h-4 ml-2" />
        </button>
      </div>
    </div>
  );
};

// Step 3: Offers
const Step3Offers = ({ data, onChange, onNext, onBack }) => {
  const [offers, setOffers] = useState(data.offers || []);
  const [newOffer, setNewOffer] = useState({
    name: '',
    description: '',
    pricing: '',
    target_segment: ''
  });

  const addOffer = () => {
    if (newOffer.name && newOffer.description) {
      const updated = [...offers, newOffer];
      setOffers(updated);
      onChange({ offers: updated });
      setNewOffer({ name: '', description: '', pricing: '', target_segment: '' });
    }
  };

  const removeOffer = (index) => {
    const updated = offers.filter((_, i) => i !== index);
    setOffers(updated);
    onChange({ offers: updated });
  };

  const handleNext = () => {
    if (offers.length > 0) {
      onNext();
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div className="mb-8">
        <h2 className="font-serif text-4xl mb-3">Your Offers</h2>
        <p className="text-neutral-600">What products or services do you provide?</p>
      </div>

      {/* Existing offers */}
      {offers.length > 0 && (
        <div className="space-y-3 mb-6">
          {offers.map((offer, index) => (
            <div key={index} className="runway-card p-4 flex items-start justify-between">
              <div className="flex-1">
                <h4 className="font-semibold text-neutral-900">{offer.name}</h4>
                <p className="text-sm text-neutral-600">{offer.description}</p>
                {offer.pricing && (
                  <p className="text-xs text-neutral-500 mt-1">Pricing: {offer.pricing}</p>
                )}
              </div>
              <button
                onClick={() => removeOffer(index)}
                className="text-neutral-400 hover:text-red-600 ml-4"
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Add new offer form */}
      <div className="runway-card p-6 mb-8">
        <h4 className="font-semibold mb-4">Add Offer</h4>
        <div className="space-y-4">
          <input
            type="text"
            value={newOffer.name}
            onChange={(e) => setNewOffer({ ...newOffer, name: e.target.value })}
            placeholder="Offer name"
            className="w-full px-4 py-2 border-2 border-neutral-200 rounded-lg focus:outline-none focus:border-neutral-900"
          />
          <textarea
            value={newOffer.description}
            onChange={(e) => setNewOffer({ ...newOffer, description: e.target.value })}
            placeholder="Brief description"
            rows={2}
            className="w-full px-4 py-2 border-2 border-neutral-200 rounded-lg focus:outline-none focus:border-neutral-900"
          />
          <div className="grid grid-cols-2 gap-4">
            <input
              type="text"
              value={newOffer.pricing}
              onChange={(e) => setNewOffer({ ...newOffer, pricing: e.target.value })}
              placeholder="Pricing (optional)"
              className="px-4 py-2 border-2 border-neutral-200 rounded-lg focus:outline-none focus:border-neutral-900"
            />
            <input
              type="text"
              value={newOffer.target_segment}
              onChange={(e) => setNewOffer({ ...newOffer, target_segment: e.target.value })}
              placeholder="Target segment (optional)"
              className="px-4 py-2 border-2 border-neutral-200 rounded-lg focus:outline-none focus:border-neutral-900"
            />
          </div>
          <button
            onClick={addOffer}
            disabled={!newOffer.name || !newOffer.description}
            className="runway-button-secondary px-4 py-2 w-full disabled:opacity-50"
          >
            Add Offer
          </button>
        </div>
      </div>

      <div className="flex gap-3">
        <button onClick={onBack} className="runway-button-secondary px-6 py-3">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </button>
        <button
          onClick={handleNext}
          disabled={offers.length === 0}
          className="runway-button-primary px-6 py-3 flex-1 disabled:opacity-50"
        >
          Continue
          <ArrowRight className="w-4 h-4 ml-2" />
        </button>
      </div>
    </div>
  );
};

// Export main component
export default function StrategyWizardEnhanced() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [wizardData, setWizardData] = useState({
    business_context: {},
    offers: [],
    markets: [],
    center_of_gravity: '',
    ninety_day_goal: '',
    success_metrics: {},
    constitution: {}
  });

  const updateWizardData = (updates) => {
    setWizardData(prev => {
      if (updates.business_context) {
        return {
          ...prev,
          business_context: { ...prev.business_context, ...updates.business_context }
        };
      }
      return { ...prev, ...updates };
    });
  };

  const handleNext = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleComplete = async () => {
    try {
      setIsSubmitting(true);

      // 1. Create global strategy
      await strategyService.createStrategy({
        ...wizardData,
        strategy_state: 'Active'
      });

      // 2. Create initial Line of Operation
      const moveService = new MoveService();
      await moveService.createLineOfOperation({
        name: 'Foundation',
        strategic_objective: wizardData.ninety_day_goal,
        center_of_gravity: wizardData.center_of_gravity,
        status: 'Active'
      });

      // 3. Create initial Sprint
      const startDate = new Date();
      const endDate = new Date();
      endDate.setDate(endDate.getDate() + 14);
      
      await sprintService.createSprint({
        name: 'Sprint 1 - Ignition',
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
        status: 'Planning',
        capacity_budget: 100
      });

      // 4. Unlock foundation capabilities
      // (Note: These IDs would need to match your seeded capability nodes)
      // await techTreeService.unlockNode('foundation_analytics');
      // await techTreeService.unlockNode('basic_authority_sprint');

      // 5. Navigate to dashboard with completion flag
      navigate('/?onboarding=complete');
    } catch (error) {
      console.error('Error completing strategy wizard:', error);
      alert('Failed to save strategy. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const currentStepData = steps[currentStep - 1];

  return (
    <div className="min-h-screen bg-[var(--cream)] py-8 px-4">
      {/* Progress bar */}
      <div className="max-w-6xl mx-auto mb-12">
        <div className="flex items-center justify-between relative">
          {/* Progress line */}
          <div className="absolute top-6 left-0 right-0 h-0.5 bg-neutral-200" style={{ zIndex: 0 }} />
          <div
            className="absolute top-6 left-0 h-0.5 bg-neutral-900 transition-all duration-500"
            style={{
              width: `${((currentStep - 1) / (steps.length - 1)) * 100}%`,
              zIndex: 0
            }}
          />

          {/* Steps */}
          {steps.map((step, index) => {
            const Icon = step.icon;
            const isCompleted = currentStep > step.id;
            const isCurrent = currentStep === step.id;
            
            return (
              <div key={step.id} className="flex flex-col items-center relative" style={{ zIndex: 1 }}>
                <div
                  className={cn(
                    "w-12 h-12 rounded-full flex items-center justify-center border-2 transition-all bg-white",
                    isCompleted && "bg-neutral-900 border-neutral-900 text-white",
                    isCurrent && "border-neutral-900 bg-white text-neutral-900 shadow-lg",
                    !isCompleted && !isCurrent && "border-neutral-300 bg-white text-neutral-400"
                  )}
                >
                  {isCompleted ? (
                    <CheckCircle2 className="w-6 h-6" />
                  ) : (
                    <Icon className="w-6 h-6" />
                  )}
                </div>
                <div className="mt-2 text-center hidden md:block">
                  <div
                    className={cn(
                      "text-xs font-medium",
                      isCurrent ? "text-neutral-900" : "text-neutral-500"
                    )}
                  >
                    {step.title}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
        >
          {currentStep === 1 && <Step1Welcome onNext={handleNext} />}
          {currentStep === 2 && (
            <Step2BusinessContext
              data={wizardData.business_context}
              onChange={(updates) => updateWizardData({ business_context: updates })}
              onNext={handleNext}
              onBack={handleBack}
            />
          )}
          {currentStep === 3 && (
            <Step3Offers
              data={wizardData}
              onChange={updateWizardData}
              onNext={handleNext}
              onBack={handleBack}
            />
          )}
          {currentStep === 4 && (
            <Step4Markets
              data={wizardData}
              onChange={updateWizardData}
              onNext={handleNext}
              onBack={handleBack}
            />
          )}
          {currentStep === 5 && (
            <Step5CenterOfGravity
              data={wizardData}
              onChange={updateWizardData}
              onNext={handleNext}
              onBack={handleBack}
            />
          )}
          {currentStep === 6 && (
            <Step6Goal
              data={wizardData}
              onChange={updateWizardData}
              onNext={handleNext}
              onBack={handleBack}
            />
          )}
          {currentStep === 7 && (
            <Step7Constitution
              data={wizardData}
              onChange={updateWizardData}
              onNext={handleNext}
              onBack={handleBack}
            />
          )}
          {currentStep === 8 && (
            <Step8Launch
              data={wizardData}
              onComplete={handleComplete}
              onBack={handleBack}
              isSubmitting={isSubmitting}
            />
          )}
        </motion.div>
      </AnimatePresence>

      {isSubmitting && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 flex items-center gap-4">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span>Launching your campaign...</span>
          </div>
        </div>
      )}
    </div>
  );
}
