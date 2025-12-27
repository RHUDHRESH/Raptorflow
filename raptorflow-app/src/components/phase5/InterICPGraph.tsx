'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
    GitBranch, Users, ArrowRight, Star, Circle,
    Plus, Trash2, Edit2, Check, Info
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ICP, InterICPGraph, ICPGraphNode, ICPGraphEdge, ICPEdgeType } from '@/lib/foundation';

// Updated interface to match wizard usage
interface InterICPGraphProps {
    icps: ICP[];
    graph: InterICPGraph;
    onUpdateGraph: (graph: InterICPGraph) => void;
    onSetTargetSequence: (sequence: string[]) => void;
}

const EDGE_TYPES: Array<{ type: ICPEdgeType; label: string; color: string }> = [
    { type: 'influences', label: 'Influences', color: '#64B5F6' },
    { type: 'refers', label: 'Refers', color: '#81C784' },
    { type: 'upstream', label: 'Upgrade', color: '#FFB74D' },
    { type: 'downstream', label: 'Downgrade', color: '#E57373' }
];

function NodeCard({
    node,
    isWedge,
    isInSequence,
    sequencePosition,
    onSetWedge,
    onToggleSequence
}: {
    node: ICPGraphNode;
    isWedge: boolean;
    isInSequence: boolean;
    sequencePosition?: number;
    onSetWedge: () => void;
    onToggleSequence: () => void;
}) {
    const isICP = node.type === 'icp';

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className={`bg-white border-2 rounded-2xl p-5 ${isWedge ? 'border-[#2D3538] shadow-lg' : 'border-[#E5E6E3]'
                }`}
        >
            <div className="flex items-center gap-4">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${isICP ? 'bg-[#2D3538]' : 'bg-[#9D9F9F]'
                    }`}>
                    {isICP ? (
                        <Users className="w-6 h-6 text-white" />
                    ) : (
                        <GitBranch className="w-6 h-6 text-white" />
                    )}
                </div>

                <div className="flex-1">
                    <div className="flex items-center gap-2">
                        <span className="text-[9px] font-mono uppercase text-[#9D9F9F]">
                            {isICP ? 'ICP' : 'Influencer'}
                        </span>
                        {isWedge && (
                            <span className="text-[9px] font-mono uppercase bg-[#2D3538] text-white px-2 py-0.5 rounded">
                                Primary Wedge
                            </span>
                        )}
                        {isInSequence && sequencePosition !== undefined && (
                            <span className="text-[9px] font-mono bg-[#F3F4EE] px-2 py-0.5 rounded">
                                #{sequencePosition + 1} in sequence
                            </span>
                        )}
                    </div>
                    <h3 className="font-medium text-[#2D3538] mt-1">{node.label}</h3>
                </div>

                <div className="flex gap-2">
                    {isICP && !isWedge && (
                        <button
                            onClick={onSetWedge}
                            className="p-2 hover:bg-[#F3F4EE] rounded-lg transition-colors"
                            title="Set as primary wedge"
                        >
                            <Star className="w-4 h-4 text-[#9D9F9F]" />
                        </button>
                    )}
                    {isICP && (
                        <button
                            onClick={onToggleSequence}
                            className={`p-2 rounded-lg transition-colors ${isInSequence
                                    ? 'bg-[#2D3538] text-white'
                                    : 'hover:bg-[#F3F4EE] text-[#9D9F9F]'
                                }`}
                            title={isInSequence ? 'Remove from sequence' : 'Add to sequence'}
                        >
                            {isInSequence ? <Check className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
                        </button>
                    )}
                </div>
            </div>
        </motion.div>
    );
}

function EdgeItem({
    edge,
    fromNode,
    toNode,
    onRemove
}: {
    edge: ICPGraphEdge;
    fromNode?: ICPGraphNode;
    toNode?: ICPGraphNode;
    onRemove: () => void;
}) {
    const edgeConfig = EDGE_TYPES.find(t => t.type === edge.type) || EDGE_TYPES[0];

    return (
        <div className="flex items-center gap-3 bg-[#FAFAF8] rounded-xl p-3">
            <div className="flex items-center gap-2 flex-1">
                <span className="text-sm text-[#2D3538]">{fromNode?.label || 'Unknown'}</span>
                <ArrowRight className="w-4 h-4 text-[#9D9F9F]" />
                <span className="text-sm text-[#2D3538]">{toNode?.label || 'Unknown'}</span>
            </div>
            <span
                className="text-[10px] font-mono uppercase px-2 py-1 rounded"
                style={{ backgroundColor: edgeConfig.color + '20', color: edgeConfig.color }}
            >
                {edgeConfig.label}
            </span>
            <div className="flex items-center gap-1">
                {[1, 2, 3, 4, 5].map(i => (
                    <div
                        key={i}
                        className={`w-1 h-3 rounded-sm ${i <= edge.weight ? 'bg-[#2D3538]' : 'bg-[#E5E6E3]'
                            }`}
                    />
                ))}
            </div>
            <button
                onClick={onRemove}
                className="p-1 hover:bg-red-50 rounded transition-colors"
            >
                <Trash2 className="w-3 h-3 text-red-400 hover:text-red-600" />
            </button>
        </div>
    );
}

export function InterICPGraph({
    icps,
    graph,
    onUpdateGraph,
    onSetTargetSequence
}: InterICPGraphProps) {
    const [targetSequence, setTargetSequence] = useState<string[]>(graph.targetSequence || []);

    const icpNodes = graph.nodes.filter(n => n.type === 'icp');
    const influencerNodes = graph.nodes.filter(n => n.type === 'influencer');

    const handleSetWedge = (nodeId: string) => {
        onUpdateGraph({ ...graph, primaryWedgeICP: nodeId });
    };

    const handleToggleSequence = (nodeId: string) => {
        let newSequence: string[];
        if (targetSequence.includes(nodeId)) {
            newSequence = targetSequence.filter(id => id !== nodeId);
        } else {
            newSequence = [...targetSequence, nodeId];
        }
        setTargetSequence(newSequence);
        onSetTargetSequence(newSequence);
    };

    const handleRemoveEdge = (edgeId: string) => {
        onUpdateGraph({
            ...graph,
            edges: graph.edges.filter(e => e.id !== edgeId)
        });
    };

    return (
        <div className="space-y-6">
            {/* Header Info */}
            <div className="flex items-start gap-3 p-4 bg-[#F3F4EE] rounded-xl">
                <Info className="w-5 h-5 text-[#2D3538] flex-shrink-0 mt-0.5" />
                <div>
                    <p className="text-sm text-[#5B5F61]">
                        <strong className="text-[#2D3538]">ICP Relationship Graph</strong> — How your ICPs connect.
                        Set your primary wedge and define the targeting sequence.
                    </p>
                </div>
            </div>

            {/* Target Sequence */}
            {targetSequence.length > 0 && (
                <div className="bg-[#2D3538] rounded-2xl p-5">
                    <span className="text-[10px] font-mono uppercase text-white/60 block mb-3">
                        Target Sequence
                    </span>
                    <div className="flex items-center gap-3">
                        {targetSequence.map((id, i) => {
                            const node = graph.nodes.find(n => n.id === id);
                            return (
                                <React.Fragment key={id}>
                                    <div className="bg-white/10 rounded-xl px-4 py-2 flex items-center gap-2">
                                        <span className="text-white font-mono text-sm">#{i + 1}</span>
                                        <span className="text-white text-sm">{node?.label}</span>
                                    </div>
                                    {i < targetSequence.length - 1 && (
                                        <ArrowRight className="w-4 h-4 text-white/40" />
                                    )}
                                </React.Fragment>
                            );
                        })}
                    </div>
                    <p className="text-xs text-white/60 mt-3">
                        Target in this order based on fit score and friction levels.
                    </p>
                </div>
            )}

            {/* ICP Nodes */}
            <div>
                <h3 className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-3">
                    ICPs ({icpNodes.length})
                </h3>
                <div className="space-y-3">
                    {icpNodes.map(node => (
                        <NodeCard
                            key={node.id}
                            node={node}
                            isWedge={graph.primaryWedgeICP === node.id}
                            isInSequence={targetSequence.includes(node.id)}
                            sequencePosition={targetSequence.indexOf(node.id)}
                            onSetWedge={() => handleSetWedge(node.id)}
                            onToggleSequence={() => handleToggleSequence(node.id)}
                        />
                    ))}
                </div>
            </div>

            {/* Influencer Nodes */}
            {influencerNodes.length > 0 && (
                <div>
                    <h3 className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-3">
                        Influencers ({influencerNodes.length})
                    </h3>
                    <div className="space-y-3">
                        {influencerNodes.map(node => (
                            <NodeCard
                                key={node.id}
                                node={node}
                                isWedge={false}
                                isInSequence={false}
                                onSetWedge={() => { }}
                                onToggleSequence={() => { }}
                            />
                        ))}
                    </div>
                </div>
            )}

            {/* Edges */}
            <div>
                <h3 className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-3">
                    Relationships ({graph.edges.length})
                </h3>
                <div className="space-y-2">
                    {graph.edges.map(edge => (
                        <EdgeItem
                            key={edge.id}
                            edge={edge}
                            fromNode={graph.nodes.find(n => n.id === edge.from)}
                            toNode={graph.nodes.find(n => n.id === edge.to)}
                            onRemove={() => handleRemoveEdge(edge.id)}
                        />
                    ))}
                    {graph.edges.length === 0 && (
                        <div className="text-center py-8 text-[#9D9F9F]">
                            <GitBranch className="w-8 h-8 mx-auto mb-2 opacity-40" />
                            <p className="text-sm">No relationships defined yet</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
