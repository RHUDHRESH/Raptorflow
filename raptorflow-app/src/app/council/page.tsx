import React from "react"
import { CouncilChamber } from "@/components/council/CouncilChamber"
import { SkillUploadZone } from "@/components/council/SkillUploadZone"
import { AgentTrainingDashboard } from "@/components/council/AgentTrainingDashboard"
import { AppLayout } from "@/components/layout/AppLayout"

export default function CouncilPage() {
    // Mock data for initial render
    const mockMetrics = {
        alignment: 0.85,
        confidence: 0.92,
        risk: 0.12
    }

    return (
        <AppLayout>
            <div className="p-8 max-w-7xl mx-auto space-y-24">
                <section>
                    <CouncilChamber consensusMetrics={mockMetrics} />
                </section>

                <section className="pt-12 border-t border-borders/30">
                    <AgentTrainingDashboard />
                </section>

                <section className="grid grid-cols-1 md:grid-cols-2 gap-12 pt-12 border-t border-borders/30">
                    <SkillUploadZone />

                    <div className="space-y-6">
                        <header>
                            <h3 className="text-lg font-serif italic text-ink">Global Heuristics</h3>
                            <p className="text-xs text-secondary-text mt-1">Live rules currently governing all 12 Experts.</p>
                        </header>
                        <div className="p-6 rounded-3xl bg-surface/50 border border-borders/50 min-h-[200px] flex flex-col gap-3">
                            <div className="flex items-center gap-3 p-3 rounded-xl bg-green-500/5 border border-green-500/10">
                                <Zap className="h-3.5 w-3.5 text-green-500" />
                                <span className="text-[11px] text-primary-text font-medium">Always maintain brand voice consistency.</span>
                            </div>
                            <div className="flex items-center gap-3 p-3 rounded-xl bg-red-500/5 border border-red-500/10">
                                <Shield className="h-3.5 w-3.5 text-red-500" />
                                <span className="text-[11px] text-primary-text font-medium">Never post without 24h lead time.</span>
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </AppLayout>
    )
}
