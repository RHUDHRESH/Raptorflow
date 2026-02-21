"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { create } from "zustand";

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

const SECTION_IDS = ["hero", "modules", "control", "stats", "personas", "pricing"];

export function LandingClient() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { setActiveSection } = useLandingStore();

  useEffect(() => {
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const ctx = gsap.context(() => {
      SECTION_IDS.forEach((id) => {
        const el = document.getElementById(id);
        if (!el) return;
        ScrollTrigger.create({
          trigger: el,
          start: "top 60%",
          end: "bottom 40%",
          onEnter: () => setActiveSection(id),
          onEnterBack: () => setActiveSection(id),
        });
      });

      if (!prefersReducedMotion) {
        document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
          anchor.addEventListener("click", (e) => {
            const href = anchor.getAttribute("href");
            if (!href || href === "#") return;
            const target = document.querySelector(href);
            if (target) {
              e.preventDefault();
              target.scrollIntoView({ behavior: "smooth", block: "start" });
            }
          });
        });
      }
    }, containerRef);

    return () => {
      ctx.revert();
      ScrollTrigger.getAll().forEach((t) => t.kill());
    };
  }, [setActiveSection]);

  return (
    <div ref={containerRef} className="min-h-screen bg-[var(--bg-canvas)]">
      <LandingNavbar />
      <main>
        <HeroSection />
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
