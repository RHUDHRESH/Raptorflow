"use client";

import { useEffect, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

// Effects
import { GrainOverlay } from "./effects/GrainOverlay";
import { CursorFollower } from "./effects/CursorFollower";

// Sections
import { Navigation } from "./sections/Navigation";
import { Hero } from "./sections/Hero";
import { Features } from "./sections/Features";
import { HowItWorks } from "./sections/HowItWorks";
import { Testimonials } from "./sections/Testimonials";
import { Pricing } from "./sections/Pricing";
import { FAQ } from "./sections/FAQ";
import { FinalCTA } from "./sections/FinalCTA";
import { Footer } from "./sections/Footer";

// ═══════════════════════════════════════════════════════════════
// ARTISANAL LUXURY LANDING PAGE
// Coffeehouse aesthetic meets premium SaaS
// GSAP-driven, Hugeicons-powered, handcrafted experience
// ═══════════════════════════════════════════════════════════════

export default function ArtisanalLandingPage() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Register GSAP plugins
    gsap.registerPlugin(ScrollTrigger);

    // Simulate loading for smooth entrance
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 800);

    return () => {
      clearTimeout(timer);
      ScrollTrigger.getAll().forEach((trigger) => trigger.kill());
    };
  }, []);

  // Loading screen
  if (isLoading) {
    return (
      <div className="fixed inset-0 z-[100] bg-shaft-500 flex items-center justify-center">
        <div className="text-center">
          <div className="relative w-16 h-16 mx-auto mb-4">
            <div className="absolute inset-0 rounded-full border-2 border-barley/20" />
            <div className="absolute inset-0 rounded-full border-2 border-barley border-t-transparent animate-spin" />
          </div>
          <p className="text-rock/60 text-sm font-medium tracking-widest uppercase animate-pulse">
            Brewing Experience...
          </p>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Global Effects */}
      <GrainOverlay />
      <CursorFollower />

      {/* Navigation */}
      <Navigation />

      {/* Main Content */}
      <main className="relative bg-shaft-500">
        <Hero />
        <Features />
        <HowItWorks />
        <Testimonials />
        <Pricing />
        <FAQ />
        <FinalCTA />
        <Footer />
      </main>
    </>
  );
}
