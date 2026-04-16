import type * as React from "react";
import Link from "next/link";
import type { Route } from "next";
import { ArrowLeftIcon, FilePlusIcon } from "@radix-ui/react-icons";
import { Button } from "@/components/ui/button";
import { GsapBridge } from "@/components/ui/gsap-bridge";

interface FoundationShellProps {
  currentStepIndex: number;
  totalSteps: number;
  stepTitle: string;
  stepDescription: string;
  isSaving?: boolean;
  hasSaved?: boolean;
  onSaveAndContinue?: () => void;
  onSaveDraft?: () => void;
  prevHref?: Route;
  nextHref?: Route;
  children: React.ReactNode;
}

export function FoundationShell({
  currentStepIndex,
  totalSteps,
  stepTitle,
  stepDescription,
  isSaving = false,
  hasSaved = false,
  onSaveAndContinue,
  onSaveDraft,
  prevHref,
  nextHref,
  children,
}: FoundationShellProps) {
  const progressPercentage = ((currentStepIndex + 1) / totalSteps) * 100;

  return (
    <div className="min-h-screen bg-[var(--background)] flex flex-col font-body">
      
      {/* Top Header / Progress Bar */}
      <header className="sticky top-0 z-40 bg-[var(--background)]/90 backdrop-blur border-b border-[var(--border)] px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <Link href="/app" className="text-sm font-mono tracking-widest uppercase hover:opacity-70 transition-opacity">
            ◂ Exit Office
          </Link>
          <div className="h-4 border-l border-[var(--border)]" />
          <div className="text-xs font-mono uppercase tracking-widest text-[var(--muted-foreground)]">
            Step {currentStepIndex + 1} of {totalSteps}
          </div>
        </div>
        
        <div className="flex items-center gap-4 text-xs font-mono">
          {isSaving ? (
            <span className="text-[var(--muted-foreground)] animate-pulse">Saving...</span>
          ) : hasSaved ? (
            <span className="text-[var(--primary)]">Saved to draft</span>
          ) : null}
          <div className="font-[family-name:var(--font-display)] text-lg">RAPTORFLOW</div>
        </div>
        
        {/* Progress Line absolute bottom of header */}
        <div className="absolute left-0 right-0 bottom-[-1px] h-[1px] bg-[var(--border)]">
          <div 
            className="h-[1px] bg-[var(--primary)] transition-all duration-500 ease-out" 
            style={{ width: `${progressPercentage}%` }} 
          />
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col items-center py-20 px-6">
        <GsapBridge stagger={true} className="w-full max-w-2xl">
          <div className="gsap-reveal mb-12">
            <h1 className="font-[family-name:var(--font-display)] text-4xl mb-3 text-[var(--foreground)]">{stepTitle}</h1>
            <p className="text-[var(--muted-foreground)] text-lg leading-relaxed">{stepDescription}</p>
          </div>

          <div className="gsap-reveal space-y-8">
            {children}
          </div>
        </GsapBridge>
      </main>

      {/* Footer Navigation */}
      <footer className="sticky bottom-0 z-40 bg-[var(--card)] border-t border-[var(--border)] px-6 py-4 flex items-center justify-between">
        <div>
          {prevHref ? (
             <Button asChild variant="outline" className="rounded-none border-[var(--border)] shadow-none h-12 px-6 uppercase tracking-widest text-xs font-mono">
               <Link href={prevHref}><ArrowLeftIcon className="mr-2 h-4 w-4" /> Previous</Link>
             </Button>
          ) : (
            <div /> // Spacer
          )}
        </div>
        
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={onSaveDraft} className="rounded-none h-12 px-6 uppercase tracking-widest text-xs font-mono text-[var(--muted-foreground)] hover:text-[var(--foreground)]">
            <FilePlusIcon className="mr-2 h-4 w-4" /> Save Draft
          </Button>
          
          <Button onClick={onSaveAndContinue} className="rounded-none h-12 px-10 uppercase tracking-widest text-xs font-mono bg-[var(--primary)] text-[var(--primary-foreground)] hover:bg-[var(--primary)]/90 border border-[var(--primary)]">
            Save & Continue
          </Button>
        </div>
      </footer>
    </div>
  );
}
