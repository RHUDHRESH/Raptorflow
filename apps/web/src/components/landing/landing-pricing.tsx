"use client";

import * as React from "react";
import { ArrowRight, Check } from "lucide-react";
import { GsapBridge } from "@/components/ui/gsap-bridge";

export function LandingPricing() {
  return (
    <section id="access" className="py-24 paper-soft">
      <GsapBridge stagger className="mx-auto max-w-6xl px-6 lg:px-8">
        <div className="gsap-reveal text-center max-w-3xl mx-auto mb-16">
          <p className="eyebrow mb-4">Access</p>
          <h2 className="display-md mb-4">
            One login. <span className="italic text-[var(--primary)]">Full product access.</span>
          </h2>
          <p className="text-lg text-[var(--ink-500)]">
            Sign in with Clerk and use the app immediately. No plans, no paywall, no unlock step.
          </p>
        </div>

        <div className="gsap-reveal max-w-4xl mx-auto">
          <div className="grid md:grid-cols-3 gap-6">
            {[
              "Clerk sign-in and sign-up only",
              "Live backend, no mock access wall",
              "Everything unlocked after login",
            ].map((item) => (
              <div
                key={item}
                className="bg-white rounded-[var(--radius-lg)] p-6 border border-[var(--border)] card-elevated"
              >
                <div className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-[var(--primary)] shrink-0 mt-0.5" />
                  <p className="text-[var(--ink-700)]">{item}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="gsap-reveal text-center mt-10">
            <a href="/sign-up" className="btn-primary px-8 py-4 text-base shadow-lg">
              Create your account
              <ArrowRight className="w-5 h-5" />
            </a>
          </div>
        </div>
      </GsapBridge>
    </section>
  );
}
