"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { HugeiconsIcon } from "@hugeicons/react";
import {
  Rocket01Icon,
  ArrowRight01Icon
} from "@hugeicons/core-free-icons";

export function FinalCTA() {
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!sectionRef.current) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        ".cta-content",
        { y: 60, opacity: 0, scale: 0.95 },
        {
          y: 0,
          opacity: 1,
          scale: 1,
          duration: 0.8,
          ease: "power3.out",
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top 80%",
            toggleActions: "play none none none",
          },
        }
      );
    });

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      className="relative py-32 bg-rock overflow-hidden"
    >
      {/* Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-0 right-0 h-32 bg-gradient-to-b from-shaft-500 to-transparent" />
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-barley/10 rounded-full blur-[150px]" />
      </div>

      <div className="relative z-10 max-w-4xl mx-auto px-6 lg:px-8">
        <div className="cta-content text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-barley/10 border border-barley/20 mb-8">
            <HugeiconsIcon icon={Rocket01Icon} className="w-4 h-4 text-barley" />
            <span className="text-barley text-sm font-medium tracking-wide">14-Day Free Trial</span>
          </div>

          {/* Title */}
          <h2 className="font-display text-4xl sm:text-5xl lg:text-7xl font-semibold text-shaft-500 mb-6 leading-tight">
            Ready to Brew
            <span className="text-barley italic"> Something Amazing?</span>
          </h2>

          {/* Description */}
          <p className="text-shaft-400/70 text-lg sm:text-xl max-w-2xl mx-auto mb-10 leading-relaxed">
            Join thousands of teams who've discovered the art of effortless automation.
            Your first workflow is just minutes away.
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              className="group relative px-10 py-5 bg-barley text-shaft-500 font-semibold rounded-full overflow-hidden transition-all duration-300 hover:shadow-xl hover:shadow-barley/20"
              data-cursor-hover
            >
              <span className="relative z-10 flex items-center justify-center gap-2">
                Start Free Trial
                <HugeiconsIcon icon={ArrowRight01Icon} className="w-5 h-5 transition-transform duration-300 group-hover:translate-x-1" />
              </span>
              <div className="absolute inset-0 bg-gradient-to-r from-barley to-akaroa-400 transform translate-y-full transition-transform duration-300 group-hover:translate-y-0" />
            </button>

            <button
              className="px-10 py-5 border-2 border-shaft-200 text-shaft-500 rounded-full font-medium transition-all duration-300 hover:bg-shaft-500 hover:text-rock hover:border-shaft-500"
              data-cursor-hover
            >
              Schedule a Demo
            </button>
          </div>

          {/* Trust Text */}
          <p className="mt-8 text-shaft-400/50 text-sm">
            No credit card required • Cancel anytime • 24/7 Support
          </p>
        </div>
      </div>
    </section>
  );
}
