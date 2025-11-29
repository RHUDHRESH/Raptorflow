import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, ArrowLeft, Target, Layers, Zap, Check } from 'lucide-react';
import { LuxeHeading, LuxeCard, LuxeButton, LuxeBadge } from '../ui/PremiumUI';
import PositioningMap from './PositioningMap';

const Act2Battlefield = ({ positioning, onComplete, onBack }) => {
    const [selectedStrategy, setSelectedStrategy] = useState(null);
    const [selectedClusters, setSelectedClusters] = useState(['your-white-space']);

    const strategies = [
        {
            id: 'specialization',
            title: 'Deepen Specialization',
            description: 'Focus relentlessly on a specific niche or use case to dominate a smaller market.',
            icon: Target
        },
        {
            id: 'service',
            title: 'Add Service Layer',
            description: 'Combine your software with expert services to deliver outcomes, not just tools.',
            icon: Layers
        },
        {
            id: 'efficiency',
            title: 'Scale Efficiency',
            description: 'Broaden appeal with lower friction, self-serve models, and aggressive pricing.',
            icon: Zap
        }
    ];

    const clusters = [
        { id: 'generic', label: 'Generic Tools (Overcrowded)' },
        { id: 'legacy', label: 'Enterprise Legacy' },
        { id: 'your-white-space', label: 'Your White Space' }
    ];

    const toggleCluster = (id) => {
        setSelectedClusters(prev =>
            prev.includes(id) ? prev.filter(c => c !== id) : [...prev, id]
        );
    };

    const handleComplete = () => {
        if (selectedStrategy) {
            onComplete({
                strategy: selectedStrategy,
                clusters: selectedClusters
            });
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="w-full py-12"
        >
            <div className="max-w-[1200px] mx-auto">
                {/* Header */}
                <div className="text-center mb-12">
                    <LuxeBadge variant="outline" className="mb-4">Act II</LuxeBadge>
                    <h1 className="font-display text-4xl lg:text-5xl mb-3" style={{ fontFamily: 'var(--font-display)', color: 'var(--ink-strong)' }}>
                        The Battlefield
                    </h1>
                    <p className="text-lg" style={{ color: 'var(--ink-soft)' }}>
                        Choose your vector of attack.
                    </p>
                </div>

                {/* Two-column layout */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
                    {/* Left: Quadrant + Clusters */}
                    <div className="lg:col-span-7 space-y-6">
                        {/* Quadrant */}
                        <LuxeCard className="p-8">
                            <h3 className="font-semibold text-lg mb-6" style={{ color: 'var(--ink-strong)' }}>
                                Market Landscape
                            </h3>
                            <div className="aspect-square relative rounded-lg bg-neutral-50 overflow-visible p-8" style={{ border: '1px solid var(--border-subtle)' }}>
                                <PositioningMap
                                    initialX={positioning?.analysis?.coordinates?.x || 65}
                                    initialY={positioning?.analysis?.coordinates?.y || 40}
                                    readOnly={true}
                                    showClusters={true}
                                    activeClusters={selectedClusters}
                                />
                            </div>
                            <p className="text-xs mt-4 text-center" style={{ color: 'var(--ink-soft)' }}>
                                Your position relative to the competitive landscape.
                            </p>
                        </LuxeCard>

                        {/* Market Clusters */}
                        <div className="flex items-center gap-4 flex-wrap">
                            <span className="text-xs font-bold uppercase tracking-widest" style={{ color: 'var(--ink-soft)' }}>
                                Market Clusters:
                            </span>
                            <div className="flex flex-wrap gap-2">
                                {clusters.map(cluster => (
                                    <button
                                        key={cluster.id}
                                        onClick={() => toggleCluster(cluster.id)}
                                        className="px-4 py-2 rounded-full text-xs font-semibold uppercase tracking-wider transition-all"
                                        style={{
                                            border: '1px solid var(--border-subtle)',
                                            backgroundColor: selectedClusters.includes(cluster.id) ? 'var(--ink-strong)' : 'white',
                                            color: selectedClusters.includes(cluster.id) ? 'white' : 'var(--ink-soft)'
                                        }}
                                    >
                                        {cluster.label}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Right: Strategy Selection */}
                    <div className="lg:col-span-5 space-y-6">
                        <div className="space-y-4">
                            {strategies.map((strategy) => {
                                const Icon = strategy.icon;
                                const isSelected = selectedStrategy === strategy.id;

                                return (
                                    <div
                                        key={strategy.id}
                                        onClick={() => setSelectedStrategy(strategy.id)}
                                        className="relative p-6 rounded-xl cursor-pointer transition-all duration-300 group"
                                        style={{
                                            border: isSelected ? '2px solid var(--ink-strong)' : '1px solid var(--border-subtle)',
                                            backgroundColor: isSelected ? '#FAFAFA' : 'white'
                                        }}
                                    >
                                        <div className="flex items-start gap-4">
                                            <div
                                                className="w-10 h-10 rounded-lg flex items-center justify-center transition-colors"
                                                style={{
                                                    backgroundColor: isSelected ? 'var(--ink-strong)' : '#F5F5F5',
                                                    color: isSelected ? 'white' : 'var(--ink-soft)'
                                                }}
                                            >
                                                <Icon className="w-5 h-5" />
                                            </div>
                                            <div className="flex-1">
                                                <h3
                                                    className="font-display text-lg font-medium mb-1 transition-colors"
                                                    style={{
                                                        fontFamily: 'var(--font-display)',
                                                        color: 'var(--ink-strong)'
                                                    }}
                                                >
                                                    {strategy.title}
                                                </h3>
                                                <p className="text-sm leading-relaxed" style={{ color: 'var(--ink-soft)' }}>
                                                    {strategy.description}
                                                </p>
                                            </div>
                                            {isSelected && (
                                                <div className="absolute top-6 right-6">
                                                    <div className="w-6 h-6 rounded-full flex items-center justify-center" style={{ backgroundColor: 'var(--ink-strong)' }}>
                                                        <Check className="w-3 h-3 text-white" />
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>

                        {/* Controls */}
                        <div className="flex justify-between items-center pt-4">
                            <LuxeButton variant="ghost" onClick={onBack}>
                                <ArrowLeft className="mr-2 w-4 h-4" /> Back
                            </LuxeButton>
                            <LuxeButton
                                onClick={handleComplete}
                                disabled={!selectedStrategy}
                                size="lg"
                            >
                                Confirm Strategy <ArrowRight className="ml-2 w-4 h-4" />
                            </LuxeButton>
                        </div>
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

export default Act2Battlefield;
