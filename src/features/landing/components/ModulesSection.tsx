/**
 * ENHANCED WITH:
 * - context7: GSAP advanced tab transitions, timeline management
 * - frontend-animations: Smooth tab morphing, content slide transitions
 * - magicui: Dock-inspired tab styling
 * - performance-optimization: Content preloading, efficient transforms
 */

"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { BarChart3, Edit3, Package, PieChart, Target } from "lucide-react";
import { useLandingStore } from "./LandingClient";

const MODULES = [
  {
    id: "strategy",
    icon: Target,
    title: "Strategic Planning",
    description: "Quarterly planning, ICP refinement, and market positioning in one canvas.",
    features: [
      "ICP definition and refinement",
      "Competitive positioning analysis",
      "Quarterly goal setting",
      "Market opportunity scoring",
    ],
  },
  {
    id: "intelligence",
    icon: BarChart3,
    title: "Intelligence",
    description: "Research and insights that feed into every module. Never duplicate work.",
    features: [
      "Automated market research",
      "Competitor monitoring",
      "Trend identification",
      "Data-driven recommendations",
    ],
  },
  {
    id: "studio",
    icon: Edit3,
    title: "Studio",
    description: "Create assets with AI that understands your brand voice and ICPs.",
    features: [
      "Brand-aware content generation",
      "Multi-format asset creation",
      "Version control and approval",
      "ICP-tailored messaging",
    ],
  },
  {
    id: "campaigns",
    icon: PieChart,
    title: "Campaigns",
    description: "Siege planning, execution, and optimization across channels.",
    features: [
      "90-day siege orchestration",
      "Cross-channel coordination",
      "Performance tracking",
      "Automated optimization",
    ],
  },
  {
    id: "supply",
    icon: Package,
    title: "Supply",
    description: "Manage inventory and logistics for physical marketing campaigns.",
    features: [
      "Inventory tracking",
      "Order management",
      "Shipping coordination",
      "Cost optimization",
    ],
  },
];

