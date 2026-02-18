"use client";

import { useEffect, useRef, useState } from "react";
import { gsap } from "gsap";
import { CompassLogo } from "@/components/compass/CompassLogo";

interface StepWelcomeProps {
  onStart: () => void;
}

export function StepWelcome({ onStart }: StepWelcomeProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const logoRef = useRef<HTMLDivElement>(null);
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: "power3.out" } });

      // Logo entrance with scale and rotation
      tl.fromTo(
        logoRef.current,
        { opacity: 0, scale: 0.8, rotation: -15 },
        { opacity: 1, scale: 1, rotation: 0, duration: 1 }
      )
        .fromTo(
          ".welcome-title",
          { opacity: 0, y: 30 },
          { opacity: 1, y: 0, duration: 0.8 },
          "-=0.4"
        )
        .fromTo(
          ".welcome-subtitle",
          { opacity: 0, y: 20 },
          { opacity: 1, y: 0, duration: 0.6 },
          "-=0.4"
        )
        .fromTo(
          ".welcome-description",
          { opacity: 0, y: 20 },
          { opacity: 1, y: 0, duration: 0.6 },
          "-=0.3"
        )
        .fromTo(
          ".welcome-features > *",
          { opacity: 0, x: -20 },
          { opacity: 1, x: 0, duration: 0.5, stagger: 0.1 },
          "-=0.2"
        )
        .fromTo(
          ".welcome-cta",
          { opacity: 0, y: 20 },
          { opacity: 1, y: 0, duration: 0.5 },
          "-=0.2"
        );
    }, containerRef);

    return () => ctx.revert();
  }, []);

  // Subtle hover animation
  useEffect(() => {
    if (logoRef.current) {
      gsap.to(logoRef.current, {
        scale: isHovered ? 1.05 : 1,
        duration: 0.3,
        ease: "power2.out",
      });
    }
  }, [isHovered]);

  return (
    <div
      ref={containerRef}
      className="min-h-screen bg-[var(--bg-canvas)] flex items-center justify-center px-6 py-12"
    >
      <div className="max-w-xl w-full text-center">
        {/* Animated Logo */}
        <div
          ref={logoRef}
          className="inline-flex items-center justify-center mb-10 cursor-pointer"
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          <div className="relative">
            <div className="absolute inset-0 bg-[var(--rf-charcoal)] opacity-5 rounded-full blur-3xl transform scale-150" />
            <CompassLogo
              size={80}
              className="text-[var(--rf-charcoal)] relative z-10"
              animate={true}
            />
          </div>
        </div>

        {/* Title */}
        <h1 className="welcome-title text-[40px] leading-[48px] font-bold text-[var(--ink-1)] mb-4 tracking-tight">
          Welcome to RaptorFlow
        </h1>

        {/* Subtitle */}
        <p className="welcome-subtitle text-xl text-[var(--ink-2)] mb-6 font-medium">
          Your marketing operating system
        </p>

        {/* Description */}
        <p className="welcome-description text-base text-[var(--ink-3)] leading-relaxed mb-10 max-w-md mx-auto">
          In the next few minutes, we&apos;ll capture the essence of your business
          to build your personalized marketing intelligence. This becomes the
          foundation for every strategy we create together.
        </p>

        {/* Features */}
        <div className="welcome-features space-y-4 mb-12 text-left max-w-sm mx-auto">
          {[
            { icon: "🎯", text: "Lock your positioning and ICP" },
            { icon: "📝", text: "Define your brand voice and guardrails" },
            { icon: "🚀", text: "Generate your first marketing moves" },
          ].map((feature, i) => (
            <div
              key={i}
              className="flex items-center gap-4 p-4 rounded-[var(--radius-md)] bg-[var(--bg-surface)] border border-[var(--border-1)] hover:border-[var(--border-2)] transition-colors"
            >
              <span className="text-xl">{feature.icon}</span>
              <span className="text-sm font-medium text-[var(--ink-1)]">
                {feature.text}
              </span>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="welcome-cta">
          <button
            onClick={onStart}
            className="rf-btn-primary text-base px-10 py-4 shadow-lg shadow-[var(--rf-charcoal)]/10 hover:shadow-xl hover:shadow-[var(--rf-charcoal)]/15"
          >
            Start Building Your Foundation
            <svg
              className="w-5 h-5 ml-2 inline-block"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 7l5 5m0 0l-5 5m5-5H6"
              />
            </svg>
          </button>
          <p className="mt-4 text-xs text-[var(--ink-3)]">
            Takes about 5 minutes · You can edit anytime
          </p>
        </div>
      </div>
    </div>
  );
}
