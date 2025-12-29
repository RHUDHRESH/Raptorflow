'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';
import { Button } from '@/components/ui/button';
import { supabase } from '@/lib/supabase';

type PlanFeature = {
  name: string;
  value?: string;
  included?: boolean;
};

type PricingPlan = {
  id?: string;
  name: string;
  price: number;
  description: string;
  features: PlanFeature[];
  cta: string;
  popular: boolean;
  currency?: string;
  billing_interval?: string;
};

const fallbackPlans: PricingPlan[] = [
  {
    name: 'Ascent',
    price: 5000,
    description: 'For founders just getting started with systematic marketing.',
    features: [
      { name: 'Active Campaigns', value: '3' },
      { name: 'Moves / month', value: '20' },
      { name: 'Move Generations', value: '60' },
      { name: 'Cohorts', value: '3' },
      { name: 'Matrix Access', included: true },
      { name: 'Blackbox (Lab A/B)', included: false },
      { name: 'Radar Access', included: false },
      { name: 'Support', value: 'Email' },
    ],
    cta: 'Start with Ascent',
    popular: false,
    currency: 'INR',
    billing_interval: 'monthly',
  },
  {
    name: 'Glide',
    price: 7000,
    description: 'For growing teams ready to scale their marketing machine.',
    features: [
      { name: 'Active Campaigns', value: '6' },
      { name: 'Moves / month', value: '60' },
      { name: 'Move Generations', value: '200' },
      { name: 'Cohorts', value: '6' },
      { name: 'Matrix Access', included: true },
      { name: 'Blackbox (Lab A/B)', included: true },
      { name: 'Radar Access', included: true },
      { name: 'Support', value: 'Priority' },
    ],
    cta: 'Start with Glide',
    popular: true,
    currency: 'INR',
    billing_interval: 'monthly',
  },
  {
    name: 'Soar',
    price: 10000,
    description: 'For serious operators running multiple campaigns at scale.',
    features: [
      { name: 'Active Campaigns', value: '9' },
      { name: 'Moves / month', value: '150' },
      { name: 'Move Generations', value: '700' },
      { name: 'Cohorts', value: '9' },
      { name: 'Matrix Access', included: true },
      { name: 'Blackbox (Lab A/B)', included: true },
      { name: 'Radar Access', included: true },
      { name: 'Support', value: 'Dedicated' },
    ],
    cta: 'Start with Soar',
    popular: false,
    currency: 'INR',
    billing_interval: 'monthly',
  },
];

const faqs = [
  {
    question: 'Can I change plans later?',
    answer:
      'Yes, you can upgrade or downgrade at any time. Changes take effect at the start of your next billing cycle.',
  },
  {
    question: 'What counts as a "Move"?',
    answer:
      'A Move is a single execution packet - one piece of content with its context, channel, and tracking. 20 Moves means you ship 20 pieces of marketing per month.',
  },
  {
    question: 'What is the difference between Moves and Move Generations?',
    answer:
      'Moves are what you ship. Move Generations are AI-generated options you can choose from. More generations = more options to find the perfect angle.',
  },
  {
    question: 'Is there a free trial?',
    answer:
      'Yes! All plans include a 14-day free trial. No credit card required to start.',
  },
];

