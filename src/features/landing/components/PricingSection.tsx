"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { Check } from "lucide-react";
import { useLandingStore } from "./LandingClient";

const TIERS = [
  {
    name: "Essential",
    price: "49",
    priceDetail: "/mo",
    description: "For solo operators who need to move fast.",
    features: [
      "Full access to all 6 modules",
      "1 workspace",
      "50 AI credits/month",
      "BCM builder",
      "Email support",
    ],
    cta: "Start free trial",
    href: "/onboarding",
    featured: false,
  },
  {
    name: "Growth",
    price: "99",
    priceDetail: "/mo",
    description: "For scaling teams that need coordination.",
    features: [
      "Everything in Essential",
      "Unlimited workspaces",
      "250 AI credits/month",
      "Team collaboration",
      "Priority support",
      "Advanced analytics",
    ],
    cta: "Start free trial",
    href: "/onboarding",
    featured: true,
    badge: "MOST POPULAR",
  },
  {
    name: "Enterprise",
    price: "Custom",
    priceDetail: "",
    description: "For organizations with complex requirements.",
    features: [
      "Everything in Growth",
      "Unlimited AI credits",
      "Dedicated success manager",
      "Custom integrations",
      "SLA guarantees",
      "On-premise option",
    ],
    cta: "Contact sales",
    href: "/contact",
    featured: false,
  },
];

export function PricingSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const { isReducedMotion } = useLandingStore();

  useEffect(() => {
    if (!sectionRef.current || isReducedMotion) return;

    const ctx = gsap.context(() => {
      gsap.from(".pricing-header > *", {
        scrollTrigger: {
          trigger: ".pricing-header",
          start: "top 85%",
          toggleActions: "play none none none",
        },
        y: 40,
        opacity: 0,
        duration: 0.7,
        stagger: 0.1,
        ease: "power3.out",
      });

      gsap.from(".pricing-card", {
        scrollTrigger: {
          trigger: ".pricing-grid",
          start: "top 80%",
          toggleActions: "play none none none",
        },
        y: 80,
        opacity: 0,
        duration: 0.8,
        stagger: 0.12,
        ease: "power3.out",
        onComplete: () => {
          const featured = sectionRef.current?.querySelector(".pricing-card.featured");
          if (featured) {
            gsap.to(featured, { y: -12, duration: 0.4, ease: "power2.out" });
          }
        },
      });

      const mm = gsap.matchMedia();
      mm.add("(min-width: 768px)", () => {
        const cards = sectionRef.current?.querySelectorAll(".pricing-card");
        cards?.forEach((card) => {
          const isFeatured = card.classList.contains("featured");
          const baseY = isFeatured ? -12 : 0;

          card.addEventListener("mouseenter", () => {
            gsap.to(card, { y: baseY - 8, duration: 0.3, ease: "power2.out" });
          });
          card.addEventListener("mouseleave", () => {
            gsap.to(card, { y: baseY, duration: 0.3, ease: "power2.out" });
          });
        });
        return () => {};
      });

      return () => mm.revert();
    }, sectionRef);

    return () => ctx.revert();
  }, [isReducedMotion]);

  return (
    <section id="pricing" ref={sectionRef} className="py-32 px-6 bg-[var(--bg-canvas)]">
      <div className="max-w-[var(--shell-max-w)] mx-auto">
        <div className="pricing-header mb-16">
          <span className="rf-label text-[var(--rf-charcoal)]/40 tracking-[0.15em] mb-5 block">
            PRICING
          </span>
          <h2 className="text-[clamp(28px,4.5vw,48px)] font-bold text-[var(--rf-charcoal)] leading-tight tracking-[-0.02em]">
            Straightforward pricing.
            <br />
            <span className="text-[var(--rf-charcoal)]/45">No surprises.</span>
          </h2>
          <p className="mt-5 text-[17px] text-[var(--ink-2)] max-w-sm leading-relaxed">
            Start free for 14 days. Upgrade when you need more power.
          </p>
        </div>

        <div className="pricing-grid grid grid-cols-1 md:grid-cols-3 gap-4 items-start">
          {TIERS.map((tier) => (
            <div
              key={tier.name}
              className={`pricing-card relative rounded-[var(--radius-md)] border p-8 flex flex-col will-change-transform ${
                tier.featured
                  ? "featured bg-[var(--rf-charcoal)] border-[var(--rf-charcoal)]"
                  : "bg-[var(--bg-surface)] border-[var(--border-1)] hover:border-[var(--border-2)]"
              }`}
            >
              {tier.featured && tier.badge && (
                <div className="absolute top-5 right-5 px-2.5 py-1 bg-white/10 rounded-[6px] text-[10px] font-semibold tracking-[0.1em] text-white/70">
                  {tier.badge}
                </div>
              )}

              <div className="mb-8">
                <span className={`text-[12px] font-semibold tracking-[0.1em] uppercase ${tier.featured ? "text-white/40" : "text-[var(--ink-3)]"}`}>
                  {tier.name}
                </span>
                <div className="flex items-baseline gap-1 mt-3 mb-3">
                  <span className={`text-[clamp(36px,5vw,52px)] font-bold leading-none rf-mono tracking-tight ${tier.featured ? "text-[var(--rf-ivory)]" : "text-[var(--rf-charcoal)]"}`}>
                    {tier.price === "Custom" ? "" : "$"}{tier.price}
                  </span>
                  {tier.priceDetail && (
                    <span className={`text-[14px] ${tier.featured ? "text-white/50" : "text-[var(--ink-3)]"}`}>
                      {tier.priceDetail}
                    </span>
                  )}
                </div>
                <p className={`text-[14px] leading-relaxed ${tier.featured ? "text-white/60" : "text-[var(--ink-2)]"}`}>
                  {tier.description}
                </p>
              </div>

              <ul className="space-y-3 mb-8 flex-1">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-3">
                    <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 ${tier.featured ? "bg-white/15" : "bg-[var(--rf-charcoal)]/10"}`}>
                      <Check size={11} className={tier.featured ? "text-white" : "text-[var(--rf-charcoal)]"} />
                    </div>
                    <span className={`text-[14px] ${tier.featured ? "text-white/75" : "text-[var(--ink-1)]"}`}>
                      {feature}
                    </span>
                  </li>
                ))}
              </ul>

              <a
                href={tier.href}
                className={`w-full py-3.5 rounded-[var(--radius-sm)] text-[14px] font-semibold text-center transition-all duration-200 block ${
                  tier.featured
                    ? "bg-[var(--rf-ivory)] text-[var(--rf-charcoal)] hover:bg-white"
                    : "bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] hover:bg-[#3d363b]"
                }`}
              >
                {tier.cta}
              </a>
            </div>
          ))}
        </div>

        <p className="mt-10 text-[13px] text-[var(--ink-3)]">
          All plans include a 14-day free trial. No credit card required.
        </p>
      </div>
    </section>
  );
}
