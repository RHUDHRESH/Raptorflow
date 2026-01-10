"use client";

import React, { createContext, useContext, useMemo } from "react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { ONBOARDING_STEPS } from "@/lib/onboarding-tokens";

/* ══════════════════════════════════════════════════════════════════════════════
   ONBOARDING DATA PROVIDER — Cross-step data access
   Provides computed selectors for accessing data from any step
   ══════════════════════════════════════════════════════════════════════════════ */

// Types for step data
interface EvidenceItem {
    id: string;
    type: "url" | "file";
    name: string;
    status: "pending" | "processing" | "complete" | "error";
    url?: string;
    fileType?: string;
    size?: number;
    tags?: string[];
}

interface ExtractedFact {
    id: string;
    category: string;
    label: string;
    value: string;
    confidence: number;
    sources: { type: "url" | "file"; name: string; excerpt?: string }[];
    status: "pending" | "verified" | "edited";
}

interface Issue {
    id: string;
    type: "contradiction" | "unproven" | "missing";
    priority: "high" | "medium" | "low";
    title: string;
    description: string;
    resolved: boolean;
    resolution?: string;
}

interface TruthSheetItem {
    id: string;
    category: string;
    label: string;
    value: string;
    status: "confirmed" | "needs-review" | "edited";
    proofLinked: boolean;
}

interface ICPProfile {
    id: string;
    name: string;
    description: string;
    painIntensity: number;
    willingnessToPay: number;
    accessibility: number;
    isPrimary: boolean;
}

interface PositioningStatement {
    id: string;
    statement: string;
    target: string;
    category: string;
    benefit: string;
    proof: string;
    isSelected: boolean;
}

interface OnboardingDataContextType {
    // Step 1: Evidence Vault
    evidence: EvidenceItem[];
    evidenceCount: number;
    hasRequiredEvidence: boolean;

    // Step 2: Extracted Facts
    facts: ExtractedFact[];
    factsByCategory: Record<string, ExtractedFact[]>;

    // Step 3: Issues
    issues: Issue[];
    unresolvedHighPriority: Issue[];

    // Step 4: Truth Sheet
    truthSheet: TruthSheetItem[];
    isTruthSheetLocked: boolean;

    // Step 15: ICP
    icpProfiles: ICPProfile[];
    primaryICP: ICPProfile | null;

    // Step 13: Positioning
    positioningStatements: PositioningStatement[];
    selectedPositioning: PositioningStatement | null;

    // Computed helpers
    getStepData: <T>(stepId: number) => T | undefined;
    isStepComplete: (stepId: number) => boolean;
    canProceed: boolean;
}

const OnboardingDataContext = createContext<OnboardingDataContextType | null>(null);

export function OnboardingDataProvider({ children }: { children: React.ReactNode }) {
    const { steps, getStepById } = useOnboardingStore();

    const value = useMemo(() => {
        // Helper to get typed step data
        const getStepData = <T,>(stepId: number): T | undefined => {
            return getStepById(stepId)?.data as T | undefined;
        };

        const isStepComplete = (stepId: number): boolean => {
            return getStepById(stepId)?.status === "complete";
        };

        // Step 1: Evidence
        const step1Data = getStepData<{ evidence?: EvidenceItem[] }>(1);
        const evidence = step1Data?.evidence || [];
        const evidenceCount = evidence.length;
        const hasRequiredEvidence = evidence.some(e => e.type === "url") && evidence.some(e => e.type === "file");

        // Step 2: Facts
        const step2Data = getStepData<{ facts?: ExtractedFact[] }>(2);
        const facts = step2Data?.facts || [];
        const factsByCategory = facts.reduce((acc, fact) => {
            if (!acc[fact.category]) acc[fact.category] = [];
            acc[fact.category].push(fact);
            return acc;
        }, {} as Record<string, ExtractedFact[]>);

        // Step 3: Issues
        const step3Data = getStepData<{ issues?: Issue[] }>(3);
        const issues = step3Data?.issues || [];
        const unresolvedHighPriority = issues.filter(i => i.priority === "high" && !i.resolved);

        // Step 4: Truth Sheet
        const step4Data = getStepData<{ truthSheet?: TruthSheetItem[]; locked?: boolean }>(4);
        const truthSheet = step4Data?.truthSheet || [];
        const isTruthSheetLocked = step4Data?.locked || false;

        // Step 15: ICP
        const step15Data = getStepData<{ profiles?: ICPProfile[] }>(15);
        const icpProfiles = step15Data?.profiles || [];
        const primaryICP = icpProfiles.find(p => p.isPrimary) || null;

        // Step 13: Positioning
        const step13Data = getStepData<{ statements?: PositioningStatement[] }>(13);
        const positioningStatements = step13Data?.statements || [];
        const selectedPositioning = positioningStatements.find(s => s.isSelected) || null;

        // Overall progress check
        const requiredSteps = ONBOARDING_STEPS.filter(s => s.required);
        const canProceed = requiredSteps.every(s => isStepComplete(s.id));

        return {
            evidence,
            evidenceCount,
            hasRequiredEvidence,
            facts,
            factsByCategory,
            issues,
            unresolvedHighPriority,
            truthSheet,
            isTruthSheetLocked,
            icpProfiles,
            primaryICP,
            positioningStatements,
            selectedPositioning,
            getStepData,
            isStepComplete,
            canProceed,
        };
    }, [steps, getStepById]);

    return (
        <OnboardingDataContext.Provider value={value}>
            {children}
        </OnboardingDataContext.Provider>
    );
}

export function useOnboardingData() {
    const context = useContext(OnboardingDataContext);
    if (!context) {
        throw new Error("useOnboardingData must be used within OnboardingDataProvider");
    }
    return context;
}

// Convenience hooks for specific data
export function useEvidenceVault() {
    const { evidence, evidenceCount, hasRequiredEvidence } = useOnboardingData();
    return { evidence, evidenceCount, hasRequiredEvidence };
}

export function useTruthSheet() {
    const { truthSheet, isTruthSheetLocked, facts, factsByCategory } = useOnboardingData();
    return { truthSheet, isTruthSheetLocked, facts, factsByCategory };
}

export function usePositioning() {
    const { positioningStatements, selectedPositioning } = useOnboardingData();
    return { positioningStatements, selectedPositioning };
}

export function useICP() {
    const { icpProfiles, primaryICP } = useOnboardingData();
    return { icpProfiles, primaryICP };
}
