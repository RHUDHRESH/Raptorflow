import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';

/**
 * PositioningMap Component
 * 
 * The "Seth Godin" 2D Graph.
 * Displays a 2-axis grid where the user is positioned relative to the market.
 * 
 * Props:
 * - axes: { x: { min: string, max: string }, y: { min: string, max: string } }
 * - userPosition: { x: number, y: number } (0-100 scale)
 * - competitors: Array of { id, name, x, y, type }
 * - quadrants: Array of 4 strings [TL, TR, BL, BR] labels
 * - interactive: boolean (allow dragging/clicking)
 * - onPositionChange: (newPos) => void
 */
const PositioningMap = ({
    axes = {
        x: { min: 'Generic', max: 'Specialist' },
        y: { min: 'DIY', max: 'Done-for-You' }
    },
    userPosition = { x: 50, y: 50 },
    competitors = [],
    quadrants = ['Commodity', 'Premium Partner', 'DIY Platform', 'White-glove Shop'],
    interactive = true,
    onPositionChange,
    className
}) => {
    const [localPos, setLocalPos] = useState(userPosition);

    useEffect(() => {
        setLocalPos(userPosition);
    }, [userPosition.x, userPosition.y]);

    const handleInteraction = (e, info) => {
        if (!interactive || !onPositionChange) return;

        // Calculate position based on click or drag
        // This is a simplified handler - in a real drag implementation we'd use the container bounds
        // For now, we'll rely on the parent passing updated positions via sliders for precision,
        // but visually this component renders the state.
    };

    return (
        <div className={cn("relative w-full aspect-square bg-neutral-50 rounded-xl border border-neutral-200 overflow-hidden", className)}>
            {/* Grid Lines */}
            <div className="absolute inset-0 grid grid-cols-2 grid-rows-2">
                <div className="border-r border-b border-neutral-200/50 p-4 flex items-start justify-start">
                    <span className="text-xs font-mono text-neutral-400 uppercase tracking-wider opacity-50">{quadrants[0]}</span>
                </div>
                <div className="border-b border-neutral-200/50 p-4 flex items-start justify-end">
                    <span className="text-xs font-mono text-neutral-400 uppercase tracking-wider opacity-50">{quadrants[1]}</span>
                </div>
                <div className="border-r border-neutral-200/50 p-4 flex items-end justify-start">
                    <span className="text-xs font-mono text-neutral-400 uppercase tracking-wider opacity-50">{quadrants[2]}</span>
                </div>
                <div className="p-4 flex items-end justify-end">
                    <span className="text-xs font-mono text-neutral-400 uppercase tracking-wider opacity-50">{quadrants[3]}</span>
                </div>
            </div>

            {/* Center Axes */}
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="w-full h-px bg-neutral-300"></div>
                <div className="h-full w-px bg-neutral-300 absolute"></div>
            </div>

            {/* Axis Labels */}
            <div className="absolute inset-x-0 bottom-2 text-center pointer-events-none">
                <span className="text-[10px] font-bold uppercase tracking-widest text-neutral-500 bg-neutral-50 px-2">
                    {axes.x.min} ↔ {axes.x.max}
                </span>
            </div>
            <div className="absolute inset-y-0 left-2 flex items-center pointer-events-none">
                <span className="text-[10px] font-bold uppercase tracking-widest text-neutral-500 bg-neutral-50 px-2 -rotate-90 whitespace-nowrap">
                    {axes.y.min} ↔ {axes.y.max}
                </span>
            </div>

            {/* Competitors */}
            {competitors.map((comp) => (
                <motion.div
                    key={comp.id}
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: 0.2 + Math.random() * 0.5 }}
                    className="absolute w-3 h-3 rounded-full bg-neutral-300 border border-neutral-400 shadow-sm z-10"
                    style={{
                        left: `${comp.x}%`,
                        top: `${100 - comp.y}%`, // Invert Y for standard graph behavior (0 at bottom)
                        x: '-50%',
                        y: '-50%'
                    }}
                >
                    <div className="absolute -top-6 left-1/2 -translate-x-1/2 whitespace-nowrap bg-white/80 backdrop-blur px-1.5 py-0.5 rounded text-[9px] font-medium text-neutral-500 opacity-0 hover:opacity-100 transition-opacity pointer-events-auto cursor-help">
                        {comp.name}
                    </div>
                </motion.div>
            ))}

            {/* User Dot (The "You" Star) */}
            <motion.div
                className="absolute z-20 cursor-grab active:cursor-grabbing"
                animate={{
                    left: `${localPos.x}%`,
                    top: `${100 - localPos.y}%`
                }}
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                style={{ x: '-50%', y: '-50%' }}
            >
                <div className="relative">
                    <div className="w-6 h-6 rounded-full bg-neutral-900 border-2 border-white shadow-lg flex items-center justify-center">
                        <div className="w-2 h-2 rounded-full bg-white" />
                    </div>
                    {/* Pulse Effect */}
                    <div className="absolute inset-0 rounded-full bg-neutral-900/30 animate-ping" />

                    {/* Label */}
                    <div className="absolute top-8 left-1/2 -translate-x-1/2 whitespace-nowrap bg-neutral-900 text-white px-2 py-1 rounded text-[10px] font-bold tracking-wide shadow-xl">
                        YOU
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default PositioningMap;
