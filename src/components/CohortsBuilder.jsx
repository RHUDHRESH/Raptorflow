import React, { useState, useEffect, useRef } from 'react';
import {
  ArrowRight,
  ArrowLeft,
  Sparkles,
  Loader2,
  X,
  ChevronDown,
  Check,
  CheckCircle2,
  Target,
  Building2,
  Users,
  MapPin,
  DollarSign,
  Clock,
  MessageSquare,
  Brain,
  TrendingUp,
  AlertCircle,
  Lightbulb,
  Heart,
  Zap,
  Briefcase,
  GraduationCap,
  Rocket,
  Shield,
  BarChart3
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { generateCohortFromInputs, computePsychographics } from '../lib/services/cohorts-api';
import { supabase } from '../lib/supabase';
import { useAuth } from '../context/AuthContext';

// Hat icons representing different archetypes
const HAT_ICONS = [
  { id: 'innovator', label: 'Innovator', icon: Rocket, color: 'blue' },
  { id: 'manager', label: 'Manager', icon: Briefcase, color: 'purple' },
  { id: 'technical', label: 'Technical Lead', icon: Zap, color: 'yellow' },
  { id: 'executive', label: 'Executive', icon: Building2, color: 'green' },
  { id: 'researcher', label: 'Researcher', icon: GraduationCap, color: 'indigo' },
  { id: 'guardian', label: 'Guardian', icon: Shield, color: 'red' },
  { id: 'analyst', label: 'Analyst', icon: BarChart3, color: 'orange' },
];

// Common descriptor tags
const COMMON_DESCRIPTORS = [
  'Growth-focused', 'Cost-conscious', 'Early Adopter', 'Risk-averse',
  'Data-driven', 'Innovation-oriented', 'Efficiency-seeker', 'Quality-focused',
  'Community-driven', 'Sustainability-minded', 'Budget-conscious', 'Speed-oriented'
];

// Industry options
const INDUSTRIES = [
  'SaaS', 'E-commerce', 'Healthcare', 'Finance', 'Education',
  'Manufacturing', 'Retail', 'Real Estate', 'Consulting', 'Other'
];

// Company size ranges
const COMPANY_SIZES = [
  '1-10', '11-50', '51-200', '201-500', '501-1000', '1000+'
];

// Revenue ranges
const REVENUE_RANGES = [
  '$0-$1M', '$1M-$5M', '$5M-$25M', '$25M-$100M', '$100M+'
];

// Buyer roles
const BUYER_ROLES = [
  'Founder/CEO', 'CTO', 'CMO', 'CFO', 'VP of Sales', 'VP of Marketing',
  'Director', 'Manager', 'Individual Contributor', 'Other'
];

// Communication channels
const CHANNELS = [
  'Email', 'LinkedIn', 'Twitter/X', 'Events', 'Webinars', 'Cold Calls',
  'Content Marketing', 'Referrals', 'Partnerships', 'Other'
];

// Grain overlay component
const GrainOverlay = () => (
  <div className="absolute inset-0 pointer-events-none z-0 opacity-[0.03] mix-blend-multiply"
    style={{
      backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='1'/%3E%3C/svg%3E")`
    }}>
  </div>
);

// Step 1: Launch Screen
const Step1Launch = ({ onNext, userProfile, existingCohorts, userPlan, cohortsLimit, currentCohortsCount, canCreate }) => {
  const planName = userPlan.charAt(0).toUpperCase() + userPlan.slice(1);

  return (
    <div className="w-full max-w-4xl mx-auto text-center animate-in fade-in slide-in-from-bottom-12 duration-1000">
      <div className="mb-12">
        {/* Enhanced Icon with Gradient Background */}
        <div className="relative inline-block mb-8">
          <div className="icon-gradient-bg w-24 h-24 rounded-full flex items-center justify-center icon-glow">
            <Target className="w-12 h-12 text-neutral-900" />
          </div>
          <div className="absolute inset-0 rounded-full bg-gradient-to-br from-neutral-900/5 to-transparent pointer-events-none"></div>
        </div>

        {/* Enhanced Typography */}
        <h1 className="font-serif text-5xl md:text-6xl lg:text-7xl mb-6 gradient-text text-shadow-subtle leading-tight tracking-tighter">
          Create Your Ideal Customer Profile
        </h1>
        <p className="text-lg md:text-xl text-neutral-600 max-w-2xl mx-auto mb-10 leading-relaxed">
          A cohort is a detailed description of an ideal-fit company for your product or service.
          Think of it as your perfect customer—the type of business that gets the most value from what you offer.
        </p>

        {/* Glassmorphism Example Card */}
        <div className="glass-card p-6 max-w-xl mx-auto text-left mb-6 rounded-2xl transform hover:scale-[1.02] transition-transform duration-300">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400/20 to-amber-600/20 flex items-center justify-center flex-shrink-0">
              <Lightbulb className="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <p className="text-sm font-bold text-neutral-900 mb-2 tracking-tight">Example</p>
              <p className="text-sm text-neutral-700 leading-relaxed">
                "Mid-market SaaS companies (50–200 employees, $5–25M revenue) with mature customer success teams,
                seeking efficiency and data-driven solutions."
              </p>
            </div>
          </div>
        </div>

        {/* Glassmorphism Plan Info Card */}
        <div className="glass-card p-6 max-w-xl mx-auto mb-6 rounded-2xl">
          <div className="flex items-center justify-between mb-4">
            <div className="text-left">
              <p className="text-sm font-semibold text-neutral-900 tracking-tight">
                Current Plan: <span className="font-bold gradient-text">{planName}</span>
              </p>
              <p className="text-xs text-neutral-500 mt-1.5 tracking-wide">Cohorts Limit: {cohortsLimit}</p>
            </div>
            <div className="text-right">
              <p className="text-sm font-semibold text-neutral-900 tracking-tight">
                {currentCohortsCount} / {cohortsLimit} cohorts
              </p>
              {/* Modern Progress Bar */}
              <div className="w-32 h-3 bg-gradient-to-r from-neutral-100 to-neutral-200 rounded-full mt-2 overflow-hidden shadow-inner">
                <div
                  className="h-full progress-gradient rounded-full transition-all duration-700 ease-out"
                  style={{ width: `${(currentCohortsCount / cohortsLimit) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {!canCreate && (
          <div className="glass-card p-6 max-w-xl mx-auto mb-6 border-2 border-red-300/50 bg-red-50/80 rounded-2xl backdrop-blur-xl">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-xl bg-red-500/10 flex items-center justify-center flex-shrink-0">
                <AlertCircle className="w-5 h-5 text-red-600" />
              </div>
              <div className="text-left">
                <p className="text-sm font-bold text-red-900 mb-1 tracking-tight">Cohorts Limit Reached</p>
                <p className="text-sm text-red-700 leading-relaxed">
                  You've reached your {planName} plan limit of {cohortsLimit} cohorts.
                  Upgrade to {userPlan === 'ascent' ? 'Glide' : 'Soar'} to create more cohorts.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {existingCohorts && existingCohorts.length > 0 && (
        <div className="mb-8 text-sm text-neutral-500 font-medium tracking-wide">
          You have {existingCohorts.length} existing cohort{existingCohorts.length !== 1 ? 's' : ''} in your account.
        </div>
      )}

      {/* Enhanced Button */}
      <button
        onClick={onNext}
        disabled={!canCreate}
        className={`group relative px-16 py-6 overflow-hidden rounded-xl ${canCreate
          ? 'button-enhanced text-white'
          : 'bg-neutral-300 text-neutral-500 cursor-not-allowed'
          }`}
      >
        <div className="relative z-10 flex items-center space-x-4">
          <span className="font-sans text-xs font-bold tracking-widest uppercase">
            {canCreate ? 'Get Started' : 'Limit Reached'}
          </span>
          {canCreate && <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform duration-500" />}
        </div>
        {canCreate && (
          <div className="absolute inset-0 bg-gradient-to-r from-neutral-900 to-neutral-800 transform translate-y-full group-hover:translate-y-0 transition-transform duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"></div>
        )}
      </button>
    </div>
  );
};

// Step 2: Choose Creation Mode
const Step2ModeSelection = ({ onSelect, userPreferences, onBack }) => {
  const [selectedMode, setSelectedMode] = useState(userPreferences?.preferredMode || null);

  const handleSelect = (mode) => {
    setSelectedMode(mode);
    setTimeout(() => onSelect(mode), 300);
  };

  return (
    <div className="w-full max-w-5xl mx-auto animate-in fade-in slide-in-from-bottom-12 duration-1000">
      <div className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl mb-4 text-neutral-900">How would you like to create your cohort?</h2>
        <p className="text-neutral-600">Choose your preferred method</p>
      </div>

      <div className="grid md:grid-cols-2 gap-8 mb-12">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => handleSelect('ai')}
          className={`runway-card p-8 text-left cursor-pointer transition-all ${selectedMode === 'ai'
            ? 'ring-2 ring-black shadow-xl'
            : 'hover:shadow-xl'
            }`}
        >
          <div className="flex items-start gap-4 mb-4">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${selectedMode === 'ai' ? 'bg-black text-white' : 'bg-neutral-100 text-neutral-900'
              }`}>
              <Sparkles className="w-6 h-6" />
            </div>
            <div className="flex-1">
              <h3 className="text-2xl font-bold text-neutral-900 mb-2">Auto-generate with AI</h3>
              <p className="text-neutral-600 text-sm">
                Let AI analyze your business and customer data to generate a comprehensive cohort automatically.
              </p>
            </div>
          </div>
          <div className="mt-6 pt-6 border-t border-neutral-200">
            <ul className="space-y-2 text-sm text-neutral-600">
              <li className="flex items-center gap-2">
                <Check className="w-4 h-4 text-green-600" />
                Analyzes your existing customer data
              </li>
              <li className="flex items-center gap-2">
                <Check className="w-4 h-4 text-green-600" />
                Identifies patterns and psychographics
              </li>
              <li className="flex items-center gap-2">
                <Check className="w-4 h-4 text-green-600" />
                Faster setup, typically 2-3 minutes
              </li>
            </ul>
          </div>
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => handleSelect('manual')}
          className={`runway-card p-8 text-left cursor-pointer transition-all ${selectedMode === 'manual'
            ? 'ring-2 ring-black shadow-xl'
            : 'hover:shadow-xl'
            }`}
        >
          <div className="flex items-start gap-4 mb-4">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${selectedMode === 'manual' ? 'bg-black text-white' : 'bg-neutral-100 text-neutral-900'
              }`}>
              <Users className="w-6 h-6" />
            </div>
            <div className="flex-1">
              <h3 className="text-2xl font-bold text-neutral-900 mb-2">Build Manually</h3>
              <p className="text-neutral-600 text-sm">
                Use our guided builder to create a custom cohort step-by-step with full control.
              </p>
            </div>
          </div>
          <div className="mt-6 pt-6 border-t border-neutral-200">
            <ul className="space-y-2 text-sm text-neutral-600">
              <li className="flex items-center gap-2">
                <Check className="w-4 h-4 text-green-600" />
                Complete control over every detail
              </li>
              <li className="flex items-center gap-2">
                <Check className="w-4 h-4 text-green-600" />
                Visual builder with intuitive tools
              </li>
              <li className="flex items-center gap-2">
                <Check className="w-4 h-4 text-green-600" />
                Perfect for specific requirements
              </li>
            </ul>
          </div>
        </motion.button>
      </div>

      <div className="flex justify-center">
        <button
          onClick={onBack}
          className="text-neutral-500 hover:text-black text-sm font-medium transition-colors flex items-center gap-2"
        >
          <ArrowLeft size={16} />
          Back
        </button>
      </div>
    </div>
  );
};

// Step 3: Initial Inputs (AI Path)
const Step3AIInputs = ({ onSubmit, initialData, onBack }) => {
  const [inputs, setInputs] = useState({
    businessDescription: initialData?.businessDescription || '',
    productDescription: initialData?.productDescription || '',
    targetMarket: initialData?.targetMarket || '',
    valueProposition: initialData?.valueProposition || '',
    topCustomers: initialData?.topCustomers || '',
  });

  const handleChange = (field, value) => {
    setInputs(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="w-full max-w-3xl mx-auto animate-in fade-in slide-in-from-bottom-12 duration-1000">
      <div className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl mb-4 text-neutral-900">Tell us about your business</h2>
        <p className="text-neutral-600">The more detail you provide, the better we can generate your cohort</p>
      </div>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-neutral-700 mb-2">
            What does your business do?
          </label>
          <textarea
            value={inputs.businessDescription}
            onChange={(e) => handleChange('businessDescription', e.target.value)}
            placeholder="e.g., We provide cloud-based project management software for remote teams..."
            rows={3}
            className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900 resize-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-neutral-700 mb-2">
            Describe your product or service
          </label>
          <textarea
            value={inputs.productDescription}
            onChange={(e) => handleChange('productDescription', e.target.value)}
            placeholder="Key features, benefits, and what makes it unique..."
            rows={3}
            className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900 resize-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-neutral-700 mb-2">
            Who is your target market?
          </label>
          <textarea
            value={inputs.targetMarket}
            onChange={(e) => handleChange('targetMarket', e.target.value)}
            placeholder="e.g., Small to medium-sized SaaS companies, E-commerce businesses..."
            rows={2}
            className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900 resize-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-neutral-700 mb-2">
            What's your value proposition?
          </label>
          <textarea
            value={inputs.valueProposition}
            onChange={(e) => handleChange('valueProposition', e.target.value)}
            placeholder="What problem do you solve? Why do customers choose you?"
            rows={2}
            className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900 resize-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-neutral-700 mb-2">
            Describe your top 2-3 customers (optional)
          </label>
          <textarea
            value={inputs.topCustomers}
            onChange={(e) => handleChange('topCustomers', e.target.value)}
            placeholder="e.g., A SaaS company with 150 employees that values efficiency and data-driven decisions..."
            rows={3}
            className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900 resize-none"
          />
        </div>
      </div>

      <div className="mt-12 flex justify-between items-center">
        <button
          onClick={onBack}
          className="text-neutral-500 hover:text-black text-sm font-medium transition-colors flex items-center gap-2"
        >
          <ArrowLeft size={16} />
          Back
        </button>
        <button
          onClick={() => onSubmit(inputs)}
          disabled={!inputs.businessDescription.trim()}
          className="group relative bg-black text-white px-12 py-4 overflow-hidden transition-all duration-500 hover:shadow-2xl hover:shadow-neutral-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <div className="relative z-10 flex items-center space-x-4">
            <span className="font-sans text-xs font-bold tracking-widest uppercase">
              Generate cohort
            </span>
            <Sparkles size={14} className="group-hover:rotate-12 transition-transform duration-500" />
          </div>
          <div className="absolute inset-0 bg-neutral-800 transform translate-y-full group-hover:translate-y-0 transition-transform duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"></div>
        </button>
      </div>
    </div>
  );
};

// Step 4: AI Analysis & Suggestions
const Step4AIGeneration = ({ inputs, onComplete, onBack }) => {
  const [status, setStatus] = useState('analyzing'); // 'analyzing' | 'suggestions' | 'error'
  const [suggestions, setSuggestions] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Real AI analysis
    const analyzeData = async () => {
      setStatus('analyzing');
      setError(null);

      try {
        // Generate suggestions using Vertex AI via our service
        const { suggestCohorts } = await import('../lib/services/cohorts-api');
        const results = await suggestCohorts(inputs);

        if (!results || results.length === 0) {
          // If no suggestions, fallback to generating a single cohort directly
          // This handles cases where the suggestion endpoint might fail or return empty
          const { generateCohortFromInputs } = await import('../lib/services/cohorts-api');
          const generated = await generateCohortFromInputs(inputs);

          const sanitized = {
            ...generated,
            demographics: generated.demographics || { companySize: 'Unknown', industry: 'Unknown', revenue: 'Unknown', location: 'Unknown' },
            psychographics: generated.psychographics || { values: [], decisionStyle: '', priorities: [] },
            painPoints: generated.painPoints || [],
            goals: generated.goals || [],
            behavioralTriggers: generated.behavioralTriggers || [],
            communication: generated.communication || { channels: [], tone: '', format: '' }
          };

          onComplete(sanitized);
          return;
        }

        setSuggestions(results);
        setStatus('suggestions');
      } catch (err) {
        console.error("AI Generation Error:", err);
        setError("Failed to generate suggestions. Please try again or build manually.");
        setStatus('error');
      }
    };

    analyzeData();
  }, [inputs]);

  const handleSelectSuggestion = async (suggestion) => {
    setStatus('analyzing'); // Show loading while generating full profile
    try {
      const { generateCohortFromInputs } = await import('../lib/services/cohorts-api');
      // Combine original inputs with the selected suggestion for a targeted generation
      const refinedInputs = {
        ...inputs,
        targetMarket: suggestion.name,
        valueProposition: `${inputs.valueProposition}. Focus on: ${suggestion.reasoning}`
      };

      const generated = await generateCohortFromInputs(refinedInputs);

      // Ensure we have valid data structures
      const sanitized = {
        ...generated,
        name: suggestion.name, // Use the suggested name
        executiveSummary: generated.executiveSummary || suggestion.description,
        demographics: generated.demographics || { companySize: 'Unknown', industry: 'Unknown', revenue: 'Unknown', location: 'Unknown' },
        psychographics: generated.psychographics || { values: [], decisionStyle: '', priorities: [] },
        painPoints: generated.painPoints || [],
        goals: generated.goals || [],
        behavioralTriggers: generated.behavioralTriggers || [],
        communication: generated.communication || { channels: [], tone: '', format: '' }
      };

      onComplete(sanitized);
    } catch (err) {
      console.error("Full Profile Generation Error:", err);
      setError("Failed to generate full profile. Please try again.");
      setStatus('error');
    }
  };

  if (status === 'error') {
    return (
      <div className="w-full max-w-3xl mx-auto text-center animate-in fade-in duration-1000">
        <AlertCircle className="text-red-500 mx-auto mb-6" size={48} />
        <div className="space-y-4">
          <p className="font-serif text-2xl italic text-red-900">Generation Failed</p>
          <p className="text-neutral-600">
            {error}
          </p>
          <div className="flex justify-center gap-4">
            <button onClick={onBack} className="px-6 py-2 border border-black rounded-lg hover:bg-neutral-50">
              Go Back
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (status === 'analyzing') {
    return (
      <div className="w-full max-w-3xl mx-auto text-center animate-in fade-in duration-1000">
        <Loader2 className="animate-spin text-black mx-auto mb-6" size={48} />
        <div className="space-y-2">
          <p className="font-serif text-2xl italic">Analyzing your inputs...</p>
          <p className="font-sans text-[10px] uppercase tracking-widest text-neutral-400">
            Using AI to identify the best cohorts for you
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-5xl mx-auto animate-in fade-in slide-in-from-bottom-12 duration-1000">
      <div className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl mb-4 text-neutral-900">We found 3 high-potential cohorts</h2>
        <p className="text-neutral-600">Select the one you want to target first.</p>
      </div>

      <div className="grid md:grid-cols-3 gap-6 mb-12">
        {suggestions.map((suggestion, idx) => (
          <motion.div
            key={idx}
            whileHover={{ y: -5 }}
            className="group relative flex flex-col h-full"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-neutral-100 to-white rounded-2xl transform rotate-1 group-hover:rotate-2 transition-transform duration-300"></div>
            <div className="relative flex-1 bg-white border border-neutral-200 p-8 rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col">
              <div className="w-12 h-12 bg-black text-white rounded-xl flex items-center justify-center mb-6 text-xl font-serif">
                {idx + 1}
              </div>

              <h3 className="text-xl font-bold text-neutral-900 mb-3">{suggestion.name}</h3>
              <p className="text-sm text-neutral-600 mb-6 flex-1 leading-relaxed">
                {suggestion.description}
              </p>

              <div className="bg-neutral-50 p-4 rounded-lg mb-6">
                <p className="text-xs font-bold uppercase tracking-widest text-neutral-500 mb-2">Why this works</p>
                <p className="text-xs text-neutral-700 italic">"{suggestion.reasoning}"</p>
              </div>

              <button
                onClick={() => handleSelectSuggestion(suggestion)}
                className="w-full py-3 bg-white border-2 border-black text-black font-bold text-sm uppercase tracking-wider hover:bg-black hover:text-white transition-colors rounded-lg"
              >
                Select Cohort
              </button>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="flex justify-center">
        <button
          onClick={onBack}
          className="text-neutral-500 hover:text-black text-sm font-medium transition-colors flex items-center gap-2"
        >
          <ArrowLeft size={16} />
          Back to Inputs
        </button>
      </div>
    </div>
  );
};

// Step 5: Review and Refine
const Step5ReviewRefine = ({ draftCohort, onComplete, onBack, userPreferences }) => {
  const [cohort, setCohort] = useState(draftCohort || {
    name: '',
    executiveSummary: '',
    demographics: { companySize: '', industry: '', revenue: '', location: '' },
    buyerRole: '',
    psychographics: { values: [], decisionStyle: '', priorities: [] },
    painPoints: [],
    goals: [],
    behavioralTriggers: [],
    communication: { channels: [], tone: '', format: '' },
    budget: '',
    timeline: '',
    decisionStructure: ''
  });

  const [activePanel, setActivePanel] = useState('demographics');
  const [newPainPoint, setNewPainPoint] = useState('');
  const [newGoal, setNewGoal] = useState('');
  const [newTrigger, setNewTrigger] = useState('');

  const updateField = (path, value) => {
    setCohort(prev => {
      const keys = path.split('.');
      const updated = { ...prev };
      let current = updated;
      for (let i = 0; i < keys.length - 1; i++) {
        current[keys[i]] = { ...current[keys[i]] };
        current = current[keys[i]];
      }
      current[keys[keys.length - 1]] = value;
      return updated;
    });
  };

  const addArrayItem = (path, value) => {
    if (!value.trim()) return;
    setCohort(prev => {
      const keys = path.split('.');
      const updated = { ...prev };
      let current = updated;
      for (let i = 0; i < keys.length - 1; i++) {
        current[keys[i]] = { ...current[keys[i]] };
        current = current[keys[i]];
      }
      current[keys[keys.length - 1]] = [...(current[keys[keys.length - 1]] || []), value];
      return updated;
    });
  };

  const removeArrayItem = (path, index) => {
    setCohort(prev => {
      const keys = path.split('.');
      const updated = { ...prev };
      let current = updated;
      for (let i = 0; i < keys.length - 1; i++) {
        current[keys[i]] = { ...current[keys[i]] };
        current = current[keys[i]];
      }
      current[keys[keys.length - 1]] = current[keys[keys.length - 1]].filter((_, i) => i !== index);
      return updated;
    });
  };

  const panels = [
    { id: 'demographics', label: 'Demographics & Firmographics', icon: Building2 },
    { id: 'buyer', label: 'Buyer Profile', icon: Users },
    { id: 'psychographics', label: 'Psychographics', icon: Brain },
    { id: 'pains', label: 'Pain Points & Goals', icon: AlertCircle },
    { id: 'triggers', label: 'Behavioral Triggers', icon: Zap },
    { id: 'communication', label: 'Communication', icon: MessageSquare },
    { id: 'budget', label: 'Budget & Timeline', icon: DollarSign },
  ];

  return (
    <div className="w-full max-w-6xl mx-auto animate-in fade-in slide-in-from-bottom-12 duration-1000">
      <div className="text-center mb-8">
        <h2 className="font-serif text-4xl md:text-5xl mb-4 text-neutral-900">Review and Refine Your cohort</h2>
        <p className="text-neutral-600">Edit any field to customize your ideal customer profile</p>
      </div>

      <div className="grid lg:grid-cols-4 gap-6">
        {/* Sidebar Navigation */}
        <div className="lg:col-span-1">
          <div className="runway-card p-4 sticky top-4">
            <div className="space-y-1">
              {panels.map((panel) => {
                const Icon = panel.icon;
                return (
                  <button
                    key={panel.id}
                    onClick={() => setActivePanel(panel.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left transition-all ${activePanel === panel.id
                      ? 'bg-black text-white'
                      : 'hover:bg-neutral-100 text-neutral-700'
                      }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="text-sm font-medium">{panel.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3">
          <div className="runway-card p-8">
            {/* Name Field */}
            <div className="mb-8">
              <label className="block text-sm font-medium text-neutral-700 mb-2">Cohort Name</label>
              <input
                type="text"
                value={cohort.name}
                onChange={(e) => updateField('name', e.target.value)}
                placeholder="e.g., Enterprise SaaS CTOs"
                className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900"
              />
            </div>

            {/* Demographics Panel */}
            {activePanel === 'demographics' && (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">Company Size</label>
                  <select
                    value={cohort.demographics.companySize}
                    onChange={(e) => updateField('demographics.companySize', e.target.value)}
                    className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900"
                  >
                    <option value="">Select size range</option>
                    {COMPANY_SIZES.map(size => (
                      <option key={size} value={size}>{size} employees</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">Industry</label>
                  <select
                    value={cohort.demographics.industry}
                    onChange={(e) => updateField('demographics.industry', e.target.value)}
                    className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900"
                  >
                    <option value="">Select industry</option>
                    {INDUSTRIES.map(industry => (
                      <option key={industry} value={industry}>{industry}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">Revenue Range</label>
                  <select
                    value={cohort.demographics.revenue}
                    onChange={(e) => updateField('demographics.revenue', e.target.value)}
                    className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900"
                  >
                    <option value="">Select revenue range</option>
                    {REVENUE_RANGES.map(range => (
                      <option key={range} value={range}>{range}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">Geographic Location</label>
                  <input
                    type="text"
                    value={cohort.demographics.location}
                    onChange={(e) => updateField('demographics.location', e.target.value)}
                    placeholder="e.g., North America, Europe, Global"
                    className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900"
                  />
                </div>
              </div>
            )}

            {/* Buyer Profile Panel */}
            {activePanel === 'buyer' && (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">Buyer Role</label>
                  <select
                    value={cohort.buyerRole}
                    onChange={(e) => updateField('buyerRole', e.target.value)}
                    className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900"
                  >
                    <option value="">Select buyer role</option>
                    {BUYER_ROLES.map(role => (
                      <option key={role} value={role}>{role}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">Decision-Making Structure</label>
                  <textarea
                    value={cohort.decisionStructure}
                    onChange={(e) => updateField('decisionStructure', e.target.value)}
                    placeholder="Describe the buying committee and approval process..."
                    rows={3}
                    className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900 resize-none"
                  />
                </div>
              </div>
            )}

            {/* Psychographics Panel */}
            {activePanel === 'psychographics' && (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">Values & Motivations</label>
                  <div className="flex flex-wrap gap-2 mb-3">
                    {COMMON_DESCRIPTORS.map(desc => (
                      <button
                        key={desc}
                        onClick={() => {
                          const values = cohort.psychographics.values || [];
                          if (values.includes(desc)) {
                            updateField('psychographics.values', values.filter(v => v !== desc));
                          } else {
                            updateField('psychographics.values', [...values, desc]);
                          }
                        }}
                        className={`px-4 py-2 text-[10px] font-mono uppercase tracking-[0.2em] transition-all ${(cohort.psychographics.values || []).includes(desc)
                          ? 'bg-black text-white'
                          : 'bg-neutral-100 text-neutral-700 border border-neutral-200 hover:bg-neutral-200'
                          }`}
                      >
                        {desc}
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">Decision Style</label>
                  <input
                    type="text"
                    value={cohort.psychographics.decisionStyle || ''}
                    onChange={(e) => updateField('psychographics.decisionStyle', e.target.value)}
                    placeholder="e.g., Analytical and methodical, Quick decider"
                    className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">Priorities</label>
                  <textarea
                    value={(cohort.psychographics.priorities || []).join(', ')}
                    onChange={(e) => updateField('psychographics.priorities', e.target.value.split(', ').filter(p => p.trim()))}
                    placeholder="e.g., Cost savings, Scalability, Integration"
                    rows={2}
                    className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900 resize-none"
                  />
                </div>
              </div>
            )}

            {/* Pain Points & Goals Panel */}
            {activePanel === 'pains' && (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">Pain Points</label>
                  <div className="space-y-2 mb-3">
                    {(cohort.painPoints || []).map((pain, idx) => (
                      <div key={idx} className="flex items-center gap-2">
                        <AlertCircle className="w-4 h-4 text-red-500" />
                        <span className="flex-1">{pain}</span>
                        <button
                          onClick={() => removeArrayItem('painPoints', idx)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <X size={16} />
                        </button>
                      </div>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newPainPoint}
                      onChange={(e) => setNewPainPoint(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          addArrayItem('painPoints', newPainPoint);
                          setNewPainPoint('');
                        }
                      }}
                      placeholder="Add a pain point..."
                      className="flex-1 px-4 py-2 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900"
                    />
                    <button
                      onClick={() => {
                        addArrayItem('painPoints', newPainPoint);
                        setNewPainPoint('');
                      }}
                      className="px-4 py-2 bg-black text-white rounded-xl hover:bg-neutral-800"
                    >
                      Add
                    </button>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">Goals</label>
                  <div className="space-y-2 mb-3">
                    {(cohort.goals || []).map((goal, idx) => (
                      <div key={idx} className="flex items-center gap-2">
                        <Target className="w-4 h-4 text-green-500" />
                        <span className="flex-1">{goal}</span>
                        <button
                          onClick={() => removeArrayItem('goals', idx)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <X size={16} />
                        </button>
                      </div>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newGoal}
                      onChange={(e) => setNewGoal(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          addArrayItem('goals', newGoal);
                          setNewGoal('');
                        }
                      }}
                      placeholder="Add a goal..."
                      className="flex-1 px-4 py-2 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900"
                    />
                    <button
                      onClick={() => {
                        addArrayItem('goals', newGoal);
                        setNewGoal('');
                      }}
                      className="px-4 py-2 bg-black text-white rounded-xl hover:bg-neutral-800"
                    >
                      Add
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Behavioral Triggers Panel */}
            {activePanel === 'triggers' && (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">Behavioral Triggers</label>
                  <p className="text-sm text-neutral-500 mb-4">
                    Events or signals that indicate buying intent
                  </p>
                  <div className="space-y-2 mb-3">
                    {(cohort.behavioralTriggers || []).map((trigger, idx) => (
                      <div key={idx} className="flex items-center gap-2">
                        <Zap className="w-4 h-4 text-yellow-500" />
                        <span className="flex-1">{trigger}</span>
                        <button
                          onClick={() => removeArrayItem('behavioralTriggers', idx)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <X size={16} />
                        </button>
                      </div>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newTrigger}
                      onChange={(e) => setNewTrigger(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          addArrayItem('behavioralTriggers', newTrigger);
                          setNewTrigger('');
                        }
                      }}
                      placeholder="e.g., Recent funding round, New leadership hire"
                      className="flex-1 px-4 py-2 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900"
                    />
                    <button
                      onClick={() => {
                        addArrayItem('behavioralTriggers', newTrigger);
                        setNewTrigger('');
                      }}
                      className="px-4 py-2 bg-black text-white rounded-xl hover:bg-neutral-800"
                    >
                      Add
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Communication Panel */}
            {activePanel === 'communication' && (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">Preferred Channels</label>
                  <div className="flex flex-wrap gap-2 mb-3">
                    {CHANNELS.map(channel => (
                      <button
                        key={channel}
                        onClick={() => {
                          const channels = cohort.communication.channels || [];
                          if (channels.includes(channel)) {
                            updateField('communication.channels', channels.filter(c => c !== channel));
                          } else {
                            updateField('communication.channels', [...channels, channel]);
                          }
                        }}
                        className={`px-4 py-2 text-[10px] font-mono uppercase tracking-[0.2em] transition-all ${(cohort.communication.channels || []).includes(channel)
                          ? 'bg-black text-white'
                          : 'bg-neutral-100 text-neutral-700 border border-neutral-200 hover:bg-neutral-200'
                          }`}
                      >
                        {channel}
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">Communication Tone</label>
                  <input
                    type="text"
                    value={cohort.communication.tone || ''}
                    onChange={(e) => updateField('communication.tone', e.target.value)}
                    placeholder="e.g., Professional, data-focused, Casual"
                    className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">Preferred Content Format</label>
                  <input
                    type="text"
                    value={cohort.communication.format || ''}
                    onChange={(e) => updateField('communication.format', e.target.value)}
                    placeholder="e.g., Case studies, Whitepapers, Videos"
                    className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900"
                  />
                </div>
              </div>
            )}

            {/* Budget & Timeline Panel */}
            {activePanel === 'budget' && (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">Budget Range</label>
                  <input
                    type="text"
                    value={cohort.budget}
                    onChange={(e) => updateField('budget', e.target.value)}
                    placeholder="e.g., $50k-$200k annually"
                    className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">Purchase Timeline</label>
                  <input
                    type="text"
                    value={cohort.timeline}
                    onChange={(e) => updateField('timeline', e.target.value)}
                    placeholder="e.g., 3-6 months, Urgent (within 30 days)"
                    className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900"
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="flex justify-between mt-8">
        <button
          onClick={onBack}
          className="font-sans text-[10px] font-bold uppercase tracking-widest border-b border-transparent hover:border-black transition-all duration-500 pb-1 text-neutral-400 hover:text-black"
        >
          Back
        </button>
        <button
          onClick={() => onComplete(cohort)}
          className="group relative bg-black text-white px-12 py-4 overflow-hidden transition-all duration-500 hover:shadow-2xl hover:shadow-neutral-500/20"
        >
          <div className="relative z-10 flex items-center space-x-4">
            <span className="font-sans text-xs font-bold tracking-widest uppercase">
              Continue
            </span>
            <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform duration-500" />
          </div>
          <div className="absolute inset-0 bg-neutral-800 transform translate-y-full group-hover:translate-y-0 transition-transform duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"></div>
        </button>
      </div>
    </div>
  );
};

// Step 6: Manual Builder (with Hat Selector)
const Step6ManualBuilder = ({ onComplete, onBack, userPreferences }) => {
  const [selectedHat, setSelectedHat] = useState(null);
  const [cohortName, setCohortName] = useState('');
  const [descriptors, setDescriptors] = useState([]);
  const [size, setSize] = useState(50); // Percentage of market
  const [cohort, setCohort] = useState({
    demographics: { companySize: '', industry: '', revenue: '', location: '' },
    buyerRole: '',
    psychographics: { values: [], decisionStyle: '', priorities: [] },
    painPoints: [],
    goals: [],
    behavioralTriggers: [],
    communication: { channels: [], tone: '', format: '' },
    budget: '',
    timeline: '',
  });

  const handleDescriptorToggle = (desc) => {
    setDescriptors(prev =>
      prev.includes(desc)
        ? prev.filter(d => d !== desc)
        : [...prev, desc]
    );
  };

  return (
    <div className="w-full max-w-6xl mx-auto animate-in fade-in slide-in-from-bottom-12 duration-1000">
      <div className="text-center mb-8">
        <h2 className="font-serif text-4xl md:text-5xl mb-4 text-neutral-900">Build Your cohort Manually</h2>
        <p className="text-neutral-600">Start by selecting a persona archetype</p>
      </div>

      {/* Hat Selector */}
      <div className="runway-card p-8 mb-6">
        <h3 className="text-xl font-bold text-neutral-900 mb-6">Choose a Persona Archetype</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {HAT_ICONS.map((hat) => {
            const Icon = hat.icon;
            const isSelected = selectedHat === hat.id;
            return (
              <motion.button
                key={hat.id}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setSelectedHat(hat.id)}
                className={`p-6 rounded-2xl border-2 transition-all ${isSelected
                  ? 'border-black bg-black text-white'
                  : 'border-neutral-200 hover:border-neutral-400 bg-white'
                  }`}
              >
                <Icon className={`w-12 h-12 mx-auto mb-3 ${isSelected ? 'text-white' : 'text-neutral-700'}`} />
                <div className={`text-sm font-medium ${isSelected ? 'text-white' : 'text-neutral-900'}`}>
                  {hat.label}
                </div>
              </motion.button>
            );
          })}
        </div>
      </div>

      {/* Name and Descriptors */}
      {selectedHat && (
        <div className="runway-card p-8 mb-6">
          <div className="mb-6">
            <label className="block text-sm font-medium text-neutral-700 mb-2">Cohort Name</label>
            <input
              type="text"
              value={cohortName}
              onChange={(e) => setCohortName(e.target.value)}
              placeholder="e.g., Enterprise Erin, Tech Tina"
              className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900"
            />
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-neutral-700 mb-2">Descriptor Tags</label>
            <div className="flex flex-wrap gap-2">
              {COMMON_DESCRIPTORS.map(desc => (
                <button
                  key={desc}
                  onClick={() => handleDescriptorToggle(desc)}
                  className={`px-4 py-2 text-[10px] font-mono uppercase tracking-[0.2em] transition-all ${descriptors.includes(desc)
                    ? 'bg-black text-white'
                    : 'bg-neutral-100 text-neutral-700 border border-neutral-200 hover:bg-neutral-200'
                    }`}
                >
                  {desc}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">
              Segment Size: {size}% of market
            </label>
            <input
              type="range"
              min="1"
              max="100"
              value={size}
              onChange={(e) => setSize(Number(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-neutral-500 mt-1">
              <span>Niche</span>
              <span>Broad</span>
            </div>
          </div>
        </div>
      )}

      {/* Navigation */}
      <div className="flex justify-between items-center mt-8">
        <button
          onClick={onBack}
          className="text-neutral-500 hover:text-black text-sm font-medium transition-colors flex items-center gap-2"
        >
          <ArrowLeft size={16} />
          Back
        </button>

        {selectedHat && cohortName && (
          <button
            onClick={() => onComplete({ ...cohort, name: cohortName, hat: selectedHat, descriptors, size })}
            className="group relative bg-black text-white px-12 py-4 overflow-hidden transition-all duration-500 hover:shadow-2xl hover:shadow-neutral-500/20"
          >
            <div className="relative z-10 flex items-center space-x-4">
              <span className="font-sans text-xs font-bold tracking-widest uppercase">
                Continue Building
              </span>
              <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform duration-500" />
            </div>
            <div className="absolute inset-0 bg-neutral-800 transform translate-y-full group-hover:translate-y-0 transition-transform duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"></div>
          </button>
        )}
      </div>
    </div>
  );
};

// Step 7: Psychographics Computation
const Step7Psychographics = ({ cohort, onComplete, onBack }) => {
  const [computedPsychographics, setComputedPsychographics] = useState(null);
  const [isComputing, setIsComputing] = useState(true);

  useEffect(() => {
    // Real psychographic computation
    const computeData = async () => {
      setIsComputing(true);

      try {
        const computed = await computePsychographics(cohort);
        setComputedPsychographics(computed);
      } catch (err) {
        console.error("Psychographics Error:", err);
        // Fallback to basic structure if AI fails
        setComputedPsychographics({
          values: cohort.psychographics?.values || [],
          decisionStyle: cohort.psychographics?.decisionStyle || '',
          personalityTraits: [],
          interests: [],
          painPsychology: { primaryFear: '', motivation: '', emotionalDriver: '' },
          contentPreferences: { format: '', tone: '', channels: [] }
        });
      } finally {
        setIsComputing(false);
      }
    };

    computeData();
  }, [cohort]);

  if (isComputing) {
    return (
      <div className="w-full max-w-3xl mx-auto text-center animate-in fade-in duration-1000">
        <Loader2 className="animate-spin text-black mx-auto mb-6" size={48} />
        <div className="space-y-2">
          <p className="font-serif text-2xl italic">Computing psychographics...</p>
          <p className="font-sans text-[10px] uppercase tracking-widest text-neutral-400">
            Analyzing values, motivations, and behavioral patterns
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-12 duration-1000">
      <div className="text-center mb-8">
        <h2 className="font-serif text-4xl md:text-5xl mb-4 text-neutral-900">Psychographic Profile</h2>
        <p className="text-neutral-600">AI-generated insights into your cohort's psychology and motivations</p>
      </div>

      <div className="runway-card p-8 space-y-8">
        <div>
          <h3 className="text-xl font-bold text-neutral-900 mb-4">Core Values & Motivations</h3>
          <div className="flex flex-wrap gap-2">
            {computedPsychographics.values.map((value, idx) => (
              <span key={idx} className="px-4 py-2 bg-black text-white text-[10px] font-mono uppercase tracking-[0.2em]">
                {value}
              </span>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-xl font-bold text-neutral-900 mb-4">Personality & Decision Style</h3>
          <p className="text-neutral-700 mb-3">{computedPsychographics.decisionStyle}</p>
          <div className="flex flex-wrap gap-2">
            {computedPsychographics.personalityTraits.map((trait, idx) => (
              <span key={idx} className="px-3 py-1.5 bg-neutral-100 text-neutral-900 border border-neutral-200 text-[10px] font-mono uppercase tracking-[0.2em]">
                {trait}
              </span>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-xl font-bold text-neutral-900 mb-4">Pain Psychology</h3>
          <div className="space-y-3">
            <div>
              <span className="text-sm font-medium text-neutral-500">Primary Fear:</span>
              <p className="text-neutral-900">{computedPsychographics.painPsychology.primaryFear}</p>
            </div>
            <div>
              <span className="text-sm font-medium text-neutral-500">Core Motivation:</span>
              <p className="text-neutral-900">{computedPsychographics.painPsychology.motivation}</p>
            </div>
            <div>
              <span className="text-sm font-medium text-neutral-500">Emotional Driver:</span>
              <p className="text-neutral-900">{computedPsychographics.painPsychology.emotionalDriver}</p>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-xl font-bold text-neutral-900 mb-4">Content & Communication Preferences</h3>
          <div className="space-y-2 text-sm">
            <div><span className="font-medium">Format:</span> {computedPsychographics.contentPreferences.format}</div>
            <div><span className="font-medium">Tone:</span> {computedPsychographics.contentPreferences.tone}</div>
            <div>
              <span className="font-medium">Channels:</span>{' '}
              {computedPsychographics.contentPreferences.channels.join(', ')}
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-between mt-8">
        <button
          onClick={onBack}
          className="font-sans text-[10px] font-bold uppercase tracking-widest border-b border-transparent hover:border-black transition-all duration-500 pb-1 text-neutral-400 hover:text-black"
        >
          Back
        </button>
        <button
          onClick={() => onComplete({ ...cohort, computedPsychographics })}
          className="group relative bg-black text-white px-12 py-4 overflow-hidden transition-all duration-500 hover:shadow-2xl hover:shadow-neutral-500/20"
        >
          <div className="relative z-10 flex items-center space-x-4">
            <span className="font-sans text-xs font-bold tracking-widest uppercase">
              Finalize cohort
            </span>
            <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform duration-500" />
          </div>
          <div className="absolute inset-0 bg-neutral-800 transform translate-y-full group-hover:translate-y-0 transition-transform duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"></div>
        </button>
      </div>
    </div>
  );
};

// Step 8: Finalize and Save
const Step8Finalize = ({ cohort, onComplete, onClose, onBack }) => {
  const [cohortName, setCohortName] = useState(cohort.name || '');
  const [fitScore, setFitScore] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    // Calculate fit score (mock calculation)
    const calculateFitScore = () => {
      let score = 0;
      if (cohort.demographics?.companySize) score += 15;
      if (cohort.demographics?.industry) score += 15;
      if (cohort.demographics?.revenue) score += 10;
      if (cohort.buyerRole) score += 15;
      if (cohort.psychographics?.values?.length > 0) score += 15;
      if (cohort.painPoints?.length > 0) score += 10;
      if (cohort.goals?.length > 0) score += 10;
      if (cohort.budget) score += 10;
      setFitScore(Math.min(score, 100));
    };

    calculateFitScore();
  }, [cohort]);

  const handleSave = async () => {
    if (!cohortName.trim()) {
      alert('Please enter a cohort name');
      return;
    }

    // Check limit before saving
    const currentCount = getCurrentCohortsCount();
    const limit = getCohortsLimit();

    if (currentCount >= limit) {
      alert(`You've reached your plan limit of ${limit} cohorts. Please upgrade to create more.`);
      return;
    }

    setIsSaving(true);

    try {
      // Save to Supabase
      const { data, error } = await supabase
        .from('cohorts')
        .insert([
          {
            user_id: user?.id,
            name: cohortName,
            data: {
              ...cohort,
              fitScore
            },
            created_at: new Date().toISOString()
          }
        ])
        .select();

      if (error) throw error;

      // Also save to localStorage for fallback/cache
      const savedCohort = {
        ...cohort,
        name: cohortName,
        fitScore,
        createdAt: new Date().toISOString(),
        id: data[0]?.id || Date.now(), // Use DB ID if available
        is_synced: true
      };

      const existingCohorts = JSON.parse(localStorage.getItem('cohorts') || '[]');
      existingCohorts.push(savedCohort);
      localStorage.setItem('cohorts', JSON.stringify(existingCohorts));

      // Update user preferences
      const preferences = JSON.parse(localStorage.getItem('userPreferences') || '{}');
      if (!preferences.preferredMode) {
        preferences.preferredMode = 'ai';
      }
      if (cohort.demographics?.industry && !preferences.commonIndustries?.includes(cohort.demographics.industry)) {
        preferences.commonIndustries = [...(preferences.commonIndustries || []), cohort.demographics.industry];
      }
      localStorage.setItem('userPreferences', JSON.stringify(preferences));

      setIsSaving(false);
      onComplete(savedCohort);

    } catch (err) {
      console.error("Error saving cohort:", err);
      alert("Failed to save cohort to cloud. Saving locally instead.");

      // Fallback to local storage only
      const savedCohort = {
        ...cohort,
        name: cohortName,
        fitScore,
        createdAt: new Date().toISOString(),
        id: Date.now(),
        is_synced: false
      };

      const existingCohorts = JSON.parse(localStorage.getItem('cohorts') || '[]');
      existingCohorts.push(savedCohort);
      localStorage.setItem('cohorts', JSON.stringify(existingCohorts));

      setIsSaving(false);
      onComplete(savedCohort);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-12 duration-1000">
      <div className="text-center mb-8">
        <h2 className="font-serif text-4xl md:text-5xl mb-4 text-neutral-900">Finalize Your cohort</h2>
        <p className="text-neutral-600">Give it a name and save it to your account</p>
      </div>

      <div className="runway-card p-8 mb-6">
        <div className="mb-6">
          <label className="block text-sm font-medium text-neutral-700 mb-2">Cohort Name</label>
          <input
            type="text"
            value={cohortName}
            onChange={(e) => setCohortName(e.target.value)}
            placeholder="e.g., Enterprise SaaS CTOs"
            className="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900"
          />
        </div>

        {fitScore !== null && (
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-neutral-700">Profile Completeness</span>
              <span className="text-lg font-bold text-neutral-900">{fitScore}%</span>
            </div>
            <div className="w-full h-3 bg-neutral-200 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${fitScore}%` }}
                transition={{ duration: 1 }}
                className="h-full bg-gradient-to-r from-neutral-700 to-neutral-900 rounded-full"
              />
            </div>
            {fitScore < 70 && (
              <p className="text-xs text-neutral-500 mt-2">
                Consider adding more details to improve your cohort's accuracy
              </p>
            )}
          </div>
        )}

        <div className="pt-6 border-t border-neutral-200">
          <h3 className="text-lg font-bold text-neutral-900 mb-4">Summary</h3>
          <div className="space-y-2 text-sm text-neutral-600">
            <div><span className="font-medium">Industry:</span> {cohort.demographics?.industry || 'Not specified'}</div>
            <div><span className="font-medium">Company Size:</span> {cohort.demographics?.companySize || 'Not specified'}</div>
            <div><span className="font-medium">Buyer Role:</span> {cohort.buyerRole || 'Not specified'}</div>
            <div><span className="font-medium">Pain Points:</span> {cohort.painPoints?.length || 0} identified</div>
            <div><span className="font-medium">Goals:</span> {cohort.goals?.length || 0} identified</div>
          </div>
        </div>
      </div>

      <div className="flex justify-between">
        <button
          onClick={onBack}
          className="font-sans text-[10px] font-bold uppercase tracking-widest border-b border-transparent hover:border-black transition-all duration-500 pb-1 text-neutral-400 hover:text-black"
        >
          Back
        </button>
        <button
          onClick={handleSave}
          disabled={isSaving || !cohortName.trim()}
          className="group relative bg-black text-white px-12 py-4 overflow-hidden transition-all duration-500 hover:shadow-2xl hover:shadow-neutral-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <div className="relative z-10 flex items-center space-x-4">
            {isSaving ? (
              <>
                <Loader2 className="animate-spin" size={14} />
                <span className="font-sans text-xs font-bold tracking-widest uppercase">Saving...</span>
              </>
            ) : (
              <>
                <span className="font-sans text-xs font-bold tracking-widest uppercase">Save cohort</span>
                <Check size={14} className="group-hover:scale-110 transition-transform duration-500" />
              </>
            )}
          </div>
          <div className="absolute inset-0 bg-neutral-800 transform translate-y-full group-hover:translate-y-0 transition-transform duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"></div>
        </button>
      </div>
    </div>
  );
};

// Plan limits
const PLAN_LIMITS = {
  ascent: 3,
  glide: 6,
  soar: 9
};

// Get user plan (default to 'ascent' if not set)
const getUserPlan = () => {
  const plan = localStorage.getItem('userPlan') || 'ascent';
  return plan.toLowerCase();
};

// Get cohorts limit for current plan
const getCohortsLimit = () => {
  const plan = getUserPlan();
  return PLAN_LIMITS[plan] || PLAN_LIMITS.ascent;
};

// Get current cohorts count
const getCurrentCohortsCount = () => {
  const cohorts = JSON.parse(localStorage.getItem('cohorts') || '[]');
  return cohorts.length;
};

// Check if user can create more cohorts
const canCreateCohort = () => {
  const currentCount = getCurrentCohortsCount();
  const limit = getCohortsLimit();
  return currentCount < limit;
};

// Main Cohorts Builder Component
export default function CohortsBuilder({
  onClose,
  onboardingData,
  // New props for integration
  userProfile: propUserProfile,
  userPlan: propUserPlan,
  cohortsLimit: propCohortsLimit,
  currentCohortsCount: propCurrentCohortsCount,
  onComplete: propOnComplete,
  initialData
}) {
  const [currentStep, setCurrentStep] = useState(1);
  const [creationMode, setCreationMode] = useState(null); // 'ai' or 'manual'
  const [cohortData, setCohortData] = useState({});
  const [userPreferences, setUserPreferences] = useState(() => {
    // Load from localStorage
    const saved = localStorage.getItem('userPreferences');
    return saved ? JSON.parse(saved) : {
      preferredMode: null,
      commonIndustries: [],
      commonRoles: []
    };
  });

  // Use props if available, otherwise fall back to internal logic
  const userPlan = propUserPlan || getUserPlan();
  const cohortsLimit = propCohortsLimit !== undefined ? propCohortsLimit : getCohortsLimit();
  const currentCohortsCount = propCurrentCohortsCount !== undefined ? propCurrentCohortsCount : getCurrentCohortsCount();
  const canCreate = propCohortsLimit ? (currentCohortsCount < cohortsLimit) : canCreateCohort();

  // Mock user profile and existing cohorts (would come from backend)
  const userProfile = propUserProfile || {
    companyName: onboardingData?.answers?.q1 || 'Your Company',
    industry: 'Technology'
  };

  const existingCohorts = []; // In a real app, fetch this

  const handleNext = () => {
    setCurrentStep(prev => prev + 1);
  };

  const handleBack = () => {
    setCurrentStep(prev => prev - 1);
  };

  const handleModeSelect = (mode) => {
    setCreationMode(mode);
    // Save preference
    const newPrefs = { ...userPreferences, preferredMode: mode };
    setUserPreferences(newPrefs);
    localStorage.setItem('userPreferences', JSON.stringify(newPrefs));

    handleNext();
  };

  const handleAIInputSubmit = (inputs) => {
    setCohortData(inputs);
    handleNext();
  };

  const handleDraftComplete = (draft) => {
    setCohortData(draft);
    handleNext();
  };

  const handleFinalize = (finalCohort) => {
    if (propOnComplete) {
      propOnComplete(finalCohort);
    } else if (onClose) {
      onClose();
    }
  };

  return (
    <div className="min-h-screen bg-cream text-neutral-900 font-sans selection:bg-black selection:text-white">
      {/* Background Noise */}
      <GrainOverlay />

      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 px-6 py-4 bg-white/80 backdrop-blur-md border-b border-neutral-200/50">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center">
              <Target className="text-white w-5 h-5" />
            </div>
            <span className="font-serif font-bold text-xl tracking-tight">RaptorFlow</span>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="p-2 hover:bg-neutral-100 rounded-full transition-colors"
            >
              <X size={20} />
            </button>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="pt-32 pb-20 px-6 relative z-10">
        <AnimatePresence mode="wait">
          {currentStep === 1 && (
            <Step1Launch
              key="step1"
              onNext={handleNext}
              userProfile={userProfile}
              existingCohorts={existingCohorts}
              userPlan={userPlan}
              cohortsLimit={cohortsLimit}
              currentCohortsCount={currentCohortsCount}
              canCreate={canCreate}
            />
          )}

          {currentStep === 2 && (
            <Step2ModeSelection
              key="step2"
              onSelect={handleModeSelect}
              userPreferences={userPreferences}
              onBack={handleBack}
            />
          )}

          {currentStep === 3 && creationMode === 'ai' && (
            <Step3AIInputs
              key="step3-ai"
              onSubmit={handleAIInputSubmit}
              initialData={initialData}
              onBack={handleBack}
            />
          )}

          {currentStep === 4 && creationMode === 'ai' && (
            <Step4AIGeneration
              key="step4-ai"
              inputs={cohortData}
              onComplete={handleDraftComplete}
              onBack={handleBack}
            />
          )}

          {currentStep === 5 && creationMode === 'ai' && (
            <Step5ReviewRefine
              key="step5-ai"
              draftCohort={cohortData}
              onComplete={(data) => {
                setCohortData(data);
                setCurrentStep(8); // Go to finalize
              }}
              onBack={handleBack}
              userPreferences={userPreferences}
            />
          )}

          {currentStep === 3 && creationMode === 'manual' && (
            <Step6ManualBuilder
              key="step6-manual"
              onComplete={(data) => {
                setCohortData(data);
                setCurrentStep(7); // Go to psychographics
              }}
              onBack={handleBack}
              userPreferences={userPreferences}
            />
          )}

          {currentStep === 7 && (
            <Step7Psychographics
              key="step7"
              cohort={cohortData}
              onComplete={(data) => {
                setCohortData(data);
                setCurrentStep(8); // Go to finalize
              }}
              onBack={handleBack}
            />
          )}

          {currentStep === 8 && (
            <Step8Finalize
              key="step8"
              cohort={cohortData}
              onComplete={handleFinalize}
              onClose={onClose}
              onBack={handleBack}
            />
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

