'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
  Phase3Data,
  FoundationData,
  emptyPhase3,
  loadFoundationDB,
  saveFoundation,
  JTBDForces,
  VPCData,
  ProofArtifact,
  UVPDraft,
  USPDraft,
  OfferProfile,
  IntakeSummaryItem,
  Phase3Session,
} from '@/lib/foundation';
import {
  derivePhase3,
  derivePhase3FromQuestionnaire,
} from '@/lib/phase3-derivation';
import { PhaseScreen, PhaseStep } from '@/components/phase-shared';
import { toast } from 'sonner';
import { v4 as uuidv4 } from 'uuid';

// Import all screen components
import { ValueLabLanding } from './ValueLabLanding';
import { IntakeSummary } from './IntakeSummary';
import { CustomerProgress } from './CustomerProgress';
import { VPCCustomerProfile } from './VPCCustomerProfile';
import { VPCSolutionMap } from './VPCSolutionMap';
import { ProofStackScreen } from './ProofStackScreen';
import { StrategyCanvasScreen } from './StrategyCanvasScreen';
import { ERRCGridScreen } from './ERRCGridScreen';
import { UVPUSPDrafts } from './UVPUSPDrafts';
import { OfferPackaging } from './OfferPackaging';
import { Phase3Review } from './Phase3Review';

// All Phase 3 screens
type Phase3Screen =
  | 'landing'
  | 'intake'
  | 'jtbd'
  | 'vpc-customer'
  | 'vpc-solution'
  | 'proof'
  | 'canvas'
  | 'errc'
  | 'claims'
  | 'offer'
  | 'review';

const STEPS: PhaseStep[] = [
  { id: 'intake', label: 'Review Inputs' },
  { id: 'jtbd', label: 'Customer Goal' },
  { id: 'vpc-customer', label: 'Their World' },
  { id: 'vpc-solution', label: 'Your Solution' },
  { id: 'proof', label: 'Proof Library' },
  { id: 'canvas', label: 'Competitive Edge' },
  { id: 'errc', label: 'Strategic Moves' },
  { id: 'claims', label: 'Your Claims' },
  { id: 'offer', label: 'How You Deliver' },
  { id: 'review', label: 'Lock & Continue' },
];

const SCREEN_CONTENT: Record<
  Phase3Screen,
  { title: string; subtitle: string }
> = {
  landing: {
    title: 'Value Lab',
    subtitle:
      'Turn everything you told us into a clear, defendable value proposition.',
  },
  intake: {
    title: 'Quick Review',
    subtitle:
      "Here's what we extracted. Fix anything that's wrong, then continue.",
  },
  jtbd: {
    title: 'What Are They Trying to Achieve?',
    subtitle: 'Define the core goal your customer is trying to accomplish.',
  },
  'vpc-customer': {
    title: 'Step Into Their Shoes',
    subtitle:
      'What jobs are they doing? What frustrates them? What would delight them?',
  },
  'vpc-solution': {
    title: 'How You Help',
    subtitle: 'Connect your features to their pains and desired outcomes.',
  },
  proof: {
    title: 'What Can You Actually Prove?',
    subtitle: 'Add evidence for your claims. No proof = no claim.',
  },
  canvas: {
    title: 'Where You Win',
    subtitle: 'Plot your value against competitors. Where do you stand out?',
  },
  errc: {
    title: 'Make Strategic Choices',
    subtitle: 'What to eliminate, reduce, raise, or create to stand apart?',
  },
  claims: {
    title: 'Your Value Propositions',
    subtitle: 'We drafted these from your inputs. Pick the best ones.',
  },
  offer: {
    title: 'How You Deliver Value',
    subtitle:
      'DIY, done-with-you, or done-for-you? How fast do they see results?',
  },
  review: {
    title: 'Ready to Lock?',
    subtitle: 'Review your Value Pack and lock it to move to positioning.',
  },
};

