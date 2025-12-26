'use client';

import React from 'react';
import { InterICPGraph, ICPGraphNode, ICPGraphEdge, ICPEdgeType } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import { ArrowRight, Circle, ArrowRightCircle, Star, X, Plus } from 'lucide-react';
import { cn } from '@/lib/utils';

interface InterICPGraphProps {
    graph: InterICPGraph;
    onChange: (graph: InterICPGraph) => void;
    onContinue: () => void;
}

function NodeCard({
    node,
    isWedge,
    onSetWedge,
    onRemove,
}: {
    node: ICPGraphNode;
    isWedge: boolean;
    onSetWedge: () => void;
    onRemove: () => void;
}) {
    return (
        <div className={cn(
            "p-4 rounded-xl border-2 flex items-center gap-3",
            node.type === 'icp'
                ? "border-primary bg-primary/5"
                : "border-amber-500 bg-amber-50/50 dark:bg-amber-950/20"
        )}>
            <div className={cn(
                "w-10 h-10 rounded-full flex items-center justify-center",
                node.type === 'icp' ? "bg-primary/20" : "bg-amber-200 dark:bg-amber-900/50"
            )}>
                <Circle className="h-4 w-4" />
            </div>
            <div className="flex-1">
                <span className="font-medium">{node.label}</span>
                <span className={cn(
                    "text-xs ml-2",
                    node.type === 'icp' ? "text-primary" : "text-amber-600"
                )}>
                    {node.type === 'icp' ? 'ICP' : 'Influencer'}
                </span>
            </div>
            {node.type === 'icp' && (
                <button
                    onClick={onSetWedge}
                    className={cn(
                        "p-2 rounded-lg transition-colors",
                        isWedge ? "bg-primary text-primary-foreground" : "hover:bg-muted"
                    )}
                    title="Set as primary wedge ICP"
                >
                    <Star className={cn("h-4 w-4", isWedge && "fill-current")} />
                </button>
            )}
            {node.type === 'influencer' && (
                <button onClick={onRemove} className="p-2 hover:bg-destructive/10 rounded-lg">
                    <X className="h-4 w-4 text-muted-foreground" />
                </button>
            )}
        </div>
    );
}

function EdgeCard({
    edge,
    nodes,
    onRemove,
    onWeightChange,
}: {
    edge: ICPGraphEdge;
    nodes: ICPGraphNode[];
    onRemove: () => void;
    onWeightChange: (weight: number) => void;
}) {
    const fromNode = nodes.find(n => n.id === edge.from);
    const toNode = nodes.find(n => n.id === edge.to);

    const typeLabels: Record<ICPEdgeType, string> = {
        influences: '→ influences →',
        refers: '→ refers →',
        upstream: '← upstream of',
        downstream: '→ downstream of'
    };

    return (
        <div className="p-3 bg-muted/50 rounded-lg flex items-center gap-3">
            <span className="text-sm font-medium">{fromNode?.label}</span>
            <span className="text-xs text-muted-foreground">{typeLabels[edge.type]}</span>
            <span className="text-sm font-medium">{toNode?.label}</span>
            <div className="flex-1" />
            <div className="flex items-center gap-1">
                {[1, 2, 3, 4, 5].map(w => (
                    <button
                        key={w}
                        onClick={() => onWeightChange(w)}
                        className={cn(
                            "w-6 h-6 rounded text-xs",
                            edge.weight === w
                                ? "bg-primary text-primary-foreground"
                                : "bg-muted text-muted-foreground hover:bg-muted/80"
                        )}
                    >
                        {w}
                    </button>
                ))}
            </div>
            <button onClick={onRemove} className="p-1 hover:bg-destructive/10 rounded">
                <X className="h-3 w-3 text-muted-foreground" />
            </button>
        </div>
    );
}

export function InterICPGraphScreen({ graph, onChange, onContinue }: InterICPGraphProps) {
    const icpNodes = graph.nodes.filter(n => n.type === 'icp');
    const influencerNodes = graph.nodes.filter(n => n.type === 'influencer');

    const setWedge = (nodeId: string) => {
        onChange({ ...graph, primaryWedgeICP: nodeId });
    };

    const removeNode = (nodeId: string) => {
        onChange({
            ...graph,
            nodes: graph.nodes.filter(n => n.id !== nodeId),
            edges: graph.edges.filter(e => e.from !== nodeId && e.to !== nodeId)
        });
    };

    const removeEdge = (edgeId: string) => {
        onChange({
            ...graph,
            edges: graph.edges.filter(e => e.id !== edgeId)
        });
    };

    const updateEdgeWeight = (edgeId: string, weight: number) => {
        onChange({
            ...graph,
            edges: graph.edges.map(e => e.id === edgeId ? { ...e, weight } : e)
        });
    };

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="text-center space-y-2">
                <h1 className="text-3xl font-serif font-bold text-foreground">
                    Inter-ICP Relationship Graph
                </h1>
                <p className="text-muted-foreground max-w-lg mx-auto">
                    Map how ICPs and influencers connect. This drives ecosystem leverage.
                </p>
            </div>

            {/* ICP Nodes */}
            <div className="max-w-2xl mx-auto">
                <h2 className="font-semibold mb-4">ICPs</h2>
                <div className="grid gap-3">
                    {icpNodes.map(node => (
                        <NodeCard
                            key={node.id}
                            node={node}
                            isWedge={node.id === graph.primaryWedgeICP}
                            onSetWedge={() => setWedge(node.id)}
                            onRemove={() => { }}
                        />
                    ))}
                </div>
            </div>

            {/* Influencer Nodes */}
            <div className="max-w-2xl mx-auto">
                <h2 className="font-semibold mb-4">Influencer Nodes</h2>
                <div className="grid gap-3">
                    {influencerNodes.map(node => (
                        <NodeCard
                            key={node.id}
                            node={node}
                            isWedge={false}
                            onSetWedge={() => { }}
                            onRemove={() => removeNode(node.id)}
                        />
                    ))}
                </div>
            </div>

            {/* Edges */}
            <div className="max-w-2xl mx-auto">
                <h2 className="font-semibold mb-4">Relationships (weight = leverage)</h2>
                <div className="space-y-2">
                    {graph.edges.map(edge => (
                        <EdgeCard
                            key={edge.id}
                            edge={edge}
                            nodes={graph.nodes}
                            onRemove={() => removeEdge(edge.id)}
                            onWeightChange={(w) => updateEdgeWeight(edge.id, w)}
                        />
                    ))}
                </div>
            </div>

            {/* Wedge Strategy */}
            {graph.primaryWedgeICP && (
                <div className="max-w-2xl mx-auto bg-primary/5 border-2 border-primary/20 rounded-xl p-4 text-center">
                    <Star className="h-6 w-6 text-primary mx-auto mb-2" />
                    <p className="font-semibold">
                        Primary Wedge: {icpNodes.find(n => n.id === graph.primaryWedgeICP)?.label}
                    </p>
                    <p className="text-sm text-muted-foreground">This is the ICP you enter through</p>
                </div>
            )}

            {/* Continue Button */}
            <div className="flex justify-center pt-4">
                <Button
                    size="lg"
                    onClick={onContinue}
                    disabled={!graph.primaryWedgeICP}
                    className="px-8 py-6 text-lg rounded-xl"
                >
                    {graph.primaryWedgeICP ? 'Continue' : 'Select a Primary Wedge ICP'}
                    <ArrowRight className="h-5 w-5 ml-2" />
                </Button>
            </div>
        </div>
    );
}
