'use client';

import React, { useState } from 'react';
import { PrimaryContext } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Check, Pencil, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ContextConfirmProps {
    context: PrimaryContext;
    onChange: (context: PrimaryContext) => void;
    onConfirm: () => void;
}

interface ContextCardProps {
    label: string;
    value: string;
    onEdit: (value: string) => void;
}

function ContextCard({ label, value, onEdit }: ContextCardProps) {
    const [isEditing, setIsEditing] = useState(false);
    const [editValue, setEditValue] = useState(value);

    const handleSave = () => {
        onEdit(editValue);
        setIsEditing(false);
    };

    const handleCancel = () => {
        setEditValue(value);
        setIsEditing(false);
    };

    return (
        <div className={cn(
            "relative bg-card border-2 rounded-2xl p-6 transition-all",
            isEditing ? "border-primary" : "border-border hover:border-primary/30"
        )}>
            <div className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">
                {label}
            </div>

            {isEditing ? (
                <div className="space-y-3">
                    <Input
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        className="text-lg font-medium"
                        autoFocus
                    />
                    <div className="flex gap-2 justify-end">
                        <Button size="sm" variant="ghost" onClick={handleCancel}>
                            <X className="h-4 w-4 mr-1" /> Cancel
                        </Button>
                        <Button size="sm" onClick={handleSave}>
                            <Check className="h-4 w-4 mr-1" /> Save
                        </Button>
                    </div>
                </div>
            ) : (
                <div className="flex items-start justify-between gap-4">
                    <p className="text-xl font-semibold text-foreground leading-tight">
                        {value || <span className="text-muted-foreground italic">Not detected</span>}
                    </p>
                    <button
                        onClick={() => setIsEditing(true)}
                        className="p-2 rounded-lg hover:bg-muted transition-colors flex-shrink-0"
                    >
                        <Pencil className="h-4 w-4 text-muted-foreground" />
                    </button>
                </div>
            )}
        </div>
    );
}

export function ContextConfirm({ context, onChange, onConfirm }: ContextConfirmProps) {
    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="text-center space-y-2">
                <h1 className="text-3xl font-serif font-bold text-foreground">
                    Here's what we understood
                </h1>
                <p className="text-muted-foreground max-w-md mx-auto">
                    Confirm or edit these three cards. This becomes the foundation for everything we derive.
                </p>
            </div>

            {/* Context Cards */}
            <div className="grid gap-6 max-w-2xl mx-auto">
                <ContextCard
                    label="You sell"
                    value={context.youSell}
                    onEdit={(v) => onChange({ ...context, youSell: v })}
                />
                <ContextCard
                    label="To"
                    value={context.to}
                    onEdit={(v) => onChange({ ...context, to: v })}
                />
                <ContextCard
                    label="So they can"
                    value={context.soTheyCan}
                    onEdit={(v) => onChange({ ...context, soTheyCan: v })}
                />
            </div>

            {/* Confirm Button */}
            <div className="flex justify-center pt-4">
                <Button
                    size="lg"
                    onClick={onConfirm}
                    className="px-8 py-6 text-lg rounded-xl"
                >
                    <Check className="h-5 w-5 mr-2" />
                    Looks right — Continue
                </Button>
            </div>
        </div>
    );
}
