"use client";

import React from "react";
import { useEffect } from "react";
import { MagicWandIcon, ViewGridIcon, ActivityLogIcon, PersonIcon } from "@radix-ui/react-icons";
import { OfficeCanvas } from "@/components/office/office-canvas";
import { OfficeNudgePanel } from "@/components/office/office-nudge-panel";
import { useQuery } from "@tanstack/react-query";
import { useOfficeStore } from "@/state/office-store";
import { useFoundationStore } from "@/state/foundation-store";
import { officeApi } from "@/lib/api";
import { useOfficeSocket } from "@/lib/socket";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/cn";

/**
 * RaptorFlow Office Shell
 * 
 * The main container for the Office environment. Managed Layer 2 (HUD)
 * and hosts the Layer 1 (Canvas).
 */
export function OfficeShell() {
  const { zoom, focusedZone, agentStatuses, eventLog, snarkFeed, connectionStatus, setConnectionStatus } = useOfficeStore();
  const { sectionData } = useFoundationStore();
  
  const bizName = sectionData.scan_results?.businessName || "RaptorFlow HQ";
  const activeAgentCount = Object.keys(agentStatuses).length;
  const { connect, disconnect, addStatusListener } = useOfficeSocket("dev-org");
  const officeState = useQuery({
    queryKey: ["office", "state"],
    queryFn: () => officeApi.getState(),
    refetchInterval: 15_000,
  });

  useEffect(() => {
    connect();
    const removeListener = addStatusListener((status) => {
      if (status === "connected" || status === "connecting" || status === "disconnected") {
        setConnectionStatus(status);
      }
    });

    return () => {
      removeListener();
      disconnect();
    };
  }, [addStatusListener, connect, disconnect, setConnectionStatus]);

  return (
    <div className="flex flex-col gap-6 p-6 h-full max-w-7xl mx-auto">
      <OfficeNudgePanel />

      {/* Header HUD */}
      <header className="flex items-end justify-between border-b border-zinc-800 pb-6">
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <div className="bg-amber-500 p-1">
              <MagicWandIcon className="h-4 w-4 text-black" />
            </div>
            <p className="font-mono text-[10px] font-bold uppercase tracking-[0.25em] text-amber-500">
              Live Operations Center
            </p>
            <Badge variant="outline" className="h-5 text-[9px] font-mono border-zinc-800 text-zinc-500">
              {connectionStatus.toUpperCase()}
            </Badge>
          </div>
          <div className="space-y-0.5">
            <h1 className="font-serif text-4xl text-white tracking-tight leading-none">
              {bizName}
            </h1>
            <p className="font-mono text-[10px] text-zinc-500 uppercase tracking-[0.2em]">
              Strategic Command Post
            </p>
          </div>
        </div>

        {/* Live Counters */}
        <div className="flex items-center gap-10">
          <div className="text-right">
            <p className="font-serif text-2xl text-white leading-none mb-1">{activeAgentCount}</p>
            <p className="font-mono text-[8px] text-amber-500 font-bold uppercase tracking-widest bg-amber-500/10 px-1.5 py-0.5 border border-amber-500/20">
              Agents Active
            </p>
          </div>
          <div className="text-right">
            <p className="font-serif text-2xl text-white leading-none mb-1">{officeState.data?.activeCampaigns ?? eventLog.length}</p>
            <p className="font-mono text-[8px] text-zinc-500 font-bold uppercase tracking-widest">
              Active Campaigns
            </p>
          </div>
        </div>
      </header>

      {/* Main Operations Card */}
      <Card className="flex-1 bg-background border-zinc-800 overflow-hidden relative flex flex-col">
        {/* Subtle Obsidian Grid Overlay */}
        <div className="absolute inset-0 pointer-events-none opacity-[0.03]" style={{ backgroundImage: 'radial-gradient(#ffffff 1px, transparent 1px)', backgroundSize: '24px 24px' }} />
        
        <Tabs defaultValue="canvas" className="flex-1 flex flex-col">
          <div className="px-4 border-b border-zinc-800 bg-background/50 backdrop-blur-sm z-10 flex items-center justify-between">
            <TabsList className="bg-transparent h-12 gap-6">
              <TabsTrigger value="canvas" className="data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-amber-500 rounded-none h-full px-0 font-mono text-[10px] uppercase tracking-widest text-zinc-500 data-[state=active]:text-white">
                <ViewGridIcon className="w-3.5 h-3.5 mr-2" />
                Floor Plan
              </TabsTrigger>
              <TabsTrigger value="events" className="data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-amber-500 rounded-none h-full px-0 font-mono text-[10px] uppercase tracking-widest text-zinc-500 data-[state=active]:text-white">
                <ActivityLogIcon className="w-3.5 h-3.5 mr-2" />
                Event Trail
              </TabsTrigger>
              <TabsTrigger value="roster" className="data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-amber-500 rounded-none h-full px-0 font-mono text-[10px] uppercase tracking-widest text-zinc-500 data-[state=active]:text-white">
                <PersonIcon className="w-3.5 h-3.5 mr-2" />
                Agent Roster
              </TabsTrigger>
            </TabsList>
            
            <Badge variant="secondary" className="font-mono text-[9px] opacity-40">
              ZOOM: {Math.round(zoom * 100)}% · NUDGES: {officeState.data?.openNudges ?? 0}
            </Badge>
          </div>

          <TabsContent value="canvas" className="flex-1 relative m-0">
            <OfficeCanvas />
            
            {/* Context Footer */}
            <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between pointer-events-none">
              <span className="bg-black/80 px-2 py-1 border border-zinc-800 text-[8px] font-mono text-zinc-500 uppercase tracking-widest backdrop-blur-sm">
                ZONE://{focusedZone || 'GLOBAL_VIEW'}
              </span>
              <span className="text-[8px] font-mono text-zinc-700 uppercase tracking-widest font-bold">
                GL_RENDER_STABLE
              </span>
            </div>
          </TabsContent>

          <TabsContent value="events" className="flex-1 m-0">
            <ScrollArea className="h-[500px]">
              <div className="p-4 space-y-3">
                {eventLog.map((event, i) => (
                <div key={i} className="flex items-center gap-4 border-b border-zinc-800/50 pb-2 last:border-0">
                    <span className="text-[9px] font-mono text-zinc-600 uppercase grow-0 shrink-0 w-24">
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </span>
                    <span className="text-[10px] font-bold text-amber-500 uppercase tracking-widest w-32">
                      {event.type}
                    </span>
                    <span className="text-xs text-zinc-400">
                      Telemetry received from {event.agentKey || 'CORE'}
                    </span>
                  </div>
                ))}
                {eventLog.length === 0 && (
                  <div className="py-12 text-center text-[10px] font-mono uppercase tracking-widest text-zinc-600">
                    Waiting for live office events from the backend runtime.
                  </div>
                )}
              </div>
            </ScrollArea>
          </TabsContent>

          <TabsContent value="roster" className="flex-1 m-0">
             <div className="p-6 grid grid-cols-4 gap-4">
                {/* Roster components would go here, imported or nested */}
                {activeAgentCount === 0 ? (
                  <div className="text-zinc-600 font-mono text-[10px] col-span-4 text-center py-20 uppercase tracking-widest">
                    No live agent activity yet.
                  </div>
                ) : (
                  Object.entries(agentStatuses).map(([key, status]) => (
                    <div key={key} className="border border-zinc-800 p-4 bg-zinc-950/50">
                      <div className="font-mono text-[10px] uppercase tracking-widest text-amber-500">{key}</div>
                      <div className="mt-2 text-sm text-zinc-300">{status.status}</div>
                      <div className="mt-1 text-[10px] font-mono uppercase tracking-widest text-zinc-600">{status.currentZone}</div>
                    </div>
                  ))
                )}
             </div>
          </TabsContent>
        </Tabs>
      </Card>

      {/* Footer HUD elements */}
      <footer className="grid grid-cols-3 gap-6 h-32">
        <Card className="bg-background border-zinc-800 p-4 flex flex-col justify-between">
           <span className="text-[9px] font-bold font-mono text-zinc-500 uppercase tracking-widest">Live Snark</span>
           <div className="flex-1 mt-2 overflow-hidden">
             {snarkFeed.slice(0, 3).map(line => (
               <p key={line.id} className="text-[11px] text-zinc-400 line-clamp-1 italic">
                 &lt;{line.agentKey}&gt; {line.text}
               </p>
             ))}
           </div>
        </Card>
        <div className="col-span-2 bg-[#1a1a1a] border-2 border-dashed border-zinc-800/50 rounded-lg flex items-center justify-center">
           <span className="text-[10px] font-mono text-zinc-700 uppercase tracking-[0.3em]">
             Muse (7d): {officeState.data?.recentMuseConversations ?? 0} · Council Active: {officeState.data?.activeCouncilSessions ?? 0}
           </span>
        </div>
      </footer>
    </div>
  );
}
