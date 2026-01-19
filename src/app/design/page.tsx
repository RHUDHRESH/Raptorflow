"use client";

import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintTimeline } from "@/components/ui/BlueprintTimeline";
import { BlueprintProgress } from "@/components/ui/BlueprintProgress";
import { BlueprintCommandPrompt } from "@/components/ui/BlueprintCommandPrompt";
import { useState } from "react";
import { Zap, Shield, Box, Check, Star } from "lucide-react";

/* ══════════════════════════════════════════════════════════════════════════════
   DESIGN SYSTEM GALLERY
   Verification suite for the new UI components.
   ══════════════════════════════════════════════════════════════════════════════ */

export default function DesignPage() {
    const [progress, setProgress] = useState(45);

    const timelineEvents = [
        { id: "1", title: "Market Infiltration", description: "Stealth launch of beta", timestamp: "T-MINUS 12D", status: "complete" as const, code: "MKT-01" },
        { id: "2", title: "Viral Loop Activation", description: "Referral engine spin-up", timestamp: "TODAY", status: "current" as const, code: "VIR-88" },
        { id: "3", title: "Revenue Capture", description: "Paywall deployment", timestamp: "T-PLUS 7D", status: "pending" as const, code: "REV-99" },
    ];

    return (
        <div className="max-w-4xl mx-auto space-y-12 pb-24">
            <div>
                <h1 className="font-serif text-4xl text-[var(--ink)]">Design System</h1>
                <p className="text-[var(--ink-secondary)]">Component Verification Laboratory</p>
            </div>

            {/* Typography */}
            <section className="space-y-4">
                <h2 className="text-xs font-mono uppercase text-[var(--muted)]">01 // TYPOGRAPHY</h2>
                <div className="grid grid-cols-2 gap-8">
                    <div className="space-y-2">
                        <p className="font-serif text-4xl">H1 Editorial</p>
                        <p className="font-serif text-2xl">H2 Serif Display</p>
                        <p className="font-sans text-xl font-bold">H3 Sans Bold</p>
                    </div>
                    <div className="space-y-2">
                        <p className="font-technical text-[var(--blueprint)]">TECHNICAL DATA READOUT</p>
                        <p className="font-mono text-xs">Monospace Code Value</p>
                        <p className="text-sm text-[var(--ink-secondary)] leading-relaxed">
                            Body text designed for high readability in dense information environments.
                            The Paper Terminal aesthetic relies on crisp typography and whitespace.
                        </p>
                    </div>
                </div>
            </section>

            {/* Buttons */}
            <section className="space-y-4">
                <h2 className="text-xs font-mono uppercase text-[var(--muted)]">02 // ACTIONS</h2>
                <div className="flex gap-4 items-center">
                    <BlueprintButton>Primary Action</BlueprintButton>
                    <SecondaryButton>Secondary</SecondaryButton>
                    <BlueprintButton disabled>Disabled</BlueprintButton>
                    <BlueprintButton className="bg-[var(--error)] hover:bg-[var(--error)]/90 border-transparent text-white">Destructive</BlueprintButton>
                </div>
            </section>

            {/* Cards */}
            <section className="space-y-4">
                <h2 className="text-xs font-mono uppercase text-[var(--muted)]">03 // CONTAINERS</h2>
                <div className="grid grid-cols-2 gap-6">
                    <BlueprintCard title="Standard Card" figure="FIG A" showCorners padding="lg">
                        This is a standard content container with corner marks.
                    </BlueprintCard>
                    <BlueprintCard title="Elevated" variant="elevated" padding="lg">
                        Elevated card for specialized content.
                    </BlueprintCard>
                </div>
            </section>

            {/* Timeline */}
            <section className="space-y-4">
                <h2 className="text-xs font-mono uppercase text-[var(--muted)]">04 // TIMELINE</h2>
                <BlueprintCard padding="lg">
                    <BlueprintTimeline events={timelineEvents} figure="SEQ-09" />
                </BlueprintCard>
            </section>

            {/* Progress & Badges */}
            <section className="space-y-4">
                <h2 className="text-xs font-mono uppercase text-[var(--muted)]">05 // INDICATORS</h2>
                <div className="space-y-6">
                    <div>
                        <BlueprintProgress value={progress} max={100} label="System Integrity" />
                        <input type="range" value={progress} onChange={(e) => setProgress(Number(e.target.value))} className="mt-2 w-full" />
                    </div>
                    <div className="flex gap-2">
                        <BlueprintBadge variant="default">Default</BlueprintBadge>
                        <BlueprintBadge variant="blueprint">Blueprint</BlueprintBadge>
                        <BlueprintBadge variant="success">Success</BlueprintBadge>
                        <BlueprintBadge className="bg-[var(--blueprint)] text-white">Custom</BlueprintBadge>
                    </div>
                </div>
            </section>

            {/* Command Palette Test */}
            <section className="space-y-4">
                <h2 className="text-xs font-mono uppercase text-[var(--muted)]">06 // COMMAND</h2>
                <BlueprintCard className="flex items-center justify-between p-4 bg-[var(--surface)]">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-[var(--paper)] border rounded">⌘K</div>
                        <span>Press Cmd+K to open Global Command</span>
                    </div>
                </BlueprintCard>
            </section>
        </div>
    );
}
