import type * as React from "react";
import Link from "next/link";
import { GsapBridge } from "@/components/ui/gsap-bridge";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <main className="min-h-screen bg-[var(--background)] text-[var(--foreground)] flex">
      {/* Left Branding Pane */}
      <div className="hidden lg:flex flex-col justify-between w-1/2 p-12 bg-[#100E0F] text-[#F3F0E7] border-r border-[#332D2F]">
        <Link href="/" className="font-[family-name:var(--font-display)] text-3xl font-bold tracking-tight">RAPTORFLOW</Link>
        <GsapBridge stagger={true}>
          <div className="space-y-6 max-w-lg mb-20">
            <h1 className="gsap-reveal font-[family-name:var(--font-display)] text-5xl leading-tight">
              A council of 21 strategists awaits.
            </h1>
            <p className="gsap-reveal text-[#EAE6DB]/70 font-mono text-sm leading-loose uppercase tracking-widest">
              Stop managing a tool. Start managing a team.
            </p>
          </div>
        </GsapBridge>
      </div>

      {/* Right Auth Pane */}
      <div className="flex-1 flex flex-col items-center justify-center p-6 relative">
        <div className="absolute top-6 right-6 lg:hidden font-[family-name:var(--font-display)] text-xl font-bold">RAPTORFLOW</div>
        <GsapBridge className="w-full flex justify-center" stagger={true}>
          <div className="gsap-reveal w-full max-w-md">
            {children}
          </div>
        </GsapBridge>
      </div>
    </main>
  );
}
