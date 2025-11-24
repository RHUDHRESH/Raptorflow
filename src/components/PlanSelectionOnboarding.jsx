import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, ArrowLeft, Check, X, Sparkles } from 'lucide-react';
import { cn } from '../utils/cn';

const PlanSelectionOnboarding = () => {
  const navigate = useNavigate();
  const [selectedPrice, setSelectedPrice] = useState('');
  const [selectedServiceLevel, setSelectedServiceLevel] = useState('');
  const [selectedAction, setSelectedAction] = useState('');

  const priceOptions = [
    { id: 'affordable', label: 'More affordable', description: 'Budget-conscious solutions' },
    { id: 'expensive', label: 'More expensive', description: 'Premium, comprehensive support' }
  ];

  const serviceLevelOptions = [
    { id: 'self-serve', label: 'Self-serve / DIY', description: 'Tools and templates you can use yourself', icon: '🔧' },
    { id: 'freelancers', label: 'Freelancers / Contractors', description: 'Individual experts help you get it done', icon: '👨‍💻' },
    { id: 'agencies', label: 'Full-service agencies', description: 'Complete teams handle everything for you', icon: '🏢' },
    { id: 'done-for-you', label: 'Done-for-you / High support', description: 'Executive-level strategy and implementation', icon: '✨' }
  ];

  const actions = [
    { id: 'continue', label: 'Continue', description: 'I\'m ready to get started' },
    { id: 'explore', label: 'Do nothing (I\'m just exploring)', description: 'Maybe later - let me look around first' }
  ];

  const canProceed = selectedPrice && selectedServiceLevel && selectedAction === 'continue';

  const handleContinue = () => {
    if (canProceed) {
      // Store selection for later use
      const onboardingPreferences = {
        priceTier: selectedPrice,
        serviceLevel: selectedServiceLevel,
        action: selectedAction,
        timestamp: new Date().toISOString(),
        completedPlanSelection: true
      };

      // Store in localStorage temporarily (could also go to Supabase)
      localStorage.setItem('onboardingPreferences', JSON.stringify(onboardingPreferences));

      // Navigate to the detailed onboarding questionnaire
      navigate('/onboarding', { state: { preferences: onboardingPreferences } });
    }
  };

  const handleExplore = () => {
    const onboardingPreferences = {
      priceTier: selectedPrice,
      serviceLevel: selectedServiceLevel,
      action: 'explore',
      timestamp: new Date().toISOString(),
      completedPlanSelection: true
    };

    localStorage.setItem('onboardingPreferences', JSON.stringify(onboardingPreferences));
    // Navigate to dashboard with exploring status
    navigate('/', {
      state: {
        isExploring: true,
        preferences: onboardingPreferences
      }
    });
  };

  const handleAction = (actionId) => {
    setSelectedAction(actionId);
    if (actionId === 'explore') {
      handleExplore();
    }
  };

  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="max-w-4xl w-full space-y-12"
      >
        {/* Header */}
        <div className="text-center space-y-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="inline-flex items-center gap-3 px-4 py-2 bg-neutral-100 rounded-full text-sm font-medium text-neutral-700"
          >
            <Sparkles className="w-4 h-4" />
            Getting Started
          </motion.div>

          <h1 className="text-4xl lg:text-5xl font-light text-neutral-900 leading-tight">
            Which best describes your needs?
          </h1>
        </div>

        {/* Price Selection */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="space-y-4"
        >
          <div className="text-center">
            <span className="text-xs uppercase tracking-[0.3em] text-neutral-500 font-semibold">Price</span>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
            {priceOptions.map((option) => (
              <button
                key={option.id}
                onClick={() => setSelectedPrice(option.id)}
                className={cn(
                  "flex-1 p-6 rounded-xl border-2 transition-all duration-200 text-center group hover:shadow-sm",
                  selectedPrice === option.id
                    ? "border-neutral-900 bg-neutral-900 text-white"
                    : "border-neutral-200 hover:border-neutral-300 bg-white"
                )}
              >
                <div className="font-medium mb-1">{option.label}</div>
                <div className="text-sm opacity-70 group-hover:opacity-100 transition-opacity">
                  {selectedPrice === option.id ? '' : option.description}
                </div>
              </button>
            ))}
          </div>
        </motion.div>

        {/* Service Level Selection */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="space-y-6"
        >
          <div className="text-center">
            <span className="text-xs uppercase tracking-[0.3em] text-neutral-500 font-semibold">Service Level</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {serviceLevelOptions.map((option) => (
              <button
                key={option.id}
                onClick={() => setSelectedServiceLevel(option.id)}
                className={cn(
                  "p-6 rounded-xl border-2 transition-all duration-200 text-left group hover:shadow-sm",
                  selectedServiceLevel === option.id
                    ? "border-neutral-900 bg-neutral-900 text-white"
                    : "border-neutral-200 hover:border-neutral-300 bg-white"
                )}
              >
                <div className="flex items-start gap-4">
                  <span className="text-2xl mt-0.5">{option.icon}</span>
                  <div className="flex-1">
                    <div className="font-medium mb-2">{option.label}</div>
                    <div className={cn(
                      "text-sm group-hover:opacity-100 transition-opacity",
                      selectedServiceLevel === option.id ? "opacity-90" : "opacity-60"
                    )}>
                      {option.description}
                    </div>
                  </div>
                  {selectedServiceLevel === option.id && (
                    <Check className="w-5 h-5 mt-0.5 flex-shrink-0" />
                  )}
                </div>
              </button>
            ))}
          </div>
        </motion.div>

        {/* Action Selection */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="space-y-6"
        >
          <div className="flex flex-col gap-4 max-w-lg mx-auto">
            {actions.map((action) => (
              <button
                key={action.id}
                onClick={() => handleAction(action.id)}
                className={cn(
                  "p-6 rounded-xl border-2 transition-all duration-200 text-center group",
                  action.id === 'explore'
                    ? "border-dashed border-neutral-300 bg-neutral-25 hover:bg-neutral-50"
                    : "border-neutral-200 hover:border-neutral-300 bg-white hover:shadow-sm",
                  selectedAction === action.id && action.id !== 'explore' && "border-neutral-900 bg-neutral-900 text-white"
                )}
              >
                <div className="font-medium mb-1">{action.label}</div>
                <div className={cn(
                  "text-sm opacity-60 group-hover:opacity-100 transition-opacity",
                  selectedAction === action.id && action.id !== 'explore' && "opacity-90",
                  action.id === 'explore' && "text-neutral-500"
                )}>
                  {action.description}
                </div>
              </button>
            ))}
          </div>
        </motion.div>

        {/* Navigation */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="flex items-center justify-center pt-8"
        >
          <div className="flex items-center gap-8">
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-2 px-6 py-3 text-neutral-600 hover:text-neutral-900 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Home
            </button>

            <button
              onClick={handleContinue}
              disabled={!canProceed}
              className={cn(
                "flex items-center gap-2 px-8 py-4 rounded-lg font-medium transition-all duration-200",
                canProceed
                  ? "bg-neutral-900 text-white hover:bg-neutral-800 active:bg-neutral-900 hover:shadow-sm"
                  : "bg-neutral-200 text-neutral-400 cursor-not-allowed"
              )}
            >
              Next
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default PlanSelectionOnboarding;
