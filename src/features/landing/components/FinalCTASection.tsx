/**
 * ENHANCED WITH:
 * - context7: GSAP master timeline for CTA entrance sequence
 * - frontend-animations: Button glow, floating orbs
 * - magicui: Particles-inspired background orbs
 * - performance-optimization: GPU-only transforms
 * - raptorflow-design-vibe: High-impact conversion moment
 */

"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { ArrowRight } from "lucide-react";
import { useLandingStore } from "./LandingClient";

export function FinalCTASection() {
  const sectionRef = useRef<HTMLElement>(null);
  const { isReducedMotion } = useLandingStore();

  useEffect(() => {
    if (!sectionRef.current || isReducedMotion) return;

    const ctx = gsap.context(() => {
      // Master timeline for dramatic entrance
      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top 70%",
          toggleActions: "play none none none",
        },
      });

      // Label
      tl.from(".cta-label", {
        y: 20,
        opacity: 0,
        duration: 0.5,
        ease: "power2.out",
      });

      // Title with word split
      tl.from(".cta-title span", {
        y: 60,
        opacity: 0,
        duration: 0.8,
        stagger: 0.08,
        ease: "power3.out",
      }, "-=0.3");

      // Description
      tl.from(".cta-description", {
        y: 20,
        opacity: 0,
        filter: "blur(8px)",
        duration: 0.6,
        ease: "power2.out",
        clearProps: "filter",
      }, "-=0.5");

      // Button with elastic bounce
      tl.from(".cta-button", {
        scale: 0.8,
        opacity: 0,
        duration: 0.6,
        ease: "back.out(1.7)",
      }, "-=0.3");

      // Secondary CTA
      tl.from(".cta-secondary", {
        y: 10,
        opacity: 0,
        duration: 0.4,
        ease: "power2.out",
      }, "-=0.2");

      // Floating orbs continuous animation
      gsap.to(".orb-1", {
        y: -30,
        x: 20,
        duration: 4,
        ease: "sine.inOut",
        yoyo: true,
        repeat: -1,
      });

      gsap.to(".orb-2", {
        y: 20,
        x: -15,
        duration: 5,
        ease: "sine.inOut",
        yoyo: true,
        repeat: -1,
        delay: 1,
      });

      gsap.to(".orb-3", {
        y: -15,
        x: -25,
        duration: 3.5,
        ease: "sine.inOut",
        yoyo: true,
        repeat: -1,
        delay: 0.5,
      });

      // Button hover glow effect
      const button = sectionRef.current?.querySelector(".cta-button");
      if (button) {
        button.addEventListener("mouseenter", () => {
          gsap.to(button, {
            scale: 1.05,
            duration: 0.25,
            ease: "power2.out",
          });
          gsap.to(".button-glow", {
            opacity: 0.6,
            scale: 1.2,
            duration: 0.3,
          });
        });

        button.addEventListener("mouseleave", () => {
          gsap.to(button, {
            scale: 1,
            duration: 0.25,
            ease: "power2.out",
          });
          gsap.to(".button-glow", {
            opacity: 0,
            scale: 1,
            duration: 0.3,
          });
        });
      }
    }, sectionRef);

    return () => ctx.revert();
  }, [isReducedMotion]);

  return (
    <section
      id="final-cta"
      ref={sectionRef}
      className="relative py-32 px-6 bg-[var(--rf-charcoal)] overflow-hidden"
    >
      {/* Background orbs */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="orb-1 absolute top-20 left-[10%] w-[400px] h-[400px] rounded-full bg-white/[0.03] blur-[100px] will-change-transform" />
        <div className="orb-2 absolute bottom-20 right-[10%] w-[350px] h-[350px] rounded-full bg-white/[0.02] blur-[80px] will-change-transform" />
        <div className="orb-3 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] rounded-full bg-white/[0.01] blur-[120px] will-change-transform" />
      </div>

      <div className="max-w-[var(--shell-max-w)] mx-auto relative z-10">
        <div className="text-center max-w-3xl mx-auto">
          {/* Label */}
          <span className="cta-label text-white/40 text-[12px] font-mono tracking-[0.2em] mb-6 block">
            READY TO TAKE CONTROL?
          </span>

          {/* Title */}
          <h2 className="cta-title text-[clamp(36px,7vw,72px)] font-bold text-[var(--rf-ivory)] leading-[0.95] tracking-[-0.03em] mb-8">
            {"Stop juggling tools.".split(" ").map((word, i) => (
              <span key={i} className="inline-block mr-[0.25em]">{word}</span>
            ))}
            <br />
            {"Start winning markets.".split(" ").map((word, i) => (
              <span key={i} className="inline-block mr-[0.25em]">{word}</span>
            ))}
          </h2>

          {/* Description */}
          <p className="cta-description text-[18px] text-white/60 leading-relaxed mb-10 max-w-xl mx-auto">
            Join operators who have replaced their entire marketing stack with one system designed for precision and speed.
          </p>

          {/* CTA Button with glow */}
          <div className="relative inline-block mb-6">
            <div className="button-glow absolute inset-0 bg-[var(--rf-ivory)]/20 rounded-[var(--radius-sm)] blur-xl opacity-0 pointer-events-none" />
            
            <a
              href="/onboarding"
              className="cta-button relative inline-flex items-center gap-3 px-10 py-5 bg-[var(--rf-ivory)] text-[var(--rf-charcoal)] rounded-[var(--radius-sm)] text-[17px] font-semibold will-change-transform"
            >
              Start Building for Free
              <ArrowRight size={20} />
            </a>
          </div>

          {/* Secondary CTA */}
          <p className="cta-secondary text-[14px] text-white/40">
            No credit card required. 14-day free trial.
          </p>
        </div>
      </div>
    </section>
  );
}
