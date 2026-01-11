"use client";

import { useRef, useEffect, useState } from "react";
import gsap from "gsap";
import {
    TrendingUp,
    Activity,
    Users,
    Globe,
    ArrowRight,
    ChevronDown,
    Download,
    Calendar,
    MousePointer2,
    Eye,
    CreditCard,
    Target
} from "lucide-react";

import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintKPI, KPIGrid } from "@/components/ui/BlueprintKPI";
import { BlueprintChart } from "@/components/ui/BlueprintChart";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintTabs } from "@/components/ui/BlueprintTabs";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Matrix (Analytics)
   High-density performance reporting
   ══════════════════════════════════════════════════════════════════════════════ */

const TABS = [
    { id: "overview", label: "Overview", code: "VIEW-01" },
    { id: "campaigns", label: "Campaigns", code: "VIEW-02" },
    { id: "engagement", label: "Engagement", code: "VIEW-03" },
];

const TRAFFIC_DATA = [
    { label: "01", value: 240 }, { label: "02", value: 300 }, { label: "03", value: 280 },
    { label: "04", value: 450 }, { label: "05", value: 410 }, { label: "06", value: 580 },
    { label: "07", value: 520 }, { label: "08", value: 650 }, { label: "09", value: 610 },
    { label: "10", value: 750 },
];

const SOURCE_DATA = [
    { label: "Direct", value: 45 },
    { label: "Social", value: 32 },
    { label: "Organic", value: 15 },
    { label: "Referral", value: 8 },
];

