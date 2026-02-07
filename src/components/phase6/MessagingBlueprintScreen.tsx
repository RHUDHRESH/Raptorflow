'use client';

import React from 'react';
import { MessagingBlueprint, MessagingPillar } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ArrowRight, AlertTriangle, Check, Layers } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MessagingBlueprintScreenProps {
    blueprint: MessagingBlueprint;
    onChange: (blueprint: MessagingBlueprint) => void;
    onContinue: () => void;
}

function PillarCard({
    pillar,
    onUpdate,
}: {
    pillar: MessagingPillar;
    onUpdate: (pillar: MessagingPillar) => void;
}) {
    return (
        <div className={cn(
            "p-4 rounded-xl border-2 transition-all",
            pillar.isProven
                ? "border-green-500 bg-green-50/30 dark:bg-green-950/20"
                : "border-dashed border-amber-500 bg-amber-50/30 dark:bg-amber-950/20"
        )}>
            <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                        <span className="bg-muted px-2 py-0.5 rounded text-xs font-medium">
                            #{pillar.priority}
                        </span>
                        <input
                            type="text"
                            value={pillar.name}
                            onChange={(e) => onUpdate({ ...pillar, name: e.target.value })}
                            className="font-semibold bg-transparent border-none focus:outline-none focus:ring-1 focus:ring-primary rounded px-1"
                        />
                    </div>
                    <div className="flex items-center gap-2">
                        {pillar.isProven ? (
                            <span className="text-xs text-green-600 flex items-center gap-1">
                                <Check className="h-3 w-3" /> Proven
                            </span>
                        ) : (
                            <span className="text-xs text-amber-600 flex items-center gap-1">
                                <AlertTriangle className="h-3 w-3" /> Needs proof
                            </span>
                        )}
                        <span className="text-xs text-muted-foreground">
                            {pillar.proofIds.length} proof attached
                        </span>
                    </div>
                </div>
                <button
                    onClick={() => onUpdate({ ...pillar, isProven: !pillar.isProven })}
                    className={cn(
                        "px-3 py-1 rounded-lg text-xs transition-colors",
                        pillar.isProven
                            ? "bg-green-100 text-green-700 dark:bg-green-900/30"
                            : "bg-muted text-muted-foreground hover:bg-muted/80"
                    )}
                >
                    {pillar.isProven ? 'Mark Unproven' : 'Mark Proven'}
                </button>
            </div>
        </div>
    );
}

export function MessagingBlueprintScreen({ blueprint, onChange, onContinue }: MessagingBlueprintScreenProps) {
    const handlePillarUpdate = (pillerId: string, updatedPillar: MessagingPillar) => {
        onChange({
            ...blueprint,
            pillars: blueprint.pillars.map(p => p.id === pillerId ? updatedPillar : p)
        });
    };

    const provenCount = blueprint.pillars.filter(p => p.isProven).length;

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="text-center space-y-2">
                <h1 className="text-3xl font-serif font-bold text-foreground">
                    Messaging Blueprint
                </h1>
                <p className="text-muted-foreground max-w-lg mx-auto">
                    Your messaging hierarchy. Core → Pillars → Proof.
                </p>
            </div>

            {/* Controlling Idea */}
            <div className="max-w-2xl mx-auto">
                <label className="text-sm font-medium text-muted-foreground block mb-2">
                    Controlling Idea (Single Sentence)
                </label>
                <Textarea
                    value={blueprint.controllingIdea}
                    onChange={(e) => onChange({ ...blueprint, controllingIdea: e.target.value })}
                    className="min-h-[80px] text-lg"
                    placeholder="The moral of the story..."
                />
            </div>

            {/* Core Message */}
            <div className="max-w-2xl mx-auto">
                <label className="text-sm font-medium text-muted-foreground block mb-2">
                    Core Message
                </label>
                <Textarea
                    value={blueprint.coreMessage}
                    onChange={(e) => onChange({ ...blueprint, coreMessage: e.target.value })}
                    className="min-h-[60px]"
                    placeholder="For [segment], we deliver [value]..."
                />
            </div>

            {/* Pillars */}
            <div className="max-w-2xl mx-auto">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                        <Layers className="h-5 w-5 text-muted-foreground" />
                        <h2 className="font-semibold">Messaging Pillars</h2>
                    </div>
                    <span className={cn(
                        "text-sm font-medium",
                        provenCount === blueprint.pillars.length ? "text-green-600" : "text-amber-600"
                    )}>
                        {provenCount}/{blueprint.pillars.length} proven
                    </span>
                </div>
                <div className="space-y-3">
                    {blueprint.pillars.map(pillar => (
                        <PillarCard
                            key={pillar.id}
                            pillar={pillar}
                            onUpdate={(p) => handlePillarUpdate(pillar.id, p)}
                        />
                    ))}
                </div>
            </div>

            {/* Missing Proof Alerts */}
            {blueprint.missingProofAlerts.length > 0 && (
                <div className="max-w-2xl mx-auto">
                    <div className="bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900 rounded-xl p-4">
                        <h3 className="font-medium text-amber-700 dark:text-amber-400 mb-2 flex items-center gap-2">
                            <AlertTriangle className="h-4 w-4" /> Missing Proof
                        </h3>
                        <ul className="text-sm text-amber-600 dark:text-amber-400 space-y-1">
                            {blueprint.missingProofAlerts.map((alert, i) => (
                                <li key={i}>• {alert}</li>
                            ))}
                        </ul>
                    </div>
                </div>
            )}

            {/* Continue Button */}
            <div className="flex justify-center pt-4">
                <Button size="lg" onClick={onContinue} className="px-8 py-6 text-lg rounded-xl">
                    Continue <ArrowRight className="h-5 w-5 ml-2" />
                </Button>
            </div>
        </div>
    );
}
