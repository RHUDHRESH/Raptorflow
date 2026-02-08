"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useMemo } from "react";
import MuseChat from "@/components/muse/MuseChat";

/* ══════════════════════════════════════════════════════════════════════════════
   MUSE — AI Content Assistant
   Quiet Luxury: Clean interface, powerful AI-powered content creation
   ══════════════════════════════════════════════════════════════════════════════ */

interface MuseContext {
    topic?: string;
    angle?: string;
    hook?: string;
    outline?: string[];
    platform?: string;
}

function MusePageContent() {
    const searchParams = useSearchParams();

    // Parse context from URL if provided (from Daily Wins, BlackBox, etc.)
    const initialContext = useMemo(() => {
        if (!searchParams) return null;
        const contextParam = searchParams.get("context");
        if (!contextParam) return null;

        try {
            const parsed = JSON.parse(decodeURIComponent(contextParam)) as MuseContext;

            // Build initial prompt from context
            const promptParts: string[] = [];

            if (parsed.topic) {
                promptParts.push(`Topic: ${parsed.topic}`);
            }
            if (parsed.angle) {
                promptParts.push(`Angle: ${parsed.angle}`);
            }
            if (parsed.hook) {
                promptParts.push(`Hook: "${parsed.hook}"`);
            }
            if (parsed.outline && parsed.outline.length > 0) {
                promptParts.push(`Structure:\n${parsed.outline.map((s, i) => `${i + 1}. ${s}`).join("\n")}`);
            }
            if (parsed.platform) {
                promptParts.push(`Target Platform: ${parsed.platform}`);
            }

            const fullPrompt = `Help me expand this content idea into a full post:\n\n${promptParts.join("\n\n")}\n\nPlease write the complete post following this structure.`;

            return {
                topic: parsed.topic || "Content Expansion",
                prompt: fullPrompt,
                platform: parsed.platform
            };
        } catch {
            return null;
        }
    }, [searchParams]);

    return (
        <div className="h-screen bg-[var(--canvas)]">
            <div className="h-full max-w-4xl mx-auto p-4">
                <div className="h-full">
                    <MuseChat initialContext={initialContext} />
                </div>
            </div>
        </div>
    );
}

export default function MusePage() {
    return (
        <Suspense fallback={
            <div className="h-screen bg-[var(--canvas)] flex items-center justify-center">
                <div className="text-center">
                    <div className="w-8 h-8 border-2 border-[var(--ink)] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                    <p className="text-sm text-[var(--muted)]">Loading Muse...</p>
                </div>
            </div>
        }>
            <MusePageContent />
        </Suspense>
    );
}
