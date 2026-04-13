"use client";

import * as React from "react";
import type { Route } from "next";
import { useState } from "react";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const DATE_RANGES = [
  { id: "7d", label: "Last 7 days" },
  { id: "30d", label: "Last 30 days" },
  { id: "90d", label: "Last 90 days" },
] as const;

interface MetricSeries {
  date: string;
  impressions: number;
  clicks: number;
  conversions: number;
  spend: number;
}

const generateSeries = (days: number): MetricSeries[] => {
  const series: MetricSeries[] = [];
  let baseImpressions = 12000;
  let baseClicks = 800;
  let baseConversions = 45;
  let baseSpend = 320;

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const noise = () => 0.85 + Math.random() * 0.3;
    baseImpressions = Math.max(1000, baseImpressions * noise());
    baseClicks = Math.max(50, baseClicks * noise());
    baseConversions = Math.max(5, baseConversions * noise());
    baseSpend = Math.max(50, baseSpend * noise());

    series.push({
      date: date.toLocaleDateString("en-US", { month: "short", day: "numeric" }),
      impressions: Math.round(baseImpressions),
      clicks: Math.round(baseClicks),
      conversions: Math.round(baseConversions),
      spend: Math.round(baseSpend * 100) / 100,
    });
  }
  return series;
};

