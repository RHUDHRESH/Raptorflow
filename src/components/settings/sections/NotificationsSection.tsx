"use client";

import React from "react";
import { SettingsGroup, SettingsRow } from "../SettingsRow";
import { SettingsToggle } from "../SettingsToggle";

// ═══════════════════════════════════════════════════════════════
// NotificationsSection - Notification preferences
// ═══════════════════════════════════════════════════════════════

interface NotificationsData {
    email: boolean;
    weekly: boolean;
    reminders: boolean;
    marketing: boolean;
}

interface NotificationsSectionProps {
    data: NotificationsData;
    onChange: (field: keyof NotificationsData, value: boolean) => void;
}

const NOTIFICATION_ITEMS: {
    id: keyof NotificationsData;
    label: string;
    description: string;
    category: string;
}[] = [
        {
            id: "email",
            label: "Email notifications",
            description: "Updates about your campaigns and moves",
            category: "Activity",
        },
        {
            id: "reminders",
            label: "Execution reminders",
            description: "Reminders for scheduled moves",
            category: "Activity",
        },
        {
            id: "weekly",
            label: "Weekly digest",
            description: "Performance summary every Monday",
            category: "Digest",
        },
        {
            id: "marketing",
            label: "Product updates",
            description: "New features, tips, and announcements",
            category: "Marketing",
        },
    ];

export function NotificationsSection({ data, onChange }: NotificationsSectionProps) {
    // Group items by category
    const categories = NOTIFICATION_ITEMS.reduce((acc, item) => {
        if (!acc[item.category]) acc[item.category] = [];
        acc[item.category].push(item);
        return acc;
    }, {} as Record<string, typeof NOTIFICATION_ITEMS>);

    return (
        <div className="space-y-8">
            {/* Page Header */}
            <div>
                <h2 className="text-2xl font-semibold text-[var(--ink)]">Notifications</h2>
                <p className="text-sm text-[var(--muted)] mt-1">
                    Choose what updates you receive
                </p>
            </div>

            {/* Notification Groups */}
            {Object.entries(categories).map(([category, items]) => (
                <SettingsGroup key={category} title={category}>
                    {items.map((item, index) => (
                        <SettingsRow
                            key={item.id}
                            label={item.label}
                            description={item.description}
                            isLast={index === items.length - 1}
                        >
                            <SettingsToggle
                                checked={data[item.id]}
                                onChange={(checked) => onChange(item.id, checked)}
                                label={item.label}
                            />
                        </SettingsRow>
                    ))}
                </SettingsGroup>
            ))}
        </div>
    );
}
