"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Check, Sparkles } from "lucide-react";

gsap.registerPlugin(ScrollTrigger);

const PLANS = [
  {
    name: "Ascent",
    price: 5000,
    yearlyPrice: 50000,
    description: "For founders just getting started with systematic marketing.",
    features: [
      "Foundation setup (ICP + Positioning)",
      "Weekly Moves (3 per week)",
      "Basic Muse AI generation",
      "Matrix analytics dashboard",
      "3 Active Campaigns",
      "Email support",
      "Business Context Manifest",
    ],
    cta: "Start with Ascent",
    highlighted: false,
    popular: false,
  },
  {
    name: "Glide",
    price: 7000,
    yearlyPrice: 70000,
    description: "For founders scaling their marketing engine.",
    features: [
      "Everything in Ascent",
      "Unlimited Moves",
      "Advanced Muse (voice training)",
      "Cohort segmentation",
      "Campaign planning tools",
      "Priority support",
      "Blackbox learnings vault",
      "Competitive intelligence",
    ],
    cta: "Start with Glide",
    highlighted: true,
    popular: true,
  },
  {
    name: "Soar",
    price: 10000,
    yearlyPrice: 100000,
    description: "For teams running multi-channel campaigns.",
    features: [
      "Everything in Glide",
      "Unlimited Team seats (up to 5)",
      "White-label exports",
      "Custom AI training",
      "Full API access",
      "Dedicated success manager",
      "Custom integrations",
      "Advanced analytics",
    ],
    cta: "Contact Sales",
    highlighted: false,
    popular: false,
  },
];

export function Pricing() {
  const router = useRouter();
  const sectionRef = useRef<HTMLDivElement>(null);
  const [isAnnual, setIsAnnual] = useState(true);

  useEffect(() => {
    if (!sectionRef.current) return;

    const cards = sectionRef.current.querySelectorAll(".pricing-card");

    const ctx = gsap.context(() => {
      cards.forEach((card, index) => {
        gsap.fromTo(
          card,
          { y: 50, opacity: 0 },
          {
            y: 0,
            opacity: 1,
            duration: 0.8,
            ease: "power3.out",
            scrollTrigger: {
              trigger: card,
              start: "top 85%",
              toggleActions: "play none none reverse",
            },
            delay: index * 0.15,
          }
        );
      });
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(price);
  };

  const handlePlanSelect = (planName: string) => {
    router.push(`/signup?plan=${planName.toLowerCase()}`);
  };

  return (
    <section
      id="pricing"
      ref={sectionRef}
      className="relative py-32 bg-[var(--bg-primary)]"
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <span className="inline-block px-4 py-1.5 bg-[var(--bg-tertiary)] border border-[var(--border)] rounded-full text-xs font-semibold tracking-widest uppercase text-[var(--accent)] mb-6">
            Simple Pricing
          </span>
          <h2 className="font-display text-4xl md:text-5xl lg:text-6xl font-semibold text-[var(--text-primary)] mb-6">
            Invest in Clarity.
            <br />
            <span className="text-[var(--accent)]">Not Chaos.</span>
          </h2>
          <p className="text-lg text-[var(--text-secondary)] max-w-2xl mx-auto mb-10">
            Start now. No credit card required. Cancel anytime.
          </p>

          {/* Billing Toggle */}
          <div className="flex items-center justify-center gap-4">
            <span
              className={`text-sm font-medium transition-colors ${
                !isAnnual ? "text-[var(--text-primary)]" : "text-[var(--text-muted)]"
              }`}
            >
              Monthly
            </span>
            <button
              onClick={() => setIsAnnual(!isAnnual)}
              className={`relative w-14 h-7 rounded-full transition-colors ${
                isAnnual ? "bg-[var(--accent)]" : "bg-[var(--border)]"
              }`}
              aria-label="Toggle billing cycle"
            >
              <div
                className={`absolute top-1 w-5 h-5 rounded-full bg-white shadow transition-transform ${
                  isAnnual ? "translate-x-8" : "translate-x-1"
                }`}
              />
            </button>
            <span
              className={`text-sm font-medium transition-colors ${
                isAnnual ? "text-[var(--text-primary)]" : "text-[var(--text-muted)]"
              }`}
            >
              Annual
              <span className="ml-1.5 text-xs text-[var(--accent)]">(Save 20%)</span>
            </span>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-stretch">
          {PLANS.map((plan, index) => (
            <div
              key={index}
              className={`pricing-card relative flex flex-col rounded-2xl border transition-all duration-500 ${
                plan.highlighted
                  ? "bg-[var(--bg-secondary)] border-[var(--accent)] shadow-xl scale-105 z-10"
                  : "bg-[var(--bg-secondary)] border-[var(--border)] hover:border-[var(--border-strong)]"
              }`}
            >
              {/* Popular Badge */}
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <div className="flex items-center gap-1.5 px-4 py-1.5 bg-[var(--accent)] text-white text-xs font-bold uppercase tracking-wider rounded-full">
                    <Sparkles size={12} />
                    Most Popular
                  </div>
                </div>
              )}

              <div className="p-8 flex-1 flex flex-col">
                {/* Plan Header */}
                <div className="mb-6">
                  <h3 className="font-display text-2xl font-semibold text-[var(--text-primary)] mb-2">
                    {plan.name}
                  </h3>
                  <p className="text-sm text-[var(--text-muted)]">{plan.description}</p>
                </div>

                {/* Price */}
                <div className="mb-8">
                  <div className="flex items-baseline gap-1">
                    <span className="text-4xl font-bold text-[var(--text-primary)]">
                      {formatPrice(isAnnual ? plan.yearlyPrice / 12 : plan.price)}
                    </span>
                    <span className="text-[var(--text-muted)]">/month</span>
                  </div>
                  {isAnnual && (
                    <p className="text-xs text-[var(--text-muted)] mt-1">
                      Billed annually ({formatPrice(plan.yearlyPrice)}/year)
                    </p>
                  )}
                </div>

                {/* CTA Button */}
                <button
                  onClick={() => handlePlanSelect(plan.name)}
                  className={`w-full py-3.5 rounded-xl font-medium transition-all mb-8 ${
                    plan.highlighted
                      ? "bg-[var(--accent)] text-white hover:bg-[var(--accent-dark)]"
                      : "bg-[var(--bg-primary)] border border-[var(--border)] text-[var(--text-primary)] hover:border-[var(--accent)]"
                  }`}
                >
                  {plan.cta}
                </button>

                {/* Features */}
                <div className="flex-1">
                  <p className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)] mb-4">
                    What&apos;s included
                  </p>
                  <ul className="space-y-3">
                    {plan.features.map((feature, i) => (
                      <li key={i} className="flex items-start gap-3">
                        <div className="mt-0.5 flex-shrink-0 w-5 h-5 rounded-full bg-[var(--accent)]/10 flex items-center justify-center">
                          <Check size={12} className="text-[var(--accent)]" />
                        </div>
                        <span className="text-sm text-[var(--text-secondary)]">
                          {feature}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Enterprise Note */}
        <div className="mt-16 text-center">
          <p className="text-[var(--text-muted)]">
            Need a custom solution?{" "}
            <button
              onClick={() => router.push("/contact")}
              className="text-[var(--accent)] hover:underline font-medium"
            >
              Contact our sales team
            </button>
          </p>
        </div>
      </div>
    </section>
  );
}

export default Pricing;
