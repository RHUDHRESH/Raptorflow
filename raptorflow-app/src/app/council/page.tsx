import React from "react"
import { CouncilChamber } from "@/components/council/CouncilChamber"
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
            <div className="p-8">
                <CouncilChamber consensusMetrics={mockMetrics} />
            </div>
        </AppLayout>
    )
}
