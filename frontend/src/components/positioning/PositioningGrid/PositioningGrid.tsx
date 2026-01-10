"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import { Plus, X, Sparkles, Expand, Check, AlertTriangle, Users, Layers, Heart, BookOpen, GripVertical } from "lucide-react";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";

/* ══════════════════════════════════════════════════════════════════════════════
   FOUR-COORDINATE POSITIONING GRID

   2×2 Card-based builder for:
   - MARKET: Who you serve
   - CATEGORY: What you are
   - TRIBE: Community/identity
   - STORY: Narrative/why
   ══════════════════════════════════════════════════════════════════════════════ */

export interface PositionCard {
    id: string;
    label: string;
    isCustom?: boolean;
    isSelected?: boolean;
}

export interface QuadrantData {
    id: "market" | "category" | "tribe" | "story";
    title: string;
    description: string;
    icon: React.ElementType;
    color: string;
    cards: PositionCard[];
    selectedCards: string[];
}

export interface PositioningGridData {
    market: QuadrantData;
    category: QuadrantData;
    tribe: QuadrantData;
    story: QuadrantData;
}

// Default card options per quadrant
const DEFAULT_CARDS = {
    market: [
        { id: "m1", label: "SMB (1-50 employees)" },
        { id: "m2", label: "Mid-Market (50-500)" },
        { id: "m3", label: "Enterprise (500+)" },
        { id: "m4", label: "Startups / Early-stage" },
        { id: "m5", label: "Solopreneurs" },
        { id: "m6", label: "Agencies" },
    ],
    category: [
        { id: "c1", label: "CRM" },
        { id: "c2", label: "Project Management" },
        { id: "c3", label: "Analytics Platform" },
        { id: "c4", label: "Marketing Automation" },
        { id: "c5", label: "Communication Tool" },
        { id: "c6", label: "Developer Tool" },
    ],
    tribe: [
        { id: "t1", label: "Growth Teams" },
        { id: "t2", label: "Indie Hackers" },
        { id: "t3", label: "Marketing Leaders" },
        { id: "t4", label: "Product Managers" },
        { id: "t5", label: "Founders" },
        { id: "t6", label: "Developers" },
    ],
    story: [
        { id: "s1", label: "From chaos to clarity" },
        { id: "s2", label: "David vs Goliath" },
        { id: "s3", label: "The underdog wins" },
        { id: "s4", label: "Simplify the complex" },
        { id: "s5", label: "Built by practitioners" },
        { id: "s6", label: "Open and transparent" },
    ],
};

const QUADRANT_CONFIG = {
    market: { title: "Market", description: "Who do you serve?", icon: Users, color: "blueprint" },
    category: { title: "Category", description: "What are you?", icon: Layers, color: "success" },
    tribe: { title: "Tribe", description: "Who's your community?", icon: Heart, color: "warning" },
    story: { title: "Story", description: "What's your narrative?", icon: BookOpen, color: "error" },
};

