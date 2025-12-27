'use client';

import React from 'react';
import { motion, Reorder } from 'framer-motion';
import { BuyingRole } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import {
    Users, User, Wallet, Shield, Scale, Briefcase,
    Check, X, GripVertical, AlertCircle, Info
} from 'lucide-react';

// Updated interface to match wizard usage
interface BuyingGroupMapProps {
    roles: BuyingRole[];
    onReorderRoles: (roles: BuyingRole[]) => void;
    onToggleRole: (roleId: string) => void;
    onUpdateRole: (roleId: string, updates: Partial<BuyingRole>) => void;
}

const ROLE_CONFIG: Record<string, {
    icon: React.ElementType;
    color: string;
    bgColor: string;
    concerns: string[];
    fears: string[];
    proofNeeds: string[];
}> = {
    'Economic Buyer': {
        icon: Wallet,
        color: '#2D3538',
        bgColor: '#F3F4EE',
        concerns: ['ROI', 'Budget alignment', 'Risk mitigation'],
        fears: ['Wasted investment', 'Team won\'t adopt'],
        proofNeeds: ['ROI calculator', 'Case studies with metrics']
    },
    'Champion': {
        icon: Users,
        color: '#64B5F6',
        bgColor: '#E3F2FD',
        concerns: ['Implementation ease', 'Quick wins', 'Team adoption'],
        fears: ['Political risk', 'Time investment wasted'],
        proofNeeds: ['Quick start demo', 'Reference calls']
    },
    'Primary User': {
        icon: User,
        color: '#81C784',
        bgColor: '#E8F5E9',
        concerns: ['Daily workflow', 'Learning curve', 'Time savings'],
        fears: ['Another tool to learn', 'Complexity'],
        proofNeeds: ['Hands-on trial', 'Video tutorials']
    },
    'Technical': {
        icon: Shield,
        color: '#9575CD',
        bgColor: '#EDE7F6',
        concerns: ['Integration', 'Security', 'Data privacy'],
        fears: ['Security vulnerabilities', 'Integration failures'],
        proofNeeds: ['Technical docs', 'Security certifications']
    },
    'Finance': {
        icon: Scale,
        color: '#FFB74D',
        bgColor: '#FFF3E0',
        concerns: ['Contract terms', 'Payment flexibility', 'Cost predictability'],
        fears: ['Hidden costs', 'Lock-in'],
        proofNeeds: ['Transparent pricing', 'Flexible contracts']
    },
    'Blocker': {
        icon: AlertCircle,
        color: '#E57373',
        bgColor: '#FFEBEE',
        concerns: ['Status quo works', 'Change is risky', 'Timing'],
        fears: ['Disruption', 'Being wrong about change'],
        proofNeeds: ['Migration guarantee', 'Parallel run option']
    }
};

