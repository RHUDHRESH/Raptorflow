"use client";

import React, { useState, useEffect } from "react";
import { SettingsNav } from "@/components/settings/SettingsNav";
import { AppearanceSection, ACCENT_COLORS } from "@/components/settings/sections";

export default function AppearanceSettingsPage() {
    const [data, setData] = useState({ accentColor: "blueprint" });

    // Load from localStorage
    useEffect(() => {
        const saved = localStorage.getItem("raptorflow_settings");
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                if (parsed.appearance) setData(parsed.appearance);
            } catch (e) {
                console.error(e);
            }
        }
    }, []);

    // Apply accent color
    useEffect(() => {
        const color = ACCENT_COLORS.find((c) => c.id === data.accentColor);
        if (color) {
            document.documentElement.style.setProperty("--blueprint", color.value);
            document.documentElement.style.setProperty("--accent-blue", color.value);
        }
        // Persist immediately on change
        const existing = JSON.parse(localStorage.getItem("raptorflow_settings") || "{}");
        localStorage.setItem(
            "raptorflow_settings",
            JSON.stringify({ ...existing, appearance: data })
        );
    }, [data]);

    const handleChange = (field: keyof typeof data, value: string) => {
        setData((prev) => ({ ...prev, [field]: value }));
    };

    return (
        <div className="min-h-[calc(100vh-80px)] bg-[var(--canvas)]">
            <div className="max-w-5xl mx-auto px-8 py-10">
                <div className="flex gap-12">
                    <SettingsNav />
                    <main className="flex-1 max-w-2xl">
                        <AppearanceSection data={data} onChange={handleChange} />
                    </main>
                </div>
            </div>
        </div>
    );
}