// Single Quadrant Component
function Quadrant({
    data,
    onCardSelect,
    onAddCard,
    onRemoveCard,
    onExpand,
}: {
    data: QuadrantData;
    onCardSelect: (quadrant: string, cardId: string) => void;
    onAddCard: (quadrant: string, label: string) => void;
    onRemoveCard: (quadrant: string, cardId: string) => void;
    onExpand: () => void;
}) {
    const [isAdding, setIsAdding] = useState(false);
    const [newCardLabel, setNewCardLabel] = useState("");
    const Icon = data.icon;
    const colorClass = `var(--${data.color})`;

    const handleAddCard = () => {
        if (newCardLabel.trim()) {
            onAddCard(data.id, newCardLabel.trim());
            setNewCardLabel("");
            setIsAdding(false);
        }
    };

    return (
        <div className="p-5 rounded-2xl bg-[var(--paper)] border border-[var(--border)] hover:border-[var(--ink)]/30 transition-all">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: `${colorClass}20` }}>
                        <Icon size={18} style={{ color: colorClass }} />
                    </div>
                    <div>
                        <h3 className="font-serif text-lg text-[var(--ink)]">{data.title}</h3>
                        <p className="text-xs text-[var(--secondary)]">{data.description}</p>
                    </div>
                </div>
                <button onClick={onExpand} className="p-2 rounded-lg hover:bg-[var(--canvas)] text-[var(--muted)]">
                    <Expand size={14} />
                </button>
            </div>

            {/* Selected Count */}
            <div className="flex items-center justify-between mb-3">
                <span className="font-technical text-[9px] text-[var(--muted)]">{data.selectedCards.length} SELECTED</span>
                {data.selectedCards.length === 0 && (
                    <BlueprintBadge variant="warning" className="text-[8px]">INCOMPLETE</BlueprintBadge>
                )}
            </div>

            {/* Cards */}
            <div className="space-y-2 max-h-48 overflow-y-auto">
                {data.cards.map((card) => {
                    const isSelected = data.selectedCards.includes(card.id);
                    return (
                        <div
                            key={card.id}
                            onClick={() => onCardSelect(data.id, card.id)}
                            className={`
                                flex items-center justify-between p-3 rounded-xl cursor-pointer transition-all
                                ${isSelected
                                    ? "bg-[var(--ink)] text-[var(--paper)]"
                                    : "bg-[var(--canvas)] text-[var(--ink)] hover:bg-[var(--canvas)]/80"}
                            `}
                        >
                            <span className="text-sm">{card.label}</span>
                            <div className="flex items-center gap-2">
                                {card.isCustom && (
                                    <button
                                        onClick={(e) => { e.stopPropagation(); onRemoveCard(data.id, card.id); }}
                                        className={`p-1 rounded ${isSelected ? "hover:bg-[var(--paper)]/20" : "hover:bg-[var(--error-light)]"}`}
                                    >
                                        <X size={12} className={isSelected ? "" : "text-[var(--error)]"} />
                                    </button>
                                )}
                                {isSelected && <Check size={14} />}
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Add Custom */}
            {isAdding ? (
                <div className="mt-3 flex gap-2">
                    <input
                        type="text"
                        value={newCardLabel}
                        onChange={(e) => setNewCardLabel(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleAddCard()}
                        placeholder="Custom option..."
                        className="flex-1 px-3 py-2 text-sm bg-[var(--canvas)] border border-[var(--border)] rounded-lg focus:outline-none focus:border-[var(--ink)]"
                        autoFocus
                    />
                    <button onClick={handleAddCard} className="p-2 rounded-lg bg-[var(--ink)] text-[var(--paper)]">
                        <Check size={14} />
                    </button>
                    <button onClick={() => setIsAdding(false)} className="p-2 rounded-lg hover:bg-[var(--canvas)] text-[var(--muted)]">
                        <X size={14} />
                    </button>
                </div>
            ) : (
                <button
                    onClick={() => setIsAdding(true)}
                    className="mt-3 w-full py-2 rounded-lg border border-dashed border-[var(--border)] text-[var(--muted)] hover:border-[var(--ink)] hover:text-[var(--ink)] transition-colors flex items-center justify-center gap-2"
                >
                    <Plus size={14} />
                    <span className="text-sm">Add custom</span>
                </button>
            )}
        </div>
    );
}

// Expanded Quadrant View
function ExpandedQuadrant({
    data,
    onCardSelect,
    onAddCard,
    onRemoveCard,
    onClose,
    suggestions,
}: {
    data: QuadrantData;
    onCardSelect: (quadrant: string, cardId: string) => void;
    onAddCard: (quadrant: string, label: string) => void;
    onRemoveCard: (quadrant: string, cardId: string) => void;
    onClose: () => void;
    suggestions?: string[];
}) {
    const Icon = data.icon;
    const colorClass = `var(--${data.color})`;
    const [newCardLabel, setNewCardLabel] = useState("");

    return (
        <div className="fixed inset-0 bg-black/20 z-50 flex items-center justify-center p-8">
            <div className="w-full max-w-3xl bg-[var(--paper)] rounded-2xl shadow-2xl overflow-hidden">
                {/* Header */}
                <div className="p-6 border-b border-[var(--border)] flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="w-14 h-14 rounded-xl flex items-center justify-center" style={{ backgroundColor: `${colorClass}20` }}>
                            <Icon size={24} style={{ color: colorClass }} />
                        </div>
                        <div>
                            <h2 className="font-serif text-2xl text-[var(--ink)]">{data.title}</h2>
                            <p className="text-sm text-[var(--secondary)]">{data.description}</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 rounded-lg hover:bg-[var(--canvas)] text-[var(--muted)]">
                        <X size={20} />
                    </button>
                </div>

                <div className="p-6 grid md:grid-cols-2 gap-6">
                    {/* Options */}
                    <div>
                        <span className="font-technical text-[9px] text-[var(--muted)] block mb-3">OPTIONS</span>
                        <div className="space-y-2 max-h-80 overflow-y-auto">
                            {data.cards.map((card) => {
                                const isSelected = data.selectedCards.includes(card.id);
                                return (
                                    <div
                                        key={card.id}
                                        onClick={() => onCardSelect(data.id, card.id)}
                                        className={`
                                            flex items-center justify-between p-4 rounded-xl cursor-pointer transition-all
                                            ${isSelected
                                                ? "bg-[var(--ink)] text-[var(--paper)]"
                                                : "bg-[var(--canvas)] text-[var(--ink)] hover:bg-[var(--canvas)]/80"}
                                        `}
                                    >
                                        <span>{card.label}</span>
                                        {isSelected && <Check size={16} />}
                                    </div>
                                );
                            })}
                        </div>

                        {/* Add Custom */}
                        <div className="mt-4 flex gap-2">
                            <input
                                type="text"
                                value={newCardLabel}
                                onChange={(e) => setNewCardLabel(e.target.value)}
                                onKeyDown={(e) => {
                                    if (e.key === "Enter" && newCardLabel.trim()) {
                                        onAddCard(data.id, newCardLabel.trim());
                                        setNewCardLabel("");
                                    }
                                }}
                                placeholder="Add custom option..."
                                className="flex-1 px-4 py-3 text-sm bg-[var(--canvas)] border border-[var(--border)] rounded-xl focus:outline-none focus:border-[var(--ink)]"
                            />
                            <button
                                onClick={() => {
                                    if (newCardLabel.trim()) {
                                        onAddCard(data.id, newCardLabel.trim());
                                        setNewCardLabel("");
                                    }
                                }}
                                className="px-4 py-3 rounded-xl bg-[var(--ink)] text-[var(--paper)]"
                            >
                                <Plus size={16} />
                            </button>
                        </div>
                    </div>

                    {/* AI Suggestions */}
                    <div>
                        <div className="flex items-center gap-2 mb-3">
                            <Sparkles size={14} className="text-[var(--blueprint)]" />
                            <span className="font-technical text-[9px] text-[var(--blueprint)]">AI SUGGESTIONS</span>
                        </div>
                        <div className="p-4 rounded-xl bg-[var(--blueprint-light)] border border-[var(--blueprint)]/30">
                            <p className="text-sm text-[var(--secondary)] mb-4">
                                Based on your competitors and market gaps, consider:
                            </p>
                            <div className="space-y-2">
                                {(suggestions || ["No suggestions yet"]).map((s, i) => (
                                    <button
                                        key={i}
                                        onClick={() => onAddCard(data.id, s)}
                                        className="w-full text-left p-3 rounded-lg bg-[var(--paper)] hover:bg-[var(--canvas)] text-sm text-[var(--ink)] transition-colors"
                                    >
                                        + {s}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="p-6 border-t border-[var(--border)] flex justify-end">
                    <BlueprintButton onClick={onClose}>
                        <Check size={14} />Done
                    </BlueprintButton>
                </div>
            </div>
        </div>
    );
}

// Main Grid Component
export interface PositioningGridProps {
    data?: PositioningGridData;
    onChange?: (data: PositioningGridData) => void;
    className?: string;
}

export function PositioningGrid({ data, onChange, className = "" }: PositioningGridProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const [expandedQuadrant, setExpandedQuadrant] = useState<string | null>(null);

    // Initialize data
    const [gridData, setGridData] = useState<PositioningGridData>(() => {
        if (data) return data;
        return {
            market: { ...QUADRANT_CONFIG.market, id: "market", cards: DEFAULT_CARDS.market.map(c => ({ ...c })), selectedCards: [] },
            category: { ...QUADRANT_CONFIG.category, id: "category", cards: DEFAULT_CARDS.category.map(c => ({ ...c })), selectedCards: [] },
            tribe: { ...QUADRANT_CONFIG.tribe, id: "tribe", cards: DEFAULT_CARDS.tribe.map(c => ({ ...c })), selectedCards: [] },
            story: { ...QUADRANT_CONFIG.story, id: "story", cards: DEFAULT_CARDS.story.map(c => ({ ...c })), selectedCards: [] },
        };
    });

    useEffect(() => {
        if (!containerRef.current) return;
        gsap.fromTo(containerRef.current.querySelectorAll("[data-animate]"), { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.4, stagger: 0.08, ease: "power2.out" });
    }, []);

    const updateData = (newData: PositioningGridData) => {
        setGridData(newData);
        onChange?.(newData);
    };

    const handleCardSelect = (quadrant: string, cardId: string) => {
        const q = gridData[quadrant as keyof PositioningGridData];
        const isSelected = q.selectedCards.includes(cardId);
        const newSelected = isSelected
            ? q.selectedCards.filter(id => id !== cardId)
            : [...q.selectedCards, cardId];

        updateData({
            ...gridData,
            [quadrant]: { ...q, selectedCards: newSelected },
        });
    };

    const handleAddCard = (quadrant: string, label: string) => {
        const q = gridData[quadrant as keyof PositioningGridData];
        const newCard: PositionCard = { id: `custom-${Date.now()}`, label, isCustom: true };
        updateData({
            ...gridData,
            [quadrant]: { ...q, cards: [...q.cards, newCard], selectedCards: [...q.selectedCards, newCard.id] },
        });
    };

    const handleRemoveCard = (quadrant: string, cardId: string) => {
        const q = gridData[quadrant as keyof PositioningGridData];
        updateData({
            ...gridData,
            [quadrant]: {
                ...q,
                cards: q.cards.filter(c => c.id !== cardId),
                selectedCards: q.selectedCards.filter(id => id !== cardId),
            },
        });
    };

    const expandedData = expandedQuadrant ? gridData[expandedQuadrant as keyof PositioningGridData] : null;
    const completeness = Object.values(gridData).filter(q => q.selectedCards.length > 0).length;

    return (
        <div ref={containerRef} className={className}>
            {/* Header */}
            <div data-animate className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="font-serif text-2xl text-[var(--ink)]">Positioning Grid</h2>
                    <p className="text-sm text-[var(--secondary)]">Define your market, category, tribe, and story</p>
                </div>
                <div className="flex items-center gap-2">
                    <span className="font-technical text-[10px] text-[var(--muted)]">{completeness}/4 COMPLETE</span>
                    {completeness < 4 && <AlertTriangle size={14} className="text-[var(--warning)]" />}
                    {completeness === 4 && <Check size={14} className="text-[var(--success)]" />}
                </div>
            </div>

            {/* 2×2 Grid */}
            <div data-animate className="grid md:grid-cols-2 gap-4">
                {(["market", "category", "tribe", "story"] as const).map((key) => (
                    <Quadrant
                        key={key}
                        data={gridData[key]}
                        onCardSelect={handleCardSelect}
                        onAddCard={handleAddCard}
                        onRemoveCard={handleRemoveCard}
                        onExpand={() => setExpandedQuadrant(key)}
                    />
                ))}
            </div>

            {/* Expanded View */}
            {expandedData && (
                <ExpandedQuadrant
                    data={expandedData}
                    onCardSelect={handleCardSelect}
                    onAddCard={handleAddCard}
                    onRemoveCard={handleRemoveCard}
                    onClose={() => setExpandedQuadrant(null)}
                    suggestions={[
                        "Underserved mid-market segment",
                        "Technical teams with non-technical needs",
                        "Fast-growing remote teams",
                    ]}
                />
            )}
        </div>
    );
}

export default PositioningGrid;
