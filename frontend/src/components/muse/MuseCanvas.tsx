"use client";

import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { MuseAsset, useMuseStore } from "@/stores/museStore";
import { MuseNode } from "@/components/muse/MuseNode";
import { MuseToolbar, CanvasTool } from "@/components/muse/MuseToolbar";
import { MuseProperties } from "@/components/muse/MuseProperties";
import { MuseOracle } from "@/components/muse/MuseOracle";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   MUSE CANVAS (IDE V3)
   A professional grade diagramming environment.
   ══════════════════════════════════════════════════════════════════════════════ */

interface CanvasNode extends MuseAsset {
    x: number;
    y: number;
}

export function MuseCanvas() {
    const { assets, addAsset, deleteAsset } = useMuseStore();
    const containerRef = useRef<HTMLDivElement>(null);

    // State
    const [nodes, setNodes] = useState<CanvasNode[]>([]);
    const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
    const [activeTool, setActiveTool] = useState<CanvasTool>('select');
    const [isThinking, setIsThinking] = useState(false);

    // Viewport
    const [pan, setPan] = useState({ x: 0, y: 0 });
    const [isDraggingCanvas, setIsDraggingCanvas] = useState(false);
    const [zoom, setZoom] = useState(1);

    // Sync assets to nodes once
    useEffect(() => {
        if (nodes.length === 0 && assets.length > 0) {
            const GRID_SIZE = 40;
            const COLS = 4;
            setNodes(assets.map((asset, i) => ({
                ...asset,
                // Align to grid
                x: (i % COLS) * 320 - ((COLS * 320) / 2) + (Math.random() * 20),
                y: Math.floor(i / COLS) * 200 - 200
            })));
        }
    }, [assets]);

    const handlePan = (e: React.MouseEvent) => {
        if (activeTool === 'hand' && isDraggingCanvas) {
            setPan(prev => ({
                x: prev.x + e.movementX,
                y: prev.y + e.movementY
            }));
        }
    };

    const handleWheel = (e: React.WheelEvent) => {
        if (e.ctrlKey) {
            e.preventDefault();
            const newZoom = Math.max(0.2, Math.min(2, zoom - e.deltaY * 0.001));
            setZoom(newZoom);
        }
    };

    return (
        <div
            ref={containerRef}
            className={cn(
                "relative w-full h-full overflow-hidden bg-[var(--paper)] select-none",
                activeTool === 'hand' ? "cursor-grab active:cursor-grabbing" : "cursor-default"
            )}
            onMouseDown={(e) => {
                if (e.target === containerRef.current) {
                    setSelectedNodeId(null);
                    if (activeTool === 'hand') setIsDraggingCanvas(true);
                }
            }}
            onMouseUp={() => setIsDraggingCanvas(false)}
            onMouseLeave={() => setIsDraggingCanvas(false)}
            onMouseMove={handlePan}
            onWheel={handleWheel}
        >
            {/* 1. Infinite Technical Grid */}
            <div
                className="absolute inset-0 pointer-events-none opacity-20"
                style={{
                    transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
                    transformOrigin: '0 0',
                    backgroundImage: `
                        linear-gradient(to right, var(--ink) 1px, transparent 1px),
                        linear-gradient(to bottom, var(--ink) 1px, transparent 1px)
                    `,
                    backgroundSize: '40px 40px'
                }}
            />
            {/* Major Grid Lines */}
            <div
                className="absolute inset-0 pointer-events-none opacity-10"
                style={{
                    transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
                    transformOrigin: '0 0',
                    backgroundImage: `
                        linear-gradient(to right, var(--blueprint) 1px, transparent 1px),
                        linear-gradient(to bottom, var(--blueprint) 1px, transparent 1px)
                    `,
                    backgroundSize: '200px 200px'
                }}
            />

            {/* 2. Content Layer */}
            <motion.div
                className="absolute inset-0 flex items-center justify-center pointer-events-none will-change-transform"
                animate={{ x: pan.x, y: pan.y, scale: zoom }}
                transition={{ type: "spring", stiffness: 800, damping: 50 }} // Tight spring for tech feel
            >
                {/* Center Datum */}
                <div className="absolute w-4 h-0.5 bg-[var(--error)]" />
                <div className="absolute w-0.5 h-4 bg-[var(--error)]" />

                {nodes.map(node => (
                    <div key={node.id} className="pointer-events-auto absolute" style={{ left: 0, top: 0 }}>
                        <MuseNode
                            asset={node}
                            x={node.x}
                            y={node.y}
                            isSelected={selectedNodeId === node.id}
                            onSelect={() => setSelectedNodeId(node.id)}
                        />
                    </div>
                ))}
            </motion.div>

            {/* 3. Interface Layer */}

            {/* Top Left: HUD */}
            <div className="absolute top-6 left-20 pointer-events-none">
                <div className="flex flex-col">
                    <h1 className="font-serif text-xl text-[var(--ink)]">MKT-OS // WORKSPACE</h1>
                    <div className="flex gap-4 mt-1 font-mono text-[10px] text-[var(--muted)] uppercase tracking-wider">
                        <span>X: {Math.round(pan.x)} Y: {Math.round(pan.y)}</span>
                        <span>ZM: {Math.round(zoom * 100)}%</span>
                        <span>OBJS: {nodes.length}</span>
                    </div>
                </div>
            </div>

            {/* Toolbar */}
            <MuseToolbar activeTool={activeTool} onToolChange={setActiveTool} />

            {/* Oracle (Only visible if not inspecting, to reduce clutter? Or always visible?) */}
            {/* Let's put Oracle at bottom center, cleaner */}
            <MuseOracle
                isThinking={isThinking}
                onInvoke={(prompt) => {
                    setIsThinking(true);
                    setTimeout(() => {
                        setIsThinking(false);
                        const newAsset: MuseAsset = {
                            id: `GEN-${Date.now()}`,
                            title: prompt,
                            type: 'Campaign',
                            content: "Generated content placeholder...",
                            tags: ["AI"],
                            createdAt: new Date().toISOString(),
                            source: 'Muse'
                        };
                        addAsset(newAsset);
                        setNodes(prev => [...prev, { ...newAsset, x: -pan.x, y: -pan.y }]);
                    }, 1000);
                }}
            />

            {/* Properties Panel (Right) */}
            <MuseProperties
                selectedAsset={selectedNodeId ? nodes.find(n => n.id === selectedNodeId) || null : null}
                onClose={() => setSelectedNodeId(null)}
                onDelete={(id) => {
                    deleteAsset(id);
                    setNodes(prev => prev.filter(n => n.id !== id));
                    setSelectedNodeId(null);
                }}
            />

        </div>
    );
}
