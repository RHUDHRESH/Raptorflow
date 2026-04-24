"use client";

import * as React from "react";
import { LandingNav } from "./landing-nav";
import { LandingHero } from "./landing-hero";
import { LandingSocialProof } from "./landing-social-proof";
import { LandingFeatures } from "./landing-features";
import { LandingHowItWorks } from "./landing-how-it-works";
import { LandingPricing } from "./landing-pricing";
import { LandingFooter } from "./landing-footer";
import { WhatsAppFloat } from "./whatsapp-float";
import { PageTransition } from "@/components/ui/gsap-bridge";

export function LandingPage() {
  return (
    <PageTransition>
      <main className="min-h-screen paper-soft">
        <LandingNav />
        <LandingHero />
        <LandingSocialProof />
        <LandingFeatures />
        <LandingHowItWorks />
        <LandingPricing />
        <LandingFooter />
        <WhatsAppFloat />
      </main>
    </PageTransition>
  );
}
