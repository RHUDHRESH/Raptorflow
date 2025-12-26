'use client';

import { useState, useEffect, useCallback } from 'react';
import {
    FoundationData,
    emptyFoundation,
    saveFoundation,
    loadFoundationDB
} from '@/lib/foundation';
import { toast } from 'sonner';

export type OnboardingPhase = 'phase3' | 'phase4' | 'phase5' | 'phase6';

export function useOnboarding() {
    const [data, setData] = useState<FoundationData>(emptyFoundation);
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);

    // Load data from DB on mount
    useEffect(() => {
        async function init() {
            try {
                const dbData = await loadFoundationDB();
                setData(dbData);
            } catch (error) {
                console.error('Failed to load onboarding data:', error);
                toast.error('Failed to load your progress');
            } finally {
                setIsLoading(false);
            }
        }
        init();
    }, []);

    const updateData = useCallback((updater: (prev: FoundationData) => FoundationData) => {
        setData(prev => {
            const newData = updater(prev);
            return newData;
        });
    }, []);

    const saveProgress = useCallback(async (overrides?: Partial<FoundationData>) => {
        setIsSaving(true);
        try {
            const dataToSave = overrides ? { ...data, ...overrides } : data;
            await saveFoundation(dataToSave);
            setIsSaving(false);
            return true;
        } catch (error) {
            console.error('Failed to save progress:', error);
            toast.error('Failed to save progress');
            setIsSaving(false);
            return false;
        }
    }, [data]);

    const completePhase = useCallback(async (phase: OnboardingPhase, phaseData: any) => {
        const updater = (prev: FoundationData): FoundationData => {
            return {
                ...prev,
                [phase]: phaseData,
                // Update legacy fields if necessary
            };
        };

        const newData = updater(data);
        setData(newData);
        return await saveProgress(newData);
    }, [data, saveProgress]);

    return {
        data,
        isLoading,
        isSaving,
        updateData,
        saveProgress,
        completePhase,
    };
}
