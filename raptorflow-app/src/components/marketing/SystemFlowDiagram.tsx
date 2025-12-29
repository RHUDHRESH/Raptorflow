'use client';

import { useEffect, useRef, useState } from 'react';

interface FlowNode {
  id: string;
  label: string;
  x: number;
  y: number;
  description: string;
}

const nodes: FlowNode[] = [
  {
    id: 'foundation',
    label: 'Foundation',
    x: 15,
    y: 50,
    description: 'Your BrandKit & positioning',
  },
  {
    id: 'cohorts',
    label: 'Cohorts',
    x: 30,
    y: 30,
    description: 'ICP & segmentation',
  },
  {
    id: 'campaigns',
    label: 'Campaigns',
    x: 45,
    y: 50,
    description: '90-day strategic arcs',
  },
  {
    id: 'moves',
    label: 'Moves',
    x: 60,
    y: 30,
    description: 'Weekly execution',
  },
  {
    id: 'muse',
    label: 'Muse',
    x: 60,
    y: 70,
    description: 'AI content factory',
  },
  {
    id: 'matrix',
    label: 'Matrix',
    x: 75,
    y: 50,
    description: 'Command center',
  },
  {
    id: 'blackbox',
    label: 'Blackbox',
    x: 90,
    y: 30,
    description: 'A/B experiments',
  },
  {
    id: 'radar',
    label: 'Radar',
    x: 90,
    y: 70,
    description: 'Competitor intel',
  },
];

const connections: [string, string][] = [
  ['foundation', 'cohorts'],
  ['foundation', 'campaigns'],
  ['cohorts', 'campaigns'],
  ['campaigns', 'moves'],
  ['campaigns', 'muse'],
  ['moves', 'matrix'],
  ['muse', 'matrix'],
  ['matrix', 'blackbox'],
  ['matrix', 'radar'],
  ['blackbox', 'foundation'],
  ['radar', 'foundation'],
];

export function SystemFlowDiagram() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.offsetWidth,
          height: containerRef.current.offsetHeight,
        });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  const getNodePosition = (node: FlowNode) => ({
    x: (node.x / 100) * dimensions.width,
    y: (node.y / 100) * dimensions.height,
  });

  const getConnection = (fromId: string, toId: string) => {
    const fromNode = nodes.find((n) => n.id === fromId);
    const toNode = nodes.find((n) => n.id === toId);
    if (!fromNode || !toNode) return null;

    const from = getNodePosition(fromNode);
    const to = getNodePosition(toNode);

    return { from, to };
  };

  return (
    <div
      ref={containerRef}
      className="relative w-full h-[400px] lg:h-[500px] bg-muted/30 rounded-2xl overflow-hidden"
    >
      {/* SVG for connections */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none">
        <defs>
          <linearGradient id="flowGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="currentColor" stopOpacity="0.1" />
            <stop offset="50%" stopColor="currentColor" stopOpacity="0.4" />
            <stop offset="100%" stopColor="currentColor" stopOpacity="0.1" />
          </linearGradient>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="7"
            refX="9"
            refY="3.5"
            orient="auto"
          >
            <polygon
              points="0 0, 10 3.5, 0 7"
              fill="currentColor"
              className="opacity-30"
            />
          </marker>
        </defs>

        {connections.map(([fromId, toId]) => {
          const conn = getConnection(fromId, toId);
          if (!conn) return null;

          const isHighlighted = hoveredNode === fromId || hoveredNode === toId;

          return (
            <g key={`${fromId}-${toId}`}>
              <line
                x1={conn.from.x}
                y1={conn.from.y}
                x2={conn.to.x}
                y2={conn.to.y}
                stroke="currentColor"
                strokeWidth={isHighlighted ? 2 : 1}
                className={`transition-all duration-300 ${isHighlighted ? 'opacity-50' : 'opacity-20'}`}
                markerEnd="url(#arrowhead)"
              />
              {/* Animated particle */}
              <circle r="3" fill="currentColor" className="opacity-60">
                <animateMotion
                  dur={`${2 + Math.random() * 2}s`}
                  repeatCount="indefinite"
                  path={`M${conn.from.x},${conn.from.y} L${conn.to.x},${conn.to.y}`}
                />
              </circle>
            </g>
          );
        })}
      </svg>

      {/* Nodes */}
      {nodes.map((node) => {
        const pos = getNodePosition(node);
        const isHovered = hoveredNode === node.id;

        return (
          <div
            key={node.id}
            className={`
              absolute transform -translate-x-1/2 -translate-y-1/2
              transition-all duration-300 cursor-pointer z-10
              ${isHovered ? 'scale-110' : 'scale-100'}
            `}
            style={{ left: pos.x, top: pos.y }}
            onMouseEnter={() => setHoveredNode(node.id)}
            onMouseLeave={() => setHoveredNode(null)}
          >
            <div
              className={`
                rounded-xl border-2 bg-card px-4 py-3 shadow-sm
                transition-all duration-300
                ${isHovered ? 'border-foreground shadow-lg' : 'border-border'}
              `}
            >
              <div className="font-semibold text-sm whitespace-nowrap">
                {node.label}
              </div>
              {isHovered && (
                <div className="text-xs text-muted-foreground mt-1 whitespace-nowrap">
                  {node.description}
                </div>
              )}
            </div>
          </div>
        );
      })}

      {/* Legend */}
      <div className="absolute bottom-4 left-4 text-xs text-muted-foreground">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-foreground animate-pulse" />
          <span>Data flows continuously between modules</span>
        </div>
      </div>

      {/* Feedback Loop Label */}
      <div className="absolute bottom-4 right-4 text-xs text-muted-foreground">
        <span className="px-2 py-1 rounded bg-muted">
          Feedback Loop: Learn → Improve
        </span>
      </div>
    </div>
  );
}
