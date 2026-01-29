import type { ChangeEvent, FormEvent } from 'react';
import { useState } from 'react';

type BusinessContextFormState = {
  brandName: string;
  tagline: string;
  corePromise: string;
  missionStatement: string;
  visionStatement: string;
  manifestoSummary: string;
  values: string;
  toneOfVoice: string;
  personalityTraits: string;
  primaryAudience: string;
  secondaryAudiences: string;
  painPoints: string;
  desires: string;
  challenges: string;
  goals: string;
  mediaConsumption: string;
  decisionFactors: string;
  marketCategory: string;
  marketSubcategory: string;
  differentiator: string;
  perceptualQuadrant: string;
  strategyPath: 'safe' | 'clever' | 'bold';
  positioningStatement: string;
  messagingCoreMessage: string;
  messagingValueProposition: string;
  messagingSupportingPoints: string;
  messagingProofPoints: string;
  messagingCallToAction: string;
  messagingToneGuidelines: string;
  competitiveMarketPosition: string;
  competitivePositioningStatement: string;
  primaryCompetitors: string;
  competitiveAdvantages: string;
  competitiveDifferentiators: string;
};

type SubmissionStatus = {
  type: 'idle' | 'success' | 'error';
  message?: string;
  details?: string[];
};

const initialState: BusinessContextFormState = {
  brandName: '',
  tagline: '',
  corePromise: '',
  missionStatement: '',
  visionStatement: '',
  manifestoSummary: '',
  values: '',
  toneOfVoice: '',
  personalityTraits: '',
  primaryAudience: '',
  secondaryAudiences: '',
  painPoints: '',
  desires: '',
  challenges: '',
  goals: '',
  mediaConsumption: '',
  decisionFactors: '',
  marketCategory: '',
  marketSubcategory: '',
  differentiator: '',
  perceptualQuadrant: '',
  strategyPath: 'safe',
  positioningStatement: '',
  messagingCoreMessage: '',
  messagingValueProposition: '',
  messagingSupportingPoints: '',
  messagingProofPoints: '',
  messagingCallToAction: '',
  messagingToneGuidelines: '',
  competitiveMarketPosition: '',
  competitivePositioningStatement: '',
  primaryCompetitors: '',
  competitiveAdvantages: '',
  competitiveDifferentiators: '',
};

const splitList = (value: string) =>
  value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);

const buildPayload = (state: BusinessContextFormState) => ({
  brand_name: state.brandName,
  tagline: state.tagline || null,
  core_promise: state.corePromise,
  mission_statement: state.missionStatement || null,
  vision_statement: state.visionStatement || null,
  manifesto_summary: state.manifestoSummary,
  values: splitList(state.values),
  tone_of_voice: splitList(state.toneOfVoice),
  personality_traits: splitList(state.personalityTraits),
  primary_audience: state.primaryAudience,
  secondary_audiences: splitList(state.secondaryAudiences),
  pain_points: splitList(state.painPoints),
  desires: splitList(state.desires),
  challenges: splitList(state.challenges),
  goals: splitList(state.goals),
  media_consumption: splitList(state.mediaConsumption),
  decision_factors: splitList(state.decisionFactors),
  market_category: state.marketCategory,
  market_subcategory: state.marketSubcategory || null,
  differentiator: state.differentiator,
  perceptual_quadrant: state.perceptualQuadrant,
  strategy_path: state.strategyPath,
  positioning_statement: state.positioningStatement,
  messaging_core_message: state.messagingCoreMessage,
  messaging_value_proposition: state.messagingValueProposition,
  messaging_supporting_points: splitList(state.messagingSupportingPoints),
  messaging_proof_points: splitList(state.messagingProofPoints),
  messaging_call_to_action: state.messagingCallToAction,
  messaging_tone_guidelines: splitList(state.messagingToneGuidelines),
  competitive_market_position: state.competitiveMarketPosition,
  competitive_positioning_statement: state.competitivePositioningStatement,
  primary_competitors: splitList(state.primaryCompetitors),
  competitive_advantages: splitList(state.competitiveAdvantages),
  competitive_differentiators: splitList(state.competitiveDifferentiators),
});

