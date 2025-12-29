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
  Check,
} from 'lucide-react';
import { CanvasElement, CanvasData } from '../types';
import { SmartCropPresets } from '../BrandKitOverlay';
import { CaptionSuggestions } from '../CaptionSuggestions';
import { AnimationPresets } from '../AnimationPresets';
import { copyToClipboard, shareContent } from '../utils/exports';
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
} from '@/components/ui/resizable';
import {
  TypographyH3,
  TypographySmall,
  TypographyMuted,
} from '@/components/ui/typography';
import { Separator } from '@/components/ui/separator';
import { Skeleton } from '@/components/ui/skeleton';
import { Kbd } from '@/components/ui/kbd';
import { ButtonGroup } from '@/components/ui/button-group';

interface MuseCanvasProps {
  initialData?: CanvasData;
  onSave?: (data: CanvasData) => void;
  onClose?: () => void;
  onChange?: () => void;
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
  onChange,
  className,
}: MuseCanvasProps) {
  const [canvasData, setCanvasData] = useState<CanvasData>(
    initialData || DEFAULT_CANVAS
  );
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [zoom, setZoom] = useState(1);
  const [tool, setTool] = useState<
    'select' | 'text' | 'rectangle' | 'circle' | 'image'
  >('select');
  const [activePanel, setActivePanel] = useState<
    'layers' | 'smart-crop' | 'captions' | 'animate' | null
  >('layers');
  const [copied, setCopied] = useState(false);
  const canvasRef = useRef<HTMLDivElement>(null);

  // Notify parent of changes for dirty state tracking
  useEffect(() => {
    if (canvasData !== (initialData || DEFAULT_CANVAS)) {
      onChange?.();
    }
  }, [canvasData, initialData, onChange]);

  const selectedElement = canvasData.elements.find((e) => e.id === selectedId);

  // Add new element
  const addElement = useCallback(
    (type: 'text' | 'image' | 'shape', shapeType?: 'rectangle' | 'circle') => {
      const newElement: CanvasElement = {
        id: generateId(),
        type: type === 'shape' ? 'shape' : type,
        x: 100 + Math.random() * 200,
        y: 100 + Math.random() * 100,
        width: type === 'text' ? 200 : 150,
        height: type === 'text' ? 50 : 150,
        rotation: 0,
        content:
          type === 'text' ? 'Double-click to edit' : shapeType || 'rectangle',
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

      setCanvasData((prev) => ({
        ...prev,
        elements: [...prev.elements, newElement],
      }));
      setSelectedId(newElement.id);
      setTool('select');
    },
    []
  );

  // Delete element
  const deleteElement = useCallback(
    (id: string) => {
      setCanvasData((prev) => ({
        ...prev,
        elements: prev.elements.filter((e) => e.id !== id),
      }));
      if (selectedId === id) setSelectedId(null);
    },
    [selectedId]
  );

  // Toggle visibility
  const toggleVisibility = useCallback((id: string) => {
    setCanvasData((prev) => ({
      ...prev,
      elements: prev.elements.map((e) =>
        e.id === id ? { ...e, visible: !e.visible } : e
      ),
    }));
  }, []);

  // Toggle lock
  const toggleLock = useCallback((id: string) => {
    setCanvasData((prev) => ({
      ...prev,
      elements: prev.elements.map((e) =>
        e.id === id ? { ...e, locked: !e.locked } : e
      ),
    }));
  }, []);

  // Move element in layer order
  const moveElement = useCallback((id: string, direction: 'up' | 'down') => {
    setCanvasData((prev) => {
      const index = prev.elements.findIndex((e) => e.id === id);
      if (index === -1) return prev;
      if (direction === 'up' && index === prev.elements.length - 1) return prev;
      if (direction === 'down' && index === 0) return prev;

      const newElements = [...prev.elements];
      const swapIndex = direction === 'up' ? index + 1 : index - 1;
      [newElements[index], newElements[swapIndex]] = [
        newElements[swapIndex],
        newElements[index],
      ];

      return { ...prev, elements: newElements };
    });
  }, []);

  // Duplicate element
  const duplicateElement = useCallback(
    (id: string) => {
      const element = canvasData.elements.find((e) => e.id === id);
      if (!element) return;

      const newElement: CanvasElement = {
        ...element,
        id: generateId(),
        x: element.x + 20,
        y: element.y + 20,
      };

      setCanvasData((prev) => ({
        ...prev,
        elements: [...prev.elements, newElement],
      }));
      setSelectedId(newElement.id);
    },
    [canvasData.elements]
  );

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
    await shareContent(
      'Muse Canvas',
      `Canvas with ${canvasData.elements.length} elements`
    );
  };

  const handleDownloadCanvas = () => {
    // Download canvas as JSON (could be enhanced to export as PNG)
    const blob = new Blob([JSON.stringify(canvasData, null, 2)], {
      type: 'application/json',
    });
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
          <TypographyH3 className="text-lg">Muse Canvas</TypographyH3>
        </div>

        <div className="flex items-center gap-4">
          {/* Zoom controls using ButtonGroup */}
          <ButtonGroup className="h-9">
            <button
              onClick={() => setZoom((z) => Math.max(0.25, z - 0.25))}
              className="px-2 hover:bg-muted transition-colors flex items-center justify-center border-r border-input last:border-r-0"
              title="Zoom Out"
            >
              <ZoomOut className="h-3.5 w-3.5" />
            </button>
            <div className="px-2 min-w-[3rem] flex items-center justify-center text-xs font-mono font-medium border-r border-input bg-muted/20">
              {Math.round(zoom * 100)}%
            </div>
            <button
              onClick={() => setZoom((z) => Math.min(2, z + 0.25))}
              className="px-2 hover:bg-muted transition-colors flex items-center justify-center border-r border-input last:border-r-0"
              title="Zoom In"
            >
              <ZoomIn className="h-3.5 w-3.5" />
            </button>
          </ButtonGroup>

          {/* Actions with Popover for Share */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopyCanvas}
              title="Copy"
              className="h-9 w-9 rounded-lg flex items-center justify-center hover:bg-muted transition-colors"
            >
              {copied ? (
                <Check className="h-4 w-4 text-green-500" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
            </button>

            <Popover>
              <PopoverTrigger asChild>
                <button className="h-9 w-9 rounded-lg flex items-center justify-center hover:bg-muted transition-colors">
                  <Share2 className="h-4 w-4" />
                </button>
              </PopoverTrigger>
              <PopoverContent>
                <div className="grid gap-4">
                  <div className="space-y-2">
                    <h4 className="font-medium leading-none">Share Canvas</h4>
                    <p className="text-sm text-muted-foreground">
                      Export or share your current design.
                    </p>
                  </div>
                  <div className="grid gap-2">
                    <div className="grid grid-cols-3 items-center gap-4">
                      <button
                        onClick={handleShareCanvas}
                        className="w-full text-left text-sm hover:underline flex items-center justify-between col-span-3"
                      >
                        <span>Share Link</span>
                        <Kbd>⌘S</Kbd>
                      </button>
                    </div>
                    <Separator />
                    <div className="grid grid-cols-3 items-center gap-4">
                      <button
                        onClick={handleDownloadCanvas}
                        className="w-full text-left text-sm hover:underline flex items-center justify-between col-span-3"
                      >
                        <span>Download JSON</span>
                        <Kbd>⌘D</Kbd>
                      </button>
                    </div>
                  </div>
                </div>
              </PopoverContent>
            </Popover>

            <button
              onClick={handleDownloadCanvas}
              title="Download"
              className="h-9 w-9 rounded-lg flex items-center justify-center hover:bg-muted transition-colors"
            >
              <Download className="h-4 w-4" />
            </button>
          </div>

          <Separator orientation="vertical" className="h-6" />

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

      <ResizablePanelGroup direction="horizontal">
        {/* Left Toolbar */}
        <ResizablePanel
          defaultSize={4}
          minSize={4}
          maxSize={4}
          className="min-w-[50px] border-r border-border/40 bg-muted/5 flex flex-col items-center py-4 gap-4"
        >
          <ToggleGroup
            type="single"
            value={tool}
            onValueChange={(val) => {
              if (val) {
                setTool(val as any);
                if (val !== 'select' && val !== 'image')
                  addElement(
                    val === 'rectangle' || val === 'circle'
                      ? 'shape'
                      : (val as any),
                    val === 'rectangle' || val === 'circle' ? val : undefined
                  );
              }
            }}
            orientation="vertical"
            className="flex flex-col gap-2"
          >
            <ToggleGroupItem value="text" aria-label="Text" title="Text (T)">
              <div className="flex flex-col items-center gap-0.5">
                <Type className="h-4 w-4" />
              </div>
            </ToggleGroupItem>
            <ToggleGroupItem
              value="rectangle"
              aria-label="Rectangle"
              title="Rectangle (R)"
            >
              <div className="flex flex-col items-center gap-0.5">
                <Square className="h-4 w-4" />
              </div>
            </ToggleGroupItem>
            <ToggleGroupItem
              value="circle"
              aria-label="Circle"
              title="Circle (C)"
            >
              <div className="flex flex-col items-center gap-0.5">
                <Circle className="h-4 w-4" />
              </div>
            </ToggleGroupItem>
            <ToggleGroupItem value="image" aria-label="Image" title="Image (I)">
              <div className="flex flex-col items-center gap-0.5">
                <ImageIcon className="h-4 w-4" />
              </div>
            </ToggleGroupItem>
          </ToggleGroup>
          <div className="flex-1" />
          <button
            onClick={() =>
              setActivePanel(activePanel === 'layers' ? null : 'layers')
            }
            className={cn(
              'p-2 rounded-md transition-colors',
              activePanel === 'layers'
                ? 'bg-muted text-foreground'
                : 'text-muted-foreground hover:bg-muted/50'
            )}
            title="Layers (L)"
          >
            <Clock className="h-5 w-5" />
          </button>
        </ResizablePanel>

        <ResizableHandle />

        {/* Main Canvas */}
        <ResizablePanel defaultSize={80}>
          <div className="flex-1 overflow-auto bg-muted/30 p-8 h-full flex items-center justify-center">
            <div
              ref={canvasRef}
              className="relative shadow-lg rounded-lg overflow-hidden transition-all duration-200"
              style={{
                width: canvasData.width * zoom,
                height: canvasData.height * zoom,
                backgroundColor: canvasData.background,
                transform: `scale(${zoom})`, // Still stick with scale for zoom but container handles overflow
                transformOrigin: 'center center',
              }}
              onClick={(e) => {
                if (e.target === canvasRef.current) {
                  setSelectedId(null);
                }
              }}
            >
              {canvasData.elements.map((element) => (
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
        </ResizablePanel>

        {/* Right Panels (Intelligence & Context) */}
        <ResizableHandle />

        <ResizablePanel
          defaultSize={20}
          minSize={15}
          maxSize={30}
          collapsible={true}
          collapsedSize={4}
        >
          <div className="h-full flex flex-row">
            {/* Right Toolbar Strip */}
            <div className="w-12 border-l border-r border-border/40 flex flex-col items-center py-4 gap-4 bg-muted/5 z-10">
              <ToggleGroup
                type="single"
                value={activePanel || ''}
                onValueChange={(val) => setActivePanel(val as any)}
                orientation="vertical"
                className="flex flex-col gap-2"
              >
                <ToggleGroupItem value="smart-crop">
                  <Maximize2 className="h-4 w-4" />
                </ToggleGroupItem>
                <ToggleGroupItem value="captions">
                  <MessageCircle className="h-4 w-4" />
                </ToggleGroupItem>
                <ToggleGroupItem value="animate">
                  <Sparkles className="h-4 w-4" />
                </ToggleGroupItem>
              </ToggleGroup>
            </div>

            {/* Panel Content */}
            <div className="flex-1 bg-card overflow-hidden flex flex-col">
              {activePanel && (
                <>
                  <div className="p-4 border-b border-border/40 flex items-center justify-between bg-muted/5">
                    <TypographySmall className="uppercase tracking-wider text-muted-foreground">
                      {activePanel === 'layers' && 'Layers'}
                      {activePanel === 'smart-crop' && 'Canvas Resize'}
                      {activePanel === 'captions' && 'AI Captions'}
                      {activePanel === 'animate' && 'Motion Presets'}
                    </TypographySmall>
                    <button onClick={() => setActivePanel(null)}>
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                  <div className="flex-1 overflow-auto p-4">
                    {activePanel === 'layers' && (
                      <div className="space-y-1">
                        {[...canvasData.elements].reverse().map((element) => (
                          <LayerItem
                            key={element.id}
                            element={element}
                            isSelected={selectedId === element.id}
                            onSelect={() => setSelectedId(element.id)}
                            onToggleVisibility={() =>
                              toggleVisibility(element.id)
                            }
                            onToggleLock={() => toggleLock(element.id)}
                            onMoveUp={() => moveElement(element.id, 'up')}
                            onMoveDown={() => moveElement(element.id, 'down')}
                            onDuplicate={() => duplicateElement(element.id)}
                            onDelete={() => deleteElement(element.id)}
                          />
                        ))}
                        {canvasData.elements.length === 0 && (
                          <Alert variant="default" className="mt-4 bg-muted/30">
                            <AlertTitle>Canvas is empty</AlertTitle>
                            <AlertDescription>
                              Use the toolbar to add elements.
                            </AlertDescription>
                          </Alert>
                        )}
                      </div>
                    )}
                    {activePanel === 'smart-crop' && (
                      <SmartCropPresets
                        onSelect={(preset) => {
                          const { width, height } = preset;
                          if (width && height) {
                            setCanvasData((prev) => ({
                              ...prev,
                              width,
                              height,
                            }));
                          }
                        }}
                      />
                    )}
                    {activePanel === 'captions' && (
                      <CaptionSuggestions
                        onSelect={(text) => {
                          addElement('text');
                          // Note: Ideally we'd pass text to addElement or update the last added element
                        }}
                      />
                    )}
                    {activePanel === 'animate' &&
                      (selectedId ? (
                        <AnimationPresets
                          selectedAnimation={selectedElement?.animation}
                          onSelect={(anim) => {
                            setCanvasData((prev) => ({
                              ...prev,
                              elements: prev.elements.map((e) =>
                                e.id === selectedId
                                  ? { ...e, animation: anim }
                                  : e
                              ),
                            }));
                          }}
                        />
                      ) : (
                        <div className="text-center py-12 text-muted-foreground">
                          <Sparkles className="h-8 w-8 mx-auto mb-3 opacity-30" />
                          <TypographyMuted>
                            Select an element to animate
                          </TypographyMuted>
                        </div>
                      ))}
                  </div>
                </>
              )}
            </div>
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
}

function CanvasElementComponent({
  element,
  isSelected,
  onSelect,
  zoom,
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
    ...(element.style as React.CSSProperties),
    cursor: element.locked ? 'not-allowed' : 'move',
  };

  const getAnimationClass = () => {
    switch (element.animation) {
      case 'fade':
        return 'animate-in fade-in duration-1000';
      case 'slide-up':
        return 'animate-in slide-in-from-bottom-10 fade-in duration-1000';
      case 'scale':
        return 'animate-in zoom-in duration-1000';
      case 'breathe':
        return 'animate-pulse';
      default:
        return '';
    }
  };

  return (
    <div
      onClick={(e) => {
        e.stopPropagation();
        onSelect();
      }}
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
      {element.type === 'shape' && <div className="w-full h-full" />}
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
  primary,
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
          ? primary
            ? 'bg-foreground text-background shadow-lg shadow-foreground/10'
            : 'bg-background text-foreground shadow-sm ring-1 ring-border'
          : primary
            ? 'text-muted-foreground hover:text-foreground hover:bg-muted'
            : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
      )}
    >
      <Icon
        className={cn(
          'h-5 w-5',
          active && 'animate-in zoom-in-75 duration-300'
        )}
      />
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
  onDelete,
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
  const Icon =
    element.type === 'text'
      ? Type
      : element.type === 'image'
        ? ImageIcon
        : Square;

  return (
    <div
      onClick={onSelect}
      className={cn(
        'group flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors',
        isSelected ? 'bg-muted' : 'hover:bg-muted/50'
      )}
    >
      <Icon className="h-4 w-4 text-muted-foreground shrink-0" />
      <span
        className={cn(
          'flex-1 text-sm truncate',
          !element.visible && 'text-muted-foreground/50'
        )}
      >
        {element.type === 'text'
          ? element.content.substring(0, 15)
          : element.type}
      </span>

      <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onToggleVisibility();
          }}
          className="p-1 rounded hover:bg-background"
        >
          {element.visible ? (
            <Eye className="h-3 w-3" />
          ) : (
            <EyeOff className="h-3 w-3" />
          )}
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onToggleLock();
          }}
          className="p-1 rounded hover:bg-background"
        >
          {element.locked ? (
            <Lock className="h-3 w-3" />
          ) : (
            <Unlock className="h-3 w-3" />
          )}
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          className="p-1 rounded hover:bg-background text-red-500"
        >
          <Trash2 className="h-3 w-3" />
        </button>
      </div>
    </div>
  );
}
