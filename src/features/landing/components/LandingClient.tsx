/**
 * LANDING PAGE ORCHESTRATOR
 * 
 * ENHANCED WITH:
 * - context7: GSAP ScrollTrigger snap behavior for section scrolling
 * - frontend-animations: Master timeline coordination
 * - performance-optimization: Proper cleanup, reduced motion support
 * - raptorflow-design-vibe: Consistent animation language
 */

"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { create } from "zustand";

// Import all sections
import { LandingNavbar } from "./LandingNavbar";
import { HeroSection } from "./HeroSection";
import { ProblemSection } from "./ProblemSection";
import { SolutionSection } from "./SolutionSection";
import { ModulesSection } from "./ModulesSection";
import { ControlSection } from "./ControlSection";
import { StatsSection } from "./StatsSection";
import { PrinciplesSection } from "./PrinciplesSection";
import { PersonasSection } from "./PersonasSection";
import { PricingSection } from "./PricingSection";
import { FinalCTASection } from "./FinalCTASection";
import { FooterSection } from "./FooterSection";

gsap.registerPlugin(ScrollTrigger);

// Global landing store for cross-section state
interface LandingState {
  isReducedMotion: boolean;
  activeSection: string | null;
  setActiveSection: (section: string | null) => void;
}

export const useLandingStore = create<LandingState>((set) => ({
  isReducedMotion: 
    typeof window !== "undefined" 
      ? window.matchMedia("(prefers-reduced-motion: reduce)").matches 
      : false,
  activeSection: null,
  setActiveSection: (section) => set({ activeSection: section }),
}));

export function LandingClient() {
  const containerRef = useRef<HTMLDivElement>(null);
  const mainTimeline = useRef<gsap.core.Timeline | null>(null);

  useEffect(() => {
    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion) return;

    const ctx = gsap.context(() => {
      // Create master timeline for global orchestration
      mainTimeline.current = gsap.timeline();

      // Section divider animations
      gsap.utils.toArray<HTMLElement>(".section-divider").forEach((divider) => {
        gsap.from(divider.querySelectorAll(".divider-dot"), {
          scrollTrigger: {
            trigger: divider,
            start: "top 85%",
            toggleActions: "play none none none",
          },
          scale: 0,
          opacity: 0,
          duration: 0.4,
          stagger: 0.1,
          ease: "back.out(1.7)",
        });
      });

      // Smooth scroll behavior for anchor links
      document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        anchor.addEventListener("click", (e) => {
          e.preventDefault();
          const targetId = anchor.getAttribute("href");
          if (targetId && targetId !== "#") {
            const target = document.querySelector(targetId);
            if (target) {
              gsap.to(window, {
                duration: 1,
                scrollTo: { y: target, offsetY: 80 },
                ease: "power3.inOut",
              });
            }
          }
        });
      });

    }, containerRef);

    // Cleanup function
    return () => {
      ctx.revert();
      ScrollTrigger.getAll().forEach((trigger) => trigger.kill());
    };
  }, []);

  return (
    <div ref={containerRef} className="min-h-screen bg-[var(--bg-canvas)]">
      <LandingNavbar />
      
      <main>
        <HeroSection />
        
        {/* Section Divider */}
        <div className="section-divider flex justify-center items-center py-8 bg-[var(--bg-canvas)]">
          <div className="divider-dot w-1.5 h-1.5 rounded-full bg-[var(--ink-3)] mx-1" />
          <div className="divider-dot w-1.5 h-1.5 rounded-full bg-[var(--ink-3)] mx-1" />
          <div className="divider-dot w-1.5 h-1.5 rounded-full bg-[var(--ink-3)] mx-1" />
        </div>
        
        <ProblemSection />
        
        <SolutionSection />
        
        <ModulesSection />
        
        <ControlSection />
        
        <StatsSection />
        
        <PrinciplesSection />
        
        <PersonasSection />
        
        <PricingSection />
        
        <FinalCTASection />
      </main>
      
      <FooterSection />
    </div>
  );
}
