/**
 * Tests for OnboardingProgressEnhanced Component
 */

import '@testing-library/jest-dom/vitest';
import { render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { OnboardingProgressEnhanced } from '../OnboardingProgressEnhanced';
import { useOnboardingStore } from '@/stores/onboardingStore';

vi.mock('@/stores/onboardingStore');

type StepStatus = 'pending' | 'in-progress' | 'complete' | 'blocked' | 'error';

interface StepState {
  id: number;
  status: StepStatus;
  data: Record<string, unknown>;
  savedAt: Date | null;
}

interface StoreMock {
  session: { sessionId: string; clientName?: string } | null;
  currentStep: number;
  steps: StepState[];
  saveStatus: 'saved' | 'saving' | 'error';
  lastSyncedAt: Date | null;
  getProgress: () => { completed: number; total: number; percentage: number };
  getStepById: (stepId: number) => StepState | undefined;
  canProceedToStep: (stepId: number) => boolean;
  setSaveStatus: ReturnType<typeof vi.fn>;
  setCurrentStep: ReturnType<typeof vi.fn>;
  updateStepStatus: ReturnType<typeof vi.fn>;
  updateStepData: ReturnType<typeof vi.fn>;
}

const buildStore = (overrides: Partial<StoreMock> = {}): StoreMock => {
  const steps =
    overrides.steps ?? ([
      { id: 1, status: 'complete', data: {}, savedAt: null },
      { id: 2, status: 'in-progress', data: {}, savedAt: null },
    ] satisfies StepState[]);

  return {
    session: overrides.session ?? { sessionId: 'session-1', clientName: 'Test Client' },
    currentStep: overrides.currentStep ?? steps[1]?.id ?? 1,
    steps,
    saveStatus: overrides.saveStatus ?? 'saved',
    lastSyncedAt: overrides.lastSyncedAt ?? new Date('2026-01-27T12:00:00Z'),
    getProgress: overrides.getProgress ?? (() => ({ completed: 4, total: 24, percentage: 17 })),
    getStepById: overrides.getStepById ?? ((stepId: number) => steps.find((step) => step.id === stepId)),
    canProceedToStep: overrides.canProceedToStep ?? ((stepId: number) => stepId <= (steps[1]?.id ?? 1)),
    setSaveStatus: overrides.setSaveStatus ?? vi.fn(),
    setCurrentStep: overrides.setCurrentStep ?? vi.fn(),
    updateStepStatus: overrides.updateStepStatus ?? vi.fn(),
    updateStepData: overrides.updateStepData ?? vi.fn(),
  };
};

const mockedUseStore = useOnboardingStore as unknown as ReturnType<typeof vi.fn>;

describe('OnboardingProgressEnhanced', () => {
  beforeEach(() => {
    mockedUseStore.mockReturnValue(buildStore());
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders compact summary', () => {
    const { getByText } = render(<OnboardingProgressEnhanced compact />);
    expect(getByText('Progress')).toBeInTheDocument();
    expect(getByText('17%')).toBeInTheDocument();
    expect(getByText('4 of 24 steps')).toBeInTheDocument();
  });

  it('shows detailed header with sync info', () => {
    const { getByText } = render(<OnboardingProgressEnhanced showDetails />);
    expect(getByText('Onboarding Progress')).toBeInTheDocument();
    expect(getByText('4 of 24 steps')).toBeInTheDocument();
    expect(getByText(/Last activity/)).toBeInTheDocument();
    expect(getByText(/Synced/)).toBeInTheDocument();
  });

  it('hides finalize button when progress is below threshold', () => {
    mockedUseStore.mockReturnValue(
      buildStore({ getProgress: () => ({ completed: 4, total: 24, percentage: 25 }) })
    );

    const { queryByText } = render(<OnboardingProgressEnhanced showDetails interactive />);
    expect(queryByText('Finalize')).not.toBeInTheDocument();
  });

  it('shows finalize button when progress is sufficient', () => {
    mockedUseStore.mockReturnValue(
      buildStore({ getProgress: () => ({ completed: 18, total: 24, percentage: 75 }) })
    );

    const { getByText } = render(<OnboardingProgressEnhanced showDetails interactive />);
    expect(getByText('Finalize')).toBeInTheDocument();
  });

  it('calls onStepClick when Continue Current Step is pressed', async () => {
    const handleStepClick = vi.fn();
    const targetStep = 2;
    mockedUseStore.mockReturnValue(
      buildStore({
        currentStep: targetStep,
        canProceedToStep: () => true,
      })
    );

    const user = userEvent.setup();
    const { getByText } = render(
      <OnboardingProgressEnhanced interactive onStepClick={handleStepClick} />
    );

    await user.click(getByText('Continue Current Step'));
    expect(handleStepClick).toHaveBeenCalledWith(targetStep);
  });
});
