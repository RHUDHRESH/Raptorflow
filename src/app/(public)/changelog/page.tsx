"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Card } from "@/components/raptor/ui/Card";
import { Button } from "@/components/raptor/ui/Button";
import { 
  GitCommit, 
  Sparkles, 
  Bug, 
  Zap,
  Shield,
  Rocket,
  ChevronDown,
  Calendar,
  Hash,
  ArrowRight,
  Download,
  Bell
} from "lucide-react";

gsap.registerPlugin(ScrollTrigger);

// ═══════════════════════════════════════════════════════════════════════════════
// CHANGELOG — Radical Timeline Experience
// Vertical timeline with scroll-triggered animations
// ═══════════════════════════════════════════════════════════════════════════════

type ChangeType = "feature" | "improvement" | "bugfix" | "security";

interface Change {
  type: ChangeType;
  title: string;
  description: string;
  highlight?: boolean;
}

interface Release {
  version: string;
  date: string;
  status: "current" | "previous" | "legacy";
  summary?: string;
  changes: Change[];
}

const RELEASES: Release[] = [
  {
    version: "1.0.0-beta",
    date: "February 2025",
    status: "current",
    summary: "Public beta launch with full Foundation, Moves, and Muse capabilities.",
    changes: [
      {
        type: "feature",
        title: "Public Beta Launch",
        description: "RaptorFlow is now available in public beta. Create workspaces, build foundations, and start executing strategic moves.",
        highlight: true,
      },
      {
        type: "feature",
        title: "Foundation Module",
        description: "Build your marketing ground truth with positioning statements, Rich ICPs, and core messaging. Lock versions to preserve strategic decisions.",
        highlight: true,
      },
      {
        type: "feature",
        title: "Strategic Moves",
        description: "Create and execute 14-day marketing sprints across 5 categories: Ignite, Capture, Authority, Repair, Rally.",
        highlight: true,
      },
      {
        type: "feature",
        title: "Muse AI Assistant",
        description: "Context-aware AI that understands your foundation and provides pull-based suggestions. Never publishes without approval.",
        highlight: true,
      },
      {
        type: "feature",
        title: "Campaign Management",
        description: "Link moves to campaigns, track outcomes, and collaborate with your team.",
      },
      {
        type: "feature",
        title: "BCM (Business Context Manifest)",
        description: "Synthesized representation of your entire marketing foundation for AI consistency.",
      },
      {
        type: "improvement",
        title: "Charcoal/Ivory Design System",
        description: "Refined visual design with focus on clarity and reduced cognitive load.",
      },
      {
        type: "security",
        title: "SOC 2 Type II Compliance",
        description: "Achieved SOC 2 Type II certification for enterprise security.",
      },
    ],
  },
  {
    version: "0.9.0",
    date: "January 2025",
    status: "previous",
    summary: "Private beta with core infrastructure and early access features.",
    changes: [
      {
        type: "feature",
        title: "Private Beta",
        description: "Initial private beta release for early adopters and design partners.",
        highlight: true,
      },
      {
        type: "feature",
        title: "Move Execution Engine",
        description: "Backend infrastructure for 14-day sprint execution.",
      },
      {
        type: "improvement",
        title: "UI Polish",
        description: "Refined the Charcoal/Ivory design system for better readability and focus.",
      },
      {
        type: "improvement",
        title: "Performance Optimization",
        description: "Reduced initial load time by 40% through code splitting and lazy loading.",
      },
    ],
  },
];

const TYPE_CONFIG: Record<ChangeType, { icon: typeof Sparkles; color: string; bg: string; label: string }> = {
  feature: {
    icon: Sparkles,
    color: "#3D5A42",
    bg: "#3D5A4220",
    label: "Feature",
  },
  improvement: {
    icon: Zap,
    color: "#3D5A6B",
    bg: "#3D5A6B20",
    label: "Improvement",
  },
  bugfix: {
    icon: Bug,
    color: "#8B6914",
    bg: "#8B691420",
    label: "Bugfix",
  },
  security: {
    icon: Shield,
    color: "#6B3D5A",
    bg: "#6B3D5A20",
    label: "Security",
  },
};

