"use client";

import * as React from "react";
import { LandingNav } from "./landing-nav";
import { LandingHero } from "./landing-hero";
import { LandingProblem } from "./landing-problem";
import { LandingGuide } from "./landing-guide";
import { LandingStory } from "./landing-story";
import { LandingHowItWorks } from "./landing-how-it-works";
import { LandingPillars } from "./landing-pillars";
import { LandingGuarantee } from "./landing-guarantee";
import { LandingPricing } from "./landing-pricing";
import { LandingFinalCTA } from "./landing-final-cta";
import { LandingFooter } from "./landing-footer";
import { WhatsAppFloat } from "./whatsapp-float";

export function LandingPage() {
  return (
    <main className="min-h-screen overflow-x-hidden">
      <LandingNav />
      <LandingHero />
      <LandingProblem />
      <LandingGuide />
      <LandingStory />
      <LandingHowItWorks />
      <LandingPillars />
      <LandingGuarantee />
      <LandingPricing />
      <LandingFinalCTA />
      <LandingFooter />
      <WhatsAppFloat />
    </main>
  );
}
