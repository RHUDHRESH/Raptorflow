'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';

interface ProgressBarProps {
  currentStep: number;
  totalSteps: number;
  onStepClick?: (stepId: number) => void;
  showLabels?: boolean;
  compact?: boolean;
}

interface StepInfo {
  id: number;
  title: string;
  description: string;
  category: string;
}

const ONBOARDING_STEPS: StepInfo[] = [
  { id: 1, title: "Welcome", description: "Introduction to Raptorflow", category: "Foundation" },
  { id: 2, title: "Account Setup", description: "Basic profile information", category: "Foundation" },
  { id: 3, title: "Business Name", description: "Your company identity", category: "Foundation" },
  { id: 4, title: "Industry", description: "Business sector classification", category: "Foundation" },
  { id: 5, title: "Company Size", description: "Team and revenue scale", category: "Foundation" },
  { id: 6, title: "Business Model", description: "Revenue streams", category: "Foundation" },
  { id: 7, title: "Target Audience", description: "Primary customer profile", category: "ICP" },
  { id: 8, title: "Pain Points", description: "Customer challenges", category: "ICP" },
  { id: 9, title: "Solutions", description: "Value propositions", category: "ICP" },
  { id: 10, title: "Competition", description: "Market landscape", category: "Competitive" },
  { id: 11, title: "Differentiation", description: "Unique advantages", category: "Competitive" },
  { id: 12, title: "Positioning", description: "Market placement", category: "Competitive" },
  { id: 13, title: "Brand Voice", description: "Communication style", category: "Messaging" },
  { id: 14, title: "Key Messages", description: "Core communication points", category: "Messaging" },
  { id: 15, title: "Value Proposition", description: "Primary value statement", category: "Messaging" },
  { id: 16, title: "Marketing Channels", description: "Distribution platforms", category: "Go-to-Market" },
  { id: 17, title: "Sales Strategy", description: "Revenue generation approach", category: "Go-to-Market" },
  { id: 18, title: "Customer Journey", description: "Experience mapping", category: "Go-to-Market" },
  { id: 19, title: "Success Metrics", description: "KPIs and measurements", category: "Analytics" },
  { id: 20, title: "Growth Goals", description: "Scaling objectives", category: "Analytics" },
  { id: 21, title: "Technical Setup", description: "Platform configuration", category: "Implementation" },
  { id: 22, title: "Team Access", description: "User permissions", category: "Implementation" },
  { id: 23, title: "Launch Ready", description: "Final preparations", category: "Implementation" }
];

const CATEGORIES = [
  { name: "Foundation", color: "blue", steps: 1 },
  { name: "ICP", color: "green", steps: 3 },
  { name: "Competitive", color: "purple", steps: 3 },
  { name: "Messaging", color: "orange", steps: 3 },
  { name: "Go-to-Market", color: "red", steps: 3 },
  { name: "Analytics", color: "cyan", steps: 2 },
  { name: "Implementation", color: "gray", steps: 3 }
];

