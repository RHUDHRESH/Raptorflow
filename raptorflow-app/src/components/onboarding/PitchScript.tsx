'use client';

import React, { useState, useMemo } from 'react';
import { FoundationData } from '@/lib/foundation';
import { cn } from '@/lib/utils';
import { Video, Copy, Play, Pause, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface PitchScriptProps {
    data: FoundationData;
    className?: string;
}

/**
 * Generates a 60-second pitch script from Foundation data
 */
export function PitchScript({ data, className }: PitchScriptProps) {
    const [copied, setCopied] = useState(false);
    const [teleprompterMode, setTeleprompterMode] = useState(false);
    const [isPlaying, setIsPlaying] = useState(false);

    const script = useMemo(() => {
        const { name, industry, stage } = data.business || {};
        const { category, targetAudience, psychologicalOutcome } = data.positioning || {};
        const { beliefPillar, promisePillar, proofPillar } = data.messaging || {};
        const { expensiveProblem } = data.confession || {};

        const lines = [
            // Hook (5 seconds)
            expensiveProblem
                ? `Here's what keeps ${targetAudience || 'our customers'} up at night: ${expensiveProblem}.`
                : `Let me tell you about a problem that costs ${targetAudience || 'businesses'} thousands.`,

            // Introduction (10 seconds)
            `I'm the founder of ${name || '[Your Company]'}${industry ? `, in the ${industry} space` : ''}.`,

            // Positioning (15 seconds)
            category && targetAudience && psychologicalOutcome
                ? `We're the ${category} for ${targetAudience} who want ${psychologicalOutcome}.`
                : `We help ${targetAudience || 'our customers'} achieve what they really want.`,

            // Belief (10 seconds)
            beliefPillar
                ? `We believe ${beliefPillar}.`
                : '',

            // Promise (10 seconds)
            promisePillar
                ? `That's why we promise ${promisePillar}.`
                : '',

            // Proof (5 seconds)
            proofPillar
                ? `And we prove it by ${proofPillar}.`
                : '',

            // Call to Action (5 seconds)
            `If this resonates, let's talk. Visit us online or reach out directly.`
        ].filter(Boolean);

        return lines;
    }, [data]);

    const fullScript = script.join('\n\n');

    const handleCopy = async () => {
        await navigator.clipboard.writeText(fullScript);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className={cn("bg-card border border-border rounded-2xl overflow-hidden", className)}>
            {/* Header */}
            <div className="px-6 py-4 border-b border-border flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
                        <Video className="h-4 w-4 text-primary" />
                    </div>
                    <div>
                        <span className="text-sm font-medium text-foreground">60-Second Pitch</span>
                        <p className="text-xs text-muted-foreground">Your story, ready to tell</p>
                    </div>
                </div>
                <div className="flex gap-2">
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setTeleprompterMode(!teleprompterMode)}
                        className="text-xs"
                    >
                        {teleprompterMode ? <Pause className="h-3 w-3 mr-1" /> : <Play className="h-3 w-3 mr-1" />}
                        {teleprompterMode ? 'Exit' : 'Teleprompter'}
                    </Button>
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={handleCopy}
                        className="text-xs"
                    >
                        {copied ? <Check className="h-3 w-3 mr-1" /> : <Copy className="h-3 w-3 mr-1" />}
                        {copied ? 'Copied!' : 'Copy'}
                    </Button>
                </div>
            </div>

            {/* Script content */}
            <div className={cn(
                "p-6 transition-all duration-500",
                teleprompterMode && "bg-black text-white min-h-[300px]"
            )}>
                {teleprompterMode ? (
                    <div className="text-center">
                        {script.map((line, idx) => (
                            <p
                                key={idx}
                                className={cn(
                                    "text-2xl font-serif leading-relaxed mb-6 transition-opacity",
                                    "animate-in fade-in slide-in-from-bottom-4"
                                )}
                                style={{ animationDelay: `${idx * 0.5}s` }}
                            >
                                {line}
                            </p>
                        ))}
                    </div>
                ) : (
                    <div className="space-y-4">
                        {script.map((line, idx) => (
                            <p key={idx} className="text-sm text-foreground leading-relaxed">
                                <span className="text-xs text-muted-foreground mr-2">
                                    {idx + 1}.
                                </span>
                                {line}
                            </p>
                        ))}
                    </div>
                )}
            </div>

            {/* Footer */}
            <div className="px-6 py-3 border-t border-border bg-muted/30">
                <p className="text-xs text-muted-foreground text-center">
                    Estimated read time: ~60 seconds | {script.length} sections
                </p>
            </div>
        </div>
    );
}
