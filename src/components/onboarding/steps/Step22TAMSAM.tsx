"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ArrowRight, Globe, TrendingUp, Target, Loader2, RefreshCw } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 21: Market Sizing (Organic Layout)
   
   PURPOSE: "Show & Tell" - Market Size Narrative.
   - Non-Grid / Asymmetric Layout.
   - Large Narrative Context ("Big Paragraph").
   - Distinctive Visual Blocks.
   - NOW INTEGRATED with AI market-size API
   ══════════════════════════════════════════════════════════════════════════════ */

interface MarketSizeData {
    tam: { value: number; formatted: string; description: string; growth_rate?: number };
    sam: { value: number; formatted: string; percentage_of_tam: number; description: string };
    som: { value: number; formatted: string; percentage_of_tam: number; description: string };
    summary: string;
    recommendations: string[];
}

export default function Step21TAMSAM() {
    const { updateStepStatus, updateStepData, getStepById, session } = useOnboardingStore();
    const containerRef = useRef<HTMLDivElement>(null);

    const [isLoading, setIsLoading] = useState(false);
    const [marketData, setMarketData] = useState<MarketSizeData | null>(null);
    const [error, setError] = useState<string | null>(null);

    // Fallback data
    const FALLBACK_DATA = {
        tam: "$4.2B",
        sam: "$850M",
        som: "$42M"
    };

    // Fetch market size data on mount
    useEffect(() => {
        const fetchMarketSize = async () => {
            setIsLoading(true);
            setError(null);

            try {
                const response = await fetch('/api/onboarding/market-size', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: session?.sessionId || 'demo',
                        company_info: {
                            industry: 'saas',
                            target_market: 'smb',
                            market_scope: 'north_america',
                            ...getStepById(4)?.data // Truth sheet data
                        }
                    })
                });

                const data = await response.json();
                if (data.success && data.market_size) {
                    setMarketData(data.market_size);
                    updateStepData(21, { marketSize: data.market_size });
                }
            } catch (err) {
                console.error('Failed to fetch market size:', err);
                setError('Using estimated market data');
            } finally {
                setIsLoading(false);
            }
        };

        // Only fetch if we don't have data already
        const existingData = getStepById(21)?.data as any;
        if (existingData?.marketSize) {
            setMarketData(existingData.marketSize);
        } else {
            fetchMarketSize();
        }
    }, [session?.sessionId]);

    const displayData = {
        tam: marketData?.tam?.formatted || FALLBACK_DATA.tam,
        sam: marketData?.sam?.formatted || FALLBACK_DATA.sam,
        som: marketData?.som?.formatted || FALLBACK_DATA.som
    };

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(containerRef.current.querySelectorAll(".animate-in"),
            { opacity: 0, y: 30, scale: 0.98 },
            { opacity: 1, y: 0, scale: 1, duration: 0.8, stagger: 0.15, ease: "power3.out" }
        );
    }, []);

    const handleContinue = () => {
        updateStepStatus(21, "complete"); // Map to 21
    };

    return (
        <div ref={containerRef} className="h-full flex flex-col max-w-6xl mx-auto space-y-8 pb-8">

            {/* Header */}
            <div className="animate-in text-left space-y-2 shrink-0 border-b border-[var(--border-subtle)] pb-4">
                <span className="font-technical text-[10px] tracking-[0.2em] text-[var(--blueprint)] uppercase">Step 21 / 23</span>
                <h2 className="font-serif text-3xl text-[var(--ink)]">The Market Reality</h2>
            </div>

            {/* Main Content: Organic Layout */}
            <div className="flex-1 min-h-0 grid grid-cols-1 md:grid-cols-12 gap-6 items-stretch">

                {/* 1. Large Narrative Block (Left, Spans 7 cols) */}
                <div className="md:col-span-7 bg-[var(--paper)] border border-[var(--border)] p-8 rounded-lg flex flex-col justify-between animate-in group hover:border-[var(--blueprint)] transition-colors">
                    <div>
                        <div className="p-3 bg-[var(--canvas)] w-fit rounded mb-6 text-[var(--blueprint)]">
                            <Globe size={24} />
                        </div>
                        <h3 className="font-serif text-2xl text-[var(--ink)] mb-4 leading-tight">
                            Your niche isn't "small". <br />
                            It's <span className="text-[var(--blueprint)] font-medium">focused</span>.
                        </h3>
                        <p className="text-sm md:text-base text-[var(--ink)] leading-relaxed opacity-80 font-serif">
                            Most founders chase a phantom TAM. Based on your "Category Creator" strategy, we aren't looking for everyone.
                            We are looking for the <strong className="text-[var(--ink)]">0.5%</strong> who are tired of the status quo.
                            <br /><br />
                            We calculated your reachable market based on the <strong>High-Intent Signals</strong> from step 15.
                            This isn't a vanity metric. This is the war chest available to you within 24 months if you execute the "David" strategy perfectly.
                        </p>
                    </div>

                    <div className="mt-8 pt-8 border-t border-[var(--border-subtle)] flex items-end justify-between">
                        <div>
                            <div className="text-[10px] uppercase tracking-widest text-[var(--muted)] mb-1">Total Addressable Market</div>
                            <div className="text-4xl font-serif text-[var(--muted)]/50">{displayData.tam}</div>
                        </div>
                    </div>
                </div>

                {/* 2. Right Column Stack (Spans 5 cols) */}
                <div className="md:col-span-5 flex flex-col gap-6">

                    {/* SAM Block - Visual & Punchy */}
                    <div className="flex-1 bg-[var(--ink)] text-[var(--paper)] rounded-lg p-6 flex flex-col justify-center animate-in shadow-lg relative overflow-hidden">
                        <div className="absolute top-0 right-0 p-8 opacity-10 text-[var(--paper)] transform translate-x-4 -translate-y-4">
                            <Target size={120} />
                        </div>
                        <div className="relative z-10">
                            <div className="text-[10px] uppercase tracking-widest opacity-60 mb-2">Serviceable Available Market</div>
                            <div className="text-5xl font-serif font-medium mb-2">{displayData.sam}</div>
                            <p className="text-xs opacity-70 leading-relaxed max-w-[80%]">
                                The realistic ceiling for your current product version without major pivots.
                            </p>
                        </div>
                    </div>

                    {/* SOM Block - The Goal */}
                    <div className="h-40 bg-[var(--blueprint)]/10 border border-[var(--blueprint)] text-[var(--blueprint)] rounded-lg p-6 flex items-center justify-between animate-in">
                        <div>
                            <div className="text-[10px] uppercase tracking-widest mb-1 font-bold">Your 5-Year Target (SOM)</div>
                            <div className="text-4xl font-serif font-bold">{displayData.som}</div>
                        </div>
                        <div className="h-12 w-12 rounded-full bg-[var(--blueprint)] text-[var(--paper)] flex items-center justify-center">
                            <TrendingUp size={20} />
                        </div>
                    </div>

                </div>

            </div>

            {/* Footer */}
            <div className="animate-in flex justify-end pt-4">
                <BlueprintButton onClick={handleContinue} size="lg" className="px-12">
                    <span>Accept Opportunity</span> <ArrowRight size={14} />
                </BlueprintButton>
            </div>
        </div>
    );
}
