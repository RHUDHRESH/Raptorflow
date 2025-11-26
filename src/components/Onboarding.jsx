import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import CohortsBuilder from './CohortsBuilder';
import {
  ArrowRight,
  ArrowLeft,
  Sparkles,
  Target,
  Shield,
  Zap,
  Eye,
  CheckCircle2,
  Building2,
  Users,
  Rocket,
  MapPin,
  Globe,
  Instagram,
  Linkedin,
  Youtube,
  DollarSign,
  Briefcase,
  LayoutGrid,
  MessageSquare,
  BarChart3,
  Loader2,
  AlertCircle
} from 'lucide-react';


import { supabase } from '../lib/supabase';
import { analyzeWebsite, normalizeUrl, isValidUrl } from '../lib/services/scraper-api';

const CORE_QUESTIONS = {
  business: [
    { id: 'q1', label: 'The Elevator Pitch', question: 'What do you do, in one sentence?', placeholder: 'We help [X] achieve [Y] by [Z]...' },
    { id: 'q2', label: 'Segments', question: 'Who are you trying to reach right now?', placeholder: 'e.g. CMOs at Series B tech companies...' },
    { id: 'q3', label: 'The Offer', question: 'What are you selling primarily?', placeholder: 'e.g. $2k/mo retainer, $50 SaaS subscription...' },
    { id: 'q4', label: 'Channels', question: 'How do customers currently find you?', placeholder: 'e.g. SEO, LinkedIn, Referrals...' },
    { id: 'q5', label: 'Friction', question: 'What is NOT working?', placeholder: 'e.g. Lots of traffic but low conversion...' },
    { id: 'q6', label: 'Snapshot', question: 'Roughly, what are your current numbers?', placeholder: 'e.g. $10k MRR, 5k visitors/mo...' },
    { id: 'q7', label: 'The Stake', question: 'What MUST happen in the next 90 days?', placeholder: 'e.g. Close 5 new enterprise deals...' }
  ],
  founder: [
    { id: 'q1', label: 'Superpower', question: 'What is your core expertise or "superpower"?', placeholder: 'e.g. Crisis management for startups...' },
    { id: 'q2', label: 'Audience', question: 'Who needs to know you exist?', placeholder: 'e.g. VCs, early-stage founders...' },
    { id: 'q3', label: 'The Offer', question: 'How do you monetize (or plan to)?', placeholder: 'e.g. Coaching, speaking, advisory...' },
    { id: 'q4', label: 'Platform', question: 'Where are you most active?', placeholder: 'e.g. Twitter/X, LinkedIn, Newsletter...' },
    { id: 'q5', label: 'Bottleneck', question: 'What is holding you back?', placeholder: 'e.g. Inconsistent content, no clear funnel...' },
    { id: 'q6', label: 'Reach', question: 'Current audience size?', placeholder: 'e.g. 2k followers, 500 subs...' },
    { id: 'q7', label: 'The Win', question: 'What does a "win" look like in 90 days?', placeholder: 'e.g. Launch my course, get 3 speaking gigs...' }
  ],
  agency: [
    { id: 'q1', label: 'Niche', question: 'What is your specific niche?', placeholder: 'e.g. SEO for Dental Practices...' },
    { id: 'q2', label: 'Ideal Client', question: 'Who is your dream client?', placeholder: 'e.g. Multi-location clinics with $1M+ revenue...' },
    { id: 'q3', label: 'Model', question: 'What is your service model?', placeholder: 'e.g. Performance-based, Retainer, Project...' },
    { id: 'q4', label: 'Acquisition', question: 'How do you get clients now?', placeholder: 'e.g. Cold outreach, referrals...' },
    { id: 'q5', label: 'Friction', question: 'Biggest growth blocker?', placeholder: 'e.g. Churn, fulfillment capacity...' },
    { id: 'q6', label: 'Scale', question: 'Current client count / MRR?', placeholder: 'e.g. 12 clients, $40k MRR...' },
    { id: 'q7', label: 'Milestone', question: 'Next big milestone?', placeholder: 'e.g. Hit $83k/mo (1M run rate)...' }
  ]
};

