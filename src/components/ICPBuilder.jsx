import React, { useState, useEffect, useRef } from 'react';
import { 
  ArrowRight, 
  Sparkles, 
  Loader2, 
  X, 
  ChevronDown, 
  Check, 
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
        <Target className="w-16 h-16 mx-auto mb-6 text-neutral-900" />
        <h1 className="font-serif text-5xl md:text-6xl mb-6 text-neutral-900">Create Your Ideal Customer Profile</h1>
        <p className="text-lg text-neutral-600 max-w-2xl mx-auto mb-8">
          A cohort is a detailed description of an ideal-fit company for your product or service. 
          Think of it as your perfect customer—the type of business that gets the most value from what you offer.
        </p>
        <div className="runway-card p-6 max-w-xl mx-auto text-left mb-6">
          <div className="flex items-start gap-3">
            <Lightbulb className="w-5 h-5 text-neutral-500 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-neutral-900 mb-1">Example</p>
              <p className="text-sm text-neutral-600">
                "Mid-market SaaS companies (50–200 employees, $5–25M revenue) with mature customer success teams, 
                seeking efficiency and data-driven solutions."
              </p>
            </div>
          </div>
        </div>
        
        {/* Plan Info */}
        <div className="runway-card p-6 max-w-xl mx-auto mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="text-left">
              <p className="text-sm font-medium text-neutral-900">Current Plan: <span className="font-bold">{planName}</span></p>
              <p className="text-xs text-neutral-500 mt-1">Cohorts Limit: {cohortsLimit}</p>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium text-neutral-900">
                {currentCohortsCount} / {cohortsLimit} cohorts
              </p>
              <div className="w-32 h-2 bg-neutral-200 rounded-full mt-2 overflow-hidden">
                <div 
                  className="h-full bg-black transition-all duration-500"
                  style={{ width: `${(currentCohortsCount / cohortsLimit) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {!canCreate && (
          <div className="runway-card p-6 max-w-xl mx-auto mb-6 border-2 border-red-200 bg-red-50">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
              <div className="text-left">
                <p className="text-sm font-bold text-red-900 mb-1">Cohorts Limit Reached</p>
                <p className="text-sm text-red-700">
                  You've reached your {planName} plan limit of {cohortsLimit} cohorts. 
                  Upgrade to {userPlan === 'ascent' ? 'Glide' : 'Soar'} to create more cohorts.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {existingCohorts && existingCohorts.length > 0 && (
        <div className="mb-8 text-sm text-neutral-500">
          You have {existingCohorts.length} existing cohort{existingCohorts.length !== 1 ? 's' : ''} in your account.
        </div>
      )}
      
      <button
        onClick={onNext}
        disabled={!canCreate}
        className={`group relative px-16 py-6 overflow-hidden transition-all duration-500 ${
          canCreate 
            ? 'bg-black text-white hover:shadow-2xl hover:shadow-neutral-500/20' 
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
          <div className="absolute inset-0 bg-neutral-800 transform translate-y-full group-hover:translate-y-0 transition-transform duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"></div>
        )}
      </button>
    </div>
  );
};

// Step 2: Choose Creation Mode
const Step2ModeSelection = ({ onSelect, userPreferences }) => {
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
      
      <div className="grid md:grid-cols-2 gap-8">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => handleSelect('ai')}
          className={`runway-card p-8 text-left cursor-pointer transition-all ${
            selectedMode === 'ai' 
              ? 'ring-2 ring-black shadow-xl' 
              : 'hover:shadow-xl'
          }`}
        >
          <div className="flex items-start gap-4 mb-4">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
              selectedMode === 'ai' ? 'bg-black text-white' : 'bg-neutral-100 text-neutral-900'
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
          className={`runway-card p-8 text-left cursor-pointer transition-all ${
            selectedMode === 'manual' 
              ? 'ring-2 ring-black shadow-xl' 
              : 'hover:shadow-xl'
          }`}
        >
          <div className="flex items-start gap-4 mb-4">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
              selectedMode === 'manual' ? 'bg-black text-white' : 'bg-neutral-100 text-neutral-900'
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
    </div>
  );
};

