'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
    Target, Heart, Users, Zap, ChevronDown, ChevronUp,
    ArrowRight, ArrowLeft, Check, Plus, X, Lightbulb
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ICPJTBD, ICPForcesOfProgress, ForceItem, DataConfidence } from '@/lib/foundation';

interface JTBDStruggleMomentsProps {
    jtbd: ICPJTBD;
    forces: ICPForcesOfProgress;
    strugglingMoments: string[];
    onUpdateJTBD: (updates: Partial<ICPJTBD>) => void;
    onUpdateForces: (updates: Partial<ICPForcesOfProgress>) => void;
    onUpdateStruggles: (moments: string[]) => void;
    onSetPrimaryJob: (type: 'functional' | 'emotional' | 'social') => void;
    primaryJobType: 'functional' | 'emotional' | 'social';
}

const JOB_CONFIG = {
    functional: {
        icon: Target,
        color: '#2D3538',
        bgColor: '#F3F4EE',
        label: 'Functional Job',
        description: 'The practical task they need to accomplish',
        placeholder: 'e.g., "Get marketing under control and executing weekly"'
    },
    emotional: {
        icon: Heart,
        color: '#E57373',
        bgColor: '#FEF3F2',
        label: 'Emotional Job',
        description: 'How they want to feel',
        placeholder: 'e.g., "Feel confident about marketing direction"'
    },
    social: {
        icon: Users,
        color: '#64B5F6',
        bgColor: '#EFF6FF',
        label: 'Social Job',
        description: 'How they want to be perceived',
        placeholder: 'e.g., "Be seen as strategic, not chaotic"'
    }
};

function JobCard({
    type,
    value,
    isPrimary,
    onUpdate,
    onSetPrimary,
    struggles
}: {
    type: 'functional' | 'emotional' | 'social';
    value: string;
    isPrimary: boolean;
    onUpdate: (value: string) => void;
    onSetPrimary: () => void;
    struggles: string[];
}) {
    const config = JOB_CONFIG[type];
    const Icon = config.icon;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`rounded-2xl border-2 overflow-hidden ${isPrimary ? 'border-[#2D3538]' : 'border-[#E5E6E3]'
                }`}
        >
            {/* Header */}
            <div
                className="p-5 flex items-center justify-between"
                style={{ backgroundColor: config.bgColor }}
            >
                <div className="flex items-center gap-3">
                    <div
                        className="w-10 h-10 rounded-xl flex items-center justify-center"
                        style={{ backgroundColor: config.color }}
                    >
                        <Icon className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h3 className="font-medium text-[#2D3538]">{config.label}</h3>
                        <p className="text-xs text-[#5B5F61]">{config.description}</p>
                    </div>
                </div>
                {isPrimary ? (
                    <span className="text-[9px] font-mono uppercase bg-[#2D3538] text-white px-2 py-1 rounded">
                        Primary
                    </span>
                ) : (
                    <button
                        onClick={onSetPrimary}
                        className="text-xs text-[#5B5F61] hover:text-[#2D3538] transition-colors"
                    >
                        Set as Primary
                    </button>
                )}
            </div>

            {/* Job Statement */}
            <div className="p-5 bg-white">
                <textarea
                    value={value}
                    onChange={(e) => onUpdate(e.target.value)}
                    placeholder={config.placeholder}
                    className="w-full h-24 border border-[#E5E6E3] rounded-xl px-4 py-3 text-sm resize-none focus:outline-none focus:border-[#2D3538]"
                />
            </div>

            {/* Struggle Moments */}
            <div className="p-5 bg-[#FAFAF8] border-t border-[#E5E6E3]">
                <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-3 block">
                    Struggle Moments
                </span>
                <ul className="space-y-2">
                    {struggles.slice(0, 3).map((struggle, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-[#5B5F61]">
                            <div className="w-1.5 h-1.5 rounded-full bg-[#9D9F9F] mt-1.5 flex-shrink-0" />
                            <span>{struggle}</span>
                        </li>
                    ))}
                    {struggles.length === 0 && (
                        <li className="text-sm text-[#9D9F9F] italic">No struggles defined</li>
                    )}
                </ul>
            </div>
        </motion.div>
    );
}

