"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import gsap from "gsap";
import { Plus, Building2, ChevronRight, LogOut } from "lucide-react";
import dynamic from 'next/dynamic';
import { BlueprintCard } from "@/components/ui/BlueprintCard";

const BlueprintButton = dynamic(() => import("@/components/ui/BlueprintButton").then(mod => ({ default: mod.BlueprintButton })), { ssr: false });
const SecondaryButton = dynamic(() => import("@/components/ui/BlueprintButton").then(mod => ({ default: mod.SecondaryButton })), { ssr: false });
const BlueprintAvatar = dynamic(() => import("@/components/ui/BlueprintAvatar").then(mod => ({ default: mod.BlueprintAvatar })), { ssr: false });

export const runtime = 'edge';

const WORKSPACES = [
  { id: "ws-1", name: "Acme Corp", role: "Owner", members: 4, initials: "AC" },
  { id: "ws-2", name: "Side Project", role: "Admin", members: 1, initials: "SP" },
];

export default function WorkspacePage() {
  const router = useRouter();
  const pageRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!pageRef.current) return;
    gsap.fromTo("[data-anim]", { opacity: 0, scale: 0.95 }, { opacity: 1, scale: 1, duration: 0.5, ease: "back.out(1.7)" });
  }, []);

  const handleSelect = (id: string) => {
    // Logic to set active workspace in context/store
    router.push('/dashboard');
  };

  return (
    <div ref={pageRef} className="min-h-screen bg-[var(--canvas)] flex items-center justify-center p-4 relative">
      <div className="fixed inset-0 pointer-events-none z-0" style={{ backgroundImage: "url('/textures/paper-grain.png')", opacity: 0.05, mixBlendMode: "multiply" }} />
      <div className="fixed inset-0 blueprint-grid pointer-events-none z-0 opacity-20" />

      <div className="w-full max-w-md" data-anim>
        <div className="text-center mb-8">
          <h1 className="font-serif text-3xl text-[var(--ink)] mb-2">Select Workspace</h1>
          <p className="text-[var(--ink-secondary)] font-technical text-sm">Welcome back, Alex.</p>
        </div>

        <div className="space-y-4">
          {WORKSPACES.map((ws) => (
            <BlueprintCard
              key={ws.id}
              onClick={() => handleSelect(ws.id)}
              className="group cursor-pointer hover:border-[var(--blueprint)] transition-all"
              padding="md"
              showCorners
            >
              <div className="align-center gap-4">
                <BlueprintAvatar initials={ws.initials} size="lg" />
                <div className="flex-1">
                  <h3 className="font-semibold text-[var(--ink)] group-hover:text-[var(--blueprint)] transition-colors">{ws.name}</h3>
                  <div className="align-center gap-2 text-xs text-[var(--ink-secondary)]">
                    <span>{ws.role}</span>
                    <span className="w-1 h-1 rounded-full bg-[var(--border)]" />
                    <span>{ws.members} Members</span>
                  </div>
                </div>
                <ChevronRight size={18} className="text-[var(--ink-secondary)] group-hover:text-[var(--blueprint)] group-hover:translate-x-1 transition-all" />
              </div>
            </BlueprintCard>
          ))}

          <BlueprintButton
            variant="ghost"
            className="w-full border-dashed"
            onClick={() => console.log('Create new workspace')}
          >
            <Plus size={16} />
            Create New Workspace
          </BlueprintButton>
        </div>

        <div className="mt-8 text-center">
          <BlueprintButton
            variant="ghost"
            size="sm"
            onClick={() => router.push('/')}
            className="mx-auto"
          >
            <LogOut size={12} /> Sign Out
          </BlueprintButton>
        </div>
      </div>
    </div>
  );
}
