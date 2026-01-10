"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import { Check, Download, FileText, Image, Code, Presentation, Mail, Copy, Sparkles, ArrowRight } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintKPI, KPIGrid } from "@/components/ui/BlueprintKPI";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 25: Export
   Download all foundation assets
   ══════════════════════════════════════════════════════════════════════════════ */

interface ExportItem {
    id: string;
    icon: React.ElementType;
    name: string;
    description: string;
    format: string;
    ready: boolean;
    code: string;
}

const EXPORT_ITEMS: ExportItem[] = [
    { id: "1", icon: FileText, name: "Brand Kit PDF", description: "Complete positioning, messaging, and brand guidelines", format: "PDF", ready: true, code: "EXP-01" },
    { id: "2", icon: Presentation, name: "Pitch Deck Template", description: "Positioning-aligned presentation template", format: "PPTX", ready: true, code: "EXP-02" },
    { id: "3", icon: Image, name: "Social Media Templates", description: "LinkedIn, Twitter headers and post templates", format: "PNG/Figma", ready: true, code: "EXP-03" },
    { id: "4", icon: Mail, name: "Email Templates", description: "Cold outreach and nurture sequences", format: "TXT/HTML", ready: true, code: "EXP-04" },
    { id: "5", icon: Code, name: "Website Copy", description: "Homepage, about, and feature page copy", format: "TXT/MD", ready: true, code: "EXP-05" },
    { id: "6", icon: FileText, name: "Truth Sheet", description: "Locked and validated facts about your business", format: "JSON/PDF", ready: true, code: "EXP-06" },
];

export default function Step25Export() {
    const { updateStepStatus, getProgress } = useOnboardingStore();
    const [downloaded, setDownloaded] = useState<string[]>([]);
    const [allExported, setAllExported] = useState(false);
    const progress = getProgress();
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(containerRef.current.querySelectorAll("[data-animate]"), { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.4, stagger: 0.08, ease: "power2.out" });
    }, []);

    const handleDownload = (id: string) => { if (!downloaded.includes(id)) setDownloaded([...downloaded, id]); console.log(`Downloading ${id}`); };
    const handleExportAll = () => { setDownloaded(EXPORT_ITEMS.map((i) => i.id)); setAllExported(true); updateStepStatus(25, "complete"); };
    const handleCopyToClipboard = () => { navigator.clipboard.writeText(`RaptorFlow Foundation Export\n\nPositioning: Marketing. Finally under control.\nICP: B2B SaaS founders, 10-50 employees\nTagline: Stop guessing. Start executing.`); };

    return (
        <div ref={containerRef} className="space-y-6">
            {/* Hero */}
            <BlueprintCard data-animate showCorners variant="elevated" padding="lg" className="text-center border-[var(--blueprint)] bg-[var(--blueprint)]">
                <div className="w-14 h-14 rounded-[var(--radius-md)] bg-[var(--paper)]/20 flex items-center justify-center mx-auto mb-4">
                    <Sparkles size={28} className="text-[var(--paper)]" />
                </div>
                <h2 className="font-serif text-2xl text-[var(--paper)] mb-2">Congratulations!</h2>
                <p className="text-[var(--paper)]/80">Your marketing foundation is complete. Export your assets below.</p>
            </BlueprintCard>

            {/* Stats */}
            <KPIGrid data-animate columns={3}>
                <BlueprintKPI label="Steps Completed" value={String(progress.completed)} code="S-01" />
                <BlueprintKPI label="Assets Ready" value={String(EXPORT_ITEMS.length)} code="S-02" />
                <BlueprintKPI label="Downloaded" value={String(downloaded.length)} code="S-03" />
            </KPIGrid>

            {/* Export Items */}
            <div>
                <div className="flex items-center gap-3 mb-4">
                    <span className="font-technical text-[var(--blueprint)]">FIG. 01</span>
                    <div className="h-px flex-1 bg-[var(--blueprint-line)]" />
                    <span className="font-technical text-[var(--muted)]">ASSETS</span>
                </div>
                <div className="space-y-3">
                    {EXPORT_ITEMS.map((item) => {
                        const isDownloaded = downloaded.includes(item.id);
                        return (
                            <BlueprintCard key={item.id} data-animate code={item.code} showCorners padding="md" className={`transition-all ${isDownloaded ? "border-[var(--success)]/30 bg-[var(--success-light)]" : ""}`}>
                                <div className="flex items-center gap-4">
                                    <div className={`w-10 h-10 rounded-[var(--radius-sm)] flex items-center justify-center ${isDownloaded ? "bg-[var(--success)] ink-bleed-xs" : "bg-[var(--canvas)] border border-[var(--border)]"}`}>
                                        {isDownloaded ? <Check size={18} strokeWidth={1.5} className="text-[var(--paper)]" /> : <item.icon size={18} strokeWidth={1.5} className="text-[var(--blueprint)]" />}
                                    </div>
                                    <div className="flex-1">
                                        <h3 className="text-sm font-semibold text-[var(--ink)]">{item.name}</h3>
                                        <p className="text-xs text-[var(--muted)]">{item.description}</p>
                                    </div>
                                    <BlueprintBadge variant="default">{item.format}</BlueprintBadge>
                                    {isDownloaded ? (
                                        <BlueprintBadge variant="success" dot>DOWNLOADED</BlueprintBadge>
                                    ) : (
                                        <BlueprintButton size="sm" onClick={() => handleDownload(item.id)}><Download size={12} strokeWidth={1.5} />Download</BlueprintButton>
                                    )}
                                </div>
                            </BlueprintCard>
                        );
                    })}
                </div>
            </div>

            {/* Actions */}
            <div className="flex gap-3">
                <BlueprintButton data-animate size="lg" onClick={handleExportAll} className="flex-1" label="BTN-EXPORT"><Download size={16} strokeWidth={1.5} />Export All Assets</BlueprintButton>
                <SecondaryButton data-animate size="lg" onClick={handleCopyToClipboard}><Copy size={16} strokeWidth={1.5} />Copy Summary</SecondaryButton>
            </div>

            {/* Complete */}
            {allExported && (
                <BlueprintCard data-animate showCorners variant="elevated" padding="lg" className="text-center border-[var(--success)]/30 bg-gradient-to-r from-[var(--success-light)] via-[var(--paper)] to-[var(--blueprint-light)]">
                    <div className="w-12 h-12 rounded-[var(--radius-md)] bg-[var(--success)] flex items-center justify-center mx-auto mb-4 ink-bleed-sm"><Check size={22} className="text-[var(--paper)]" /></div>
                    <h3 className="font-serif text-xl text-[var(--ink)] mb-2">All Assets Exported!</h3>
                    <p className="text-sm text-[var(--secondary)] mb-4">Your foundation is ready. Head to your dashboard to start executing.</p>
                    <a href="/dashboard"><BlueprintButton size="lg">Go to Dashboard<ArrowRight size={16} strokeWidth={1.5} /></BlueprintButton></a>
                </BlueprintCard>
            )}

            {/* Document Footer */}
            <div className="flex justify-center pt-4">
                <span className="font-technical text-[var(--muted)]">DOCUMENT: EXPORT-ASSETS | STEP 25/25 | FINAL</span>
            </div>
        </div>
    );
}