function MetricCard({ label, value, delta, unit }: { label: string; value: string | number; delta?: number; unit?: string }) {
  const isPositive = delta && delta > 0;
  return (
    <Card>
      <CardContent className="p-4">
        <div className="space-y-1">
          <p className="text-xs uppercase tracking-[0.18em] text-[var(--muted-foreground)]">{label}</p>
          <p className="text-3xl font-bold">
            {typeof value === "number" ? value.toLocaleString() : value}
            {unit && <span className="ml-1 text-sm font-normal text-[var(--muted-foreground)]">{unit}</span>}
          </p>
          {delta !== undefined && (
            <p className={`text-xs font-medium ${isPositive ? "text-green-600" : "text-red-600"}`}>
              {isPositive ? "+" : ""}{delta.toFixed(1)}% vs prev period
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function SimpleBarChart({ data, height = 200 }: { data: { label: string; value: number; color?: string }[]; height?: number }) {
  const max = Math.max(...data.map((d) => d.value));
  return (
    <div className="flex items-end gap-2" style={{ height }}>
      {data.map((d, i) => (
        <div key={i} className="flex flex-1 flex-col items-center gap-1">
          <div
            className="w-full rounded-t-sm transition-all hover:opacity-80"
            style={{
              height: `${(d.value / max) * (height - 24)}px`,
              backgroundColor: d.color ?? "var(--primary)",
            }}
          />
          <span className="text-xs text-[var(--muted-foreground)]">{d.label}</span>
        </div>
      ))}
    </div>
  );
}

function SimpleLineChart({ data, height = 160 }: { data: { label: string; value: number; value2?: number }[]; height?: number }) {
  const max = Math.max(...data.flatMap((d) => [d.value, d.value2 ?? d.value]));
  const min = Math.min(...data.flatMap((d) => [d.value, d.value2 ?? d.value]));
  const range = max - min || 1;

  const toY = (v: number) => height - 16 - ((v - min) / range) * (height - 24);

  const path = data.map((d, i) => {
    const x = (i / (data.length - 1)) * 100;
    const y = toY(d.value);
    return `${i === 0 ? "M" : "L"} ${x}% ${y}px`;
  }).join(" ");

  const areaPath = path + ` L 100% ${height}px L 0% ${height}px Z`;

  return (
    <div className="relative overflow-hidden" style={{ height }}>
      <svg className="w-full" style={{ height }} preserveAspectRatio="none" viewBox={`0 0 100 ${height}`}>
        <defs>
          <linearGradient id="lineGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--primary)" stopOpacity="0.15" />
            <stop offset="100%" stopColor="var(--primary)" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path d={areaPath} fill="url(#lineGrad)" />
        <path d={path} fill="none" stroke="var(--primary)" strokeWidth="1.5" vectorEffect="non-scaling-stroke" />
      </svg>
      <div className="absolute inset-x-0 bottom-0 flex justify-between px-1">
        {data.filter((_, i) => i % Math.ceil(data.length / 6) === 0).map((d, i) => (
          <span key={i} className="text-xs text-[var(--muted-foreground)]">{d.label}</span>
        ))}
      </div>
    </div>
  );
}

export default function CampaignPerformancePage({
  params
}: {
  params: Promise<{ campaignId: string }>;
}): React.ReactElement {
  const resolvedParams = React.use(params);
  const { campaignId } = resolvedParams;

  const [range, setRange] = useState<typeof DATE_RANGES[number]>(DATE_RANGES[1]);

  const days = range.id === "7d" ? 7 : range.id === "30d" ? 30 : 90;
  const series = generateSeries(days);

  const totalImpressions = series.reduce((s, d) => s + d.impressions, 0);
  const totalClicks = series.reduce((s, d) => s + d.clicks, 0);
  const totalConversions = series.reduce((s, d) => s + d.conversions, 0);
  const totalSpend = series.reduce((s, d) => s + d.spend, 0);
  const avgCtr = (totalClicks / totalImpressions) * 100;
  const avgConvRate = (totalConversions / totalClicks) * 100;
  const cpc = totalSpend / totalClicks;
  const cpa = totalSpend / totalConversions;

  const impressionBarData = series.slice(-14).map((d) => ({ label: d.date, value: d.impressions }));
  const conversionBarData = series.slice(-14).map((d) => ({ label: d.date, value: d.conversions }));
  const trendData = series.slice(-14).map((d) => ({ label: d.date, value: d.clicks, value2: d.conversions * 10 }));

  const campaignRoute = `/campaigns/${campaignId}` as Route;

  return (
    <RouteShell
      eyebrow="Performance"
      title="Campaign Analytics"
      description={`Performance metrics for campaign ${campaignId} across the selected period.`}
      tags={["analytics", "metrics", "campaign"]}
      backHref={campaignRoute}
      backLabel="Back to Campaign"
    >
      <div className="flex items-center justify-between gap-4">
        <div className="flex gap-2">
          {DATE_RANGES.map((r) => (
            <Button
              key={r.id}
              size="sm"
              variant={range.id === r.id ? "default" : "secondary"}
              onClick={() => setRange(r)}
            >
              {r.label}
            </Button>
          ))}
        </div>
        <Button size="sm" variant="secondary">
          Export CSV
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Impressions" value={totalImpressions} delta={12.4} />
        <MetricCard label="Clicks" value={totalClicks} delta={8.1} />
        <MetricCard label="Conversions" value={totalConversions} delta={-2.3} />
        <MetricCard label="Spend" value={`$${totalSpend.toFixed(2)}`} delta={5.7} />
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="CTR" value={`${avgCtr.toFixed(2)}%`} delta={0.3} />
        <MetricCard label="Conv. Rate" value={`${avgConvRate.toFixed(2)}%`} delta={-0.8} />
        <MetricCard label="CPC" value={`$${cpc.toFixed(2)}`} delta={-4.2} />
        <MetricCard label="CPA" value={`$${cpa.toFixed(2)}`} delta={3.1} />
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Impressions — Last 14 days</CardTitle>
          </CardHeader>
          <CardContent>
            <SimpleBarChart data={impressionBarData} height={160} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Conversions — Last 14 days</CardTitle>
          </CardHeader>
          <CardContent>
            <SimpleBarChart data={conversionBarData} height={160} />
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">Clicks vs Conversions (×10) — Last 14 days</CardTitle>
            <div className="flex gap-4">
              <div className="flex items-center gap-2 text-xs">
                <div className="h-2 w-4 rounded-sm bg-[var(--primary)]" />
                Clicks
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className="h-2 w-4 rounded-sm bg-[var(--accent)]" />
                Conversions × 10
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <SimpleLineChart data={trendData} height={180} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Channel Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              { channel: "LinkedIn", impressions: Math.round(totalImpressions * 0.45), clicks: Math.round(totalClicks * 0.42), conversions: Math.round(totalConversions * 0.38), spend: totalSpend * 0.50 },
              { channel: "Content / SEO", impressions: Math.round(totalImpressions * 0.25), clicks: Math.round(totalClicks * 0.30), conversions: Math.round(totalConversions * 0.35), spend: totalSpend * 0.20 },
              { channel: "Email", impressions: Math.round(totalImpressions * 0.15), clicks: Math.round(totalClicks * 0.18), conversions: Math.round(totalConversions * 0.20), spend: totalSpend * 0.15 },
              { channel: "Paid Search", impressions: Math.round(totalImpressions * 0.15), clicks: Math.round(totalClicks * 0.10), conversions: Math.round(totalConversions * 0.07), spend: totalSpend * 0.15 },
            ].map((ch) => (
              <div key={ch.channel} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium">{ch.channel}</span>
                  <span className="text-[var(--muted-foreground)]">${ch.spend.toFixed(2)} spend</span>
                </div>
                <div className="flex h-2 overflow-hidden rounded-full bg-[var(--muted)]">
                  <div className="bg-[var(--primary)]" style={{ width: `${(ch.impressions / totalImpressions) * 100}%` }} />
                  <div className="bg-[var(--accent)]" style={{ width: `${(ch.clicks / totalClicks) * 100}%` }} />
                  <div className="bg-green-500" style={{ width: `${(ch.conversions / totalConversions) * 100}%` }} />
                </div>
                <div className="flex justify-between text-xs text-[var(--muted-foreground)]">
                  <span>{(ch.impressions / totalImpressions * 100).toFixed(0)}% impressions</span>
                  <span>{(ch.clicks / totalClicks * 100).toFixed(0)}% clicks</span>
                  <span>{(ch.conversions / totalConversions * 100).toFixed(0)}% conversions</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </RouteShell>
  );
}
