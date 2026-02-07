import { describe, it, expect, vi, beforeEach } from 'vitest';
import { FoundationData, emptyFoundation } from '@/lib/foundation';

// Mocking external dependencies
vi.mock('@/lib/foundation', async (importOriginal) => {
    const actual = await importOriginal() as any;
    return {
        ...actual,
        saveFoundation: vi.fn().mockResolvedValue(true),
        loadFoundationDB: vi.fn(),
    };
});

describe('Onboarding End-to-End Logic Validation', () => {
    let mockData: FoundationData;

    beforeEach(() => {
        mockData = JSON.parse(JSON.stringify(emptyFoundation));
        vi.clearAllMocks();
    });

    it('validates the complete data flow through all phases', async () => {
        // 1. Initial State (Questionnaire)
        mockData.phase1 = {
            identity: { name: 'Test User', company: 'Test Co', geo: { basedIn: 'India', sellsTo: ['global'] } },
            origin: { narrative: 'Testing onboarding' },
            success: { win90Days: 'Growth', win90Bullets: [], win12Months: 'Scale', bragMetric: 'revenue', optimizingFor: 'acquire' },
            offer: { primaryType: 'saas', timeToValue: 'instant', unfairAdvantage: { howWeWin: 'Logic', whyCantCopy: 'Complexity', whyItMatters: 'Speed' } },
            value: { pricingMode: 'monthly', currency: 'INR' },
            buyerUser: { userRoles: ['founder'], buyerRoles: ['founder'], samePersonAsBuyer: true },
            triggers: { triggers: [] },
            currentSystem: { workflowSteps: [], artifacts: [], triedBefore: [] },
            proofGuardrails: { proofAssets: { testimonials: true, caseStudies: false, numbers: true, logos: true, screenshots: false }, forbiddenClaims: [], voiceTone: 'calm', wordsToAvoid: [] }
        };

        // 2. Phase 3: Foundation & JTBD
        mockData.phase3 = {
            primaryContextId: '1',
            primaryContext: { youSell: 'SaaS', to: 'Founders', soTheyCan: 'Grow' },
            jtbd: {
                functional: 'Automate marketing',
                emotional: 'Feel in control',
                social: 'Be a leader',
                jobs: [], strugglingMoments: [], forces: { push: [], pull: [], anxiety: [], habit: [] }, switchTriggers: [], successMetrics: []
            },
            hierarchy: { essence: 'Unification', coreMessage: 'Systems first', pillars: [] },
            awarenessMatrix: { unaware: 'Pain', problem: 'Agitation', solution: 'Mechanism', product: 'Proof', most: 'Action' },
            vpc: { customerProfile: { jobs: [], pains: [], gains: [] }, valueMap: { productsServices: [], painRelievers: [], gainCreators: [] }, fitCoverage: { score: 0, gaps: [] } },
            differentiators: [], strategyCanvas: { factors: [], curves: { statusQuo: [], categoryLeader: [], youCurrent: [], youTarget: [] }, competitorNames: [] },
            errc: { eliminate: [], reduce: [], raise: [], create: [] }, claims: [], primaryClaimId: '', proofStack: []
        };

        // 3. Phase 5: Proof Vault
        mockData.proof = {
            evidence: [
                { id: 'e1', type: 'stat', content: '89% success rate', isVerified: true }
            ]
        };

        // 4. Phase 6: Soundbites
        mockData.phase6 = {
            soundbites: [
                { id: 's1', type: 'problem_revelation', text: 'You are losing time.', isLocked: true, alternatives: [] }
            ],
            blueprint: { controllingIdea: '', coreMessage: '', pillars: [], missingProofAlerts: [] },
            variants: [], realityCheck: { competitorChecks: [], proofQuality: [], awarenessMismatches: [], claimsAtRisk: [] },
            constraints: { bannedClaims: [], bannedWords: [], regulatedFlags: [], tonePreference: 'premium' },
            version: '1.0'
        };

        expect(mockData.phase3.jtbd.functional).toBe('Automate marketing');
        expect(mockData.proof.evidence[0].content).toContain('89%');
        expect(mockData.phase6.soundbites[0].isLocked).toBe(true);
    });
});
