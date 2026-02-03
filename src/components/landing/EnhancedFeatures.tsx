"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Compass, Brain, PenTool, Target, ArrowRight } from "lucide-react";
import { MagneticButton } from "@/components/effects/MagneticButton";
import { RevealOnScroll } from "@/components/effects/RevealOnScroll";
import { ParallaxImage } from "@/components/effects/ParallaxImage";

gsap.registerPlugin(ScrollTrigger);

const FEATURES = [
  {
    icon: Compass,
    title: "Marketing Foundation",
    subtitle: "Lay Your Strategic Groundwork",
    description:
      "Define your positioning, ideal customer profile, and messaging framework. Build the strategic foundation that guides all your marketing decisions.",
    highlights: ["ICP Definition", "Positioning Strategy", "Messaging Framework", "Channel Strategy"],
    image: "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=800&q=80",
  },
  {
    icon: Brain,
    title: "Cognitive Engine",
    subtitle: "AI That Understands Your Business",
    description:
      "Our stateful LangGraph-based engine performs deep business analysis. SWOT, PESTEL, Value Chain, and competitive intelligence—automated.",
    highlights: ["Business Analysis", "SWOT & PESTEL", "Competitive Intel", "Brand Archetypes"],
    image: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&q=80",
  },
  {
    icon: PenTool,
    title: "Muse",
    subtitle: "Create Content That Converts",
    description:
      "AI-powered content generation trained on your voice. LinkedIn posts, emails, blog posts, and campaigns—crafted in minutes, not hours.",
    highlights: ["Voice Training", "Multi-Channel Content", "Template Library", "Engagement Tracking"],
    image: "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=800&q=80",
  },
  {
    icon: Target,
    title: "Moves & Campaigns",
    subtitle: "Execute With Precision",
    description:
      "Weekly marketing moves and multi-channel campaigns. Track progress, measure results, and optimize your execution for maximum impact.",
    highlights: ["Weekly Moves", "Campaign Planning", "Performance Analytics", "Budget Tracking"],
    image: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80",
  },
];

export function EnhancedFeatures() {
  const router = useRouter();
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!sectionRef.current) return;

    const cards = sectionRef.current.querySelectorAll(".feature-card");

    const ctx = gsap.context(() => {
      cards.forEach((card, index) => {
        const image = card.querySelector(".feature-image");
        const content = card.querySelector(".feature-content");

        gsap.fromTo(
          card,
          { y: 80, opacity: 0 },
          {
            y: 0,
            opacity: 1,
            duration: 1,
            ease: "power3.out",
            scrollTrigger: {
              trigger: card,
              start: "top 85%",
              toggleActions: "play none none reverse",
            },
            delay: index * 0.1,
          }
        );

        // Parallax effect on images
        if (image) {
          gsap.to(image, {
            yPercent: 15,
            ease: "none",
            scrollTrigger: {
              trigger: card,
              start: "top bottom",
              end: "bottom top",
              scrub: true,
            },
          });
        }
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
        <RevealOnScroll animation="fadeUp" className="text-center mb-20">
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
        </RevealOnScroll>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {FEATURES.map((feature, index) => (
            <div
              key={index}
              className="feature-card group relative bg-[var(--bg-secondary)] border border-[var(--border)] rounded-2xl overflow-hidden hover:border-[var(--accent)] transition-all duration-500"
            >
              {/* Image with parallax */}
              <div className="relative h-56 overflow-hidden">
                <div className="feature-image absolute inset-0 scale-110">
                  <img
                    src={feature.image}
                    alt={feature.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
                  />
                </div>
                <div className="absolute inset-0 bg-gradient-to-t from-[var(--bg-secondary)] to-transparent" />

                {/* Icon badge */}
                <div className="absolute top-4 left-4 w-14 h-14 bg-[var(--bg-primary)]/90 backdrop-blur-sm rounded-xl flex items-center justify-center border border-[var(--border)] group-hover:border-[var(--accent)] transition-colors duration-300">
                  <feature.icon size={28} style={{ color: "var(--accent)" }} />
                </div>
              </div>

              {/* Content */}
              <div className="feature-content p-8">
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
                      className="px-3 py-1.5 bg-[var(--bg-primary)] border border-[var(--border)] rounded-full text-xs font-medium text-[var(--text-secondary)] group-hover:border-[var(--accent)]/50 transition-colors"
                    >
                      {highlight}
                    </span>
                  ))}
                </div>

                {/* Learn more link with magnetic effect */}
                <MagneticButton
                  strength={0.2}
                  onClick={() => router.push(`/features/${feature.title.toLowerCase().replace(/\s+/g, "-")}`)}
                  className="group/link inline-flex items-center gap-2 text-sm font-medium text-[var(--accent)] hover:text-[var(--accent-dark)] transition-colors"
                >
                  Learn more
                  <ArrowRight size={16} className="group-hover/link:translate-x-1 transition-transform" />
                </MagneticButton>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default EnhancedFeatures;
