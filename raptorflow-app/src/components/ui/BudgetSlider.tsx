import React, { useState, useEffect, useRef } from 'react';
import { motion, useMotionValue, useTransform } from 'framer-motion';

interface BudgetSliderProps {
    value: string; // e.g., "$1k - $5k"
    onChange: (value: string) => void;
    ranges: string[]; // ["<$1k", "$1k-$5k", "$5k-$10k", "$10k+"]
}

export const BudgetSlider: React.FC<BudgetSliderProps> = ({ value, onChange, ranges }) => {
    // Find index of current value
    const initialIndex = ranges.indexOf(value) !== -1 ? ranges.indexOf(value) : 0;
    const [currentIndex, setCurrentIndex] = useState(initialIndex);
    const containerRef = useRef<HTMLDivElement>(null);
    const [width, setWidth] = useState(0);

    useEffect(() => {
        if (containerRef.current) {
            setWidth(containerRef.current.offsetWidth);
        }
    }, []);

    // Snap to index on change
    useEffect(() => {
        const idx = ranges.indexOf(value);
        if (idx !== -1) setCurrentIndex(idx);
    }, [value, ranges]);

    const handleClick = (index: number) => {
        setCurrentIndex(index);
        onChange(ranges[index]);
    };

    return (
        <div className="w-full py-8 px-4 select-none" ref={containerRef}>
            <div className="relative h-2 bg-[#E5E7E1] rounded-full">
                {/* Active Track */}
                <motion.div
                    className="absolute top-0 left-0 h-full bg-[#2D3538] rounded-full"
                    initial={false}
                    animate={{ width: `${(currentIndex / (ranges.length - 1)) * 100}%` }}
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                />

                {/* Knobs */}
                {ranges.map((range, index) => {
                    const position = (index / (ranges.length - 1)) * 100;
                    const isActive = index === currentIndex;
                    const isPassed = index <= currentIndex;

                    return (
                        <div
                            key={range}
                            className="absolute top-1/2 -translate-y-1/2 cursor-pointer group"
                            style={{ left: `${position}%` }}
                            onClick={() => handleClick(index)}
                        >
                            {/* Knob Circle */}
                            <motion.div
                                className={`w-4 h-4 rounded-full border-2 transition-colors duration-300 z-10 relative
                                    ${isActive
                                        ? 'bg-[#2D3538] border-[#2D3538] scale-125'
                                        : isPassed
                                            ? 'bg-[#2D3538] border-[#2D3538]'
                                            : 'bg-[#F3F4EE] border-[#C0C1BE]'
                                    }`}
                                whileHover={{ scale: 1.5 }}
                                whileTap={{ scale: 1.1 }}
                            />

                            {/* Label */}
                            <div
                                className={`absolute top-6 left-1/2 -translate-x-1/2 text-xs font-medium whitespace-nowrap transition-colors duration-300
                                    ${isActive ? 'text-[#2D3538] font-bold scale-110' : 'text-[#9D9F9F]'}`}
                            >
                                {range}
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Value Display */}
            <div className="mt-8 text-center">
                <span className="text-sm text-[#5B5F61]">Estimated Monthly Budget:</span>
                <div className="text-2xl font-serif text-[#2D3538] mt-1">
                    {ranges[currentIndex]}
                </div>
            </div>
        </div>
    );
};
