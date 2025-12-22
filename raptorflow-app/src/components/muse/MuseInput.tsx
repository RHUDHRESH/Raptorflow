'use client';

import React, { useState, useRef, useCallback } from 'react';
import { Send, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';
import { AssetType, ASSET_TYPES, getAssetConfig } from './types';

interface MuseInputProps {
    onSubmit: (prompt: string, detectedType?: AssetType) => void;
    disabled?: boolean;
    className?: string;
}

// Simple keyword detection for asset types
function detectAssetType(prompt: string): AssetType | undefined {
    const lower = prompt.toLowerCase();

    if (lower.includes('meme')) return 'meme';
    if (lower.includes('wireframe')) return 'wireframe';
    if (lower.includes('sales email') || lower.includes('cold email')) return 'sales-email';
    if (lower.includes('nurture')) return 'nurture-email';
    if (lower.includes('email')) return 'email';
    if (lower.includes('tagline')) return 'tagline';
    if (lower.includes('one-liner') || lower.includes('elevator pitch')) return 'one-liner';
    if (lower.includes('brand story') || lower.includes('story')) return 'brand-story';
    if (lower.includes('video script') || lower.includes('script')) return 'video-script';
    if (lower.includes('social') || lower.includes('linkedin') || lower.includes('twitter')) return 'social-post';
    if (lower.includes('product description') || lower.includes('description')) return 'product-description';
    if (lower.includes('product name') || lower.includes('name idea')) return 'product-name';
    if (lower.includes('domain')) return 'domain-name';
    if (lower.includes('pdf') || lower.includes('lead magnet')) return 'lead-gen-pdf';
    if (lower.includes('talking point') || lower.includes('sales call')) return 'sales-talking-points';

    return undefined;
}

export function MuseInput({ onSubmit, disabled, className }: MuseInputProps) {
    const [value, setValue] = useState('');
    const [isFocused, setIsFocused] = useState(false);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const detectedType = detectAssetType(value);
    const detectedConfig = detectedType ? getAssetConfig(detectedType) : undefined;

    const handleSubmit = useCallback(() => {
        if (!value.trim() || disabled) return;
        onSubmit(value.trim(), detectedType);
        setValue('');
    }, [value, onSubmit, disabled, detectedType]);

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    // Auto-resize textarea
    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setValue(e.target.value);
        const textarea = textareaRef.current;
        if (textarea) {
            textarea.style.height = 'auto';
            textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
        }
    };

    return (
        <div className={cn('w-full max-w-2xl mx-auto', className)}>
            {/* Main input container */}
            <div
                className={cn(
                    'relative group rounded-2xl border bg-card transition-all duration-300',
                    isFocused
                        ? 'border-foreground/20 shadow-lg shadow-foreground/5'
                        : 'border-border/60 shadow-sm',
                    disabled && 'opacity-50 cursor-not-allowed'
                )}
            >
                {/* Subtle glow on focus */}
                <div
                    className={cn(
                        'absolute inset-0 rounded-2xl bg-gradient-to-b from-foreground/5 to-transparent opacity-0 transition-opacity duration-500 pointer-events-none',
                        isFocused && 'opacity-100'
                    )}
                />

                <div className="relative p-4">
                    {/* Textarea */}
                    <textarea
                        ref={textareaRef}
                        value={value}
                        onChange={handleChange}
                        onKeyDown={handleKeyDown}
                        onFocus={() => setIsFocused(true)}
                        onBlur={() => setIsFocused(false)}
                        disabled={disabled}
                        placeholder="Describe what you want to create..."
                        rows={1}
                        className={cn(
                            'w-full resize-none bg-transparent border-none outline-none',
                            'text-lg leading-relaxed placeholder:text-muted-foreground/50',
                            'min-h-[28px] max-h-[200px]',
                            'disabled:cursor-not-allowed'
                        )}
                        style={{
                            fontFamily: 'var(--font-sans)',
                            letterSpacing: '-0.01em'
                        }}
                    />

                    {/* Bottom row: detected type + submit */}
                    <div className="flex items-center justify-between mt-3 pt-3 border-t border-border/40">
                        {/* Detected asset type chip */}
                        <div className="flex items-center gap-2 min-h-[32px]">
                            {detectedConfig ? (
                                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-foreground/5 border border-border/40">
                                    <Sparkles className="h-3.5 w-3.5 text-muted-foreground" />
                                    <span className="text-xs font-medium text-foreground/80">
                                        {detectedConfig.label}
                                    </span>
                                </div>
                            ) : (
                                <span className="text-xs text-muted-foreground/60 pl-1">
                                    Start typing to detect asset type...
                                </span>
                            )}
                        </div>

                        {/* Submit button */}
                        <button
                            onClick={handleSubmit}
                            disabled={!value.trim() || disabled}
                            className={cn(
                                'flex items-center justify-center h-9 w-9 rounded-xl',
                                'bg-foreground text-background',
                                'transition-all duration-200',
                                'hover:scale-105 active:scale-95',
                                'disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:scale-100'
                            )}
                        >
                            <Send className="h-4 w-4" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Hint text */}
            <p className="text-center text-xs text-muted-foreground/60 mt-4">
                Press <kbd className="px-1.5 py-0.5 rounded bg-muted font-mono text-[10px]">Enter</kbd> to create • <kbd className="px-1.5 py-0.5 rounded bg-muted font-mono text-[10px]">Shift + Enter</kbd> for new line
            </p>
        </div>
    );
}
