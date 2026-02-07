'use client';

import React, { useState } from 'react';
import { Move, NextAction } from '@/lib/campaigns-types';
import { Plus, Check, X } from 'lucide-react';
import { toast } from 'sonner';

interface TodayPanelProps {
    moves: Move[];
    onLogProgress: (moveId: string) => void;
    onSaveCheckin: (data: CheckinData) => void;
}

export interface CheckinData {
    executed: boolean;
    quality: number;
    energy: number;
    note?: string;
}

export function TodayPanel({ moves, onLogProgress, onSaveCheckin }: TodayPanelProps) {
    const [executed, setExecuted] = useState<boolean | null>(null);
    const [quality, setQuality] = useState(7);
    const [energy, setEnergy] = useState(7);
    const [note, setNote] = useState('');
    const [activeBlockers, setActiveBlockers] = useState<string[]>([]);

    // Get today's queue from active moves' next actions
    const activeMoves = moves.filter(m => m.status === 'active');
    const queue: { moveId: string; moveName: string; action: NextAction }[] = [];

    for (const move of activeMoves) {
        if (move.nextAction) {
            queue.push({
                moveId: move.id,
                moveName: move.name,
                action: move.nextAction
            });
        } else if (move.checklist) {
            // Fallback: get first incomplete task
            const nextTask = move.checklist.find(t => !t.completed);
            if (nextTask) {
                queue.push({
                    moveId: move.id,
                    moveName: move.name,
                    action: {
                        label: nextTask.label,
                        dueDate: 'today',
                        estimatedMinutes: 20,
                        taskId: nextTask.id
                    }
                });
            }
        }
    }

    // Sort by due date and limit to 5
    const todayQueue = queue.slice(0, 5);

    const handleSaveCheckin = () => {
        if (executed === null) return;
        onSaveCheckin({
            executed,
            quality,
            energy,
            note: note || undefined
        });
        // Reset form
        setExecuted(null);
        setQuality(7);
        setEnergy(7);
        setNote('');
        toast.success('Check-in saved!');
    };

    const blockerOptions = [
        { id: 'no_time', label: 'No time' },
        { id: 'no_idea', label: 'No idea' },
        { id: 'tech_issue', label: 'Tech issue' },
        { id: 'need_asset', label: 'Need asset' },
        { id: 'need_approval', label: 'Need approval' },
    ];

    return (
        <div className="bg-white border border-[#E5E6E3] rounded-2xl overflow-hidden">
            {/* Header */}
            <div className="px-6 py-5 border-b border-[#E5E6E3]">
                <h3 className="font-serif text-[20px] text-[#2D3538] mb-1">Today</h3>
                <p className="text-[13px] text-[#9D9F9F]">Your execution queue</p>
            </div>

            {/* Today's Queue */}
            <div className="px-6 py-5 border-b border-[#E5E6E3]">
                <h4 className="text-[11px] font-semibold uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">Queue</h4>
                {todayQueue.length > 0 ? (
                    <div className="space-y-3">
                        {todayQueue.map((item, idx) => (
                            <div key={`${item.moveId}-${idx}`} className="flex items-center gap-3">
                                <span className="w-5 h-5 rounded-full bg-[#F8F9F7] border border-[#E5E6E3] flex items-center justify-center text-[11px] font-mono text-[#9D9F9F]">
                                    {idx + 1}
                                </span>
                                <div className="flex-1 min-w-0">
                                    <span className="block text-[14px] text-[#2D3538] truncate">{item.action.label}</span>
                                    <span className="block text-[11px] text-[#9D9F9F] truncate">{item.moveName}</span>
                                </div>
                                <span className="text-[11px] font-mono text-[#C0C1BE]">{item.action.estimatedMinutes}m</span>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="text-[13px] text-[#9D9F9F] italic">No actions queued for today</p>
                )}
            </div>

            {/* 60-Second Check-in */}
            <div className="px-6 py-5 border-b border-[#E5E6E3]">
                <h4 className="text-[11px] font-semibold uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">60-Sec Check-in</h4>

                {/* Executed Today */}
                <div className="flex items-center justify-between mb-4">
                    <span className="text-[14px] text-[#2D3538]">Did you execute today?</span>
                    <div className="flex gap-2">
                        <button
                            onClick={() => setExecuted(true)}
                            className={`h-8 px-4 rounded-lg text-[12px] font-medium transition-all ${executed === true
                                    ? 'bg-[#2D3538] text-white'
                                    : 'bg-[#F8F9F7] text-[#5B5F61] border border-[#E5E6E3] hover:border-[#C0C1BE]'
                                }`}
                        >
                            Yes
                        </button>
                        <button
                            onClick={() => setExecuted(false)}
                            className={`h-8 px-4 rounded-lg text-[12px] font-medium transition-all ${executed === false
                                    ? 'bg-[#2D3538] text-white'
                                    : 'bg-[#F8F9F7] text-[#5B5F61] border border-[#E5E6E3] hover:border-[#C0C1BE]'
                                }`}
                        >
                            No
                        </button>
                    </div>
                </div>

                {/* Quality Slider */}
                <div className="flex items-center gap-4 mb-3">
                    <span className="text-[12px] text-[#5B5F61] w-16">Quality</span>
                    <input
                        type="range"
                        min="1"
                        max="10"
                        value={quality}
                        onChange={(e) => setQuality(parseInt(e.target.value))}
                        className="flex-1 h-1 bg-[#E5E6E3] rounded-full appearance-none accent-[#2D3538]"
                    />
                    <span className="text-[12px] font-mono text-[#2D3538] w-8 text-right">{quality}</span>
                </div>

                {/* Energy Slider */}
                <div className="flex items-center gap-4 mb-5">
                    <span className="text-[12px] text-[#5B5F61] w-16">Energy</span>
                    <input
                        type="range"
                        min="1"
                        max="10"
                        value={energy}
                        onChange={(e) => setEnergy(parseInt(e.target.value))}
                        className="flex-1 h-1 bg-[#E5E6E3] rounded-full appearance-none accent-[#2D3538]"
                    />
                    <span className="text-[12px] font-mono text-[#2D3538] w-8 text-right">{energy}</span>
                </div>

                {/* Save Button */}
                <button
                    onClick={handleSaveCheckin}
                    disabled={executed === null}
                    className={`w-full h-10 rounded-xl text-[14px] font-medium transition-all ${executed === null
                            ? 'bg-[#F8F9F7] text-[#C0C1BE] cursor-not-allowed'
                            : 'bg-[#1A1D1E] text-white hover:bg-black'
                        }`}
                >
                    Save Check-in
                </button>
            </div>

            {/* Blockers */}
            <div className="px-6 py-5">
                <h4 className="text-[11px] font-semibold uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">Blockers</h4>
                <div className="flex flex-wrap gap-2">
                    {blockerOptions.map(opt => {
                        const isActive = activeBlockers.includes(opt.id);
                        return (
                            <button
                                key={opt.id}
                                onClick={() => {
                                    if (isActive) {
                                        setActiveBlockers(prev => prev.filter(b => b !== opt.id));
                                        toast.info(`Removed blocker: ${opt.label}`);
                                    } else {
                                        setActiveBlockers(prev => [...prev, opt.id]);
                                        toast.warning(`Blocker added: ${opt.label}`);
                                    }
                                }}
                                className={`h-8 px-3 rounded-lg text-[12px] font-medium transition-all flex items-center gap-1.5 ${isActive
                                        ? 'bg-[#1A1D1E] text-white border border-[#1A1D1E]'
                                        : 'bg-[#F8F9F7] text-[#5B5F61] border border-dashed border-[#E5E6E3] hover:border-[#C0C1BE]'
                                    }`}
                            >
                                {isActive ? (
                                    <X className="w-3 h-3" />
                                ) : (
                                    <Plus className="w-3 h-3" />
                                )}
                                {opt.label}
                            </button>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
