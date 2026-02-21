/**
 * ENHANCED WITH:
 * - context7: GSAP pricing toggle animations, card reveals
 * - frontend-animations: Featured card glow, badge pulse
 * - magicui: ShineBorder-inspired featured card
 * - performance-optimization: GPU-accelerated transforms
 */

"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Check } from "lucide-react";
import { useLandingStore } from "./LandingClient";

const TIERS = [
  {
    name: "Essential",
    price: "49",
    priceDetail: "/user/month",
    description: "For solo operators who need to move fast.",
    features: [
      "Full access to all modules",
      "1 company workspace",
      "50 AI credits/month",
      "Email support",
    ],
    cta: "Start Free Trial",
    featured: false,
  },
  {
    name: "Growth",
    price: "99",
    priceDetail: "/user/month",
    description: "For scaling teams that need coordination.",
    features: [
      "Everything in Essential",
      "Unlimited workspaces",
      "250 AI credits/month",
      "Priority support",
      "Advanced analytics",
      "Team collaboration tools",
    ],
    cta: "Start Free Trial",
    featured: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    priceDetail: "",
    description: "For organizations with complex needs.",
    features: [
      "Everything in Growth",
      "Unlimited AI credits",
      "Dedicated success manager",
      "Custom integrations",
      "SLA guarantees",
      "On-premise deployment option",
    ],
    cta: "Contact Sales",
    featured: false,
  },
];

export function PricingSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const { isReducedMotion } = useLandingStore();

  useEffect(() => {
    if (!sectionRef.current || isReducedMotion) return;

    const ctx = gsap.context(() => {
      // Header animation
      gsap.from(".pricing-header", {
        scrollTrigger: {
          trigger: ".pricing-header",
          start: "top 85%",
          toggleActions: "play none none none",
        },
        y: 40,
        opacity: 0,
        duration: 0.8,
        ease: "power3.out",
      });

      // Cards stagger with featured card emphasis
      gsap.from(".pricing-card", {
        scrollTrigger: {
          trigger: ".pricing-grid",
          start: "top 80%",
          toggleActions: "play none none none",
        },
        y: 60,
        opacity: 0,
        duration: 0.8,
        stagger: 0.1,
        ease: "power3.out",
      });

      // Featured badge pulse animation
      gsap.to(".featured-badge", {
        scale: 1.05,
        duration: 1,
        ease: "sine.inOut",
        yoyo: true,
        repeat: -1,
      });

      // Hover effects (desktop)
      const mm = gsap.matchMedia();
      mm.add("(min-width: 768px)", () => {
        const cards = sectionRef.current?.querySelectorAll(".pricing-card");
        cards?.forEach((card) => {
          const isFeatured = card.classList.contains("featured");
          
          card.addEventListener("mouseenter", () => {
            gsap.to(card, {
              y: isFeatured ? -16 : -8,
              scale: isFeatured ? 1.02 : 1.01,
              duration: 0.3,
              ease: "power2.out",
            });
          });
          
          card.addEventListener("mouseleave", () => {
            gsap.to(card, {
              y: 0,
              scale: 1,
              duration: 0.3,
              ease: "power2.out",
            });
          });
        });
        
        return;
      });

      return () => mm.revert();
    }, sectionRef);

    return () => ctx.revert();
  }, [isReducedMotion]);

  return (
    <section ref={sectionRef} className="py-32 px-6 bg-[var(--bg-canvas)]">
      <div className="max-w-[var(--shell-max-w)] mx-auto">
        {/* Header */}
        <div className="pricing-header text-center mb-16">
          <span className="rf-label text-[var(--rf-charcoal)]/40 tracking-[0.15em] mb-4 block">
            PRICING
          </span>
          <h2 className="text-[clamp(28px,4vw,44px)] font-bold text-[var(--rf-charcoal)] leading-tight tracking-[-0.02em]">
            Simple pricing. No surprises.
          </h2>
          <p className="mt-6 text-[17px] text-[var(--ink-2)] max-w-lg mx-auto leading-relaxed">
            Start free. Upgrade when you need more power.
          </p>
        </div>

        {/* Pricing grid */}
        <div className="pricing-grid grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {TIERS.map((tier) => (
            <div
              key={tier.name}
              className={`pricing-card relative rounded-[var(--radius-md)] border p-8 flex flex-col will-change-transform ${
                tier.featured
                  ? "featured bg-[var(--rf-charcoal)] text-white border-[var(--rf-charcoal)]"
                  : "bg-[var(--bg-surface)] text-[var(--rf-charcoal)] border-[var(--border-1)] hover:border-[var(--rf-charcoal)]/20"
              }`}
            >
              {tier.featured && (
                <div className="featured-badge absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 bg-[var(--rf-charcoal)] text-white text-[11px] font-semibold rounded-full tracking-wider uppercase">
                  Most Popular
                </div>
              )}

              {/* Content */}
              <div className="mb-8">
                <h3
                  className={`text-[18px] font-semibold mb-2 ${
                    tier.featured ? "text-white" : "text-[var(--rf-charcoal)]"
                  }`}
                >
                  {tier.name}
                </h3>
                <div className="flex items-baseline gap-1 mb-3">
                  <span
                    className={`text-[48px] font-bold tracking-tight font-mono ${
                      tier.featured ? "text-white" : "text-[var(--rf-charcoal)]"
                    }`}
                  >
                    {tier.price}
                  </span>
                  {tier.priceDetail && (
                    <span
                      className={`text-[14px] ${
                        tier.featured ? "text-white/60" : "text-[var(--ink-2)]"
                      }`}
                    >
                      {tier.priceDetail}
                    </span>
                  )}
                </div>
                <p
                  className={`text-[15px] ${
                    tier.featured ? "text-white/70" : "text-[var(--ink-2)]"
                  }`}
                >
                  {tier.description}
                </p>
              </div>

              {/* Features */}
              <ul className="space-y-3 mb-8 flex-1">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-3">
                    <div
                      className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 ${
                        tier.featured ? "bg-white/20" : "bg-[var(--rf-charcoal)]/10"
                      }`}
                    >
                      <Check size={12} className={tier.featured ? "text-white" : "text-[var(--rf-charcoal)]"} />
                    </div>
                    <span
                      className={`text-[14px] ${
                        tier.featured ? "text-white/80" : "text-[var(--ink-1)]"
                      }`}
                    >
                      {feature}
                    </span>
                  </li>
                ))}
              </ul>

              {/* CTA */}
              <button
                className={`w-full py-3 rounded-lg text-[15px] font-medium transition-all duration-300 ${
                  tier.featured
                    ? "bg-white text-[var(--rf-charcoal)] hover:bg-white/90"
                    : "bg-[var(--rf-charcoal)] text-white hover:bg-[var(--rf-charcoal)]/90"
                }`}
              >
                {tier.cta}
              </button>
            </div>
          ))}
        </div>

        {/* Footer note */}
        <p className="mt-12 text-center text-[14px] text-[var(--ink-3)]">
          All plans include a 14-day free trial. No credit card required.
        </p>
      </div>
    </section>
  );
}
