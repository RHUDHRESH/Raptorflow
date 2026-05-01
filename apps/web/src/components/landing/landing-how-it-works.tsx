"use client";

import * as React from "react";
import { ArrowRight } from "lucide-react";
import { GsapBridge } from "@/components/ui/gsap-bridge";

const steps = [
  {
    number: "01",
    title: "Tell us about your business",
    description: "Fill out the foundation. We learn your product, customers, and competitors.",
  },
  {
    number: "02",
    title: "We go to work immediately",
    description:
      "Our AI team researches your market, analyzes competitors, and builds your first campaign within 24 hours.",
  },
  {
    number: "03",
    title: "Get your morning briefing",
    description:
      "Every day: 3 prioritized actions. Every week: content calendar. Every month: smarter strategy.",
  },
];

export function LandingHowItWorks() {
  return (
    <section id="how-it-works" className="py-24 bg-[var(--paper-150)] paper-soft">
      <GsapBridge stagger className="mx-auto max-w-6xl px-6 lg:px-8">
        <div className="gsap-reveal text-center max-w-3xl mx-auto mb-16">
          <p className="eyebrow mb-4">Process</p>
          <h2 className="display-md mb-4">
            Get started in <span className="italic text-[var(--primary)]">minutes</span>
          </h2>
          <p className="text-lg text-[var(--ink-500)]">
            No onboarding calls. No agency meetings. Just answer questions and watch us work.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((step, i) => (
            <div key={i} className="gsap-reveal relative">
              {i < steps.length - 1 && (
                <div className="hidden md:block absolute top-12 left-full w-full h-px bg-[var(--border)]">
                  <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-[var(--primary)]" />
                </div>
              )}

              <div className="bg-white rounded-[var(--radius-lg)] p-8 border border-[var(--border)] h-full card-elevated">
                <div className="text-5xl font-bold text-[var(--paper-300)] mb-4 font-display">
                  {step.number}
                </div>
                <h3 className="h2 mb-3">{step.title}</h3>
                <p className="body-muted">{step.description}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="gsap-reveal text-center mt-12">
          <a href="/sign-up" className="btn-primary px-8 py-4 text-base shadow-lg">
            Create your account
            <ArrowRight className="w-5 h-5" />
          </a>
        </div>
      </GsapBridge>
    </section>
  );
}
