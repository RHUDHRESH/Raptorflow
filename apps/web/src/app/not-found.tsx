"use client";

import * as React from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { GsapBridge } from "@/components/ui/gsap-bridge";
import { MixerHorizontalIcon, ArrowLeftIcon } from "@radix-ui/react-icons";

export default function NotFound(): React.ReactElement {
  return (
    <div className="flex min-h-screen bg-[#FBF8F2] items-center justify-center p-8 overflow-hidden relative">
      <div
        className="absolute inset-0 opacity-10 pointer-events-none"
        style={{
          backgroundImage: "radial-gradient(circle at 2px 2px, #D5CBC0 1px, transparent 0)",
          backgroundSize: "24px 24px",
        }}
      />

      <GsapBridge stagger={true}>
        <div className="gsap-reveal max-w-xl w-full border-2 border-[var(--foreground)] bg-white p-12 relative z-10 text-center">
          <p className="font-mono text-[10px] uppercase font-bold tracking-[0.3em] text-[#9A948C] mb-6">
            Error // Status_404
          </p>

          <h1
            style={{
              fontFamily: "'DM Serif Display', serif",
              fontSize: 120,
              lineHeight: 1,
              margin: 0,
            }}
            className="text-[#2A2622] mb-2"
          >
            404
          </h1>

          <p
            style={{ fontFamily: "'DM Serif Display', serif", fontSize: 24 }}
            className="text-[#6B655E] mb-8 italic"
          >
            "Coordinates Lost in the Signal"
          </p>

          <p className="text-[#9A948C] text-sm font-light leading-relaxed mb-10 max-w-sm mx-auto">
            The requested tactical path does not exist in the current foundation. The Council
            suggests retreating to the main command center.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              asChild
              className="bg-[#2A2622] text-white rounded-none h-12 px-8 text-[11px] font-mono font-bold uppercase tracking-widest hover:bg-[#4A4540]"
            >
              <Link href="/daily-wins">
                <ArrowLeftIcon className="mr-2 h-4 w-4" /> Return to Command
              </Link>
            </Button>
            <Button
              asChild
              variant="outline"
              className="border-[#E5DED4] rounded-none h-12 px-8 text-[11px] font-mono font-bold uppercase tracking-widest hover:border-[#D5CBC0] bg-transparent"
            >
              <Link href="/ripples">Scan Ripples</Link>
            </Button>
          </div>
        </div>
      </GsapBridge>
    </div>
  );
}
