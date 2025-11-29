import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, ArrowLeft, Target, Layers, Zap, Check } from 'lucide-react';
import { LuxeHeading, LuxeCard, LuxeButton, LuxeBadge } from '../ui/PremiumUI';
import PositioningMap from './PositioningMap';

const Act2Battlefield = ({ positioning, onComplete }) => {
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
            className="w-full max-w-7xl mx-auto"
        >
            <div className="text-center mb-12">
                <LuxeBadge variant="outline" className="mb-4">Act II</LuxeBadge>
                <LuxeHeading level={2}>The Battlefield</LuxeHeading>
                <p className="text-neutral-500 mt-2">Choose your vector of attack.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
                {/* Left: Map & Clusters */}
                <div className="lg:col-span-7 space-y-8">
                    <LuxeCard className="p-6 h-[500px] flex flex-col relative overflow-hidden">
                        <div className="absolute top-4 left-4 z-10">
                            <h3 className="font-serif text-lg font-bold">Market Landscape</h3>
                        </div>
                        <div className="flex-1 relative rounded-lg border border-neutral-100 bg-neutral-50 overflow-hidden mt-8">
                            <PositioningMap
                                initialX={positioning?.analysis?.coordinates?.x || 65}
                                initialY={positioning?.analysis?.coordinates?.y || 40}
                                readOnly={true}
                                showClusters={true} // Assuming PositioningMap handles this prop now or ignores it safely
                                activeClusters={selectedClusters}
                            />
                        </div>
                    </LuxeCard>

                    <div className="flex items-center gap-4">
                        <span className="text-xs font-bold text-neutral-400 uppercase tracking-widest">Market Clusters:</span>
                        <div className="flex flex-wrap gap-2">
                            {clusters.map(cluster => (
                                <button
                                    key={cluster.id}
                                    onClick={() => toggleCluster(cluster.id)}
                                    className={`px-4 py-2 rounded-full text-xs font-semibold uppercase tracking-wider transition-all border ${selectedClusters.includes(cluster.id)
                                            ? 'bg-neutral-900 text-white border-neutral-900'
                                            : 'bg-white text-neutral-500 border-neutral-200 hover:border-neutral-400'
                                        }`}
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
                                    className={`relative p-6 rounded-xl border-2 cursor-pointer transition-all duration-300 group ${isSelected
                                            ? 'border-neutral-900 bg-neutral-50'
                                            : 'border-neutral-100 bg-white hover:border-neutral-300'
                                        }`}
                                >
                                    <div className="flex items-start gap-4">
                                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center transition-colors ${isSelected ? 'bg-neutral-900 text-white' : 'bg-neutral-100 text-neutral-400 group-hover:bg-neutral-200'
                                            }`}>
                                            <Icon className="w-5 h-5" />
                                        </div>
                                        <div className="flex-1">
                                            <h3 className={`font-serif text-lg font-bold mb-1 transition-colors ${isSelected ? 'text-neutral-900' : 'text-neutral-700'
                                                }`}>
                                                {strategy.title}
                                            </h3>
                                            <p className="text-sm text-neutral-500 leading-relaxed">
                                                {strategy.description}
                                            </p>
                                        </div>
                                        {isSelected && (
                                            <div className="absolute top-6 right-6">
                                                <div className="w-6 h-6 bg-neutral-900 rounded-full flex items-center justify-center">
                                                    <Check className="w-3 h-3 text-white" />
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    <div className="pt-8 flex justify-end">
                        <LuxeButton
                            onClick={handleComplete}
                            disabled={!selectedStrategy}
                            size="lg"
                            className="w-full md:w-auto"
                        >
                            Confirm Strategy <ArrowRight className="ml-2 w-4 h-4" />
                        </LuxeButton>
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

export default Act2Battlefield;