export default function ChangelogPage() {
  const pageRef = useRef<HTMLDivElement>(null);
  const [expandedReleases, setExpandedReleases] = useState<string[]>(["1.0.0-beta"]);
  const [filter, setFilter] = useState<ChangeType | "all">("all");

  const toggleRelease = (version: string) => {
    setExpandedReleases((prev) =>
      prev.includes(version)
        ? prev.filter((v) => v !== version)
        : [...prev, version]
    );
  };

  const getFilteredChanges = (changes: Change[]) => {
    if (filter === "all") return changes;
    return changes.filter((c) => c.type === filter);
  };

  useEffect(() => {
    if (!pageRef.current) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        ".changelog-header",
        { y: 40, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.8, ease: "power3.out" }
      );
    }, pageRef);

    return () => ctx.revert();
  }, []);

  return (
    <div ref={pageRef} className="max-w-4xl mx-auto px-6 pb-24 pt-8">
      {/* Header */}
      <div className="changelog-header text-center mb-12">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-[var(--bg-canvas)] rounded-full mb-6">
          <Rocket size={16} className="text-[var(--ink-2)]" />
          <span className="rf-mono-xs text-[var(--ink-2)] uppercase tracking-wider">
            Product Updates
          </span>
        </div>
        <h1 className="rf-display mb-4">Changelog</h1>
        <p className="rf-body-lg text-[var(--ink-2)] max-w-xl mx-auto mb-6">
          Track new features, improvements, and bug fixes as we build RaptorFlow.
        </p>
        <Button variant="secondary" leftIcon={<Bell size={16} />}>
          Subscribe to Updates
        </Button>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center justify-center gap-2 mb-12">
        <button
          onClick={() => setFilter("all")}
          className={`px-4 py-2 rounded-full rf-body-sm transition-all ${
            filter === "all"
              ? "bg-[var(--ink-1)] text-white"
              : "bg-[var(--bg-canvas)] text-[var(--ink-2)] hover:bg-[var(--border-1)]"
          }`}
        >
          All Updates
        </button>
        {(Object.keys(TYPE_CONFIG) as ChangeType[]).map((type) => {
          const config = TYPE_CONFIG[type];
          const Icon = config.icon;
          return (
            <button
              key={type}
              onClick={() => setFilter(type)}
              className={`px-4 py-2 rounded-full rf-body-sm transition-all flex items-center gap-2 ${
                filter === type
                  ? "bg-[var(--ink-1)] text-white"
                  : "bg-[var(--bg-canvas)] text-[var(--ink-2)] hover:bg-[var(--border-1)]"
              }`}
            >
              <Icon size={14} />
              {config.label}
            </button>
          );
        })}
      </div>

      {/* Releases */}
      <div className="space-y-8">
        {RELEASES.map((release) => {
          const isExpanded = expandedReleases.includes(release.version);
          const filteredChanges = getFilteredChanges(release.changes);

          if (filteredChanges.length === 0 && filter !== "all") return null;

          return (
            <Card key={release.version} padding="md">
              <button
                onClick={() => toggleRelease(release.version)}
                className="w-full flex items-start justify-between text-left"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <Hash size={14} />
                    <span className="rf-mono-sm font-semibold">{release.version}</span>
                    {release.status === "current" && (
                      <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">
                        Current
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2 text-[var(--ink-3)] mb-2">
                    <Calendar size={14} />
                    <span className="rf-mono-xs">{release.date}</span>
                  </div>
                  {release.summary && (
                    <p className="rf-body-sm text-[var(--ink-2)]">{release.summary}</p>
                  )}
                </div>
                <ChevronDown
                  size={20}
                  className={`text-[var(--ink-3)] transition-transform ${isExpanded ? "rotate-180" : ""}`}
                />
              </button>

              {isExpanded && (
                <>
                  <div className="h-px bg-[var(--border-1)] my-4" />
                  <div className="space-y-4">
                    {filteredChanges.map((change, idx) => {
                      const config = TYPE_CONFIG[change.type];
                      const Icon = config.icon;

                      return (
                        <div key={idx} className="flex gap-4 p-4 rounded-lg hover:bg-[var(--bg-canvas)]">
                          <div
                            className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                            style={{ backgroundColor: config.bg }}
                          >
                            <Icon size={18} style={{ color: config.color }} />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <h3 className="rf-body font-semibold">{change.title}</h3>
                              {change.highlight && <Sparkles size={14} className="text-amber-500" />}
                            </div>
                            <p className="rf-body-sm text-[var(--ink-2)]">{change.description}</p>
                          </div>
                          <span
                            className="rf-mono-xs px-2 py-1 rounded flex-shrink-0"
                            style={{ backgroundColor: config.bg, color: config.color }}
                          >
                            {config.label}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </>
              )}
            </Card>
          );
        })}
      </div>

      {/* End of Timeline */}
      <div className="mt-16 text-center">
        <div className="inline-flex items-center gap-3 px-6 py-3 bg-[var(--bg-canvas)] rounded-full">
          <GitCommit size={16} className="text-[var(--ink-3)]" />
          <span className="rf-mono-xs text-[var(--ink-3)]">Development started November 2024</span>
        </div>
      </div>
    </div>
  );
}
