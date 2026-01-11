"use client";

import { useRef, useEffect, useState } from "react";
import gsap from "gsap";
import { cn } from "@/lib/utils";
import { MoveCategory, MoveCategoryInfo, MOVE_CATEGORIES } from "./types";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { ArrowRight, CheckCircle2 } from "lucide-react";

interface MoveCategorySelectorProps {
    selected: MoveCategory | null;
    onSelect: (category: MoveCategory) => void;
    className?: string;
}

export function MoveCategorySelector({ selected, onSelect, className }: MoveCategorySelectorProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const categories = Object.values(MOVE_CATEGORIES);

    useEffect(() => {
        if (!containerRef.current) return;
        const cards = containerRef.current.querySelectorAll("[data-category-card]");
        gsap.fromTo(
            cards,
            { opacity: 0, scale: 0.95 },
            { opacity: 1, scale: 1, duration: 0.5, stagger: 0.05, ease: "back.out(1.5)" }
        );
    }, []);

    return (
        <div ref={containerRef} className={cn("space-y-6", className)}>
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="space-y-2">
                    <div className="flex items-center gap-3">
                        <span className="font-technical text-[var(--blueprint)]">PHASE-01</span>
                        <div className="h-px w-12 bg-[var(--blueprint-line)]" />
                        <span className="font-technical text-[var(--muted)]">SELECTION</span>
                    </div>
                    <h2 className="font-serif text-2xl text-[var(--ink)]">Select Tactical Approach</h2>
                </div>
                <span className="text-xs font-mono text-[var(--muted)]">{categories.length} MODULES AVAILABLE</span>
            </div>

            {/* Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {categories.map((category) => (
                    <CategoryTile
                        key={category.id}
                        category={category}
                        isSelected={selected === category.id}
                        onClick={() => onSelect(category.id)}
                    />
                ))}
            </div>
        </div>
    );
}

function CategoryTile({ category, isSelected, onClick }: { category: MoveCategoryInfo, isSelected: boolean, onClick: () => void }) {
    return (
        <div
            data-category-card
            onClick={onClick}
            className={cn(
                "group relative p-6 rounded-[var(--radius-md)] border transition-all duration-300 cursor-pointer overflow-hidden",
                isSelected
                    ? "bg-[var(--ink)] border-[var(--ink)] text-[var(--paper)] shadow-xl scale-[1.02]"
                    : "bg-[var(--paper)] border-[var(--border)] hover:border-[var(--blueprint)] hover:shadow-lg hover:-translate-y-1"
            )}
        >
            {/* Background Texture for Selected */}
            {isSelected && (
                <div className="absolute inset-0 pointer-events-none opacity-10" style={{ backgroundImage: "url('/textures/paper-grain.png')" }} />
            )}

            {/* Selection Check */}
            <div className={cn(
                "absolute top-4 right-4 transition-all duration-300",
                isSelected ? "opacity-100 scale-100" : "opacity-0 scale-50"
            )}>
                <CheckCircle2 size={24} className="text-[var(--success)]" fill="currentColor" />
            </div>

            <div className="relative z-10">
                <div className="text-4xl mb-4 transform group-hover:scale-110 transition-transform duration-300 origin-left">{category.emoji}</div>

                <h3 className={cn("font-serif text-xl mb-2", isSelected ? "text-[var(--paper)]" : "text-[var(--ink)]")}>
                    {category.name}
                </h3>

                <p className={cn("text-sm mb-6 leading-relaxed", isSelected ? "text-[var(--paper)]/80" : "text-[var(--secondary)]")}>
                    {category.description}
                </p>

                <div className="flex flex-wrap gap-2 mb-4">
                    {category.useFor.slice(0, 2).map(tag => (
                        <span key={tag} className={cn(
                            "text-[10px] uppercase tracking-wider px-2 py-1 rounded",
                            isSelected ? "bg-[var(--paper)]/20 text-[var(--paper)]" : "bg-[var(--canvas)] text-[var(--muted)] border border-[var(--border)]"
                        )}>
                            {tag}
                        </span>
                    ))}
                </div>

                <div className={cn(
                    "flex items-center gap-2 text-xs font-bold uppercase tracking-widest transition-opacity",
                    isSelected ? "text-[var(--blueprint-light)]" : "text-[var(--blueprint)] opacity-0 group-hover:opacity-100"
                )}>
                    <span>Initialize</span>
                    <ArrowRight size={12} />
                </div>
            </div>
        </div>
    );
}

export default MoveCategorySelector;
