'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Sparkles, AlertCircle, CheckCircle2, Search } from 'lucide-react';

interface VoiceAnalysisResults {
    score: number;
    feedback: string[];
    alignment: 'low' | 'medium' | 'high';
}

interface VoiceAnalyzerProps {
    className?: string;
    onAnalysisComplete?: (results: VoiceAnalysisResults) => void;
}

export function VoiceAnalyzer({ className, onAnalysisComplete }: VoiceAnalyzerProps) {
    const [text, setText] = useState('');
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [results, setResults] = useState<VoiceAnalysisResults | null>(null);

    const handleRunAnalysis = async () => {
        if (!text.trim()) return;

        setIsAnalyzing(true);
        // Simulate AI analysis delay
        await new Promise(resolve => setTimeout(resolve, 2000));

        const mockResults: VoiceAnalysisResults = {
            score: 82,
            alignment: 'high',
            feedback: [
                "Strong use of 'Calm & Premium' vocabulary.",
                "Sentence structure is well-balanced.",
                "Consider removing the last exclamation mark to maintain 'Quiet Luxury' tone."
            ]
        };

        setResults(mockResults);
        setIsAnalyzing(false);
        onAnalysisComplete?.(mockResults);
    };

    return (
        <div className={cn(
            "p-8 rounded-[24px] bg-card border border-border flex flex-col transition-all duration-300",
            className
        )}>
            <div className="flex items-center gap-3 mb-8">
                <div className="h-8 w-8 rounded-lg bg-primary/5 flex items-center justify-center">
                    <Sparkles className="h-4 w-4 text-primary/60" />
                </div>
                <h3 className="text-[11px] font-semibold uppercase tracking-[0.2em] text-muted-foreground/80 font-sans">
                    Voice Alignment Analyzer
                </h3>
            </div>

            <div className="space-y-6">
                <div>
                    <label className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider mb-2 block">
                        Sample Text
                    </label>
                    <Textarea
                        placeholder="Paste sample copy here (e.g. LinkedIn post, Email draft)..."
                        className="min-h-[120px] bg-background/50 border-border/50 focus:border-primary/30 transition-all rounded-xl resize-none text-sm leading-relaxed"
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                    />
                </div>

                <Button
                    variant="outline"
                    className="w-full h-12 rounded-xl border-primary/10 hover:bg-primary/5 text-[11px] font-semibold uppercase tracking-widest transition-all"
                    onClick={handleRunAnalysis}
                    disabled={isAnalyzing || !text.trim()}
                >
                    {isAnalyzing ? (
                        <span className="flex items-center gap-2">
                            <Search className="h-3 w-3 animate-pulse" />
                            Analyzing Tone...
                        </span>
                    ) : (
                        "Run Voice Audit"
                    )}
                </Button>

                <AnimatePresence>
                    {results && !isAnalyzing && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="overflow-hidden pt-4"
                        >
                            <div className="p-6 rounded-2xl bg-muted/30 border border-border/50">
                                <div className="flex items-end justify-between mb-6">
                                    <div>
                                        <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground block mb-1">
                                            Alignment Score
                                        </span>
                                        <div className="flex items-baseline gap-2">
                                            <span className="text-3xl font-display font-medium text-foreground">
                                                {results.score}%
                                            </span>
                                            <span className={cn(
                                                "text-[10px] font-bold uppercase tracking-tighter px-2 py-0.5 rounded-full",
                                                results.alignment === 'high' ? "bg-green-100/50 text-green-700" : "bg-amber-100/50 text-amber-700"
                                            )}>
                                                {results.alignment} Match
                                            </span>
                                        </div>
                                    </div>
                                    <div className="h-12 w-12 rounded-full border-4 border-primary/10 flex items-center justify-center relative">
                                        <svg className="h-full w-full -rotate-90">
                                            <circle
                                                cx="24" cy="24" r="20"
                                                fill="transparent"
                                                stroke="currentColor"
                                                strokeWidth="4"
                                                className="text-primary/20"
                                            />
                                            <circle
                                                cx="24" cy="24" r="20"
                                                fill="transparent"
                                                stroke="currentColor"
                                                strokeWidth="4"
                                                strokeDasharray={125.6}
                                                strokeDashoffset={125.6 * (1 - results.score/100)}
                                                className="text-primary"
                                            />
                                        </svg>
                                        <CheckCircle2 className="absolute h-4 w-4 text-primary" />
                                    </div>
                                </div>

                                <div className="space-y-3">
                                    <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground block">
                                        AI Feedback
                                    </span>
                                    {results.feedback.map((item, i) => (
                                        <div key={i} className="flex gap-2 text-xs text-foreground/80 leading-relaxed font-sans">
                                            <div className="mt-1 h-1 w-1 rounded-full bg-primary/40 shrink-0" />
                                            {item}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
}
