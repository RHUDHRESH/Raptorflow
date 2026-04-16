"use client";

import * as React from "react";
import type { Route } from "next";
import { useState } from "react";
import Link from "next/link";
import { ArrowLeftIcon, DownloadIcon, TriangleUpIcon, TriangleDownIcon } from "@radix-ui/react-icons";

const DATE_RANGES = [
  { id: "7d",  label: "7D"  },
  { id: "30d", label: "30D" },
  { id: "90d", label: "90D" },
] as const;

/* ─── Data generation ───────────────────────────────────────────── */
interface MetricSeries {
  date: string;
  impressions: number;
  clicks: number;
  conversions: number;
  spend: number;
}

const generateSeries = (days: number): MetricSeries[] => {
  const series: MetricSeries[] = [];
  let imp = 12000, clk = 800, conv = 45, spend = 320;
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    const n = () => 0.85 + Math.random() * 0.3;
    imp = Math.max(1000, imp * n()); clk = Math.max(50, clk * n());
    conv = Math.max(5, conv * n()); spend = Math.max(50, spend * n());
    series.push({
      date: d.toLocaleDateString("en-IN", { day: "numeric", month: "short" }),
      impressions: Math.round(imp), clicks: Math.round(clk),
      conversions: Math.round(conv), spend: Math.round(spend * 100) / 100,
    });
  }
  return series;
};

/* ─── KPI Card ──────────────────────────────────────────────────── */
function KpiCard({
  label, value, unit, delta,
}: {
  label: string; value: string | number; unit?: string; delta?: number;
}): React.ReactElement {
  const isPos = delta !== undefined && delta > 0;
  const Icon  = isPos ? TriangleUpIcon : TriangleDownIcon;

  return (
    <div
      className="border border-[var(--border)] p-5"
      style={{ background: "var(--card)" }}
    >
      <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 8, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.16em", color: "var(--muted-foreground)", marginBottom: 8 }}>
        {label}
      </p>
      <p style={{ fontFamily: "'DM Serif Display', serif", fontSize: 30, lineHeight: 1, color: "var(--foreground)", margin: 0 }}>
        {typeof value === "number" ? value.toLocaleString("en-IN") : value}
        {unit && <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 12, color: "var(--muted-foreground)", marginLeft: 4 }}>{unit}</span>}
      </p>
      {delta !== undefined && (
        <div className="flex items-center gap-1 mt-2">
          <Icon className="h-2.5 w-2.5" style={{ color: isPos ? "var(--leaf-confirm)" : "var(--signal-red)" }} />
          <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 8, fontWeight: 700, color: isPos ? "var(--leaf-confirm)" : "var(--signal-red)" }}>
            {isPos ? "+" : ""}{delta.toFixed(1)}% vs prev
          </span>
        </div>
      )}
    </div>
  );
}

/* ─── SVG Bar Chart ─────────────────────────────────────────────── */
function BarChart({
  data,
  color = "var(--foreground)",
  height = 120,
}: {
  data: { label: string; value: number }[];
  color?: string;
  height?: number;
}): React.ReactElement {
  const max = Math.max(...data.map((d) => d.value)) || 1;
  const show = data.filter((_, i) => i % Math.ceil(data.length / 7) === 0);

  return (
    <div>
      <svg
        width="100%"
        style={{ height, display: "block" }}
        viewBox={`0 0 ${data.length * 16} ${height}`}
        preserveAspectRatio="none"
      >
        {data.map((d, i) => {
          const barH = Math.max(2, (d.value / max) * (height - 8));
          return (
            <rect
              key={i}
              x={i * 16 + 2}
              y={height - barH}
              width={12}
              height={barH}
              fill={color}
              opacity={0.8}
            >
              <title>{d.label}: {d.value.toLocaleString("en-IN")}</title>
            </rect>
          );
        })}
      </svg>
      <div className="flex justify-between mt-1">
        {show.map((d, i) => (
          <span key={i} style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 7, color: "var(--muted-foreground)" }}>
            {d.label}
          </span>
        ))}
      </div>
    </div>
  );
}

