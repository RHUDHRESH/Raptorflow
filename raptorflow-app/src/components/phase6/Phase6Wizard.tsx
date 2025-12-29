'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import {
  Phase6Data,
  Phase5Data,
  emptyPhase6,
  loadFoundationDB,
  saveFoundation,
  FoundationData,
  VoCPhrase,
  SB7Spine,
  AwarenessStageContent,
  Signal7Soundbite,
  ProofSlot,
  VoiceSpec,
  WebsiteHeroPack,
  ChannelAsset,
  ToneRisk,
} from '@/lib/foundation';
import { forgePhase6, regenerateSignal7Soundbite } from '@/lib/phase6-forge';
import { PhaseScreen, PhaseStep } from '@/components/phase-shared';
import { Button } from '@/components/ui/button';
import { AlertCircle, ArrowRight, Sparkles, Check } from 'lucide-react';
import { toast } from 'sonner';
import gsap from 'gsap';

// Screen components
import {
  MessagingFactoryLanding,
  VoCExtractor,
  SB7NarrativeSpine,
  AwarenessLadderTuner,
  PrecisionSoundbites,
  ProofBinding,
  ToneLexiconCadence,
  AssetPackaging,
  ClarityDiffTests,
  FinalMessagingKit,
} from './screens';

type Phase6Screen =
  | 'landing'
  | 'voc'
  | 'sb7'
  | 'awareness'
  | 'soundbites'
  | 'proof'
  | 'voice'
  | 'assets'
  | 'qa'
  | 'kit';

const STEPS: PhaseStep[] = [
  { id: 'landing', label: 'Setup' },
  { id: 'voc', label: 'VoC' },
  { id: 'sb7', label: 'Narrative' },
  { id: 'awareness', label: 'Awareness' },
  { id: 'soundbites', label: 'Soundbites' },
  { id: 'proof', label: 'Proof' },
  { id: 'voice', label: 'Voice' },
  { id: 'assets', label: 'Assets' },
  { id: 'qa', label: 'QA' },
  { id: 'kit', label: 'Kit' },
];

const SCREEN_CONTENT: Record<
  Phase6Screen,
  { title: string; subtitle: string }
> = {
  landing: {
    title: 'Messaging Factory',
    subtitle: 'Generate your complete Messaging Kit from ICP + Positioning.',
  },
  voc: {
    title: 'Voice of Customer',
    subtitle: 'Stop sounding like a founder. Start sounding like your buyer.',
  },
  sb7: {
    title: 'Brand Narrative',
    subtitle: 'Your story, structured. Customer as hero, you as guide.',
  },
  awareness: {
    title: 'Awareness Ladder',
    subtitle:
      'Same product, different mental states. Tune your message per stage.',
  },
  soundbites: {
    title: '7 Precision Soundbites',
    subtitle: 'SIGNAL-7: The deployable lines that do the heavy lifting.',
  },
  proof: {
    title: 'Proof Binding',
    subtitle: 'No proof = weak message. Attach evidence to every claim.',
  },
  voice: {
    title: 'Tone & Lexicon',
    subtitle: 'This is how you stop sounding generic.',
  },
  assets: {
    title: 'Asset Packaging',
    subtitle: 'Turn soundbites into paste-ready channel assets.',
  },
  qa: {
    title: 'Clarity Tests',
    subtitle: 'Auto QA to avoid shipping mush.',
  },
  kit: {
    title: 'Your Messaging Kit',
    subtitle: 'Lock it. Export it. Deploy it everywhere.',
  },
};

