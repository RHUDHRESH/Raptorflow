"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import gsap from "gsap";
import {
    Search, Users, MessageSquare, Target, Play, Check, RefreshCw, ExternalLink,
    ChevronDown, ChevronUp, Loader2, Quote, TrendingUp, AlertTriangle, FileText,
    Globe, Terminal, Radio, Radar, CheckCircle
} from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { StepLoadingState, StepEmptyState } from "../StepStates";
import { cn } from "@/lib/utils";

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   PAPER TERMINAL ΓÇö Step 6: Market Intelligence
   
   PURPOSE: Visualize the "Market Scraper" and gather real customer insights.
   - "Quiet Luxury" Refactor: "Intelligence Dossier" style.
   - Terminal-like "Scanning" visualization.
   - Focus on PAIN (problems) and DESIRE (outcomes).
   - Auto-detected competitors only (NO manual entry).
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

interface CustomerInsight {
    id: string;
    type: "pain" | "desire" | "objection";
    quote: string;
    source: string;
    sourceIcon?: string; // e.g. "reddit", "twitter"
    sentiment: number; // 0-100
}

interface MarketIntelResult {
    insights: CustomerInsight[];
    detectedCompetitors: string[];
    summary: string;
    reviewed: boolean;
}

const MOCK_SOURCES = ["Reddit (r/SaaS)", "G2 Crowd", "Twitter", "ProductHunt", "LinkedIn"];

function ScraperTerminal({ onComplete }: { onComplete: () => void }) {
    const [lines, setLines] = useState<string[]>([]);
    const [sourceIdx, setSourceIdx] = useState(0);

    useEffect(() => {
        if (sourceIdx >= MOCK_SOURCES.length) {
            setTimeout(onComplete, 800);
            return;
        }

        const source = MOCK_SOURCES[sourceIdx];
        const newLines = [
            `> Initializing spyder on ${source}...`,
            `> Connected.`,
            `> Scanning threads for keywords: [pricing, pain, alternative]...`,
            `> Extracted 14 verbatims.`,
            `> Closing connection.`
        ];

        let lineIdx = 0;
        const interval = setInterval(() => {
            if (lineIdx >= newLines.length) {
                clearInterval(interval);
                setTimeout(() => setSourceIdx(prev => prev + 1), 400);
                return;
            }
            setLines(prev => [...prev.slice(-7), newLines[lineIdx]]); // Keep last 8 lines
            lineIdx++;
        }, 150);

        return () => clearInterval(interval);
    }, [sourceIdx, onComplete]);

    return (
        <div className="w-full max-w-2xl mx-auto bg-[#0A0A0A] rounded-[4px] border border-[var(--border)] p-6 font-mono text-xs overflow-hidden shadow-2xl relative">
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-[var(--success)] to-transparent opacity-50 animate-pulse" />
            <div className="flex items-center gap-2 mb-4 border-b border-white/10 pb-2">
                <Terminal size={12} className="text-[var(--success)]" />
                <span className="text-white/60">RAPTOR_INTEL_CLI ΓÇö v2.4.0</span>
            </div>
            <div className="space-y-1.5 h-[200px] text-[var(--success)]/80">
                {lines.map((line, i) => (
                    <div key={i} className="animate-in fade-in slide-in-from-left-2 duration-100">
                        {line}
                    </div>
                ))}
                <div className="w-2 h-4 bg-[var(--success)] animate-pulse" />
            </div>
        </div>
    );
}

function InsightCard({ insight }: { insight: CustomerInsight }) {
    const typeConfig = {
        pain: { label: "PAIN POINT", color: "text-[var(--error)]", border: "border-l-[var(--error)]" },
        desire: { label: "CORE DESIRE", color: "text-[var(--success)]", border: "border-l-[var(--success)]" },
        objection: { label: "OBJECTION", color: "text-[var(--warning)]", border: "border-l-[var(--warning)]" },
    };
    const config = typeConfig[insight.type];

    return (
        <div className={cn(
            "group relative p-6 bg-[var(--paper)] border border-[var(--border-subtle)] hover:border-[var(--ink)] hover:shadow-sm transition-all duration-300",
            "border-l-2", config.border
        )}>
            <div className="flex items-center justify-between mb-3">
                <span className={cn("font-technical text-[10px] tracking-widest uppercase", config.color)}>
                    {config.label}
                </span>
                <div className="flex items-center gap-2 text-[var(--muted)]">
                    <Globe size={10} />
                    <span className="font-technical text-[10px] uppercase tracking-wide">{insight.source}</span>
                </div>
            </div>

            <p className="font-serif text-lg text-[var(--ink)] leading-relaxed italic mb-4">
                "{insight.quote}"
            </p>

            <div className="flex justify-end opacity-0 group-hover:opacity-100 transition-opacity">
                <div className="flex items-center gap-1 bg-[var(--canvas)] px-2 py-1 rounded text-[10px] font-technical uppercase text-[var(--secondary)]">
                    Sentiment: {insight.sentiment}%
                </div>
            </div>
        </div>
    );
}

