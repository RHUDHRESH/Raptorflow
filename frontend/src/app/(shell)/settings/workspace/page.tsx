"use client";

import React, { useState, useEffect, useCallback } from "react";
import { toast } from "sonner";
import { useAuth } from "@/components/auth/AuthProvider";
import { SettingsNav } from "@/components/settings/SettingsNav";
import { WorkspaceSection } from "@/components/settings/sections";

export default function WorkspaceSettingsPage() {
    const { user } = useAuth();
    const [hasChanges, setHasChanges] = useState(false);
    const [saving, setSaving] = useState(false);

    const [data, setData] = useState({
        name: `${user
                ? user.email.split("@")[0].charAt(0).toUpperCase() +
                user.email.split("@")[0].slice(1)
                : "User"
            }'s Marketing HQ`,
        industry: "b2b-saas",
        timezone: "Asia/Kolkata",
    });

    // Load from localStorage
    useEffect(() => {
        const saved = localStorage.getItem("raptorflow_settings");
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                if (parsed.workspace) setData(parsed.workspace);
            } catch (e) {
                console.error(e);
            }
        }
    }, []);

    const handleChange = (field: keyof typeof data, value: string) => {
        setData((prev) => ({ ...prev, [field]: value }));
        setHasChanges(true);
    };

    const handleSave = async () => {
        setSaving(true);
        await new Promise((r) => setTimeout(r, 500));
        const existing = JSON.parse(localStorage.getItem("raptorflow_settings") || "{}");
        localStorage.setItem(
            "raptorflow_settings",
            JSON.stringify({ ...existing, workspace: data })
        );
        setSaving(false);
        setHasChanges(false);
        toast.success("Workspace settings saved");
    };

    return (
        <div className="min-h-[calc(100vh-80px)] bg-[var(--canvas)]">
            <div className="max-w-5xl mx-auto px-8 py-10">
                <div className="flex gap-12">
                    <SettingsNav />
                    <main className="flex-1 max-w-2xl">
                        <WorkspaceSection
                            data={data}
                            onChange={handleChange}
                            onSave={handleSave}
                            hasChanges={hasChanges}
                            saving={saving}
                        />
                    </main>
                </div>
            </div>
        </div>
    );
}
