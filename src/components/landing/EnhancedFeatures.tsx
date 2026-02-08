"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { ArrowRight } from "lucide-react";
import { MagneticButton } from "@/components/effects/MagneticButton";
import { RevealOnScroll } from "@/components/effects/RevealOnScroll";
import { ParallaxImage } from "@/components/effects/ParallaxImage";
import { MARKETING_FEATURES } from "@/lib/marketingFeatures";

gsap.registerPlugin(ScrollTrigger);

const FEATURES = MARKETING_FEATURES;

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
                  onClick={() => router.push(`/features/${feature.slug}`)}
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