const validateForm = (state: BusinessContextFormState) => {
  const errors: string[] = [];
  if (state.brandName.trim().length < 2) errors.push('Brand name must be at least 2 characters.');
  if (state.corePromise.trim().length < 10) errors.push('Core promise must be at least 10 characters.');
  if (state.manifestoSummary.trim().length < 10) errors.push('Manifesto summary must be at least 10 characters.');
  if (state.primaryAudience.trim().length < 5) errors.push('Primary audience must be at least 5 characters.');
  if (splitList(state.painPoints).length < 2) errors.push('Add at least 2 pain points.');
  if (splitList(state.desires).length < 2) errors.push('Add at least 2 desires.');
  if (state.marketCategory.trim().length < 3) errors.push('Market category must be at least 3 characters.');
  if (state.differentiator.trim().length < 10) errors.push('Differentiator must be at least 10 characters.');
  if (state.perceptualQuadrant.trim().length < 3) errors.push('Perceptual quadrant is required.');
  if (state.positioningStatement.trim().length < 15) errors.push('Positioning statement must be at least 15 characters.');
  if (state.messagingCoreMessage.trim().length < 15) errors.push('Messaging core message must be at least 15 characters.');
  if (state.messagingValueProposition.trim().length < 10) {
    errors.push('Messaging value proposition must be at least 10 characters.');
  }
  if (state.messagingCallToAction.trim().length < 3) errors.push('Messaging CTA must be at least 3 characters.');
  if (state.competitiveMarketPosition.trim().length < 8) {
    errors.push('Competitive market position must be at least 8 characters.');
  }
  if (state.competitivePositioningStatement.trim().length < 15) {
    errors.push('Competitive positioning statement must be at least 15 characters.');
  }
  return errors;
};