/* ─── SVG Line Sparkline ────────────────────────────────────────── */
function SparkLine({
  data,
  color = "var(--amber-war)",
  height = 80,
}: {
  data: number[];
  color?: string;
  height?: number;
}): React.ReactElement {
  if (data.length < 2) return <div style={{ height }} />;
  const max = Math.max(...data) || 1;
  const min = Math.min(...data);
  const range = max - min || 1;
  const W = 300;
  const pts = data.map((v, i) => {
    const x = (i / (data.length - 1)) * W;
    const y = height - 4 - ((v - min) / range) * (height - 8);
    return `${x},${y}`;
  }).join(" ");
  const area = `0,${height} ` + pts + ` ${W},${height}`;

  return (
    <svg width="100%" viewBox={`0 0 ${W} ${height}`} preserveAspectRatio="none" style={{ height, display: "block" }}>
      <defs>
        <linearGradient id={`sg-${color.replace(/[^a-z]/g, "")}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.15" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <polygon points={area} fill={`url(#sg-${color.replace(/[^a-z]/g, "")})`} />
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.5" vectorEffect="non-scaling-stroke" />
    </svg>
  );
}

/* ─── Channel Row ────────────────────────────────────────────────── */
function ChannelRow({
  channel, pct, spend, clicks,
}: {
  channel: string; pct: number; spend: number; clicks: number;
}): React.ReactElement {
  return (
    <div className="flex items-center gap-5 py-3 border-b border-[var(--border)] last:border-0">
      <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, fontWeight: 500, color: "var(--foreground)", width: 130, flexShrink: 0 }}>
        {channel}
      </span>
      <div className="flex-1" style={{ height: 4, background: "var(--muted)" }}>
        <div style={{ height: "100%", width: `${pct}%`, background: "var(--amber-war)", transition: "width 0.6s" }} />
      </div>
      <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, color: "var(--muted-foreground)", width: 70, textAlign: "right" }}>
        ₹{spend.toLocaleString("en-IN")}
      </span>
      <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, color: "var(--muted-foreground)", width: 60, textAlign: "right" }}>
        {clicks.toLocaleString("en-IN")} clk
      </span>
    </div>
  );
}

