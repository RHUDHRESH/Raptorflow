"use client";

/*
 * Twenty-one screen scaffold
 * Reserved route content, form contract, websocket hooks, and autosave behavior.
 */

import type * as React from "react";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, Zap, CheckCircle2, AlertCircle, ArrowRight, Sparkles } from "lucide-react";
import { Route } from "next";
import Link from "next/link";
import { ChevronRightIcon, MixIcon } from "@radix-ui/react-icons";
import { useFoundation, useFoundationScan } from "@/features/foundation/hooks/useFoundation";
import { foundationApi } from "@/lib/api";
import { FOUNDATION_STEPS } from "@/lib/foundation";
import { GsapBridge } from "@/components/ui/gsap-bridge";
import type { QuickScanResult } from "@/lib/api";

const screens = [
  { slug: "url", title: "URL" },
  { slug: "identity-confirmation", title: "Identity Confirmation" },
  { slug: "business-stage-and-team", title: "Business Stage and Team" },
  { slug: "what-you-actually-sell", title: "What You Actually Sell" },
  { slug: "the-problem-you-solve", title: "The Problem You Solve" },
  { slug: "primary-icp", title: "Primary ICP" },
  { slug: "secondary-icps", title: "Secondary ICPs" },
  { slug: "competitive-landscape", title: "Competitive Landscape" },
  { slug: "competitive-differentiation", title: "Competitive Differentiation" },
  { slug: "positioning-statement", title: "Positioning Statement" },
  { slug: "brand-personality", title: "Brand Personality" },
  { slug: "voice-in-practice", title: "Voice in Practice" },
  { slug: "content-territories", title: "Content Territories" },
  { slug: "marketing-channels", title: "Marketing Channels" },
  { slug: "goals-and-kpis", title: "Goals and KPIs" },
  { slug: "keywords-and-seo", title: "Keywords and SEO" },
  { slug: "existing-assets", title: "Existing Assets" },
  { slug: "current-frustrations", title: "Current Frustrations" },
  { slug: "existing-tools", title: "Existing Tools" },
  { slug: "reference-brands", title: "Reference Brands" },
  { slug: "campaign-strategist", title: "Campaign Strategist" },
];

function relativeTime(isoString: string): string {
  const diff = Date.now() - new Date(isoString).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

function ScoreCircle({ score }: { score: number }) {
  const pct = Math.round((score / 10) * 100);
  const color = score >= 7 ? "#16a34a" : score >= 4 ? "#d97706" : "#dc2626";
  const bg = score >= 7 ? "#dcfce7" : score >= 4 ? "#fef9c3" : "#fee2e2";

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg className="w-16 h-16 -rotate-90" viewBox="0 0 36 36">
        <circle cx="18" cy="18" r="15.9" fill="none" stroke="#e5e7eb" strokeWidth="3" />
        <circle
          cx="18"
          cy="18"
          r="15.9"
          fill="none"
          stroke={color}
          strokeWidth="3"
          strokeDasharray={`${pct} 100`}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-lg font-mono font-bold leading-none" style={{ color }}>
          {score}
        </span>
        <span className="text-[8px] font-mono text-[var(--muted-foreground)]">/10</span>
      </div>
    </div>
  );
}

