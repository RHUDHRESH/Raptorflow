"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import gsap from "gsap";
import { Check, ArrowRight, ListTodo, MessageCircle, Phone, Coffee, Users, Search, Loader2, Sparkles } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { useBCMStore } from "@/stores/bcmStore";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { cn } from "@/lib/utils";

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   PAPER TERMINAL ΓÇö Step 22: Validation Tasks (Reality Check)
   
   PURPOSE: 5 Non-Content Tasks to "Get in Tune".
   - Simple, Checklist UI.
   - Minimalist.
   - Skip or Commit.
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

interface ValidationTask {
    id: string;
    text: string;
    icon: any;
    checked: boolean;
}

const TASKS: ValidationTask[] = [
    { id: "1", text: "Interview 3 'Early Adopter' Founders about their biggest pain point.", icon: Phone, checked: false },
    { id: "2", text: "Test your 'One-Liner' on a stranger (not in tech).", icon: MessageCircle, checked: false },
    { id: "3", text: "Shadow a potential user for 30 mins while they work.", icon: Search, checked: false },
    { id: "4", text: "Ask 5 contacts: 'What is the one thing you'd pay to solve today?'", icon: Users, checked: false },
    { id: "5", text: "Buy a coffee for a competitor's ex-customer.", icon: Coffee, checked: false },
];

export default function Step23ValidationTodos() {
    const { updateStepStatus, getStepById, updateStepData } = useOnboardingStore();
    const { generateFromOnboarding } = useBCMStore();
    const containerRef = useRef<HTMLDivElement>(null);
    const [tasks, setTasks] = useState(TASKS);
    const [isGenerating, setIsGenerating] = useState(false);
    const [launchReadiness, setLaunchReadiness] = useState<any>(null);

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(containerRef.current.querySelectorAll(".animate-task"),
            { opacity: 0, x: -10 },
            { opacity: 1, x: 0, duration: 0.5, stagger: 0.1, ease: "power2.out" }
        );
    }, []);

    const toggleTask = (id: string) => {
        setTasks(tasks.map(t => t.id === id ? { ...t, checked: !t.checked } : t));
    };

    // Fetch AI-generated launch readiness
    const generateLaunchReadiness = useCallback(async () => {
        setIsGenerating(true);
        try {
            // Collect all onboarding data
            const allData: Record<string, any> = {};
            for (let i = 0; i <= 23; i++) {
                const stepData = getStepById(i)?.data;
                if (stepData) {
                    allData[`step_${i}`] = stepData;
                }
            }
            
            const response = await fetch('/api/onboarding/launch-readiness', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: 'demo',
                    onboarding_data: allData
                })
            });
            
            const data = await response.json();
            if (data.success && data.launch_readiness) {
                setLaunchReadiness(data.launch_readiness);
                updateStepData(23, { ...data.launch_readiness, tasks, confirmed: false });
            }
        } catch (err) {
            console.error('Failed to generate launch readiness:', err);
        } finally {
            setIsGenerating(false);
        }
    }, [getStepById, updateStepData]);

    const handleCommit = async () => {
        // Generate BCM from onboarding data before completing
        try {
            const allData: Record<string, any> = {};
            for (let i = 0; i <= 23; i++) {
                const stepData = getStepById(i)?.data;
                if (stepData) {
                    allData[`step_${i}`] = stepData;
                }
            }
            
            await generateFromOnboarding(allData);
        } catch (error) {
            console.error('Failed to generate BCM:', error);
        }
        
        updateStepStatus(22, "complete"); // Map to 22
    };

    return (
        <div ref={containerRef} className="h-full flex flex-col max-w-2xl mx-auto space-y-8 pb-8 justify-center">

            {/* Header */}
            <div className="text-center space-y-3 shrink-0 animate-in fade-in zoom-in duration-500">
                <span className="font-technical text-[10px] tracking-[0.2em] text-[var(--blueprint)] uppercase">Step 22 / 23</span>
                <h2 className="font-serif text-3xl text-[var(--ink)]">Reality Check</h2>
                <div className="flex items-center justify-center gap-2 text-[var(--secondary)]">
                    <ListTodo size={14} />
                    <span className="font-serif italic text-sm">"Get out of the building. Content comes later."</span>
                </div>
                <BlueprintButton 
                    onClick={generateLaunchReadiness} 
                    disabled={isGenerating}
                    size="sm"
                    className="mt-2"
                >
                    {isGenerating ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />}
                    {isGenerating ? "Checking..." : "Check Launch Readiness"}
                </BlueprintButton>
            </div>

            {/* Checklist */}
            <div className="space-y-3">
                {tasks.map((task) => (
                    <div
                        key={task.id}
                        onClick={() => toggleTask(task.id)}
                        className={cn(
                            "animate-task group flex items-center gap-4 p-4 rounded border transition-all cursor-pointer select-none",
                            task.checked
                                ? "bg-[var(--success)]/5 border-[var(--success)]"
                                : "bg-[var(--paper)] border-[var(--border)] hover:border-[var(--blueprint)] hover:translate-x-1"
                        )}
                    >
                        <div className={cn(
                            "w-6 h-6 rounded-full border flex items-center justify-center transition-colors shrink-0",
                            task.checked ? "bg-[var(--success)] border-[var(--success)] text-[var(--paper)]" : "border-[var(--border)] text-transparent group-hover:border-[var(--blueprint)]"
                        )}>
                            <Check size={14} />
                        </div>

                        <div className={cn("p-2 rounded bg-[var(--canvas)] text-[var(--muted)] group-hover:text-[var(--blueprint)] transition-colors shrink-0", task.checked && "text-[var(--success)]")}>
                            <task.icon size={18} />
                        </div>

                        <span className={cn("font-serif text-base text-[var(--ink)]", task.checked && "line-through opacity-60")}>
                            {task.text}
                        </span>
                    </div>
                ))}
            </div>

            {/* Footer */}
            <div className="flex flex-col items-center gap-4 pt-6 animate-in fade-in delay-500">
                <BlueprintButton onClick={handleCommit} size="lg" className="px-12 w-full md:w-auto">
                    <span>Commit to these Actions</span> <ArrowRight size={14} />
                </BlueprintButton>
                <button onClick={handleCommit} className="text-xs text-[var(--muted)] hover:text-[var(--ink)] underline decoration-dotted transition-colors">
                    Skip for now (I promise I'll do them)
                </button>
            </div>

        </div>
    );
}
