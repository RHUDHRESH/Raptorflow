"use client";

import { useEffect, useRef } from "react";
import { ArrowRight } from "lucide-react";

/**
 * Hero Section - Luxury Editorial Style
 *
 * "ChatGPT meets MasterClass" aesthetic with:
 * - Playfair Display headline with fluid typography
 * - Shimmer CTA button effect
 * - Subtle scroll-triggered animations
 * - 8px grid-compliant spacing
 */

export function Hero() {
  const heroRef = useRef<HTMLElement>(null);

  useEffect(() => {
    // Intersection Observer for scroll reveal animations
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("revealed");
          }
        });
      },
      { threshold: 0.1 }
    );

    const revealElements = heroRef.current?.querySelectorAll(".reveal");
    revealElements?.forEach((el) => observer.observe(el));

    return () => observer.disconnect();
  }, []);

  return (
    <section
      ref={heroRef}
      className="relative min-h-screen flex items-center justify-center overflow-hidden bg-base"
    >
      {/* Subtle gradient background */}
      <div
        className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-bg-subtle opacity-50"
        aria-hidden="true"
      />

      {/* Content container */}
      <div className="container-editorial relative z-10 py-32 lg:py-40">
        <div className="max-w-4xl mx-auto text-center">
          {/* Overline badge */}
          <div className="reveal mb-8">
            <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-subtle border border-hairline text-label text-tertiary">
              <span className="w-2 h-2 rounded-full bg-text-primary animate-pulse" />
              The Founder Marketing OS
            </span>
          </div>

          {/* Main headline - Playfair Display */}
          <h1 className="reveal stagger-1 text-display-2xl text-primary mb-8">
            Stop guessing.
            <br />
            <span className="text-tertiary">Start executing.</span>
          </h1>

          {/* Subheadline - Inter */}
          <p className="reveal stagger-2 text-body-xl text-secondary max-w-2xl mx-auto mb-12">
            RaptorFlow transforms your marketing chaos into a systematic operating system.
            AI-powered strategy that actually converts.
          </p>

          {/* CTA Group */}
          <div className="reveal stagger-3 flex flex-col sm:flex-row items-center justify-center gap-4">
            {/* Primary CTA with shimmer effect */}
            <a
              href="/auth/signup"
              className="shimmer-button group inline-flex items-center justify-center gap-3 h-14 px-8 rounded-lg bg-accent text-inverse text-body-md font-medium transition-all duration-200 hover:bg-accent-hover active:scale-[0.98] focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-accent"
            >
              Get Noticed
              <ArrowRight className="w-5 h-5 transition-transform duration-200 group-hover:translate-x-1" />
            </a>

            {/* Secondary CTA */}
            <a
              href="#how-it-works"
              className="inline-flex items-center justify-center h-14 px-8 rounded-lg border border-default text-primary text-body-md font-medium transition-all duration-200 hover:bg-subtle hover:border-strong"
            >
              See How It Works
            </a>
          </div>

          {/* Social proof hint */}
          <p className="reveal stagger-4 mt-12 text-body-sm text-muted">
            Trusted by 500+ founders building in public
          </p>
        </div>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-float">
        <div className="w-6 h-10 rounded-full border-2 border-muted flex items-start justify-center p-2">
          <div className="w-1.5 h-1.5 rounded-full bg-muted animate-pulse" />
        </div>
      </div>
    </section>
  );
}
