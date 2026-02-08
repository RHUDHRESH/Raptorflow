"use client";

import { Navbar } from "@/components/landing/Navbar";
import { Pricing } from "@/components/landing/Pricing";
import { FinalCTA } from "@/components/landing/FinalCTA";
import { Footer } from "@/components/landing/Footer";

export default function PricingPage() {
  return (
    <main className="relative">
      <Navbar />
      <div className="pt-24">
        <Pricing />
        <FinalCTA />
        <Footer />
      </div>
    </main>
  );
}

