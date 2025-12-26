'use client';

import React, { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Plus, Trash2, GripVertical } from 'lucide-react';
import { WorkflowStep } from '@/lib/foundation';
import { Reorder } from 'framer-motion';

interface StepBuilderProps {
    value: WorkflowStep[];
    onChange: (value: WorkflowStep[]) => void;
}

const emptyStep: WorkflowStep = { action: '', tool: '', timeSpent: '' };

export function StepBuilder({ value = [], onChange }: StepBuilderProps) {
    const steps = value.length > 0 ? value : [{ ...emptyStep }];

    const addStep = () => {
        onChange([...steps, { ...emptyStep }]);
    };

    const removeStep = (index: number) => {
        if (steps.length > 1) {
            onChange(steps.filter((_, i) => i !== index));
        }
    };

    const updateStep = (index: number, field: keyof WorkflowStep, newValue: string) => {
        const newSteps = [...steps];
        newSteps[index] = { ...newSteps[index], [field]: newValue };
        onChange(newSteps);
    };

    return (
        <div className="space-y-4">
            <Reorder.Group
                axis="y"
                values={steps}
                onReorder={onChange}
                className="space-y-3"
            >
                {steps.map((step, index) => (
                    <Reorder.Item
                        key={index}
                        value={step}
                        className="bg-card border-2 border-border rounded-xl p-4 cursor-grab active:cursor-grabbing shadow-sm hover:border-sidebar-accent transition-colors"
                    >
                        <div className="flex items-start gap-3">
                            <div className="text-muted-foreground/50 mt-3">
                                <GripVertical className="w-5 h-5" />
                            </div>
                            <div className="flex-1 space-y-3">
                                <div className="flex items-center gap-2">
                                    <span className="text-xs font-mono font-bold text-muted-foreground/50 bg-muted/50 px-2 py-1 rounded">
                                        Step {index + 1}
                                    </span>
                                </div>
                                <Input
                                    placeholder="What action do you take?"
                                    value={step.action}
                                    onChange={(e) => updateStep(index, 'action', e.target.value)}
                                    className="h-12 text-base bg-background border-2 focus-visible:ring-0 focus-visible:border-primary"
                                />
                                <div className="grid grid-cols-2 gap-3">
                                    <Input
                                        placeholder="Tool used (e.g., Notion, Sheets)"
                                        value={step.tool}
                                        onChange={(e) => updateStep(index, 'tool', e.target.value)}
                                        className="h-10 text-sm bg-background border-2 focus-visible:ring-0 focus-visible:border-primary"
                                    />
                                    <Input
                                        placeholder="Time spent (e.g., 30 min)"
                                        value={step.timeSpent}
                                        onChange={(e) => updateStep(index, 'timeSpent', e.target.value)}
                                        className="h-10 text-sm bg-background border-2 focus-visible:ring-0 focus-visible:border-primary"
                                    />
                                </div>
                            </div>
                            {steps.length > 1 && (
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={() => removeStep(index)}
                                    className="text-muted-foreground hover:text-destructive mt-3"
                                >
                                    <Trash2 className="h-4 w-4" />
                                </Button>
                            )}
                        </div>
                    </Reorder.Item>
                ))}
            </Reorder.Group>

            <Button
                variant="outline"
                onClick={addStep}
                className="w-full h-12 border-dashed border-2 hover:border-primary hover:bg-accent/5"
            >
                <Plus className="h-4 w-4 mr-2" />
                Add Step
            </Button>

            <p className="text-xs text-center text-muted-foreground">
                Drag to reorder • Describe each step in your current workflow
            </p>
        </div>
    );
}
