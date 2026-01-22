"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import gsap from "gsap";
import { Check, Compass, ArrowRight, ShieldCheck, Zap, BarChart3, BrainCircuit, Users, Globe } from "lucide-react";
import dynamic from 'next/dynamic';
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";

const BlueprintButton = dynamic(() => import("@/components/ui/BlueprintButton").then(mod => ({ default: mod.BlueprintButton })), { ssr: false });
const SecondaryButton = dynamic(() => import("@/components/ui/BlueprintButton").then(mod => ({ default: mod.SecondaryButton })), { ssr: false });

export const runtime = 'edge';

const PLANS = [
  {
    name: "Ascent",
    price: "Γé╣5,000",
    priceValue: 500000, // in paise
    desc: "Foundation for high-growth founders.",
    features: [
      "Full Brand Identity Audit",
      "Weekly 'Moves' Execution Plan",
      "Basic Muse AI Access",
      "3 Active Campaigns",
      "Market Intelligence Reports (Monthly)",
      "Single User Seat"
    ],
    code: "PLN-ASC",
    icon: Zap,
    popular: false
  },
  {
    name: "Glide",
    price: "Γé╣7,000",
    priceValue: 700000, // in paise
    desc: "Scale operations with AI precision.",
    features: [
      "Everything in Ascent",
      "Unlimited Campaigns",
      "Advanced Muse AI (GPT-4o)",
      "Competitor Radar Tracking",
      "Multi-Channel Attribution",
      "5 Team Seats",
      "Priority Support Channel"
    ],
    code: "PLN-GLD",
    icon: BarChart3,
    popular: true
  },
  {
    name: "Soar",
    price: "Γé╣10,000",
    priceValue: 1000000, // in paise
    desc: "Dominance for category leaders.",
    features: [
      "Everything in Glide",
      "Dedicated Growth Strategist",
      "Custom AI Model Fine-tuning",
      "White-label Reporting",
      "API Access & Integrations",
      "Unlimited Team Seats",
      "24/7 Concierge Support"
    ],
    code: "PLN-SOA",
    icon: BrainCircuit,
    popular: false
  }
];

export default function PricingPage() {
  const router = useRouter();
  const pageRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!pageRef.current) return;
    const tl = gsap.timeline({ defaults: { ease: "power2.out" } });
    tl.fromTo("[data-anim-hero]", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6 });
    tl.fromTo("[data-anim-card]", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.5, stagger: 0.1 }, "-=0.3");
  }, []);

  return (
    <div ref={pageRef} className="min-h-screen bg-[var(--canvas)] relative overflow-hidden">
      <div className="fixed inset-0 pointer-events-none z-0" style={{ backgroundImage: "url('/textures/paper-grain.png')", opacity: 0.05, mixBlendMode: "multiply" }} />
      <div className="fixed inset-0 blueprint-grid pointer-events-none z-0 opacity-10" />

      {/* Nav */}
      <div className="relative z-10 flex justify-between items-center px-8 py-6 max-w-7xl mx-auto">
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => router.push('/')}>
          <Compass size={24} /> <span className="font-serif font-bold text-lg">RaptorFlow</span>
        </div>
        <div className="flex gap-4">
          <button onClick={() => router.push('/login')} className="text-sm font-technical text-[var(--muted)] hover:text-[var(--ink)]">LOG IN</button>
        </div>
      </div>

      <div className="relative z-10 py-20 px-4">
        <div className="text-center mb-24" data-anim-hero>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-[var(--border)] bg-[var(--paper)] text-xs font-medium text-[var(--ink-secondary)] mb-6">
            <ShieldCheck size={12} />
            <span>HIGH-TICKET PARTNERSHIP</span>
          </div>
          <h1 className="font-serif text-6xl text-[var(--ink)] mb-6">Invest in Dominance.</h1>
          <p className="text-xl text-[var(--secondary)] max-w-2xl mx-auto font-light leading-relaxed">
            RaptorFlow isn&apos;t a tool. It&apos;s a strategic operating system designed to replace your agency.
          </p>
        </div>

        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
          {PLANS.map((plan, i) => (
            <div key={i} data-anim-card className={`relative ${plan.popular ? '-mt-6' : ''}`}>
              {plan.popular && (
                <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 z-20">
                  <BlueprintBadge variant="blackbox">RECOMMENDED</BlueprintBadge>
                </div>
              )}
              <BlueprintCard
                code={plan.code}
                showCorners
                padding="lg"
                variant={plan.popular ? "elevated" : "default"}
                className={`h-full flex flex-col ${plan.popular ? 'border-[var(--ink)] ring-1 ring-[var(--ink)] shadow-2xl' : 'border-[var(--border)]'}`}
              >
                <div className="mb-6">
                  <div className={`w-12 h-12 rounded-[var(--radius-md)] flex items-center justify-center mb-4 ${plan.popular ? 'bg-[var(--ink)] text-[var(--paper)]' : 'bg-[var(--surface)] text-[var(--ink)]'}`}>
                    <plan.icon size={24} strokeWidth={1.5} />
                  </div>
                  <h3 className="font-serif text-3xl text-[var(--ink)] mb-2">{plan.name}</h3>
                  <p className="text-sm text-[var(--secondary)]">{plan.desc}</p>
                </div>

                <div className="flex items-baseline gap-1 mb-8 pb-8 border-b border-[var(--border-subtle)]">
                  <span className="text-4xl font-bold text-[var(--ink)]">{plan.price}</span>
                  <span className="text-sm text-[var(--muted)]">/ year</span>
                </div>

                <div className="flex-1 space-y-4 mb-8">
                  {plan.features.map((feat, j) => (
                    <div key={j} className="flex items-start gap-3 text-sm text-[var(--ink)]">
                      <div className="mt-0.5 min-w-[16px]">
                        <Check size={16} strokeWidth={2} className="text-[var(--ink)]" />
                      </div>
                      <span className="leading-relaxed">{feat}</span>
                    </div>
                  ))}
                </div>

                <div className="mt-auto">
                  <BlueprintButton
                    variant={plan.popular ? "default" : "outline"}
                    className="w-full h-12 text-sm font-medium tracking-wide"
                    onClick={() => router.push('/signup')}
                  >
                    Select {plan.name}
                  </BlueprintButton>
                </div>
              </BlueprintCard>
            </div>
          ))}
        </div>

        <div className="max-w-4xl mx-auto mt-32 grid md:grid-cols-3 gap-8 text-center border-t border-[var(--border)] pt-16">
          <div>
            <h4 className="font-serif text-lg mb-2">Enterprise Grade</h4>
            <p className="text-sm text-[var(--secondary)]">SOC2 Compliant Security</p>
          </div>
          <div>
            <h4 className="font-serif text-lg mb-2">Dedicated Success</h4>
            <p className="text-sm text-[var(--secondary)]">Real human strategy support</p>
          </div>
          <div>
            <h4 className="font-serif text-lg mb-2">Data Sovereignty</h4>
            <p className="text-sm text-[var(--secondary)]">Your intelligence stays yours</p>
          </div>
        </div>
      </div>
    </div>
  );
}