// Step 3: Initial Inputs (AI Path)
const Step3AIInputs = ({ onSubmit, initialData }) => {
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

      <div className="mt-12 flex justify-end">
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

// Step 4: AI Analysis & Draft Generation
const Step4AIGeneration = ({ inputs, onComplete, onBack }) => {
  const [status, setStatus] = useState('analyzing'); // 'analyzing' | 'draft'
  const [draftCohort, setDraftCohort] = useState(null);

  useEffect(() => {
    // Simulate AI analysis
    const analyzeData = async () => {
      setStatus('analyzing');
      
      // Simulate processing time
      await new Promise(resolve => setTimeout(resolve, 3000));

      // Extract insights from onboarding data
      const businessDesc = inputs.businessDescription || '';
      const productDesc = inputs.productDescription || '';
      const bestCustomers = inputs.topCustomers || inputs.targetMarket || '';
      const location = inputs.location || 'Global';
      
      // Parse company size from best customers description
      let companySize = '51-200';
      if (bestCustomers.toLowerCase().includes('small') || bestCustomers.toLowerCase().includes('startup')) {
        companySize = '1-50';
      } else if (bestCustomers.toLowerCase().includes('enterprise') || bestCustomers.toLowerCase().includes('large')) {
        companySize = '500+';
      }

      // Parse industry
      let industry = 'Technology';
      const industries = ['SaaS', 'E-commerce', 'Healthcare', 'Finance', 'Education', 'Manufacturing', 'Retail'];
      for (const ind of industries) {
        if (businessDesc.toLowerCase().includes(ind.toLowerCase()) || bestCustomers.toLowerCase().includes(ind.toLowerCase())) {
          industry = ind;
          break;
        }
      }

      // Generate draft cohort based on inputs
      const generated = {
        name: 'AI-Generated cohort',
        executiveSummary: `${bestCustomers || 'Mid-market companies'} (${companySize} employees) in ${industry} seeking ${inputs.valueProposition || 'efficiency and data-driven solutions'}.`,
        demographics: {
          companySize: companySize,
          industry: industry,
          revenue: companySize === '1-50' ? '$1M-$5M' : companySize === '51-200' ? '$5M-$25M' : '$25M-$100M',
          location: location,
        },
        buyerRole: bestCustomers.toLowerCase().includes('founder') ? 'Founder/CEO' : 
                   bestCustomers.toLowerCase().includes('cto') ? 'CTO' :
                   bestCustomers.toLowerCase().includes('cmo') ? 'CMO' :
                   'VP or Director',
        psychographics: {
          values: ['Efficiency', 'Data-driven decisions', 'Innovation'],
          decisionStyle: 'Analytical and methodical',
          priorities: ['Cost savings', 'Scalability', 'Integration'],
        },
        painPoints: [
          businessDesc ? `Challenges related to ${businessDesc.split(' ').slice(0, 3).join(' ')}` : 'Manual processes slowing growth',
          'Lack of visibility into operations',
          'Difficulty scaling efficiently'
        ],
        goals: [
          inputs.goals || 'Streamline operations',
          'Improve team productivity',
          'Scale without proportional cost increase'
        ],
        behavioralTriggers: [
          'Recent funding round',
          'New leadership hire',
          'Rapid team growth',
          'Expansion into new markets'
        ],
        communication: {
          channels: inputs.currentMarketing ? inputs.currentMarketing.split(',').map(c => c.trim()) : ['Email', 'LinkedIn', 'Content Marketing'],
          tone: 'Professional, data-focused',
          format: 'Case studies, whitepapers'
        },
        budget: '$50k-$200k annually',
        timeline: '3-6 months',
        decisionStructure: 'Buying committee with VP-level approval'
      };

      setDraftCohort(generated);
      setStatus('draft');
    };

    analyzeData();
  }, [inputs]);

  if (status === 'analyzing') {
    return (
      <div className="w-full max-w-3xl mx-auto text-center animate-in fade-in duration-1000">
        <Loader2 className="animate-spin text-black mx-auto mb-6" size={48} />
        <div className="space-y-2">
          <p className="font-serif text-2xl italic">Analyzing your inputs...</p>
          <p className="font-sans text-[10px] uppercase tracking-widest text-neutral-400">
            Using AI to identify patterns and generate your cohort
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-12 duration-1000">
      <div className="text-center mb-8">
        <h2 className="font-serif text-4xl md:text-5xl mb-4 text-neutral-900">Your AI-Generated cohort</h2>
        <p className="text-neutral-600">Review the suggestions below. You can edit any field in the next step.</p>
      </div>

      <div className="runway-card p-8 mb-6">
        <div className="mb-6">
          <h3 className="text-xl font-bold text-neutral-900 mb-3">Executive Summary</h3>
          <p className="text-neutral-700 leading-relaxed">{draftCohort.executiveSummary}</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-6">
          <div>
            <h4 className="text-sm font-bold uppercase tracking-widest text-neutral-500 mb-3">Firmographics</h4>
            <div className="space-y-2 text-sm">
              <div><span className="font-medium">Company Size:</span> {draftCohort.demographics.companySize} employees</div>
              <div><span className="font-medium">Industry:</span> {draftCohort.demographics.industry}</div>
              <div><span className="font-medium">Revenue:</span> {draftCohort.demographics.revenue}</div>
              <div><span className="font-medium">Location:</span> {draftCohort.demographics.location}</div>
            </div>
          </div>

          <div>
            <h4 className="text-sm font-bold uppercase tracking-widest text-neutral-500 mb-3">Buyer Profile</h4>
            <div className="space-y-2 text-sm">
              <div><span className="font-medium">Role:</span> {draftCohort.buyerRole}</div>
              <div><span className="font-medium">Budget:</span> {draftCohort.budget}</div>
              <div><span className="font-medium">Timeline:</span> {draftCohort.timeline}</div>
            </div>
          </div>
        </div>

        <div className="mb-6">
          <h4 className="text-sm font-bold uppercase tracking-widest text-neutral-500 mb-3">Psychographics</h4>
          <div className="flex flex-wrap gap-2 mb-3">
            {draftCohort.psychographics.values.map((value, idx) => (
              <span key={idx} className="px-3 py-1.5 bg-neutral-100 text-neutral-900 border border-neutral-200 text-[10px] font-mono uppercase tracking-[0.2em]">
                {value}
              </span>
            ))}
          </div>
          <p className="text-sm text-neutral-600"><span className="font-medium">Decision Style:</span> {draftCohort.psychographics.decisionStyle}</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-bold uppercase tracking-widest text-neutral-500 mb-3">Pain Points</h4>
            <ul className="space-y-1 text-sm">
              {draftCohort.painPoints.map((pain, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                  <span>{pain}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-bold uppercase tracking-widest text-neutral-500 mb-3">Goals</h4>
            <ul className="space-y-1 text-sm">
              {draftCohort.goals.map((goal, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <Target className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>{goal}</span>
                </li>
              ))}
            </ul>
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
          onClick={() => onComplete(draftCohort)}
          className="group relative bg-black text-white px-12 py-4 overflow-hidden transition-all duration-500 hover:shadow-2xl hover:shadow-neutral-500/20"
        >
          <div className="relative z-10 flex items-center space-x-4">
            <span className="font-sans text-xs font-bold tracking-widest uppercase">
              Continue to Refine
            </span>
            <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform duration-500" />
          </div>
          <div className="absolute inset-0 bg-neutral-800 transform translate-y-full group-hover:translate-y-0 transition-transform duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"></div>
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
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left transition-all ${
                      activePanel === panel.id
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
                        className={`px-4 py-2 text-[10px] font-mono uppercase tracking-[0.2em] transition-all ${
                          (cohort.psychographics.values || []).includes(desc)
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
                        className={`px-4 py-2 text-[10px] font-mono uppercase tracking-[0.2em] transition-all ${
                          (cohort.communication.channels || []).includes(channel)
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
                className={`p-6 rounded-2xl border-2 transition-all ${
                  isSelected
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
                  className={`px-4 py-2 text-[10px] font-mono uppercase tracking-[0.2em] transition-all ${
                    descriptors.includes(desc)
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

      {/* Continue to detailed fields */}
      {selectedHat && cohortName && (
        <div className="flex justify-end">
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
        </div>
      )}
    </div>
  );
};

// Step 7: Psychographics Computation
const Step7Psychographics = ({ cohort, onComplete, onBack }) => {
  const [computedPsychographics, setComputedPsychographics] = useState(null);
  const [isComputing, setIsComputing] = useState(true);

  useEffect(() => {
    // Simulate psychographic computation
    const computePsychographics = async () => {
      setIsComputing(true);
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Compute psychographics based on cohort data
      const computed = {
        values: cohort.psychographics?.values || ['Efficiency', 'Innovation'],
        decisionStyle: cohort.psychographics?.decisionStyle || 'Analytical and methodical',
        personalityTraits: ['Research-oriented', 'Risk-aware', 'Data-driven'],
        interests: ['Industry reports', 'Case studies', 'Technical documentation'],
        painPsychology: {
          primaryFear: 'Inefficiency and wasted resources',
          motivation: 'Achieving operational excellence',
          emotionalDriver: 'Desire for control and predictability'
        },
        contentPreferences: {
          format: cohort.communication?.format || 'Whitepapers and case studies',
          tone: cohort.communication?.tone || 'Professional and data-focused',
          channels: cohort.communication?.channels || ['Email', 'LinkedIn']
        }
      };

      setComputedPsychographics(computed);
      setIsComputing(false);
    };

    computePsychographics();
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
const Step8Finalize = ({ cohort, onComplete, onClose }) => {
  const [cohortName, setCohortName] = useState(cohort.name || '');
  const [fitScore, setFitScore] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

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
    // Simulate save
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Save to memory/user preferences
    const savedCohort = {
      ...cohort,
      name: cohortName,
      fitScore,
      createdAt: new Date().toISOString(),
      id: Date.now()
    };

    // Store in localStorage (would be API call in production)
    const existingCohorts = JSON.parse(localStorage.getItem('cohorts') || '[]');
    existingCohorts.push(savedCohort);
    localStorage.setItem('cohorts', JSON.stringify(existingCohorts));

    // Update user preferences
    const preferences = JSON.parse(localStorage.getItem('userPreferences') || '{}');
    if (!preferences.preferredMode) {
      preferences.preferredMode = 'ai'; // or 'manual'
    }
    if (cohort.demographics?.industry && !preferences.commonIndustries?.includes(cohort.demographics.industry)) {
      preferences.commonIndustries = [...(preferences.commonIndustries || []), cohort.demographics.industry];
    }
    localStorage.setItem('userPreferences', JSON.stringify(preferences));

    setIsSaving(false);
    onComplete(savedCohort);
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
          onClick={onClose}
          className="font-sans text-[10px] font-bold uppercase tracking-widest border-b border-transparent hover:border-black transition-all duration-500 pb-1 text-neutral-400 hover:text-black"
        >
          Cancel
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
export default function CohortsBuilder({ onClose, onboardingData }) {
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

  // Get plan info
  const userPlan = getUserPlan();
  const cohortsLimit = getCohortsLimit();
  const currentCohortsCount = getCurrentCohortsCount();
  const canCreate = canCreateCohort();

  // Mock user profile and existing cohorts (would come from backend)
  const userProfile = {
    companyName: onboardingData?.answers?.q1 || 'Your Company',
    industry: 'Technology'
  };

  const existingCohorts = JSON.parse(localStorage.getItem('cohorts') || '[]');

  const handleStep1Complete = () => {
    // Skip directly to AI generation using onboarding data
    // Convert onboarding answers to AI inputs format
    const aiInputs = {
      businessDescription: onboardingData?.answers?.q1 || '',
      productDescription: onboardingData?.answers?.q2 || '',
      targetMarket: onboardingData?.answers?.q4 || '', // Best customers
      valueProposition: onboardingData?.answers?.q3 || '', // Why they started
      topCustomers: onboardingData?.answers?.q4 || '',
      location: onboardingData?.answers?.q6?.address || '',
      currentMarketing: onboardingData?.answers?.q7a || '',
      timeAvailable: onboardingData?.answers?.q7b || '',
      goals: onboardingData?.answers?.q7c || '',
    };
    setCohortData(prev => ({ ...prev, aiInputs }));
    setCurrentStep(4); // Go directly to AI generation
  };

  const handleAIGenerationComplete = (draft) => {
    setCohortData(prev => ({ ...prev, draft }));
    setCurrentStep(5);
  };

  const handleReviewComplete = (refinedCohort) => {
    setCohortData(prev => ({ ...prev, refined: refinedCohort }));
    setCurrentStep(7); // Skip to psychographics
  };


  const handlePsychographicsComplete = (cohortWithPsychographics) => {
    setCohortData(prev => ({ ...prev, final: cohortWithPsychographics }));
    setCurrentStep(8);
  };

  const handleFinalizeComplete = (savedCohort) => {
    console.log('Cohort saved:', savedCohort);
    
    // Check if we're at limit after saving
    const newCount = getCurrentCohortsCount();
    const limit = getCohortsLimit();
    
    if (newCount >= limit) {
      // Show a message that limit is reached
      alert(`Cohort created successfully! You've reached your ${userPlan.charAt(0).toUpperCase() + userPlan.slice(1)} plan limit of ${limit} cohorts.`);
    }
    
    if (onClose) {
      onClose();
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <Step1Launch 
            onNext={handleStep1Complete} 
            userProfile={userProfile} 
            existingCohorts={existingCohorts}
            userPlan={userPlan}
            cohortsLimit={cohortsLimit}
            currentCohortsCount={currentCohortsCount}
            canCreate={canCreate}
          />
        );
      case 4:
        return (
          <Step4AIGeneration 
            inputs={cohortData.aiInputs} 
            onComplete={handleAIGenerationComplete}
            onBack={handleBack}
          />
        );
      case 5:
        return (
          <Step5ReviewRefine 
            draftCohort={cohortData.draft}
            onComplete={handleReviewComplete}
            onBack={handleBack}
            userPreferences={userPreferences}
          />
        );
      case 7:
        return (
          <Step7Psychographics 
            cohort={cohortData.refined}
            onComplete={handlePsychographicsComplete}
            onBack={handleBack}
          />
        );
      case 8:
        return (
          <Step8Finalize 
            cohort={cohortData.final}
            onComplete={handleFinalizeComplete}
            onClose={onClose}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex h-screen w-screen bg-white text-neutral-900 overflow-hidden font-sans selection:bg-black selection:text-white">
      <GrainOverlay />
      {onClose && (
        <button 
          className="absolute top-8 left-8 z-50 p-2 text-neutral-400 hover:text-black transition-colors hover:bg-neutral-100"
          onClick={onClose} 
        >
          <X size={24} />
        </button>
      )}
      <div className="flex-grow flex flex-col justify-center items-center px-6 md:px-8 relative z-10 overflow-y-auto py-20">
        {renderStep()}
      </div>
    </div>
  );
}
