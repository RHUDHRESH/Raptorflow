'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { v4 as uuidv4 } from 'uuid';
import {
  Phase5Data,
  FoundationData,
  CandidateSegment,
  ICP,
  TriggerSignal,
  ChannelHabitatItem,
  BeliefItem,
  ObjectionItem,
  NegativeICP,
  BuyingJobsCoverageCell,
  loadFoundationDB,
  saveFoundation,
  emptyPhase5,
} from '@/lib/foundation';
import { compilePhase5 } from '@/lib/phase5-compiler';
import { PhaseScreen, PhaseStep } from '@/components/phase-shared';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { Check, ArrowRight, Users, AlertCircle, Sparkles } from 'lucide-react';

// Screen Components
import { ICPEngineLanding } from './ICPEngineLanding';
import { ICPCandidateGenerator } from './ICPCandidateGenerator';
import { ICPDefinitionBuilder } from './ICPDefinitionBuilder';
import { JTBDStruggleMoments } from './JTBDStruggleMoments';
import { BuyingGroupMap } from './BuyingGroupMap';
import { BuyingJobsCoverage } from './BuyingJobsCoverage';
import { TriggerStack } from './TriggerStack';
import { ChannelHabitatMap } from './ChannelHabitatMap';
import { BeliefObjectionStack } from './BeliefObjectionStack';
import { NegativeICPBuilder } from './NegativeICPBuilder';
import { InterICPGraph } from './InterICPGraph';

type Phase5Screen =
  | 'landing'
  | 'candidates'
  | 'definition'
  | 'jtbd'
  | 'buying-group'
  | 'buying-jobs'
  | 'triggers'
  | 'channels'
  | 'beliefs'
  | 'negative'
  | 'graph'
  | 'complete';

const STEPS: PhaseStep[] = [
  { id: 'landing', label: 'Overview' },
  { id: 'candidates', label: 'Candidates' },
  { id: 'definition', label: 'ICP Definition' },
  { id: 'jtbd', label: 'JTBD' },
  { id: 'buying-group', label: 'Buying Group' },
  { id: 'buying-jobs', label: 'Buying Jobs' },
  { id: 'triggers', label: 'Triggers' },
  { id: 'channels', label: 'Channels' },
  { id: 'beliefs', label: 'Beliefs' },
  { id: 'negative', label: 'Negative ICP' },
  { id: 'graph', label: 'Graph' },
  { id: 'complete', label: 'Complete' },
];

const SCREEN_CONTENT: Record<
  Phase5Screen,
  { title: string; subtitle: string }
> = {
  landing: {
    title: 'ICP Engine',
    subtitle: 'Generate ideal customer profiles from your foundation data.',
  },
  candidates: {
    title: 'ICP Candidates',
    subtitle: 'Select your primary and secondary ICP targets.',
  },
  definition: {
    title: 'ICP Definition',
    subtitle: 'Firmographics, technographics, and operating model.',
  },
  jtbd: {
    title: 'Jobs-To-Be-Done',
    subtitle: 'Functional, emotional, and social jobs with struggle moments.',
  },
  'buying-group': {
    title: 'Buying Group',
    subtitle: 'Map the committee: roles, concerns, and proof needs.',
  },
  'buying-jobs': {
    title: 'Buying Jobs Coverage',
    subtitle: 'What each role must believe at each buying stage.',
  },
  triggers: {
    title: 'Trigger Stack',
    subtitle: 'Events that create urgency and how to detect them.',
  },
  channels: {
    title: 'Channel Habitat',
    subtitle: 'Where your ICP spends time and what content works.',
  },
  beliefs: {
    title: 'Beliefs & Objections',
    subtitle: 'What they must believe to buy, and what blocks them.',
  },
  negative: {
    title: 'Negative ICP',
    subtitle: 'Who to avoid — churn magnets and poor fits.',
  },
  graph: {
    title: 'ICP Relationships',
    subtitle: 'How ICPs connect: upgrade paths and influence networks.',
  },
  complete: {
    title: 'ICPs Complete',
    subtitle: 'Your ICP pack is ready to power messaging.',
  },
};

