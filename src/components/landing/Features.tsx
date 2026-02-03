"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import {
  Compass,
  Brain,
  PenTool,
  Target,
  ArrowRight
} from "lucide-react";
import { useRouter } from "next/navigation";

gsap.registerPlugin(ScrollTrigger);

const FEATURES = [
  {
    icon: Compass,
    title: "Marketing Foundation",
    subtitle: "Lay Your Strategic Groundwork",
    description:
      "Define your positioning, ideal customer profile, and messaging framework. Build the strategic foundation that guides all your marketing decisions.",
    highlights: ["ICP Definition", "Positioning Strategy", "Messaging Framework", "Channel Strategy"],
    color: "var(--accent)",
    image: "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=800&q=80",
  },
  {
    icon: Brain,
    title: "Cognitive Engine",
    subtitle: "AI That Understands Your Business",
    description:
      "Our stateful LangGraph-based engine performs deep business analysis. SWOT, PESTEL, Value Chain, and competitive intelligence—automated.",
    highlights: ["Business Analysis", "SWOT & PESTEL", "Competitive Intel", "Brand Archetypes"],
    color: "var(--accent)",
    image: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&q=80",
  },
  {
    icon: PenTool,
    title: "Muse",
    subtitle: "Create Content That Converts",
    description:
      "AI-powered content generation trained on your voice. LinkedIn posts, emails, blog posts, and campaigns—crafted in minutes, not hours.",
    highlights: ["Voice Training", "Multi-Channel Content", "Template Library", "Engagement Tracking"],
    color: "var(--accent)",
    image: "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=800&q=80",
  },
  {
    icon: Target,
    title: "Moves & Campaigns",
    subtitle: "Execute With Precision",
    description:
      "Weekly marketing moves and multi-channel campaigns. Track progress, measure results, and optimize your execution for maximum impact.",
    highlights: ["Weekly Moves", "Campaign Planning", "Performance Analytics", "Budget Tracking"],
    color: "var(--accent)",
    image: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80",
  },
];

export function Features() {
  const router = useRouter();
  const sectionRef = useRef<HTMLDivElement>(null);
  const cardsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!cardsRef.current) return;

    const cards = cardsRef.current.querySelectorAll(".feature-card");

    const ctx = gsap.context(() => {
      cards.forEach((card, index) => {
        gsap.fromTo(
          card,
          { y: 60, opacity: 0 },
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
            delay: index * 0.1,
          }
        );
      });
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      id="features"
      ref={sectionRef}
      className="relative py-32 bg-[var(--bg-primary)]"
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-20">
          <span className="inline-block px-4 py-1.5 bg-[var(--bg-tertiary)] border border-[var(--border)] rounded-full text-xs font-semibold tracking-widest uppercase text-[var(--accent)] mb-6">
            The Complete System
          </span>
          <h2 className="font-display text-4xl md:text-5xl lg:text-6xl font-semibold text-[var(--text-primary)] mb-6">
            Everything You Need to
            <br />
            <span className="text-[var(--accent)]">Navigate Growth</span>
          </h2>
          <p className="text-lg text-[var(--text-secondary)] max-w-2xl mx-auto">
            Four interconnected pillars that transform how you approach marketing—from
            strategic foundation to AI-powered execution.
          </p>
        </div>

        {/* Features Grid */}
        <div ref={cardsRef} className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {FEATURES.map((feature, index) => (
            <div
              key={index}
              className="feature-card group relative bg-[var(--bg-secondary)] border border-[var(--border)] rounded-2xl overflow-hidden hover:border-[var(--accent)] transition-all duration-500"
            >
              {/* Image */}
              <div className="relative h-48 overflow-hidden">
                <img
                  src={feature.image}
                  alt={feature.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[var(--bg-secondary)] to-transparent" />

                {/* Icon badge */}
                <div className="absolute top-4 left-4 w-12 h-12 bg-[var(--bg-primary)]/90 backdrop-blur-sm rounded-xl flex items-center justify-center border border-[var(--border)]">
                  <feature.icon size={24} style={{ color: feature.color }} />
                </div>
              </div>

              {/* Content */}
              <div className="p-8">
                <span className="text-xs font-semibold tracking-widest uppercase text-[var(--accent)] mb-2 block">
                  {feature.subtitle}
                </span>
                <h3 className="font-display text-2xl font-semibold text-[var(--text-primary)] mb-3">
                  {feature.title}
                </h3>
                <p className="text-[var(--text-secondary)] mb-6 leading-relaxed">
                  {feature.description}
                </p>

                {/* Highlights */}
                <div className="flex flex-wrap gap-2 mb-6">
                  {feature.highlights.map((highlight, i) => (
                    <span
                      key={i}
                      className="px-3 py-1 bg-[var(--bg-primary)] border border-[var(--border)] rounded-full text-xs font-medium text-[var(--text-secondary)]"
                    >
                      {highlight}
                    </span>
                  ))}
                </div>

                {/* Learn more link */}
                <button
                  onClick={() => router.push(`/features/${feature.title.toLowerCase().replace(/\s+/g, "-")}`)}
                  className="group/link inline-flex items-center gap-2 text-sm font-medium text-[var(--accent)] hover:text-[var(--accent-dark)] transition-colors"
                >
                  Learn more
                  <ArrowRight size={16} className="group-hover/link:translate-x-1 transition-transform" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default Features;
