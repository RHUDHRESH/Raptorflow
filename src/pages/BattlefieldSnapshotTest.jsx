import React from 'react';
import BattlefieldSnapshotStep from '../components/onboarding/BattlefieldSnapshotStep';

// Mock data for testing
const mockAnalysis = {
    analysisId: 'analysis-123',
    summary: {
        companyType: 'B2B SaaS',
        productOrService: 'AI-powered marketing automation platform that helps mid-market companies scale their content production and distribution.',
        primaryAudience: 'Marketing directors at B2B SaaS companies with 50-200 employees, struggling to maintain consistent content velocity.',
        mainPainPoints: [
            'Content production bottleneck',
            'Inconsistent brand voice',
            'Poor attribution tracking',
        ],
        currentApproach: 'Manual content creation with freelancers',
        desiredOutcome: 'Scale to 3x content output while maintaining quality',
    },
    diagnostics: {
        positioningUniqueness: 0.65,
        icpClarity: 0.82,
        marketingMaturity: 0.45,
    },
    notes: {
        positioningRisks: [
            'Crowded AI marketing space',
            'Generic "AI-powered" positioning',
            'Unclear differentiation from HubSpot',
        ],
        obviousOpportunities: [
            'Strong ICP clarity enables focused messaging',
            'Mid-market gap between enterprise and SMB tools',
            'Content velocity as a specific wedge',
        ],
        statusQuoCompetitor: 'Doing it manually with a team of freelancers',
    },
    createdAt: new Date().toISOString(),
};

const BattlefieldSnapshotTest = () => {
    const handleBack = () => {
        console.log('Back clicked');
    };

    const handleBlueprintReady = (blueprintId) => {
        console.log('Blueprint ready:', blueprintId);
    };

    return (
        <BattlefieldSnapshotStep
            analysis={mockAnalysis}
            onBack={handleBack}
            onBlueprintReady={handleBlueprintReady}
        />
    );
};

export default BattlefieldSnapshotTest;
