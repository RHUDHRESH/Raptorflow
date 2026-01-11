"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import { Check, Target, Plus, Trash2, SkipForward, Zap, AlertCircle } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintProgress } from "@/components/ui/BlueprintProgress";
import { OnboardingStepLayout } from "../OnboardingStepLayout";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Step 23: Validation Todos (OPTIONAL)

   Reframed as optional — users can skip to Final Synthesis
   Track positioning validation tasks for post-onboarding
   ══════════════════════════════════════════════════════════════════════════════ */

interface TodoItem {
    id: string;
    category: "messaging" | "positioning" | "icp" | "content";
    task: string;
    priority: "high" | "medium" | "low";
    completed: boolean;
    code: string;
}

const INITIAL_TODOS: TodoItem[] = [
    { id: "1", category: "messaging", task: "Test elevator pitch with 5 prospects", priority: "high", completed: false, code: "TODO-01" },
    { id: "2", category: "positioning", task: "Validate differentiation claims with customers", priority: "high", completed: false, code: "TODO-02" },
    { id: "3", category: "icp", task: "Interview 3 ideal customers about pain points", priority: "medium", completed: false, code: "TODO-03" },
    { id: "4", category: "content", task: "Create social proof content from validated claims", priority: "medium", completed: false, code: "TODO-04" },
    { id: "5", category: "messaging", task: "A/B test tagline variations", priority: "low", completed: false, code: "TODO-05" },
];

const priorityConfig = {
    high: { label: "HIGH", color: "text-[var(--error)]", bg: "bg-[var(--error-light)]" },
    medium: { label: "MED", color: "text-[var(--warning)]", bg: "bg-[var(--warning-light)]" },
    low: { label: "LOW", color: "text-[var(--muted)]", bg: "bg-[var(--canvas)]" }
};

const categoryConfig = {
    messaging: { label: "MESSAGING", color: "text-[var(--blueprint)]" },
    positioning: { label: "POSITIONING", color: "text-[var(--success)]" },
    icp: { label: "ICP", color: "text-[var(--warning)]" },
    content: { label: "CONTENT", color: "text-[var(--muted)]" }
};