export default function BusinessContextForm() {
  const [formState, setFormState] = useState(initialState);
  const [status, setStatus] = useState<SubmissionStatus>({ type: 'idle' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (field: keyof BusinessContextFormState) => (
    event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setFormState((prev) => ({ ...prev, [field]: event.target.value }));
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setStatus({ type: 'idle' });

    const validationErrors = validateForm(formState);
    if (validationErrors.length) {
      setStatus({ type: 'error', message: 'Fix the highlighted issues.', details: validationErrors });
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await fetch('/api/proxy/api/v1/business-contexts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(buildPayload(formState)),
      });
      const data = await response.json();
      if (!response.ok) {
        const errorDetails = data?.detail?.errors || data?.detail?.warnings || data?.detail?.message;
        setStatus({
          type: 'error',
          message: 'Unable to save business context.',
          details: Array.isArray(errorDetails) ? errorDetails : errorDetails ? [errorDetails] : undefined,
        });
        return;
      }
      setStatus({ type: 'success', message: data?.message || 'Business context saved.' });
      setFormState(initialState);
    } catch (error) {
      setStatus({
        type: 'error',
        message: 'Unexpected error while saving business context.',
        details: error instanceof Error ? [error.message] : undefined,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 mb-8">
      <div className="flex flex-col gap-2 mb-6">
        <h2 className="text-xl font-semibold text-gray-900">🧭 Business Context Intake</h2>
        <p className="text-sm text-gray-600">
          Capture the essentials needed to validate and persist a structured business context.
        </p>
      </div>

      {status.type !== 'idle' && (
        <div
          className={`mb-6 rounded-lg border px-4 py-3 text-sm ${
            status.type === 'success'
              ? 'border-green-200 bg-green-50 text-green-700'
              : 'border-red-200 bg-red-50 text-red-700'
          }`}
        >
          <p className="font-medium">{status.message}</p>
          {status.details && (
            <ul className="mt-2 list-disc list-inside space-y-1">
              {status.details.map((detail) => (
                <li key={detail}>{detail}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-8">
        <section className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Brand identity</h3>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <label className="text-sm text-gray-700">
              Brand name
              <input
                value={formState.brandName}
                onChange={handleChange('brandName')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                placeholder="RaptorFlow"
              />
            </label>
            <label className="text-sm text-gray-700">
              Tagline
              <input
                value={formState.tagline}
                onChange={handleChange('tagline')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                placeholder="Operations clarity for growth teams"
              />
            </label>
            <label className="text-sm text-gray-700 md:col-span-2">
              Core promise
              <textarea
                value={formState.corePromise}
                onChange={handleChange('corePromise')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                rows={2}
                placeholder="Describe the main promise delivered to customers."
              />
            </label>
            <label className="text-sm text-gray-700 md:col-span-2">
              Manifesto summary
              <textarea
                value={formState.manifestoSummary}
                onChange={handleChange('manifestoSummary')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                rows={2}
                placeholder="Summarize the brand manifesto."
              />
            </label>
            <label className="text-sm text-gray-700">
              Mission statement
              <textarea
                value={formState.missionStatement}
                onChange={handleChange('missionStatement')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                rows={2}
                placeholder="Optional mission statement."
              />
            </label>
            <label className="text-sm text-gray-700">
              Vision statement
              <textarea
                value={formState.visionStatement}
                onChange={handleChange('visionStatement')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                rows={2}
                placeholder="Optional vision statement."
              />
            </label>
            <label className="text-sm text-gray-700">
              Values (comma separated)
              <input
                value={formState.values}
                onChange={handleChange('values')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                placeholder="Transparency, speed, trust"
              />
            </label>
            <label className="text-sm text-gray-700">
              Tone of voice (comma separated)
              <input
                value={formState.toneOfVoice}
                onChange={handleChange('toneOfVoice')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                placeholder="Confident, helpful, direct"
              />
            </label>
            <label className="text-sm text-gray-700 md:col-span-2">
              Personality traits (comma separated)
              <input
                value={formState.personalityTraits}
                onChange={handleChange('personalityTraits')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                placeholder="Analytical, ambitious, pragmatic"
              />
            </label>
          </div>
        </section>

        <section className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Audience</h3>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <label className="text-sm text-gray-700 md:col-span-2">
              Primary audience
              <textarea
                value={formState.primaryAudience}
                onChange={handleChange('primaryAudience')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                rows={2}
                placeholder="Describe the primary audience segment."
              />
            </label>
            <label className="text-sm text-gray-700 md:col-span-2">
              Secondary audiences (comma separated)
              <input
                value={formState.secondaryAudiences}
                onChange={handleChange('secondaryAudiences')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                placeholder="Operations leaders, growth marketers"
              />
            </label>
            <label className="text-sm text-gray-700">
              Pain points (comma separated)
              <textarea
                value={formState.painPoints}
                onChange={handleChange('painPoints')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                rows={2}
                placeholder="Slow reporting, unclear priorities"
              />
            </label>
            <label className="text-sm text-gray-700">
              Desires (comma separated)
              <textarea
                value={formState.desires}
                onChange={handleChange('desires')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                rows={2}
                placeholder="Faster insights, confident decisions"
              />
            </label>
            <label className="text-sm text-gray-700">
              Challenges (comma separated)
              <input
                value={formState.challenges}
                onChange={handleChange('challenges')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                placeholder="Tool sprawl, resource constraints"
              />
            </label>
            <label className="text-sm text-gray-700">
              Goals (comma separated)
              <input
                value={formState.goals}
                onChange={handleChange('goals')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                placeholder="Predictable pipeline, measurable ROI"
              />
            </label>
            <label className="text-sm text-gray-700">
              Media consumption (comma separated)
              <input
                value={formState.mediaConsumption}
                onChange={handleChange('mediaConsumption')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                placeholder="LinkedIn, industry newsletters"
              />
            </label>
            <label className="text-sm text-gray-700">
              Decision factors (comma separated)
              <input
                value={formState.decisionFactors}
                onChange={handleChange('decisionFactors')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                placeholder="ROI proof, ease of onboarding"
              />
            </label>
          </div>
        </section>

        <section className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Market positioning</h3>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <label className="text-sm text-gray-700">
              Market category
              <input
                value={formState.marketCategory}
                onChange={handleChange('marketCategory')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                placeholder="Marketing operations platform"
              />
            </label>
            <label className="text-sm text-gray-700">
              Market subcategory
              <input
                value={formState.marketSubcategory}
                onChange={handleChange('marketSubcategory')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                placeholder="Workflow automation"
              />
            </label>
            <label className="text-sm text-gray-700 md:col-span-2">
              Differentiator
              <textarea
                value={formState.differentiator}
                onChange={handleChange('differentiator')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                rows={2}
                placeholder="Explain what makes you distinct."
              />
            </label>
            <label className="text-sm text-gray-700">
              Perceptual quadrant
              <input
                value={formState.perceptualQuadrant}
                onChange={handleChange('perceptualQuadrant')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                placeholder="High-touch / high-automation"
              />
            </label>
            <label className="text-sm text-gray-700">
              Strategy path
              <select
                value={formState.strategyPath}
                onChange={handleChange('strategyPath')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
              >
                <option value="safe">Safe</option>
                <option value="clever">Clever</option>
                <option value="bold">Bold</option>
              </select>
            </label>
            <label className="text-sm text-gray-700 md:col-span-2">
              Positioning statement
              <textarea
                value={formState.positioningStatement}
                onChange={handleChange('positioningStatement')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                rows={2}
                placeholder="Positioning statement for the market."
              />
            </label>
          </div>
        </section>

        <section className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Messaging framework</h3>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <label className="text-sm text-gray-700 md:col-span-2">
              Core message
              <textarea
                value={formState.messagingCoreMessage}
                onChange={handleChange('messagingCoreMessage')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                rows={2}
                placeholder="The one message you want customers to remember."
              />
            </label>
            <label className="text-sm text-gray-700 md:col-span-2">
              Value proposition
              <textarea
                value={formState.messagingValueProposition}
                onChange={handleChange('messagingValueProposition')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                rows={2}
                placeholder="Describe the value proposition."
              />
            </label>
            <label className="text-sm text-gray-700">
              Supporting points (comma separated)
              <input
                value={formState.messagingSupportingPoints}
                onChange={handleChange('messagingSupportingPoints')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                placeholder="Proof, ease, speed"
              />
            </label>
            <label className="text-sm text-gray-700">
              Proof points (comma separated)
              <input
                value={formState.messagingProofPoints}
                onChange={handleChange('messagingProofPoints')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                placeholder="Case studies, benchmarks"
              />
            </label>
            <label className="text-sm text-gray-700">
              Call to action
              <input
                value={formState.messagingCallToAction}
                onChange={handleChange('messagingCallToAction')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                placeholder="Book a strategy call"
              />
            </label>
            <label className="text-sm text-gray-700">
              Tone guidelines (comma separated)
              <input
                value={formState.messagingToneGuidelines}
                onChange={handleChange('messagingToneGuidelines')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                placeholder="Authoritative, practical"
              />
            </label>
          </div>
        </section>

        <section className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Competitive positioning</h3>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <label className="text-sm text-gray-700 md:col-span-2">
              Market position
              <textarea
                value={formState.competitiveMarketPosition}
                onChange={handleChange('competitiveMarketPosition')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                rows={2}
                placeholder="Describe current competitive position."
              />
            </label>
            <label className="text-sm text-gray-700 md:col-span-2">
              Competitive positioning statement
              <textarea
                value={formState.competitivePositioningStatement}
                onChange={handleChange('competitivePositioningStatement')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                rows={2}
                placeholder="How you position against competitors."
              />
            </label>
            <label className="text-sm text-gray-700">
              Primary competitors (comma separated)
              <input
                value={formState.primaryCompetitors}
                onChange={handleChange('primaryCompetitors')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                placeholder="Competitor A, Competitor B"
              />
            </label>
            <label className="text-sm text-gray-700">
              Competitive advantages (comma separated)
              <input
                value={formState.competitiveAdvantages}
                onChange={handleChange('competitiveAdvantages')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                placeholder="Faster setup, richer insights"
              />
            </label>
            <label className="text-sm text-gray-700 md:col-span-2">
              Differentiators (comma separated)
              <input
                value={formState.competitiveDifferentiators}
                onChange={handleChange('competitiveDifferentiators')}
                className="mt-1 w-full rounded border border-gray-300 px-3 py-2 text-sm"
                placeholder="Proactive guidance, automation"
              />
            </label>
          </div>
        </section>

        <div className="flex items-center justify-end gap-3">
          <button
            type="submit"
            disabled={isSubmitting}
            className="inline-flex items-center justify-center rounded bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSubmitting ? 'Saving...' : 'Save business context'}
          </button>
        </div>
      </form>
    </div>
  );
}
