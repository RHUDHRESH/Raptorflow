"use client";

import React from "react";

// Section imports
import {
    HeaderV2,
    HeroV2,
    SocialProofV2,
    ProblemStatement,
    SystemGrid,
    JourneySection,
    BenefitsV2,
    TestimonialsV2,
    PricingV2,
    FAQSection,
    FinalCTA,
    FooterV2,
} from "./sections";

// Shared imports
import { ScrollProgress } from "./shared";

// ═══════════════════════════════════════════════════════════════
// LandingPageV2 - Orchestrator Component
// ═══════════════════════════════════════════════════════════════
// 
// This is the main landing page v2 component that composes all sections.
// Each section is designed to be enhanced independently in future sessions.
//
// Session Roadmap:
// - Session 1: Hero cinematics + scroll infrastructure ✓ (shell ready)
// - Session 2: Social Proof marquee + Problem statement drama
// - Session 3: SystemGrid interactivity + module flow visuals
// - Session 4: Journey scroll-driven reveal + progress indicator
// - Session 5: Benefits dark section polish
// - Session 6: Testimonials carousel/rotation
// - Session 7: Pricing premium effects
// - Session 8: Final CTA + Footer polish
// - Session 9: Performance + cross-browser
//
// ═══════════════════════════════════════════════════════════════

export default function LandingPageV2() {
    return (
        <main className="min-h-screen bg-[var(--canvas)] text-[var(--ink)] overflow-x-hidden">
            {/* Reading Progress Indicator */}
            <ScrollProgress position="top" color="var(--accent)" />

            {/* Fixed Header */}
            <HeaderV2 />

            {/* Hero Section */}
            <HeroV2 />

            {/* Social Proof Bar */}
            <SocialProofV2 />

            {/* Problem Statement */}
            <ProblemStatement />

            {/* The System - Module Grid */}
            <SystemGrid />

            {/* How It Works - Journey */}
            <JourneySection />

            {/* Benefits - Why Switch */}
            <BenefitsV2 />

            {/* Testimonials */}
            <TestimonialsV2 />

            {/* Pricing */}
            <PricingV2 />

            {/* FAQ */}
            <FAQSection />

            {/* Final CTA */}
            <FinalCTA />

            {/* Footer */}
            <FooterV2 />
        </main>
    );
}
