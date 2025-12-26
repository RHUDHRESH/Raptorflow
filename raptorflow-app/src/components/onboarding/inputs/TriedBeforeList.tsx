'use client';

import React from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Plus, Trash2 } from 'lucide-react';
import { TriedBefore } from '@/lib/foundation';

interface TriedBeforeListProps {
    value: TriedBefore[];
    onChange: (value: TriedBefore[]) => void;
}

const emptyEntry: TriedBefore = { toolOrService: '', whatYouHoped: '', whatFailed: '' };

export function TriedBeforeList({ value = [], onChange }: TriedBeforeListProps) {
    const entries = value.length > 0 ? value : [{ ...emptyEntry }];

    const addEntry = () => {
        onChange([...entries, { ...emptyEntry }]);
    };

    const removeEntry = (index: number) => {
        if (entries.length > 1) {
            onChange(entries.filter((_, i) => i !== index));
        }
    };

    const updateEntry = (index: number, field: keyof TriedBefore, newValue: string) => {
        const newEntries = [...entries];
        newEntries[index] = { ...newEntries[index], [field]: newValue };
        onChange(newEntries);
    };

    return (
        <div className="space-y-4">
            {entries.map((entry, index) => (
                <div
                    key={index}
                    className="bg-card border-2 border-border rounded-xl p-5 shadow-sm relative group"
                >
                    <div className="absolute -top-3 left-4 px-2 py-0.5 bg-muted text-xs font-mono font-bold text-muted-foreground rounded">
                        #{index + 1}
                    </div>

                    {entries.length > 1 && (
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => removeEntry(index)}
                            className="absolute top-2 right-2 text-muted-foreground hover:text-destructive opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                            <Trash2 className="h-4 w-4" />
                        </Button>
                    )}

                    <div className="space-y-4 mt-2">
                        <div>
                            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1.5 block">
                                Tool or Service
                            </label>
                            <Input
                                placeholder="e.g., HubSpot, Agency X, Internal team"
                                value={entry.toolOrService}
                                onChange={(e) => updateEntry(index, 'toolOrService', e.target.value)}
                                className="h-11 text-base bg-background border-2 focus-visible:ring-0 focus-visible:border-primary"
                            />
                        </div>

                        <div>
                            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1.5 block">
                                What you hoped for
                            </label>
                            <Input
                                placeholder="I wanted it to..."
                                value={entry.whatYouHoped}
                                onChange={(e) => updateEntry(index, 'whatYouHoped', e.target.value)}
                                className="h-11 text-base bg-background border-2 focus-visible:ring-0 focus-visible:border-primary"
                            />
                        </div>

                        <div>
                            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1.5 block">
                                Why it didn't work
                            </label>
                            <Input
                                placeholder="It failed because..."
                                value={entry.whatFailed}
                                onChange={(e) => updateEntry(index, 'whatFailed', e.target.value)}
                                className="h-11 text-base bg-background border-2 focus-visible:ring-0 focus-visible:border-primary"
                            />
                        </div>
                    </div>
                </div>
            ))}

            <Button
                variant="outline"
                onClick={addEntry}
                className="w-full h-12 border-dashed border-2 hover:border-primary hover:bg-accent/5"
            >
                <Plus className="h-4 w-4 mr-2" />
                Add Another
            </Button>

            <p className="text-xs text-center text-muted-foreground">
                Each entry helps us understand your objections and alternatives
            </p>
        </div>
    );
}
