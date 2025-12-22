'use client';

import React from 'react';
import { MessageCircle, UserPlus, Calendar, MousePointer, Users, DollarSign } from 'lucide-react';
import { cn } from '@/lib/utils';
import { GoalType } from '@/lib/blackbox-types';

interface GoalSelectorProps {
    selectedGoal: GoalType | null;
    onSelect: (goal: GoalType) => void;
}

const GOALS = [
    { id: 'replies' as GoalType, label: 'Replies', icon: MessageCircle },
    { id: 'leads' as GoalType, label: 'Leads', icon: UserPlus },
    { id: 'calls' as GoalType, label: 'Demos', icon: Calendar },
    { id: 'clicks' as GoalType, label: 'Clicks', icon: MousePointer },
    { id: 'followers' as GoalType, label: 'Followers', icon: Users },
    { id: 'sales' as GoalType, label: 'Sales', icon: DollarSign },
];

export function GoalSelector({ selectedGoal, onSelect }: GoalSelectorProps) {
    return (
        <div className="w-full space-y-4 text-center">
            <div>
                <h2 className="text-xl font-semibold mb-1 font-sans">What's your goal?</h2>
                <p className="text-sm text-zinc-500 font-sans">Pick one. We'll design experiments around it.</p>
            </div>
            <div className="grid grid-cols-3 gap-2 max-w-sm mx-auto">
                {GOALS.map((g) => {
                    const Icon = g.icon;
                    const isSelected = selectedGoal === g.id;
                    return (
                        <button
                            key={g.id}
                            onClick={() => onSelect(g.id)}
                            className={cn(
                                "flex flex-col items-center justify-center p-4 rounded-xl border-2 transition-all",
                                isSelected
                                    ? "bg-zinc-900 border-zinc-900 text-white dark:bg-white dark:border-white dark:text-zinc-900"
                                    : "border-zinc-200 text-zinc-600 hover:border-zinc-400 dark:border-zinc-800 dark:text-zinc-400"
                            )}
                        >
                            <Icon className="w-5 h-5 mb-1.5" />
                            <span className="text-xs font-medium font-sans">{g.label}</span>
                        </button>
                    );
                })}
            </div>
        </div>
    );
}
