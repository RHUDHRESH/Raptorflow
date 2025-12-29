'use client';

import React, { useState } from 'react';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { AssetTypeSelector } from './AssetTypeSelector';
import { AssetType, getAssetConfig } from './types';
import { Sparkles, X, Wand2, ArrowRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'motion/react';

interface CreateAssetModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onCreate: (type: AssetType, prompt?: string) => void;
}

export function CreateAssetModal({
    open,
    onOpenChange,
    onCreate,
}: CreateAssetModalProps) {
    const [selectedType, setSelectedType] = useState<AssetType | undefined>(undefined);
    const [prompt, setPrompt] = useState('');
    const [mode, setMode] = useState<'type' | 'prompt'>('type');

    const config = selectedType ? getAssetConfig(selectedType) : undefined;

    const handleNext = () => {
        if (mode === 'type' && selectedType) {
            setMode('prompt');
        } else if (mode === 'prompt' && selectedType) {
            onCreate(selectedType, prompt.trim() || undefined);
            reset();
        }
    };

    const reset = () => {
        setSelectedType(undefined);
        setPrompt('');
        setMode('type');
        onOpenChange(false);
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-xl p-0 overflow-hidden bg-white border-[#E5E6E3] rounded-3xl shadow-2xl">
                <div className="p-8 space-y-8">
                    <DialogHeader className="space-y-3">
                        <div className="flex items-center justify-between">
                            <DialogTitle className="font-serif text-[32px] text-[#2D3538] tracking-tight leading-none">
                                {mode === 'type' ? 'Select Artifact' : 'The Spark'}
                            </DialogTitle>
                            <div className="h-10 w-10 rounded-full bg-[#F8F9F7] border border-[#C0C1BE]/30 flex items-center justify-center">
                                <Sparkles className="h-5 w-5 text-[#2D3538]" />
                            </div>
                        </div>
                        <DialogDescription className="font-sans text-[15px] text-[#5B5F61]">
                            {mode === 'type'
                                ? 'What kind of brand artifact are we distilled today?'
                                : `What should this ${config?.label?.toLowerCase() || 'asset'} be about?`}
                        </DialogDescription>
                    </DialogHeader>

                    <div className="relative min-h-[300px]">
                        <AnimatePresence mode="wait">
                            {mode === 'type' ? (
                                <motion.div
                                    key="type-selector"
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: 20 }}
                                    transition={{ duration: 0.3 }}
                                >
                                    <AssetTypeSelector
                                        onSelect={setSelectedType}
                                        selectedType={selectedType}
                                    />
                                </motion.div>
                            ) : (
                                <motion.div
                                    key="prompt-input"
                                    initial={{ opacity: 0, x: 20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: -20 }}
                                    transition={{ duration: 0.3 }}
                                    className="space-y-6"
                                >
                                    <div className="relative group">
                                        <textarea
                                            value={prompt}
                                            onChange={(e) => setPrompt(e.target.value)}
                                            placeholder="Describe the context, tone, or specific details..."
                                            className={cn(
                                                "w-full h-40 p-6 rounded-2xl bg-[#F8F9F7] border border-[#E5E6E3]",
                                                "text-[15px] text-[#2D3538] placeholder:text-[#9D9F9F] leading-relaxed",
                                                "focus:outline-none focus:border-[#2D3538] focus:bg-white transition-all",
                                                "resize-none"
                                            )}
                                            autoFocus
                                        />
                                        <div className="absolute bottom-4 right-4 text-[11px] font-mono text-[#9D9F9F] group-focus-within:text-[#2D3538] transition-colors">
                                            Speed Daemon Active
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-2 p-4 rounded-xl bg-[#F3F4EE] border border-[#C0C1BE]/20">
                                        <Wand2 className="h-4 w-4 text-[#5B5F61]" />
                                        <p className="text-[13px] text-[#5B5F61]">
                                            Leave empty to start from a blank canvas.
                                        </p>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    <DialogFooter className="flex items-center justify-between sm:justify-between border-t border-[#E5E6E3] pt-8 mt-4">
                        {mode === 'prompt' ? (
                            <Button
                                variant="ghost"
                                onClick={() => setMode('type')}
                                className="text-[#5B5F61] hover:text-[#2D3538] hover:bg-[#F8F9F7] px-0"
                            >
                                Back to types
                            </Button>
                        ) : (
                            <div />
                        )}

                        <Button
                            disabled={mode === 'type' && !selectedType}
                            onClick={handleNext}
                            className={cn(
                                "h-12 px-8 rounded-xl bg-[#1a1d1e] text-white font-medium group transition-all",
                                "hover:scale-[1.02] active:scale-[0.98] shadow-lg hover:shadow-xl",
                                "disabled:opacity-30 disabled:hover:scale-100 disabled:shadow-none"
                            )}
                        >
                            <span className="mr-2">
                                {mode === 'type' ? 'Continue' : prompt.trim() ? 'Generate with Muse' : 'Create Blank'}
                            </span>
                            <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                        </Button>
                    </DialogFooter>
                </div>
            </DialogContent>
        </Dialog>
    );
}
