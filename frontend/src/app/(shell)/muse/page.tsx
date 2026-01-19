"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useMemo, useState } from "react";
import MuseChat from "@/components/muse/MuseChat";
import { MuseLibrary } from "@/components/muse/MuseLibrary";
import { ContentCalendar } from "@/components/muse/ContentCalendar";
import { TemplateSelector } from "@/components/muse/TemplateSelector";
import { TemplateEditor } from "@/components/muse/TemplateEditor";
import { MuseAnalytics } from "@/components/muse/MuseAnalytics";
import { QuickActionsBar } from "@/components/muse/QuickActionsBar";
import { BlueprintTabs, TabContent } from "@/components/ui/BlueprintTabs";
import { MessageSquare, Library, Layout, Calendar, BarChart2 } from "lucide-react";
import { useMuseStore } from "@/stores/museStore";
import { Template } from "@/lib/museTemplates";
import { exportAssets } from "@/lib/museExport";

/* ══════════════════════════════════════════════════════════════════════════════
   MUSE — Content Operating System
   The central hub for strategy-driven content creation and distribution.
   ══════════════════════════════════════════════════════════════════════════════ */

function MusePageContent() {
    const searchParams = useSearchParams();
    const { assets, addAsset } = useMuseStore();
    const [activeTab, setActiveTab] = useState("chat");
    const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
    const [chatKey, setChatKey] = useState(Date.now()); // For resetting chat

    // Parse context from URL
    const initialContext = useMemo(() => {
        const contextParam = searchParams.get("context");
        if (!contextParam) return null;
        try {
            const parsed = JSON.parse(decodeURIComponent(contextParam));
            return {
                topic: parsed.topic || "Content Expansion",
                prompt: parsed.prompt || `Help me expand on: ${parsed.topic}`,
                platform: parsed.platform
            };
        } catch { return null; }
    }, [searchParams]);

    const tabs = [
        { id: "chat", label: "CHAT", icon: <MessageSquare size={16} />, code: "MSC-01" },
        { id: "templates", label: "TEMPLATES", icon: <Layout size={16} />, code: "MSC-02" },
        { id: "library", label: "LIBRARY", icon: <Library size={16} />, code: "MSC-03" },
        { id: "calendar", label: "CALENDAR", icon: <Calendar size={16} />, code: "MSC-04" },
        { id: "analytics", label: "ANALYTICS", icon: <BarChart2 size={16} />, code: "MSC-05" },
    ];

    const handleTemplateSubmit = (content: string) => {
        if (!selectedTemplate) return;
        
        addAsset({
            title: `Draft: ${selectedTemplate.title}`,
            content,
            type: selectedTemplate.type as any,
            tags: [...selectedTemplate.tags, "Template"],
            source: "Template"
        });
        
        setSelectedTemplate(null);
        setActiveTab("library");
    };

    // Quick Action Handlers
    const handleNewChat = () => {
        setChatKey(Date.now());
        setActiveTab("chat");
    };

    const handleUseTemplate = () => {
        setActiveTab("templates");
    };

    const handleExport = () => {
        if (assets.length === 0) return;
        exportAssets(assets, 'markdown', { includeMetadata: true });
    };

    const handleSync = () => {
        // Refresh BCM context or server sync
        console.log("Syncing Muse OS state...");
    };

    return (
        <div className="min-h-screen bg-[var(--canvas)] relative pb-24">
            <div className="max-w-6xl mx-auto p-6 space-y-8">
                {/* Header Section */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <h1 className="text-3xl font-bold text-[var(--ink)] tracking-tight">Muse</h1>
                        <p className="text-[var(--ink-muted)] mt-1">Strategic Content Operating System</p>
                    </div>
                    <BlueprintTabs 
                        tabs={tabs} 
                        activeTab={activeTab} 
                        onChange={setActiveTab}
                        className="w-auto"
                    />
                </div>

                {/* View Container */}
                <div className="relative min-h-[700px]">
                    {activeTab === "chat" && (
                        <TabContent>
                            <div className="max-w-4xl mx-auto h-[700px] border border-[var(--structure-subtle)] rounded-xl overflow-hidden shadow-sm bg-[var(--paper)]">
                                <MuseChat key={chatKey} initialContext={initialContext} />
                            </div>
                        </TabContent>
                    )}

                    {activeTab === "templates" && (
                        <TabContent>
                            <TemplateSelector 
                                onSelect={setSelectedTemplate} 
                                onClose={() => setActiveTab("chat")} 
                            />
                        </TabContent>
                    )}

                    {activeTab === "library" && (
                        <TabContent>
                            <MuseLibrary />
                        </TabContent>
                    )}

                    {activeTab === "calendar" && (
                        <TabContent>
                            <div className="h-[750px] border border-[var(--structure-subtle)] rounded-xl overflow-hidden shadow-sm bg-[var(--paper)]">
                                <ContentCalendar assets={assets} />
                            </div>
                        </TabContent>
                    )}

                    {activeTab === "analytics" && (
                        <TabContent>
                            <MuseAnalytics />
                        </TabContent>
                    )}
                </div>
            </div>

            {/* Quick Actions Bar */}
            <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50">
                <QuickActionsBar 
                    onNewChat={handleNewChat}
                    onUseTemplate={handleUseTemplate}
                    onExport={handleExport}
                    onSync={handleSync}
                />
            </div>

            {/* Template Modal */}
            {selectedTemplate && (
                <TemplateEditor
                    template={selectedTemplate}
                    onClose={() => setSelectedTemplate(null)}
                    onSubmit={handleTemplateSubmit}
                />
            )}
        </div>
    );
}

export default function MusePage() {
    return (
        <Suspense fallback={
            <div className="h-screen bg-[var(--canvas)] flex items-center justify-center">
                <div className="text-center">
                    <div className="w-8 h-8 border-2 border-[var(--ink)] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                    <p className="text-sm text-[var(--muted)] uppercase font-technical">Loading Muse OS...</p>
                </div>
            </div>
        }>
            <MusePageContent />
        </Suspense>
    );
}