const steps = [
  {
    id: 'welcome_mode',
    title: 'Welcome to RaptorFlow',
    subtitle: 'Let\'s tune RaptorFlow to who you are.',
    description: 'This takes about 10–15 minutes and powers everything: your cohorts, your moves, your content, your analytics.',
    type: 'mode_selection',
    options: [
      {
        value: 'business',
        label: 'Business / Brand',
        subtitle: 'You\'re here to grow a product, service, or company.',
        examples: 'SaaS · restaurant · hotel · D2C · clinic',
        icon: Building2
      },
      {
        value: 'founder',
        label: 'Founder / Executive',
        subtitle: 'You\'re building a personal brand around you.',
        examples: 'Startup founder · coach · CXO · creator',
        icon: Users
      },
      {
        value: 'agency',
        label: 'Agency / Studio',
        subtitle: 'You run marketing for multiple clients.',
        examples: 'Agency · freelancer with several retainers',
        icon: Briefcase
      }
    ]
  },
  {
    id: 'outcome_focus',
    title: 'What do you need RaptorFlow to do?',
    subtitle: 'Select up to 3 primary outcomes for the next 90 days.',
    type: 'multi_select',
    maxSelect: 3,
    options: [
      { value: 'fill_capacity', label: 'Fill capacity', desc: 'Get more bookings, tables, demos, or calls.' },
      { value: 'grow_audience', label: 'Grow audience', desc: 'Grow followers, email list, or community.' },
      { value: 'launch', label: 'Launch something', desc: 'New offer, feature, collection, or location.' },
      { value: 'fix_leak', label: 'Fix a leak', desc: 'Improve conversions, reduce churn, increase repeat customers.' },
      { value: 'clarify_message', label: 'Clarify my message', desc: 'Tighten positioning, story, and brand narrative.' },
      { value: 'diagnose', label: 'I\'m not sure yet', desc: 'I need you to diagnose where to start.' }
    ],
    hasFreeText: true,
    freeTextLabel: 'If we\'re wildly successful together in 90 days, what happens?'
  },
  {
    id: 'context_footprint',
    title: 'Context & Footprint',
    subtitle: 'Where do you live on the internet? What\'s already in place?',
    type: 'context_form'
  },
  {
    id: 'core_questions',
    title: 'The Core Questions',
    subtitle: 'Let\'s get specific about your business.',
    type: 'core_questions'
  },
  {
    id: 'ai_followup',
    title: 'Clarifying Questions',
    subtitle: 'A few quick follow-ups to make sure we understand.',
    description: 'Our AI is analyzing your answers to ask 3 sharp clarifying questions.',
    type: 'ai_followup'
  }
  // REMOVED: cohorts_builder, positioning_grid, and first_moves steps
  // User will go straight to dashboard after AI followup
];

