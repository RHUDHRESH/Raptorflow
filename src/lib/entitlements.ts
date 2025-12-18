export function entitlementsForPlanName(planName: string | null) {
    return {
        limits: {
            activeCampaigns: 5,
            movesPerMonth: 20
        }
    }
}
