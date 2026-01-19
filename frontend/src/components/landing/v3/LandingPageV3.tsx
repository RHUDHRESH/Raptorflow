"use client";

import React, { useEffect } from "react";
import { ReactLenis } from "@studio-freight/react-lenis";
import { HeroV3 } from "./sections/HeroV3";
import { SystemV3 } from "./sections/SystemV3";
import { DiagnosisV3 } from "./sections/DiagnosisV3";
import { GapV3 } from "./sections/GapV3";
import { ManifestoV3 } from "./sections/ManifestoV3";
import { ComparisonV3 } from "./sections/ComparisonV3";
import { IntegrationsV3 } from "./sections/IntegrationsV3";
import { MethodologyV3 } from "./sections/MethodologyV3";
import { ResultsV3 } from "./sections/ResultsV3";
import { PricingV3 } from "./sections/PricingV3";
import { FooterV3 } from "./sections/FooterV3";
// We'll lazy load Lenis to ensure it only runs on client
// For now, using a simple useEffect scroll for structure.

// Fonts
// We assume CSS variables are available globally from layout.tsx
// --font-inter (Sans)
// --font-jetbrains (Mono)

/**
 * LANDING PAGE V3 - "THE ARCHITECTURAL"
 * 
 * Philosophy:
 * - Razor Strict: 1px Borders.
 * - Grid-Locked: Everything aligns.
 * - Signal Only: High contrast, no decoration.
 */
export default function LandingPageV3() {

    // Initialize Lenis (Placeholder for now - strictly structural first)
    useEffect(() => {
        // lenis init code would go here
        document.documentElement.classList.add('v3-mode');
        return () => {
            document.documentElement.classList.remove('v3-mode');
        }
    }, []);

    return (
        <main className="min-h-screen bg-[#050505] text-[#FAFAFA] font-sans selection:bg-[#3B82F6] selection:text-white">

            {/* 
              Global "Page Frame" 
              A fixed border that wraps the entire experience, 
              giving it a "Dashboard" or "Software" feel rather than a "Web Page".
            */}
            <div className="fixed inset-0 pointer-events-none z-[9999] border-[12px] border-[#050505] hidden md:block" />
            <div className="fixed inset-3 pointer-events-none z-[9998] border border-white/10 rounded-sm hidden md:block" />

            {/* Content Container - Centered "A4" feel but wider */}
            <div className="relative w-full max-w-[1440px] mx-auto border-x border-dashed border-white/10 min-h-screen">

                {/* 
                  Grid Overlay (Optional - toggleable debug) 
                  Can be made visible for "The Schematic" feel
                */}
                <div className="absolute inset-0 pointer-events-none opacity-[0.03]"
                    style={{ backgroundImage: `linear-gradient(to right, #ffffff 1px, transparent 1px), linear-gradient(to bottom, #ffffff 1px, transparent 1px)`, backgroundSize: '40px 40px' }}
                />

                {/* HEADER (Placeholder) */}
                <header className="sticky top-0 z-50 flex items-center justify-between px-6 py-4 bg-[#050505]/80 backdrop-blur-md border-b border-white/10">
                    <div className="flex items-center gap-4">
                        <div className="w-4 h-4 bg-white" /> {/* Logo Mark */}
                        <span className="font-mono text-sm tracking-widest uppercase">RaptorFlow_V3</span>
                    </div>

                    <div className="flex items-center gap-6">
                        <span className="font-mono text-xs text-white/50">SYSTEM_ONLINE</span>
                        <button className="px-6 py-2 border border-white text-xs font-mono uppercase tracking-wider hover:bg-white hover:text-black transition-colors duration-200">
                            Initialize
                        </button>
                    </div>
                </header>

                {/* SECTIONS ORCHESTRATOR */}
                <div className="relative z-10">
                    <HeroV3 />
                    <SystemV3 />
                    <DiagnosisV3 />
                    <GapV3 />
                    <ManifestoV3 />
                    <ComparisonV3 />
                    <IntegrationsV3 />
                    <MethodologyV3 />
                    <ResultsV3 />
                    <PricingV3 />
                    <FooterV3 />
                </div>

            </div>
        </main>
    );
}
