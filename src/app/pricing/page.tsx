"use client";

import { LandingNavbar } from "@/features/landing/components/LandingNavbar";
import { PricingSection } from "@/features/landing/components/PricingSection";
import { FinalCTASection } from "@/features/landing/components/FinalCTASection";
import { FooterSection } from "@/features/landing/components/FooterSection";

export default function PricingPage() {
  return (
    <main className="relative min-h-screen bg-[var(--bg-canvas)]">
      <LandingNavbar />
      <div className="pt-24">
        <PricingSection />
        <FinalCTASection />
        <FooterSection />
      </div>
    </main>
  );
}
