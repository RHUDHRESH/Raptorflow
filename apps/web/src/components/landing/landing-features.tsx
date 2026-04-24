"use client";

import * as React from "react";
import { Check } from "lucide-react";
import { GsapBridge } from "@/components/ui/gsap-bridge";

const features = [
  {
    title: "Know what your competitors are doing",
    description:
      "We monitor their ads, content, and moves. You get a weekly report on what's working for them — and where they're vulnerable.",
    icon: "target",
  },
  {
    title: "Never run out of content ideas",
    description:
      "We analyze what your customers are searching for, what your competitors missed, and hand you a content calendar every week.",
    icon: "pen",
  },
  {
    title: "Know exactly what to do next",
    description:
      "No more guessing. Every morning, you get 3 specific actions prioritized by impact. Do them, see results.",
    icon: "clipboard",
  },
  {
    title: "Works while you sleep",
    description:
      "Our team of AI agents researches, writes, and monitors 24/7. You wake up to finished work, not more tasks.",
    icon: "bolt",
  },
  {
    title: "Made for Indian markets",
    description:
      "We understand GST, UPI, WhatsApp Business, and the Indian buyer journey. No generic US playbook.",
    icon: "globe",
  },
  {
    title: "No long-term contracts",
    description:
      "Not happy? Get 100% cashback in the first 14 days. No questions, no retention calls. We're that confident.",
    icon: "shield",
  },
];

function FeatureIcon({ icon }: { icon: string }) {
  const iconClass = "w-5 h-5 text-[var(--primary)]";
  switch (icon) {
    case "target":
      return (
        <svg
          className={iconClass}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <circle cx="12" cy="12" r="10" />
          <circle cx="12" cy="12" r="6" />
          <circle cx="12" cy="12" r="2" />
        </svg>
      );
    case "pen":
      return (
        <svg
          className={iconClass}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <path d="M12 20h9" />
          <path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z" />
        </svg>
      );
    case "clipboard":
      return (
        <svg
          className={iconClass}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <rect x="9" y="2" width="6" height="4" rx="1" />
          <rect x="4" y="6" width="16" height="14" rx="2" />
          <path d="M9 12l2 2 4-4" />
        </svg>
      );
    case "bolt":
      return (
        <svg
          className={iconClass}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
        </svg>
      );
    case "globe":
      return (
        <svg
          className={iconClass}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <circle cx="12" cy="12" r="10" />
          <path d="M2 12h20" />
          <path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z" />
        </svg>
      );
    case "shield":
      return (
        <svg
          className={iconClass}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          <path d="M9 12l2 2 4-4" />
        </svg>
      );
    default:
      return <Check className={iconClass} />;
  }
}

export function LandingFeatures() {
  return (
    <section id="features" className="py-24 paper-soft">
      <GsapBridge stagger className="mx-auto max-w-6xl px-6 lg:px-8">
        <div className="gsap-reveal text-center max-w-3xl mx-auto mb-16">
          <p className="eyebrow mb-4">Capabilities</p>
          <h2 className="display-md mb-4">
            Everything you need to{" "}
            <span className="italic text-[var(--primary)]">win more customers</span>
          </h2>
          <p className="text-lg text-[var(--ink-500)]">
            No more juggling 10 tools or hiring expensive agencies. One platform. One price. Real
            results.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, i) => (
            <div
              key={i}
              className="gsap-reveal group p-6 rounded-[var(--radius-lg)] bg-white border border-[var(--border)] hover:border-[var(--primary)]/20 hover:shadow-md transition-all duration-300"
              style={{ animationDelay: `${i * 80}ms` }}
            >
              <div className="w-10 h-10 rounded-[var(--radius)] bg-[var(--amber-wash)] flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                <FeatureIcon icon={feature.icon} />
              </div>
              <h3 className="h3 mb-2">{feature.title}</h3>
              <p className="body-muted">{feature.description}</p>
            </div>
          ))}
        </div>
      </GsapBridge>
    </section>
  );
}
