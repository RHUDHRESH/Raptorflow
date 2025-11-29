import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Check, ArrowRight, Zap, Shield, TrendingUp } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { LuxeButton, LuxeHeading } from '../components/ui/PremiumUI';
import { pageTransition, fadeInUp } from '../utils/animations';

const PricingCard = ({ title, price, features, isPopular, onSubscribe, loading }) => (
  <div className={`relative p-8 border-2 flex flex-col h-full transition-transform hover:-translate-y-2 duration-300 ${isPopular ? 'border-black bg-black text-white scale-105 shadow-2xl z-10' : 'border-black/10 bg-white text-black'}`}>
    {isPopular && (
      <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-white text-black px-4 py-1 text-xs font-bold uppercase tracking-widest border-2 border-black shadow-lg">
        Most Popular
      </div>
    )}
    <div className="mb-8">
      <h3 className="text-xl font-bold uppercase tracking-widest mb-4">{title}</h3>
      <div className="flex items-baseline gap-1">
        <span className="text-5xl font-display font-black">{price}</span>
        <span className="opacity-60">/mo</span>
      </div>
    </div>
    <div className="flex-1 mb-8 space-y-4">
      {features.map((feat, i) => (
        <div key={i} className="flex items-start gap-3">
          <Check className={`w-5 h-5 flex-shrink-0 ${isPopular ? 'text-green-400' : 'text-black'}`} />
          <span className="text-sm leading-tight opacity-80">{feat}</span>
        </div>
      ))}
    </div>
    <LuxeButton
      onClick={onSubscribe}
      variant={isPopular ? 'secondary' : 'primary'}
      className="w-full"
      disabled={loading}
      isLoading={loading}
    >
      Subscribe Now
    </LuxeButton>
  </div>
);

const OnboardingPricing = () => {
  const { user, subscription } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubscribe = async (plan) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_API_URL}/payments/checkout/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${(await import('../lib/supabase').then(m => m.supabase.auth.getSession())).data.session?.access_token}`
        },
        body: JSON.stringify({
          plan: plan.toLowerCase(),
          billing_period: 'monthly',
          success_url: `${window.location.origin}/dashboard`,
          cancel_url: `${window.location.origin}/onboarding-pricing`
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to initiate checkout');
      }

      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        throw new Error('No checkout URL returned');
      }
    } catch (err) {
      console.error('Checkout error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      className="min-h-screen bg-[#f8f8f8] py-20 px-4 sm:px-6 lg:px-8"
      initial="initial"
      animate="animate"
      exit="exit"
      variants={pageTransition}
    >
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <LuxeHeading level={1} className="mb-4">Choose Your Plan</LuxeHeading>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Select the plan that fits your growth stage. Unlock the full power of RaptorFlow.
          </p>
        </div>

        {error && (
          <div className="max-w-md mx-auto mb-8 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-center">
            {error}
          </div>
        )}

        <div className="grid md:grid-cols-3 gap-8 items-start max-w-6xl mx-auto">
          <PricingCard
            title="Ascent"
            price="₹3,500"
            features={['3 Active Cohorts', 'Weekly Strategy Moves', 'Basic Analytics', 'Email Support']}
            onSubscribe={() => handleSubscribe('ascent')}
            loading={loading}
          />
          <PricingCard
            title="Glide"
            price="₹7,000"
            features={['6 Active Cohorts', 'Advanced Moves Planner', 'AI Tone Guardian', 'Priority Support', 'Team Access (3 Seats)']}
            isPopular
            onSubscribe={() => handleSubscribe('glide')}
            loading={loading}
          />
          <PricingCard
            title="Soar"
            price="₹10,000"
            features={['Unlimited Cohorts', 'Full Command Center', 'Agency Whitelabeling', 'Dedicated Manager', 'API Access']}
            onSubscribe={() => handleSubscribe('soar')}
            loading={loading}
          />
        </div>

        <div className="mt-16 text-center">
          <p className="text-gray-500 text-sm">
            Secure payment via PhonePe. Cancel anytime.
          </p>
        </div>
      </div>
    </motion.div>
  );
};

export default OnboardingPricing;
