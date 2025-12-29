'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Stage, Layer, Text, Rect, Transformer } from 'react-konva';
import { useIsMobile } from '@/hooks/use-mobile';

interface CanvasElement {
  id: string;
  type: 'text' | 'image' | 'rect';
  x: number;
  y: number;
  text?: string;
  fontSize?: number;
  fill?: string;
  width?: number;
  height?: number;
}

interface MemeCanvasProps {
  initialElements: CanvasElement[];
  onSave: (elements: CanvasElement[]) => void;
}

const Element = ({ shapeProps, isSelected, onSelect, onChange }: any) => {
  const shapeRef = useRef<any>(null);
  const trRef = useRef<any>(null);

  useEffect(() => {
    if (isSelected) {
      trRef.current.nodes([shapeRef.current]);
      trRef.current.getLayer().batchDraw();
    }
  }, [isSelected]);

  return (
    <React.Fragment>
      {shapeProps.type === 'text' && (
        <Text
          onClick={onSelect}
          onTap={onSelect}
          ref={shapeRef}
          {...shapeProps}
          draggable
          onDragEnd={(e) => {
            onChange({
              ...shapeProps,
              x: e.target.x(),
              y: e.target.y(),
            });
          }}
          onTransformEnd={() => {
            const node = shapeRef.current;
            const scaleX = node.scaleX();
            const scaleY = node.scaleY();
            node.scaleX(1);
            node.scaleY(1);
            onChange({
              ...shapeProps,
              x: node.x(),
              y: node.y(),
              fontSize: node.fontSize() * Math.max(scaleX, scaleY),
            });
          }}
        />
      )}
      {isSelected && (
        <Transformer
          ref={trRef}
          boundBoxFunc={(oldBox, newBox) => {
            if (newBox.width < 5 || newBox.height < 5) {
              return oldBox;
            }
            return newBox;
          }}
        />
      )}
    </React.Fragment>
  );
};

export function MemeCanvas({ initialElements, onSave }: MemeCanvasProps) {
  const [elements, setElements] = useState<CanvasElement[]>(initialElements);
  const [selectedId, selectShape] = useState<string | null>(null);
  const isMobile = useIsMobile();
  const size = isMobile ? 350 : 600;

  const checkDeselect = (e: any) => {
    const clickedOnEmpty = e.target === e.target.getStage();
    if (clickedOnEmpty) {
      selectShape(null);
    }
  };

  return (
    <div className="flex flex-col items-center gap-8 py-12 bg-[#0E1112] rounded-[24px] border border-[#2B3437]">
      <div className="bg-white rounded-xl overflow-hidden shadow-[0_0_50px_rgba(0,0,0,0.5)]">
        <Stage
          width={size}
          height={size}
          onMouseDown={checkDeselect}
          onTouchStart={checkDeselect}
        >
          <Layer>
            <Rect width={size} height={size} fill="#ffffff" />
            {elements.map((el, i) => (
              <Element
                key={el.id}
                shapeProps={el}
                isSelected={el.id === selectedId}
                onSelect={() => selectShape(el.id)}
                onChange={(newAttrs: any) => {
                  const els = elements.slice();
                  els[i] = newAttrs;
                  setElements(els);
                  onSave(els);
                }}
              />
            ))}
          </Layer>
        </Stage>
      </div>

      <div className="flex gap-4">
        <button
          onClick={() => onSave(elements)}
          className="px-8 py-3 bg-[#E9ECE6] text-[#0E1112] rounded-xl font-medium hover:bg-white transition-all"
        >
          Save Canvas
        </button>
      </div>
    </div>
  );
}
