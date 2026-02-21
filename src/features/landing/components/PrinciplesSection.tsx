"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Shield, ArrowRight, Zap, User } from "lucide-react";
import { useLandingStore } from "./LandingClient";

const FEATURED_PRINCIPLE = {
  number: "01",
  title: "You remain in control",
  description:
    "AI proposes. You lock. You deploy. Every step requires your command. No move executes without your explicit approval — ever.",
  Icon: Shield,
};

const SMALL_PRINCIPLES = [
  {
    title: "Context flows everywhere",
    description: "Your BCM is the brain. Every module reads it. Nothing repeats.",
    Icon: ArrowRight,
  },
  {
    title: "Speed without noise",
    description: "From strategy to executed campaign in hours, not weeks.",
    Icon: Zap,
  },
  {
    title: "Built for operators",
    description: "Not consultants. Not agencies. The people doing the work.",
    Icon: User,
  },
];

export function PrinciplesSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const { isReducedMotion } = useLandingStore();

  useEffect(() => {
    if (!sectionRef.current || isReducedMotion) return;

    const ctx = gsap.context(() => {
      gsap.from(".principles-header > *", {
        scrollTrigger: {
          trigger: ".principles-header",
          start: "top 85%",
          toggleActions: "play none none none",
        },
        y: 40,
        opacity: 0,
        duration: 0.7,
        stagger: 0.1,
        ease: "power3.out",
      });

      gsap.from(".principle-featured", {
        scrollTrigger: {
          trigger: ".principles-layout",
          start: "top 80%",
          toggleActions: "play none none none",
        },
        x: -60,
        opacity: 0,
        duration: 1,
        ease: "power3.out",
      });

      gsap.from(".principle-small", {
        scrollTrigger: {
          trigger: ".principles-layout",
          start: "top 78%",
          toggleActions: "play none none none",
        },
        x: 40,
        opacity: 0,
        duration: 0.8,
        stagger: 0.12,
        ease: "power3.out",
      });

      const mm = gsap.matchMedia();
      mm.add("(min-width: 1024px)", () => {
        const featured = sectionRef.current?.querySelector(".principle-featured");
        if (featured) {
          featured.addEventListener("mouseenter", () => {
            gsap.to(featured, { scale: 1.01, duration: 0.4, ease: "power2.out" });
          });
          featured.addEventListener("mouseleave", () => {
            gsap.to(featured, { scale: 1, duration: 0.4, ease: "power2.out" });
          });
        }
        return () => {};
      });

      return () => mm.revert();
    }, sectionRef);

    return () => ctx.revert();
  }, [isReducedMotion]);

  const FeaturedIcon = FEATURED_PRINCIPLE.Icon;

  return (
    <section ref={sectionRef} className="py-32 px-6 bg-[var(--bg-surface)]">
      <div className="max-w-[var(--shell-max-w)] mx-auto">
        <div className="principles-header mb-16">
          <span className="rf-label text-[var(--rf-charcoal)]/40 tracking-[0.15em] mb-5 block">
            OUR PRINCIPLES
          </span>
          <h2 className="text-[clamp(28px,4.5vw,44px)] font-bold text-[var(--rf-charcoal)] leading-tight tracking-[-0.02em]">
            Built on conviction.
          </h2>
        </div>

        <div className="principles-layout grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="principle-featured lg:col-span-2 relative rounded-[var(--radius-lg)] bg-[var(--rf-charcoal)] p-12 flex flex-col overflow-hidden will-change-transform cursor-default">
            <div className="absolute top-8 right-10">
              <span className="text-[80px] font-bold font-mono text-white/[0.07] leading-none select-none">
                {FEATURED_PRINCIPLE.number}
              </span>
            </div>
            <div className="relative z-10 flex flex-col h-full">
              <div className="w-14 h-14 rounded-[var(--radius-sm)] bg-white/10 flex items-center justify-center mb-auto">
                <FeaturedIcon size={26} className="text-[var(--rf-ivory)]" />
              </div>
              <div className="mt-12">
                <h3 className="text-[clamp(24px,3.5vw,36px)] font-bold text-[var(--rf-ivory)] leading-tight tracking-[-0.02em] mb-5">
                  {FEATURED_PRINCIPLE.title}
                </h3>
                <p className="text-[17px] text-white/60 leading-relaxed max-w-md">
                  {FEATURED_PRINCIPLE.description}
                </p>
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-6">
            {SMALL_PRINCIPLES.map((p) => {
              const PIcon = p.Icon;
              return (
                <div
                  key={p.title}
                  className="principle-small rf-card flex-1 will-change-transform"
                >
                  <div className="w-9 h-9 rounded-[var(--radius-sm)] bg-[var(--rf-charcoal)]/[0.07] flex items-center justify-center mb-5">
                    <PIcon size={18} className="text-[var(--rf-charcoal)]" />
                  </div>
                  <h4 className="text-[16px] font-bold text-[var(--rf-charcoal)] mb-2">
                    {p.title}
                  </h4>
                  <p className="text-[13px] text-[var(--ink-2)] leading-relaxed">
                    {p.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
