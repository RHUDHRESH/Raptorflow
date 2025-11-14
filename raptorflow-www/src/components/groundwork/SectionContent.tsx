'use client';

import React from 'react';
import { QuestionHeader } from './QuestionHeader';
import { AgentInsight } from './AgentInsight';
import { SectionActions } from './SectionActions';
import { BusinessIdentitySection } from './sections/BusinessIdentitySection';
import { AudienceICPSection } from './sections/AudienceICPSection';
import { GoalsConstraintsSection } from './sections/GoalsConstraintsSection';
import { AssetsVisualsSection } from './sections/AssetsVisualsSection';
import { BrandEnergySection } from './sections/BrandEnergySection';
import { useGroundwork } from './GroundworkProvider';
import { SectionId } from '@/lib/groundwork/types';

const SECTION_COMPONENTS: Record<SectionId, React.ComponentType> = {
  'business-identity': BusinessIdentitySection,
  'audience-icp': AudienceICPSection,
  'goals-constraints': GoalsConstraintsSection,
  'assets-visuals': AssetsVisualsSection,
  'brand-energy': BrandEnergySection,
};

export function SectionContent() {
  const { state, removeAgentQuestion } = useGroundwork();
  const currentSection = state.sections[state.currentSection];
  const SectionComponent = SECTION_COMPONENTS[state.currentSection];

  const handleDismissQuestion = (questionId: string) => {
    removeAgentQuestion(state.currentSection, questionId);
  };

  const handleAnswerQuestion = (questionId: string, answer: string) => {
    // In real implementation, this would send answer to backend
    // For now, just dismiss the question
    removeAgentQuestion(state.currentSection, questionId);
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto p-8">
          <QuestionHeader />

          <div className="space-y-6">
            {currentSection.agentQuestions.map((question) => (
              <AgentInsight
                key={question.id}
                question={question}
                onDismiss={() => handleDismissQuestion(question.id)}
                onAnswer={(answer) => handleAnswerQuestion(question.id, answer)}
              />
            ))}

            {SectionComponent && <SectionComponent />}
          </div>
        </div>
      </div>
      <SectionActions />
    </div>
  );
}

