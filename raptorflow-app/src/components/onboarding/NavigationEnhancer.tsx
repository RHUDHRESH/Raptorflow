import React, { useState, useEffect } from 'react';
import { ArrowLeft, ArrowRight, Save, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

interface NavigationEnhancerProps {
  currentPhase: string;
  completedPhases: string[];
  availablePhases: string[];
  onNavigate: (phase: string) => void;
  onSave: () => void;
  onRefresh: () => void;
  isLoading?: boolean;
}

export function NavigationEnhancer({
  currentPhase,
  completedPhases,
  availablePhases,
  onNavigate,
  onSave,
  onRefresh,
  isLoading = false,
}: NavigationEnhancerProps) {
  const [backEnabled, setBackEnabled] = useState(false);
  const [nextEnabled, setNextEnabled] = useState(false);
  const [canSave, setCanSave] = useState(false);

  useEffect(() => {
    // Enable back navigation if not on the first phase
    setBackEnabled(currentPhase !== 'icps');

    // Enable next navigation if current phase is completed
    setNextEnabled(completedPhases.includes(currentPhase));

    // Enable save if there's data to save
    setCanSave(completedPhases.length > 0);
  }, [currentPhase, completedPhases]);

  const handleBack = () => {
    const currentIndex = availablePhases.indexOf(currentPhase);
    if (currentIndex > 0) {
      const previousPhase = availablePhases[currentIndex - 1];
      onNavigate(previousPhase);
    }
  };

  const handleNext = () => {
    const currentIndex = availablePhases.indexOf(currentPhase);
    if (currentIndex < availablePhases.length - 1) {
      const nextPhase = availablePhases[currentIndex + 1];
      onNavigate(nextPhase);
    }
  };

  const handleSave = () => {
    onSave();
    toast.success('Progress saved successfully');
  };

  const handleRefresh = () => {
    onRefresh();
    toast.info('Refreshing data...');
  };

  const getPhaseName = (phase: string) => {
    const phaseNames: Record<string, string> = {
      icps: 'ICP Reveal',
      positioning: 'Positioning',
      competitors: 'Competitive Analysis',
      messaging: 'Messaging',
      market: 'Market Analysis',
    };
    return phaseNames[phase] || phase;
  };

  return (
    <div className="flex items-center justify-between p-4 border border-[#E5E6E3] bg-white rounded-xl">
      {/* Back Navigation */}
      <div className="flex items-center gap-3">
        <Button
          onClick={handleBack}
          disabled={!backEnabled || isLoading}
          variant="outline"
          size="sm"
          className="flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </Button>

        {/* Breadcrumb Trail */}
        <div className="flex items-center gap-2 text-sm text-[#9D9F9F">
          {availablePhases.map((phase, index) => (
            <React.Fragment key={phase}>
              <span
                className={`cursor-pointer transition-colors ${
                  phase === currentPhase
                    ? 'text-[#2D3538] font-medium'
                    : completedPhases.includes(phase)
                      ? 'text-[#5B5F61] hover:text-[#2D3538]'
                      : 'text-[#C0C1BE] cursor-not-allowed'
                }`}
                onClick={() =>
                  completedPhases.includes(phase) && onNavigate(phase)
                }
              >
                {getPhaseName(phase)}
              </span>
              {index < availablePhases.length - 1 && (
                <span className="text-[#C0C1BE]">/</span>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-3">
        {/* Save Button */}
        <Button
          onClick={handleSave}
          disabled={!canSave || isLoading}
          variant="outline"
          size="sm"
          className="flex items-center gap-2"
        >
          <Save className="w-4 h-4" />
          Save Progress
        </Button>

        {/* Refresh Button */}
        <Button
          onClick={handleRefresh}
          disabled={isLoading}
          variant="outline"
          size="sm"
          className="flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>

        {/* Next Navigation */}
        <Button
          onClick={handleNext}
          disabled={!nextEnabled || isLoading}
          className="flex items-center gap-2 bg-[#2D3538] hover:bg-[#1A1D1E]"
          size="sm"
        >
          Next
          <ArrowRight className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}

// Hook for managing navigation state
export function useNavigationState(initialPhase: string = 'icps') {
  const [currentPhase, setCurrentPhase] = useState(initialPhase);
  const [completedPhases, setCompletedPhases] = useState<string[]>([]);
  const [availablePhases] = useState([
    'icps',
    'positioning',
    'competitors',
    'messaging',
    'market',
  ]);

  const navigateToPhase = (phase: string) => {
    if (completedPhases.includes(phase) || phase === currentPhase) {
      setCurrentPhase(phase);
    }
  };

  const markPhaseCompleted = (phase: string) => {
    setCompletedPhases((prev) =>
      prev.includes(phase) ? prev : [...prev, phase]
    );
  };

  const resetProgress = () => {
    setCompletedPhases([]);
    setCurrentPhase('icps');
  };

  return {
    currentPhase,
    completedPhases,
    availablePhases,
    navigateToPhase,
    markPhaseCompleted,
    resetProgress,
  };
}
