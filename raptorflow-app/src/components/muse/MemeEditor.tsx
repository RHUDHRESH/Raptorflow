'use client';

import React, { useState } from 'react';
import { Stage, Layer, Text, Image as KonvaImage, Rect } from 'react-konva';
import { useIsMobile } from '@/hooks/use-mobile';

interface MemeElement {
    id: string;
    type: 'text' | 'image';
    x: number;
    y: number;
    text?: string;
    fontSize?: number;
    fill?: string;
    width?: number;
    height?: number;
    src?: string;
}

interface MemeEditorProps {
    elements: MemeElement[];
    onSave: (json: string) => void;
}

export default function MemeEditor({ elements: initialElements, onSave }: MemeEditorProps) {
    const [elements, setElements] = useState<MemeElement[]>(initialElements);
    const isMobile = useIsMobile();
    const size = isMobile ? 350 : 600;

    const handleExport = () => {
        // Simple serialization
        onSave(JSON.stringify(elements));
    };

    return (
        <div className="flex flex-col items-center gap-6 p-8 bg-card rounded-2xl border border-border/60">
            <div className="shadow-2xl rounded-lg overflow-hidden border border-zinc-200">
                <Stage width={size} height={size}>
                    <Layer>
                        <Rect width={size} height={size} fill="#ffffff" />
                        {elements.map((el) => (
                            <React.Fragment key={el.id}>
                                {el.type === 'text' && (
                                    <Text
                                        text={el.text}
                                        x={el.x}
                                        y={el.y}
                                        fontSize={el.fontSize || 40}
                                        fill={el.fill || '#000000'}
                                        draggable
                                        fontFamily="Inter"
                                        align="center"
                                        width={size - 40}
                                    />
                                )}
                            </React.Fragment>
                        ))}
                    </Layer>
                </Stage>
            </div>

            <button
                onClick={handleExport}
                className="px-8 py-3 bg-zinc-900 text-white rounded-xl hover:bg-zinc-800 transition-all"
            >
                Export Meme
            </button>
        </div>
    );
}