export default function Step23ValidationTodos() {
    const { updateStepData, updateStepStatus, getStepById } = useOnboardingStore();
    const stepData = getStepById(23)?.data as { todos?: TodoItem[]; confirmed?: boolean; skipped?: boolean } | undefined;
    const [todos, setTodos] = useState<TodoItem[]>(stepData?.todos || INITIAL_TODOS);
    const [isAdding, setIsAdding] = useState(false);
    const [newTodo, setNewTodo] = useState<{ task: string; category: TodoItem["category"]; priority: TodoItem["priority"] }>({ task: "", category: "messaging", priority: "medium" });
    const [confirmed, setConfirmed] = useState(stepData?.confirmed || false);
    const [skipped, setSkipped] = useState(stepData?.skipped || false);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(
            containerRef.current.querySelectorAll("[data-animate]"),
            { opacity: 0, y: 16 },
            { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" }
        );
    }, []);

    const saveData = (items: TodoItem[]) => {
        setTodos(items);
        updateStepData(23, { todos: items });
    };

    const toggleComplete = (id: string) => saveData(todos.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t)));
    const removeTodo = (id: string) => saveData(todos.filter((t) => t.id !== id));

    const addTodo = () => {
        if (!newTodo.task.trim()) return;
        const item: TodoItem = {
            id: `todo-${Date.now()}`,
            ...newTodo,
            completed: false,
            code: `TODO-${String(todos.length + 1).padStart(2, "0")}`
        };
        saveData([...todos, item]);
        setNewTodo({ task: "", category: "messaging", priority: "medium" });
        setIsAdding(false);
    };

    const handleConfirm = () => {
        setConfirmed(true);
        updateStepData(23, { todos, confirmed: true, skipped: false });
        updateStepStatus(23, "complete");
    };

    const handleSkip = () => {
        setSkipped(true);
        updateStepData(23, { todos, confirmed: false, skipped: true });
        updateStepStatus(23, "complete");
    };

    const completedCount = todos.filter((t) => t.completed).length;
    const highPriorityCount = todos.filter((t) => t.priority === "high" && !t.completed).length;

    if (confirmed || skipped) {
        return (
            <div ref={containerRef} className="space-y-6">
                <BlueprintCard data-animate showCorners padding="lg" className={skipped ? "border-[var(--warning)]/30 bg-[var(--warning-light)]" : "border-[var(--success)]/30 bg-[var(--success-light)]"}>
                    <div className="flex items-center gap-4">
                        <div className={`w-14 h-14 rounded-xl ${skipped ? "bg-[var(--warning)]" : "bg-[var(--success)]"} flex items-center justify-center`}>
                            {skipped ? <SkipForward size={24} className="text-[var(--paper)]" /> : <Check size={24} className="text-[var(--paper)]" />}
                        </div>
                        <div>
                            <span className="text-lg font-serif text-[var(--ink)]">
                                {skipped ? "Validation Skipped" : "Validation Plan Ready"}
                            </span>
                            <p className="text-sm text-[var(--secondary)]">
                                {skipped
                                    ? "You can set up validation tasks later from your dashboard"
                                    : `${todos.length} tasks to validate your positioning`}
                            </p>
                        </div>
                        <BlueprintBadge variant={skipped ? "warning" : "success"} dot className="ml-auto">
                            {skipped ? "SKIPPED" : "COMPLETE"}
                        </BlueprintBadge>
                    </div>
                </BlueprintCard>
                <div className="flex justify-center pt-4">
                    <span className="font-technical text-[var(--muted)]">VALIDATION-TASKS • STEP 22/24 • OPTIONAL</span>
                </div>
            </div>
        );
    }

    return (
        <OnboardingStepLayout stepId={23} moduleLabel="VALIDATION" itemCount={todos.length}>
            <div ref={containerRef} className="space-y-6">
                {/* Header with Optional Badge */}
                <div data-animate className="text-center py-4">
                    <div className="inline-flex items-center gap-2 mb-2">
                        <h2 className="text-2xl font-serif text-[var(--ink)]">Validation Roadmap</h2>
                        <BlueprintBadge variant="warning">OPTIONAL</BlueprintBadge>
                    </div>
                    <p className="text-sm text-[var(--secondary)] max-w-lg mx-auto">
                        These are post-launch tasks to validate your positioning with real prospects.
                        You can skip this and set it up later, or customize your validation plan now.
                    </p>
                </div>

                {/* Skip Option */}
                <BlueprintCard data-animate showCorners padding="md" className="border-[var(--warning)]/30 bg-[var(--warning-light)]">
                    <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-[var(--warning)] flex items-center justify-center">
                            <SkipForward size={16} className="text-[var(--paper)]" />
                        </div>
                        <div className="flex-1">
                            <span className="text-sm font-medium text-[var(--ink)]">Skip for now?</span>
                            <p className="text-xs text-[var(--secondary)]">You can set up validation tasks from your dashboard later</p>
                        </div>
                        <SecondaryButton size="sm" onClick={handleSkip}>
                            Skip to Final
                        </SecondaryButton>
                    </div>
                </BlueprintCard>

                {/* Progress */}
                <BlueprintCard data-animate figure="FIG. 01" title="Progress" code="PROG" showCorners padding="md">
                    <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-4">
                            <span className="text-sm font-medium text-[var(--ink)]">{completedCount} of {todos.length} complete</span>
                            {highPriorityCount > 0 && (
                                <span className="flex items-center gap-1 text-xs text-[var(--error)]">
                                    <AlertCircle size={10} />{highPriorityCount} high priority
                                </span>
                            )}
                        </div>
                        <span className="font-technical text-[var(--muted)]">{Math.round((completedCount / todos.length) * 100)}%</span>
                    </div>
                    <BlueprintProgress value={(completedCount / todos.length) * 100} />
                </BlueprintCard>

                {/* Todo List */}
                <div data-animate className="space-y-2">
                    {todos.map((todo) => (
                        <div
                            key={todo.id}
                            className={`
                            flex items-center gap-4 p-4 rounded-xl border transition-all
                            ${todo.completed
                                    ? "bg-[var(--canvas)] border-[var(--border)] opacity-60"
                                    : "bg-[var(--paper)] border-[var(--border)] hover:border-[var(--blueprint)]/50"}
                        `}
                        >
                            <button
                                onClick={() => toggleComplete(todo.id)}
                                className={`
                                w-6 h-6 rounded-lg border-2 flex items-center justify-center transition-all
                                ${todo.completed ? "bg-[var(--success)] border-[var(--success)]" : "border-[var(--border)] hover:border-[var(--success)]"}
                            `}
                            >
                                {todo.completed && <Check size={12} strokeWidth={2} className="text-[var(--paper)]" />}
                            </button>
                            <div className="flex-1 min-w-0">
                                <p className={`text-sm ${todo.completed ? "line-through text-[var(--muted)]" : "text-[var(--ink)]"}`}>
                                    {todo.task}
                                </p>
                                <span className={`font-technical text-[9px] ${categoryConfig[todo.category].color}`}>
                                    {categoryConfig[todo.category].label}
                                </span>
                            </div>
                            <span className={`font-technical text-[8px] px-2 py-0.5 rounded-full ${priorityConfig[todo.priority].bg} ${priorityConfig[todo.priority].color}`}>
                                {priorityConfig[todo.priority].label}
                            </span>
                            <button
                                onClick={() => removeTodo(todo.id)}
                                className="p-1.5 text-[var(--muted)] hover:text-[var(--error)] hover:bg-[var(--error-light)] rounded-lg transition-all"
                            >
                                <Trash2 size={12} strokeWidth={1.5} />
                            </button>
                        </div>
                    ))}
                </div>

                {/* Add New */}
                {isAdding ? (
                    <BlueprintCard data-animate code="NEW" showCorners padding="md" className="border-[var(--blueprint)]">
                        <div className="space-y-4">
                            <input
                                type="text"
                                value={newTodo.task}
                                onChange={(e) => setNewTodo({ ...newTodo, task: e.target.value })}
                                placeholder="What do you need to validate?"
                                className="w-full h-10 px-4 text-sm bg-[var(--paper)] border border-[var(--border)] rounded-lg text-[var(--ink)] placeholder:text-[var(--placeholder)] focus:outline-none focus:border-[var(--blueprint)]"
                                autoFocus
                            />
                            <div className="flex gap-2">
                                {(["high", "medium", "low"] as const).map((p) => (
                                    <button
                                        key={p}
                                        onClick={() => setNewTodo({ ...newTodo, priority: p })}
                                        className={`
                                        flex-1 px-3 py-2 font-technical text-[10px] rounded-lg capitalize transition-all
                                        ${newTodo.priority === p
                                                ? `${priorityConfig[p].bg} ${priorityConfig[p].color} ring-2 ring-offset-2`
                                                : "bg-[var(--canvas)] text-[var(--muted)]"}
                                    `}
                                    >
                                        {p}
                                    </button>
                                ))}
                            </div>
                            <div className="flex gap-2">
                                <BlueprintButton size="sm" onClick={addTodo}>Add Task</BlueprintButton>
                                <SecondaryButton size="sm" onClick={() => setIsAdding(false)}>Cancel</SecondaryButton>
                            </div>
                        </div>
                    </BlueprintCard>
                ) : (
                    <SecondaryButton data-animate onClick={() => setIsAdding(true)} className="w-full">
                        <Plus size={12} strokeWidth={1.5} />Add Validation Task
                    </SecondaryButton>
                )}

                {/* Confirm */}
                <BlueprintButton data-animate size="lg" onClick={handleConfirm} className="w-full" label="BTN-CONFIRM">
                    <Target size={14} strokeWidth={1.5} />Save Validation Plan
                </BlueprintButton>

            </div>
        </OnboardingStepLayout>
    );
}
