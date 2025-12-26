import React, { useState, useEffect } from 'react';
import { NavigationEnhancer, useNavigationState } from './NavigationEnhancer';
import { ICPRevealScreen } from './ICPRevealScreen';
import { PositioningRevealScreen } from './PositioningRevealScreen';
import { toast } from 'sonner';

interface RevealScreenData {
  icps: any[];
  positioning: any;
  competitive: any;
  soundbites: any;
  market: any;
  differentiators: any;
  claims: any;
  blueprint: any;
  targetSegments: any;
  [key: string]: any; // Add index signature to allow dynamic access
}

interface EnhancedRevealFlowProps {
  initialData: RevealScreenData;
  onSynthesisComplete?: (data: RevealScreenData) => void;
  onSaveProgress?: (phase: string, data: any) => void;
}

export function EnhancedRevealFlow({
  initialData,
  onSynthesisComplete,
  onSaveProgress
}: EnhancedRevealFlowProps) {
  const navigation = useNavigationState('icps');
  const [data, setData] = useState<RevealScreenData>(initialData);
  const [isLoading, setIsLoading] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  // Track which phases have been viewed
  useEffect(() => {
    if (navigation.currentPhase && !navigation.completedPhases.includes(navigation.currentPhase)) {
      navigation.markPhaseCompleted(navigation.currentPhase);
    }
  }, [navigation.currentPhase]);

  const handleNavigate = (phase: string) => {
    if (hasUnsavedChanges) {
      // Auto-save before navigating
      handleSave();
    }
    navigation.navigateToPhase(phase);
  };

  const handleSave = async () => {
    setIsLoading(true);
    try {
      // Save current phase data
      if (onSaveProgress) {
        await onSaveProgress(navigation.currentPhase, data[navigation.currentPhase]);
      }

      // Save to localStorage as backup
      localStorage.setItem('raptorflow_reveal_progress', JSON.stringify({
        currentPhase: navigation.currentPhase,
        completedPhases: navigation.completedPhases,
        data: data,
        timestamp: new Date().toISOString()
      }));

      setHasUnsavedChanges(false);
      toast.success('Progress saved successfully');
    } catch (error) {
      toast.error('Failed to save progress');
      console.error('Save error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    setIsLoading(true);
    try {
      // Re-trigger synthesis for current phase
      const response = await fetch('/api/foundation/resynthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phase: navigation.currentPhase,
          foundationData: data
        })
      });

      if (response.ok) {
        const refreshedData = await response.json();
        setData(prev => ({
          ...prev,
          [navigation.currentPhase]: refreshedData
        }));
        setHasUnsavedChanges(true);
        toast.success('Data refreshed successfully');
      } else {
        throw new Error('Refresh failed');
      }
    } catch (error) {
      toast.error('Failed to refresh data');
      console.error('Refresh error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleContinue = () => {
    const currentIndex = navigation.availablePhases.indexOf(navigation.currentPhase);
    if (currentIndex < navigation.availablePhases.length - 1) {
      const nextPhase = navigation.availablePhases[currentIndex + 1];
      navigation.navigateToPhase(nextPhase);
    } else {
      // All phases completed
      if (onSynthesisComplete) {
        onSynthesisComplete(data);
      }
      toast.success('All phases completed successfully!');
    }
  };

  const renderCurrentPhase = () => {
    switch (navigation.currentPhase) {
      case 'icps':
        return (
          <ICPRevealScreen
            icps={data.icps || []}
            onContinue={handleContinue}
          />
        );

      case 'positioning':
        return (
          <PositioningRevealScreen
            positioning={data.positioning || {}}
            onContinue={handleContinue}
          />
        );

      case 'competitors':
        return (
          <CompetitiveRevealScreen
            competitive={data.competitive || {}}
            onContinue={handleContinue}
          />
        );

      case 'messaging':
        return (
          <MessagingRevealScreen
            soundbites={data.soundbites || []}
            blueprint={data.blueprint || {}}
            onContinue={handleContinue}
          />
        );

      case 'market':
        return (
          <MarketRevealScreen
            market={data.market || {}}
            targetSegments={data.targetSegments || []}
            onContinue={handleContinue}
          />
        );

      default:
        return <div>Phase not found</div>;
    }
  };

  return (
    <div className="min-h-screen bg-[#FAFAF8]">
      {/* Navigation Header */}
      <div className="sticky top-0 z-40 bg-white border-b border-[#E5E6E3]">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <NavigationEnhancer
            currentPhase={navigation.currentPhase}
            completedPhases={navigation.completedPhases}
            availablePhases={navigation.availablePhases}
            onNavigate={handleNavigate}
            onSave={handleSave}
            onRefresh={handleRefresh}
            isLoading={isLoading}
          />
        </div>
      </div>

      {/* Phase Content */}
      <div className="py-8">
        {renderCurrentPhase()}
      </div>

      {/* Unsaved Changes Warning */}
      {hasUnsavedChanges && (
        <div className="fixed bottom-4 right-4 bg-yellow-100 border border-yellow-400 text-yellow-800 px-4 py-2 rounded-lg shadow-lg">
          <p className="text-sm font-medium">You have unsaved changes</p>
          <button
            onClick={handleSave}
            className="mt-1 text-xs underline hover:no-underline"
          >
            Save now
          </button>
        </div>
      )}
    </div>
  );
}

// Placeholder components for other reveal screens
function CompetitiveRevealScreen({ competitive, onContinue }: any) {
  return (
    <div className="max-w-4xl mx-auto px-4">
      <h1 className="text-3xl font-bold mb-6">Competitive Analysis</h1>
      <div className="bg-white p-6 rounded-xl border border-[#E5E6E3]">
        <pre>{JSON.stringify(competitive, null, 2)}</pre>
        <button onClick={onContinue} className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg">
          Continue
        </button>
      </div>
    </div>
  );
}

function MessagingRevealScreen({ soundbites, blueprint, onContinue }: any) {
  return (
    <div className="max-w-4xl mx-auto px-4">
      <h1 className="text-3xl font-bold mb-6">Messaging & Soundbites</h1>
      <div className="bg-white p-6 rounded-xl border border-[#E5E6E3]">
        <pre>{JSON.stringify({ soundbites, blueprint }, null, 2)}</pre>
        <button onClick={onContinue} className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg">
          Continue
        </button>
      </div>
    </div>
  );
}

function MarketRevealScreen({ market, targetSegments, onContinue }: any) {
  return (
    <div className="max-w-4xl mx-auto px-4">
      <h1 className="text-3xl font-bold mb-6">Market Analysis</h1>
      <div className="bg-white p-6 rounded-xl border border-[#E5E6E3]">
        <pre>{JSON.stringify({ market, targetSegments }, null, 2)}</pre>
        <button onClick={onContinue} className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg">
          Continue
        </button>
      </div>
    </div>
  );
}
