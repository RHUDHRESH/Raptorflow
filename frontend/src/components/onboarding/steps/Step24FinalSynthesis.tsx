"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ArrowRight, CheckCheck, Rocket, LayoutDashboard } from "lucide-react";
import { useRouter } from "next/navigation";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintButton } from "@/components/ui/BlueprintButton";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 23: Onboarding Complete
   
   PURPOSE: Celebration & Handover.
   - "Boom! Onboarding is done."
   - Redirect to Global Dashboard.
   - No Export.
   ══════════════════════════════════════════════════════════════════════════════ */

export default function Step23FinalSynthesis() {
    const router = useRouter();
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;

        const tl = gsap.timeline();

        // Initial Reveal
        tl.fromTo(containerRef.current.querySelector(".hero-text"),
            { opacity: 0, scale: 0.9, y: 20 },
            { opacity: 1, scale: 1, y: 0, duration: 1, ease: "power4.out" }
        )
            .fromTo(containerRef.current.querySelector(".sub-text"),
                { opacity: 0, y: 10 },
                { opacity: 1, y: 0, duration: 0.8 },
                "-=0.5"
            )
            .fromTo(containerRef.current.querySelector(".action-btn"),
                { opacity: 0, y: 10 },
                { opacity: 1, y: 0, duration: 0.6 },
                "-=0.4"
            );

    }, []);

    const handleEnterApp = () => {
        // Here we would finalize the session in DB if needed
        router.push("/dashboard");
    };

    return (
        <div ref={containerRef} className="h-full flex flex-col items-center justify-center text-center max-w-2xl mx-auto space-y-8 pb-12">

            <div className="hero-text relative">
                <div className="absolute inset-0 bg-[var(--blueprint)] blur-[100px] opacity-10 rounded-full" />
                <div className="relative z-10 p-6 rounded-full bg-[var(--paper)] border-2 border-[var(--blueprint)] text-[var(--blueprint)] shadow-xl inline-flex mb-8">
                    <Rocket size={48} strokeWidth={1.5} />
                </div>
                <h1 className="relative z-10 font-serif text-5xl md:text-6xl text-[var(--ink)] mb-4">
                    Systems Online.
                </h1>
            </div>

            <p className="sub-text text-xl text-[var(--secondary)] font-serif italic max-w-lg leading-relaxed">
                "Strategy is not an event. It is a discipline."<br />
                Your foundation is built. Now we execute.
            </p>

            <div className="action-btn pt-8">
                <BlueprintButton onClick={handleEnterApp} size="lg" className="px-16 py-8 text-lg shadow-2xl hover:scale-105 transition-transform">
                    <LayoutDashboard size={20} className="mr-3" /> Enter Command Center
                </BlueprintButton>
                <p className="mt-4 text-[10px] uppercase tracking-widest text-[var(--muted)] opacity-60">
                    RaptorFlow OS v1.0 Ready
                </p>
            </div>

        </div>
    );
}
