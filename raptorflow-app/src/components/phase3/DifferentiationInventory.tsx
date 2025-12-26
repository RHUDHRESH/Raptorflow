'use client';

import React from 'react';
import { Differentiator, DifferentiatorStatus } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ArrowRight, Check, AlertTriangle, X, Plus, Upload, Link } from 'lucide-react';
import { cn } from '@/lib/utils';

interface DifferentiationInventoryProps {
    differentiators: Differentiator[];
    onChange: (differentiators: Differentiator[]) => void;
    onContinue: () => void;
}

function StatusBadge({ status }: { status: DifferentiatorStatus }) {
    const config: Record<DifferentiatorStatus, { bg: string; text: string; label: string }> = {
        proven: {
            bg: 'bg-green-100 dark:bg-green-900/30',
            text: 'text-green-700 dark:text-green-400',
            label: 'Proven',
        },
        unproven: {
            bg: 'bg-amber-100 dark:bg-amber-900/30',
            text: 'text-amber-700 dark:text-amber-400',
            label: 'Needs Proof',
        },
        blocked: {
            bg: 'bg-red-100 dark:bg-red-900/30',
            text: 'text-red-700 dark:text-red-400',
            label: 'Blocked',
        },
    };

    const { bg, text, label } = config[status];

    return (
        <span className={cn("text-xs px-2 py-1 rounded-full font-medium", bg, text)}>
            {label}
        </span>
    );
}

function DifferentiatorCard({
    diff,
    onUpdate,
    onRemove,
}: {
    diff: Differentiator;
    onUpdate: (diff: Differentiator) => void;
    onRemove: () => void;
}) {
    const [showProofInput, setShowProofInput] = React.useState(false);
    const [proofUrl, setProofUrl] = React.useState('');

    const addProof = () => {
        if (proofUrl.trim()) {
            onUpdate({
                ...diff,
                proof: [...diff.proof, proofUrl.trim()],
                status: 'proven',
            });
            setProofUrl('');
            setShowProofInput(false);
        }
    };

    const toggleStatus = () => {
        const nextStatus: Record<DifferentiatorStatus, DifferentiatorStatus> = {
            proven: 'unproven',
            unproven: 'blocked',
            blocked: 'proven',
        };
        onUpdate({ ...diff, status: nextStatus[diff.status] });
    };

    return (
        <div className={cn(
            "p-5 rounded-xl border-2 transition-all",
            diff.status === 'blocked' ? "opacity-50 border-dashed" : "border-border"
        )}>
            <div className="flex items-start gap-4">
                <div className="flex-1 space-y-3">
                    {/* Capability */}
                    <div>
                        <label className="text-xs text-muted-foreground uppercase tracking-wider">Capability</label>
                        <p className="text-lg font-medium text-foreground">{diff.capability}</p>
                    </div>

                    {/* Mechanism */}
                    <div>
                        <label className="text-xs text-muted-foreground uppercase tracking-wider">Mechanism (How)</label>
                        <p className="text-sm text-muted-foreground">{diff.mechanism}</p>
                    </div>

                    {/* Proof */}
                    <div>
                        <label className="text-xs text-muted-foreground uppercase tracking-wider">Proof</label>
                        {diff.proof.length > 0 ? (
                            <div className="flex flex-wrap gap-2 mt-1">
                                {diff.proof.map((p, i) => (
                                    <a
                                        key={i}
                                        href={p}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-xs text-primary hover:underline flex items-center gap-1 bg-primary/5 px-2 py-1 rounded"
                                    >
                                        <Link className="h-3 w-3" />
                                        {p.length > 30 ? p.slice(0, 30) + '...' : p}
                                    </a>
                                ))}
                            </div>
                        ) : (
                            <p className="text-sm text-amber-600 flex items-center gap-1 mt-1">
                                <AlertTriangle className="h-3 w-3" /> No proof attached
                            </p>
                        )}

                        {showProofInput ? (
                            <div className="flex gap-2 mt-2">
                                <Input
                                    placeholder="Paste URL or file reference..."
                                    value={proofUrl}
                                    onChange={(e) => setProofUrl(e.target.value)}
                                    className="text-sm"
                                    autoFocus
                                />
                                <Button size="sm" onClick={addProof}>Add</Button>
                                <Button size="sm" variant="ghost" onClick={() => setShowProofInput(false)}>
                                    <X className="h-4 w-4" />
                                </Button>
                            </div>
                        ) : (
                            <button
                                onClick={() => setShowProofInput(true)}
                                className="text-xs text-primary hover:underline flex items-center gap-1 mt-2"
                            >
                                <Upload className="h-3 w-3" /> Attach proof
                            </button>
                        )}
                    </div>
                </div>

                <div className="flex flex-col items-end gap-2">
                    <button onClick={toggleStatus}>
                        <StatusBadge status={diff.status} />
                    </button>
                    <button
                        onClick={onRemove}
                        className="p-1 hover:bg-destructive/10 rounded text-muted-foreground"
                    >
                        <X className="h-4 w-4" />
                    </button>
                </div>
            </div>
        </div>
    );
}

export function DifferentiationInventory({ differentiators, onChange, onContinue }: DifferentiationInventoryProps) {
    const provenCount = differentiators.filter(d => d.status === 'proven').length;
    const totalCount = differentiators.filter(d => d.status !== 'blocked').length;

    const updateDiff = (id: string, diff: Differentiator) => {
        onChange(differentiators.map(d => d.id === id ? diff : d));
    };

    const removeDiff = (id: string) => {
        onChange(differentiators.filter(d => d.id !== id));
    };

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="text-center space-y-2">
                <h1 className="text-3xl font-serif font-bold text-foreground">
                    Differentiation Inventory
                </h1>
                <p className="text-muted-foreground max-w-lg mx-auto">
                    Claims without proof are marketing fiction. Attach evidence to graduate each differentiator.
                </p>
            </div>

            {/* Progress */}
            <div className="max-w-md mx-auto bg-card border rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">Proof Coverage</span>
                    <span className={cn(
                        "text-sm font-bold",
                        provenCount === totalCount ? "text-green-600" : "text-amber-600"
                    )}>
                        {provenCount} / {totalCount} proven
                    </span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                        className={cn(
                            "h-full rounded-full transition-all",
                            provenCount === totalCount ? "bg-green-500" : "bg-amber-500"
                        )}
                        style={{ width: totalCount > 0 ? `${(provenCount / totalCount) * 100}%` : '0%' }}
                    />
                </div>
            </div>

            {/* Differentiators */}
            <div className="space-y-4 max-w-3xl mx-auto">
                {differentiators.map(diff => (
                    <DifferentiatorCard
                        key={diff.id}
                        diff={diff}
                        onUpdate={(d) => updateDiff(diff.id, d)}
                        onRemove={() => removeDiff(diff.id)}
                    />
                ))}
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
