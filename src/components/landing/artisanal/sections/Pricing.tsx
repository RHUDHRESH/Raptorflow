"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { HugeiconsIcon } from "@hugeicons/react";
import { 
  CheckmarkCircle01Icon,
  CrownIcon,
  Coffee01Icon,
  Briefcase01Icon
} from "@hugeicons/core-free-icons";

const plans = [
  {
    name: "Espresso",
    description: "Perfect for solo creators and small projects",
    price: { monthly: 19, yearly: 15 },
    icon: Coffee01Icon,
    features: [
      "5 Active Workflows",
      "1,000 Executions/month",
      "Basic Integrations",
      "Email Support",
      "Community Access",
    ],
    cta: "Start Free Trial",
    popular: false,
  },
  {
    name: "Pour Over",
    description: "For growing teams who need more power",
    price: { monthly: 49, yearly: 39 },
    icon: Briefcase01Icon,
    features: [
      "Unlimited Workflows",
      "50,000 Executions/month",
      "Premium Integrations",
      "Priority Support",
      "Advanced Analytics",
      "Team Collaboration",
      "Custom Webhooks",
    ],
    cta: "Start Free Trial",
    popular: true,
  },
  {
    name: "Reserve",
    description: "Enterprise-grade for organizations at scale",
    price: { monthly: 149, yearly: 119 },
    icon: CrownIcon,
    features: [
      "Everything in Pour Over",
      "Unlimited Executions",
      "Dedicated Infrastructure",
      "SLA Guarantee",
      "Custom Integrations",
      "Dedicated Success Manager",
      "SSO & Advanced Security",
      "Audit Logs",
    ],
    cta: "Contact Sales",
    popular: false,
  },
];

export function Pricing() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const [isYearly, setIsYearly] = useState(true);

  useEffect(() => {
    if (!sectionRef.current) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        ".pricing-header",
        { y: 60, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.8,
          ease: "power3.out",
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top 80%",
            toggleActions: "play none none none",
          },
        }
      );

      gsap.fromTo(
        ".pricing-card",
        { y: 60, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.7,
          stagger: 0.15,
          ease: "power3.out",
          scrollTrigger: {
            trigger: ".pricing-grid",
            start: "top 80%",
            toggleActions: "play none none none",
          },
        }
      );
    });

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      id="pricing"
      className="relative py-32 bg-rock overflow-hidden"
    >
      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8">
        {/* Header */}
        <div className="pricing-header text-center max-w-3xl mx-auto mb-12">
          <span className="inline-block text-barley text-sm font-medium tracking-widest uppercase mb-4">
            Pricing
          </span>
          <h2 className="font-display text-4xl sm:text-5xl lg:text-6xl font-semibold text-shaft-500 mb-6 leading-tight">
            Simple, Transparent
            <span className="text-barley italic"> Pricing</span>
          </h2>
          <p className="text-shaft-400/70 text-lg leading-relaxed">
            Like a good coffee menu — no surprises, just quality at fair prices.
          </p>
        </div>

        {/* Toggle */}
        <div className="flex items-center justify-center gap-4 mb-16">
          <span className={`text-sm font-medium transition-colors duration-300 ${!isYearly ? "text-shaft-500" : "text-shaft-400/50"}`}>
            Monthly
          </span>
          <button
            onClick={() => setIsYearly(!isYearly)}
            className="relative w-16 h-8 rounded-full bg-shaft-200 transition-colors duration-300"
            data-cursor-hover
          >
            <div
              className={`absolute top-1 w-6 h-6 rounded-full bg-barley shadow-lg transition-all duration-300 ${
                isYearly ? "left-9" : "left-1"
              }`}
            />
          </button>
          <span className={`text-sm font-medium transition-colors duration-300 ${isYearly ? "text-shaft-500" : "text-shaft-400/50"}`}>
            Yearly
          </span>
          {isYearly && (
            <span className="px-3 py-1 rounded-full bg-barley/10 text-barley text-xs font-medium">
              Save 20%
            </span>
          )}
        </div>

        {/* Pricing Cards */}
        <div className="pricing-grid grid md:grid-cols-3 gap-8">
          {plans.map((plan) => {
            const Icon = plan.icon;
            return (
              <div
                key={plan.name}
                className={`pricing-card relative rounded-2xl p-8 transition-all duration-500 ${
                  plan.popular
                    ? "bg-shaft-500 text-rock scale-105 shadow-2xl shadow-shaft-500/20 border-2 border-barley/30"
                    : "bg-shaft-500/5 text-shaft-500 border border-shaft-200 hover:border-barley/30"
                }`}
                data-cursor-hover
              >
                {/* Popular Badge */}
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <span className="px-4 py-1.5 bg-barley text-shaft-500 text-sm font-semibold rounded-full">
                      Most Popular
                    </span>
                  </div>
                )}

                {/* Icon */}
                <div className={`w-14 h-14 rounded-xl flex items-center justify-center mb-6 ${
                  plan.popular ? "bg-barley/20" : "bg-barley/10"
                }`}>
                  <HugeiconsIcon icon={Icon} className={`w-7 h-7 ${plan.popular ? "text-barley" : "text-barley"}`} />
                </div>

                {/* Plan Name */}
                <h3 className="font-display text-2xl font-semibold mb-2">
                  {plan.name}
                </h3>
                <p className={`text-sm mb-6 ${plan.popular ? "text-rock/60" : "text-shaft-400/60"}`}>
                  {plan.description}
                </p>

                {/* Price */}
                <div className="mb-8">
                  <div className="flex items-baseline gap-1">
                    <span className="font-display text-5xl font-bold">
                      ${isYearly ? plan.price.yearly : plan.price.monthly}
                    </span>
                    <span className={`text-sm ${plan.popular ? "text-rock/50" : "text-shaft-400/50"}`}>
                      /month
                    </span>
                  </div>
                  {isYearly && (
                    <p className={`text-sm mt-1 ${plan.popular ? "text-barley" : "text-barley"}`}>
                      Billed annually
                    </p>
                  )}
                </div>

                {/* Features */}
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-3">
                      <HugeiconsIcon icon={CheckmarkCircle01Icon} className={`w-5 h-5 flex-shrink-0 mt-0.5 ${
                        plan.popular ? "text-barley" : "text-barley"
                      }`} />
                      <span className={`text-sm ${plan.popular ? "text-rock/80" : "text-shaft-400/80"}`}>
                        {feature}
                      </span>
                    </li>
                  ))}
                </ul>

                {/* CTA */}
                <button
                  className={`w-full py-4 rounded-xl font-semibold transition-all duration-300 ${
                    plan.popular
                      ? "bg-barley text-shaft-500 hover:bg-akaroa-300 hover:shadow-lg hover:shadow-barley/20"
                      : "bg-shaft-500 text-rock hover:bg-shaft-600"
                  }`}
                  data-cursor-hover
                >
                  {plan.cta}
                </button>
              </div>
            );
          })}
        </div>

        {/* Bottom Note */}
        <p className="text-center mt-12 text-shaft-400/50 text-sm">
          All plans include a 14-day free trial. No credit card required.
        </p>
      </div>
    </section>
  );
}
