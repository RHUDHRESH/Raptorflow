'use client';

import React, { useMemo } from 'react';
import { FoundationData, emptyFoundation } from '@/lib/foundation';
import { QUESTIONS } from '@/lib/questionFlowData';
import { cn } from '@/lib/utils';

interface ClarityScoreProps {
    data: FoundationData;
    className?: string;
}

/**
 * Calculate clarity score (0-100) based on how many questions are answered.
 * Required questions count more than optional ones.
 */
export function calculateClarityScore(data: FoundationData): number {
    let totalPoints = 0;
    let earnedPoints = 0;

    const getValue = (path: string): any => {
        const parts = path.split('.');
        let value: any = data;
        for (const part of parts) {
            value = value?.[part];
        }
        return value;
    };

    for (const question of QUESTIONS) {
        const weight = question.required ? 2 : 1;
        totalPoints += weight;

        const value = getValue(question.field);
        const hasValue = Array.isArray(value)
            ? value.length > 0
            : (typeof value === 'string' ? value.trim().length > 0 : !!value);

        if (hasValue) {
            earnedPoints += weight;
        }
    }

    return totalPoints > 0 ? Math.round((earnedPoints / totalPoints) * 100) : 0;
}

export function ClarityScore({ data, className }: ClarityScoreProps) {
    const score = useMemo(() => calculateClarityScore(data), [data]);

    // Color based on score
    const getColor = () => {
        if (score >= 80) return 'text-green-500';
        if (score >= 50) return 'text-yellow-500';
        return 'text-muted-foreground';
    };

    const getStrokeColor = () => {
        if (score >= 80) return '#22c55e'; // green-500
        if (score >= 50) return '#eab308'; // yellow-500
        return 'hsl(var(--muted-foreground))';
    };

    // SVG circle math
    const size = 80;
    const strokeWidth = 6;
    const radius = (size - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (score / 100) * circumference;

    return (
        <div className={cn("flex flex-col items-center gap-2", className)}>
            <div className="relative" style={{ width: size, height: size }}>
                {/* Background circle */}
                <svg className="absolute inset-0 -rotate-90" width={size} height={size}>
                    <circle
                        cx={size / 2}
                        cy={size / 2}
                        r={radius}
                        fill="none"
                        stroke="hsl(var(--border))"
                        strokeWidth={strokeWidth}
                    />
                    {/* Progress circle */}
                    <circle
                        cx={size / 2}
                        cy={size / 2}
                        r={radius}
                        fill="none"
                        stroke={getStrokeColor()}
                        strokeWidth={strokeWidth}
                        strokeLinecap="round"
                        strokeDasharray={circumference}
                        strokeDashoffset={offset}
                        className="transition-all duration-500 ease-out"
                    />
                </svg>
                {/* Score number */}
                <div className="absolute inset-0 flex items-center justify-center">
                    <span className={cn("text-xl font-bold tabular-nums", getColor())}>
                        {score}
                    </span>
                </div>
            </div>
            <div className="text-center">
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Clarity Score
                </p>
                <p className="text-[10px] text-muted-foreground/60 mt-0.5">
                    {score < 50 ? 'Keep going!' : score < 80 ? 'Almost there!' : 'Excellent!'}
                </p>
            </div>
        </div>
    );
}
