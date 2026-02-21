"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { useLandingStore } from "./LandingClient";

export function FinalCTASection() {
  const sectionRef = useRef<HTMLElement>(null);
  const { isReducedMotion } = useLandingStore();

  useEffect(() => {
    if (!sectionRef.current || isReducedMotion) return;

    const ctx = gsap.context(() => {
      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top 70%",
          toggleActions: "play none none none",
        },
        defaults: { ease: "power4.out" },
      });

      tl.from(".cta-word", {
        y: 100,
        opacity: 0,
        rotateX: 15,
        duration: 0.9,
        stagger: 0.1,
      })
        .from(".cta-fine", {
          opacity: 0,
          duration: 0.6,
        }, "-=0.3")
        .from(".cta-btn", {
          scale: 0.85,
          opacity: 0,
          duration: 0.6,
          ease: "back.out(1.5)",
        }, "-=0.4")
        .from(".cta-dots-bg", {
          opacity: 0,
          duration: 2,
        }, 0);

      const btn = sectionRef.current?.querySelector(".cta-btn");
      if (btn) {
        btn.addEventListener("mouseenter", () => {
          gsap.to(btn, { scale: 1.04, duration: 0.25, ease: "power2.out" });
        });
        btn.addEventListener("mouseleave", () => {
          gsap.to(btn, { scale: 1, duration: 0.25, ease: "power2.out" });
        });
      }
    }, sectionRef);

    return () => ctx.revert();
  }, [isReducedMotion]);

  return (
    <section
      id="final-cta"
      ref={sectionRef}
      className="relative min-h-[80vh] flex items-center justify-center px-6 py-32 bg-[var(--rf-charcoal)] overflow-hidden"
    >
      <div
        className="cta-dots-bg absolute inset-0 pointer-events-none"
        style={{
          backgroundImage: `radial-gradient(circle at 2px 2px, rgba(243,240,231,0.06) 1px, transparent 0)`,
          backgroundSize: "44px 44px",
        }}
      />

      <div className="relative z-10 text-center max-w-4xl mx-auto">
        <div className="overflow-hidden mb-8" style={{ perspective: "800px" }}>
          <h2
            className="font-bold text-[var(--rf-ivory)] leading-[0.9] tracking-[-0.04em]"
            style={{ fontSize: "clamp(60px, 11vw, 130px)" }}
          >
            <span className="cta-word inline-block will-change-transform">Take the</span>
            <br />
            <span className="cta-word inline-block will-change-transform">cockpit.</span>
          </h2>
        </div>

        <p className="cta-fine rf-mono-xs text-white/35 mb-12 tracking-[0.05em]">
          14-day free trial. No card required. Cancel any time.
        </p>

        <a
          href="/onboarding"
          className="cta-btn inline-flex items-center justify-center px-12 py-5 bg-[var(--rf-ivory)] text-[var(--rf-charcoal)] rounded-[var(--radius-sm)] text-[18px] font-bold will-change-transform"
        >
          Enter RaptorFlow
        </a>
      </div>
    </section>
  );
}
