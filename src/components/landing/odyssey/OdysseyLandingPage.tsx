"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Hero } from "./sections/Hero";
import { Navigation } from "./sections/Navigation";
import { Features } from "./sections/Features";
import { HowItWorks } from "./sections/HowItWorks";
import { Testimonials } from "./sections/Testimonials";
import { Pricing } from "./sections/Pricing";
import { FinalCTA } from "./sections/FinalCTA";
import { Footer } from "./sections/Footer";
import { ParticleField } from "./effects/ParticleField";
import { GradientOrbs } from "./effects/GradientOrbs";

// ═══════════════════════════════════════════════════════════════
// ODYSSEY LANDING PAGE
// Inspired by stunning Pinterest designs:
// - Deep purple/blue gradients
// - Parallax layered landscapes
// - Animated compass centerpiece
// - GSAP-heavy scroll animations
// ═══════════════════════════════════════════════════════════════

export default function OdysseyLandingPage() {
  const [isLoading, setIsLoading] = useState(true);
  const mainRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Register GSAP plugins
    gsap.registerPlugin(ScrollTrigger);

    // Simulate loading for smooth entrance
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1200);

    return () => {
      clearTimeout(timer);
      ScrollTrigger.getAll().forEach((trigger) => trigger.kill());
    };
  }, []);

  // Loading screen with animated compass
  if (isLoading) {
    return (
      <div className="fixed inset-0 z-[100] bg-[#0a0a1a] flex items-center justify-center overflow-hidden">
        {/* Animated gradient background */}
        <div className="absolute inset-0">
          <div className="absolute top-1/4 -left-32 w-[600px] h-[600px] bg-purple-600/20 rounded-full blur-[150px] animate-pulse" />
          <div className="absolute bottom-1/4 -right-32 w-[500px] h-[500px] bg-blue-600/20 rounded-full blur-[150px] animate-pulse" style={{ animationDelay: "0.5s" }} />
        </div>

        <div className="relative z-10 text-center">
          {/* Animated Compass Loader */}
          <div className="relative w-24 h-24 mx-auto mb-6">
            {/* Outer ring */}
            <div className="absolute inset-0 rounded-full border-2 border-purple-500/30 animate-spin" style={{ animationDuration: "3s" }} />
            {/* Middle ring */}
            <div className="absolute inset-2 rounded-full border-2 border-blue-500/40 animate-spin" style={{ animationDuration: "2s", animationDirection: "reverse" }} />
            {/* Inner compass needle */}
            <div className="absolute inset-4 flex items-center justify-center">
              <div className="w-1 h-12 bg-gradient-to-t from-purple-500 to-transparent transform rotate-45 animate-pulse" />
              <div className="absolute w-1 h-12 bg-gradient-to-b from-blue-500 to-transparent transform rotate-45 animate-pulse" />
            </div>
            {/* Center dot */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full shadow-lg shadow-purple-500/50" />
          </div>

          <p className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400 text-sm font-medium tracking-[0.3em] uppercase animate-pulse">
            Charting Your Course...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div ref={mainRef} className="relative min-h-screen bg-[#0a0a1a] text-white overflow-x-hidden">
      {/* Global Background Effects */}
      <GradientOrbs />
      <ParticleField />

      {/* Navigation */}
      <Navigation />

      {/* Main Content */}
      <main className="relative">
        <Hero />
        <Features />
        <HowItWorks />
        <Testimonials />
        <Pricing />
        <FinalCTA />
        <Footer />
      </main>
    </div>
  );
}