// Generate intake summary from foundation data
function generateIntakeSummary(
  foundation: FoundationData
): IntakeSummaryItem[] {
  const items: IntakeSummaryItem[] = [];
  const phase1 = foundation.phase1;

  if (phase1?.identity) {
    items.push({
      id: uuidv4(),
      section: 'company',
      label: 'Company',
      text: `${phase1.identity.company || 'Your Company'}`,
      sourceConfidence: 'high',
      isAssumption: false,
      sourceQuotes: [],
    });
  }

  if (phase1?.offer) {
    items.push({
      id: uuidv4(),
      section: 'company',
      label: 'Offer Type',
      text: phase1.offer.primaryType || 'Solution',
      sourceConfidence: 'high',
      isAssumption: false,
      sourceQuotes: [],
    });
  }

  if (phase1?.buyerUser?.userRoles) {
    items.push({
      id: uuidv4(),
      section: 'company',
      label: 'Target Audience',
      text: phase1.buyerUser.userRoles.join(', ') || 'Business leaders',
      sourceConfidence: 'medium',
      isAssumption: false,
      sourceQuotes: [],
    });
  }

  if (phase1?.triggers?.triggers) {
    phase1.triggers.triggers.forEach((t, i) => {
      items.push({
        id: uuidv4(),
        section: 'pains',
        label: `Trigger ${i + 1}`,
        text: t.freeText || t.type || 'Growth challenge',
        sourceConfidence: 'medium',
        isAssumption: false,
        sourceQuotes: [],
      });
    });
  }

  if (phase1?.currentSystem?.artifacts) {
    items.push({
      id: uuidv4(),
      section: 'stack',
      label: 'Current Tools',
      text: phase1.currentSystem.artifacts.join(', ') || 'Various tools',
      sourceConfidence: 'high',
      isAssumption: false,
      sourceQuotes: [],
    });
  }

  if (phase1?.proofGuardrails?.forbiddenClaims) {
    phase1.proofGuardrails.forbiddenClaims.forEach((claim, i) => {
      items.push({
        id: uuidv4(),
        section: 'constraints',
        label: `Forbidden ${i + 1}`,
        text: claim,
        sourceConfidence: 'high',
        isAssumption: false,
        sourceQuotes: [],
      });
    });
  }

  return items;
}

// Generate default UVP drafts
function generateDefaultUVPDrafts(phase3: Phase3Data): UVPDraft[] {
  const primaryJob =
    phase3.jtbd?.jobs?.find((j) => j.isPrimary)?.statement ||
    'achieve their goals';
  const topPain =
    phase3.vpc?.customerProfile?.pains?.[0]?.text || 'common frustrations';
  const topGain =
    phase3.vpc?.customerProfile?.gains?.[0]?.text || 'desired outcomes';

  return [
    {
      id: uuidv4(),
      text: `Help you ${primaryJob} without ${topPain}.`,
      topJobId: phase3.jtbd?.jobs?.[0]?.id,
      topPainId: phase3.vpc?.customerProfile?.pains?.[0]?.id,
      proofAttached: false,
      differentiationScore: 65,
      clarityScore: 70,
      isPrimary: true,
    },
    {
      id: uuidv4(),
      text: `The fastest way to ${topGain} for busy founders.`,
      topGainId: phase3.vpc?.customerProfile?.gains?.[0]?.id,
      proofAttached: false,
      differentiationScore: 55,
      clarityScore: 80,
      isPrimary: false,
    },
    {
      id: uuidv4(),
      text: `Finally ${primaryJob} with a system that actually works.`,
      topJobId: phase3.jtbd?.jobs?.[0]?.id,
      proofAttached: false,
      differentiationScore: 50,
      clarityScore: 75,
      isPrimary: false,
    },
  ];
}

// Generate default USP drafts
function generateDefaultUSPDrafts(phase3: Phase3Data): USPDraft[] {
  const mechanism = phase3.primaryContext?.youSell || 'our unique approach';
  const errcCreate =
    phase3.errc?.create?.[0]?.factor || 'innovative capability';

  return [
    {
      id: uuidv4(),
      text: `The only ${mechanism} that delivers ${errcCreate}.`,
      specificBenefit: errcCreate,
      uniquenessVsAlternatives: 'First to market',
      proofAttached: false,
      isSpecific: true,
      isUnique: true,
      movesBuyers: true,
      isPrimary: true,
    },
    {
      id: uuidv4(),
      text: `Unlike alternatives, we focus 100% on ${errcCreate}.`,
      specificBenefit: errcCreate,
      uniquenessVsAlternatives: 'Focus differentiator',
      proofAttached: false,
      isSpecific: true,
      isUnique: true,
      movesBuyers: false,
      isPrimary: false,
    },
    {
      id: uuidv4(),
      text: `Built for founders who won't settle for generic solutions.`,
      specificBenefit: 'Founder-focused',
      uniquenessVsAlternatives: 'Audience focus',
      proofAttached: false,
      isSpecific: false,
      isUnique: true,
      movesBuyers: true,
      isPrimary: false,
    },
  ];
}

