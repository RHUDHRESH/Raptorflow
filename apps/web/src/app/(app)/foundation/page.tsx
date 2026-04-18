"use client";

import type * as React from "react";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { Loader2 } from "lucide-react";
import { Route } from "next";
import Link from "next/link";
import { ChevronRightIcon, MixIcon } from "@radix-ui/react-icons";
import { useFoundation } from "@/hooks/use-foundation";
import { foundationApi } from "@/lib/api";
import { FOUNDATION_STEPS } from "@/lib/foundation";
import { GsapBridge } from "@/components/ui/gsap-bridge";

export default function FoundationIndexPage(): React.ReactElement {
  const router = useRouter();
  const { getToken } = useAuth();
  const { data: foundation, isLoading } = useFoundation();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    async function checkStatus() {
      try {
        const data = await foundationApi.getFullStatus();
        if (data.status !== "complete") {
          const nextStep = data.missing_sections[0] || "url";
          router.replace(`/foundation/${nextStep}` as Route);
        } else {
          setChecking(false);
        }
      } catch (err) {
        console.error("Status check failed", err);
        setChecking(false);
      }
    }

    checkStatus();
  }, [router]);

  if (checking || isLoading) {
    return (
      <div className="flex h-[80vh] w-full items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 text-amber-500 animate-spin" />
          <p className="text-zinc-500 text-[10px] font-bold tracking-[0.2em] uppercase font-mono">
            Uplink: Synchronizing Foundation Nodes...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-12 py-6">
      <GsapBridge stagger={true}>
        {/* Header */}
        <header className="gsap-reveal flex items-end justify-between border-b-2 border-[var(--foreground)] pb-8">
           <div className="space-y-2">
             <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.2em", color: "var(--muted-foreground)" }}>
               System Asset
             </p>
             <h1 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 48, lineHeight: 1, margin: 0 }}>
               The Foundation
             </h1>
           </div>
           <p className="max-w-md text-right text-xs text-zinc-500 font-mono uppercase tracking-widest leading-relaxed">
             21 nodes of strategic constraint. <br/>
             Modified: {new Date().toLocaleDateString()} // STATUS: LOCKED
           </p>
        </header>

        {/* The Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-[1px] bg-zinc-800 border border-zinc-800">
          {FOUNDATION_STEPS.map((step, i) => {
            const val = (foundation?.sections?.[step.section] as string) || "";
            const isFilled = val.length > 0;

            return (
              <Link
                key={step.id}
                href={`/foundation/${step.id}` as Route}
                className="gsap-reveal bg-[var(--background)] p-6 hover:bg-zinc-900 transition-colors group relative flex flex-col justify-between min-h-[200px]"
              >
                <div>
                   <div className="flex items-center justify-between mb-4">
                      <span className="font-mono text-[9px] text-zinc-600 font-bold tracking-widest uppercase">
                        Node_{String(i + 1).padStart(2, '0')}
                      </span>
                      {isFilled ? (
                        <div className="h-1.5 w-1.5 rounded-full bg-amber-500" />
                      ) : (
                        <div className="h-1.5 w-1.5 rounded-full bg-zinc-800" />
                      )}
                   </div>
                   <h3 className="font-bold text-sm text-white mb-2 group-hover:text-amber-500 transition-colors">
                     {step.title}
                   </h3>
                   <p className="text-[11px] text-zinc-500 line-clamp-3 font-light leading-relaxed">
                     {val || "No context provided. System default applied."}
                   </p>
                </div>
                
                <div className="pt-4 flex items-center justify-between opacity-0 group-hover:opacity-100 transition-opacity">
                   <span className="text-[8px] font-mono uppercase tracking-[0.2em] text-amber-500 font-bold">Edit Node</span>
                   <ChevronRightIcon className="w-4 h-4 text-amber-500" />
                </div>
              </Link>
            );
          })}

          {/* Reset / Re-map Card */}
          <div className="gsap-reveal bg-zinc-900/50 p-6 flex flex-col justify-center items-center gap-4 text-center border-dashed border-2 border-zinc-800 m-2">
             <MixIcon className="w-8 h-8 text-zinc-700" />
             <p className="text-[9px] font-mono text-zinc-600 uppercase tracking-widest">
               Destructive Action
             </p>
             <button className="text-[10px] font-bold uppercase tracking-widest text-red-500/50 hover:text-red-500 transition-colors">
               Re-map Foundation
             </button>
          </div>
        </div>
      </GsapBridge>
    </div>
  );
}
