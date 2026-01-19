"use client";

import { useState, useEffect, useRef } from "react";
import { 
  Users, 
  Target, 
  MessageSquare, 
  ShieldCheck, 
  Zap,
  Play,
  CheckCircle2,
  RefreshCw,
  MoreHorizontal,
  Info
} from "lucide-react";
import gsap from "gsap";

import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintLoader } from "@/components/ui/BlueprintLoader";
import { api } from "@/lib/api/client";

/* ══════════════════════════════════════════════════════════════════════════════
   EXPERT COUNCIL ROOM — Multi-Agent Collaboration UI
   Where the Strategist, Copywriter, and Analyst debate your marketing.
   ══════════════════════════════════════════════════════════════════════════════ */

interface Contribution {
  agent_id: string;
  agent_name: string;
  content: string;
  type: string;
  timestamp: string;
}

interface CouncilAgent {
  id: string;
  name: string;
  role: string;
  avatar: string;
  color: string;
}

const AGENTS: Record<string, CouncilAgent> = {
  orchestrator: { id: "orchestrator", name: "Swarm Lead", role: "Orchestrator", avatar: "⚖️", color: "var(--ink-muted)" },
  architect: { id: "architect", name: "Marcus", role: "Strategy Architect", avatar: "🏛️", color: "var(--blueprint)" },
  analyst: { id: "analyst", name: "Sera", role: "Performance Analyst", avatar: "📈", color: "#D7C9AE" },
  developer: { id: "developer", name: "Jax", role: "GTM Developer", avatar: "🛠️", color: "#9D9F9F" },
  qa: { id: "qa", name: "Elena", role: "Brand QA", avatar: "🛡️", color: "#5B5F61" },
};

