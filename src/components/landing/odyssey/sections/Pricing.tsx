"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Link from "next/link";
import { Check, Sparkles } from "lucide-react";

const plans = [
  {
    name: "Explorer",
    description: "For solo founders just starting their journey",
    price: { monthly: 49, yearly: 39 },
    features: [
      "Strategic Foundation Builder",
      "5 Active Campaigns",
      "Basic AI Content Generation",
      "Email Support",
      "Community Access",
    ],
    cta: "Start Exploring",
    popular: false,
    gradient: "from-slate-500 to-slate-600",
  },
  {
    name: "Navigator",
    description: "For growing teams ready to scale",
    price: { monthly: 149, yearly: 119 },
    features: [
      "Everything in Explorer",
      "Unlimited Campaigns",
      "Advanced AI Content Suite",
      "Team Collaboration (5 seats)",
      "Priority Support",
      "Analytics Dashboard",
      "API Access",
    ],
    cta: "Start Navigating",
    popular: true,
    gradient: "from-purple-600 to-blue-600",
  },
  {
    name: "Voyager",
    description: "For enterprises with complex needs",
    price: { monthly: 399, yearly: 319 },
    features: [
      "Everything in Navigator",
      "Unlimited Team Seats",
      "Custom AI Training",
      "Dedicated Success Manager",
      "White-label Options",
      "Advanced Integrations",
      "SLA Guarantee",
    ],
    cta: "Contact Sales",
    popular: false,
    gradient: "from-amber-500 to-orange-500",
  },
];

export function Pricing() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const [isYearly, setIsYearly] = useState(true);

  useEffect(() => {
    if (!sectionRef.current) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        ".pricing-title",
        { y: 50, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.8,
          ease: "power3.out",
          scrollTrigger: {
            trigger: ".pricing-title",
            start: "top 80%",
            toggleActions: "play none none reverse",
          },
        }
      );

      const cards = sectionRef.current!.querySelectorAll(".pricing-card");
      gsap.fromTo(
        cards,
        { y: 60, opacity: 0, scale: 0.95 },
        {
          y: 0,
          opacity: 1,
          scale: 1,
          duration: 0.6,
          stagger: 0.15,
          ease: "power3.out",
          scrollTrigger: {
            trigger: ".pricing-grid",
            start: "top 80%",
            toggleActions: "play none none reverse",
          },
        }
      );
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      id="pricing"
      className="relative py-32 overflow-hidden"
    >
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-purple-900/10 to-transparent" />

      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8">
        {/* Section Header */}
        <div className="pricing-title text-center mb-16">
          <span className="inline-block px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-sm font-medium tracking-wide mb-6">
            Pricing
          </span>
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-6">
            Choose Your{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">
              Path
            </span>
          </h2>
          <p className="text-lg text-white/60 max-w-2xl mx-auto mb-10">
            Simple, transparent pricing. No hidden fees. Cancel anytime.
          </p>

          {/* Toggle */}
          <div className="inline-flex items-center gap-4 p-1.5 rounded-full bg-white/5 border border-white/10">
            <button
              onClick={() => setIsYearly(false)}
              className={`px-6 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
                !isYearly
                  ? "bg-white/10 text-white"
                  : "text-white/50 hover:text-white/70"
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setIsYearly(true)}
              className={`px-6 py-2 rounded-full text-sm font-medium transition-all duration-300 flex items-center gap-2 ${
                isYearly
                  ? "bg-gradient-to-r from-purple-500 to-blue-500 text-white"
                  : "text-white/50 hover:text-white/70"
              }`}
            >
              Yearly
              <span className="px-2 py-0.5 rounded-full bg-white/20 text-xs">
                Save 20%
              </span>
            </button>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="pricing-grid grid md:grid-cols-3 gap-6 lg:gap-8">
          {plans.map((plan, index) => (
            <div
              key={index}
              className={`pricing-card relative p-8 rounded-3xl ${
                plan.popular
                  ? "bg-gradient-to-b from-purple-500/20 to-blue-500/10 border-2 border-purple-500/30 scale-105 z-10"
                  : "bg-white/[0.03] border border-white/[0.08]"
              } backdrop-blur-sm`}
            >
              {/* Popular Badge */}
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <div className="px-4 py-1.5 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 text-white text-sm font-medium flex items-center gap-1.5 shadow-lg shadow-purple-500/25">
                    <Sparkles className="w-4 h-4" />
                    Most Popular
                  </div>
                </div>
              )}

              {/* Plan Header */}
              <div className="mb-8">
                <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                <p className="text-white/50 text-sm">{plan.description}</p>
              </div>

              {/* Price */}
              <div className="mb-8">
                <div className="flex items-baseline gap-2">
                  <span className="text-5xl font-bold text-white">
                    ${isYearly ? plan.price.yearly : plan.price.monthly}
                  </span>
                  <span className="text-white/50">/month</span>
                </div>
                {isYearly && (
                  <p className="text-emerald-400 text-sm mt-2">
                    Billed annually (${plan.price.yearly * 12}/year)
                  </p>
                )}
              </div>

              {/* Features */}
              <ul className="space-y-4 mb-8">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <div className={`p-1 rounded-full bg-gradient-to-br ${plan.gradient} mt-0.5`}>
                      <Check className="w-3 h-3 text-white" />
                    </div>
                    <span className="text-white/70 text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              {/* CTA */}
              <Link
                href={plan.popular ? "/signup" : "/signup"}
                className={`block w-full py-4 rounded-xl font-semibold text-center transition-all duration-300 ${
                  plan.popular
                    ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:shadow-lg hover:shadow-purple-500/25"
                    : "bg-white/10 text-white hover:bg-white/20 border border-white/10"
                }`}
              >
                {plan.cta}
              </Link>
            </div>
          ))}
        </div>

        {/* Enterprise Note */}
        <p className="text-center text-white/40 text-sm mt-12">
          Need something custom?{" "}
          <Link href="/contact" className="text-purple-400 hover:text-purple-300 transition-colors">
            Let's talk about Enterprise
          </Link>
        </p>
      </div>
    </section>
  );
}
