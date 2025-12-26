'use client';

import React from 'react';
import { Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ArtifactLocation } from '@/lib/foundation';
import styles from '../QuestionFlow.module.css';

interface ArtifactOption {
    value: ArtifactLocation;
    label: string;
    icon: string;
    color?: string;
    gradient?: string;
}

interface ArtifactSelectorProps {
    value: ArtifactLocation[];
    onChange: (value: ArtifactLocation[]) => void;
    options: ArtifactOption[];
}

export function ArtifactSelector({ value = [], onChange, options }: ArtifactSelectorProps) {
    const toggleArtifact = (artifact: ArtifactLocation) => {
        if (value.includes(artifact)) {
            onChange(value.filter(v => v !== artifact));
        } else {
            onChange([...value, artifact]);
        }
    };

    return (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
            {options.map((opt) => {
                const isSelected = value.includes(opt.value);
                return (
                    <div
                        key={opt.value}
                        onClick={() => toggleArtifact(opt.value)}
                        className={cn(
                            "relative flex flex-col items-center justify-center p-4 rounded-xl border-2 cursor-pointer transition-all duration-200",
                            "hover:border-primary/50 hover:bg-accent/5",
                            isSelected
                                ? "border-primary bg-primary/5 shadow-sm"
                                : "border-border bg-card"
                        )}
                    >
                        <div className={cn(
                            "w-8 h-8 mb-2 rounded-lg flex items-center justify-center text-white font-bold text-sm",
                            opt.gradient || "bg-gradient-to-br from-blue-500 to-blue-600"
                        )}>
                            {opt.icon}
                        </div>
                        <span className={cn(
                            "text-sm font-medium text-center",
                            isSelected ? "text-primary" : "text-foreground"
                        )}>
                            {opt.label}
                        </span>
                        {isSelected && (
                            <div className="absolute top-2 right-2 w-5 h-5 bg-primary rounded-full flex items-center justify-center">
                                <Check className="h-3 w-3 text-primary-foreground" />
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );
}