export default function Onboarding() {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState({
    outcomes: [],
    socials: {},
    coreQuestions: {},
    aiQuestions: [],
    aiAnswers: {},
    positioning: { x: 50, y: 50 }, // Default center
    firstMove: null,
    generatedMoves: []
  });
  const [isGeneratingQuestions, setIsGeneratingQuestions] = useState(false);
  const [isGeneratingMoves, setIsGeneratingMoves] = useState(false);
  const [isCompleting, setIsCompleting] = useState(false);
  const [isScrapingWebsite, setIsScrapingWebsite] = useState(false);
  const [websiteAnalysis, setWebsiteAnalysis] = useState(null);
  const [showScrapedDataPreview, setShowScrapedDataPreview] = useState(false);
  const [showSkipConfirmation, setShowSkipConfirmation] = useState(false);

  const navigate = useNavigate();
  const { markOnboardingComplete, user, subscription } = useAuth();

  const step = steps[currentStep];
  const isFirstStep = currentStep === 0;

  // Check if current step is valid to proceed
  const canProceed = () => {
    if (step.id === 'welcome_mode') return !!answers.mode;
    if (step.id === 'outcome_focus') return answers.outcomes && answers.outcomes.length > 0;
    if (step.id === 'context_footprint') return !!answers.businessName; // Basic validation
    if (step.id === 'core_questions') {
      // Check if at least 3 core questions are answered
      const mode = answers.mode || 'business';
      const questions = CORE_QUESTIONS[mode];
      const answeredCount = questions.filter(q => !!answers.coreQuestions?.[q.id]).length;
      return answeredCount >= 3;
    }
    if (step.id === 'ai_followup') {
      // Must answer all generated questions
      if (!answers.aiQuestions || answers.aiQuestions.length === 0) return false;
      const answeredCount = answers.aiQuestions.filter(q => !!answers.aiAnswers?.[q.id]).length;
      return answeredCount === answers.aiQuestions.length;
    }
    if (step.id === 'cohorts_builder') return true; // Handled by component
    if (step.id === 'positioning_grid') return answers.positioning !== null;
    if (step.id === 'first_moves') return !!answers.firstMove;
    return true;
  };

  // Generate AI Questions when entering the step
  const generateAIQuestions = async () => {
    if (answers.aiQuestions && answers.aiQuestions.length > 0) return; // Already generated

    setIsGeneratingQuestions(true);

    // Simulate AI generation for now (replace with backend call later)
    // In a real implementation, this would call /api/v1/onboarding/generate-questions
    setTimeout(() => {
      const mode = answers.mode || 'business';
      let newQuestions = [];

      if (mode === 'business') {
        newQuestions = [
          { id: 'ai_q1', question: 'When are your busiest months, and when is it usually hardest to fill capacity?' },
          { id: 'ai_q2', question: 'Who do you MOST want to attract more of – families, couples, business groups, or something else?' },
          { id: 'ai_q3', question: 'In one sentence, what do customers say they love most after buying from you?' }
        ];
      } else if (mode === 'founder') {
        newQuestions = [
          { id: 'ai_q1', question: 'What specific topics do you want to own in your niche?' },
          { id: 'ai_q2', question: 'What makes you credible? (Exits, revenue, years of experience)' },
          { id: 'ai_q3', question: 'What type of audience do you want more of? (Investors, talent, clients)' }
        ];
      } else {
        newQuestions = [
          { id: 'ai_q1', question: 'What is the typical budget range for your ideal client?' },
          { id: 'ai_q2', question: 'Do you prefer retainer work or project-based work?' },
          { id: 'ai_q3', question: 'What is the biggest bottleneck in your current fulfillment process?' }
        ];
      }

      setAnswers(prev => ({ ...prev, aiQuestions: newQuestions }));
      setIsGeneratingQuestions(false);
    }, 2000);
  };

  const generateFirstMoves = async () => {
    if (answers.generatedMoves && answers.generatedMoves.length > 0) return;

    setIsGeneratingMoves(true);

    // Simulate AI strategy generation
    setTimeout(() => {
      const outcomes = answers.outcomes || [];
      const mode = answers.mode || 'business';
      const cohortName = answers.firstCohort?.name || 'Target Audience';

      let moves = [];

      // Logic to pick moves based on outcomes
      if (outcomes.includes('fill_capacity')) {
        moves.push({
          id: 'capacity_push',
          title: 'Weekend Capacity Push',
          duration: '14 days',
          target: cohortName,
          objective: 'Increase weekend occupancy from 60% → 80% within 6 weeks.',
          channels: ['Instagram', 'WhatsApp', 'Google Maps'],
          summary: 'Run a 14-day sprint focusing on weekend deals, with emotional family-time messaging and strong visuals.',
          icon: Zap
        });
      }

      if (outcomes.includes('grow_audience') || mode === 'founder') {
        moves.push({
          id: 'magnet_campaign',
          title: 'The Magnet Campaign',
          duration: '30 days',
          target: 'Broad Audience',
          objective: 'Grow email list by 500 subscribers.',
          channels: ['LinkedIn', 'Twitter/X', 'Newsletter'],
          summary: 'Publish high-value threads/carousels leading to a specific lead magnet to capture emails.',
          icon: Sparkles
        });
      }

      if (outcomes.includes('fix_leak') || outcomes.includes('clarify_message')) {
        moves.push({
          id: 'review_loop',
          title: 'Review & Proof Loop',
          duration: '28 days',
          target: 'Past Customers',
          objective: 'Double reviews on Google and Trustpilot.',
          channels: ['Email', 'SMS'],
          summary: 'Automated sequence to recent happy customers asking for specific, keyword-rich reviews.',
          icon: CheckCircle2
        });
      }

      if (outcomes.includes('launch')) {
        moves.push({
          id: 'launch_sequence',
          title: 'The Hype Sequence',
          duration: '21 days',
          target: 'Waitlist / Followers',
          objective: 'Generate $10k in opening week sales.',
          channels: ['Email', 'Social Stories'],
          summary: 'A structured 3-part launch: Tease, Reveal, and Open Cart with scarcity.',
          icon: Rocket
        });
      }

      // Fallback if we don't have enough moves
      if (moves.length < 3) {
        moves.push({
          id: 'local_outreach',
          title: 'Local Corporate Outreach',
          duration: '14 days',
          target: 'Local Businesses',
          objective: 'Get 5 new B2B inquiries.',
          channels: ['LinkedIn', 'Direct Email'],
          summary: 'Direct outreach to local office managers for offsites and events.',
          icon: Building2
        });
      }

      if (moves.length < 3) {
        moves.push({
          id: 'sniper_outreach',
          title: 'The Sniper Approach',
          duration: 'Ongoing',
          target: 'Dream Clients',
          objective: 'Start conversations with 10 high-value prospects.',
          channels: ['Personal Email', 'LinkedIn'],
          summary: 'High-touch, personalized research and outreach to your top 50 dream clients.',
          icon: Target
        });
      }

      setAnswers(prev => ({ ...prev, generatedMoves: moves.slice(0, 3) }));
      setIsGeneratingMoves(false);
    }, 2500);
  };

  // Handle website analysis and auto-prefill
  const handleWebsiteAnalysis = async (websiteUrl) => {
    if (!websiteUrl || !isValidUrl(normalizeUrl(websiteUrl))) {
      return;
    }

    setIsScrapingWebsite(true);
    setWebsiteAnalysis(null);

    try {
      const normalizedUrl = normalizeUrl(websiteUrl);
      const analysis = await analyzeWebsite(normalizedUrl);

      setWebsiteAnalysis(analysis);
      setShowScrapedDataPreview(true);

      // Auto-prefill business name if available
      if (analysis.business_name && analysis.business_name !== 'Unknown') {
        setAnswers(prev => ({
          ...prev,
          businessName: analysis.business_name
        }));
      }

      // Auto-prefill industry if available and determine if precise location is needed
      if (analysis.industry && analysis.industry !== 'Unknown') {
        const industryLower = analysis.industry.toLowerCase();
        const locationBoundIndustries = ['hospitality', 'restaurant', 'retail', 'salon', 'clinic', 'gym', 'real_estate', 'hotel', 'spa', 'fitness', 'healthcare'];
        const needsPreciseLocation = locationBoundIndustries.some(keyword => industryLower.includes(keyword));

        setAnswers(prev => ({
          ...prev,
          industry: analysis.industry,
          needsPreciseLocation
        }));
      }

      // Auto-prefill location if available
      if (analysis.location && analysis.location !== 'Unknown') {
        // If precise location is needed, put it in preciseLocation, otherwise in general location
        const fieldName = answers.needsPreciseLocation ? 'preciseLocation' : 'location';
        setAnswers(prev => ({
          ...prev,
          [fieldName]: analysis.location
        }));
      }

      // Auto-prefill core questions based on analysis
      const mode = answers.mode || 'business';
      const coreQuestionsUpdate = {};

      if (analysis.description && analysis.description !== 'Unknown') {
        coreQuestionsUpdate['q1'] = analysis.description;
      }

      if (analysis.target_audience && analysis.target_audience !== 'Unknown') {
        coreQuestionsUpdate['q2'] = analysis.target_audience;
      }

      if (analysis.products_services && analysis.products_services !== 'Unknown') {
        coreQuestionsUpdate['q3'] = analysis.products_services;
      }

      if (Object.keys(coreQuestionsUpdate).length > 0) {
        setAnswers(prev => ({
          ...prev,
          coreQuestions: {
            ...prev.coreQuestions,
            ...coreQuestionsUpdate
          }
        }));
      }

      console.log('Website analysis complete:', analysis);
    } catch (error) {
      console.error('Website analysis failed:', error);
      // Silently fail - user can still fill manually
    } finally {
      setIsScrapingWebsite(false);
    }
  };

  const handleNext = () => {
    if (currentStep === steps.length - 1) {
      handleFinalComplete();
    } else {
      const nextStepIdx = currentStep + 1;
      const nextStep = steps[nextStepIdx];

      if (nextStep.id === 'ai_followup') {
        generateAIQuestions();
      }

      if (nextStep.id === 'first_moves') {
        generateFirstMoves();
      }

      setCurrentStep(prev => prev + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleCohortComplete = (cohortData) => {
    // Save cohort data to state/local storage but don't finish onboarding yet
    updateAnswer('firstCohort', cohortData);
    handleNext();
  };

  const handleFinalComplete = async () => {
    setIsCompleting(true);

    try {
      // Save to Supabase
      if (user) {
        const { error } = await supabase
          .from('user_profiles')
          .update({
            onboarding_completed: true,
            preferences: {
              ...answers,
              onboarding_completed_at: new Date().toISOString()
            }
          })
          .eq('id', user.id);

        if (error) {
          console.error('Error saving profile to Supabase:', error);
          // Continue anyway to not block user
        }
      }

      // Local storage backup
      const finalData = {
        ...answers,
        completedAt: new Date().toISOString()
      };
      localStorage.setItem('raptorflow_onboarding', JSON.stringify(finalData));

      // Update context
      await markOnboardingComplete();

      // Navigate to dashboard
      setTimeout(() => {
        navigate('/dashboard');
      }, 800);

    } catch (err) {
      console.error('Error completing onboarding:', err);
      // Force navigation if something goes wrong
      navigate('/dashboard');
    }
  };

  const handleSkipOnboarding = async () => {
    setShowSkipConfirmation(false);
    setIsCompleting(true);

    try {
      // Mark as skipped in local storage
      const skippedData = {
        skipped: true,
        skippedAt: new Date().toISOString()
      };
      localStorage.setItem('raptorflow_onboarding', JSON.stringify(skippedData));

      // Update context
      await markOnboardingComplete();

      // Navigate to dashboard
      setTimeout(() => {
        navigate('/dashboard');
      }, 300);

    } catch (err) {
      console.error('Error skipping onboarding:', err);
      // Force navigation if something goes wrong
      navigate('/dashboard');
    }
  };


  const updateAnswer = (key, value) => {
    setAnswers(prev => ({ ...prev, [key]: value }));
  };

  const updateCoreQuestion = (id, value) => {
    setAnswers(prev => ({
      ...prev,
      coreQuestions: {
        ...prev.coreQuestions,
        [id]: value
      }
    }));
  };

  const updateAIAnswer = (id, value) => {
    setAnswers(prev => ({
      ...prev,
      aiAnswers: {
        ...prev.aiAnswers,
        [id]: value
      }
    }));
  };

  const toggleOutcome = (value) => {
    setAnswers(prev => {
      const current = prev.outcomes || [];
      if (current.includes(value)) {
        return { ...prev, outcomes: current.filter(i => i !== value) };
      }
      if (current.length >= 3) return prev;
      return { ...prev, outcomes: [...current, value] };
    });
  };

  // Render Step Content
  const renderStepContent = () => {
    switch (step.type) {
      case 'mode_selection':
        return (
          <div className="grid gap-4">
            {step.options.map((option) => {
              const Icon = option.icon;
              const isSelected = answers.mode === option.value;
              return (
                <motion.button
                  key={option.value}
                  onClick={() => updateAnswer('mode', option.value)}
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.99 }}
                  className={`
                    group relative p-6 border-2 rounded-lg text-left transition-all duration-200
                    ${isSelected
                      ? 'border-black bg-black text-white'
                      : 'border-black/10 bg-white hover:border-black/30'
                    }
                  `}
                >
                  <div className="flex items-start gap-4">
                    <div className={`
                      w-12 h-12 border flex items-center justify-center flex-shrink-0 rounded-full
                      ${isSelected
                        ? 'border-white/20 bg-white/10'
                        : 'border-black/10 bg-gray-50'
                      }
                    `}>
                      <Icon className={`w-6 h-6 ${isSelected ? 'text-white' : 'text-black'}`} strokeWidth={1.5} />
                    </div>
                    <div className="flex-1">
                      <h3 className={`text-xl font-serif mb-1 ${isSelected ? 'text-white' : 'text-black'}`}>
                        {option.label}
                      </h3>
                      <p className={`text-sm font-medium mb-2 ${isSelected ? 'text-white/90' : 'text-gray-900'}`}>
                        {option.subtitle}
                      </p>
                      <p className={`text-xs ${isSelected ? 'text-white/60' : 'text-gray-500'}`}>
                        e.g. {option.examples}
                      </p>
                    </div>
                    {isSelected && (
                      <CheckCircle2 className="w-6 h-6 text-white flex-shrink-0" strokeWidth={2} />
                    )}
                  </div>
                </motion.button>
              );
            })}
          </div>
        );

      case 'multi_select':
        return (
          <div className="space-y-6">
            <div className="grid md:grid-cols-2 gap-4">
              {step.options.map((option) => {
                const isSelected = (answers.outcomes || []).includes(option.value);
                return (
                  <motion.button
                    key={option.value}
                    onClick={() => toggleOutcome(option.value)}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className={`
                      p-4 border-2 rounded-lg text-left transition-all duration-200 h-full
                      ${isSelected
                        ? 'border-black bg-black text-white'
                        : 'border-black/10 bg-white hover:border-black/30'
                      }
                    `}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <h3 className={`font-bold ${isSelected ? 'text-white' : 'text-black'}`}>{option.label}</h3>
                      {isSelected && <CheckCircle2 className="w-4 h-4 text-white" />}
                    </div>
                    <p className={`text-sm ${isSelected ? 'text-white/80' : 'text-gray-600'}`}>{option.desc}</p>
                  </motion.button>
                );
              })}
            </div>
            {step.hasFreeText && (
              <div className="mt-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">{step.freeTextLabel}</label>
                <textarea
                  value={answers.outcomeFreeText || ''}
                  onChange={(e) => updateAnswer('outcomeFreeText', e.target.value)}
                  className="w-full px-4 py-3 bg-gray-50 border-2 border-transparent focus:bg-white focus:border-black rounded-lg transition-all outline-none resize-none"
                  rows={2}
                  placeholder="e.g. I want to be fully booked on weekends..."
                />
              </div>
            )}
          </div>
        );

      case 'context_form':
        return (
          <div className="grid md:grid-cols-2 gap-8">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Business Name</label>
                <input
                  type="text"
                  value={answers.businessName || ''}
                  onChange={(e) => updateAnswer('businessName', e.target.value)}
                  className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:border-black"
                  placeholder="Acme Corp"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Industry</label>
                <select
                  value={answers.industry || ''}
                  onChange={(e) => {
                    updateAnswer('industry', e.target.value);
                    // Determine if precise location is needed
                    const locationBoundIndustries = ['hospitality', 'restaurant', 'retail', 'salon', 'clinic', 'gym', 'real_estate'];
                    const needsPreciseLocation = locationBoundIndustries.includes(e.target.value);
                    updateAnswer('needsPreciseLocation', needsPreciseLocation);
                  }}
                  className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:border-black"
                >
                  <option value="">Select Industry...</option>
                  <optgroup label="Digital / Online">
                    <option value="saas">SaaS</option>
                    <option value="agency">Agency</option>
                    <option value="ecommerce">E-commerce</option>
                    <option value="creator">Creator / Coach</option>
                    <option value="consulting">Consulting</option>
                  </optgroup>
                  <optgroup label="Location-Based">
                    <option value="restaurant">Restaurant / Café</option>
                    <option value="hospitality">Hotel / Hospitality</option>
                    <option value="retail">Retail Store</option>
                    <option value="salon">Salon / Spa</option>
                    <option value="clinic">Clinic / Healthcare</option>
                    <option value="gym">Gym / Fitness</option>
                    <option value="real_estate">Real Estate</option>
                  </optgroup>
                  <optgroup label="Other">
                    <option value="other">Other</option>
                  </optgroup>
                </select>
              </div>

              {/* Smart Location Field - Shows precise location for location-bound businesses */}
              {answers.needsPreciseLocation ? (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Precise Location
                    <span className="text-xs text-gray-500 ml-2">(Important for local targeting)</span>
                  </label>
                  <div className="space-y-2">
                    <div className="relative">
                      <MapPin className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                      <input
                        type="text"
                        value={answers.preciseLocation || ''}
                        onChange={(e) => updateAnswer('preciseLocation', e.target.value)}
                        className="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:border-black"
                        placeholder="123 Main St, City, State, ZIP"
                      />
                    </div>
                    <button
                      type="button"
                      onClick={() => {
                        if (navigator.geolocation) {
                          navigator.geolocation.getCurrentPosition(
                            async (position) => {
                              const { latitude, longitude } = position.coords;
                              // Use reverse geocoding to get address
                              try {
                                const response = await fetch(
                                  `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`
                                );
                                const data = await response.json();
                                const address = data.display_name || `${latitude}, ${longitude}`;
                                updateAnswer('preciseLocation', address);
                                updateAnswer('coordinates', { lat: latitude, lng: longitude });
                              } catch (error) {
                                updateAnswer('preciseLocation', `${latitude}, ${longitude}`);
                                updateAnswer('coordinates', { lat: latitude, lng: longitude });
                              }
                            },
                            (error) => {
                              alert('Unable to get your location. Please enter it manually.');
                            }
                          );
                        } else {
                          alert('Geolocation is not supported by your browser.');
                        }
                      }}
                      className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
                    >
                      <Target className="w-4 h-4" />
                      Use My Current Location
                    </button>
                  </div>
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    General Location
                    <span className="text-xs text-gray-500 ml-2">(City or Region)</span>
                  </label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                    <input
                      type="text"
                      value={answers.location || ''}
                      onChange={(e) => updateAnswer('location', e.target.value)}
                      className="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:border-black"
                      placeholder="City, Country"
                    />
                  </div>
                </div>
              )}
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Website</label>
                <div className="relative">
                  <Globe className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                  <input
                    type="url"
                    value={answers.website || ''}
                    onChange={(e) => {
                      updateAnswer('website', e.target.value);
                    }}
                    onBlur={(e) => {
                      const url = e.target.value;
                      if (url && isValidUrl(normalizeUrl(url))) {
                        handleWebsiteAnalysis(url);
                      }
                    }}
                    className="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:border-black"
                    placeholder="https://yourwebsite.com"
                    disabled={isScrapingWebsite}
                  />
                  {isScrapingWebsite && (
                    <div className="absolute right-3 top-2.5">
                      <Loader2 className="w-4 h-4 text-black animate-spin" />
                    </div>
                  )}
                </div>
                {isScrapingWebsite && (
                  <p className="text-xs text-gray-500 mt-1 flex items-center gap-1">
                    <Sparkles className="w-3 h-3" />
                    Analyzing your website with AI...
                  </p>
                )}
                {websiteAnalysis && showScrapedDataPreview && !isScrapingWebsite && (
                  <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-xs text-green-800 font-medium flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3" />
                      Website analyzed! We've prefilled some fields for you. Feel free to edit them.
                    </p>
                  </div>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Monthly Budget</label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                  <select
                    value={answers.budget || ''}
                    onChange={(e) => updateAnswer('budget', e.target.value)}
                    className="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:border-black"
                  >
                    <option value="">Select Range...</option>
                    <option value="0-1k">&lt; $1k / mo</option>
                    <option value="1k-5k">$1k - $5k / mo</option>
                    <option value="5k-20k">$5k - $20k / mo</option>
                    <option value="20k+">$20k+ / mo</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        );

      case 'core_questions':
        const mode = answers.mode || 'business';
        const questions = CORE_QUESTIONS[mode];

        return (
          <div className="space-y-6">
            <div className="grid gap-6">
              {questions.map((q) => (
                <div key={q.id}>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <span className="text-gray-400 mr-2 font-mono text-xs uppercase tracking-wider">{q.label}</span>
                    {q.question}
                  </label>
                  <input
                    type="text"
                    value={answers.coreQuestions?.[q.id] || ''}
                    onChange={(e) => updateCoreQuestion(q.id, e.target.value)}
                    className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:border-black focus:bg-white transition-colors"
                    placeholder={q.placeholder}
                  />
                </div>
              ))}
            </div>
          </div>
        );

      case 'ai_followup':
        if (isGeneratingQuestions) {
          return (
            <div className="flex flex-col items-center justify-center py-20">
              <div className="w-16 h-16 border-4 border-black border-t-transparent rounded-full animate-spin mb-6"></div>
              <h3 className="text-xl font-serif font-bold mb-2">Analyzing your business...</h3>
              <p className="text-gray-500 text-center max-w-sm">
                Our AI is reviewing your answers to ask the most relevant follow-up questions.
              </p>
            </div>
          );
        }

        return (
          <div className="space-y-8">
            <div className="bg-blue-50 border border-blue-100 rounded-lg p-4 flex items-start gap-3">
              <Sparkles className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-blue-800">
                Based on what you told us, we have a few quick follow-ups so we don't guess.
              </p>
            </div>

            <div className="space-y-6">
              {answers.aiQuestions?.map((q, index) => (
                <motion.div
                  key={q.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <span className="text-gray-400 mr-2 font-mono text-xs uppercase tracking-wider">Clarification {index + 1}</span>
                    {q.question}
                  </label>
                  <textarea
                    value={answers.aiAnswers?.[q.id] || ''}
                    onChange={(e) => updateAIAnswer(q.id, e.target.value)}
                    className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:border-black focus:bg-white transition-colors resize-none"
                    rows={2}
                    placeholder="Your answer..."
                  />
                </motion.div>
              ))}
            </div>
          </div>
        );

      case 'positioning_grid':
        return (
          <div className="flex flex-col items-center justify-center py-8">
            <div className="relative w-full max-w-md aspect-square bg-gray-50 border-2 border-dashed border-gray-300 rounded-xl p-4">
              {/* Grid Labels */}
              <div className="absolute top-2 left-1/2 -translate-x-1/2 text-xs font-bold uppercase tracking-widest text-gray-500">Emotional / Brand</div>
              <div className="absolute bottom-2 left-1/2 -translate-x-1/2 text-xs font-bold uppercase tracking-widest text-gray-500">Functional / Utility</div>
              <div className="absolute left-2 top-1/2 -translate-y-1/2 -rotate-90 text-xs font-bold uppercase tracking-widest text-gray-500">Mass / Low Price</div>
              <div className="absolute right-2 top-1/2 -translate-y-1/2 rotate-90 text-xs font-bold uppercase tracking-widest text-gray-500">Premium / High Price</div>

              {/* Grid Lines */}
              <div className="absolute inset-0 grid grid-cols-2 grid-rows-2 pointer-events-none">
                <div className="border-r border-b border-gray-200"></div>
                <div className="border-b border-gray-200"></div>
                <div className="border-r border-gray-200"></div>
                <div></div>
              </div>

              {/* Interactive Area */}
              <div
                className="absolute inset-8 cursor-crosshair"
                onClick={(e) => {
                  const rect = e.currentTarget.getBoundingClientRect();
                  const x = ((e.clientX - rect.left) / rect.width) * 100;
                  const y = 100 - ((e.clientY - rect.top) / rect.height) * 100; // Invert Y so top is 100
                  updateAnswer('positioning', { x, y });
                }}
              >
                {/* The Dot */}
                <motion.div
                  layout
                  transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                  className="absolute w-6 h-6 bg-black rounded-full shadow-lg border-2 border-white transform -translate-x-1/2 -translate-y-1/2"
                  style={{
                    left: `${answers.positioning?.x || 50}%`,
                    top: `${100 - (answers.positioning?.y || 50)}%`
                  }}
                >
                  <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-black text-white text-[10px] px-2 py-1 rounded whitespace-nowrap opacity-0 hover:opacity-100 transition-opacity">
                    {Math.round(answers.positioning?.x || 50)}, {Math.round(answers.positioning?.y || 50)}
                  </div>
                </motion.div>
              </div>
            </div>
            <p className="mt-6 text-sm text-gray-500 text-center max-w-md">
              Click to place your brand. High price & emotional? Low price & functional?
              <br />This helps us tune your copy and strategy.
            </p>
          </div>
        );

      case 'first_moves':
        if (isGeneratingMoves) {
          return (
            <div className="flex flex-col items-center justify-center py-20">
              <div className="w-16 h-16 border-4 border-black border-t-transparent rounded-full animate-spin mb-6"></div>
              <h3 className="text-xl font-serif font-bold mb-2">Designing your strategy...</h3>
              <p className="text-gray-500 text-center max-w-sm">
                We're analyzing your cohorts and goals to build your first 90-day playbook.
              </p>
            </div>
          );
        }

        return (
          <div className="space-y-6">
            <div className="bg-green-50 border border-green-100 rounded-lg p-4 flex items-start gap-3">
              <Target className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-green-800">
                Here are 3 high-impact moves tailored to your goals. Select the one you want to start with.
              </p>
            </div>

            <div className="grid gap-4">
              {answers.generatedMoves?.map((move) => {
                const Icon = move.icon || Target;
                const isSelected = answers.firstMove === move.id;
                return (
                  <motion.button
                    key={move.id}
                    onClick={() => updateAnswer('firstMove', move.id)}
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.99 }}
                    className={`
                      relative p-6 border-2 rounded-xl text-left transition-all duration-200
                      ${isSelected
                        ? 'border-black bg-black text-white shadow-xl'
                        : 'border-black/10 bg-white hover:border-black/30'
                      }
                    `}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${isSelected ? 'bg-white/10' : 'bg-gray-100'}`}>
                          <Icon className={`w-5 h-5 ${isSelected ? 'text-white' : 'text-black'}`} />
                        </div>
                        <div>
                          <h3 className={`text-lg font-bold ${isSelected ? 'text-white' : 'text-black'}`}>
                            {move.title}
                          </h3>
                          <span className={`text-xs font-mono uppercase tracking-wider ${isSelected ? 'text-white/60' : 'text-gray-500'}`}>
                            {move.duration}
                          </span>
                        </div>
                      </div>
                      {isSelected && <CheckCircle2 className="w-6 h-6 text-green-400" />}
                    </div>

                    <p className={`text-sm mb-4 leading-relaxed ${isSelected ? 'text-white/90' : 'text-gray-600'}`}>
                      {move.summary}
                    </p>

                    <div className={`grid grid-cols-2 gap-4 mb-4 text-xs ${isSelected ? 'text-white/80' : 'text-gray-600'}`}>
                      <div>
                        <span className={`block font-bold mb-1 ${isSelected ? 'text-white/60' : 'text-gray-400'}`}>TARGET</span>
                        {move.target}
                      </div>
                      <div>
                        <span className={`block font-bold mb-1 ${isSelected ? 'text-white/60' : 'text-gray-400'}`}>OBJECTIVE</span>
                        {move.objective}
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      {move.channels?.map(channel => (
                        <span
                          key={channel}
                          className={`
                            text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded
                            ${isSelected ? 'bg-white/20 text-white' : 'bg-gray-100 text-gray-600'}
                          `}
                        >
                          {channel}
                        </span>
                      ))}
                    </div>
                  </motion.button>
                );
              })}
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  // If we are at the Cohorts Builder step, render it full screen
  if (step.id === 'cohorts_builder') {
    // Prepare initial data for CohortsBuilder from previous answers
    const mode = answers.mode || 'business';
    const questions = CORE_QUESTIONS[mode];

    // Map core questions to business description for AI context
    const businessDescription = questions
      .map(q => `${q.label}: ${answers.coreQuestions?.[q.id] || 'N/A'}`)
      .join('\n');

    const combinedDescription = `
      Business Name: ${answers.businessName}
      Industry: ${answers.industry}
      Location: ${answers.location}
      Website: ${answers.website}
      Outcomes: ${answers.outcomes?.join(', ')}
      Wild Success: ${answers.outcomeFreeText}
      
      Core Details:
      ${businessDescription}
    `;

    return (
      <div className="min-h-screen bg-cream p-6">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8 flex items-center justify-between">
            <button
              onClick={() => setCurrentStep(prev => prev - 1)}
              className="flex items-center gap-2 text-sm font-medium text-gray-500 hover:text-black transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Foundation
            </button>
            <div className="text-sm text-gray-400 font-mono uppercase tracking-widest">
              Final Step: ICP Creation
            </div>
          </div>

          <CohortsBuilder
            userProfile={user}
            userPlan={subscription?.plan || 'free'}
            cohortsLimit={100}
            currentCohortsCount={0}
            onComplete={handleCohortComplete}
            initialData={{
              businessDescription: combinedDescription,
              goals: answers.outcomes?.join(', '),
              location: answers.location
            }}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-cream flex items-center justify-center p-6">
      {/* Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-black/[0.02] rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-black/[0.02] rounded-full blur-3xl" />
      </div>

      <div className="relative w-full max-w-5xl">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-mono uppercase tracking-widest text-gray-400">
              Step {currentStep + 1} of {steps.length}
            </span>
            <span className="text-xs text-gray-500">
              {Math.round(((currentStep + 1) / steps.length) * 100)}% Complete
            </span>
          </div>
          <div className="h-1 bg-black/5 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-black"
              initial={{ width: 0 }}
              animate={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
              transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
            />
          </div>
        </div>

        {/* Content Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white border border-black/10 rounded-2xl shadow-xl shadow-black/5 p-8 md:p-12 min-h-[600px] flex flex-col"
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
              className="flex-1 flex flex-col"
            >
              {/* Header */}
              <div className="mb-8">
                <h1 className="font-serif text-4xl md:text-5xl font-bold mb-4">{step.title}</h1>
                <p className="text-xl text-gray-600">{step.subtitle}</p>
                {step.description && <p className="mt-4 text-gray-500">{step.description}</p>}
              </div>

              {/* Dynamic Content */}
              <div className="flex-1">
                {renderStepContent()}
              </div>

              {/* Navigation */}
              <div className="flex items-center justify-between pt-12 mt-8 border-t border-black/5">
                <button
                  onClick={handleBack}
                  disabled={isFirstStep}
                  className={`
                    inline-flex items-center gap-2 px-6 py-3 text-sm font-medium uppercase tracking-wide
                    transition-all duration-200
                    ${isFirstStep
                      ? 'text-gray-300 cursor-not-allowed'
                      : 'text-gray-700 hover:text-black'
                    }
                  `}
                >
                  <ArrowLeft className="w-4 h-4" strokeWidth={2} />
                  Back
                </button>

                <div className="flex items-center gap-3">
                  <button
                    onClick={() => setShowSkipConfirmation(true)}
                    className="inline-flex items-center gap-2 px-6 py-3 text-sm font-medium uppercase tracking-wide text-gray-500 hover:text-oxblood transition-all duration-200 border border-gray-200 hover:border-oxblood/30 rounded-lg"
                  >
                    Skip Onboarding
                  </button>

                  <button
                    onClick={handleNext}
                    disabled={!canProceed() || isCompleting}
                    className={`
                      inline-flex items-center gap-2 px-8 py-3 text-sm font-medium uppercase tracking-wide rounded-lg
                      transition-all duration-200
                      ${canProceed() && !isCompleting
                        ? 'bg-black text-white hover:bg-gray-900 hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-black/20'
                        : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                      }
                    `}
                  >
                    {currentStep === steps.length - 1 ? 'Finish Setup' : 'Continue'}
                    <ArrowRight className="w-4 h-4" strokeWidth={2} />
                  </button>
                </div>
              </div>
            </motion.div>
          </AnimatePresence>
        </motion.div>

        {/* Skip Confirmation Modal */}
        <AnimatePresence>
          {showSkipConfirmation && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[60] flex items-center justify-center p-4"
              onClick={() => setShowSkipConfirmation(false)}
            >
              <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: 20 }}
                transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                onClick={(e) => e.stopPropagation()}
                className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden border-2 border-black/10"
              >
                {/* Header */}
                <div className="bg-oxblood/5 border-b-2 border-oxblood/20 px-8 py-6">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-12 h-12 rounded-full bg-oxblood/10 flex items-center justify-center">
                      <AlertCircle className="w-6 h-6 text-oxblood" strokeWidth={2} />
                    </div>
                    <div>
                      <p className="text-xs font-mono uppercase tracking-widest text-oxblood/60">Warning</p>
                      <h3 className="text-2xl font-serif font-bold text-black">Are you sure?</h3>
                    </div>
                  </div>
                </div>

                {/* Content */}
                <div className="px-8 py-6">
                  <p className="text-gray-700 leading-relaxed mb-4">
                    Skipping onboarding means you'll miss out on personalized setup and recommendations.
                  </p>
                  <p className="text-sm text-gray-600 leading-relaxed">
                    You can always configure your preferences later in Settings, but it's much easier to do it now.
                  </p>
                </div>

                {/* Actions */}
                <div className="bg-gray-50 px-8 py-6 flex items-center justify-end gap-3 border-t border-gray-200">
                  <button
                    onClick={() => setShowSkipConfirmation(false)}
                    className="px-6 py-3 text-sm font-semibold text-gray-700 hover:text-black transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSkipOnboarding}
                    className="px-6 py-3 bg-oxblood text-white rounded-lg text-sm font-semibold hover:bg-oxblood-dark transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-oxblood/20"
                  >
                    Yes, Skip Onboarding
                  </button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
