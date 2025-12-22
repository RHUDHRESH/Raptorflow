import React from 'react';
import { cn } from '@/lib/utils';
import { Play, Activity, Maximize, ArrowUp } from 'lucide-react';

interface AnimationPresetsProps {
    selectedAnimation?: string;
    onSelect: (animation: 'none' | 'fade' | 'slide-up' | 'scale' | 'breathe') => void;
    className?: string;
}

const PRESETS = [
    { id: 'none', label: 'None', icon: null },
    { id: 'fade', label: 'Fade In', icon: Activity },
    { id: 'slide-up', label: 'Slide Up', icon: ArrowUp },
    { id: 'scale', label: 'Scale Up', icon: Maximize },
    { id: 'breathe', label: 'Breathe', icon: Play }, // Using Play as placeholder
];

export function AnimationPresets({
    selectedAnimation = 'none',
    onSelect,
    className
}: AnimationPresetsProps) {
    return (
        <div className={cn('space-y-4', className)}>
            <div className="flex items-center gap-2 mb-4">
                <Play className="h-4 w-4 text-muted-foreground" />
                <h3 className="text-sm font-semibold">Animations</h3>
            </div>

            <div className="grid grid-cols-2 gap-2">
                {PRESETS.map(preset => (
                    <button
                        key={preset.id}
                        onClick={() => onSelect(preset.id as any)}
                        className={cn(
                            'flex flex-col items-center justify-center gap-2 p-3 rounded-xl border transition-all',
                            selectedAnimation === preset.id
                                ? 'bg-primary/5 border-primary ring-1 ring-primary/20'
                                : 'bg-card border-border hover:border-primary/50'
                        )}
                    >
                        {preset.icon && <preset.icon className="h-5 w-5 text-muted-foreground" />}
                        <span className="text-xs font-medium">{preset.label}</span>
                    </button>
                ))}
            </div>
        </div>
    );
}
