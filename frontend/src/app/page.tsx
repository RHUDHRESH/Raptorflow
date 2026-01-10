"use client";

import React from "react";
import { TrendingUp, Target, Zap, Compass, ArrowUpRight, Play } from "lucide-react";
import Link from 'next/link';
import { BlueprintCard, CardFooter } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { InteractiveHero } from "@/components/InteractiveHero";

export const dynamic = 'force-dynamic';

/* ══════════════════════════════════════════════════════════════════════════════
   THE PAPER TERMINAL — Landing Page
   ══════════════════════════════════════════════════════════════════════════════ */

export default function RootLanding() {
  return (
    <div className="min-h-screen bg-[var(--canvas)] relative overflow-hidden">
      {/* Background Effects */}
      <div className="fixed inset-0 pointer-events-none z-0" style={{ backgroundImage: "url('/textures/paper-grain.png')", opacity: 0.05, mixBlendMode: "multiply" }} />
      <div className="fixed inset-0 blueprint-grid-major pointer-events-none opacity-30" />

      {/* Header */}
      <header className="relative z-20 w-full max-w-7xl mx-auto px-8 py-8">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-4">
            <div className="h-12 w-12 rounded-[var(--radius-sm)] bg-[var(--ink)] text-[var(--paper)] flex items-center justify-center ink-bleed-sm relative">
              <Compass size={24} strokeWidth={1.5} />
              <div className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-[var(--blueprint)] border border-[var(--paper)] animate-pulse" />
            </div>
            <div>
              <span className="font-editorial text-2xl text-[var(--ink)]">
                RaptorFlow
              </span>
              <span className="font-technical text-[var(--blueprint)]">
                MARKETING OPERATING SYSTEM
              </span>
            </div>
          </div>

          {/* Interactive Navigation */}
          <InteractiveHero />
        </div>
      </header>

      {/* HERO SECTION */}
      <section className="space-y-12 max-w-4xl mx-auto px-8 py-16">
        {/* Figure annotation */}
        <div className="flex items-center gap-4">
          <span className="font-technical text-[var(--blueprint)]">FIG. 01</span>
          <div className="h-px w-16 bg-[var(--blueprint)]" />
          <span className="font-technical text-[var(--muted)]">HERO MODULE</span>
        </div>

        {/* Main Headline */}
        <div className="space-y-4">
          <h1 className="text-7xl md:text-9xl font-serif font-medium text-[var(--ink)] leading-[0.9] tracking-tight">
            The Paper
          </h1>
          <h1 className="text-7xl md:text-9xl font-serif font-medium text-[var(--ink)] leading-[0.9] tracking-tight italic">
            Terminal
          </h1>

          {/* Technical annotation */}
          <div className="flex items-center gap-3 pt-6">
            <div className="h-px w-24 bg-[var(--blueprint)]" />
            <span className="font-technical text-[var(--blueprint)]">
              FONT: PLAYFAIR DISPLAY / 144PT / MEDIUM
            </span>
          </div>
        </div>

        {/* Subheadline */}
        <p className="text-xl md:text-2xl text-[var(--secondary)] leading-relaxed max-w-2xl font-light">
          Where premium paper texture meets technical precision.
          An architect's desk for the modern founder.
        </p>

        {/* CTA Buttons */}
        <div className="flex items-center gap-6 pt-8">
          <Link href="/signup" className="inline-block">
            <BlueprintButton size="lg" label="BTN-03">
              Initialize Workspace
              <ArrowUpRight size={18} strokeWidth={1.5} />
            </BlueprintButton>
          </Link>

          <SecondaryButton size="lg">
            <Play size={14} fill="currentColor" />
            Watch Demo
            <span className="font-technical text-[var(--muted)]">02:34</span>
          </SecondaryButton>
        </div>
      </section>

      {/* FEATURES SECTION */}
      <section className="space-y-10 max-w-7xl mx-auto px-8 py-16">
        {/* Section Header */}
        <div className="flex items-center gap-4">
          <span className="font-technical text-[var(--blueprint)]">FIG. 02</span>
          <div className="h-px flex-1 bg-[var(--blueprint-line)]" />
          <span className="font-technical text-[var(--muted)]">CORE MODULES</span>
          <div className="h-px w-8 bg-[var(--blueprint-line)]" />
          <span className="font-technical text-[var(--blueprint)]">03 ITEMS</span>
        </div>

        {/* Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            {
              title: "Moves Board",
              code: "MOV-01",
              figure: "FIG. 02-A",
              desc: "Weekly execution rhythm with tactical precision. Every move tracked, measured, proven.",
              icon: Zap,
            },
            {
              title: "Campaign Planner",
              code: "CMP-02",
              figure: "FIG. 02-B",
              desc: "90-day strategic arcs mapped on paper. Your marketing roadmap, architecturally designed.",
              icon: Target,
            },
            {
              title: "Proof Analytics",
              code: "ANL-03",
              figure: "FIG. 02-C",
              desc: "Outcomes measured, not vanity metrics. Evidence-based marketing decisions.",
              icon: TrendingUp,
            },
          ].map((item, index) => (
            <BlueprintCard
              key={item.code}
              figure={item.figure}
              code={item.code}
              showCorners
              showMeasurements
              variant="elevated"
              padding="lg"
              className="group hover:-translate-y-1 transition-transform duration-300"
            >
              {/* Icon container */}
              <div className="w-14 h-14 rounded-[var(--radius-sm)] bg-[var(--canvas)] border border-[var(--border)] flex items-center justify-center mb-6 group-hover:bg-[var(--blueprint-light)] group-hover:border-[var(--blueprint)] transition-colors">
                <item.icon
                  size={28}
                  strokeWidth={1.5}
                  className="text-[var(--muted)] group-hover:text-[var(--blueprint)] transition-colors"
                />
              </div>

              {/* Content */}
              <h3 className="text-2xl font-editorial text-[var(--ink)] mb-3">
                {item.title}
              </h3>
              <p className="text-sm text-[var(--secondary)] leading-relaxed">
                {item.desc}
              </p>

              <CardFooter>
                <Link href="/dashboard" className="flex items-center gap-2 font-technical text-[var(--muted)] hover:text-[var(--blueprint)] transition-colors">
                  <span>EXPLORE MODULE</span>
                  <ArrowUpRight size={12} className="group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                </Link>
              </CardFooter>
            </BlueprintCard>
          ))}
        </div>
      </section>

      {/* FOOTER */}
      <footer className="pt-16 border-t border-[var(--border)]">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-12 max-w-7xl mx-auto px-8">
          {/* Brand */}
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <Compass size={20} strokeWidth={1.5} className="text-[var(--ink)]" />
              <span className="font-serif font-semibold text-lg text-[var(--ink)]">
                RaptorFlow
              </span>
              <span className="font-technical text-[var(--muted)]">
                {new Date().getFullYear()}
              </span>
            </div>
            <p className="text-sm text-[var(--secondary)] max-w-md leading-relaxed">
              Built for founders who value silence, speed, and surgical precision.
              The operating system for modern marketing.
            </p>
          </div>

          {/* Links */}
          <div className="flex items-center gap-10">
            {["Privacy", "Terms", "Documentation", "GitHub"].map((link) => (
              <Link
                key={link}
                href={`#${link.toLowerCase()}`}
                className="font-technical text-[var(--muted)] hover:text-[var(--ink)] transition-colors"
              >
                {link.toUpperCase()}
              </Link>
            ))}
          </div>
        </div>

        {/* Document info */}
        <div className="mt-8 flex justify-center">
          <span className="font-technical text-[var(--muted)]">
            DOCUMENT: LANDING-PAGE-V2.0 | REVISION: {new Date().toISOString().split('T')[0]} | SCALE: 1:1
          </span>
        </div>
      </footer>
    </div>
  );
}
