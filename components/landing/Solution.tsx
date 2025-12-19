"use client";

import { useEffect, useRef } from "react";
import { Sparkles, Target, Zap, BarChart3 } from "lucide-react";

/**
 * Solution Section - Editorial Layout
 *
 * Presents RaptorFlow as the answer with:
 * - Compelling value proposition
 * - Feature highlights with editorial cards
 * - Smooth scroll animations
 */

const features = [
  {
    icon: Sparkles,
    title: "AI Strategy Engine",
    description: "Muse generates tailored marketing strategies based on your product, market, and goals. Not templates. Real strategy.",
    highlight: "Powered by GPT-4",
  },
  {
    icon: Target,
    title: "Precision Positioning",
    description: "Define your ICP, craft your narrative, and build messaging that resonates. Every word intentional.",
    highlight: "Data-driven insights",
  },
  {
    icon: Zap,
    title: "Execution Velocity",
    description: "Move from strategy to action in minutes. Pre-built frameworks, automated workflows, zero friction.",
    highlight: "10x faster",
  },
  {
    icon: BarChart3,
    title: "Clear Metrics",
    description: "Track what matters. See the connection between effort and outcomes. Finally, ROI you can measure.",
    highlight: "Real-time dashboards",
  },
];

export function Solution() {
  const sectionRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("revealed");
          }
        });
      },
      { threshold: 0.1, rootMargin: "0px 0px -10% 0px" }
    );

    const revealElements = sectionRef.current?.querySelectorAll(".reveal");
    revealElements?.forEach((el) => observer.observe(el));

    return () => observer.disconnect();
  }, []);

  return (
    <section
      ref={sectionRef}
      id="solution"
      className="section-lg bg-base relative"
    >
      <div className="container-editorial">
        {/* Section header */}
        <div className="max-w-2xl mx-auto text-center mb-20">
          <span className="reveal text-label text-muted mb-4 block">
            The Solution
          </span>
          <h2 className="reveal stagger-1 text-display-xl text-primary mb-6">
            Your marketing command center
          </h2>
          <p className="reveal stagger-2 text-body-lg text-secondary">
            RaptorFlow brings structure, strategy, and speed to founder-led marketing.
            Think of it as having a world-class CMO on demand.
          </p>
        </div>

        {/* Features grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8">
          {features.map((feature, index) => (
            <div
              key={feature.title}
              className={`reveal stagger-${index + 1} group relative p-8 lg:p-10 rounded-2xl border border-hairline bg-elevated hover-lift`}
            >
              {/* Highlight badge */}
              <span className="absolute top-6 right-6 px-3 py-1 rounded-full bg-subtle text-label text-muted text-xs">
                {feature.highlight}
              </span>

              {/* Icon */}
              <div className="w-14 h-14 rounded-2xl bg-inverse flex items-center justify-center mb-6">
                <feature.icon className="w-7 h-7 text-inverse" strokeWidth={1.5} />
              </div>

              {/* Content */}
              <h3 className="text-display-md text-primary mb-4">
                {feature.title}
              </h3>
              <p className="text-body-md text-tertiary leading-relaxed max-w-md">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="reveal mt-16 text-center">
          <a
            href="/auth/signup"
            className="shimmer-button inline-flex items-center justify-center gap-2 h-12 px-6 rounded-lg bg-accent text-inverse text-body-sm font-medium transition-all duration-200 hover:bg-accent-hover active:scale-[0.98]"
          >
            Start Building Your Strategy
          </a>
        </div>
      </div>
    </section>
  );
}
