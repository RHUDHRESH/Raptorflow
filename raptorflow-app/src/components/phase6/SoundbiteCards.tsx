'use client';

import React from 'react';
import { Soundbite, RigorScores, SoundbiteType } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import {
    Carousel,
    CarouselContent,
    CarouselItem,
    CarouselNext,
    CarouselPrevious,
} from "@/components/ui/carousel"
import {
    ContextMenu,
    ContextMenuContent,
    ContextMenuItem,
    ContextMenuTrigger,
} from "@/components/ui/context-menu"
import { ArrowRight, Lock, Unlock, RefreshCw, Check, AlertTriangle, X, Copy, Wand2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

interface SoundbiteCardsProps {
    soundbites: Soundbite[];
    onChange: (soundbites: Soundbite[]) => void;
    onRegenerate: (id: string) => void;
    onContinue: () => void;
}

const TYPE_LABELS: Record<SoundbiteType, { label: string; color: string }> = {
    'problem-reveal': { label: 'Problem Reveal', color: 'text-red-600 bg-red-100 dark:bg-red-900/30' },
    'agitate': { label: 'Agitate', color: 'text-orange-600 bg-orange-100 dark:bg-orange-900/30' },
    'jtbd-progress': { label: 'JTBD Progress', color: 'text-blue-600 bg-blue-100 dark:bg-blue-900/30' },
    'mechanism': { label: 'Mechanism', color: 'text-purple-600 bg-purple-100 dark:bg-purple-900/30' },
    'proof-punch': { label: 'Proof Punch', color: 'text-green-600 bg-green-100 dark:bg-green-900/30' },
    'objection-kill': { label: 'Objection Kill', color: 'text-amber-600 bg-amber-100 dark:bg-amber-900/30' },
    'action': { label: 'Action', color: 'text-teal-600 bg-teal-100 dark:bg-teal-900/30' }
};

function ScoreGate({ label, value, passing }: { label: string; value: number; passing: boolean }) {
    return (
        <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground w-12">{label}</span>
            <div className="flex gap-0.5">
                {[1, 2, 3, 4, 5].map(i => (
                    <div
                        key={i}
                        className={cn(
                            "w-3 h-3 rounded-sm",
                            i <= value
                                ? passing ? "bg-green-500" : value >= 3 ? "bg-amber-500" : "bg-red-500"
                                : "bg-muted"
                        )}
                    />
                ))}
            </div>
        </div>
    );
}

function SoundbiteCard({
    soundbite,
    onTextChange,
    onToggleLock,
    onRegenerate,
}: {
    soundbite: Soundbite;
    onTextChange: (text: string) => void;
    onToggleLock: () => void;
    onRegenerate: () => void;
}) {
    const { label, color } = TYPE_LABELS[soundbite.type];

    const copyToClipboard = () => {
        navigator.clipboard.writeText(soundbite.text);
        toast.success('Soundbite copied to clipboard');
    };

    return (
        <ContextMenu>
            <ContextMenuTrigger>
                <div className={cn(
                    "p-5 rounded-xl border-2 transition-all h-full bg-card",
                    soundbite.isLocked
                        ? "border-green-500 bg-green-50/30 dark:bg-green-950/20"
                        : "border-border shadow-sm"
                )}>
                    {/* Header */}
                    <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                            <span className={cn("text-xs px-2 py-1 rounded-full font-medium border border-current opacity-80", color)}>
                                {label}
                            </span>
                            {soundbite.scores.passing ? (
                                <Check className="h-4 w-4 text-green-500" />
                            ) : (
                                <AlertTriangle className="h-4 w-4 text-amber-500" />
                            )}
                        </div>
                        <div className="flex items-center gap-1">
                            <span className={cn(
                                "text-lg font-bold",
                                soundbite.scores.total >= 80 ? "text-green-600" :
                                    soundbite.scores.total >= 60 ? "text-amber-600" : "text-red-600"
                            )}>
                                {soundbite.scores.total}%
                            </span>
                        </div>
                    </div>

                    {/* Text */}
                    <Textarea
                        value={soundbite.text}
                        onChange={(e) => onTextChange(e.target.value)}
                        disabled={soundbite.isLocked}
                        className="min-h-[100px] text-base mb-4 resize-none bg-background/50 font-serif leading-relaxed"
                    />

                    {/* Tags */}
                    <div className="flex flex-wrap gap-2 mb-4">
                        <span className="text-[10px] uppercase tracking-wider text-muted-foreground border px-2 py-0.5 rounded-full">
                            {soundbite.awarenessStage}
                        </span>
                        <span className="text-[10px] uppercase tracking-wider text-muted-foreground border px-2 py-0.5 rounded-full">
                            {soundbite.buyingJob}
                        </span>
                    </div>

                    {/* Rigor Gates */}
                    <div className="grid grid-cols-2 gap-x-4 gap-y-2 mb-6 p-3 bg-muted/20 rounded-lg">
                        <ScoreGate label="Specific" value={soundbite.scores.specificity} passing={soundbite.scores.specificity >= 3} />
                        <ScoreGate label="Proof" value={soundbite.scores.proof} passing={soundbite.scores.proof >= 3} />
                        <ScoreGate label="Diff" value={soundbite.scores.differentiation} passing={soundbite.scores.differentiation >= 3} />
                        <ScoreGate label="Fit" value={soundbite.scores.awarenessFit} passing={soundbite.scores.awarenessFit >= 3} />
                        <ScoreGate label="Load" value={soundbite.scores.cognitiveLoad} passing={soundbite.scores.cognitiveLoad >= 3} />
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2">
                        <Button size="sm" variant="outline" onClick={onRegenerate} disabled={soundbite.isLocked} className="flex-1">
                            <RefreshCw className="h-3 w-3 mr-2" /> Regenerate
                        </Button>
                        <Button size="sm" variant={soundbite.isLocked ? "default" : "secondary"} onClick={onToggleLock} className="flex-1">
                            {soundbite.isLocked ? <Unlock className="h-3 w-3 mr-2" /> : <Lock className="h-3 w-3 mr-2" />}
                            {soundbite.isLocked ? 'Unlock' : 'Lock'}
                        </Button>
                    </div>
                </div>
            </ContextMenuTrigger>
            <ContextMenuContent>
                <ContextMenuItem onClick={copyToClipboard}>
                    <Copy className="mr-2 h-4 w-4" /> Copy Text
                </ContextMenuItem>
                <ContextMenuItem onClick={onRegenerate} disabled={soundbite.isLocked}>
                    <Wand2 className="mr-2 h-4 w-4" /> Regenerate
                </ContextMenuItem>
                <ContextMenuItem onClick={onToggleLock}>
                    {soundbite.isLocked ? <Unlock className="mr-2 h-4 w-4" /> : <Lock className="mr-2 h-4 w-4" />}
                    {soundbite.isLocked ? 'Unlock Soundbite' : 'Lock Soundbite'}
                </ContextMenuItem>
            </ContextMenuContent>
        </ContextMenu>
    );
}

export function SoundbiteCards({ soundbites, onChange, onRegenerate, onContinue }: SoundbiteCardsProps) {
    const handleTextChange = (id: string, text: string) => {
        onChange(soundbites.map(sb => sb.id === id ? { ...sb, text } : sb));
    };

    const handleToggleLock = (id: string) => {
        onChange(soundbites.map(sb => sb.id === id ? { ...sb, isLocked: !sb.isLocked } : sb));
    };

    const passingCount = soundbites.filter(sb => sb.scores.passing).length;
    const lockedCount = soundbites.filter(sb => sb.isLocked).length;

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="text-center space-y-2">
                <h1 className="text-3xl font-serif font-bold text-foreground">
                    7 Soundbites
                </h1>
                <p className="text-muted-foreground max-w-lg mx-auto">
                    Each soundbite is gated by 5 rigor checks. Edit, regenerate, then lock.
                </p>
            </div>

            {/* Stats */}
            <div className="flex justify-center gap-8 text-center">
                <div>
                    <div className={cn(
                        "text-3xl font-bold",
                        passingCount === 7 ? "text-green-600" : "text-amber-600"
                    )}>
                        {passingCount}/7
                    </div>
                    <div className="text-xs text-muted-foreground">Passing</div>
                </div>
                <div>
                    <div className="text-3xl font-bold text-primary">{lockedCount}/7</div>
                    <div className="text-xs text-muted-foreground">Locked</div>
                </div>
            </div>

            {/* Carousel */}
            <div className="max-w-4xl mx-auto px-12">
                <Carousel
                    opts={{
                        align: "start",
                    }}
                    className="w-full"
                >
                    <CarouselContent>
                        {soundbites.map(soundbite => (
                            <CarouselItem key={soundbite.id} className="md:basis-1/2 lg:basis-1/2 pl-6">
                                <div className="p-1 h-full">
                                    <SoundbiteCard
                                        soundbite={soundbite}
                                        onTextChange={(text) => handleTextChange(soundbite.id, text)}
                                        onToggleLock={() => handleToggleLock(soundbite.id)}
                                        onRegenerate={() => onRegenerate(soundbite.id)}
                                    />
                                </div>
                            </CarouselItem>
                        ))}
                    </CarouselContent>
                    <CarouselPrevious />
                    <CarouselNext />
                </Carousel>
            </div>

            {/* Continue Button */}
            <div className="flex justify-center pt-4">
                <Button
                    size="lg"
                    onClick={onContinue}
                    disabled={passingCount < 5}
                    className="px-8 py-6 text-lg rounded-xl"
                >
                    {passingCount < 5 ? `${5 - passingCount} more must pass` : 'Continue'}
                    <ArrowRight className="h-5 w-5 ml-2" />
                </Button>
            </div>
        </div>
    );
}
