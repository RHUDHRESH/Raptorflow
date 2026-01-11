"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import { Check, Linkedin, Twitter, Mail, FileText, Video, Plus, Trash2 } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintKPI, KPIGrid } from "@/components/ui/BlueprintKPI";
import { OnboardingStepLayout } from "../OnboardingStepLayout";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 21: Channel Mapping
   Map marketing channels by priority
   ══════════════════════════════════════════════════════════════════════════════ */

interface Channel { id: string; name: string; icon: React.ElementType; priority: "primary" | "secondary" | "experimental"; frequency: string; code: string; }

const INITIAL_CHANNELS: Channel[] = [
    { id: "1", name: "LinkedIn", icon: Linkedin, priority: "primary", frequency: "3x/week", code: "CH-01" },
    { id: "2", name: "Twitter/X", icon: Twitter, priority: "secondary", frequency: "Daily", code: "CH-02" },
    { id: "3", name: "Email Newsletter", icon: Mail, priority: "primary", frequency: "Weekly", code: "CH-03" },
    { id: "4", name: "Blog", icon: FileText, priority: "secondary", frequency: "2x/month", code: "CH-04" },
    { id: "5", name: "YouTube", icon: Video, priority: "experimental", frequency: "Monthly", code: "CH-05" },
];

const AVAILABLE_CHANNELS = [{ name: "LinkedIn", icon: Linkedin }, { name: "Twitter/X", icon: Twitter }, { name: "Email Newsletter", icon: Mail }, { name: "Blog", icon: FileText }, { name: "YouTube", icon: Video }];

export default function Step21ChannelMapping() {
    const { updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(21)?.data as { channels?: Channel[]; confirmed?: boolean } | undefined;
    const [channels, setChannels] = useState<Channel[]>(stepData?.channels || INITIAL_CHANNELS);
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);
    const containerRef = useRef<HTMLDivElement>(null);
    const idCounterRef = useRef(channels.length + 1);

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(containerRef.current.querySelectorAll("[data-animate]"), { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" });
    }, []);

    const saveData = (items: Channel[]) => { setChannels(items); updateStepData(21, { channels: items }); };
    const updatePriority = (id: string, priority: Channel["priority"]) => saveData(channels.map((c) => (c.id === id ? { ...c, priority } : c)));
    const removeChannel = (id: string) => saveData(channels.filter((c) => c.id !== id));
    const addChannel = (channelData: { name: string; icon: React.ElementType }) => {
        if (channels.some((c) => c.name === channelData.name)) return;
        const counter = idCounterRef.current++;
        const newId = `ch-${String(counter).padStart(2, "0")}`;
        const newChannel: Channel = {
            id: newId,
            ...channelData,
            priority: "experimental",
            frequency: "TBD",
            code: `CH-${String(channels.length + 1).padStart(2, "0")}`
        };
        saveData([...channels, newChannel]);
    };
    const handleConfirm = () => { setConfirmed(true); updateStepData(21, { channels, confirmed: true }); updateStepStatus(21, "complete"); };

    const priorityConfig = { primary: { label: "1°", variant: "success" as const }, secondary: { label: "2°", variant: "blueprint" as const }, experimental: { label: "?", variant: "default" as const } };

    return (
        <OnboardingStepLayout stepId={21} moduleLabel="CHANNELS" itemCount={channels.length}>
            <div ref={containerRef} className="space-y-6">
                <BlueprintCard data-animate showCorners padding="md" className="border-[var(--blueprint)]/30 bg-[var(--blueprint-light)]">
                    <p className="text-sm text-[var(--secondary)]">Map your marketing channels by priority: Primary (core focus), Secondary (supporting), Experimental (testing).</p>
                </BlueprintCard>

                <div data-animate className="space-y-3">
                    {channels.map((channel) => {
                        const ChannelIcon = channel.icon;
                        return (
                            <BlueprintCard key={channel.id} code={channel.code} showCorners padding="sm">
                                <div className="flex items-center gap-4">
                                    <div className="w-10 h-10 rounded-[var(--radius-sm)] bg-[var(--canvas)] border border-[var(--border)] flex items-center justify-center"><ChannelIcon size={18} strokeWidth={1.5} className="text-[var(--blueprint)]" /></div>
                                    <div className="flex-1"><h3 className="text-sm font-semibold text-[var(--ink)]">{channel.name}</h3><p className="font-technical text-[var(--muted)]">{channel.frequency}</p></div>
                                    <div className="flex gap-1">
                                        {(["primary", "secondary", "experimental"] as const).map((p) => (<button key={p} onClick={() => updatePriority(channel.id, p)} className={`px-2 py-1 font-technical rounded-[var(--radius-xs)] transition-all ${channel.priority === p ? `bg-[var(--${p === "primary" ? "success" : p === "secondary" ? "blueprint" : "muted"})] text-[var(--paper)]` : "text-[var(--muted)]"}`}>{priorityConfig[p].label}</button>))}
                                    </div>
                                    <button onClick={() => removeChannel(channel.id)} className="p-1.5 text-[var(--muted)] hover:text-[var(--error)] hover:bg-[var(--error-light)] rounded-[var(--radius-xs)] transition-all"><Trash2 size={12} strokeWidth={1.5} /></button>
                                </div>
                            </BlueprintCard>
                        );
                    })}
                </div>

                <BlueprintCard data-animate code="ADD" showCorners padding="md">
                    <p className="font-technical text-[var(--muted)] mb-3">ADD CHANNEL</p>
                    <div className="flex flex-wrap gap-2">
                        {AVAILABLE_CHANNELS.filter((a) => !channels.some((c) => c.name === a.name)).map((ch) => {
                            const AddIcon = ch.icon;
                            return (<button key={ch.name} onClick={() => addChannel(ch)} className="flex items-center gap-2 px-3 py-2 rounded-[var(--radius-sm)] bg-[var(--canvas)] text-sm text-[var(--secondary)] border border-[var(--border)] hover:border-[var(--blueprint)] hover:text-[var(--blueprint)] transition-all"><Plus size={10} strokeWidth={1.5} /><AddIcon size={12} strokeWidth={1.5} />{ch.name}</button>);
                        })}
                    </div>
                </BlueprintCard>

                <BlueprintCard data-animate figure="FIG. 01" title="Summary" code="SUM" showCorners padding="md">
                    <KPIGrid columns={3}>
                        <BlueprintKPI label="Primary" value={String(channels.filter((c) => c.priority === "primary").length)} code="1°" trend="up" />
                        <BlueprintKPI label="Secondary" value={String(channels.filter((c) => c.priority === "secondary").length)} code="2°" />
                        <BlueprintKPI label="Experimental" value={String(channels.filter((c) => c.priority === "experimental").length)} code="?" />
                    </KPIGrid>
                </BlueprintCard>

                {!confirmed && channels.length >= 3 && (
                    <BlueprintButton data-animate size="lg" onClick={handleConfirm} className="w-full" label="BTN-CONFIRM"><Check size={14} strokeWidth={1.5} />Confirm Channel Strategy</BlueprintButton>
                )}
                {confirmed && (
                    <BlueprintCard data-animate showCorners padding="md" className="border-[var(--success)]/30 bg-[var(--success-light)]">
                        <div className="flex items-center gap-3"><Check size={18} strokeWidth={1.5} className="text-[var(--success)]" /><span className="text-sm font-medium text-[var(--ink)]">Channel strategy confirmed</span><BlueprintBadge variant="success" dot className="ml-auto">CONFIRMED</BlueprintBadge></div>
                    </BlueprintCard>
                )}

            </div>
        </OnboardingStepLayout>
    );
}