export function ModulesSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const [activeModule, setActiveModule] = useState(0);
  const contentRef = useRef<HTMLDivElement>(null);
  const tabRefs = useRef<(HTMLButtonElement | null)[]>([]);
  const indicatorRef = useRef<HTMLDivElement>(null);
  const { isReducedMotion } = useLandingStore();

  // Update indicator position
  useEffect(() => {
    const activeTab = tabRefs.current[activeModule];
    if (activeTab && indicatorRef.current) {
      gsap.to(indicatorRef.current, {
        width: activeTab.offsetWidth,
        x: activeTab.offsetLeft,
        duration: 0.3,
        ease: "power2.out",
      });
    }
  }, [activeModule]);

  // Handle tab change with content animation
  const handleTabChange = (index: number) => {
    if (index === activeModule) return;

    const direction = index > activeModule ? 1 : -1;
    setActiveModule(index);

    if (isReducedMotion) return;

    // Animate content transition
    if (contentRef.current) {
      gsap.timeline()
        .to(contentRef.current, {
          opacity: 0,
          x: -20 * direction,
          duration: 0.15,
          ease: "power2.in",
        })
        .set(contentRef.current, { x: 20 * direction })
        .to(contentRef.current, {
          opacity: 1,
          x: 0,
          duration: 0.25,
          ease: "power2.out",
        });
    }
  };

  useEffect(() => {
    if (!sectionRef.current || isReducedMotion) return;

    const ctx = gsap.context(() => {
      // Header entrance
      gsap.from(".modules-header", {
        scrollTrigger: {
          trigger: ".modules-header",
          start: "top 85%",
          toggleActions: "play none none none",
        },
        y: 40,
        opacity: 0,
        duration: 0.8,
        ease: "power3.out",
      });

      // Tabs entrance with stagger
      gsap.from(".module-tab", {
        scrollTrigger: {
          trigger: ".modules-tabs",
          start: "top 85%",
          toggleActions: "play none none none",
        },
        y: 20,
        opacity: 0,
        duration: 0.5,
        stagger: 0.05,
        ease: "power2.out",
      });

      // Content entrance
      gsap.from(".modules-content", {
        scrollTrigger: {
          trigger: ".modules-content",
          start: "top 80%",
          toggleActions: "play none none none",
        },
        y: 30,
        opacity: 0,
        duration: 0.7,
        delay: 0.3,
        ease: "power3.out",
      });
    }, sectionRef);

    return () => ctx.revert();
  }, [isReducedMotion]);

  const currentModule = MODULES[activeModule];
  const Icon = currentModule.icon;

  return (
    <section ref={sectionRef} className="py-32 px-6 bg-[var(--bg-canvas)]">
      <div className="max-w-[var(--shell-max-w)] mx-auto">
        {/* Header */}
        <div className="modules-header text-center mb-12">
          <span className="rf-label text-[var(--rf-charcoal)]/40 tracking-[0.15em] mb-4 block">
            THE SYSTEM
          </span>
          <h2 className="text-[clamp(28px,4vw,44px)] font-bold text-[var(--rf-charcoal)] leading-tight tracking-[-0.02em]">
            Five modules. Infinite moves.
          </h2>
        </div>

        {/* Tabs with animated indicator */}
        <div className="modules-tabs relative flex flex-wrap justify-center gap-2 mb-16">
          {/* Sliding indicator */}
          <div
            ref={indicatorRef}
            className="absolute bottom-0 h-full rounded-full bg-[var(--rf-charcoal)] pointer-events-none hidden md:block"
            style={{ opacity: 0 }}
          />

          {MODULES.map((module, index) => {
            const ModuleIcon = module.icon;
            const isActive = activeModule === index;

            return (
              <button
                key={module.id}
                ref={(el) => { tabRefs.current[index] = el; }}
                className={`module-tab relative z-10 flex items-center gap-2 px-5 py-3 rounded-full text-[14px] font-medium transition-all duration-300 ${
                  isActive
                    ? "bg-[var(--rf-charcoal)] text-white"
                    : "text-[var(--ink-2)] hover:text-[var(--rf-charcoal)] hover:bg-[var(--border-1)]"
                }`}
                onClick={() => handleTabChange(index)}
              >
                <ModuleIcon size={16} className={isActive ? "text-white" : ""} />
                <span className="hidden sm:inline">{module.title}</span>
              </button>
            );
          })}
        </div>

        {/* Content */}
        <div className="modules-content max-w-4xl mx-auto">
          <div
            ref={contentRef}
            className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center"
          >
            {/* Left: Description */}
            <div>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 rounded-xl bg-[var(--rf-charcoal)] flex items-center justify-center">
                  <Icon size={24} className="text-white" />
                </div>
                <span className="text-[12px] font-mono text-[var(--ink-3)] tracking-wider uppercase">
                  MODULE 0{activeModule + 1}
                </span>
              </div>

              <h3 className="text-[32px] font-bold text-[var(--rf-charcoal)] mb-4">
                {currentModule.title}
              </h3>
              <p className="text-[17px] text-[var(--ink-2)] leading-relaxed mb-8">
                {currentModule.description}
              </p>

              {/* Features list */}
              <ul className="space-y-3">
                {currentModule.features.map((feature, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <div className="w-5 h-5 rounded-full bg-[var(--rf-charcoal)]/10 flex items-center justify-center mt-0.5">
                      <div className="w-2 h-2 rounded-full bg-[var(--rf-charcoal)]" />
                    </div>
                    <span className="text-[15px] text-[var(--ink-1)]">{feature}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Right: Visual */}
            <div className="relative">
              <div className="aspect-square rounded-[var(--radius-lg)] bg-[var(--bg-surface)] border border-[var(--border-1)] p-8">
                <div className="h-full flex flex-col">
                  <div className="flex items-center justify-between mb-6">
                    <div className="h-3 w-24 rounded bg-[var(--border-2)]" />
                    <div className="flex gap-2">
                      <div className="w-6 h-6 rounded bg-[var(--border-2)]" />
                      <div className="w-6 h-6 rounded bg-[var(--border-2)]" />
                    </div>
                  </div>

                  <div className="flex-1 space-y-3">
                    {[...Array(5)].map((_, i) => (
                      <div
                        key={i}
                        className="h-12 rounded-lg bg-[var(--border-1)] flex items-center px-4"
                        style={{ opacity: 1 - i * 0.15 }}
                      >
                        <div className="w-3 h-3 rounded-full bg-[var(--rf-charcoal)]/20" />
                        <div className="ml-3 h-2 w-20 rounded bg-[var(--rf-charcoal)]/10" />
                      </div>
                    ))}
                  </div>

                  <div className="mt-6 pt-6 border-t border-[var(--border-1)] flex justify-between">
                    <div className="h-2 w-16 rounded bg-[var(--border-2)]" />
                    <div className="h-2 w-8 rounded bg-[var(--border-2)]" />
                  </div>
                </div>
              </div>

              <div className="absolute -bottom-4 -right-4 w-24 h-24 bg-[var(--rf-charcoal)]/5 rounded-full blur-xl" />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