function RoleCard({
    role,
    config,
    onToggle,
    onUpdateInfluence,
    index
}: {
    role: BuyingRole;
    config: typeof ROLE_CONFIG[string];
    onToggle: () => void;
    onUpdateInfluence: (influence: 'high' | 'medium' | 'low') => void;
    index: number;
}) {
    const Icon = config?.icon || User;
    const isActive = role.isActive;

    return (
        <Reorder.Item value={role}>
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className={`bg-white border-2 rounded-2xl overflow-hidden cursor-grab active:cursor-grabbing ${isActive ? 'border-[#2D3538]' : 'border-dashed border-[#E5E6E3] opacity-60'
                    }`}
            >
                {/* Header */}
                <div
                    className="p-4 flex items-center gap-4"
                    style={{ backgroundColor: isActive ? config?.bgColor : '#FAFAF8' }}
                >
                    <div className="flex items-center gap-3">
                        <GripVertical className="w-4 h-4 text-[#9D9F9F]" />
                        <div
                            className="w-10 h-10 rounded-xl flex items-center justify-center"
                            style={{ backgroundColor: isActive ? config?.color : '#E5E6E3' }}
                        >
                            <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-[#9D9F9F]'}`} />
                        </div>
                    </div>

                    <div className="flex-1">
                        <h3 className={`font-medium ${isActive ? 'text-[#2D3538]' : 'text-[#9D9F9F]'}`}>
                            {role.role}
                        </h3>
                    </div>

                    {/* Toggle & Influence */}
                    <div className="flex items-center gap-3">
                        {isActive && (
                            <div className="flex gap-1">
                                {(['high', 'medium', 'low'] as const).map(level => (
                                    <button
                                        key={level}
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            onUpdateInfluence(level);
                                        }}
                                        className={`px-2 py-1 text-[10px] font-mono uppercase rounded transition-colors ${role.influence === level
                                                ? 'bg-[#2D3538] text-white'
                                                : 'bg-white text-[#9D9F9F] hover:bg-[#F3F4EE]'
                                            }`}
                                    >
                                        {level}
                                    </button>
                                ))}
                            </div>
                        )}
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                onToggle();
                            }}
                            className={`w-8 h-8 rounded-lg flex items-center justify-center transition-colors ${isActive
                                    ? 'bg-[#2D3538] text-white'
                                    : 'bg-[#E5E6E3] text-[#9D9F9F] hover:bg-[#D0D1CE]'
                                }`}
                        >
                            {isActive ? <Check className="w-4 h-4" /> : <X className="w-4 h-4" />}
                        </button>
                    </div>
                </div>

                {/* Details (only when active) */}
                {isActive && config && (
                    <div className="p-4 border-t border-[#E5E6E3] grid grid-cols-3 gap-4">
                        <div>
                            <span className="text-[10px] font-mono uppercase text-[#9D9F9F] block mb-2">
                                Cares About
                            </span>
                            <ul className="space-y-1">
                                {config.concerns.map((c, i) => (
                                    <li key={i} className="text-xs text-[#5B5F61] flex items-start gap-1">
                                        <div className="w-1 h-1 rounded-full bg-[#9D9F9F] mt-1.5 flex-shrink-0" />
                                        {c}
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <div>
                            <span className="text-[10px] font-mono uppercase text-[#9D9F9F] block mb-2">
                                Fears
                            </span>
                            <ul className="space-y-1">
                                {config.fears.map((f, i) => (
                                    <li key={i} className="text-xs text-[#E57373] flex items-start gap-1">
                                        <div className="w-1 h-1 rounded-full bg-[#E57373] mt-1.5 flex-shrink-0" />
                                        {f}
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <div>
                            <span className="text-[10px] font-mono uppercase text-[#9D9F9F] block mb-2">
                                Proof Needs
                            </span>
                            <ul className="space-y-1">
                                {config.proofNeeds.map((p, i) => (
                                    <li key={i} className="text-xs text-[#2D3538] flex items-start gap-1">
                                        <div className="w-1 h-1 rounded-full bg-[#2D3538] mt-1.5 flex-shrink-0" />
                                        {p}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                )}
            </motion.div>
        </Reorder.Item>
    );
}

export function BuyingGroupMap({
    roles,
    onReorderRoles,
    onToggleRole,
    onUpdateRole
}: BuyingGroupMapProps) {
    const activeCount = roles.filter(r => r.isActive).length;

    return (
        <div className="space-y-6">
            {/* Header Info */}
            <div className="flex items-start gap-3 p-4 bg-[#F3F4EE] rounded-xl">
                <Info className="w-5 h-5 text-[#2D3538] flex-shrink-0 mt-0.5" />
                <div>
                    <p className="text-sm text-[#5B5F61]">
                        <strong className="text-[#2D3538]">Buying Group Map</strong> — B2B purchases involve
                        6–10 stakeholders. Drag to reorder by influence. Toggle roles on/off.
                    </p>
                    <p className="text-xs text-[#9D9F9F] mt-1">
                        Buyers do 83% of their research without talking to you.
                    </p>
                </div>
            </div>

            {/* Active Count */}
            <div className="flex items-center gap-4 p-4 bg-[#2D3538] rounded-2xl">
                <Users className="w-6 h-6 text-white" />
                <div>
                    <span className="text-white/60 text-[10px] font-mono uppercase">Active Roles</span>
                    <p className="text-white text-xl font-mono">{activeCount} of {roles.length}</p>
                </div>
            </div>

            {/* Role Cards */}
            <Reorder.Group
                axis="y"
                values={roles}
                onReorder={onReorderRoles}
                className="space-y-3"
            >
                {roles.map((role, index) => {
                    const roleName = role.role.split(' (')[0];
                    const config = Object.entries(ROLE_CONFIG).find(([key]) =>
                        roleName.includes(key) || key.includes(roleName.split(' ')[0])
                    )?.[1] || ROLE_CONFIG['Champion'];

                    return (
                        <RoleCard
                            key={role.id}
                            role={role}
                            config={config}
                            onToggle={() => onToggleRole(role.id)}
                            onUpdateInfluence={(influence) => onUpdateRole(role.id, { influence })}
                            index={index}
                        />
                    );
                })}
            </Reorder.Group>
        </div>
    );
}
