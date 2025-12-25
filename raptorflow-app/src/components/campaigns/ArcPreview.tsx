"use client";

import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Move, CHANNEL_LABELS } from '@/lib/campaigns-types';
import { cn } from '@/lib/utils';
import { Calendar, CheckCircle2, Clock, Target } from 'lucide-react';

interface ArcPreviewProps {
    moves: Move[];
    duration: number;
    objective: string;
}

export function ArcPreview({ moves, duration, objective }: ArcPreviewProps) {
    return (
        <div className="h-full flex flex-col space-y-6 animate-in fade-in slide-in-from-right-4 duration-700">
            <div className="space-y-1">
                <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-stone-400">90-Day Strategic Arc</h3>
                <p className="text-sm font-serif text-stone-600">Iterative momentum for {objective}</p>
            </div>

            <div className="flex-1 space-y-4 overflow-y-auto pr-2 custom-scrollbar">
                {moves.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center border-2 border-dashed border-stone-100 rounded-2xl p-8 text-center space-y-3">
                        <div className="w-12 h-12 rounded-full bg-stone-50 flex items-center justify-center">
                            <Clock className="w-6 h-6 text-stone-200" />
                        </div>
                        <p className="text-xs text-stone-400 font-sans max-w-[180px]">
                            Complete the steps to see your AI-generated 90-day arc.
                        </p>
                    </div>
                ) : (
                    moves.map((move, i) => (
                        <div key={move.id} className="relative pl-8 group">
                            {/* Timeline Line */}
                            {i < moves.length - 1 && (
                                <div className="absolute left-[11px] top-6 bottom-[-16px] w-[2px] bg-stone-100 group-hover:bg-stone-200 transition-colors" />
                            )}

                            {/* Timeline Node */}
                            <div className={cn(
                                "absolute left-0 top-1 w-6 h-6 rounded-full border-2 bg-white flex items-center justify-center transition-all duration-500",
                                i === 0 ? "border-stone-800 ring-4 ring-stone-50" : "border-stone-200"
                            )}>
                                {i === 0 ? <Target className="w-3 h-3 text-stone-800" /> : <span className="text-[10px] font-bold text-stone-300">{i + 1}</span>}
                            </div>

                            <Card className="rounded-xl border-stone-200 bg-white/50 hover:bg-white hover:shadow-md transition-all duration-300 overflow-hidden">
                                <CardContent className="p-4 space-y-3">
                                    <div className="flex justify-between items-start">
                                        <h4 className="text-sm font-bold text-stone-800">{move.name}</h4>
                                        <span className="text-[10px] font-mono text-stone-400 bg-stone-50 px-1.5 py-0.5 rounded border border-stone-100">
                                            {CHANNEL_LABELS[move.channel]}
                                        </span>
                                    </div>

                                    <div className="flex items-center space-x-4 text-[10px] text-stone-500 uppercase tracking-wider font-semibold">
                                        <div className="flex items-center">
                                            <Calendar className="w-3 h-3 mr-1 text-stone-300" />
                                            {move.duration} Days
                                        </div>
                                        <div className="flex items-center">
                                            <Clock className="w-3 h-3 mr-1 text-stone-300" />
                                            {move.dailyEffort}m/Day
                                        </div>
                                    </div>

                                    {i === 0 && (
                                        <div className="pt-2 border-t border-stone-100">
                                            <div className="flex items-start space-x-2">
                                                <CheckCircle2 className="w-3 h-3 text-stone-400 mt-0.5" />
                                                <p className="text-[11px] text-stone-500 leading-relaxed italic">
                                                    {move.hypothesis}
                                                </p>
                                            </div>
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        </div>
                    ))
                )}
            </div>

            {moves.length > 0 && (
                <div className="pt-4 border-t border-stone-100 flex items-center justify-between">
                    <span className="text-[10px] font-bold text-stone-400 uppercase tracking-widest">Confidence Score</span>
                    <div className="flex items-center space-x-2">
                        <div className="w-24 h-1.5 bg-stone-100 rounded-full overflow-hidden">
                            <div className="h-full bg-stone-800 w-[85%]" />
                        </div>
                        <span className="text-[10px] font-mono text-stone-800 font-bold">85%</span>
                    </div>
                </div>
            )}
        </div>
    );
}
