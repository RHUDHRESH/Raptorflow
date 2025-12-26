'use client';

import React from 'react';
import { ElevatorPitch, WeAreWeAreNot, ObjectionKillshot } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ArrowRight, Copy, Check, X, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

interface PositioningOutputsProps {
    statement: string;
    pitch: ElevatorPitch;
    weAreWeAreNot: WeAreWeAreNot;
    objections: ObjectionKillshot[];
    onStatementChange: (statement: string) => void;
    onContinue: () => void;
}

function CopyButton({ text }: { text: string }) {
    const copy = () => {
        navigator.clipboard.writeText(text);
        toast.success('Copied to clipboard');
    };

    return (
        <button onClick={copy} className="p-2 hover:bg-muted rounded-lg transition-colors">
            <Copy className="h-4 w-4 text-muted-foreground" />
        </button>
    );
}

export function PositioningOutputs({
    statement,
    pitch,
    weAreWeAreNot,
    objections,
    onStatementChange,
    onContinue,
}: PositioningOutputsProps) {
    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="text-center space-y-2">
                <h1 className="text-3xl font-serif font-bold text-foreground">
                    Positioning Outputs
                </h1>
                <p className="text-muted-foreground max-w-lg mx-auto">
                    Your positioning deliverables — statement, pitches, and objection responses.
                </p>
            </div>

            {/* Positioning Statement */}
            <div className="max-w-2xl mx-auto">
                <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold">Positioning Statement</h3>
                    <CopyButton text={statement} />
                </div>
                <Textarea
                    value={statement}
                    onChange={(e) => onStatementChange(e.target.value)}
                    className="min-h-[100px] text-lg"
                />
            </div>

            {/* Elevator Pitches */}
            <div className="max-w-2xl mx-auto space-y-4">
                <h3 className="font-semibold">Elevator Pitches</h3>
                <div className="grid gap-4">
                    {[
                        { label: '10 seconds', value: pitch.tenSec },
                        { label: '30 seconds', value: pitch.thirtySec },
                        { label: '2 minutes', value: pitch.twoMin },
                    ].map(({ label, value }) => (
                        <div key={label} className="bg-card border rounded-xl p-4">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                                    {label}
                                </span>
                                <CopyButton text={value} />
                            </div>
                            <p className="text-sm">{value}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* We Are / We Are Not */}
            <div className="max-w-2xl mx-auto">
                <h3 className="font-semibold mb-4">We Are / We Are Not</h3>
                <div className="grid md:grid-cols-2 gap-4">
                    <div className="bg-green-50/50 dark:bg-green-950/20 border-2 border-green-200 dark:border-green-900 rounded-xl p-4">
                        <h4 className="font-medium text-green-700 dark:text-green-400 mb-3 flex items-center gap-2">
                            <Check className="h-4 w-4" /> We Are
                        </h4>
                        <ul className="space-y-2">
                            {weAreWeAreNot.weAre.map((item, i) => (
                                <li key={i} className="text-sm text-green-700 dark:text-green-400">{item}</li>
                            ))}
                        </ul>
                    </div>
                    <div className="bg-red-50/50 dark:bg-red-950/20 border-2 border-red-200 dark:border-red-900 rounded-xl p-4">
                        <h4 className="font-medium text-red-700 dark:text-red-400 mb-3 flex items-center gap-2">
                            <X className="h-4 w-4" /> We Are Not
                        </h4>
                        <ul className="space-y-2">
                            {weAreWeAreNot.weAreNot.map((item, i) => (
                                <li key={i} className="text-sm text-red-700 dark:text-red-400">{item}</li>
                            ))}
                        </ul>
                    </div>
                </div>
            </div>

            {/* Objection Killshots */}
            <div className="max-w-2xl mx-auto">
                <h3 className="font-semibold mb-4 flex items-center gap-2">
                    <Zap className="h-4 w-4" /> Objection Killshots
                </h3>
                <div className="space-y-3">
                    {objections.map((obj) => (
                        <div key={obj.id} className="bg-card border rounded-xl p-4">
                            <p className="text-sm font-medium text-muted-foreground mb-2">
                                "{obj.objection}"
                            </p>
                            <p className="text-sm">{obj.response}</p>
                            <p className="text-xs text-muted-foreground mt-2">
                                Tied to: {obj.alternativeTied}
                            </p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Continue Button */}
            <div className="flex justify-center pt-4">
                <Button size="lg" onClick={onContinue} className="px-8 py-6 text-lg rounded-xl">
                    Continue <ArrowRight className="h-5 w-5 ml-2" />
                </Button>
            </div>
        </div>
    );
}
