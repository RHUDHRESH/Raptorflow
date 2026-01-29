"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

// Sections
import { NavigationGod } from "./sections/NavigationGod";
import { HeroGod } from "./sections/HeroGod";
import { ProblemSection } from "./sections/ProblemSection";
import { SolutionSection } from "./sections/SolutionSection";
import { ProductDemo } from "./sections/ProductDemo";
import { FeaturesGrid } from "./sections/FeaturesGrid";
import { HowItWorks } from "./sections/HowItWorks";
import { SocialProof } from "./sections/SocialProof";
import { TestimonialsCarousel } from "./sections/TestimonialsCarousel";
import { PricingGod } from "./sections/PricingGod";
import { FAQSection } from "./sections/FAQSection";
import { FinalCTA } from "./sections/FinalCTA";
import { GodFooter } from "./sections/GodFooter";

// Effects
import { ScrollProgress } from "./effects/ScrollProgress";
import { ParticleField } from "./effects/ParticleField";

// ═══════════════════════════════════════════════════════════════
// GOD TIER LANDING PAGE
// Cinematic, conversion-optimized, premium experience
// ═══════════════════════════════════════════════════════════════

export default function GodLandingPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [scrollY, setScrollY] = useState(0);

  // Preloader simulation
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1500);
    return () => clearTimeout(timer);
  }, []);

  // Scroll tracking for parallax effects
  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY);
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <>
      {/* Preloader */}
      <AnimatePresence>
        {isLoading && (
          <motion.div
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="fixed inset-0 z-[100] bg-[var(--canvas)] flex items-center justify-center"
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="text-center"
            >
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                className="w-12 h-12 border-2 border-[var(--ink)] border-t-transparent rounded-full mx-auto mb-4"
              />
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="text-sm text-[var(--muted)] font-medium tracking-widest uppercase"
              >
                RaptorFlow
              </motion.p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Scroll Progress */}
      <ScrollProgress />

      {/* Background Particle Field */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <ParticleField />
      </div>

      {/* Main Content */}
      <motion.main
        initial={{ opacity: 0 }}
        animate={{ opacity: isLoading ? 0 : 1 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="relative z-10 min-h-screen bg-[var(--canvas)] text-[var(--ink)] overflow-x-hidden"
      >
        {/* Fixed Navigation */}
        <NavigationGod />

        {/* Hero Section */}
        <HeroGod scrollY={scrollY} />

        {/* Problem Section */}
        <ProblemSection />

        {/* Solution Section */}
        <SolutionSection />

        {/* Product Demo */}
        <ProductDemo />

        {/* Features Grid */}
        <FeaturesGrid />

        {/* How It Works */}
        <HowItWorks />

        {/* Social Proof Bar */}
        <SocialProof />

        {/* Testimonials */}
        <TestimonialsCarousel />

        {/* Pricing */}
        <PricingGod />

        {/* FAQ */}
        <FAQSection />

        {/* Final CTA */}
        <FinalCTA />

        {/* Footer */}
        <GodFooter />
      </motion.main>
    </>
  );
}
