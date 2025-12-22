'use client';

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { cn } from '@/lib/utils';
import {
    Type,
    Square,
    Circle,
    Image as ImageIcon,
    Trash2,
    Copy,
    MoveUp,
    MoveDown,
    Eye,
    EyeOff,
    Lock,
    Unlock,
    Download,
    ZoomIn,
    ZoomOut,
    RotateCcw,
    X,
    Plus,
    Clock,
    MessageCircle,
    Sparkles,
    Maximize2,
    Share2,
    Check
} from 'lucide-react';
import { CanvasElement, CanvasData } from '../types';
import { SmartCropPresets } from '../BrandKitOverlay';
import { CaptionSuggestions } from '../CaptionSuggestions';
import { AnimationPresets } from '../AnimationPresets';
import { copyToClipboard, shareContent } from '../utils/exports';

interface MuseCanvasProps {
    initialData?: CanvasData;
    onSave?: (data: CanvasData) => void;
    onClose?: () => void;
    className?: string;
}

const DEFAULT_CANVAS: CanvasData = {
    width: 800,
    height: 600,
    background: '#ffffff',
    elements: [],
};

let elementIdCounter = 0;
function generateId() {
    return `element-${Date.now()}-${elementIdCounter++}`;
}

export function MuseCanvas({
    initialData,
    onSave,
    onClose,
    className
}: MuseCanvasProps) {
    const [canvasData, setCanvasData] = useState<CanvasData>(initialData || DEFAULT_CANVAS);
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [zoom, setZoom] = useState(1);
    const [tool, setTool] = useState<'select' | 'text' | 'rectangle' | 'circle' | 'image'>('select');
    const [activePanel, setActivePanel] = useState<'layers' | 'smart-crop' | 'captions' | 'animate' | null>('layers');
    const [copied, setCopied] = useState(false);
    const canvasRef = useRef<HTMLDivElement>(null);

    const selectedElement = canvasData.elements.find(e => e.id === selectedId);

    // Add new element
    const addElement = useCallback((type: 'text' | 'image' | 'shape', shapeType?: 'rectangle' | 'circle') => {
        const newElement: CanvasElement = {
            id: generateId(),
            type: type === 'shape' ? 'shape' : type,
            x: 100 + Math.random() * 200,
            y: 100 + Math.random() * 100,
            width: type === 'text' ? 200 : 150,
            height: type === 'text' ? 50 : 150,
            rotation: 0,
            content: type === 'text' ? 'Double-click to edit' : (shapeType || 'rectangle'),
            style: {
                fontSize: 24,
                fontWeight: 'bold',
                color: '#000000',
                backgroundColor: type === 'shape' ? '#e5e5e5' : 'transparent',
                borderRadius: shapeType === 'circle' ? '50%' : '0',
            },
            locked: false,
            visible: true,
        };

        setCanvasData(prev => ({
            ...prev,
            elements: [...prev.elements, newElement],
        }));
        setSelectedId(newElement.id);
        setTool('select');
    }, []);

    // Delete element
    const deleteElement = useCallback((id: string) => {
        setCanvasData(prev => ({
            ...prev,
            elements: prev.elements.filter(e => e.id !== id),
        }));
        if (selectedId === id) setSelectedId(null);
    }, [selectedId]);

    // Toggle visibility
    const toggleVisibility = useCallback((id: string) => {
        setCanvasData(prev => ({
            ...prev,
            elements: prev.elements.map(e =>
                e.id === id ? { ...e, visible: !e.visible } : e
            ),
        }));
    }, []);

    // Toggle lock
    const toggleLock = useCallback((id: string) => {
        setCanvasData(prev => ({
            ...prev,
            elements: prev.elements.map(e =>
                e.id === id ? { ...e, locked: !e.locked } : e
            ),
        }));
    }, []);

    // Move element in layer order
    const moveElement = useCallback((id: string, direction: 'up' | 'down') => {
        setCanvasData(prev => {
            const index = prev.elements.findIndex(e => e.id === id);
            if (index === -1) return prev;
            if (direction === 'up' && index === prev.elements.length - 1) return prev;
            if (direction === 'down' && index === 0) return prev;

            const newElements = [...prev.elements];
            const swapIndex = direction === 'up' ? index + 1 : index - 1;
            [newElements[index], newElements[swapIndex]] = [newElements[swapIndex], newElements[index]];

            return { ...prev, elements: newElements };
        });
    }, []);

    // Duplicate element
    const duplicateElement = useCallback((id: string) => {
        const element = canvasData.elements.find(e => e.id === id);
        if (!element) return;

        const newElement: CanvasElement = {
            ...element,
            id: generateId(),
            x: element.x + 20,
            y: element.y + 20,
        };

        setCanvasData(prev => ({
            ...prev,
            elements: [...prev.elements, newElement],
        }));
        setSelectedId(newElement.id);
    }, [canvasData.elements]);

    // Export handlers
    const handleCopyCanvas = async () => {
        // For demo, copy a JSON representation
        const success = await copyToClipboard(JSON.stringify(canvasData, null, 2));
        if (success) {
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    const handleShareCanvas = async () => {
        await shareContent('Muse Canvas', `Canvas with ${canvasData.elements.length} elements`);
    };

    const handleDownloadCanvas = () => {
        // Download canvas as JSON (could be enhanced to export as PNG)
        const blob = new Blob([JSON.stringify(canvasData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'muse-canvas.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    return (
        <div className={cn('flex flex-col h-full bg-background', className)}>
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-border/40">
                <div className="flex items-center gap-3">
                    {onClose && (
                        <button
                            onClick={onClose}
                            className="h-8 w-8 rounded-lg flex items-center justify-center hover:bg-muted transition-colors"
                        >
                            <X className="h-4 w-4" />
                        </button>
                    )}
                    <h1 className="text-lg font-semibold">Muse Canvas</h1>
                </div>

                <div className="flex items-center gap-4">
                    {/* Zoom controls */}
                    <div className="flex items-center gap-1 px-2 py-1 rounded-lg border border-border/60">
                        <button
                            onClick={() => setZoom(z => Math.max(0.25, z - 0.25))}
                            className="p-1 hover:bg-muted rounded"
                        >
                            <ZoomOut className="h-4 w-4" />
                        </button>
                        <span className="text-xs font-mono w-12 text-center">{Math.round(zoom * 100)}%</span>
                        <button
                            onClick={() => setZoom(z => Math.min(2, z + 0.25))}
                            className="p-1 hover:bg-muted rounded"
                        >
                            <ZoomIn className="h-4 w-4" />
                        </button>
                        <button
                            onClick={() => setZoom(1)}
                            className="p-1 hover:bg-muted rounded"
                            title="Reset zoom"
                        >
                            <RotateCcw className="h-3.5 w-3.5" />
                        </button>
                    </div>

                    {/* Copy button */}
                    <button
                        onClick={handleCopyCanvas}
                        title="Copy canvas data"
                        className="h-9 w-9 rounded-lg flex items-center justify-center hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
                    >
                        {copied ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                    </button>

                    {/* Share button */}
                    <button
                        onClick={handleShareCanvas}
                        title="Share"
                        className="h-9 w-9 rounded-lg flex items-center justify-center hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
                    >
                        <Share2 className="h-4 w-4" />
                    </button>

                    {/* Download button */}
                    <button
                        onClick={handleDownloadCanvas}
                        title="Download"
                        className="h-9 w-9 rounded-lg flex items-center justify-center hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
                    >
                        <Download className="h-4 w-4" />
                    </button>

                    <div className="w-px h-6 bg-border/40" />

                    <button
                        onClick={() => onSave?.(canvasData)}
                        className={cn(
                            'h-9 px-4 rounded-lg',
                            'bg-foreground text-background',
                            'text-sm font-medium',
                            'hover:opacity-90 transition-opacity'
                        )}
                    >
                        Save
                    </button>
                </div>
            </div>

            <div className="flex-1 flex overflow-hidden">
                {/* Intelligence Side-Rail (Left) */}
                <div className="w-14 border-r border-border/40 flex flex-col items-center py-4 gap-4 bg-muted/5">
                    <RailButton
                        icon={Type}
                        active={tool === 'text'}
                        onClick={() => { setTool('text'); addElement('text'); }}
                        label="Text"
                    />
                    <RailButton
                        icon={Square}
                        active={tool === 'rectangle'}
                        onClick={() => { setTool('rectangle'); addElement('shape', 'rectangle'); }}
                        label="Box"
                    />
                    <RailButton
                        icon={Circle}
                        active={tool === 'circle'}
                        onClick={() => { setTool('circle'); addElement('shape', 'circle'); }}
                        label="Circle"
                    />
                    <RailButton
                        icon={ImageIcon}
                        active={tool === 'image'}
                        onClick={() => setTool('image')}
                        label="Image"
                    />
                    <div className="flex-1" />
                    <RailButton
                        icon={Clock}
                        active={activePanel === 'layers'}
                        onClick={() => setActivePanel(activePanel === 'layers' ? null : 'layers')}
                        label="Layers"
                    />
                </div>

                {/* Canvas Area */}
                <div className="flex-1 overflow-auto bg-muted/30 p-8">
                    <div
                        ref={canvasRef}
                        className="relative mx-auto shadow-lg rounded-lg overflow-hidden"
                        style={{
                            width: canvasData.width * zoom,
                            height: canvasData.height * zoom,
                            backgroundColor: canvasData.background,
                            transform: `scale(${zoom})`,
                            transformOrigin: 'top left',
                        }}
                        onClick={(e) => {
                            if (e.target === canvasRef.current) {
                                setSelectedId(null);
                            }
                        }}
                    >
                        {canvasData.elements.map(element => (
                            <CanvasElementComponent
                                key={element.id}
                                element={element}
                                isSelected={selectedId === element.id}
                                onSelect={() => !element.locked && setSelectedId(element.id)}
                                zoom={zoom}
                            />
                        ))}
                    </div>
                </div>

                {/* Side-Rail (Right) for Intelligence & Presets */}
                <div className="w-14 border-l border-border/40 flex flex-col items-center py-4 gap-4 bg-muted/5">
                    <RailButton
                        icon={Maximize2} // Using Maximize2 as a resize/crop icon
                        active={activePanel === 'smart-crop'}
                        onClick={() => setActivePanel(activePanel === 'smart-crop' ? null : 'smart-crop')}
                        label="Resize"
                    />
                    <RailButton
                        icon={MessageCircle}
                        active={activePanel === 'captions'}
                        onClick={() => setActivePanel(activePanel === 'captions' ? null : 'captions')}
                        label="Captions"
                    />
                    <RailButton
                        icon={Sparkles}
                        active={activePanel === 'animate'}
                        onClick={() => setActivePanel(activePanel === 'animate' ? null : 'animate')}
                        label="Animate"
                    />
                </div>

                {/* Contextual Panel (Right) */}
                <div
                    className={cn(
                        'border-l border-border/40 bg-card transition-all duration-300 ease-in-out overflow-hidden',
                        activePanel ? 'w-80' : 'w-0 border-0'
                    )}
                >
                    <div className="w-80 h-full flex flex-col">
                        <div className="p-4 border-b border-border/40 flex items-center justify-between bg-muted/5">
                            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                                {activePanel === 'layers' && 'Layers'}
                                {activePanel === 'smart-crop' && 'Canvas Resize'}
                                {activePanel === 'captions' && 'AI Captions'}
                                {activePanel === 'animate' && 'Motion Presets'}
                            </span>
                            <button
                                onClick={() => setActivePanel(null)}
                                className="h-6 w-6 rounded-full flex items-center justify-center hover:bg-muted transition-colors"
                            >
                                <X className="h-3 w-3" />
                            </button>
                        </div>

                        <div className="flex-1 overflow-auto p-4 scroll-smooth">
                            {activePanel === 'layers' && (
                                <div className="space-y-1">
                                    {[...canvasData.elements].reverse().map(element => (
                                        <LayerItem
                                            key={element.id}
                                            element={element}
                                            isSelected={selectedId === element.id}
                                            onSelect={() => setSelectedId(element.id)}
                                            onToggleVisibility={() => toggleVisibility(element.id)}
                                            onToggleLock={() => toggleLock(element.id)}
                                            onMoveUp={() => moveElement(element.id, 'up')}
                                            onMoveDown={() => moveElement(element.id, 'down')}
                                            onDuplicate={() => duplicateElement(element.id)}
                                            onDelete={() => deleteElement(element.id)}
                                        />
                                    ))}

                                    {canvasData.elements.length === 0 && (
                                        <div className="text-center py-12 px-6">
                                            <div className="w-12 h-12 bg-muted/30 rounded-full flex items-center justify-center mx-auto mb-4">
                                                <Plus className="h-6 w-6 text-muted-foreground/50" />
                                            </div>
                                            <p className="text-sm font-medium mb-1">Canvas is empty</p>
                                            <p className="text-xs text-muted-foreground">Use the left toolbar to add elements.</p>
                                        </div>
                                    )}
                                </div>
                            )}

                            {activePanel === 'smart-crop' && (
                                <SmartCropPresets
                                    onSelect={(preset) => {
                                        const { width, height } = preset;
                                        if (width && height) {
                                            setCanvasData(prev => ({ ...prev, width, height }));
                                        }
                                    }}
                                />
                            )}

                            {activePanel === 'captions' && (
                                <CaptionSuggestions
                                    onSelect={(text) => {
                                        const newElement: CanvasElement = {
                                            id: `elem-${Date.now()}`,
                                            type: 'text',
                                            x: 50,
                                            y: canvasData.height - 100,
                                            width: canvasData.width - 100,
                                            height: 60,
                                            rotation: 0,
                                            content: text,
                                            style: {
                                                fontSize: 24,
                                                fontWeight: 'bold',
                                                color: '#000000',
                                                textAlign: 'center',
                                                backgroundColor: '#ffffff',
                                                padding: '10px',
                                            },
                                            locked: false,
                                            visible: true,
                                        };
                                        setCanvasData(prev => ({
                                            ...prev,
                                            elements: [...prev.elements, newElement],
                                        }));
                                        setSelectedId(newElement.id);
                                    }}
                                />
                            )}

                            {activePanel === 'animate' && (
                                selectedId ? (
                                    <AnimationPresets
                                        selectedAnimation={selectedElement?.animation}
                                        onSelect={(anim) => {
                                            setCanvasData(prev => ({
                                                ...prev,
                                                elements: prev.elements.map(e =>
                                                    e.id === selectedId ? { ...e, animation: anim } : e
                                                )
                                            }));
                                        }}
                                    />
                                ) : (
                                    <div className="text-center py-12 text-muted-foreground">
                                        <Sparkles className="h-8 w-8 mx-auto mb-3 opacity-30" />
                                        <p className="text-sm">Select an element to animate</p>
                                    </div>
                                )
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function CanvasElementComponent({
    element,
    isSelected,
    onSelect,
    zoom
}: {
    element: CanvasElement;
    isSelected: boolean;
    onSelect: () => void;
    zoom: number;
}) {
    if (!element.visible) return null;

    const style: React.CSSProperties = {
        position: 'absolute',
        left: element.x,
        top: element.y,
        width: element.width,
        height: element.height,
        transform: `rotate(${element.rotation}deg)`,
        ...element.style as React.CSSProperties,
        cursor: element.locked ? 'not-allowed' : 'move',
    };

    const getAnimationClass = () => {
        switch (element.animation) {
            case 'fade': return 'animate-in fade-in duration-1000';
            case 'slide-up': return 'animate-in slide-in-from-bottom-10 fade-in duration-1000';
            case 'scale': return 'animate-in zoom-in duration-1000';
            case 'breathe': return 'animate-pulse';
            default: return '';
        }
    };

    return (
        <div
            onClick={(e) => { e.stopPropagation(); onSelect(); }}
            className={cn(
                'transition-shadow duration-150',
                isSelected && 'ring-2 ring-blue-500 ring-offset-2',
                getAnimationClass()
            )}
            style={style}
        >
            {element.type === 'text' && (
                <div
                    className="w-full h-full flex items-center justify-center p-2"
                    contentEditable={isSelected && !element.locked}
                    suppressContentEditableWarning
                >
                    {element.content}
                </div>
            )}
            {element.type === 'shape' && (
                <div className="w-full h-full" />
            )}
            {element.type === 'image' && (
                <div className="w-full h-full bg-muted/50 flex items-center justify-center">
                    <ImageIcon className="h-8 w-8 text-muted-foreground/50" />
                </div>
            )}
        </div>
    );
}

function RailButton({
    icon: Icon,
    label,
    active,
    onClick,
    primary
}: {
    icon: React.ComponentType<{ className?: string }>;
    label: string;
    active?: boolean;
    onClick?: () => void;
    primary?: boolean;
}) {
    return (
        <button
            onClick={onClick}
            title={label}
            className={cn(
                'group relative h-10 w-10 rounded-xl flex items-center justify-center transition-all duration-200',
                active
                    ? primary ? 'bg-foreground text-background shadow-lg shadow-foreground/10' : 'bg-background text-foreground shadow-sm ring-1 ring-border'
                    : primary ? 'text-muted-foreground hover:text-foreground hover:bg-muted' : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
            )}
        >
            <Icon className={cn('h-5 w-5', active && 'animate-in zoom-in-75 duration-300')} />
            {!active && (
                <div className="absolute left-full ml-3 px-2 py-1 rounded bg-foreground text-background text-[10px] font-medium opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50">
                    {label}
                </div>
            )}
        </button>
    );
}

function LayerItem({
    element,
    isSelected,
    onSelect,
    onToggleVisibility,
    onToggleLock,
    onMoveUp,
    onMoveDown,
    onDuplicate,
    onDelete
}: {
    element: CanvasElement;
    isSelected: boolean;
    onSelect: () => void;
    onToggleVisibility: () => void;
    onToggleLock: () => void;
    onMoveUp: () => void;
    onMoveDown: () => void;
    onDuplicate: () => void;
    onDelete: () => void;
}) {
    const Icon = element.type === 'text' ? Type : element.type === 'image' ? ImageIcon : Square;

    return (
        <div
            onClick={onSelect}
            className={cn(
                'group flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors',
                isSelected ? 'bg-muted' : 'hover:bg-muted/50'
            )}
        >
            <Icon className="h-4 w-4 text-muted-foreground shrink-0" />
            <span className={cn(
                'flex-1 text-sm truncate',
                !element.visible && 'text-muted-foreground/50'
            )}>
                {element.type === 'text' ? element.content.substring(0, 15) : element.type}
            </span>

            <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                    onClick={(e) => { e.stopPropagation(); onToggleVisibility(); }}
                    className="p-1 rounded hover:bg-background"
                >
                    {element.visible ? <Eye className="h-3 w-3" /> : <EyeOff className="h-3 w-3" />}
                </button>
                <button
                    onClick={(e) => { e.stopPropagation(); onToggleLock(); }}
                    className="p-1 rounded hover:bg-background"
                >
                    {element.locked ? <Lock className="h-3 w-3" /> : <Unlock className="h-3 w-3" />}
                </button>
                <button
                    onClick={(e) => { e.stopPropagation(); onDelete(); }}
                    className="p-1 rounded hover:bg-background text-red-500"
                >
                    <Trash2 className="h-3 w-3" />
                </button>
            </div>
        </div>
    );
}