export function Phase5Wizard() {
  const router = useRouter();
  const [foundation, setFoundation] = useState<FoundationData | null>(null);
  const [phase5, setPhase5] = useState<Phase5Data>(emptyPhase5);
  const [currentScreen, setCurrentScreen] = useState<Phase5Screen>('landing');
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);

  // Session state
  const [businessType, setBusinessType] = useState<'b2b' | 'b2c' | 'hybrid'>(
    'b2b'
  );
  const [geoFocus, setGeoFocus] = useState<'india' | 'global' | 'mixed'>(
    'global'
  );
  const [primaryICPId, setPrimaryICPId] = useState<string | undefined>();
  const [secondaryICPIds, setSecondaryICPIds] = useState<string[]>([]);
  const [selectedICPIndex, setSelectedICPIndex] = useState(0);
  const [primaryJobType, setPrimaryJobType] = useState<
    'functional' | 'emotional' | 'social'
  >('functional');
  const [confirmedTriggerIds, setConfirmedTriggerIds] = useState<string[]>([]);

  // Load foundation data
  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await loadFoundationDB();
        setFoundation(data);

        if (data.phase5 && data.phase5.icps?.length > 0) {
          setPhase5(data.phase5);
          setPrimaryICPId(data.phase5.primaryICPId);
          setSecondaryICPIds(data.phase5.secondaryICPIds || []);
        } else if (data.phase4) {
          setIsProcessing(true);
          const compiled = await compilePhase5(data.phase4);
          setPhase5(compiled);
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

  // Save handler
  const savePhase5 = useCallback(
    async (data: Phase5Data) => {
      if (!foundation) return;
      try {
        await saveFoundation({ ...foundation, phase5: data });
      } catch (error) {
        console.error('Error saving phase5:', error);
      }
    },
    [foundation]
  );

  // Navigation
  const currentIndex = STEPS.findIndex((s) => s.id === currentScreen);
  const currentICP = phase5.icps?.[selectedICPIndex];

  const goNext = () => {
    if (currentIndex < STEPS.length - 1) {
      setCurrentScreen(STEPS[currentIndex + 1].id as Phase5Screen);
      savePhase5({
        ...phase5,
        primaryICPId,
        secondaryICPIds,
      });
    }
  };

  const goBack = () => {
    if (currentIndex > 0) {
      setCurrentScreen(STEPS[currentIndex - 1].id as Phase5Screen);
    } else {
      router.push('/foundation/phase4');
    }
  };

  const handleStepClick = (stepId: string) => {
    const stepIndex = STEPS.findIndex((s) => s.id === stepId);
    if (stepIndex <= currentIndex) {
      setCurrentScreen(stepId as Phase5Screen);
    }
  };

  const handleLock = async () => {
    const lockedData = {
      ...phase5,
      primaryICPId,
      secondaryICPIds,
      lockedAt: new Date().toISOString(),
    };
    setPhase5(lockedData);
    await savePhase5(lockedData);
    toast.success('ICPs locked!');
    router.push('/foundation/phase6');
  };

  // Update handlers
  const handleSelectPrimary = (id: string) => {
    setPrimaryICPId(id);
    // Also set selectedICPIndex to view this ICP
    const idx = phase5.candidateSegments.findIndex((c) => c.id === id);
    if (idx >= 0) {
      // Find corresponding ICP
      const icpIdx = phase5.icps.findIndex((icp) =>
        icp.name.includes(phase5.candidateSegments[idx].label.split(' (')[0])
      );
      if (icpIdx >= 0) setSelectedICPIndex(icpIdx);
    }
  };

  const handleSelectSecondary = (id: string) => {
    if (secondaryICPIds.includes(id)) {
      setSecondaryICPIds(secondaryICPIds.filter((sid) => sid !== id));
    } else {
      setSecondaryICPIds([...secondaryICPIds, id]);
    }
  };

  const handleUpdateCandidate = (
    id: string,
    updates: Partial<CandidateSegment>
  ) => {
    setPhase5({
      ...phase5,
      candidateSegments: phase5.candidateSegments.map((c) =>
        c.id === id ? { ...c, ...updates } : c
      ),
    });
  };

  const handleUpdateICP = (updates: Partial<ICP>) => {
    if (!currentICP) return;
    setPhase5({
      ...phase5,
      icps: phase5.icps.map((icp, i) =>
        i === selectedICPIndex ? { ...icp, ...updates } : icp
      ),
    });
  };

  // Loading states
  if (isLoading || isProcessing) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F3F4EE]">
        <div className="text-center space-y-6">
          <div className="w-16 h-16 border-[3px] border-[#2D3538] border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="font-serif text-2xl text-[#2D3538]">
            {isProcessing ? 'Compiling ICPs...' : 'Loading...'}
          </p>
          {isProcessing && (
            <p className="text-sm text-[#5B5F61]">
              Analyzing Phase 4 data to generate ICP candidates
            </p>
          )}
        </div>
      </div>
    );
  }

  if (!foundation?.phase4) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F3F4EE]">
        <div className="text-center space-y-8 max-w-md px-8">
          <AlertCircle className="w-12 h-12 text-[#2D3538] mx-auto" />
          <h1 className="font-serif text-3xl text-[#2D3538]">
            Complete Phase 4 First
          </h1>
          <p className="text-[#5B5F61]">
            The ICP Engine requires positioning data from Phase 4.
          </p>
          <Button
            onClick={() => router.push('/foundation/phase4')}
            className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-10 py-6 rounded-2xl"
          >
            Go to Phase 4
          </Button>
        </div>
      </div>
    );
  }

  const { title, subtitle } = SCREEN_CONTENT[currentScreen];

  return (
    <PhaseScreen
      phaseNumber={5}
      phaseTitle="ICP Engine"
      currentStepId={currentScreen}
      steps={STEPS}
      title={title}
      subtitle={subtitle}
      onBack={goBack}
      onStepClick={handleStepClick}
      showContinue={currentScreen !== 'complete'}
      continueText="Continue"
      onContinue={goNext}
    >
      {/* Screen 5.0: Landing */}
      {currentScreen === 'landing' && (
        <ICPEngineLanding
          foundation={foundation}
          onContinue={goNext}
          onBusinessTypeChange={setBusinessType}
          onGeoFocusChange={setGeoFocus}
          businessType={businessType}
          geoFocus={geoFocus}
        />
      )}

      {/* Screen 5.1: Candidates */}
      {currentScreen === 'candidates' && (
        <ICPCandidateGenerator
          candidates={phase5.candidateSegments}
          onSelectPrimary={handleSelectPrimary}
          onSelectSecondary={handleSelectSecondary}
          onUpdateCandidate={handleUpdateCandidate}
          primaryId={primaryICPId}
          secondaryIds={secondaryICPIds}
        />
      )}

      {/* Screen 5.2: Definition */}
      {currentScreen === 'definition' && currentICP && (
        <ICPDefinitionBuilder
          icp={currentICP}
          onUpdate={handleUpdateICP}
          onLock={goNext}
        />
      )}

      {/* Screen 5.3: JTBD */}
      {currentScreen === 'jtbd' && currentICP && (
        <JTBDStruggleMoments
          jtbd={currentICP.jtbd}
          forces={currentICP.forces}
          strugglingMoments={foundation?.phase3?.jtbd?.strugglingMoments || []}
          onUpdateJTBD={(updates) =>
            handleUpdateICP({ jtbd: { ...currentICP.jtbd, ...updates } })
          }
          onUpdateForces={(updates) =>
            handleUpdateICP({ forces: { ...currentICP.forces, ...updates } })
          }
          onUpdateStruggles={() => {}}
          onSetPrimaryJob={setPrimaryJobType}
          primaryJobType={primaryJobType}
        />
      )}

      {/* Screen 5.4: Buying Group */}
      {currentScreen === 'buying-group' && currentICP && (
        <BuyingGroupMap
          roles={currentICP.buyingGroup.roles}
          onReorderRoles={(roles) =>
            handleUpdateICP({
              buyingGroup: { ...currentICP.buyingGroup, roles },
            })
          }
          onToggleRole={(roleId) => {
            handleUpdateICP({
              buyingGroup: {
                ...currentICP.buyingGroup,
                roles: currentICP.buyingGroup.roles.map((r) =>
                  r.id === roleId ? { ...r, isActive: !r.isActive } : r
                ),
              },
            });
          }}
          onUpdateRole={(roleId, updates) => {
            handleUpdateICP({
              buyingGroup: {
                ...currentICP.buyingGroup,
                roles: currentICP.buyingGroup.roles.map((r) =>
                  r.id === roleId ? { ...r, ...updates } : r
                ),
              },
            });
          }}
        />
      )}

      {/* Screen 5.5: Buying Jobs Coverage */}
      {currentScreen === 'buying-jobs' && currentICP && (
        <BuyingJobsCoverage
          roles={currentICP.buyingGroup.roles}
          cells={phase5.buyingJobsCoverage?.cells || []}
          gaps={phase5.buyingJobsCoverage?.gaps || []}
          onUpdateCell={(cell) => {
            const cells = phase5.buyingJobsCoverage?.cells || [];
            const existing = cells.findIndex(
              (c) => c.buyingJob === cell.buyingJob && c.roleId === cell.roleId
            );
            if (existing >= 0) {
              cells[existing] = cell;
            } else {
              cells.push(cell);
            }
            setPhase5({
              ...phase5,
              buyingJobsCoverage: {
                cells,
                gaps: phase5.buyingJobsCoverage?.gaps || [],
              },
            });
          }}
          onFlagGap={(gap) => {
            const gaps = phase5.buyingJobsCoverage?.gaps || [];
            if (!gaps.includes(gap)) {
              setPhase5({
                ...phase5,
                buyingJobsCoverage: {
                  cells: phase5.buyingJobsCoverage?.cells || [],
                  gaps: [...gaps, gap],
                },
              });
            }
          }}
        />
      )}

      {/* Screen 5.6: Triggers */}
      {currentScreen === 'triggers' && (
        <TriggerStack
          triggers={phase5.triggerStack || []}
          intentSignals={phase5.intentSignals || []}
          onUpdateTrigger={(id, updates) => {
            setPhase5({
              ...phase5,
              triggerStack: (phase5.triggerStack || []).map((t) =>
                t.id === id ? { ...t, ...updates } : t
              ),
            });
          }}
          onAddTrigger={(trigger) => {
            setPhase5({
              ...phase5,
              triggerStack: [
                ...(phase5.triggerStack || []),
                { ...trigger, id: uuidv4() },
              ],
            });
          }}
          onConfirmTop3={setConfirmedTriggerIds}
          confirmedIds={confirmedTriggerIds}
        />
      )}

      {/* Screen 5.7: Channels */}
      {currentScreen === 'channels' && (
        <ChannelHabitatMap
          channels={phase5.channelHabitats || []}
          onUpdateChannel={(id, updates) => {
            setPhase5({
              ...phase5,
              channelHabitats: (phase5.channelHabitats || []).map((c) =>
                c.id === id ? { ...c, ...updates } : c
              ),
            });
          }}
          onTogglePrimary={(id) => {
            setPhase5({
              ...phase5,
              channelHabitats: (phase5.channelHabitats || []).map((c) =>
                c.id === id
                  ? { ...c, isPrimary: !c.isPrimary, isSecondary: false }
                  : c
              ),
            });
          }}
          onToggleSecondary={(id) => {
            setPhase5({
              ...phase5,
              channelHabitats: (phase5.channelHabitats || []).map((c) =>
                c.id === id ? { ...c, isSecondary: !c.isSecondary } : c
              ),
            });
          }}
          primaryCount={
            (phase5.channelHabitats || []).filter((c) => c.isPrimary).length
          }
          secondaryCount={
            (phase5.channelHabitats || []).filter((c) => c.isSecondary).length
          }
        />
      )}

      {/* Screen 5.8: Beliefs & Objections */}
      {currentScreen === 'beliefs' && (
        <BeliefObjectionStack
          beliefs={phase5.beliefs || []}
          objections={phase5.objectionStack || []}
          onUpdateBelief={(id, updates) => {
            setPhase5({
              ...phase5,
              beliefs: (phase5.beliefs || []).map((b) =>
                b.id === id ? { ...b, ...updates } : b
              ),
            });
          }}
          onAddBelief={(belief) => {
            setPhase5({
              ...phase5,
              beliefs: [...(phase5.beliefs || []), { ...belief, id: uuidv4() }],
            });
          }}
          onRemoveBelief={(id) => {
            setPhase5({
              ...phase5,
              beliefs: (phase5.beliefs || []).filter((b) => b.id !== id),
            });
          }}
          onUpdateObjection={(id, updates) => {
            setPhase5({
              ...phase5,
              objectionStack: (phase5.objectionStack || []).map((o) =>
                o.id === id ? { ...o, ...updates } : o
              ),
            });
          }}
          onReorderObjections={(objections) => {
            setPhase5({ ...phase5, objectionStack: objections });
          }}
          onAddObjection={(objection) => {
            setPhase5({
              ...phase5,
              objectionStack: [
                ...(phase5.objectionStack || []),
                { ...objection, id: uuidv4() },
              ],
            });
          }}
          onMarkDealKiller={(id) => {
            setPhase5({
              ...phase5,
              objectionStack: (phase5.objectionStack || []).map((o) =>
                o.id === id ? { ...o, isDealKiller: !o.isDealKiller } : o
              ),
            });
          }}
        />
      )}

      {/* Screen 5.9: Negative ICP */}
      {currentScreen === 'negative' && (
        <NegativeICPBuilder
          negativeICP={
            phase5.negativeICP || {
              industries: [],
              disqualifiers: [],
              behaviorSignals: [],
            }
          }
          onUpdate={(updates) => {
            setPhase5({
              ...phase5,
              negativeICP: {
                ...(phase5.negativeICP || {
                  industries: [],
                  disqualifiers: [],
                  behaviorSignals: [],
                }),
                ...updates,
              },
            });
          }}
          onAddDisqualifier={(disq) => {
            const current = phase5.negativeICP || {
              industries: [],
              disqualifiers: [],
              behaviorSignals: [],
            };
            setPhase5({
              ...phase5,
              negativeICP: {
                ...current,
                disqualifiers: [
                  ...(current.disqualifiers || []),
                  { ...disq, id: uuidv4() },
                ],
              },
            });
          }}
          onRemoveDisqualifier={(id) => {
            const current = phase5.negativeICP || {
              industries: [],
              disqualifiers: [],
              behaviorSignals: [],
            };
            setPhase5({
              ...phase5,
              negativeICP: {
                ...current,
                disqualifiers: (current.disqualifiers || []).filter((d) => d.id !== id),
              },
            });
          }}
          onUpdateDisqualifier={(id, updates) => {
            const current = phase5.negativeICP || {
              industries: [],
              disqualifiers: [],
              behaviorSignals: [],
            };
            setPhase5({
              ...phase5,
              negativeICP: {
                ...current,
                disqualifiers: (current.disqualifiers || []).map((d) =>
                  d.id === id ? { ...d, ...updates } : d
                ),
              },
            });
          }}
        />
      )}

      {/* Screen 5.10: Graph */}
      {currentScreen === 'graph' && (
        <InterICPGraph
          icps={phase5.icps}
          graph={phase5.interICPGraph}
          onUpdateGraph={(graph) =>
            setPhase5({ ...phase5, interICPGraph: graph })
          }
          onSetTargetSequence={(sequence) => {
            setPhase5({
              ...phase5,
              interICPGraph: {
                ...phase5.interICPGraph,
                targetSequence: sequence,
              },
            });
          }}
        />
      )}

      {/* Screen: Complete */}
      {currentScreen === 'complete' && (
        <div className="text-center space-y-10 py-8">
          <div className="w-20 h-20 mx-auto bg-[#2D3538] rounded-full flex items-center justify-center">
            <Users className="w-10 h-10 text-white" />
          </div>

          <div className="max-w-md mx-auto space-y-4">
            <h2 className="font-serif text-2xl text-[#2D3538]">
              Your ICP Pack is Ready
            </h2>
            <p className="text-[#5B5F61]">
              {phase5.icps?.length || 0} ICPs defined with buying groups,
              triggers, channels, beliefs, and objections.
            </p>

            {/* Summary Cards */}
            <div className="grid grid-cols-2 gap-3 text-left mt-8">
              <div className="bg-[#F3F4EE] rounded-xl p-4">
                <span className="text-[10px] font-mono uppercase text-[#9D9F9F]">
                  Primary
                </span>
                <p className="text-sm font-medium text-[#2D3538] mt-1">
                  {phase5.icps?.[0]?.name || 'None'}
                </p>
              </div>
              <div className="bg-[#F3F4EE] rounded-xl p-4">
                <span className="text-[10px] font-mono uppercase text-[#9D9F9F]">
                  Triggers
                </span>
                <p className="text-sm font-medium text-[#2D3538] mt-1">
                  {confirmedTriggerIds.length} confirmed
                </p>
              </div>
              <div className="bg-[#F3F4EE] rounded-xl p-4">
                <span className="text-[10px] font-mono uppercase text-[#9D9F9F]">
                  Channels
                </span>
                <p className="text-sm font-medium text-[#2D3538] mt-1">
                  {
                    (phase5.channelHabitats || []).filter((c) => c.isPrimary)
                      .length
                  }{' '}
                  primary
                </p>
              </div>
              <div className="bg-[#F3F4EE] rounded-xl p-4">
                <span className="text-[10px] font-mono uppercase text-[#9D9F9F]">
                  Disqualifiers
                </span>
                <p className="text-sm font-medium text-[#2D3538] mt-1">
                  {phase5.negativeICP?.disqualifiers?.length || 0} defined
                </p>
              </div>
            </div>
          </div>

          <Button
            onClick={handleLock}
            className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-12 py-7 rounded-2xl text-lg font-medium transition-all hover:scale-[1.02]"
          >
            Lock & Continue to Phase 6 <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
        </div>
      )}
    </PhaseScreen>
  );
}
