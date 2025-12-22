'use client';

import React from 'react';
import { Signal, MOCK_ANGLES } from '../types';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { Zap, ExternalLink, Bookmark, Share2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useRouter } from 'next/navigation';

interface SignalDrawerProps {
    signal: Signal | null;
    open: boolean;
    onClose: () => void;
}

export function SignalDrawer({ signal, open, onClose }: SignalDrawerProps) {
    const router = useRouter();

    if (!signal) return null;

    const handleDraft = (anglePrompt: string) => {
        const context = `Context:\nSignal: ${signal.title}\nWhy it matters: ${signal.whyItMatters}\nSource: ${signal.source.name}`;
        const fullPrompt = `${anglePrompt}\n\n${context}`;
        router.push(`/muse?prompt=${encodeURIComponent(fullPrompt)}`);
    };

    return (
        <Sheet open={open} onOpenChange={onClose}>
            <SheetContent className="w-[400px] sm:w-[540px] sm:max-w-xl overflow-y-auto">
                <SheetHeader className="mb-8">
                    <div className="flex items-center gap-2 text-muted-foreground text-sm font-medium uppercase tracking-wide mb-2">
                        <span className={cn(
                            "h-2 w-2 rounded-full",
                            signal.confidence === 'high' ? "bg-emerald-500" :
                                signal.confidence === 'medium' ? "bg-amber-500" : "bg-zinc-300"
                        )} />
                        {signal.source.name}
                    </div>
                    <SheetTitle className="font-display text-2xl font-semibold leading-tight">
                        {signal.title}
                    </SheetTitle>
                    <SheetDescription className="text-base mt-2">
                        {signal.timestamp.toLocaleString()}
                    </SheetDescription>
                </SheetHeader>

                <div className="space-y-8">
                    {/* Why it matters section - Expanded */}
                    <div className="p-5 bg-secondary/30 rounded-xl border border-border/50">
                        <h4 className="text-sm font-semibold text-foreground mb-2 flex items-center gap-2">
                            <Zap className="h-4 w-4 text-primary" />
                            Why your ICP cares
                        </h4>
                        <p className="text-sm text-foreground/80 leading-relaxed">
                            {signal.whyItMatters}
                            <br /><br />
                            This signals a shift in market dynamics that directly affects their bottom line. Ignoring this would be a strategic blindspot.
                        </p>
                    </div>

                    {/* Angles Grid */}
                    <div>
                        <h4 className="text-sm font-medium text-muted-foreground mb-4 uppercase tracking-wider">
                            Angles & Takes
                        </h4>
                        <div className="grid grid-cols-2 gap-3">
                            {signal.angles.filter(Boolean).map((angle) => (
                                <button
                                    key={angle.id}
                                    onClick={() => handleDraft(angle.prompt)}
                                    className="flex flex-col items-start p-3 rounded-xl border border-border/60 hover:border-foreground/20 hover:bg-secondary/30 transition-all text-left"
                                >
                                    <span className="text-xs font-semibold text-primary mb-1">{angle.label}</span>
                                    <span className="text-xs text-muted-foreground line-clamp-2">
                                        {angle.prompt}
                                    </span>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Source */}
                    <div className="border-t border-border/40 pt-6">
                        <h4 className="text-sm font-medium text-muted-foreground mb-3 uppercase tracking-wider">
                            Source Context
                        </h4>
                        <div className="flex items-center justify-between p-3 rounded-lg border border-border/40 bg-card">
                            <div className="flex flex-col">
                                <span className="text-sm font-medium">{signal.source.name}</span>
                                <span className="text-xs text-muted-foreground">{signal.source.type}</span>
                            </div>
                            <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                                <ExternalLink className="h-4 w-4 text-muted-foreground" />
                            </Button>
                        </div>
                    </div>

                    {/* Footer Actions */}
                    <div className="flex gap-3 pt-4">
                        <Button className="flex-1" onClick={() => handleDraft(signal.angles[0]?.prompt)}>
                            Draft in Muse
                        </Button>
                        <Button variant="outline" size="icon">
                            <Bookmark className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="icon">
                            <Share2 className="h-4 w-4" />
                        </Button>
                    </div>
                </div>
            </SheetContent>
        </Sheet>
    );
}
