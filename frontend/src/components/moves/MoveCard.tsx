"use client";

import { useRef, useEffect } from "react";
import gsap from "gsap";
import { Check, MoreHorizontal, Calendar, User, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { StatusDot, Status, StatusType } from "./StatusDot";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — MoveCard
   Task/action card with blueprint registration marks
   ══════════════════════════════════════════════════════════════════════════════ */

export type { Status, StatusType };

export interface Move {
    id: string;
    title: string;
    description?: string;
    status: Status;
    dueDate?: string;
    assignee?: string;
    campaign?: string;
    code?: string;
}

interface MoveCardProps {
    move: Move;
    onClick?: () => void;
    onStatusChange?: (status: Status) => void;
    onEdit?: () => void;
    onDelete?: () => void;
    className?: string;
    index?: number;
}

export function MoveCard({ move, onClick, onStatusChange, onEdit, onDelete, className, index = 0 }: MoveCardProps) {
    const isCompleted = move.status === "done";
    const cardRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!cardRef.current) return;
        gsap.fromTo(cardRef.current, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.4, delay: index * 0.06, ease: "power2.out" });
    }, [index]);

    const handleMouseEnter = () => {
        if (cardRef.current) gsap.to(cardRef.current, { y: -4, duration: 0.3, ease: "power2.out" });
    };

    const handleMouseLeave = () => {
        if (cardRef.current) gsap.to(cardRef.current, { y: 0, duration: 0.3, ease: "power2.out" });
    };

    return (
        <BlueprintCard
            ref={cardRef}
            code={move.code || `MV-${move.id.slice(0, 4).toUpperCase()}`}
            showCorners
            padding="md"
            className={cn("cursor-pointer group", isCompleted && "opacity-75", className)}
            onClick={onClick}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            style={{ opacity: 0 }}
        >
            {/* Header */}
            <div className="flex items-start gap-4 mb-3">
                <div className="pt-1.5">
                    <StatusDot status={move.status} size="lg" pulse={move.status === "in-progress" || move.status === "attention"} />
                </div>
                <div className="flex-1 min-w-0">
                    <h3 className={cn("text-base font-semibold text-[var(--ink)] mb-1 group-hover:text-[var(--blueprint)] transition-colors", isCompleted && "line-through decoration-[var(--muted)]")}>
                        {move.title}
                    </h3>
                    {move.description && (
                        <p className="text-sm text-[var(--secondary)] line-clamp-2">{move.description}</p>
                    )}
                </div>
                <button onClick={(e) => { e.stopPropagation(); }} className="p-1.5 rounded-[var(--radius-xs)] text-[var(--muted)] opacity-0 group-hover:opacity-100 hover:bg-[var(--canvas)] transition-all">
                    <MoreHorizontal size={14} strokeWidth={1.5} />
                </button>
            </div>

            {/* Meta */}
            <div className="flex items-center justify-between pt-3 border-t border-[var(--border-subtle)]">
                <div className="flex items-center gap-4 font-technical text-[var(--muted)]">
                    {move.dueDate && (
                        <span className="flex items-center gap-1.5"><Calendar size={10} strokeWidth={1.5} />{move.dueDate}</span>
                    )}
                    {move.assignee && (
                        <span className="flex items-center gap-1.5"><User size={10} strokeWidth={1.5} />{move.assignee}</span>
                    )}
                    {move.campaign && <BlueprintBadge variant="default">{move.campaign}</BlueprintBadge>}
                </div>

                <button
                    onClick={(e) => { e.stopPropagation(); onStatusChange?.(isCompleted ? "in-progress" : "done"); }}
                    className={cn(
                        "flex items-center gap-2 px-3 py-1.5 rounded-[var(--radius-sm)] font-technical transition-all",
                        isCompleted
                            ? "bg-[var(--success-light)] text-[var(--success)] border border-[var(--success)]/20"
                            : "text-[var(--muted)] hover:bg-[var(--canvas)] hover:text-[var(--blueprint)]"
                    )}
                >
                    <div className={cn(
                        "flex h-4 w-4 items-center justify-center rounded-full border-2 transition-all",
                        isCompleted ? "border-[var(--success)] bg-[var(--success)]" : "border-[var(--border)]"
                    )}>
                        {isCompleted && <Check size={8} strokeWidth={2.5} className="text-[var(--paper)]" />}
                    </div>
                    {isCompleted ? "DONE" : "COMPLETE"}
                </button>
            </div>
        </BlueprintCard>
    );
}