function ForcesOfProgress({
    forces,
    onUpdate,
    isExpanded,
    onToggle
}: {
    forces: ICPForcesOfProgress;
    onUpdate: (updates: Partial<ICPForcesOfProgress>) => void;
    isExpanded: boolean;
    onToggle: () => void;
}) {
    const forceCategories = [
        { key: 'push' as const, label: 'Push', desc: 'What pushes them away from status quo', icon: ArrowRight, color: '#E57373' },
        { key: 'pull' as const, label: 'Pull', desc: 'What pulls them toward new solution', icon: Lightbulb, color: '#81C784' },
        { key: 'anxiety' as const, label: 'Anxiety', desc: 'Concerns about switching', icon: Zap, color: '#FFB74D' },
        { key: 'habit' as const, label: 'Habit', desc: 'What keeps them stuck', icon: ArrowLeft, color: '#9D9F9F' },
    ];

    return (
        <div className="bg-white border border-[#E5E6E3] rounded-2xl overflow-hidden">
            <button
                onClick={onToggle}
                className="w-full p-5 flex items-center justify-between hover:bg-[#FAFAF8] transition-colors"
            >
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-[#F3F4EE] rounded-xl flex items-center justify-center">
                        <Zap className="w-5 h-5 text-[#2D3538]" />
                    </div>
                    <div className="text-left">
                        <h3 className="font-medium text-[#2D3538]">Forces of Progress</h3>
                        <p className="text-xs text-[#5B5F61]">Push/Pull/Anxiety/Habit analysis</p>
                    </div>
                </div>
                {isExpanded ? (
                    <ChevronUp className="w-5 h-5 text-[#9D9F9F]" />
                ) : (
                    <ChevronDown className="w-5 h-5 text-[#9D9F9F]" />
                )}
            </button>

            {isExpanded && (
                <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    className="border-t border-[#E5E6E3]"
                >
                    <div className="grid grid-cols-2 gap-4 p-5">
                        {forceCategories.map(cat => (
                            <div
                                key={cat.key}
                                className="bg-[#FAFAF8] rounded-xl p-4"
                            >
                                <div className="flex items-center gap-2 mb-3">
                                    <div
                                        className="w-8 h-8 rounded-lg flex items-center justify-center"
                                        style={{ backgroundColor: cat.color + '20' }}
                                    >
                                        <cat.icon className="w-4 h-4" style={{ color: cat.color }} />
                                    </div>
                                    <div>
                                        <span className="text-sm font-medium text-[#2D3538]">{cat.label}</span>
                                        <span className="text-[10px] text-[#9D9F9F] block">{cat.desc}</span>
                                    </div>
                                </div>
                                <ul className="space-y-2">
                                    {forces[cat.key].map((item, i) => (
                                        <li key={i} className="flex items-start gap-2 text-sm text-[#5B5F61]">
                                            <div
                                                className="w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0"
                                                style={{ backgroundColor: cat.color }}
                                            />
                                            <span>{item.text}</span>
                                            <span className="text-[9px] font-mono uppercase text-[#9D9F9F]">
                                                ({item.confidence})
                                            </span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ))}
                    </div>
                </motion.div>
            )}
        </div>
    );
}

export function JTBDStruggleMoments({
    jtbd,
    forces,
    strugglingMoments,
    onUpdateJTBD,
    onUpdateForces,
    onUpdateStruggles,
    onSetPrimaryJob,
    primaryJobType
}: JTBDStruggleMomentsProps) {
    const [showForces, setShowForces] = useState(false);
    const [newStruggle, setNewStruggle] = useState('');

    // Group struggles by job type (simple heuristic)
    const functionalStruggles = strugglingMoments.filter((_, i) => i % 3 === 0);
    const emotionalStruggles = strugglingMoments.filter((_, i) => i % 3 === 1);
    const socialStruggles = strugglingMoments.filter((_, i) => i % 3 === 2);

    const addStruggle = () => {
        if (newStruggle.trim()) {
            onUpdateStruggles([...strugglingMoments, newStruggle.trim()]);
            setNewStruggle('');
        }
    };

    return (
        <div className="space-y-6">
            {/* Intro */}
            <div className="flex items-start gap-3 p-4 bg-[#F3F4EE] rounded-xl">
                <Target className="w-5 h-5 text-[#2D3538] flex-shrink-0 mt-0.5" />
                <p className="text-sm text-[#5B5F61]">
                    <strong className="text-[#2D3538]">Jobs-To-Be-Done</strong> captures the real "why they buy" —
                    not demographics. Each ICP has functional, emotional, and social jobs. Mark one as primary.
                </p>
            </div>

            {/* 3-Column Job Cards */}
            <div className="grid grid-cols-3 gap-4">
                <JobCard
                    type="functional"
                    value={jtbd.functional}
                    isPrimary={primaryJobType === 'functional'}
                    onUpdate={(v) => onUpdateJTBD({ functional: v })}
                    onSetPrimary={() => onSetPrimaryJob('functional')}
                    struggles={functionalStruggles}
                />
                <JobCard
                    type="emotional"
                    value={jtbd.emotional}
                    isPrimary={primaryJobType === 'emotional'}
                    onUpdate={(v) => onUpdateJTBD({ emotional: v })}
                    onSetPrimary={() => onSetPrimaryJob('emotional')}
                    struggles={emotionalStruggles}
                />
                <JobCard
                    type="social"
                    value={jtbd.social}
                    isPrimary={primaryJobType === 'social'}
                    onUpdate={(v) => onUpdateJTBD({ social: v })}
                    onSetPrimary={() => onSetPrimaryJob('social')}
                    struggles={socialStruggles}
                />
            </div>

            {/* Add Struggle */}
            <div className="bg-white border border-[#E5E6E3] rounded-2xl p-5">
                <label className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-3 block">
                    Add Struggle Moment
                </label>
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={newStruggle}
                        onChange={(e) => setNewStruggle(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && addStruggle()}
                        placeholder="e.g., 'Spending too much time on low-impact tasks'"
                        className="flex-1 border border-[#E5E6E3] rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-[#2D3538]"
                    />
                    <Button
                        onClick={addStruggle}
                        disabled={!newStruggle.trim()}
                        className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white rounded-xl"
                    >
                        <Plus className="w-4 h-4" />
                    </Button>
                </div>
            </div>

            {/* Forces of Progress (Collapsible) */}
            <ForcesOfProgress
                forces={forces}
                onUpdate={onUpdateForces}
                isExpanded={showForces}
                onToggle={() => setShowForces(!showForces)}
            />
        </div>
    );
}