function MatrixPageContent() {
    const pageRef = useRef<HTMLDivElement>(null);
    const [activeTab, setActiveTab] = useState("overview");

    useEffect(() => {
        if (!pageRef.current) return;
        const header = pageRef.current.querySelector("[data-header]");
        if (header) gsap.fromTo(header, { opacity: 0, y: -12 }, { opacity: 1, y: 0, duration: 0.5 });
    }, []);

    return (
        <div ref={pageRef} className="relative max-w-7xl mx-auto pb-12">
            {/* Backgrounds */}
            <div className="fixed inset-0 pointer-events-none z-0" style={{ backgroundImage: "url('/textures/paper-grain.png')", opacity: 0.04, mixBlendMode: "multiply" }} />
            <div className="fixed inset-0 blueprint-grid pointer-events-none z-0 opacity-30" />

            <div className="relative z-10 space-y-8">
                {/* DOM HEADER */}
                <div data-header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4" style={{ opacity: 0 }}>
                    <div className="space-y-1">
                        <div className="flex items-center gap-4">
                            <span className="font-technical text-[var(--blueprint)]">FIG. MX</span>
                            <div className="h-px w-8 bg-[var(--blueprint-line)]" />
                            <span className="font-technical text-[var(--muted)]">SYSTEM MATRIX</span>
                        </div>
                        <h1 className="font-serif text-4xl text-[var(--ink)]">Performance Matrix</h1>
                    </div>
                    <div className="flex items-center gap-3">
                        <SecondaryButton>
                            <Calendar size={14} /> Last 30 Days <ChevronDown size={12} />
                        </SecondaryButton>
                        <BlueprintButton label="EXP">
                            <Download size={14} /> Export Report
                        </BlueprintButton>
                    </div>
                </div>

                {/* TABS */}
                <BlueprintTabs tabs={TABS} activeTab={activeTab} onChange={setActiveTab} />

                {/* PRIMARY KPIS */}
                <KPIGrid columns={4}>
                    <BlueprintKPI label="Total Revenue" value="$42,850" code="REV" trend="up" trendValue="+12.5%" />
                    <BlueprintKPI label="Active Users" value="1,240" code="USR" trend="up" trendValue="+5.2%" />
                    <BlueprintKPI label="Conversion Rate" value="3.8%" code="CVR" trend="down" trendValue="-0.4%" />
                    <BlueprintKPI label="Avg Session" value="4m 12s" code="DUR" trend="up" trendValue="+12s" unit="Time" />
                </KPIGrid>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* MAIN CHART */}
                    <div className="lg:col-span-2">
                        <BlueprintChart
                            data={TRAFFIC_DATA}
                            title="Traffic Velocity"
                            figure="FIG. 01"
                            height={300}
                            className="h-full"
                        />
                    </div>

                    {/* SIDEBAR METRICS */}
                    <div className="space-y-6">
                        {/* Acquisition Sources */}
                        <BlueprintCard title="Acquisition Sources" code="SRC" padding="md" showCorners>
                            <div className="space-y-4">
                                {SOURCE_DATA.map((item, i) => (
                                    <div key={i} className="flex items-center justify-between">
                                        <div className="flex items-center gap-3">
                                            <span className="font-technical text-[var(--muted)]">{String(i + 1).padStart(2, '0')}</span>
                                            <span className="text-sm text-[var(--ink)]">{item.label}</span>
                                        </div>
                                        <span className="font-mono text-xs text-[var(--ink-secondary)]">{item.value}%</span>
                                    </div>
                                ))}
                            </div>
                        </BlueprintCard>

                        {/* System Health */}
                        <BlueprintCard title="System Health" code="SYS" padding="md" showCorners>
                            <div className="space-y-4">
                                <div className="flex justify-between items-center">
                                    <span className="text-xs text-[var(--muted)]">API Latency</span>
                                    <BlueprintBadge variant="success" dot>45ms</BlueprintBadge>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-xs text-[var(--muted)]">Job Queue</span>
                                    <BlueprintBadge variant="blueprint" dot>Idle</BlueprintBadge>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-xs text-[var(--muted)]">Error Rate</span>
                                    <BlueprintBadge variant="default" dot>0.01%</BlueprintBadge>
                                </div>
                            </div>
                        </BlueprintCard>
                    </div>
                </div>

                {/* DETAILED TABLES */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <BlueprintCard title="Top Performing Campaigns" code="TOP-CMP" showCorners padding="none">
                        <div className="divide-y divide-[var(--border-subtle)]">
                            {[
                                { name: "Q4 Outreach", roi: "4.2x", status: "active" },
                                { name: "Founder Brand", roi: "3.8x", status: "active" },
                                { name: "Webinar Series", roi: "2.1x", status: "paused" }
                            ].map((c, i) => (
                                <div key={i} className="flex items-center justify-between px-5 py-3 hover:bg-[var(--canvas)] transition-colors">
                                    <span className="text-sm font-medium text-[var(--ink)]">{c.name}</span>
                                    <div className="flex items-center gap-3">
                                        <span className="font-mono text-xs text-[var(--success)]">{c.roi} ROI</span>
                                        <BlueprintBadge variant={c.status === 'active' ? 'success' : 'default'} size="sm" dot>{c.status.toUpperCase()}</BlueprintBadge>
                                    </div>
                                </div>
                            ))}
                        </div>
                        <div className="p-3 border-t border-[var(--border-subtle)] text-center">
                            <button className="text-xs font-technical text-[var(--muted)] hover:text-[var(--blueprint)] transition-colors">VIEW ALL CAMPAIGNS</button>
                        </div>
                    </BlueprintCard>

                    <BlueprintCard title="Recent Conversions" code="REC-CVR" showCorners padding="none">
                        <div className="divide-y divide-[var(--border-subtle)]">
                            {[
                                { user: "acme_corp_ceo", action: "Plan Upgrade", time: "2m ago" },
                                { user: "startup_founder_x", action: "Trial Sign-up", time: "15m ago" },
                                { user: "growth_lead_y", action: "Demo Request", time: "1h ago" }
                            ].map((c, i) => (
                                <div key={i} className="flex items-center justify-between px-5 py-3 hover:bg-[var(--canvas)] transition-colors">
                                    <div className="flex items-center gap-3">
                                        <div className="w-6 h-6 rounded-full bg-[var(--surface)] border border-[var(--border)] flex items-center justify-center">
                                            <Users size={12} className="text-[var(--muted)]" />
                                        </div>
                                        <span className="text-sm text-[var(--ink)]">{c.user}</span>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <span className="text-xs text-[var(--ink-secondary)]">{c.action}</span>
                                        <span className="font-mono text-[10px] text-[var(--muted)]">{c.time}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                        <div className="p-3 border-t border-[var(--border-subtle)] text-center">
                            <button className="text-xs font-technical text-[var(--muted)] hover:text-[var(--blueprint)] transition-colors">VIEW ACTIVITY LOG</button>
                        </div>
                    </BlueprintCard>
                </div>

                <div className="flex justify-center pt-8">
                    <span className="font-technical text-[var(--muted)]">DOCUMENT: MATRIX-RPTR | REVISION: {new Date().toISOString().split('T')[0]}</span>
                </div>
            </div>
        </div>
    );
}

export default function MatrixPage() {
    return <MatrixPageContent />;
}
