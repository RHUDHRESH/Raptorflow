'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import {
  GroundworkState,
  SectionId,
  SectionData,
  AgentQuestion,
  BusinessIdentityData,
  AudienceICPData,
  GoalsConstraintsData,
  BrandEnergyData,
} from '@/lib/groundwork/types';
import { SECTIONS, INITIAL_SECTION_STATE } from '@/lib/groundwork/config';

interface GroundworkContextValue {
  state: GroundworkState;
  setCurrentSection: (section: SectionId) => void;
  updateSectionData: (section: SectionId, data: SectionData) => void;
  markSectionComplete: (section: SectionId) => void;
  addAgentQuestion: (section: SectionId, question: AgentQuestion) => void;
  removeAgentQuestion: (section: SectionId, questionId: string) => void;
  resetGroundwork: () => void;
}

const GroundworkContext = createContext<GroundworkContextValue | undefined>(undefined);

const STORAGE_KEY = 'raptorflow-groundwork-state';

function getInitialState(): GroundworkState {
  if (typeof window === 'undefined') {
    return createDefaultState();
  }

  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      // Validate structure
      if (parsed && parsed.currentSection && parsed.sections) {
        return parsed as GroundworkState;
      }
    }
  } catch (error) {
    console.error('Failed to load groundwork state:', error);
  }

  return createDefaultState();
}

function createDefaultState(): GroundworkState {
  const sections = SECTIONS.reduce((acc, section) => {
    acc[section.id] = { ...INITIAL_SECTION_STATE };
    return acc;
  }, {} as GroundworkState['sections']);

  return {
    currentSection: 'business-identity',
    sections,
    phase: 'structured',
    isSubmitting: false,
  };
}

export function GroundworkProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<GroundworkState>(getInitialState);

  // Persist to localStorage whenever state changes
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (error) {
      console.error('Failed to save groundwork state:', error);
    }
  }, [state]);

  const setCurrentSection = useCallback((section: SectionId) => {
    setState((prev) => ({
      ...prev,
      currentSection: section,
    }));
  }, []);

  const updateSectionData = useCallback((section: SectionId, data: SectionData) => {
    setState((prev) => {
      // Check if section should be marked as complete
      let shouldComplete = false;

      if (section === 'business-identity') {
        const bizData = data as BusinessIdentityData;
        shouldComplete = !!(bizData.productDescription && bizData.whoPays && bizData.whoUses);
      } else if (section === 'audience-icp') {
        const icpData = data as AudienceICPData;
        shouldComplete = !!(icpData.icps && icpData.icps.length > 0 && icpData.icps[0].name);
      } else if (section === 'goals-constraints') {
        const goalsData = data as GoalsConstraintsData;
        shouldComplete = !!(goalsData.successMetric && goalsData.targetValue > 0);
      } else if (section === 'assets-visuals') {
        // Assets section is optional, so it's complete if data exists (even if empty)
        shouldComplete = true;
      } else if (section === 'brand-energy') {
        const brandData = data as BrandEnergyData;
        shouldComplete = !!(brandData.toneSliders);
      }

      return {
        ...prev,
        sections: {
          ...prev.sections,
          [section]: {
            ...prev.sections[section],
            data,
            completed: shouldComplete || prev.sections[section].completed,
          },
        },
      };
    });
  }, []);

  const markSectionComplete = useCallback((section: SectionId) => {
    setState((prev) => ({
      ...prev,
      sections: {
        ...prev.sections,
        [section]: {
          ...prev.sections[section],
          completed: true,
        },
      },
    }));
  }, []);

  const addAgentQuestion = useCallback((section: SectionId, question: AgentQuestion) => {
    setState((prev) => ({
      ...prev,
      sections: {
        ...prev.sections,
        [section]: {
          ...prev.sections[section],
          agentQuestions: [...prev.sections[section].agentQuestions, question],
        },
      },
    }));
  }, []);

  const removeAgentQuestion = useCallback((section: SectionId, questionId: string) => {
    setState((prev) => ({
      ...prev,
      sections: {
        ...prev.sections,
        [section]: {
          ...prev.sections[section],
          agentQuestions: prev.sections[section].agentQuestions.filter(
            (q) => q.id !== questionId
          ),
        },
      },
    }));
  }, []);

  const resetGroundwork = useCallback(() => {
    const defaultState = createDefaultState();
    setState(defaultState);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  const value: GroundworkContextValue = {
    state,
    setCurrentSection,
    updateSectionData,
    markSectionComplete,
    addAgentQuestion,
    removeAgentQuestion,
    resetGroundwork,
  };

  return (
    <GroundworkContext.Provider value={value}>
      {children}
    </GroundworkContext.Provider>
  );
}

export function useGroundwork() {
  const context = useContext(GroundworkContext);
  if (context === undefined) {
    throw new Error('useGroundwork must be used within a GroundworkProvider');
  }
  return context;
}