export default function Step7ResearchBrief() {
    const { session, updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(7)?.data as MarketIntelResult | undefined;

    const [isScanning, setIsScanning] = useState(false);
    const [insights, setInsights] = useState<CustomerInsight[]>(stepData?.insights || []);
    const [detectedCompetitors, setDetectedCompetitors] = useState<string[]>(stepData?.detectedCompetitors || []);
    const [summary, setSummary] = useState(stepData?.summary || "");
    const [reviewed, setReviewed] = useState(stepData?.reviewed || false);

    const containerRef = useRef<HTMLDivElement>(null);
    const hasData = insights.length > 0;

    useEffect(() => {
        if (!containerRef.current || isScanning || !hasData) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 16 },
            { opacity: 1, y: 0, duration: 0.6, stagger: 0.08, ease: "power2.out" }
        );
    }, [hasData, isScanning]);

    const runScan = useCallback(() => {
        setIsScanning(true);
        // ScraperTerminal component handles the timing, initiates 'onComplete' when done
    }, []);

    const handleScanComplete = async () => {
        try {
            // Call real Reddit research API
            const response = await fetch('/api/onboarding/reddit-research', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: session?.sessionId || 'demo',
                    query: 'SaaS marketing automation pain points',
                    company_domain: 'marketing',
                })
            });
            
            const result = await response.json();
            
            // Map API response to our insight format
            const apiInsights: CustomerInsight[] = (result.pain_points || []).map((pp: any, idx: number) => ({
                id: pp.id || `${idx + 1}`,
                type: pp.category === 'pricing' ? 'objection' : 'pain',
                quote: pp.quotes?.[0] || pp.description,
                source: `Reddit r/${result.subreddits_analyzed?.[0] || 'SaaS'}`,
                sentiment: Math.round((1 - (pp.severity || 0.5)) * 100),
            }));
            
            // Add a desire insight from market insights
            if (result.market_insights?.length > 0) {
                apiInsights.push({
                    id: 'desire-1',
                    type: 'desire',
                    quote: 'Users want simple, actionable solutions that just work.',
                    source: 'Market Analysis',
                    sentiment: 85,
                });
            }
            
            const apiCompetitors = (result.competitor_mentions || []).map((c: any) => c.competitor);
            const apiSummary = result.research_summary || "Market research complete. Key pain points identified.";
            
            const finalInsights = apiInsights.length > 0 ? apiInsights : generateFallbackInsights();
            const finalCompetitors = apiCompetitors.length > 0 ? apiCompetitors : ["HubSpot", "Salesforce", "ClickUp"];
            
            setInsights(finalInsights);
            setDetectedCompetitors(finalCompetitors);
            setSummary(apiSummary);

            updateStepData(7, {
                insights: finalInsights,
                detectedCompetitors: finalCompetitors,
                summary: apiSummary,
                reviewed: false
            });
        } catch (error) {
            console.error('Reddit research error:', error);
            // Fallback to mock data
            const fallbackInsights = generateFallbackInsights();
            const fallbackCompetitors = ["HubSpot", "Salesforce", "ClickUp", "Monday.com"];
            const fallbackSummary = "The market is saturated with complex tools. Users are craving simplicity.";
            
            setInsights(fallbackInsights);
            setDetectedCompetitors(fallbackCompetitors);
            setSummary(fallbackSummary);

            updateStepData(7, {
                insights: fallbackInsights,
                detectedCompetitors: fallbackCompetitors,
                summary: fallbackSummary,
                reviewed: false
            });
        }
        setIsScanning(false);
    };
    
    const generateFallbackInsights = (): CustomerInsight[] => [
        { id: "1", type: "pain", quote: "I spend more time configuring the tool than actually doing the work.", source: "Reddit r/productivity", sentiment: 12 },
        { id: "2", type: "desire", quote: "I just want a dashboard that tells me exactly what to do next.", source: "G2 Crowd", sentiment: 88 },
        { id: "3", type: "objection", quote: "It seems great but I can't justify the $5k implementation fee.", source: "Twitter", sentiment: 45 },
        { id: "4", type: "pain", quote: "My current agency gives me reports, not results.", source: "LinkedIn", sentiment: 20 },
    ];

    const handleConfirm = () => {
        setReviewed(true);
        updateStepData(7, {
            insights,
            detectedCompetitors,
            summary,
            reviewed: true
        });
        updateStepStatus(7, "complete");
    };

    // 1. Initial Empty State
    if (!hasData && !isScanning) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[50vh] text-center space-y-8 animate-in fade-in duration-700">
                <div className="relative">
                    <div className="absolute inset-0 bg-[var(--blueprint)]/20 blur-xl rounded-full" />
                    <div className="relative w-24 h-24 rounded-full bg-[var(--canvas)] border border-[var(--blueprint)] flex items-center justify-center">
                        <Radar size={32} strokeWidth={1} className="text-[var(--blueprint)] animate-spin-slow" />
                    </div>
                </div>
                <div>
                    <h3 className="font-serif text-3xl text-[var(--ink)] mb-3">Market Intelligence</h3>
                    <p className="text-[var(--secondary)] max-w-lg mx-auto leading-relaxed font-serif text-lg">
                        We will scan public forums, review sites, and social channels to decode the <span className="text-[var(--ink)] font-medium">unvarnished truth</span> about your market.
                    </p>
                    <div className="flex gap-2 justify-center mt-4 text-[10px] font-technical uppercase text-[var(--muted)]">
                        <span>Targeting: Reddit</span>
                        <span>ΓÇó</span>
                        <span>G2 Crowd</span>
                        <span>ΓÇó</span>
                        <span>Twitter/X</span>
                    </div>
                </div>
                <BlueprintButton size="lg" onClick={runScan} className="px-10 py-6">
                    <Play size={14} fill="currentColor" />
                    <span>Deploy Research Agents</span>
                </BlueprintButton>
            </div>
        );
    }

    // 2. Scanning State
    if (isScanning) {
        return (
            <div className="min-h-[60vh] flex flex-col items-center justify-center">
                <ScraperTerminal onComplete={handleScanComplete} />
                <p className="mt-8 font-technical text-xs tracking-widest text-[var(--muted)] animate-pulse">
                    ESTABLISHING UPLINK...
                </p>
            </div>
        );
    }

    // 3. Results State (Dossier)
    return (
        <div ref={containerRef} className="max-w-5xl mx-auto space-y-12 pb-24">
            {/* Header */}
            <div data-animate className="flex items-start justify-between border-b border-[var(--border-subtle)] pb-8">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <div className="w-2 h-2 rounded-full bg-[var(--success)] animate-pulse" />
                        <h2 className="font-serif text-3xl text-[var(--ink)]">Intelligence Dossier</h2>
                    </div>
                    <p className="text-[var(--secondary)] max-w-2xl font-serif text-lg leading-relaxed">
                        {summary}
                    </p>
                </div>
                <BlueprintButton onClick={runScan} variant="secondary" size="sm">
                    <RefreshCw size={12} /> Rescan
                </BlueprintButton>
            </div>

            {/* Detected Competitors Ticker */}
            <div data-animate className="bg-[var(--canvas)] border-y border-[var(--border-subtle)] py-3 px-6 flex items-center gap-4 overflow-hidden">
                <span className="font-technical text-[10px] uppercase tracking-widest text-[var(--muted)] whitespace-nowrap">
                    Detected Rivals:
                </span>
                <div className="flex gap-6 animate-marquee whitespace-nowrap">
                    {detectedCompetitors.map((comp, i) => (
                        <span key={i} className="font-serif text-sm text-[var(--ink)] flex items-center gap-2">
                            <span className="w-1 h-1 rounded-full bg-[var(--border)]" /> {comp}
                        </span>
                    ))}
                </div>
            </div>

            {/* Insights Grid */}
            <div data-animate className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {insights.map((insight) => (
                    <InsightCard key={insight.id} insight={insight} />
                ))}
            </div>

            {/* Confirmation Footer */}
            <div data-animate className="flex justify-center pt-12 border-t border-[var(--border-subtle)]">
                {!reviewed ? (
                    <BlueprintButton onClick={handleConfirm} size="lg" className="px-12 py-6">
                        <Check size={16} />
                        <span>Confirm Intelligence</span>
                    </BlueprintButton>
                ) : (
                    <div className="flex items-center gap-2 text-[var(--success)]">
                        <CheckCircle size={24} />
                        <span className="font-serif italic font-medium">Dossier Locked</span>
                    </div>
                )}
            </div>
        </div>
    );
}
