'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';

// ============================================================================
// MODULE DATA
// ============================================================================

interface Module {
  id: string;
  name: string;
  description: string;
  href: string;
  icon: React.ReactNode;
  connections: string[];
}

const modules: Module[] = [
  {
    id: 'foundation',
    name: 'Foundation',
    description:
      'Build your BrandKit, positioning, and messaging architecture in one place.',
    href: '/features/foundation',
    connections: ['cohorts', 'campaigns'],
    icon: (
      <svg
        className="h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
        />
      </svg>
    ),
  },
  {
    id: 'cohorts',
    name: 'Cohorts',
    description:
      'Define and track your Ideal Customer Profiles with behavioral segmentation.',
    href: '/features/cohorts',
    connections: ['campaigns', 'muse'],
    icon: (
      <svg
        className="h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z"
        />
      </svg>
    ),
  },
  {
    id: 'moves',
    name: 'Moves',
    description: 'Weekly execution packets that turn strategy into action.',
    href: '/features/moves',
    connections: ['matrix', 'campaigns'],
    icon: (
      <svg
        className="h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z"
        />
      </svg>
    ),
  },
  {
    id: 'campaigns',
    name: 'Campaigns',
    description: '90-day strategic arcs that compound your marketing efforts.',
    href: '/features/campaigns',
    connections: ['moves', 'muse'],
    icon: (
      <svg
        className="h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5"
        />
      </svg>
    ),
  },
  {
    id: 'muse',
    name: 'Muse',
    description: 'AI-powered asset factory for content that actually converts.',
    href: '/features/muse',
    connections: ['cohorts', 'matrix'],
    icon: (
      <svg
        className="h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z"
        />
      </svg>
    ),
  },
  {
    id: 'matrix',
    name: 'Matrix',
    description: 'Your command center. See everything. Control everything.',
    href: '/features/matrix',
    connections: ['moves', 'blackbox', 'radar'],
    icon: (
      <svg
        className="h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z"
        />
      </svg>
    ),
  },
  {
    id: 'blackbox',
    name: 'Blackbox',
    description: 'A/B testing and experiments that prove what works.',
    href: '/features/blackbox',
    connections: ['matrix', 'foundation'],
    icon: (
      <svg
        className="h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5"
        />
      </svg>
    ),
  },
  {
    id: 'radar',
    name: 'Radar',
    description: 'Competitor intelligence that keeps you three moves ahead.',
    href: '/features/radar',
    connections: ['matrix', 'foundation'],
    icon: (
      <svg
        className="h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M7.5 3.75H6A2.25 2.25 0 003.75 6v1.5M16.5 3.75H18A2.25 2.25 0 0120.25 6v1.5m0 9V18A2.25 2.25 0 0118 20.25h-1.5m-9 0H6A2.25 2.25 0 013.75 18v-1.5M15 12a3 3 0 11-6 0 3 3 0 016 0z"
        />
      </svg>
    ),
  },
];

// Connection definitions
const connectionPairs: [string, string][] = [
  ['foundation', 'cohorts'],
  ['foundation', 'campaigns'],
  ['cohorts', 'campaigns'],
  ['cohorts', 'muse'],
  ['campaigns', 'moves'],
  ['campaigns', 'muse'],
  ['moves', 'matrix'],
  ['muse', 'matrix'],
  ['matrix', 'blackbox'],
  ['matrix', 'radar'],
  ['blackbox', 'foundation'],
  ['radar', 'foundation'],
];

// ============================================================================
// HOOKS
// ============================================================================

function useIntersectionObserver(threshold = 0.2) {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [threshold]);

  return { ref, isVisible };
}

// ============================================================================
// CONNECTION LINES COMPONENT
// ============================================================================

