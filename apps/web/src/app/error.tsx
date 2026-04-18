"use client";

import * as React from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { GsapBridge } from "@/components/ui/gsap-bridge";
import { ExclamationTriangleIcon, UpdateIcon, HomeIcon } from "@radix-ui/react-icons";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}): React.ReactElement {
  React.useEffect(() => {
    console.error("[GlobalError]", error);
  }, [error]);

  return (
    <div className="flex min-h-screen bg-[#050505] items-center justify-center p-8 overflow-hidden relative">
      {/* Background glitch effect element */}
      <div className="absolute inset-0 bg-red-500/5 opacity-20 animate-pulse pointer-events-none" />
      
      <GsapBridge stagger={true}>
        <div className="gsap-reveal max-w-xl w-full border-2 border-red-900 bg-[#0a0a0a] p-12 relative z-10 text-center shadow-[0_0_50px_rgba(220,38,38,0.1)]">
          <div className="flex justify-center mb-8">
            <div className="h-16 w-16 bg-red-500/10 border border-red-500/50 flex items-center justify-center rounded-none shadow-[0_0_15px_rgba(239,68,68,0.2)]">
               <ExclamationTriangleIcon className="h-8 w-8 text-red-500" />
            </div>
          </div>

          <p className="font-mono text-[10px] uppercase font-bold tracking-[0.3em] text-red-500/60 mb-6">
            Critical // Fault_Detected
          </p>
          
          <h1 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 48, lineHeight: 1.1, margin: 0 }} className="text-white mb-6">
            Strategic Failure
          </h1>
          
          <div className="bg-red-500/5 border border-red-900/50 p-4 mb-10 text-left">
             <div className="flex items-center gap-2 mb-2">
                <span className="font-mono text-[9px] font-bold text-red-500/80 uppercase tracking-widest">Diagnostic Digest</span>
                {error.digest && <span className="bg-red-500/20 text-red-100 text-[8px] px-1.5 py-0.5 font-mono">{error.digest}</span>}
             </div>
             <p className="text-zinc-500 text-xs font-mono break-all leading-relaxed">
               {error.message || "An unexpected cognitive dissonance occurred in the command sequence."}
             </p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              onClick={() => reset()}
              className="bg-red-600 text-white rounded-none h-12 px-8 text-[11px] font-mono font-bold uppercase tracking-widest hover:bg-red-500 shadow-[0_0_20px_rgba(220,38,38,0.2)]"
            >
              <UpdateIcon className="mr-2 h-4 w-4" /> Re-initialize Foundation
            </Button>
            <Button 
              asChild 
              variant="outline" 
              className="border-zinc-800 rounded-none h-12 px-8 text-[11px] font-mono font-bold uppercase tracking-widest hover:border-zinc-500 bg-transparent text-zinc-400"
            >
              <Link href="/daily-wins">
                 <HomeIcon className="mr-2 h-4 w-4" /> Back to Base
              </Link>
            </Button>
          </div>
        </div>
      </GsapBridge>
    </div>
  );
}
