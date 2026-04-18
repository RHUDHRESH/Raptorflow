"use client";

import type * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { useBillingStatus } from "@/hooks/use-billing";
import { GsapBridge } from "@/components/ui/gsap-bridge";
import { GearIcon, IdCardIcon, AvatarIcon, Link1Icon, CheckIcon } from "@radix-ui/react-icons";
import { referralSignupHref } from "@/lib/referrals";

export default function BillingPage(): React.ReactElement {
  const { data: billing, isLoading } = useBillingStatus();

  return (
    <div className="min-h-[calc(100vh-theme(spacing.16))] bg-[var(--background)] px-6 py-12 md:px-12 font-body">
      <GsapBridge stagger={true} className="mx-auto max-w-[1200px] flex flex-col md:flex-row gap-12">
        
        {/* Left Nav */}
        <aside className="gsap-reveal w-full md:w-64 shrink-0">
          <h1 className="font-[family-name:var(--font-display)] text-5xl mb-8">Settings</h1>
          <nav className="flex flex-col space-y-2 font-mono text-xs uppercase tracking-widest">
            <Link href={"/settings" as Route} className="flex items-center gap-3 hover:bg-[var(--accent)] text-[var(--foreground)] px-4 py-3 transition-colors">
              <GearIcon className="h-4 w-4" /> Workspace
            </Link>
            <Link href={"/billing" as Route} className="flex items-center gap-3 bg-[var(--primary)] text-[var(--primary-foreground)] px-4 py-3">
              <IdCardIcon className="h-4 w-4" /> Billing & Plan
            </Link>
            <button className="flex items-center gap-3 hover:bg-[var(--accent)] text-[var(--foreground)] px-4 py-3 transition-colors text-left">
              <AvatarIcon className="h-4 w-4" /> Team Access
            </button>
            <button className="flex items-center gap-3 hover:bg-[var(--accent)] text-[var(--foreground)] px-4 py-3 transition-colors text-left">
              <Link1Icon className="h-4 w-4" /> Integrations
            </button>
          </nav>
        </aside>

        {/* Main Content */}
        <div className="flex-1 space-y-16">
          
          <section className="gsap-reveal border-t-2 border-[var(--foreground)] pt-6">
            <div className="flex justify-between items-end mb-8">
              <h2 className="font-mono text-xs uppercase tracking-widest text-[var(--muted-foreground)]">Plans</h2>
              {billing?.subscription_status === "active" && (
                 <span className="font-mono text-[10px] uppercase tracking-widest bg-green-900/40 text-green-400 border border-green-800 px-3 py-1">Active</span>
              )}
            </div>

            {billing?.current_plan && (
              <div className="mb-8 border border-[var(--border)] bg-[var(--card)] p-4">
                <p className="font-mono text-[10px] uppercase tracking-[0.28em] text-[var(--muted-foreground)]">
                  Current access
                </p>
                <div className="mt-2 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                  <div>
                    <h3 className="font-[family-name:var(--font-display)] text-2xl">
                      {billing.current_plan.name}
                    </h3>
                    <p className="text-sm text-[var(--muted-foreground)]">
                      {billing.current_plan.price_inr_monthly === 0
                        ? "Referral unlocked: no charge on this workspace."
                        : "Subscription is active on the selected paid plan."}
                    </p>
                  </div>
                  <a
                    href={referralSignupHref("LOKI")}
                    className="font-mono text-[10px] uppercase tracking-[0.28em] text-[var(--primary)]"
                  >
                    Share access link
                  </a>
                </div>
              </div>
            )}
            
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {isLoading ? (
                <div className="col-span-4 h-64 bg-[var(--muted)] animate-pulse" />
              ) : (
                billing?.available_plans?.map((plan) => (
                  <div key={plan.tier} className={`border bg-[var(--card)] p-6 flex flex-col ${plan.tier === billing?.current_plan?.tier ? 'border-[var(--primary)] ring-2 ring-[var(--primary)]' : 'border-[var(--border)]'}`}>
                    <div className="mb-4">
                      <h3 className="font-[family-name:var(--font-display)] text-2xl mb-1">{plan.name}</h3>
                      <p className="font-mono text-xs text-[var(--muted-foreground)]">{plan.description}</p>
                    </div>
                    
                    <div className="mb-6">
                      {plan.price_inr_monthly === "talk_to_us" ? (
                        <p className="font-mono text-lg text-[var(--primary)]">Talk to Us</p>
                      ) : (
                        <>
                          <span className="font-mono text-3xl">₹{Number(plan.price_inr_monthly).toLocaleString()}</span>
                          <span className="font-mono text-xs text-[var(--muted-foreground)]"> / month</span>
                        </>
                      )}
                    </div>
                    
                    <ul className="space-y-2 mb-6 flex-1">
                      {plan.features.map((feat: string, i: number) => (
                        <li key={i} className="flex items-start gap-2 text-xs">
                          <CheckIcon className="h-3 w-3 text-[var(--primary)] shrink-0 mt-0.5" />
                          <span className="text-[var(--muted-foreground)]">{feat}</span>
                        </li>
                      ))}
                    </ul>
                    
                    <button className={`w-full h-10 font-mono text-[10px] uppercase tracking-widest transition-colors ${
                      plan.tier === billing?.current_plan?.tier 
                        ? 'bg-[var(--muted)] text-[var(--muted-foreground)] cursor-default'
                        : plan.tier === 'enterprise'
                          ? 'bg-[var(--foreground)] text-[var(--background)] hover:bg-[var(--primary)]'
                          : 'bg-transparent border border-[var(--foreground)] text-[var(--foreground)] hover:bg-[var(--foreground)] hover:text-[var(--background)]'
                    }`}>
                      {plan.tier === billing?.current_plan?.tier ? 'Current Plan' : plan.tier === 'enterprise' ? 'Contact Sales' : 'Subscribe'}
                    </button>
                  </div>
                ))
              )}
            </div>
            
            <div className="mt-8 p-4 bg-[var(--card)] border border-[var(--border)]">
              <p className="font-mono text-xs text-[var(--muted-foreground)] text-center">
                💡 All prices in <strong>INR (Indian Rupees)</strong>. No USD pricing. Enterprise custom solutions available.
              </p>
            </div>
          </section>

        </div>
      </GsapBridge>
    </div>
  );
}
