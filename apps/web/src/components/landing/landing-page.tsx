"use client";

import * as React from "react";
import { LandingNav } from "./landing-nav";
import { LandingHero } from "./landing-hero";
import { LandingProblem } from "./landing-problem";
import { LandingSystem } from "./landing-system";
import { LandingFoundation } from "./landing-foundation";
import { LandingCampaigns } from "./landing-campaigns";
import { LandingMuse } from "./landing-muse";
import { LandingIntel } from "./landing-intel";
import { LandingDailyWins } from "./landing-daily-wins";
import { LandingCouncil } from "./landing-council";
import { LandingMemory } from "./landing-memory";
import { LandingPricing } from "./landing-pricing";
import { LandingFinalCTA } from "./landing-final-cta";
import { referralSignupHref } from "@/lib/referrals";

export function LandingPage() {
  return (
    <main className="min-h-screen overflow-x-hidden bg-[#FBF8F2] text-[#2A2622] landing-noise">
      <LandingNav />
      <LandingHero />
      <LandingProblem />
      <LandingSystem />
      <LandingFoundation />
      <LandingCampaigns />
      <LandingMuse />
      <LandingIntel />
      <LandingDailyWins />
      <LandingCouncil />
      <LandingMemory />
      <LandingPricing />
      <LandingFinalCTA />

      {/* Site footer */}
      <footer className="border-t border-[#E5DED4] bg-[#F5F0E8] px-6 py-10 lg:px-8">
        <div className="mx-auto max-w-7xl flex flex-col md:flex-row items-center justify-between gap-4">
          <div>
            <span className="text-sm font-semibold text-[#2A2622] tracking-tight">RAPTORFLOW</span>
            <p className="text-xs font-mono text-[#9A948C] uppercase tracking-widest mt-1">
              AI-native marketing execution for Indian SMBs
            </p>
          </div>
          <div className="flex items-center gap-8 text-xs font-mono text-[#9A948C] uppercase tracking-widest">
            <a href="/sign-in" className="hover:text-[#2A2622] transition-colors duration-200">
              Sign in
            </a>
            <a href={referralSignupHref("LOKI")} className="hover:text-[#D97757] transition-colors duration-200">
              Start now
            </a>
          </div>
          <p className="text-xs font-mono text-[#BAB0A0] uppercase tracking-widest">
            © 2026 RaptorFlow
          </p>
        </div>
      </footer>
    </main>
  );
}
