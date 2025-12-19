"use client";

import { useEffect, useRef } from "react";
import { Brain, Crosshair, Rocket, LineChart, MessageSquare, Compass } from "lucide-react";

/**
 * OperatingSystem Section - How It Works
 *
 * Shows the RaptorFlow methodology with:
 * - Step-by-step process visualization
 * - Editorial numbered list design
 * - Premium card treatments
 */

const modules = [
  {
    number: "01",
    icon: Brain,
    title: "Muse",
    subtitle: "AI Strategy Generator",
    description: "Input your context, get tailored marketing strategies. Muse analyzes your product, market, and competitors to craft actionable plans.",
  },
  {
    number: "02",
    icon: Crosshair,
    title: "Position",
    subtitle: "Market Positioning",
    description: "Define your ICP with precision. Build messaging that cuts through noise. Create a positioning that competitors can't copy.",
  },
  {
    number: "03",
    icon: Rocket,
    title: "Moves",
    subtitle: "Execution Framework",
    description: "Transform strategy into daily actions. Pre-built playbooks, content calendars, and launch sequences ready to deploy.",
  },
  {
    number: "04",
    icon: MessageSquare,
    title: "Campaigns",
    subtitle: "Multi-Channel Orchestration",
    description: "Plan, execute, and track campaigns across channels. LinkedIn, Twitter, Email, Product Hunt - all coordinated.",
  },
  {
    number: "05",
    icon: LineChart,
    title: "Radar",
    subtitle: "Intelligence Dashboard",
    description: "See what's working in real-time. Track metrics that matter. Adjust strategy based on data, not gut feelings.",
  },
  {
    number: "06",
    icon: Compass,
    title: "Matrix",
    subtitle: "Strategic Overview",
    description: "The bird's eye view of your marketing operation. Priorities, dependencies, and opportunities at a glance.",
  },
];

export function OperatingSystem() {
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
      id="how-it-works"
      className="section-lg bg-inverse text-inverse relative overflow-hidden"
    >
      {/* Subtle grid pattern */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
                           linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
          backgroundSize: "64px 64px",
        }}
        aria-hidden="true"
      />

      <div className="container-editorial relative z-10">
        {/* Section header */}
        <div className="max-w-2xl mx-auto text-center mb-20">
          <span className="reveal text-label text-muted mb-4 block opacity-60">
            The Operating System
          </span>
          <h2 className="reveal stagger-1 text-display-xl mb-6">
            Six modules. One system.
          </h2>
          <p className="reveal stagger-2 text-body-lg opacity-70">
            Each module serves a specific purpose in your marketing journey.
            Together, they form a complete operating system for growth.
          </p>
        </div>

        {/* Modules grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {modules.map((module, index) => (
            <div
              key={module.title}
              className={`reveal stagger-${Math.min(index + 1, 6)} group relative p-8 rounded-2xl bg-white/[0.04] border border-white/[0.08] backdrop-blur-sm transition-all duration-300 hover:bg-white/[0.08] hover:border-white/[0.12]`}
            >
              {/* Number badge */}
              <span className="absolute top-6 right-6 text-label text-white/30 font-mono">
                {module.number}
              </span>

              {/* Icon */}
              <div className="w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center mb-6 transition-colors duration-200 group-hover:bg-white/20">
                <module.icon className="w-6 h-6 text-white/80" strokeWidth={1.5} />
              </div>

              {/* Content */}
              <div className="mb-4">
                <h3 className="text-display-sm mb-1">
                  {module.title}
                </h3>
                <span className="text-body-sm text-white/50">
                  {module.subtitle}
                </span>
              </div>
              <p className="text-body-sm text-white/60 leading-relaxed">
                {module.description}
              </p>
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="reveal mt-16 text-center">
          <p className="text-body-lg opacity-70 mb-6">
            Ready to systematize your marketing?
          </p>
          <a
            href="/auth/signup"
            className="inline-flex items-center justify-center h-14 px-8 rounded-lg bg-white text-black text-body-md font-medium transition-all duration-200 hover:bg-white/90 active:scale-[0.98]"
          >
            Get Started Free
          </a>
        </div>
      </div>
    </section>
  );
}