export function ExpertCouncilRoom() {
  const [mission, setMission] = useState("Refine our GTM strategy for the new Q1 launch.");
  const [isExecuting, setIsExecuting] = useState(false);
  const [contributions, setContributions] = useState<Contribution[]>([]);
  const [finalOutput, setFinalOutput] = useState<string | null>(null);
  const [activeAgent, setActiveAgent] = useState<string | null>(null);
  const [skillsLoaded, setSkillsLoaded] = useState<Record<string, string[]>>({});
  
  const feedRef = useRef<HTMLDivElement>(null);

  const startSession = async () => {
    if (!mission.trim()) return;
    
    setIsExecuting(true);
    setContributions([]);
    setFinalOutput(null);
    setActiveAgent("orchestrator");
    setSkillsLoaded({});

    try {
      const response = await api.post("/council/execute", { mission });
      const data = response.data;
      
      if (data.skills_loaded) {
        setSkillsLoaded(data.skills_loaded);
      }

      // Simulate session progression for visual impact
      for (const cont of data.contributions) {
        setActiveAgent(cont.agent_id);
        await new Promise(r => setTimeout(r, 1000)); // Pause for effect
        setContributions(prev => [...prev, cont]);
      }
      
      setFinalOutput(data.final_output);
      setActiveAgent(null);
    } catch (error) {
      console.error("Council failed:", error);
    } finally {
      setIsExecuting(false);
    }
  };

  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight;
    }
  }, [contributions]);

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Session Header */}
      <div className="flex items-end justify-between">
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <span className="font-technical text-[var(--blueprint)]">SYS.COUNCIL</span>
            <div className="h-px w-8 bg-[var(--structure)]" />
            <span className="font-technical text-[var(--ink-muted)]">AGENTIC_OS</span>
          </div>
          <h1 className="font-serif text-4xl text-[var(--ink)]">Expert Council Room</h1>
        </div>
        <BlueprintBadge variant="blueprint" dot>ULTRA-PREMIUM</BlueprintBadge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Agents & Control */}
        <div className="lg:col-span-4 space-y-6">
          <BlueprintCard padding="lg" showCorners>
            <h3 className="font-technical text-xs text-[var(--ink-muted)] mb-4 uppercase tracking-widest">Active Council</h3>
            <div className="space-y-4">
              {Object.values(AGENTS).map(agent => (
                <div 
                  key={agent.id}
                  className={`flex items-center gap-4 p-3 rounded-xl border transition-all ${
                    activeAgent === agent.id 
                      ? 'border-[var(--blueprint)] bg-[var(--blueprint-light)] shadow-sm scale-[1.02]' 
                      : 'border-transparent opacity-70'
                  }`}
                >
                  <div className="text-2xl w-10 h-10 flex items-center justify-center bg-[var(--surface)] rounded-lg border border-[var(--structure)]">
                    {agent.avatar}
                  </div>
                  <div>
                    <div className="font-medium text-sm text-[var(--ink)]">{agent.name}</div>
                    <div className="text-[10px] text-[var(--ink-muted)] uppercase font-bold">{agent.role}</div>
                    {skillsLoaded[agent.id] && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {skillsLoaded[agent.id].map(s => (
                          <span key={s} className="text-[8px] bg-[var(--surface)] border border-[var(--structure-subtle)] px-1 rounded text-[var(--blueprint)]">
                            {s.replace('Skill', '')}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  {activeAgent === agent.id && (
                    <div className="ml-auto">
                      <div className="flex gap-1">
                        <span className="w-1.5 h-1.5 bg-[var(--blueprint)] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <span className="w-1.5 h-1.5 bg-[var(--blueprint)] rounded-full animate-bounce" style={{ animationDelay: '200ms' }} />
                        <span className="w-1.5 h-1.5 bg-[var(--blueprint)] rounded-full animate-bounce" style={{ animationDelay: '400ms' }} />
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </BlueprintCard>

          <BlueprintCard padding="lg" showCorners>
            <h3 className="font-technical text-xs text-[var(--ink-muted)] mb-4 uppercase tracking-widest">Council Mission</h3>
            <textarea 
              value={mission}
              onChange={(e) => setMission(e.target.value)}
              className="w-full bg-[var(--surface)] border border-[var(--structure)] rounded-xl p-4 text-sm focus:outline-none focus:border-[var(--blueprint)] min-h-[120px] resize-none"
              placeholder="Enter the mission for the council..."
              disabled={isExecuting}
            />
            <div className="mt-4">
              <BlueprintButton 
                onClick={startSession} 
                disabled={isExecuting}
                className="w-full h-12"
              >
                {isExecuting ? <RefreshCw className="animate-spin mr-2" size={18} /> : <Play className="mr-2" size={18} />}
                {isExecuting ? "Council in Session..." : "Convene Expert Council"}
              </BlueprintButton>
            </div>
          </BlueprintCard>
        </div>

        {/* Right Column: Discussion Feed */}
        <div className="lg:col-span-8 space-y-6">
          <BlueprintCard 
            className="h-[600px] flex flex-col overflow-hidden bg-[var(--paper)] relative"
            padding="none"
          >
            {/* Discussion Header */}
            <div className="p-4 border-b border-[var(--structure)] bg-[var(--surface)]/50 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <MessageSquare size={16} className="text-[var(--blueprint)]" />
                <span className="font-technical text-xs">DISCUSSION_FEED</span>
              </div>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1.5">
                  <span className={`w-2 h-2 rounded-full ${isExecuting ? 'bg-green-500 animate-pulse' : 'bg-[var(--ink-muted)]'}`} />
                  <span className="text-[10px] font-bold uppercase">{isExecuting ? 'Live' : 'Standby'}</span>
                </div>
                <MoreHorizontal size={16} className="text-[var(--ink-muted)] cursor-pointer" />
              </div>
            </div>

            {/* Scrollable Area */}
            <div 
              ref={feedRef}
              className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth"
            >
              {contributions.length === 0 && !isExecuting && (
                <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-40">
                  <Users size={48} strokeWidth={1} />
                  <div className="max-w-xs text-sm">
                    The Council is currently empty. Define a mission and click "Convene" to start the deliberation.
                  </div>
                </div>
              )}

              {contributions.map((cont, idx) => (
                <div 
                  key={idx}
                  className={`flex gap-4 animate-in fade-in slide-in-from-bottom-2 duration-500`}
                >
                  <div className="w-10 h-10 shrink-0 bg-[var(--surface)] border border-[var(--structure)] rounded-lg flex items-center justify-center text-xl">
                    {AGENTS[cont.agent_id]?.avatar || "🤖"}
                  </div>
                  <div className="space-y-1.5 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold uppercase tracking-wider">{cont.agent_name}</span>
                      <span className="text-[10px] text-[var(--ink-muted)]">{new Date(cont.timestamp).toLocaleTimeString()}</span>
                      <BlueprintBadge 
                        variant={cont.type === 'moderation' ? 'default' : cont.type === 'critique' ? 'warning' : 'blueprint'}
                        className="text-[8px] py-0 px-1.5 h-4"
                      >
                        {cont.type.toUpperCase()}
                      </BlueprintBadge>
                    </div>
                    <div className="text-sm text-[var(--ink)] leading-relaxed bg-[var(--surface)] p-4 rounded-2xl rounded-tl-none border border-[var(--structure-subtle)]">
                      {cont.content}
                    </div>
                  </div>
                </div>
              ))}

              {isExecuting && (
                <div className="flex gap-4 opacity-50">
                  <div className="w-10 h-10 bg-[var(--surface)] border border-[var(--structure)] rounded-lg flex items-center justify-center">
                    <BlueprintLoader size="sm" />
                  </div>
                  <div className="space-y-2 flex-1">
                    <div className="h-3 w-24 bg-[var(--structure)] rounded animate-pulse" />
                    <div className="h-12 w-full bg-[var(--structure-subtle)] rounded-xl animate-pulse" />
                  </div>
                </div>
              )}
            </div>

            {/* Success Overlay for Final Output */}
            {finalOutput && (
              <div className="absolute inset-0 z-20 p-6 bg-[var(--paper)]/95 flex flex-col animate-in fade-in duration-700">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-green-100 text-green-600 rounded-full flex items-center justify-center">
                      <CheckCircle2 size={24} />
                    </div>
                    <div>
                      <h3 className="font-serif text-xl">Consensus Reached</h3>
                      <p className="text-xs text-[var(--ink-muted)]">Surgical plan synthesized by the Council.</p>
                    </div>
                  </div>
                  <SecondaryButton onClick={() => setFinalOutput(null)} className="h-8 text-xs">
                    View Discussion
                  </SecondaryButton>
                </div>
                
                <div className="flex-1 overflow-y-auto bg-[var(--surface)] border border-[var(--structure)] rounded-2xl p-8 shadow-inner">
                  <div className="prose prose-sm max-w-none text-[var(--ink)] leading-relaxed whitespace-pre-wrap font-serif text-lg">
                    {finalOutput}
                  </div>
                </div>

                <div className="mt-6 flex gap-4">
                  <BlueprintButton className="flex-1">Apply to Foundation</BlueprintButton>
                  <SecondaryButton className="flex-1">Export Strategy</SecondaryButton>
                </div>
              </div>
            )}
          </BlueprintCard>
        </div>
      </div>
    </div>
  );
}
