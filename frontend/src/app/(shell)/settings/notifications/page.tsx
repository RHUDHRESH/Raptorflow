"use client";

import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import dynamic from 'next/dynamic';
import { Bell, Mail, MessageSquare, Zap } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

const BlueprintButton = dynamic(() => import("@/components/ui/BlueprintButton").then(mod => ({ default: mod.BlueprintButton })), { ssr: false });
const SecondaryButton = dynamic(() => import("@/components/ui/BlueprintButton").then(mod => ({ default: mod.SecondaryButton })), { ssr: false });

export const runtime = 'edge';

interface NotificationSetting {
    id: string;
    title: string;
    description: string;
    email: boolean;
    app: boolean;
}

export default function NotificationsSettingsPage() {
    const [settings, setSettings] = useState<NotificationSetting[]>([
        { id: "1", title: "Move Completion", description: "When a move is marked as done", email: true, app: true },
        { id: "2", title: "Campaign Alerts", description: "Status changes and deadline warnings", email: true, app: true },
        { id: "3", title: "Muse Insights", description: "New generated insights and trends", email: false, app: true },
        { id: "4", title: "Blackbox Reports", description: "Experimental run results", email: true, app: false },
        { id: "5", title: "Team Mentions", description: "When someone mentions you in a note", email: true, app: true },
    ]);

    const toggle = (id: string, channel: 'email' | 'app') => {
        setSettings(prev => prev.map(s =>
            s.id === id ? { ...s, [channel]: !s[channel] } : s
        ));
    };

    return (
        <div className="space-y-8">
            <div>
                <h2 className="text-xl font-semibold text-[var(--ink)]">Notifications</h2>
                <p className="text-sm text-[var(--secondary)]">Control how and when you receive alerts.</p>
            </div>

            <BlueprintCard title="Alert Preferences" code="NOT-01" padding="none" showCorners>
                <div className="bg-[var(--canvas)] border-b border-[var(--border-subtle)] px-6 py-3 flex items-center justify-between">
                    <span className="text-xs font-technical text-[var(--muted)]">EVENT TYPE</span>
                    <div className="flex gap-8 pr-4">
                        <span className="text-xs font-technical text-[var(--muted)] flex items-center gap-1"><Mail size={12} /> EMAIL</span>
                        <span className="text-xs font-technical text-[var(--muted)] flex items-center gap-1"><Bell size={12} /> IN-APP</span>
                    </div>
                </div>
                <div className="divide-y divide-[var(--border-subtle)]">
                    {settings.map((setting) => (
                        <div key={setting.id} className="px-6 py-4 flex items-center justify-between hover:bg-[var(--canvas)] transition-colors">
                            <div>
                                <h4 className="text-sm font-medium text-[var(--ink)]">{setting.title}</h4>
                                <p className="text-xs text-[var(--secondary)]">{setting.description}</p>
                            </div>
                            <div className="flex gap-12 pr-6">
                                <div
                                    onClick={() => toggle(setting.id, 'email')}
                                    className={cn(
                                        "w-4 h-4 rounded-[4px] border cursor-pointer transition-colors flex items-center justify-center",
                                        setting.email ? "bg-[var(--blueprint)] border-[var(--blueprint)]" : "border-[var(--border)]"
                                    )}
                                >
                                    {setting.email && <div className="w-2 h-2 bg-white rounded-[1px]" />}
                                </div>
                                <div
                                    onClick={() => toggle(setting.id, 'app')}
                                    className={cn(
                                        "w-4 h-4 rounded-[4px] border cursor-pointer transition-colors flex items-center justify-center",
                                        setting.app ? "bg-[var(--blueprint)] border-[var(--blueprint)]" : "border-[var(--border)]"
                                    )}
                                >
                                    {setting.app && <div className="w-2 h-2 bg-white rounded-[1px]" />}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </BlueprintCard>

            <div className="flex justify-end gap-3">
                <SecondaryButton>Reset to Defaults</SecondaryButton>
                <BlueprintButton>Save Preferences</BlueprintButton>
            </div>
        </div>
    );
}