function ScanResultCard({ scan, lastScannedAt }: { scan: QuickScanResult; lastScannedAt: string }) {
  return (
    <div className="border border-[var(--border)] bg-[var(--card)] divide-y divide-[var(--border)]">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-3">
          <Sparkles className="w-4 h-4 text-[var(--primary)]" />
          <span className="text-xs font-mono uppercase tracking-widest text-[var(--muted-foreground)]">
            Foundation Scan
          </span>
        </div>
        <div className="flex items-center gap-4">
          <ScoreCircle score={scan.positioning_score} />
        </div>
      </div>

      {/* Summary */}
      <div className="px-6 py-4 bg-[var(--primary)]/5">
        <p className="text-sm text-[var(--foreground)] leading-relaxed italic">{scan.summary}</p>
        <p className="mt-2 text-[10px] font-mono text-[var(--muted-foreground)] uppercase tracking-widest">
          Last scanned {relativeTime(lastScannedAt)}
        </p>
      </div>

      {/* Strengths + Gaps */}
      <div className="grid grid-cols-1 sm:grid-cols-2 divide-y sm:divide-y-0 sm:divide-x divide-[var(--border)]">
        <div className="px-6 py-4">
          <h4 className="text-xs font-mono uppercase tracking-widest text-green-700 mb-3 flex items-center gap-1.5">
            <CheckCircle2 className="w-3 h-3" /> Strengths
          </h4>
          <ul className="space-y-2">
            {scan.strengths.map((s, i) => (
              <li key={i} className="text-xs text-[var(--foreground)] flex gap-2">
                <span className="text-green-600 shrink-0 mt-0.5">✓</span>
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="px-6 py-4">
          <h4 className="text-xs font-mono uppercase tracking-widest text-amber-700 mb-3 flex items-center gap-1.5">
            <AlertCircle className="w-3 h-3" /> Gaps
          </h4>
          <ul className="space-y-2">
            {scan.gaps.map((g, i) => (
              <li key={i} className="text-xs text-[var(--foreground)] flex gap-2">
                <span className="text-amber-600 shrink-0 mt-0.5">!</span>
                <span>{g}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Recommendations */}
      <div className="px-6 py-4 space-y-2">
        <h4 className="text-xs font-mono uppercase tracking-widest text-[var(--muted-foreground)] mb-3">
          Recommendations
        </h4>
        <div className="space-y-2">
          {scan.recommendations.map((r, i) => (
            <div
              key={i}
              className="flex items-center justify-between border border-[var(--border)] p-3 hover:border-[var(--primary)] transition-colors cursor-pointer group"
            >
              <div className="flex items-start gap-3">
                <span className="text-xs font-mono font-bold text-[var(--primary)] shrink-0 mt-0.5">
                  {i + 1}.
                </span>
                <span className="text-xs text-[var(--foreground)]">{r}</span>
              </div>
              <ArrowRight className="w-3 h-3 text-[var(--muted-foreground)] group-hover:text-[var(--primary)] transition-colors shrink-0 mt-0.5" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function EmptyScanState({ onScan }: { onScan: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-6 text-center border border-dashed border-[var(--border)]">
      <Sparkles className="w-10 h-10 text-[var(--primary)] mb-4" />
      <h2 className="font-[family-name:var(--font-display)] text-2xl mb-2">
        Your Foundation hasn&apos;t been scanned yet
      </h2>
      <p className="text-sm text-[var(--muted-foreground)] max-w-sm mb-8 leading-relaxed">
        Run a quick scan to get your strategic analysis — strengths, gaps, and actionable
        recommendations from Mistral Large.
      </p>
      <button
        onClick={onScan}
        className="flex items-center gap-2 px-6 py-3 bg-[var(--primary)] text-[var(--primary-foreground)] hover:opacity-90 rounded text-xs font-mono uppercase tracking-widest transition-opacity"
      >
        <Zap className="w-4 h-4" />
        Run Quick Scan
      </button>
    </div>
  );
}

export default function FoundationIndexPage(): React.ReactElement {
  const router = useRouter();
  const { data: foundation, isLoading } = useFoundation();
  const [checking, setChecking] = useState(true);
  const [scanResult, setScanResult] = useState<QuickScanResult | null>(null);
  const [scanError, setScanError] = useState<string | null>(null);
  const [lastScannedAt, setLastScannedAt] = useState<string | null>(null);

  const quickScan = useFoundationScan();

  useEffect(() => {
    async function checkStatus() {
      try {
        const data = await foundationApi.getFullStatus();
        if (data.status !== "complete") {
          const nextStep = data.missing_sections[0] || "url";
          router.replace(`/foundation/${nextStep}` as Route);
        } else {
          setChecking(false);
        }
      } catch (err) {
        console.error("Status check failed", err);
        setChecking(false);
      }
    }
    checkStatus();
  }, [router]);

  const handleRunScan = async () => {
    setScanError(null);
    try {
      const result = await quickScan.mutateAsync();
      setScanResult(result.scan);
      setLastScannedAt(result.scannedAt);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Scan failed";
      setScanError(msg);
    }
  };

  if (checking || isLoading) {
    return (
      <div className="flex h-[80vh] w-full items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 text-[#D97757] animate-spin" />
          <p className="text-[#6B655E] text-[10px] font-bold tracking-[0.2em] uppercase font-mono">
            Uplink: Synchronizing Foundation Nodes...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-10 py-6">
      <GsapBridge stagger={true}>
        {/* Header */}
        <header className="gsap-reveal flex items-end justify-between border-b-2 border-[var(--foreground)] pb-8">
          <div className="space-y-2">
            <p
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 9,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.2em",
                color: "var(--muted-foreground)",
              }}
            >
              System Asset
            </p>
            <h1
              style={{
                fontFamily: "'DM Serif Display', serif",
                fontSize: 48,
                lineHeight: 1,
                margin: 0,
              }}
            >
              The Foundation
            </h1>
          </div>
          <div className="flex flex-col items-end gap-3">
            <button
              onClick={handleRunScan}
              disabled={quickScan.isPending}
              className="flex items-center gap-2 px-4 py-2 bg-[var(--primary)] text-[var(--primary-foreground)] hover:opacity-90 disabled:opacity-50 rounded text-xs font-mono uppercase tracking-widest transition-opacity"
            >
              {quickScan.isPending ? (
                <>
                  <Loader2 className="w-3 h-3 animate-spin" /> Scanning...
                </>
              ) : (
                <>
                  <Zap className="w-3 h-3" /> Run Quick Scan
                </>
              )}
            </button>
          </div>
        </header>

        {/* Scan Result / Empty State */}
        <div className="gsap-reveal">
          {scanError ? (
            <div className="border border-red-300 bg-red-50 p-4 text-xs text-red-700 font-mono">
              Scan error: {scanError}
            </div>
          ) : scanResult && lastScannedAt ? (
            <ScanResultCard scan={scanResult} lastScannedAt={lastScannedAt} />
          ) : (
            <EmptyScanState onScan={handleRunScan} />
          )}
        </div>

        {/* The Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-[1px] bg-[#E5DED4] border border-[#E5DED4]">
          {FOUNDATION_STEPS.map((step, i) => {
            const val = (foundation?.sections?.[step.section] as string) || "";
            const isFilled = val.length > 0;

            return (
              <Link
                key={step.id}
                href={`/foundation/${step.id}` as Route}
                className="gsap-reveal bg-[var(--background)] p-6 hover:bg-[#F5F0E8] transition-colors group relative flex flex-col justify-between min-h-[200px]"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <span className="font-mono text-[9px] text-[#9A948C] font-bold tracking-widest uppercase">
                      Node_{String(i + 1).padStart(2, "0")}
                    </span>
                    {isFilled ? (
                      <div className="h-1.5 w-1.5 rounded-full bg-[#D97757]" />
                    ) : (
                      <div className="h-1.5 w-1.5 rounded-full bg-[#E5DED4]" />
                    )}
                  </div>
                  <h3 className="font-bold text-sm text-[#2A2622] mb-2 group-hover:text-[#D97757] transition-colors">
                    {step.title}
                  </h3>
                  <p className="text-[11px] text-[#6B655E] line-clamp-3 font-light leading-relaxed">
                    {val || "No context provided. System default applied."}
                  </p>
                </div>

                <div className="pt-4 flex items-center justify-between opacity-0 group-hover:opacity-100 transition-opacity">
                  <span className="text-[8px] font-mono uppercase tracking-[0.2em] text-[#D97757] font-bold">
                    Edit Node
                  </span>
                  <ChevronRightIcon className="w-4 h-4 text-[#D97757]" />
                </div>
              </Link>
            );
          })}

          {/* Reset / Re-map Card */}
          <div className="gsap-reveal bg-[#F5F0E8]/50 p-6 flex flex-col justify-center items-center gap-4 text-center border-dashed border-2 border-[#E5DED4] m-2">
            <MixIcon className="w-8 h-8 text-[#9A948C]" />
            <p className="text-[9px] font-mono text-[#9A948C] uppercase tracking-widest">
              Destructive Action
            </p>
            <button className="text-[10px] font-bold uppercase tracking-widest text-red-500/50 hover:text-red-500 transition-colors">
              Re-map Foundation
            </button>
          </div>
        </div>
      </GsapBridge>
    </div>
  );
}
