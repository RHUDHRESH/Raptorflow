// Additional Strategy Wizard Steps (4-8)
// Import this into StrategyWizardEnhanced.jsx

import { useState } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import { ArrowLeft, ArrowRight, Sparkles, Loader2 } from 'lucide-react';
import { cn } from '../utils/cn';

const CHANNELS = [
  'Email', 'LinkedIn', 'Twitter/X', 'Instagram', 'Facebook', 
  'Events', 'Webinars', 'Content Marketing', 'SEO', 'Paid Ads',
  'Partnerships', 'Referrals', 'Cold Outreach', 'Other'
];

// Step 4: Markets & Channels
export const Step4Markets = ({ data, onChange, onNext, onBack }) => {
  const [markets, setMarkets] = useState(data.markets || []);
  const [selectedChannels, setSelectedChannels] = useState([]);
  const [mapCenter, setMapCenter] = useState([20, 0]);
  const [geography, setGeography] = useState('');

  const toggleChannel = (channel) => {
    if (selectedChannels.includes(channel)) {
      setSelectedChannels(selectedChannels.filter(c => c !== channel));
    } else {
      setSelectedChannels([...selectedChannels, channel]);
    }
  };

  const addMarket = () => {
    if (geography && selectedChannels.length > 0) {
      const newMarket = {
        geography,
        channels: selectedChannels,
        positioning: ''
      };
      const updated = [...markets, newMarket];
      setMarkets(updated);
      onChange({ markets: updated });
      setGeography('');
      setSelectedChannels([]);
    }
  };

  const handleNext = () => {
    if (markets.length > 0) {
      onNext();
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="mb-8">
        <h2 className="font-serif text-4xl mb-3">Markets & Channels</h2>
        <p className="text-neutral-600">Where do you play? How do you reach customers?</p>
      </div>

      {/* Existing markets */}
      {markets.length > 0 && (
        <div className="space-y-3 mb-6">
          {markets.map((market, index) => (
            <div key={index} className="runway-card p-4">
              <h4 className="font-semibold text-neutral-900">{market.geography}</h4>
              <div className="flex flex-wrap gap-2 mt-2">
                {market.channels.map(channel => (
                  <span
                    key={channel}
                    className="px-3 py-1 bg-neutral-100 text-neutral-700 text-sm rounded-full"
                  >
                    {channel}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add new market */}
      <div className="runway-card p-6 mb-8">
        <h4 className="font-semibold mb-4">Add Market</h4>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-neutral-900 mb-2">
              Geography
            </label>
            <input
              type="text"
              value={geography}
              onChange={(e) => setGeography(e.target.value)}
              placeholder="e.g., North America, Europe, Global"
              className="w-full px-4 py-2 border-2 border-neutral-200 rounded-lg focus:outline-none focus:border-neutral-900"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-neutral-900 mb-2">
              Channels (select all that apply)
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {CHANNELS.map(channel => (
                <label
                  key={channel}
                  className={cn(
                    "px-3 py-2 border-2 rounded-lg cursor-pointer text-sm transition-all",
                    selectedChannels.includes(channel)
                      ? "bg-neutral-900 text-white border-neutral-900"
                      : "border-neutral-200 hover:border-neutral-400"
                  )}
                >
                  <input
                    type="checkbox"
                    checked={selectedChannels.includes(channel)}
                    onChange={() => toggleChannel(channel)}
                    className="sr-only"
                  />
                  {channel}
                </label>
              ))}
            </div>
          </div>

          <button
            onClick={addMarket}
            disabled={!geography || selectedChannels.length === 0}
            className="runway-button-secondary px-4 py-2 w-full disabled:opacity-50"
          >
            Add Market
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
          disabled={markets.length === 0}
          className="runway-button-primary px-6 py-3 flex-1 disabled:opacity-50"
        >
          Continue
          <ArrowRight className="w-4 h-4 ml-2" />
        </button>
      </div>
    </div>
  );
};

// Step 5: Center of Gravity
export const Step5CenterOfGravity = ({ data, onChange, onNext, onBack }) => {
  const [value, setValue] = useState(data.center_of_gravity || '');
  const [aiSuggestion, setAiSuggestion] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  const generateSuggestion = async () => {
    setIsGenerating(true);
    // TODO: Integrate with AI service
    // For now, provide a placeholder
    setTimeout(() => {
      setAiSuggestion('Capture enterprise buyers in the AI/ML space who need compliance-ready solutions');
      setIsGenerating(false);
    }, 2000);
  };

  const handleNext = () => {
    if (value.trim()) {
      onChange({ center_of_gravity: value });
      onNext();
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div className="mb-8">
        <h2 className="font-serif text-4xl mb-3">Center of Gravity</h2>
        <p className="text-neutral-600">
          What is your <strong>ONE</strong> strategic focus right now? Not three things. One.
        </p>
      </div>

      <div className="runway-card p-6 mb-6">
        <p className="text-sm text-neutral-600 mb-4">
          Your center of gravity is the single point where you concentrate force. 
          It's not "grow revenue" or "improve product" — it's specific and directional.
        </p>
        <p className="text-sm text-neutral-700 font-semibold">
          Examples: "Dominate Series A SaaS companies in fintech" · "Own the conversation on AI compliance" · 
          "Become the default for [specific use case]"
        </p>
      </div>

      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        rows={4}
        placeholder="Our center of gravity is..."
        className="w-full px-4 py-3 border-2 border-neutral-200 rounded-lg focus:outline-none focus:border-neutral-900 font-serif text-lg mb-4"
      />

      {aiSuggestion && (
        <div className="runway-card p-4 bg-blue-50 border-blue-200 mb-4">
          <p className="text-sm font-semibold text-blue-900 mb-2">AI Suggestion:</p>
          <p className="text-blue-800">{aiSuggestion}</p>
          <button
            onClick={() => setValue(aiSuggestion)}
            className="text-sm text-blue-600 underline mt-2"
          >
            Use this suggestion
          </button>
        </div>
      )}

      <button
        onClick={generateSuggestion}
        disabled={isGenerating}
        className="runway-button-secondary px-4 py-2 mb-8 disabled:opacity-50"
      >
        {isGenerating ? (
          <>
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            Generating...
          </>
        ) : (
          <>
            <Sparkles className="w-4 h-4 mr-2" />
            Get AI Suggestion
          </>
        )}
      </button>

      <div className="flex gap-3">
        <button onClick={onBack} className="runway-button-secondary px-6 py-3">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </button>
        <button
          onClick={handleNext}
          disabled={!value.trim()}
          className="runway-button-primary px-6 py-3 flex-1 disabled:opacity-50"
        >
          Continue
          <ArrowRight className="w-4 h-4 ml-2" />
        </button>
      </div>
    </div>
  );
};

// Step 6: 90-Day Goal
export const Step6Goal = ({ data, onChange, onNext, onBack }) => {
  const [goal, setGoal] = useState(data.ninety_day_goal || '');
  const [primaryMetric, setPrimaryMetric] = useState(data.success_metrics?.primary_metric || '');
  const [targetValue, setTargetValue] = useState(data.success_metrics?.target_value || '');

  const handleNext = () => {
    if (goal.trim() && primaryMetric && targetValue) {
      onChange({
        ninety_day_goal: goal,
        success_metrics: {
          primary_metric: primaryMetric,
          target_value: targetValue,
          timeframe: '90 days'
        }
      });
      onNext();
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div className="mb-8">
        <h2 className="font-serif text-4xl mb-3">90-Day Goal</h2>
        <p className="text-neutral-600">What does winning look like in 90 days?</p>
      </div>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-semibold text-neutral-900 mb-2">
            Primary Goal
          </label>
          <textarea
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            rows={3}
            placeholder="e.g., Close 20 enterprise deals worth $500K ARR"
            className="w-full px-4 py-3 border-2 border-neutral-200 rounded-lg focus:outline-none focus:border-neutral-900"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-semibold text-neutral-900 mb-2">
              Primary Metric
            </label>
            <input
              type="text"
              value={primaryMetric}
              onChange={(e) => setPrimaryMetric(e.target.value)}
              placeholder="e.g., MRR, Deals Closed, Users"
              className="w-full px-4 py-3 border-2 border-neutral-200 rounded-lg focus:outline-none focus:border-neutral-900"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-neutral-900 mb-2">
              Target Value
            </label>
            <input
              type="text"
              value={targetValue}
              onChange={(e) => setTargetValue(e.target.value)}
              placeholder="e.g., $50K, 100 users"
              className="w-full px-4 py-3 border-2 border-neutral-200 rounded-lg focus:outline-none focus:border-neutral-900"
            />
          </div>
        </div>
      </div>

      <div className="flex gap-3 mt-8">
        <button onClick={onBack} className="runway-button-secondary px-6 py-3">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </button>
        <button
          onClick={handleNext}
          disabled={!goal.trim() || !primaryMetric || !targetValue}
          className="runway-button-primary px-6 py-3 flex-1 disabled:opacity-50"
        >
          Continue
          <ArrowRight className="w-4 h-4 ml-2" />
        </button>
      </div>
    </div>
  );
};

// Step 7: Constitution
export const Step7Constitution = ({ data, onChange, onNext, onBack }) => {
  const [toneGuidelines, setToneGuidelines] = useState(data.constitution?.tone_guidelines || []);
  const [forbiddenTactics, setForbiddenTactics] = useState(data.constitution?.forbidden_tactics || []);
  const [brandValues, setBrandValues] = useState(data.constitution?.brand_values || []);
  const [newTone, setNewTone] = useState('');
  const [newForbidden, setNewForbidden] = useState('');
  const [newValue, setNewValue] = useState('');

  const addTone = () => {
    if (newTone.trim()) {
      setToneGuidelines([...toneGuidelines, newTone]);
      setNewTone('');
    }
  };

  const addForbidden = () => {
    if (newForbidden.trim()) {
      setForbiddenTactics([...forbiddenTactics, newForbidden]);
      setNewForbidden('');
    }
  };

  const addValue = () => {
    if (newValue.trim()) {
      setBrandValues([...brandValues, newValue]);
      setNewValue('');
    }
  };

  const handleNext = () => {
    onChange({
      constitution: {
        tone_guidelines: toneGuidelines,
        forbidden_tactics: forbiddenTactics,
        brand_values: brandValues,
        constraints: []
      }
    });
    onNext();
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div className="mb-8">
        <h2 className="font-serif text-4xl mb-3">Constitution</h2>
        <p className="text-neutral-600">Your operational rules and constraints</p>
      </div>

      <div className="space-y-6">
        {/* Tone Guidelines */}
        <div className="runway-card p-6">
          <h4 className="font-semibold mb-3">Tone Guidelines</h4>
          <p className="text-sm text-neutral-600 mb-3">How should you sound?</p>
          <div className="flex gap-2 mb-3">
            <input
              type="text"
              value={newTone}
              onChange={(e) => setNewTone(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addTone()}
              placeholder="e.g., Professional but approachable"
              className="flex-1 px-3 py-2 border-2 border-neutral-200 rounded-lg focus:outline-none focus:border-neutral-900"
            />
            <button onClick={addTone} className="runway-button-secondary px-4 py-2">
              Add
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {toneGuidelines.map((tone, i) => (
              <span key={i} className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                {tone}
                <button
                  onClick={() => setToneGuidelines(toneGuidelines.filter((_, idx) => idx !== i))}
                  className="ml-2 text-blue-600 hover:text-blue-800"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Forbidden Tactics */}
        <div className="runway-card p-6">
          <h4 className="font-semibold mb-3">Forbidden Tactics</h4>
          <p className="text-sm text-neutral-600 mb-3">What will you never do?</p>
          <div className="flex gap-2 mb-3">
            <input
              type="text"
              value={newForbidden}
              onChange={(e) => setNewForbidden(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addForbidden()}
              placeholder="e.g., Spammy cold emails"
              className="flex-1 px-3 py-2 border-2 border-neutral-200 rounded-lg focus:outline-none focus:border-neutral-900"
            />
            <button onClick={addForbidden} className="runway-button-secondary px-4 py-2">
              Add
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {forbiddenTactics.map((tactic, i) => (
              <span key={i} className="px-3 py-1 bg-red-100 text-red-800 text-sm rounded-full">
                {tactic}
                <button
                  onClick={() => setForbiddenTactics(forbiddenTactics.filter((_, idx) => idx !== i))}
                  className="ml-2 text-red-600 hover:text-red-800"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Brand Values */}
        <div className="runway-card p-6">
          <h4 className="font-semibold mb-3">Brand Values</h4>
          <p className="text-sm text-neutral-600 mb-3">What do you stand for?</p>
          <div className="flex gap-2 mb-3">
            <input
              type="text"
              value={newValue}
              onChange={(e) => setNewValue(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addValue()}
              placeholder="e.g., Transparency, Innovation"
              className="flex-1 px-3 py-2 border-2 border-neutral-200 rounded-lg focus:outline-none focus:border-neutral-900"
            />
            <button onClick={addValue} className="runway-button-secondary px-4 py-2">
              Add
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {brandValues.map((value, i) => (
              <span key={i} className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                {value}
                <button
                  onClick={() => setBrandValues(brandValues.filter((_, idx) => idx !== i))}
                  className="ml-2 text-green-600 hover:text-green-800"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="flex gap-3 mt-8">
        <button onClick={onBack} className="runway-button-secondary px-6 py-3">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </button>
        <button onClick={handleNext} className="runway-button-primary px-6 py-3 flex-1">
          Review & Launch
          <ArrowRight className="w-4 h-4 ml-2" />
        </button>
      </div>
    </div>
  );
};

// Step 8: OH-SHIT Moment - Launch
export const Step8Launch = ({ data, onComplete, onBack, isSubmitting }) => {
  return (
    <div className="w-full max-w-5xl mx-auto">
      <div className="mb-12 text-center">
        <h2 className="font-serif text-5xl mb-4">Your Strategy is Ready</h2>
        <p className="text-xl text-neutral-600">Here's what we built together</p>
      </div>

      {/* Strategy Overview */}
      <div className="grid md:grid-cols-2 gap-6 mb-12">
        {/* Business */}
        <div className="runway-card p-6">
          <h4 className="font-semibold text-sm uppercase tracking-wider text-neutral-500 mb-3">
            Your Business
          </h4>
          <p className="font-serif text-2xl mb-2">{data.business_context?.company_name}</p>
          <p className="text-neutral-600">
            {data.business_context?.industry} · {data.business_context?.stage}
          </p>
        </div>

        {/* Offers */}
        <div className="runway-card p-6">
          <h4 className="font-semibold text-sm uppercase tracking-wider text-neutral-500 mb-3">
            Offers
          </h4>
          <p className="font-serif text-lg">{data.offers?.length || 0} Products/Services</p>
          <div className="text-sm text-neutral-600 mt-2">
            {data.offers?.map((offer, i) => (
              <div key={i}>{offer.name}</div>
            ))}
          </div>
        </div>

        {/* Center of Gravity */}
        <div className="runway-card p-6 md:col-span-2 bg-gradient-to-br from-blue-50 to-purple-50 border-2 border-blue-200">
          <h4 className="font-semibold text-sm uppercase tracking-wider text-blue-900 mb-3">
            Center of Gravity
          </h4>
          <p className="font-serif text-2xl text-blue-900">{data.center_of_gravity}</p>
        </div>

        {/* 90-Day Goal */}
        <div className="runway-card p-6 md:col-span-2">
          <h4 className="font-semibold text-sm uppercase tracking-wider text-neutral-500 mb-3">
            90-Day Goal
          </h4>
          <p className="font-serif text-xl mb-3">{data.ninety_day_goal}</p>
          <div className="flex gap-4 text-sm">
            <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full">
              {data.success_metrics?.primary_metric}: {data.success_metrics?.target_value}
            </span>
          </div>
        </div>
      </div>

      {/* Next Steps */}
      <div className="runway-card p-8 bg-neutral-900 text-white mb-8">
        <h3 className="font-serif text-3xl mb-6">What happens next?</h3>
        <div className="space-y-4">
          <div className="flex items-start gap-4">
            <div className="w-8 h-8 rounded-full bg-white text-neutral-900 flex items-center justify-center font-bold flex-shrink-0">
              1
            </div>
            <div>
              <p className="font-semibold">Sprint 1 Created</p>
              <p className="text-neutral-300 text-sm">Your first 14-day execution window is ready</p>
            </div>
          </div>
          <div className="flex items-start gap-4">
            <div className="w-8 h-8 rounded-full bg-white text-neutral-900 flex items-center justify-center font-bold flex-shrink-0">
              2
            </div>
            <div>
              <p className="font-semibold">Foundation Capabilities Unlocked</p>
              <p className="text-neutral-300 text-sm">Basic moves are now available in your arsenal</p>
            </div>
          </div>
          <div className="flex items-start gap-4">
            <div className="w-8 h-8 rounded-full bg-white text-neutral-900 flex items-center justify-center font-bold flex-shrink-0">
              3
            </div>
            <div>
              <p className="font-semibold">Create Your First Cohort</p>
              <p className="text-neutral-300 text-sm">Define your ideal customer profile to target</p>
            </div>
          </div>
        </div>
      </div>

      <div className="flex gap-3">
        <button onClick={onBack} className="runway-button-secondary px-6 py-3" disabled={isSubmitting}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </button>
        <button
          onClick={onComplete}
          disabled={isSubmitting}
          className="runway-button-primary px-8 py-4 flex-1 text-lg disabled:opacity-50"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Launching...
            </>
          ) : (
            <>
              Launch Your Campaign
              <ArrowRight className="w-5 h-5 ml-2" />
            </>
          )}
        </button>
      </div>
    </div>
  );
};