function ConnectionLines({
  hoveredModule,
  containerRef,
}: {
  hoveredModule: string | null;
  containerRef: React.RefObject<HTMLDivElement | null>;
}) {
  const [positions, setPositions] = useState<
    Record<string, { x: number; y: number }>
  >({});

  useEffect(() => {
    const updatePositions = () => {
      if (!containerRef.current) return;

      const containerRect = containerRef.current.getBoundingClientRect();
      const newPositions: Record<string, { x: number; y: number }> = {};

      modules.forEach((module) => {
        const element = containerRef.current?.querySelector(
          `[data-module-id="${module.id}"]`
        );
        if (element) {
          const rect = element.getBoundingClientRect();
          newPositions[module.id] = {
            x: rect.left - containerRect.left + rect.width / 2,
            y: rect.top - containerRect.top + rect.height / 2,
          };
        }
      });

      setPositions(newPositions);
    };

    updatePositions();
    window.addEventListener('resize', updatePositions);
    const timer = setTimeout(updatePositions, 100);

    return () => {
      window.removeEventListener('resize', updatePositions);
      clearTimeout(timer);
    };
  }, [containerRef]);

  return (
    <svg
      className="absolute inset-0 w-full h-full pointer-events-none"
      style={{ overflow: 'visible' }}
    >
      {connectionPairs.map(([fromId, toId]) => {
        const from = positions[fromId];
        const to = positions[toId];

        if (!from || !to) return null;

        // Check if this connection is related to hovered module
        const isHighlighted = hoveredModule
          ? hoveredModule === fromId ||
            hoveredModule === toId ||
            modules
              .find((m) => m.id === hoveredModule)
              ?.connections.includes(fromId) ||
            modules
              .find((m) => m.id === hoveredModule)
              ?.connections.includes(toId)
          : false;

        return (
          <line
            key={`${fromId}-${toId}`}
            x1={from.x}
            y1={from.y}
            x2={to.x}
            y2={to.y}
            stroke="currentColor"
            strokeWidth={isHighlighted ? 1.5 : 1}
            className={`transition-opacity duration-300 ${
              isHighlighted ? 'opacity-25' : 'opacity-[0.06]'
            }`}
          />
        );
      })}
    </svg>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function ModulesSpectacle() {
  const { ref: sectionRef, isVisible } = useIntersectionObserver(0.1);
  const containerRef = useRef<HTMLDivElement>(null);
  const [hoveredModule, setHoveredModule] = useState<string | null>(null);

  return (
    <section id="features" className="py-24 lg:py-32" ref={sectionRef}>
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        {/* Header */}
        <div
          className={`
            mx-auto max-w-2xl text-center mb-16
            transition-all duration-700
            ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}
          `}
        >
          <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
            Everything You Need
          </p>
          <h2 className="font-display text-4xl lg:text-5xl font-medium tracking-tight">
            One System. Zero Chaos.
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Not another tool. A complete marketing operating system.
          </p>
        </div>

        {/* Modules Grid */}
        <div className="relative" ref={containerRef}>
          {/* Connection Lines */}
          <ConnectionLines
            hoveredModule={hoveredModule}
            containerRef={containerRef}
          />

          {/* Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 relative">
            {modules.map((module, index) => (
              <Link
                key={module.id}
                href={module.href}
                data-module-id={module.id}
                className={`
                  group rounded-2xl border border-border bg-card p-6
                  hover:border-foreground/20 hover:-translate-y-0.5
                  transition-all duration-200
                  ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'}
                `}
                style={{
                  transitionDelay: isVisible ? `${index * 50}ms` : '0ms',
                }}
                onMouseEnter={() => setHoveredModule(module.id)}
                onMouseLeave={() => setHoveredModule(null)}
              >
                <div className="h-12 w-12 rounded-xl bg-muted flex items-center justify-center text-foreground mb-4 group-hover:bg-foreground group-hover:text-background transition-colors duration-200">
                  {module.icon}
                </div>
                <h3 className="text-lg font-semibold mb-2">{module.name}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {module.description}
                </p>
              </Link>
            ))}
          </div>
        </div>

        {/* Hint */}
        <p
          className={`
            text-center text-sm text-muted-foreground mt-8
            transition-all duration-700
            ${isVisible ? 'opacity-100' : 'opacity-0'}
          `}
          style={{ transitionDelay: isVisible ? '500ms' : '0ms' }}
        >
          Hover to see how modules connect
        </p>
      </div>
    </section>
  );
}
