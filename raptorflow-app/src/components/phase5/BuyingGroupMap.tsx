'use client';

import React from 'react';
import { BuyingGroup, BuyingRole, BuyingJob, BuyingJobType } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import { ArrowRight, Users, Check, X, GripVertical } from 'lucide-react';
import { cn } from '@/lib/utils';

interface BuyingGroupMapProps {
    buyingGroup: BuyingGroup;
    onChange: (group: BuyingGroup) => void;
    onContinue: () => void;
}

const BUYING_JOBS: { job: BuyingJobType; label: string; description: string }[] = [
    { job: 'problem-id', label: 'Problem Identification', description: 'Recognizes need for change' },
    { job: 'solution-explore', label: 'Solution Exploration', description: 'Researches options' },
    { job: 'requirements', label: 'Requirements Building', description: 'Defines must-haves' },
    { job: 'supplier-select', label: 'Supplier Selection', description: 'Makes final decision' },
];

function RoleCard({
    role,
    onToggle,
    onInfluenceChange,
}: {
    role: BuyingRole;
    onToggle: () => void;
    onInfluenceChange: (influence: 'high' | 'medium' | 'low') => void;
}) {
    return (
        <div className={cn(
            "p-4 rounded-xl border-2 transition-all",
            role.isActive
                ? "border-primary bg-primary/5"
                : "border-dashed border-muted opacity-50"
        )}>
            <div className="flex items-center gap-3">
                <button onClick={onToggle} className="p-2 hover:bg-muted rounded-lg">
                    {role.isActive ? (
                        <Check className="h-4 w-4 text-primary" />
                    ) : (
                        <X className="h-4 w-4 text-muted-foreground" />
                    )}
                </button>
                <div className="flex-1">
                    <span className="font-medium">{role.role}</span>
                </div>
                {role.isActive && (
                    <div className="flex gap-1">
                        {(['low', 'medium', 'high'] as const).map(level => (
                            <button
                                key={level}
                                onClick={() => onInfluenceChange(level)}
                                className={cn(
                                    "px-2 py-1 text-xs rounded transition-colors",
                                    role.influence === level
                                        ? "bg-primary text-primary-foreground"
                                        : "bg-muted text-muted-foreground hover:bg-muted/80"
                                )}
                            >
                                {level}
                            </button>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

function BuyingJobRow({
    jobDef,
    buyingJob,
    roles,
    onChange,
}: {
    jobDef: typeof BUYING_JOBS[0];
    buyingJob?: BuyingJob;
    roles: BuyingRole[];
    onChange: (job: BuyingJob) => void;
}) {
    const activeRoles = roles.filter(r => r.isActive);

    return (
        <div className="bg-card border rounded-xl p-4">
            <div className="flex items-start gap-4">
                <div className="flex-1">
                    <h4 className="font-medium text-sm">{jobDef.label}</h4>
                    <p className="text-xs text-muted-foreground">{jobDef.description}</p>
                </div>
                <div className="flex gap-2">
                    <select
                        value={buyingJob?.primaryRoleId || ''}
                        onChange={(e) => onChange({
                            job: jobDef.job,
                            primaryRoleId: e.target.value,
                            supportRoleIds: buyingJob?.supportRoleIds || []
                        })}
                        className="text-xs px-2 py-1 rounded border bg-background"
                    >
                        <option value="">Primary Role</option>
                        {activeRoles.map(r => (
                            <option key={r.id} value={r.id}>{r.role.split(' (')[0]}</option>
                        ))}
                    </select>
                </div>
            </div>
        </div>
    );
}

export function BuyingGroupMap({ buyingGroup, onChange, onContinue }: BuyingGroupMapProps) {
    const handleRoleToggle = (roleId: string) => {
        onChange({
            ...buyingGroup,
            roles: buyingGroup.roles.map(r =>
                r.id === roleId ? { ...r, isActive: !r.isActive } : r
            )
        });
    };

    const handleInfluenceChange = (roleId: string, influence: 'high' | 'medium' | 'low') => {
        onChange({
            ...buyingGroup,
            roles: buyingGroup.roles.map(r =>
                r.id === roleId ? { ...r, influence } : r
            )
        });
    };

    const handleJobChange = (job: BuyingJob) => {
        const existing = buyingGroup.buyingJobs.findIndex(j => j.job === job.job);
        const newJobs = [...buyingGroup.buyingJobs];
        if (existing >= 0) {
            newJobs[existing] = job;
        } else {
            newJobs.push(job);
        }
        onChange({ ...buyingGroup, buyingJobs: newJobs });
    };

    const handleFrictionChange = (level: number) => {
        onChange({ ...buyingGroup, frictionLevel: level });
    };

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="text-center space-y-2">
                <h1 className="text-3xl font-serif font-bold text-foreground">
                    Buying Group Map
                </h1>
                <p className="text-muted-foreground max-w-lg mx-auto">
                    B2B buying is consensus, not one decision maker. Map who does what.
                </p>
            </div>

            {/* Roles Section */}
            <div className="max-w-2xl mx-auto">
                <div className="flex items-center gap-2 mb-4">
                    <Users className="h-5 w-5 text-muted-foreground" />
                    <h2 className="font-semibold">Buying Roles</h2>
                </div>
                <div className="grid gap-3">
                    {buyingGroup.roles.map(role => (
                        <RoleCard
                            key={role.id}
                            role={role}
                            onToggle={() => handleRoleToggle(role.id)}
                            onInfluenceChange={(inf) => handleInfluenceChange(role.id, inf)}
                        />
                    ))}
                </div>
            </div>

            {/* Buying Jobs Section */}
            <div className="max-w-2xl mx-auto">
                <h2 className="font-semibold mb-4">Buying Jobs (Gartner Model)</h2>
                <div className="space-y-3">
                    {BUYING_JOBS.map(jobDef => (
                        <BuyingJobRow
                            key={jobDef.job}
                            jobDef={jobDef}
                            buyingJob={buyingGroup.buyingJobs.find(j => j.job === jobDef.job)}
                            roles={buyingGroup.roles}
                            onChange={handleJobChange}
                        />
                    ))}
                </div>
            </div>

            {/* Friction Level */}
            <div className="max-w-2xl mx-auto">
                <h2 className="font-semibold mb-4">Procurement Friction</h2>
                <div className="flex gap-2">
                    {[1, 2, 3, 4, 5].map(level => (
                        <button
                            key={level}
                            onClick={() => handleFrictionChange(level)}
                            className={cn(
                                "flex-1 py-3 rounded-lg text-sm font-medium transition-colors",
                                buyingGroup.frictionLevel === level
                                    ? "bg-primary text-primary-foreground"
                                    : "bg-muted text-muted-foreground hover:bg-muted/80"
                            )}
                        >
                            {level === 1 ? 'Low' : level === 5 ? 'High' : level}
                        </button>
                    ))}
                </div>
                <p className="text-xs text-muted-foreground mt-2 text-center">
                    Higher friction = more approvals, longer cycle
                </p>
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
