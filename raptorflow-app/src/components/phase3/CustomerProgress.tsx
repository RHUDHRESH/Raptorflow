'use client';

import React, { useState } from 'react';
import { ChevronRight, GripVertical, Plus, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { JTBDForces, JTBDJob } from '@/lib/foundation';

interface CustomerProgressProps {
    jtbd: JTBDForces;
    onUpdate: (jtbd: JTBDForces) => void;
    onContinue: () => void;
    onBack: () => void;
}

// Forces slider with visual weight
function ForceSlider({
    label,
    value,
    onChange,
    color,
}: {
    label: string;
    value: number;
    onChange: (value: number) => void;
    color: string;
}) {
    return (
        <div className="space-y-2">
            <div className="flex items-center justify-between">
                <span className="text-[13px] font-medium text-[#2D3538]">{label}</span>
                <span className="text-[12px] font-mono text-[#9D9F9F]">{value}%</span>
            </div>
            <div className="relative h-3 bg-[#E5E6E3] rounded-full overflow-hidden">
                <div
                    className="h-full rounded-full transition-all duration-300"
                    style={{ width: `${value}%`, backgroundColor: color }}
                />
            </div>
            <Slider
                value={[value]}
                onValueChange={([v]) => onChange(v)}
                max={100}
                step={5}
                className="mt-2"
            />
        </div>
    );
}

// Struggling moment card
function StrugglingMomentCard({
    moment,
    index,
    onRemove,
}: {
    moment: string;
    index: number;
    onRemove: () => void;
}) {
    return (
        <div className="group flex items-center gap-3 bg-white border border-[#E5E6E3] rounded-xl px-4 py-3">
            <div className="w-6 h-6 rounded-full bg-[#F3F4EE] flex items-center justify-center text-[11px] font-mono text-[#5B5F61]">
                {index + 1}
            </div>
            <span className="flex-1 text-[14px] text-[#2D3538]">{moment}</span>
            <button
                onClick={onRemove}
                className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-[#F3F4EE] rounded-lg"
            >
                <X className="w-4 h-4 text-[#9D9F9F]" />
            </button>
        </div>
    );
}

// Job card with type badge
function JobCard({
    job,
    isSelected,
    onSelect,
}: {
    job: JTBDJob;
    isSelected: boolean;
    onSelect: () => void;
}) {
    const typeBadgeColors = {
        functional: 'bg-[#2D3538] text-white',
        emotional: 'bg-[#D7C9AE] text-[#2D3538]',
        social: 'bg-[#9D9F9F] text-white',
    };

    return (
        <button
            onClick={onSelect}
            className={`w-full text-left p-5 rounded-2xl border-2 transition-all ${isSelected
                ? 'border-[#2D3538] bg-white shadow-sm'
                : 'border-[#E5E6E3] bg-white hover:border-[#C0C1BE]'
                }`}
        >
            <div className="flex items-center gap-2 mb-3">
                <span
                    className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-mono uppercase tracking-[0.1em] ${typeBadgeColors[job.type]
                        }`}
                >
                    {job.type}
                </span>
                {isSelected && (
                    <span className="inline-flex px-2 py-0.5 rounded-full text-[10px] font-mono uppercase tracking-[0.1em] bg-[#2D3538] text-white">
                        Selected
                    </span>
                )}
            </div>
            <p className="text-[15px] text-[#2D3538] leading-relaxed">{job.statement}</p>
        </button>
    );
}

export function CustomerProgress({
    jtbd,
    onUpdate,
    onContinue,
    onBack,
}: CustomerProgressProps) {
    const [newMoment, setNewMoment] = useState('');
    const [isAddingJob, setIsAddingJob] = useState(false);
    const [newJobText, setNewJobText] = useState('');
    const [newJobType, setNewJobType] = useState<'functional' | 'emotional' | 'social'>('functional');

    // Calculate force weights (normalize to 100 total)
    const defaultWeights = { push: 30, pull: 30, anxiety: 20, habit: 20 };
    const [forceWeights, setForceWeights] = useState(defaultWeights);

    const handleForceChange = (force: keyof typeof forceWeights, value: number) => {
        setForceWeights((prev) => ({ ...prev, [force]: value }));
    };

    const handleSelectJob = (jobId: string) => {
        const updatedJobs = jtbd.jobs.map((j) => ({
            ...j,
            isPrimary: j.id === jobId,
        }));
        onUpdate({ ...jtbd, jobs: updatedJobs });
    };

    const handleAddJob = () => {
        if (!newJobText.trim()) return;
        const newJob: JTBDJob = {
            id: `job-${Date.now()}`,
            type: newJobType,
            statement: newJobText.trim(),
            isPrimary: jtbd.jobs.length === 0, // Make first job primary
        };
        onUpdate({
            ...jtbd,
            jobs: [...jtbd.jobs, newJob],
        });
        setNewJobText('');
        setIsAddingJob(false);
    };

    const handleAddMoment = () => {
        if (!newMoment.trim()) return;
        onUpdate({
            ...jtbd,
            strugglingMoments: [...jtbd.strugglingMoments, newMoment.trim()],
        });
        setNewMoment('');
    };

    const handleRemoveMoment = (index: number) => {
        const updated = jtbd.strugglingMoments.filter((_, i) => i !== index);
        onUpdate({ ...jtbd, strugglingMoments: updated });
    };

    const selectedJob = jtbd.jobs.find((j) => j.isPrimary);

    return (
        <div className="space-y-10">
            {/* Three Column Layout */}
            <div className="grid grid-cols-3 gap-8">
                {/* Column A: Job/Progress Statement */}
                <div className="space-y-6">
                    <div className="flex items-start justify-between">
                        <div>
                            <h3 className="text-[11px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">
                                Progress Statement
                            </h3>
                            <p className="text-[14px] text-[#5B5F61] mb-6">
                                What job is your customer trying to get done? Select one or add your own.
                            </p>
                        </div>
                        {!isAddingJob && (
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setIsAddingJob(true)}
                                className="text-[#5B5F61] border-[#C0C1BE]"
                            >
                                <Plus className="w-4 h-4 mr-1" />
                                Add Job
                            </Button>
                        )}
                    </div>

                    {/* Add Job Form */}
                    {isAddingJob && (
                        <div className="bg-white border-2 border-[#2D3538] rounded-2xl p-5 space-y-4">
                            <div>
                                <label className="text-[11px] font-mono uppercase tracking-[0.1em] text-[#9D9F9F] block mb-2">
                                    Job Type
                                </label>
                                <div className="flex gap-2">
                                    {(['functional', 'emotional', 'social'] as const).map((type) => (
                                        <button
                                            key={type}
                                            onClick={() => setNewJobType(type)}
                                            className={`px-3 py-1.5 rounded-lg text-[11px] font-medium capitalize transition-all ${newJobType === type
                                                ? 'bg-[#2D3538] text-white'
                                                : 'bg-[#F3F4EE] text-[#5B5F61] hover:bg-[#E5E6E3]'
                                                }`}
                                        >
                                            {type}
                                        </button>
                                    ))}
                                </div>
                            </div>
                            <div>
                                <label className="text-[11px] font-mono uppercase tracking-[0.1em] text-[#9D9F9F] block mb-2">
                                    Job Statement
                                </label>
                                <textarea
                                    value={newJobText}
                                    onChange={(e) => setNewJobText(e.target.value)}
                                    placeholder="e.g., 'Get my marketing strategy clear and actionable'"
                                    rows={3}
                                    className="w-full bg-[#FAFAF8] border border-[#E5E6E3] rounded-xl px-4 py-3 text-[14px] text-[#2D3538] placeholder:text-[#9D9F9F] focus:outline-none focus:ring-2 focus:ring-[#2D3538]/10"
                                />
                            </div>
                            <div className="flex gap-2">
                                <Button
                                    onClick={handleAddJob}
                                    disabled={!newJobText.trim()}
                                    className="bg-[#2D3538] text-white disabled:bg-[#9D9F9F]"
                                >
                                    Add Job
                                </Button>
                                <Button
                                    variant="ghost"
                                    onClick={() => {
                                        setIsAddingJob(false);
                                        setNewJobText('');
                                    }}
                                >
                                    Cancel
                                </Button>
                            </div>
                        </div>
                    )}

                    <div className="space-y-3">
                        {jtbd.jobs.map((job) => (
                            <JobCard
                                key={job.id}
                                job={job}
                                isSelected={job.isPrimary}
                                onSelect={() => handleSelectJob(job.id)}
                            />
                        ))}
                    </div>

                    {jtbd.jobs.length === 0 && !isAddingJob && (
                        <div className="bg-[#FAFAF8] border border-dashed border-[#C0C1BE] rounded-2xl p-8 text-center">
                            <p className="text-[#5B5F61] text-[14px] mb-3">No jobs defined yet</p>
                            <p className="text-[12px] text-[#9D9F9F]">Click "Add Job" above to define what your customer is trying to achieve.</p>
                        </div>
                    )}
                </div>

                {/* Column B: Forces of Progress */}
                <div className="space-y-6">
                    <div>
                        <h3 className="text-[11px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">
                            What Drives Change?
                        </h3>
                        <p className="text-[14px] text-[#5B5F61] mb-6">
                            How strongly does each force affect your customer's decision to switch?
                        </p>
                    </div>

                    <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6 space-y-6">
                        <ForceSlider
                            label="Pain of current situation"
                            value={forceWeights.push}
                            onChange={(v) => handleForceChange('push', v)}
                            color="#2D3538"
                        />
                        <ForceSlider
                            label="Attraction to your solution"
                            value={forceWeights.pull}
                            onChange={(v) => handleForceChange('pull', v)}
                            color="#22C55E"
                        />
                        <ForceSlider
                            label="Fear of switching"
                            value={forceWeights.anxiety}
                            onChange={(v) => handleForceChange('anxiety', v)}
                            color="#F59E0B"
                        />
                        <ForceSlider
                            label="Comfort with status quo"
                            value={forceWeights.habit}
                            onChange={(v) => handleForceChange('habit', v)}
                            color="#9D9F9F"
                        />
                    </div>

                    {/* Forces Summary */}
                    <div className="bg-[#FAFAF8] rounded-xl p-4">
                        <p className="text-[12px] text-[#5B5F61]">
                            {forceWeights.push + forceWeights.pull > forceWeights.anxiety + forceWeights.habit
                                ? '✓ Motivation outweighs resistance — customers are likely to switch'
                                : '⚠ Resistance is strong — you need to address fear and comfort'}
                        </p>
                    </div>
                </div>

                {/* Column C: Struggling Moments */}
                <div className="space-y-6">
                    <div>
                        <h3 className="text-[11px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">
                            Friction Points
                        </h3>
                        <p className="text-[14px] text-[#5B5F61] mb-6">
                            What frustrations trigger your customer to look for a solution?
                        </p>
                    </div>

                    <div className="space-y-3">
                        {jtbd.strugglingMoments.map((moment, index) => (
                            <StrugglingMomentCard
                                key={index}
                                moment={moment}
                                index={index}
                                onRemove={() => handleRemoveMoment(index)}
                            />
                        ))}
                    </div>

                    {/* Add new moment */}
                    <div className="flex items-center gap-2">
                        <input
                            type="text"
                            value={newMoment}
                            onChange={(e) => setNewMoment(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleAddMoment()}
                            placeholder="Add a struggling moment..."
                            className="flex-1 bg-white border border-[#E5E6E3] rounded-xl px-4 py-3 text-[14px] text-[#2D3538] placeholder:text-[#9D9F9F] focus:outline-none focus:ring-2 focus:ring-[#2D3538]/10"
                        />
                        <Button
                            onClick={handleAddMoment}
                            variant="outline"
                            size="icon"
                            className="h-12 w-12 rounded-xl border-[#E5E6E3]"
                        >
                            <Plus className="w-4 h-4" />
                        </Button>
                    </div>
                </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between pt-8 border-t border-[#E5E6E3]">
                <Button
                    variant="ghost"
                    onClick={onBack}
                    className="text-[#5B5F61] hover:text-[#2D3538]"
                >
                    ← Back
                </Button>
                <Button
                    onClick={onContinue}
                    disabled={!selectedJob}
                    className="bg-[#2D3538] hover:bg-[#1A1D1E] disabled:bg-[#9D9F9F] text-white px-10 py-6 rounded-2xl text-[15px] font-medium"
                >
                    Continue
                </Button>
            </div>
        </div>
    );
}
