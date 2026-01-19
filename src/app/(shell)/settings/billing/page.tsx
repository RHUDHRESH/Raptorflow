"use client";

import React from "react";
import { SettingsNav } from "@/components/settings/SettingsNav";
import { BillingSection } from "@/components/settings/sections";

export default function BillingSettingsPage() {
    return (
        <div className="min-h-[calc(100vh-80px)] bg-[var(--canvas)]">
            <div className="max-w-5xl mx-auto px-8 py-10">
                <div className="flex gap-12">
                    <SettingsNav />
                    <main className="flex-1 max-w-2xl">
                        <BillingSection />
                    </main>
                </div>
            </div>
        </div>
    );
}
