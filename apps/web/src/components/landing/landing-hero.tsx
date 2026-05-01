"use client";

import * as React from "react";
import { ArrowRight, Check } from "lucide-react";
import { GsapBridge } from "@/components/ui/gsap-bridge";

export function LandingHero() {
  return (
    <section className="relative min-h-screen flex flex-col justify-center pt-20 pb-16 overflow-hidden paper-soft">
      <GsapBridge stagger className="relative z-10 mx-auto max-w-6xl px-6 lg:px-8">
        <div className="gsap-reveal flex justify-center mb-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--amber-wash)] border border-[var(--amber-stroke)]/20">
            <span className="status-dot-live" />
            <span className="text-sm text-[var(--primary)] font-medium">
              Live app, Clerk auth, Bedrock inference, Qdrant search
            </span>
          </div>
        </div>

        <div className="gsap-reveal text-center max-w-4xl mx-auto mb-8">
          <h1 className="display-lg mb-6">
            Stop losing deals to competitors
            <br />
            <span className="italic text-[var(--primary)]">with worse products</span>
          </h1>
          <p className="text-lg sm:text-xl text-[var(--ink-500)] max-w-2xl mx-auto leading-relaxed">
            RaptorFlow is your outsourced marketing team. Sign in once, then research your market,
            monitor competitors, and execute from the same workspace.
          </p>
        </div>

        <div className="gsap-reveal flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
          <a href="/sign-up" className="btn-primary px-8 py-4 text-base shadow-lg">
            Create your account
            <ArrowRight className="w-5 h-5" />
          </a>
        </div>

        <div className="gsap-reveal flex flex-col items-center gap-4">
          <div className="flex items-center gap-6 text-sm text-[var(--ink-500)] flex-wrap justify-center">
            <span className="flex items-center gap-1.5">
              <Check className="w-4 h-4 text-[var(--leaf-confirm)]" />
              Plain Clerk sign-in
            </span>
            <span className="flex items-center gap-1.5">
              <Check className="w-4 h-4 text-[var(--leaf-confirm)]" />
              No paywall
            </span>
            <span className="flex items-center gap-1.5">
              <Check className="w-4 h-4 text-[var(--leaf-confirm)]" />
              Full app access after login
            </span>
          </div>

          <div className="flex items-center gap-3 mt-2">
            <div className="flex -space-x-2">
              {[1, 2, 3, 4].map((i) => (
                <div
                  key={i}
                  className="w-8 h-8 rounded-full bg-[var(--paper-200)] border-2 border-white"
                />
              ))}
            </div>
            <p className="text-sm text-[var(--ink-500)]">
              <span className="font-semibold text-[var(--ink-900)]">4.9/5</span> from 127 founders
            </p>
          </div>
        </div>

        <div className="gsap-reveal mt-16 relative">
          <div className="absolute -inset-4 bg-gradient-to-t from-[var(--background)] via-transparent to-transparent z-10 pointer-events-none" />

          <div className="relative bg-white rounded-[var(--radius-xl)] shadow-2xl border border-[var(--border)] overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-3 bg-[var(--paper-150)] border-b border-[var(--border)]">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-[var(--destructive)]" />
                <div className="w-3 h-3 rounded-full bg-[var(--primary)]" />
                <div className="w-3 h-3 rounded-full bg-[var(--leaf-confirm)]" />
              </div>
              <div className="flex-1 flex justify-center">
                <div className="px-4 py-1 bg-white rounded-[var(--radius-sm)] text-xs text-[var(--ink-400)] border border-[var(--border)]">
                  app.raptorflow.in
                </div>
              </div>
            </div>

            <div className="p-6 bg-[var(--paper-50)]">
              <div className="grid grid-cols-3 gap-4">
                <div className="col-span-2 bg-white rounded-[var(--radius-lg)] p-5 shadow-sm border border-[var(--border)]">
                  <div className="flex items-center gap-2 text-sm text-[var(--leaf-confirm)] font-medium mb-4">
                    <span className="w-2 h-2 rounded-full bg-[var(--leaf-confirm)]" />
                    Morning Briefing — Tuesday, 8:04 AM
                  </div>
                  <h3 className="h3 mb-3">Your market moved overnight</h3>
                  <div className="space-y-3">
                    <div className="flex items-start gap-3">
                      <div className="w-1.5 h-1.5 rounded-full bg-[var(--primary)] mt-2" />
                      <p className="text-sm text-[var(--ink-500)]">
                        <span className="font-medium text-[var(--ink-900)]">Competitor alert:</span>{" "}
                        MenuIQ launched 4 new Google ads targeting your keywords
                      </p>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="w-1.5 h-1.5 rounded-full bg-[var(--primary)] mt-2" />
                      <p className="text-sm text-[var(--ink-500)]">
                        <span className="font-medium text-[var(--ink-900)]">Opportunity:</span>{" "}
                        "dynamic pricing India" has 890 searches/month, weak competition
                      </p>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="w-1.5 h-1.5 rounded-full bg-[var(--primary)] mt-2" />
                      <p className="text-sm text-[var(--ink-500)]">
                        <span className="font-medium text-[var(--ink-900)]">Action:</span> Publish
                        Swiggy commission breakdown — estimated 40-60 visits/month
                      </p>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="bg-white rounded-[var(--radius-lg)] p-4 shadow-sm border border-[var(--border)]">
                    <div className="text-2xl font-bold font-display text-[var(--ink-900)]">
                      340%
                    </div>
                    <div className="text-sm text-[var(--ink-500)]">Organic growth</div>
                    <div className="mt-2 h-1.5 bg-[var(--paper-150)] rounded-full overflow-hidden">
                      <div className="h-full w-3/4 bg-[var(--primary)] rounded-full" />
                    </div>
                  </div>
                  <div className="bg-white rounded-[var(--radius-lg)] p-4 shadow-sm border border-[var(--border)]">
                    <div className="text-2xl font-bold font-display text-[var(--ink-900)]">12</div>
                    <div className="text-sm text-[var(--ink-500)]">Pieces published</div>
                  </div>
                  <div className="bg-white rounded-[var(--radius-lg)] p-4 shadow-sm border border-[var(--border)]">
                    <div className="text-2xl font-bold font-display text-[var(--ink-900)]">2</div>
                    <div className="text-sm text-[var(--ink-500)]">Inbound demos</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </GsapBridge>
    </section>
  );
}