/* ─── Main Performance Page ─────────────────────────────────────── */
export default function CampaignPerformancePage({
  params,
}: {
  params: Promise<{ campaignId: string }>;
}): React.ReactElement {
  const { campaignId } = React.use(params);
  const [range, setRange] = useState<typeof DATE_RANGES[number]>(DATE_RANGES[1]);

  const days   = range.id === "7d" ? 7 : range.id === "30d" ? 30 : 90;
  const series = generateSeries(days);

  const totImp  = series.reduce((s, d) => s + d.impressions, 0);
  const totClk  = series.reduce((s, d) => s + d.clicks, 0);
  const totConv = series.reduce((s, d) => s + d.conversions, 0);
  const totSpend= series.reduce((s, d) => s + d.spend, 0);
  const ctr     = (totClk / totImp) * 100;
  const cnvRate = (totConv / totClk) * 100;
  const cpc     = totSpend / totClk;
  const cpa     = totSpend / totConv;

  const CHANNELS = [
    { channel: "Instagram Reels", pct: 45, spend: Math.round(totSpend * 0.45), clicks: Math.round(totClk * 0.42) },
    { channel: "Search / SEO",    pct: 28, spend: Math.round(totSpend * 0.20), clicks: Math.round(totClk * 0.30) },
    { channel: "Email Nurture",   pct: 16, spend: Math.round(totSpend * 0.15), clicks: Math.round(totClk * 0.18) },
    { channel: "Paid Search",     pct: 11, spend: Math.round(totSpend * 0.20), clicks: Math.round(totClk * 0.10) },
  ];

  return (
    <div className="flex flex-col gap-8 py-2">

      {/* ── Back ─────────────────────────────────────────── */}
      <Link
        href={`/campaigns/${campaignId}` as Route}
        className="flex w-fit items-center gap-2 hover:underline"
        style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, textTransform: "uppercase", letterSpacing: "0.16em", color: "var(--muted-foreground)" }}
      >
        <ArrowLeftIcon className="h-3 w-3" />
        Campaign Hub
      </Link>

      {/* ── Header ───────────────────────────────────────── */}
      <header className="flex items-end justify-between border-b-2 border-[var(--foreground)] pb-6">
        <div>
          <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.2em", color: "var(--muted-foreground)", marginBottom: 8 }}>
            Performance Analytics
          </p>
          <h1 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 40, lineHeight: 1, margin: 0 }}>
            Campaign Metrics
          </h1>
        </div>

        <div className="flex items-center gap-3">
          {/* Range picker */}
          <div className="flex gap-0">
            {DATE_RANGES.map((r) => (
              <button
                key={r.id}
                onClick={() => setRange(r)}
                className="px-4 py-2 border border-[var(--border)] transition-all"
                style={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: 9,
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.12em",
                  background: range.id === r.id ? "var(--foreground)" : "transparent",
                  color: range.id === r.id ? "var(--background)" : "var(--muted-foreground)",
                  borderLeft: r.id === "7d" ? "1px solid var(--border)" : "none",
                }}
              >
                {r.label}
              </button>
            ))}
          </div>
          <button
            className="flex h-10 items-center gap-2 px-4 border border-[var(--border)] hover:border-[var(--foreground)] transition-all"
            style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.12em", color: "var(--muted-foreground)" }}
          >
            <DownloadIcon className="h-3 w-3" />
            Export
          </button>
        </div>
      </header>

      {/* ── Primary KPIs ─────────────────────────────────── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-0 border border-[var(--border)] divide-x divide-[var(--border)]">
        <KpiCard label="Impressions"  value={totImp}                  delta={12.4} />
        <KpiCard label="Clicks"       value={totClk}                  delta={8.1} />
        <KpiCard label="Conversions"  value={totConv}                 delta={-2.3} />
        <KpiCard label="Spend"        value={`₹${Math.round(totSpend).toLocaleString("en-IN")}`} delta={5.7} />
      </div>

      {/* ── Efficiency KPIs ──────────────────────────────── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-0 border border-[var(--border)] border-t-0 divide-x divide-[var(--border)]">
        <KpiCard label="CTR"          value={`${ctr.toFixed(2)}%`}           delta={0.3} />
        <KpiCard label="Conv. Rate"   value={`${cnvRate.toFixed(2)}%`}       delta={-0.8} />
        <KpiCard label="CPC"          value={`₹${cpc.toFixed(2)}`}           delta={-4.2} />
        <KpiCard label="CPA"          value={`₹${cpa.toFixed(2)}`}           delta={3.1} />
      </div>

      {/* ── Charts ──────────────────────────────────────── */}
      <div className="grid xl:grid-cols-2 gap-5">

        {/* Impressions bar */}
        <div className="border border-[var(--border)] p-5" style={{ background: "var(--card)" }}>
          <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.16em", color: "var(--muted-foreground)", marginBottom: 16 }}>
            Impressions — {range.label}
          </p>
          <BarChart data={series.slice(-14).map((d) => ({ label: d.date, value: d.impressions }))} color="var(--foreground)" />
        </div>

        {/* Conversions bar */}
        <div className="border border-[var(--border)] p-5" style={{ background: "var(--card)" }}>
          <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.16em", color: "var(--muted-foreground)", marginBottom: 16 }}>
            Conversions — {range.label}
          </p>
          <BarChart data={series.slice(-14).map((d) => ({ label: d.date, value: d.conversions }))} color="var(--leaf-confirm)" />
        </div>
      </div>

      {/* Clicks sparkline */}
      <div className="border border-[var(--border)] p-5" style={{ background: "var(--card)" }}>
        <div className="flex items-center justify-between mb-4">
          <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.16em", color: "var(--muted-foreground)" }}>
            Click Trend — {range.label}
          </p>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5">
              <div className="h-0.5 w-6" style={{ background: "var(--amber-war)" }} />
              <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 8, color: "var(--muted-foreground)" }}>Clicks</span>
            </div>
          </div>
        </div>
        <SparkLine data={series.map((d) => d.clicks)} color="var(--amber-war)" height={100} />
      </div>

      {/* Channel breakdown */}
      <div className="border border-[var(--border)]" style={{ background: "var(--card)" }}>
        <div className="px-5 py-4 border-b border-[var(--border)]">
          <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.16em", color: "var(--muted-foreground)" }}>
            Channel Breakdown
          </p>
        </div>
        <div className="px-5">
          {CHANNELS.map((ch) => (
            <ChannelRow key={ch.channel} {...ch} />
          ))}
        </div>
      </div>

    </div>
  );
}
