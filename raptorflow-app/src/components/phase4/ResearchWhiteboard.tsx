'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Playfair_Display } from 'next/font/google';
import { Plus, X, AlertTriangle, MessageSquare, Quote, Move } from 'lucide-react';
import { cn } from '@/lib/utils';

const playfair = Playfair_Display({ subsets: ['latin'] });

interface PainPoint {
    id: string;
    text: string;
    category: 'functional' | 'emotional' | 'social';
    severity: number; // 1-5
}

interface ResearchWhiteboardProps {
    pains: PainPoint[];
    onChange: (pains: PainPoint[]) => void;
}

export function ResearchWhiteboard({ pains, onChange }: ResearchWhiteboardProps) {
    const [isAdding, setIsAdding] = useState(false);
    const [newPain, setNewPain] = useState({ text: '', category: 'functional' as const });

    const addPain = () => {
        if (newPain.text.trim()) {
            const pain: PainPoint = {
                id: Math.random().toString(36).substr(2, 9),
                text: newPain.text.trim(),
                category: newPain.category,
                severity: 3
            };
            onChange([...pains, pain]);
            setNewPain({ text: '', category: 'functional' });
            setIsAdding(false);
        }
    };

    const removePain = (id: string) => {
        onChange(pains.filter(p => p.id !== id));
    };

    const categories = [
        { id: 'functional', label: 'Functional Pains', icon: <Move className="w-4 h-4" /> },
        { id: 'emotional', label: 'Emotional Pains', icon: <AlertTriangle className="w-4 h-4" /> },
        { id: 'social', label: 'Social Pains', icon: <MessageSquare className="w-4 h-4" /> },
    ];

    return (
        <div className="space-y-12">
            {/* Header / Add Trigger */}
            <div className="flex justify-between items-end border-b border-[#C0C1BE] pb-6">
                <div className="space-y-1">
                    <h3 className="text-xs font-semibold uppercase tracking-widest text-[#2D3538] opacity-60">
                        Pain point Aggregator
                    </h3>
                    <p className="text-sm text-[#5B5F61]">
                        Aggregate the raw frustrations gathered from customer research.
                    </p>
                </div>
                <button
                    onClick={() => setIsAdding(true)}
                    className="text-[10px] font-mono uppercase tracking-widest flex items-center gap-2 bg-[#2D3538] text-white px-4 py-2 rounded-lg hover:bg-[#1A1D1E] transition-all"
                >
                    <Plus className="w-3 h-3" /> Add Research Note
                </button>
            </div>

            {/* Modal for adding pain */}
            <AnimatePresence>
                {isAdding && (
                    <motion.div 
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-[#0E1112]/40 backdrop-blur-sm z-[100] flex items-center justify-center p-8"
                    >
                        <motion.div 
                            initial={{ scale: 0.95, y: 20 }}
                            animate={{ scale: 1, y: 0 }}
                            className="bg-white rounded-2xl p-8 max-w-lg w-full shadow-2xl border border-[#C0C1BE]"
                        >
                            <div className="flex justify-between items-center mb-8">
                                <h4 className={`${playfair.className} text-2xl`}>Add Research Note</h4>
                                <button onClick={() => setIsAdding(false)} className="opacity-40 hover:opacity-100 transition-opacity">
                                    <X className="w-5 h-5" />
                                </button>
                            </div>

                            <div className="space-y-6">
                                <div className="space-y-2">
                                    <label className="text-[10px] font-mono uppercase tracking-widest opacity-40">Category</label>
                                    <div className="flex gap-2">
                                        {categories.map(c => (
                                            <button
                                                key={c.id}
                                                onClick={() => setNewPain({ ...newPain, category: c.id as any })}
                                                className={cn(
                                                    "px-4 py-2 rounded-lg text-xs font-medium transition-all border",
                                                    newPain.category === c.id 
                                                        ? "bg-[#2D3538] text-white border-[#2D3538]" 
                                                        : "bg-[#F3F4EE] border-[#C0C1BE] text-[#5B5F61] hover:border-[#2D3538]"
                                                )}
                                            >
                                                {c.label.split(' ')[0]}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <label className="text-[10px] font-mono uppercase tracking-widest opacity-40">Observation</label>
                                    <textarea
                                        autoFocus
                                        value={newPain.text}
                                        onChange={(e) => setNewPain({ ...newPain, text: e.target.value })}
                                        placeholder="Paste a customer quote or describe a specific frustration..."
                                        className="w-full min-h-[120px] p-4 rounded-xl border border-[#C0C1BE] bg-[#F3F4EE]/30 focus:bg-white outline-none transition-all text-sm resize-none"
                                    />
                                </div>

                                <button
                                    onClick={addPain}
                                    className="w-full bg-[#2D3538] text-white py-4 rounded-xl font-medium hover:bg-[#1A1D1E] transition-all"
                                >
                                    Add to Board
                                </button>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Board Layout */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {categories.map(cat => (
                    <div key={cat.id} className="space-y-6">
                        <div className="flex items-center gap-2 opacity-40 border-b border-[#C0C1BE] pb-3">
                            {cat.icon}
                            <span className="text-[10px] font-mono uppercase tracking-widest font-bold">
                                {cat.label}
                            </span>
                        </div>
                        
                        <div className="space-y-4">
                            <AnimatePresence mode="popLayout">
                                {pains.filter(p => p.category === cat.id).map(pain => (
                                    <motion.div
                                        key={pain.id}
                                        layout
                                        initial={{ opacity: 0, x: -10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        exit={{ opacity: 0, scale: 0.95 }}
                                        className="p-5 bg-[#F3F4EE]/50 border border-[#C0C1BE] rounded-xl relative group hover:bg-white hover:border-[#2D3538] transition-all cursor-default"
                                    >
                                        <button
                                            onClick={() => removePain(pain.id)}
                                            className="absolute -top-2 -right-2 w-6 h-6 bg-white border border-[#C0C1BE] rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 hover:border-red-200 hover:text-red-500 transition-all shadow-sm"
                                        >
                                            <X className="w-3 h-3" />
                                        </button>
                                        <div className="flex gap-3">
                                            <Quote className="w-4 h-4 text-[#2D3538] opacity-20 flex-shrink-0" />
                                            <p className="text-sm text-[#2D3538] leading-relaxed">
                                                {pain.text}
                                            </p>
                                        </div>
                                    </motion.div>
                                ))}
                            </AnimatePresence>
                            
                            {pains.filter(p => p.category === cat.id).length === 0 && (
                                <div className="py-12 text-center border-2 border-dashed border-[#C0C1BE] rounded-xl opacity-20 flex flex-col items-center gap-2">
                                    <Plus className="w-4 h-4" />
                                    <span className="text-[10px] font-mono uppercase tracking-tighter">Empty</span>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