export function ProgressBar({
  currentStep,
  totalSteps = 23,
  onStepClick,
  showLabels = true,
  compact = false
}: ProgressBarProps) {
  const router = useRouter();
  const progressPercentage = (currentStep / totalSteps) * 100;

  const handleStepClick = (stepId: number) => {
    if (onStepClick) {
      onStepClick(stepId);
    } else {
      router.push(`/onboarding/session/step/${stepId}`);
    }
  };

  const getStepStatus = (stepId: number) => {
    if (stepId < currentStep) return 'completed';
    if (stepId === currentStep) return 'current';
    return 'upcoming';
  };

  const getStepColor = (stepId: number) => {
    const status = getStepStatus(stepId);
    switch (status) {
      case 'completed':
        return 'bg-[var(--blueprint)] text-white border-[var(--blueprint)]';
      case 'current':
        return 'bg-white text-[var(--ink)] border-[var(--blueprint)] ring-2 ring-[var(--blueprint)]';
      default:
        return 'bg-[var(--paper)] text-[var(--muted)] border-[var(--border)]';
    }
  };

  if (compact) {
    return (
      <div className="w-full">
        {/* Compact progress bar */}
        <div className="relative h-2 bg-[var(--border)] rounded-full overflow-hidden">
          <div
            className="absolute left-0 top-0 h-full bg-[var(--blueprint)] transition-all duration-300 ease-out"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>

        {/* Compact step indicators */}
        <div className="flex justify-between mt-2">
          <span className="text-xs font-technical text-[var(--muted)]">
            Step {currentStep} of {totalSteps}
          </span>
          <span className="text-xs font-technical text-[var(--muted)]">
            {Math.round(progressPercentage)}% Complete
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full space-y-4">
      {/* Progress header */}
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-serif text-[var(--ink)]">Onboarding Progress</h3>
          <p className="text-sm text-[var(--muted)] font-technical">
            Step {currentStep} of {totalSteps} • {Math.round(progressPercentage)}% Complete
          </p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-[var(--blueprint)]">
            {Math.round(progressPercentage)}%
          </div>
          <div className="text-xs text-[var(--muted)] font-technical">Complete</div>
        </div>
      </div>

      {/* Main progress bar */}
      <div className="relative h-3 bg-[var(--border)] rounded-full overflow-hidden">
        <div
          className="absolute left-0 top-0 h-full bg-gradient-to-r from-[var(--blueprint)] to-blue-600 transition-all duration-500 ease-out"
          style={{ width: `${progressPercentage}%` }}
        />
        {/* Blueprint corner marks */}
        <div className="absolute inset-0 flex">
          {[...Array(Math.floor(totalSteps / 3))].map((_, i) => (
            <div key={i} className="flex-1 border-r border-[var(--border)] opacity-30" />
          ))}
        </div>
      </div>

      {/* Category indicators */}
      <div className="flex justify-between">
        {CATEGORIES.map((category, index) => {
          const categoryStart = CATEGORIES.slice(0, index).reduce((acc, cat) => acc + cat.steps, 0) + 1;
          const categoryEnd = categoryStart + category.steps - 1;
          const isCompleted = currentStep >= categoryEnd;
          const isCurrent = currentStep >= categoryStart && currentStep <= categoryEnd;

          return (
            <div
              key={category.name}
              className={cn(
                "flex-1 text-center px-1 py-1 rounded text-xs font-technical transition-colors",
                isCompleted && "bg-blue-100 text-blue-700",
                isCurrent && !isCompleted && "bg-blue-50 text-blue-600 border border-blue-200",
                !isCompleted && !isCurrent && "text-[var(--muted)]"
              )}
            >
              <div className="truncate">{category.name}</div>
            </div>
          );
        })}
      </div>

      {/* Step navigation */}
      {showLabels && (
        <div className="space-y-3">
          {/* Step groups by category */}
          {CATEGORIES.map((category) => {
            const categoryStart = CATEGORIES.slice(0, CATEGORIES.indexOf(category)).reduce((acc, cat) => acc + cat.steps, 0) + 1;
            const categoryEnd = categoryStart + category.steps - 1;
            const categorySteps = ONBOARDING_STEPS.slice(categoryStart - 1, categoryEnd);

            return (
              <div key={category.name} className="space-y-2">
                <div className="text-xs font-technical text-[var(--muted)] uppercase tracking-wider">
                  {category.name}
                </div>
                <div className="grid grid-cols-3 gap-2">
                  {categorySteps.map((step) => {
                    const status = getStepStatus(step.id);
                    const isClickable = status === 'completed' || step.id === currentStep;

                    return (
                      <button
                        key={step.id}
                        onClick={() => isClickable && handleStepClick(step.id)}
                        disabled={!isClickable}
                        className={cn(
                          "relative p-2 rounded border transition-all duration-200 text-left",
                          getStepColor(step.id),
                          isClickable && "cursor-pointer hover:shadow-sm",
                          !isClickable && "cursor-not-allowed opacity-60"
                        )}
                      >
                        {/* Blueprint corner mark */}
                        <div className="absolute -top-px -left-px w-1 h-1 border-t border-l border-current opacity-40" />

                        <div className="flex items-center gap-2">
                          <div className={cn(
                            "w-4 h-4 rounded-full border-2 flex items-center justify-center text-xs font-technical",
                            status === 'completed' && "bg-white text-[var(--blueprint)] border-[var(--blueprint)]",
                            status === 'current' && "bg-[var(--blueprint)] text-white border-[var(--blueprint)]",
                            status === 'upcoming' && "bg-[var(--paper)] border-[var(--border)]"
                          )}>
                            {status === 'completed' ? '✓' : step.id}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="text-xs font-medium truncate">{step.title}</div>
                            <div className="text-xs text-[var(--muted)] truncate opacity-70">
                              {step.description}
                            </div>
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Quick navigation */}
      <div className="flex justify-between items-center pt-2 border-t border-[var(--border)]">
        <button
          onClick={() => currentStep > 1 && handleStepClick(currentStep - 1)}
          disabled={currentStep <= 1}
          className="px-3 py-1 text-sm font-technical text-[var(--muted)] hover:text-[var(--ink)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          ← Previous
        </button>

        <div className="flex gap-1">
          {[1, 5, 10, 15, 20, 23].map((milestone) => (
            <button
              key={milestone}
              onClick={() => handleStepClick(milestone)}
              className={cn(
                "w-6 h-6 rounded text-xs font-technical transition-colors",
                milestone <= currentStep
                  ? "bg-[var(--blueprint)] text-white"
                  : "bg-[var(--paper)] text-[var(--muted)] border border-[var(--border)]"
              )}
            >
              {milestone}
            </button>
          ))}
        </div>

        <button
          onClick={() => currentStep < totalSteps && handleStepClick(currentStep + 1)}
          disabled={currentStep >= totalSteps}
          className="px-3 py-1 text-sm font-technical text-[var(--muted)] hover:text-[var(--ink)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Next →
        </button>
      </div>
    </div>
  );
}
