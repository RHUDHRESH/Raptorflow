"use client";

import { useRef, useEffect } from "react";
import gsap from "gsap";
import {
    Bell,
    CheckCircle,
    AlertTriangle,
    Info,
    Mail,
    UserPlus,
    CreditCard
} from "lucide-react";

import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";

const NOTIFICATIONS = [
    { id: 1, type: "success", title: "Campaign Completed", message: "Q4 Outreach campaign exceeded targets by 12%.", time: "2h ago", icon: CheckCircle },
    { id: 2, type: "info", title: "New Team Member", message: "Sarah access request approved.", time: "5h ago", icon: UserPlus },
    { id: 3, type: "warning", title: "Usage Alert", message: "You have used 80% of your AI credits.", time: "1d ago", icon: AlertTriangle },
    { id: 4, type: "info", title: "Invoice Paid", message: "Payment for December successful.", time: "2d ago", icon: CreditCard },
];

export default function NotificationsPage() {
    const pageRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!pageRef.current) return;
        const tl = gsap.timeline({ defaults: { ease: "power2.out" } });
        tl.fromTo("[data-anim]", { opacity: 0, x: -10 }, { opacity: 1, x: 0, duration: 0.4, stagger: 0.08 });
    }, []);

    return (
        <div ref={pageRef} className="max-w-3xl mx-auto pb-12">
            <div className="flex justify-between items-end mb-8">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <span className="font-technical text-[var(--blueprint)]">SYS-NTF</span>
                        <div className="h-px w-8 bg-[var(--blueprint-line)]" />
                        <span className="font-technical text-[var(--muted)]">ALERTS</span>
                    </div>
                    <h1 className="font-serif text-3xl text-[var(--ink)]">Activity Feed</h1>
                </div>
                <BlueprintButton size="sm" variant="secondary">Mark All Read</BlueprintButton>
            </div>

            <BlueprintCard padding="none" showCorners code="FEED" className="divide-y divide-[var(--border-subtle)]">
                {NOTIFICATIONS.map((note) => {
                    const Icon = note.icon;
                    return (
                        <div key={note.id} className="p-5 flex gap-4 hover:bg-[var(--canvas)] transition-colors group" data-anim>
                            <div className={`mt-1 p-2 rounded-full shrink-0 ${note.type === 'success' ? 'bg-[var(--success-light)] text-[var(--success)]' :
                                    note.type === 'warning' ? 'bg-[var(--warning-light)] text-[var(--warning)]' :
                                        'bg-[var(--blueprint-light)] text-[var(--blueprint)]'
                                }`}>
                                <span className="text-base">≡ƒöö</span>
                            </div>
                            <div className="flex-1">
                                <div className="flex justify-between items-start mb-1">
                                    <h4 className="text-sm font-semibold text-[var(--ink)]">{note.title}</h4>
                                    <span className="text-xs font-mono text-[var(--muted)]">{note.time}</span>
                                </div>
                                <p className="text-sm text-[var(--secondary)]">{note.message}</p>
                            </div>
                            <div className="opacity-0 group-hover:opacity-100 transition-opacity self-center">
                                <button className="p-2 text-[var(--muted)] hover:text-[var(--ink)] hover:bg-[var(--border)] rounded-[var(--radius-sm)]">
                                    <span>Γ£à</span>
                                </button>
                            </div>
                        </div>
                    );
                })}
            </BlueprintCard>

            <div className="mt-8 text-center pt-8 border-t border-[var(--border-subtle)] border-dashed">
                <p className="text-xs text-[var(--muted)]">Showing last 30 days of activity.</p>
            </div>
        </div>
    );
}