export default function PricingPage() {
  const [plans, setPlans] = useState<PricingPlan[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [promoCode, setPromoCode] = useState('');
  const [activePlanId, setActivePlanId] = useState<string | null>(null);
  const router = useRouter();
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    async function loadPlans() {
      try {
        const response = await fetch(`${apiUrl}/v1/payments/plans`);
        if (!response.ok) {
          throw new Error('Failed to load plans.');
        }
        const payload = await response.json();
        const planList = payload?.data?.plans || [];
        const formatted = planList.map((plan: any) => ({
          id: plan.id,
          name: plan.name,
          price: Number(plan.price || 0),
          description: plan.description || '',
          features: formatPlanFeatures(plan),
          cta: `Start with ${plan.name}`,
          popular: plan.name?.toLowerCase() === 'glide',
          currency: plan.currency || 'INR',
          billing_interval: plan.billing_interval || 'monthly',
        }));
        setPlans(formatted);
        setErrorMessage(null);
      } catch (error: any) {
        setPlans([]);
        setErrorMessage(error?.message || 'Unable to load plans right now.');
      } finally {
        setIsLoading(false);
      }
    }

    loadPlans();
  }, [apiUrl]);

  const displayedPlans = plans.length ? plans : fallbackPlans;

  const handleCheckout = async (plan: PricingPlan) => {
    if (!plan.id) {
      setErrorMessage('Pricing is still loading. Please try again.');
      return;
    }

    setActivePlanId(plan.id);
    setErrorMessage(null);
    try {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!session) {
        router.push('/login');
        return;
      }

      const payload: Record<string, unknown> = {
        plan_id: plan.id,
        amount: plan.price,
        currency: plan.currency || 'INR',
        return_url: `${window.location.origin}/billing/success`,
      };

      const trimmedPromo = promoCode.trim();
      if (trimmedPromo) {
        payload.promo_code = trimmedPromo;
      }

      const response = await fetch(`${apiUrl}/v1/payments/create`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
          'X-Tenant-ID': session.user.id,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body?.detail || 'Failed to start payment.');
      }

      const data = await response.json();
      const paymentUrl = data?.payment_url;
      if (!paymentUrl) {
        throw new Error('Payment URL missing.');
      }

      window.location.href = paymentUrl;
    } catch (error: any) {
      setErrorMessage(error?.message || 'Payment failed to start.');
    } finally {
      setActivePlanId(null);
    }
  };

  return (
    <MarketingLayout>
      {/* Hero */}
      <section className="py-24 lg:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
              Pricing
            </p>
            <h1 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
              Simple, honest pricing.
            </h1>
            <p className="text-lg lg:text-xl text-muted-foreground leading-relaxed">
              No hidden fees. No surprise charges. Just marketing that
              compounds.
            </p>
          </div>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="pb-24 lg:pb-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center mb-10">
            <div className="inline-flex items-center gap-2 rounded-full border border-border px-4 py-2 text-xs text-muted-foreground">
              Live plans from your billing system
              {isLoading ? <span>Loading...</span> : null}
            </div>
            {errorMessage ? (
              <p className="mt-4 text-sm text-red-500">{errorMessage}</p>
            ) : null}
            <div className="mt-6 flex flex-col items-center gap-2">
              <label className="text-xs uppercase tracking-widest text-muted-foreground">
                Promo code
              </label>
              <input
                value={promoCode}
                onChange={(event) => setPromoCode(event.target.value)}
                placeholder="Enter promo code"
                className="h-11 w-full max-w-xs rounded-xl border border-border bg-card px-4 text-sm text-foreground"
              />
            </div>
          </div>
          <div className="grid lg:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {displayedPlans.map((plan) => (
              <div
                key={plan.name}
                className={`rounded-2xl border p-8 relative ${
                  plan.popular
                    ? 'border-2 border-foreground bg-card'
                    : 'border-border bg-card'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-foreground text-background px-4 py-1 rounded-full text-xs font-semibold uppercase tracking-wider">
                    Most Popular
                  </div>
                )}

                <div className={plan.popular ? 'mt-2' : ''}>
                  <h3 className="text-xl font-semibold">{plan.name}</h3>
                  <p className="mt-2 text-sm text-muted-foreground">
                    {plan.description}
                  </p>

                  <div className="mt-6 flex items-baseline">
                    <span className="text-4xl font-mono font-semibold">
                      {formatPrice(plan.price, plan.currency)}
                    </span>
                    <span className="ml-2 text-muted-foreground">
                      /{plan.billing_interval || 'month'}
                    </span>
                  </div>

                  <Button
                    className={`mt-8 w-full h-12 rounded-xl ${
                      plan.popular
                        ? ''
                        : 'bg-muted text-foreground hover:bg-muted/80'
                    }`}
                    variant={plan.popular ? 'default' : 'secondary'}
                    disabled={Boolean(activePlanId) || isLoading || !plan.id}
                    onClick={() => handleCheckout(plan)}
                  >
                    {activePlanId === plan.id ? 'Redirecting...' : plan.cta}
                  </Button>

                  <ul className="mt-8 space-y-4">
                    {plan.features.map((feature) => (
                      <li
                        key={feature.name}
                        className="flex items-center justify-between text-sm"
                      >
                        <span className="text-muted-foreground">
                          {feature.name}
                        </span>
                        {feature.included !== undefined ? (
                          feature.included ? (
                            <svg
                              className="h-5 w-5 text-green-600"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M5 13l4 4L19 7"
                              />
                            </svg>
                          ) : (
                            <svg
                              className="h-5 w-5 text-muted-foreground/50"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M6 18L18 6M6 6l12 12"
                              />
                            </svg>
                          )
                        ) : (
                          <span className="font-medium">{feature.value}</span>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Feature Comparison Quote */}
      <section className="border-y border-border bg-muted/30 py-16">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <blockquote className="mx-auto max-w-3xl text-center">
            <p className="text-2xl font-display font-medium text-foreground">
              &quot;Not another tool. A system: decide + ship + measure +
              iterate.&quot;
            </p>
          </blockquote>
        </div>
      </section>

      {/* Pricing FAQs */}
      <section className="py-24 lg:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-3xl">
            <h2 className="font-display text-3xl lg:text-4xl font-medium mb-12 text-center">
              Common Questions
            </h2>
            <div className="space-y-6">
              {faqs.map((faq) => (
                <div
                  key={faq.question}
                  className="rounded-xl border border-border bg-card p-6"
                >
                  <h3 className="font-semibold mb-2">{faq.question}</h3>
                  <p className="text-muted-foreground">{faq.answer}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="border-t border-border bg-foreground text-background py-24">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="font-display text-4xl font-medium mb-6">
              Start free. Upgrade when you are ready.
            </h2>
            <p className="text-lg text-background/70 mb-10">
              14-day trial on all plans. No credit card required.
            </p>
            <Button
              asChild
              size="lg"
              variant="secondary"
              className="h-14 px-8 text-base rounded-xl"
            >
              <Link href="/foundation">Get Started Free</Link>
            </Button>
          </div>
        </div>
      </section>
    </MarketingLayout>
  );
}

function formatPlanFeatures(plan: any): PlanFeature[] {
  const features = plan?.features || {};
  if (Array.isArray(features)) {
    return features;
  }

  const formatted: PlanFeature[] = [];
  Object.entries(features).forEach(([key, value]) => {
    if (typeof value === 'boolean') {
      formatted.push({ name: key, included: value });
      return;
    }
    formatted.push({ name: key, value: String(value) });
  });
  return formatted;
}

function formatPrice(amount: number, currency = 'INR') {
  const safeAmount = Number.isFinite(amount) ? amount : 0;
  const formatted = safeAmount.toLocaleString('en-IN', {
    maximumFractionDigits: 0,
  });
  return `${currency} ${formatted}`;
}
