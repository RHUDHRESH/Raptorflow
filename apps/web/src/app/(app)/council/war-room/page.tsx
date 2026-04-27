"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useCouncilOrchestrationCreate } from "@/hooks/use-council-orchestration";
import { useCouncilOrchestrationList } from "@/hooks/use-council-orchestration";
import { useCouncilOrchestrationGet } from "@/hooks/use-council-orchestration";
import { useCouncilOrchestrationTurns } from "@/hooks/use-council-orchestration";
import { useCouncilOrchestrationPresence } from "@/hooks/use-council-orchestration";
import { useCouncilOrchestrationDebateEvents } from "@/hooks/use-council-orchestration";
import { CouncilRunForm } from "@/components/council/CouncilRunForm";
import { CouncilRunList } from "@/components/council/CouncilRunList";
import { CouncilAvatarRoster } from "@/components/council/CouncilAvatarRoster";
import { CouncilTimeline } from "@/components/council/CouncilTimeline";
import { CouncilChallengeMap } from "@/components/council/CouncilChallengeMap";
import { CouncilSynthesisCards } from "@/components/council/CouncilSynthesisCards";
import { CouncilPresenceGrid } from "@/components/council/CouncilPresenceGrid";
import {
  CreateCouncilOrchestrationRequest,
  CouncilOrchestrationRun,
} from "@/lib/api";

const TERMINAL_STATUSES = ["completed", "failed", "cancelled"];

export default function WarRoomPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const { data: runs, isLoading: runsLoading } = useCouncilOrchestrationList(20);
  const selectedRun = useCouncilOrchestrationGet(selectedRunId ?? "");
  const turns = useCouncilOrchestrationTurns(selectedRunId ?? "");
  const presence = useCouncilOrchestrationPresence(selectedRunId ?? "");
  const debateEvents = useCouncilOrchestrationDebateEvents(selectedRunId ?? "");
  const createMutation = useCouncilOrchestrationCreate();

  const isTerminal =
    selectedRun.data?.status && TERMINAL_STATUSES.includes(selectedRun.data.status);

  useEffect(() => {
    const runParam = searchParams.get("run");
    if (runParam) {
      setSelectedRunId(runParam);
    }
  }, [searchParams]);

  const avatarRoster = selectedRun.data?.avatar_roster;
  const avatarRosterKeys: string[] = Array.isArray(avatarRoster)
    ? avatarRoster
    : typeof avatarRoster === "object" && avatarRoster !== null
      ? Object.keys(avatarRoster)
      : [];

  useEffect(() => {
    if (selectedRunId && !isTerminal) {
      pollingRef.current = setInterval(() => {
        selectedRun.refetch();
        turns.refetch();
        presence.refetch();
        debateEvents.refetch();
      }, 2500);
      return () => {
        if (pollingRef.current !== null) {
          clearInterval(pollingRef.current);
          pollingRef.current = null;
        }
      };
    }
  }, [selectedRunId, isTerminal]);

  const handleCreateRun = async (data: CreateCouncilOrchestrationRequest) => {
    const result = await createMutation.mutateAsync(data);
    setSelectedRunId(result.council_run_id);
    router.push(`/council/war-room?run=${result.council_run_id}`);
  };

  const handleSelectRun = (run: CouncilOrchestrationRun) => {
    setSelectedRunId(run.council_run_id);
    router.push(`/council/war-room?run=${run.council_run_id}`, { scroll: false });
  };

  const handleSelectRunId = (id: string) => {
    setSelectedRunId(id);
    router.push(`/council/war-room?run=${id}`, { scroll: false });
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-100">Council War Room</h1>
            <p className="text-sm text-slate-500 mt-1">
              Orchestrate multi-agent debate and synthesis
            </p>
          </div>
          {selectedRun.data && (
            <div className="flex items-center gap-3">
              <span className="text-xs text-slate-500 uppercase">
                {selectedRun.data.status}
              </span>
              {!isTerminal && (
                <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
              )}
            </div>
          )}
        </div>

        <div className="grid grid-cols-12 gap-6">
          <div className="col-span-12 lg:col-span-3 space-y-4">
            <CouncilRunForm onSubmit={handleCreateRun} isPending={createMutation.isPending} />
            <CouncilRunList
              runs={runs ?? []}
              selectedId={selectedRunId}
              onSelect={handleSelectRunId}
              isLoading={runsLoading}
            />
          </div>

          <div className="col-span-12 lg:col-span-9 space-y-4">
            {selectedRunId ? (
              <>
                <CouncilAvatarRoster
                  avatarKeys={avatarRosterKeys}
                  presenceStates={presence.data}
                  isLoading={presence.isLoading}
                />
                <div className="grid grid-cols-12 gap-4">
                  <div className="col-span-12 md:col-span-6">
                    <CouncilPresenceGrid
                      presenceStates={presence.data ?? []}
                      isLoading={presence.isLoading}
                    />
                  </div>
                  <div className="col-span-12 md:col-span-6">
                    <CouncilChallengeMap
                      debateEvents={debateEvents.data ?? []}
                    />
                  </div>
                </div>
                <CouncilTimeline
                  turns={turns.data ?? []}
                  debateEvents={debateEvents.data ?? []}
                  isLoading={turns.isLoading}
                />
                <CouncilSynthesisCards
                  synthesis={selectedRun.data?.synthesis ?? {}}
                  isLoading={selectedRun.isLoading}
                />
              </>
            ) : (
              <div className="card-elevated p-12 text-center">
                <p className="mono-label text-slate-500">
                  Select a run or create a new orchestration to begin
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}