export function Phase3Wizard() {
  const router = useRouter();
  const [foundation, setFoundation] = useState<FoundationData | null>(null);
  const [phase3, setPhase3] = useState<Phase3Data>(emptyPhase3);
  const [currentScreen, setCurrentScreen] = useState<Phase3Screen>('landing');
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);

  // Load data on mount
  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await loadFoundationDB();
        setFoundation(data);

        if (data.phase3 && data.phase3.jtbd?.jobs?.length > 0) {
          // Use existing Phase 3 data
          setPhase3(data.phase3);
        } else if (data.completedAt || data.phase1) {
          // Derive from Phase 1/2
          setIsProcessing(true);
          const derived = data.phase1
            ? await derivePhase3(data.phase1)
            : await derivePhase3FromQuestionnaire(data);

          // Add session and intake summary
          const session: Phase3Session = {
            id: uuidv4(),
            startedAt: new Date().toISOString(),
            inputsLocked: false,
          };

          const intakeSummary = generateIntakeSummary(data);

          setPhase3({
            ...derived,
            session,
            intakeSummary,
            proofArtifacts: [],
            uvpDrafts: generateDefaultUVPDrafts(derived),
            uspDrafts: generateDefaultUSPDrafts(derived),
            mechanismLine: '',
          });
          setIsProcessing(false);
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

  // Auto-save phase3 data
  const savePhase3 = useCallback(
    async (data: Phase3Data) => {
      if (!foundation) return;
      try {
        await saveFoundation({ ...foundation, phase3: data });
      } catch (error) {
        console.error('Error saving phase3:', error);
      }
    },
    [foundation]
  );

  // Navigation helpers
  const screenOrder: Phase3Screen[] = [
    'landing',
    'intake',
    'jtbd',
    'vpc-customer',
    'vpc-solution',
    'proof',
    'canvas',
    'errc',
    'claims',
    'offer',
    'review',
  ];

  const currentIndex = screenOrder.indexOf(currentScreen);

  const goNext = () => {
    if (currentIndex < screenOrder.length - 1) {
      setCurrentScreen(screenOrder[currentIndex + 1]);
      savePhase3(phase3);
    }
  };

  const goBack = () => {
    if (currentIndex > 0) {
      setCurrentScreen(screenOrder[currentIndex - 1]);
    } else {
      router.push('/foundation');
    }
  };

  const handleStepClick = (stepId: string) => {
    const stepIndex = screenOrder.indexOf(stepId as Phase3Screen);
    if (stepIndex >= 0 && stepIndex <= currentIndex) {
      setCurrentScreen(stepId as Phase3Screen);
    }
  };

  const handleLock = async () => {
    const lockedData = { ...phase3, lockedAt: new Date().toISOString() };
    setPhase3(lockedData);
    await savePhase3(lockedData);
    toast.success('Phase 3 locked!');
    router.push('/foundation/phase4');
  };

  // Loading states
  if (isLoading || isProcessing) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F3F4EE]">
        <div className="text-center space-y-6">
          <div className="w-16 h-16 border-[3px] border-[#2D3538] border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="font-serif text-2xl text-[#2D3538]">
            {isProcessing ? 'Deriving value proposition...' : 'Loading...'}
          </p>
        </div>
      </div>
    );
  }

  // Show landing screen
  if (currentScreen === 'landing') {
    return (
      <ValueLabLanding
        onStart={() => setCurrentScreen('intake')}
        evidenceSnippets={[]}
        completedSteps={[]}
      />
    );
  }

  const { title, subtitle } = SCREEN_CONTENT[currentScreen];
  const stepIndex = STEPS.findIndex((s) => s.id === currentScreen);

  return (
    <PhaseScreen
      phaseNumber={3}
      phaseTitle="Value & Offer"
      currentStepId={currentScreen}
      steps={STEPS}
      title={title}
      subtitle={subtitle}
      onBack={goBack}
      onStepClick={handleStepClick}
      showContinue={false}
    >
      {/* Screen: Intake Summary */}
      {currentScreen === 'intake' && (
        <IntakeSummary
          items={phase3.intakeSummary || []}
          onItemEdit={(id, text) => {
            setPhase3({
              ...phase3,
              intakeSummary:
                phase3.intakeSummary?.map((item) =>
                  item.id === id ? { ...item, text } : item
                ) || [],
            });
          }}
          onToggleAssumption={(id) => {
            setPhase3({
              ...phase3,
              intakeSummary:
                phase3.intakeSummary?.map((item) =>
                  item.id === id
                    ? { ...item, isAssumption: !item.isAssumption }
                    : item
                ) || [],
            });
          }}
          onConfirm={goNext}
          onBack={goBack}
        />
      )}

      {/* Screen: Customer Progress (JTBD) */}
      {currentScreen === 'jtbd' && (
        <CustomerProgress
          jtbd={phase3.jtbd}
          onUpdate={(jtbd) => setPhase3({ ...phase3, jtbd })}
          onContinue={goNext}
          onBack={goBack}
        />
      )}

      {/* Screen: VPC Customer Profile */}
      {currentScreen === 'vpc-customer' && (
        <VPCCustomerProfile
          vpc={phase3.vpc}
          onUpdate={(vpc) => setPhase3({ ...phase3, vpc })}
          onContinue={goNext}
          onBack={goBack}
        />
      )}

      {/* Screen: VPC Solution Map */}
      {currentScreen === 'vpc-solution' && (
        <VPCSolutionMap
          vpc={phase3.vpc}
          proofArtifacts={phase3.proofArtifacts}
          onUpdate={(vpc) => setPhase3({ ...phase3, vpc })}
          onContinue={goNext}
          onBack={goBack}
        />
      )}

      {/* Screen: Proof Stack */}
      {currentScreen === 'proof' && (
        <ProofStackScreen
          proofArtifacts={phase3.proofArtifacts || []}
          onUpdate={(artifacts) =>
            setPhase3({ ...phase3, proofArtifacts: artifacts })
          }
          onContinue={goNext}
          onBack={goBack}
        />
      )}

      {/* Screen: Strategy Canvas */}
      {currentScreen === 'canvas' && (
        <StrategyCanvasScreen
          canvas={phase3.strategyCanvas}
          onChange={(canvas) =>
            setPhase3({ ...phase3, strategyCanvas: canvas })
          }
          onContinue={goNext}
        />
      )}

      {/* Screen: ERRC Grid */}
      {currentScreen === 'errc' && (
        <ERRCGridScreen
          errc={phase3.errc}
          onChange={(errc) => setPhase3({ ...phase3, errc })}
          onContinue={goNext}
        />
      )}

      {/* Screen: UVP/USP Drafts */}
      {currentScreen === 'claims' && (
        <UVPUSPDrafts
          uvpDrafts={phase3.uvpDrafts || []}
          uspDrafts={phase3.uspDrafts || []}
          mechanismLine={phase3.mechanismLine || ''}
          onUpdateUVP={(drafts) => setPhase3({ ...phase3, uvpDrafts: drafts })}
          onUpdateUSP={(drafts) => setPhase3({ ...phase3, uspDrafts: drafts })}
          onUpdateMechanism={(line) =>
            setPhase3({ ...phase3, mechanismLine: line })
          }
          onRegenerate={(type, broader) => {
            // Regeneration logic - could call AI here
            toast.info(`Regenerating ${type}...`);
          }}
          onContinue={goNext}
          onBack={goBack}
        />
      )}

      {/* Screen: Offer Packaging */}
      {currentScreen === 'offer' && (
        <OfferPackaging
          offerProfile={phase3.offerProfile}
          onUpdate={(profile) =>
            setPhase3({ ...phase3, offerProfile: profile })
          }
          onContinue={goNext}
          onBack={goBack}
        />
      )}

      {/* Screen: Review & Lock */}
      {currentScreen === 'review' && (
        <Phase3Review phase3={phase3} onLock={handleLock} onBack={goBack} />
      )}
    </PhaseScreen>
  );
}