export function Phase6Wizard() {
  const router = useRouter();
  const confettiRef = useRef<HTMLDivElement>(null);
  const [foundation, setFoundation] = useState<FoundationData | null>(null);
  const [phase5, setPhase5] = useState<Phase5Data | null>(null);
  const [phase6, setPhase6] = useState<Phase6Data>(emptyPhase6);
  const [currentScreen, setCurrentScreen] = useState<Phase6Screen>('landing');
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await loadFoundationDB();
        setFoundation(data);

        if (data.phase5) {
          setPhase5(data.phase5);

          if (
            data.phase6 &&
            data.phase6.signal7Soundbites &&
            data.phase6.signal7Soundbites.length > 0
          ) {
            // Use existing Phase 6 data
            setPhase6(data.phase6);
          } else {
            // Forge new Phase 6 from Phase 5
            setIsProcessing(true);
            const forged = await forgePhase6(data.phase5, 'balanced');
            setPhase6(forged);
            setIsProcessing(false);
          }
        }

        setIsLoading(false);
      } catch (error) {
        console.error('Error loading foundation:', error);
        toast.error('Failed to load data');
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  // Save phase 6 data
  const savePhase6 = useCallback(
    async (data: Phase6Data) => {
      if (!foundation) return;
      try {
        const updated = { ...foundation, phase6: data };
        await saveFoundation(updated);
        setFoundation(updated);
      } catch (error) {
        console.error('Error saving phase6:', error);
      }
    },
    [foundation]
  );

  // Update phase6 and save
  const updatePhase6 = useCallback(
    (updates: Partial<Phase6Data>) => {
      const updated = { ...phase6, ...updates };
      setPhase6(updated);
      savePhase6(updated);
    },
    [phase6, savePhase6]
  );

  const currentIndex = STEPS.findIndex((s) => s.id === currentScreen);

  const goNext = useCallback(() => {
    if (currentIndex < STEPS.length - 1) {
      setCurrentScreen(STEPS[currentIndex + 1].id as Phase6Screen);
      savePhase6(phase6);
    }
  }, [currentIndex, phase6, savePhase6]);

  const goBack = useCallback(() => {
    if (currentIndex > 0) {
      setCurrentScreen(STEPS[currentIndex - 1].id as Phase6Screen);
    } else {
      router.push('/foundation/phase5');
    }
  }, [currentIndex, router]);

  const handleStepClick = useCallback(
    (stepId: string) => {
      const stepIndex = STEPS.findIndex((s) => s.id === stepId);
      if (stepIndex <= currentIndex) {
        setCurrentScreen(stepId as Phase6Screen);
      }
    },
    [currentIndex]
  );

  // Handler functions for screen components
  const handleToneChange = useCallback(
    (tone: ToneRisk) => {
      updatePhase6({ toneRisk: tone });
    },
    [updatePhase6]
  );

  const handleVoCUpdate = useCallback(
    (phrases: VoCPhrase[]) => {
      updatePhase6({ vocPhrases: phrases });
    },
    [updatePhase6]
  );

  const handleSB7Update = useCallback(
    (spine: SB7Spine) => {
      updatePhase6({ sb7Spine: spine });
    },
    [updatePhase6]
  );

  const handleLadderUpdate = useCallback(
    (ladder: AwarenessStageContent[]) => {
      updatePhase6({ awarenessLadder: ladder });
    },
    [updatePhase6]
  );

  const handleSoundbiteRegenerate = useCallback(
    (id: string, punchLevel: number) => {
      if (!phase5) return;
      const soundbite = phase6.signal7Soundbites?.find((s) => s.id === id);
      if (!soundbite) return;

      const regenerated = regenerateSignal7Soundbite(
        soundbite,
        phase5,
        punchLevel
      );
      const updated =
        phase6.signal7Soundbites?.map((s) => (s.id === id ? regenerated : s)) ||
        [];
      updatePhase6({ signal7Soundbites: updated });
      toast.success('Soundbite regenerated');
    },
    [phase5, phase6.signal7Soundbites, updatePhase6]
  );

  const handleSoundbiteUpdate = useCallback(
    (soundbites: Signal7Soundbite[]) => {
      updatePhase6({ signal7Soundbites: soundbites });
    },
    [updatePhase6]
  );

  const handleProofUpdate = useCallback(
    (slots: ProofSlot[]) => {
      updatePhase6({ proofSlots: slots });
    },
    [updatePhase6]
  );

  const handleVoiceUpdate = useCallback(
    (spec: VoiceSpec) => {
      updatePhase6({ voiceSpec: spec });
    },
    [updatePhase6]
  );

  const handleHeroUpdate = useCallback(
    (hero: WebsiteHeroPack) => {
      updatePhase6({ websiteHero: hero });
    },
    [updatePhase6]
  );

  const handleAssetsUpdate = useCallback(
    (assets: ChannelAsset[]) => {
      updatePhase6({ channelAssets: assets });
    },
    [updatePhase6]
  );

  const handleRequestRewrite = useCallback(
    (soundbiteId: string) => {
      toast.info('Rewrite requested - regenerating...');
      handleSoundbiteRegenerate(soundbiteId, 3);
    },
    [handleSoundbiteRegenerate]
  );

  const handleAcceptFix = useCallback((type: 'fluffy' | 'differentiation') => {
    toast.success('Fix applied');
  }, []);

  const handleLock = useCallback(async () => {
    const lockedData = { ...phase6, lockedAt: new Date().toISOString() };
    setPhase6(lockedData);
    await savePhase6(lockedData);
    toast.success('🎉 Messaging Kit locked!');
    router.push('/foundation/results');
  }, [phase6, savePhase6, router]);

  const handleExportJSON = useCallback(() => {
    const blob = new Blob([JSON.stringify(phase6, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'messaging-kit.json';
    a.click();
    URL.revokeObjectURL(url);
    toast.success('JSON exported');
  }, [phase6]);

  const handleExportPDF = useCallback(() => {
    toast.info('PDF export coming soon');
  }, []);

  // Loading state
  if (isLoading || isProcessing) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F3F4EE]">
        <div className="text-center space-y-6">
          <div className="w-16 h-16 border-[3px] border-[#2D3538] border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="font-serif text-2xl text-[#2D3538]">
            {isProcessing ? 'Forging your Messaging Kit...' : 'Loading...'}
          </p>
        </div>
      </div>
    );
  }

  // No Phase 5 data
  if (!phase5) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F3F4EE]">
        <div className="text-center space-y-8 max-w-md px-8">
          <AlertCircle className="w-12 h-12 text-[#2D3538] mx-auto" />
          <h1 className="font-serif text-3xl text-[#2D3538]">
            Complete Phase 5 First
          </h1>
          <p className="text-[#5B5F61]">
            Your ICP data is needed to generate messaging. Complete Phase 5 to
            continue.
          </p>
          <Button
            onClick={() => router.push('/foundation/phase5')}
            className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-10 py-6 rounded-2xl"
          >
            Go to Phase 5
          </Button>
        </div>
      </div>
    );
  }

  const { title, subtitle } = SCREEN_CONTENT[currentScreen];

  return (
    <PhaseScreen
      phaseNumber={6}
      phaseTitle="Messaging Factory"
      currentStepId={currentScreen}
      steps={STEPS}
      title={title}
      subtitle={subtitle}
      onBack={goBack}
      onStepClick={handleStepClick}
      showContinue={currentScreen !== 'kit'}
      continueText={
        currentIndex === STEPS.length - 2 ? 'Review Kit' : 'Continue'
      }
      onContinue={goNext}
    >
      {/* Screen 6.0: Landing */}
      {currentScreen === 'landing' && (
        <MessagingFactoryLanding
          phase5={phase5}
          phase6={phase6}
          onToneChange={handleToneChange}
          onConfirm={goNext}
        />
      )}

      {/* Screen 6.1: VoC */}
      {currentScreen === 'voc' && (
        <VoCExtractor phase6={phase6} onUpdatePhrases={handleVoCUpdate} />
      )}

      {/* Screen 6.2: SB7 Narrative */}
      {currentScreen === 'sb7' && (
        <SB7NarrativeSpine
          sb7Spine={phase6.sb7Spine}
          onUpdate={handleSB7Update}
        />
      )}

      {/* Screen 6.3: Awareness Ladder */}
      {currentScreen === 'awareness' && (
        <AwarenessLadderTuner
          ladder={phase6.awarenessLadder || []}
          onUpdate={handleLadderUpdate}
        />
      )}

      {/* Screen 6.4: Soundbites */}
      {currentScreen === 'soundbites' && (
        <PrecisionSoundbites
          soundbites={phase6.signal7Soundbites || []}
          onRegenerate={handleSoundbiteRegenerate}
          onUpdate={handleSoundbiteUpdate}
        />
      )}

      {/* Screen 6.5: Proof Binding */}
      {currentScreen === 'proof' && (
        <ProofBinding
          proofSlots={phase6.proofSlots || []}
          soundbites={phase6.signal7Soundbites || []}
          onUpdate={handleProofUpdate}
        />
      )}

      {/* Screen 6.6: Voice */}
      {currentScreen === 'voice' && (
        <ToneLexiconCadence
          voiceSpec={phase6.voiceSpec}
          onUpdate={handleVoiceUpdate}
        />
      )}

      {/* Screen 6.7: Assets */}
      {currentScreen === 'assets' && (
        <AssetPackaging
          websiteHero={phase6.websiteHero}
          adAngles={phase6.adAngles || []}
          channelAssets={phase6.channelAssets || []}
          soundbites={phase6.signal7Soundbites || []}
          onUpdateHero={handleHeroUpdate}
          onUpdateAssets={handleAssetsUpdate}
        />
      )}

      {/* Screen 6.8: QA */}
      {currentScreen === 'qa' && (
        <ClarityDiffTests
          qaReport={phase6.qaReport}
          soundbites={phase6.signal7Soundbites || []}
          onRequestRewrite={handleRequestRewrite}
          onAcceptFix={handleAcceptFix}
        />
      )}

      {/* Screen 6.9: Final Kit */}
      {currentScreen === 'kit' && (
        <FinalMessagingKit
          phase6={phase6}
          onLock={handleLock}
          onExportJSON={handleExportJSON}
          onExportPDF={handleExportPDF}
        />
      )}
    </PhaseScreen>
  );
}
