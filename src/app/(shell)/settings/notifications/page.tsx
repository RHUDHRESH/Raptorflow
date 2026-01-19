"use client";

import React, { useState, useEffect } from "react";
import { SettingsNav } from "@/components/settings/SettingsNav";
import { NotificationsSection } from "@/components/settings/sections";

export default function NotificationsSettingsPage() {
    const [data, setData] = useState({
        email: true,
        weekly: true,
        reminders: true,
        marketing: false,
    });

    // Load from localStorage
    useEffect(() => {
        const saved = localStorage.getItem("raptorflow_settings");
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                if (parsed.notifications) setData(parsed.notifications);
            } catch (e) {
                console.error(e);
            }
        }
    }, []);

    const handleChange = (field: keyof typeof data, value: boolean) => {
        const newData = { ...data, [field]: value };
        setData(newData);
        // Persist immediately
        const existing = JSON.parse(localStorage.getItem("raptorflow_settings") || "{}");
        localStorage.setItem(
            "raptorflow_settings",
            JSON.stringify({ ...existing, notifications: newData })
        );
    };

    return (
        <div className="min-h-[calc(100vh-80px)] bg-[var(--canvas)]">
            <div className="max-w-5xl mx-auto px-8 py-10">
                <div className="flex gap-12">
                    <SettingsNav />
                    <main className="flex-1 max-w-2xl">
                        <NotificationsSection data={data} onChange={handleChange} />
                    </main>
                </div>
            </div>
        </div>
    );
}
