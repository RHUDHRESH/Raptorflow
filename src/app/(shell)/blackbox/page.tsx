"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { Layout } from "@/components/raptor/shell/Layout";
import { Card } from "@/components/raptor/ui/Card";
import { Button } from "@/components/raptor/ui/Button";
import {
  GitCommit,
  Lock,
  Unlock,
  Lightbulb,
  Edit3,
  Calendar,
  Filter,
  ChevronDown,
  ChevronUp,
  X,
  Clock,
  User,
  ArrowRight,
  Layers,
} from "lucide-react";

// ═══════════════════════════════════════════════════════════════════════════════
// BLACKBOX PAGE — Decision Log and Change History
// "Records what changed, why it changed, what it affected"
// ═══════════════════════════════════════════════════════════════════════════════

type EntryType = "decision" | "change" | "assumption" | "lock" | "unlock";

interface BlackboxEntry {
  id: string;
  type: EntryType;
  timestamp: Date;
  user: string;
  module: string;
  entity: string;
  action: string;
  reason: string;
  impact: string[];
  diff?: {
    before: string;
    after: string;
  };
}

// Mock Data
const mockBlackbox: BlackboxEntry[] = [
  {
    id: "entry-1",
    type: "decision",
    timestamp: new Date("2024-01-15T14:30:00"),
    user: "Sarah Chen",
    module: "Moves",
    entity: "Enterprise Trial Flow",
    action: "Rescheduled from Q2 to Q1",
    reason: "Customer feedback showed urgency for enterprise features",
    impact: [
      "Campaign 'Trial Opt' rescheduled to Feb 1",
      "Move 'Q1 Content' scope reduced by 20%",
    ],
    diff: {
      before: "Q2 2024 (April 1 - June 30)",
      after: "Q1 2024 (February 1 - March 15)",
    },
  },
  {
    id: "entry-2",
    type: "lock",
    timestamp: new Date("2024-01-14T09:15:00"),
    user: "Mike Ross",
    module: "Foundation",
    entity: "Positioning",
    action: "Locked Positioning",
    reason: "Team alignment achieved after workshop",
    impact: ["Campaign generation enabled", "Messaging now read-only"],
  },
  {
    id: "entry-3",
    type: "assumption",
    timestamp: new Date("2024-01-13T16:45:00"),
    user: "System",
    module: "Foundation",
    entity: "ICP: Enterprise Operations",
    action: "Validated assumption",
    reason: "3 customer interviews confirmed pain point",
    impact: ["Confidence score increased to 85%"],
  },
  {
    id: "entry-4",
    type: "change",
    timestamp: new Date("2024-01-12T11:20:00"),
    user: "Alex Kim",
    module: "Campaigns",
    entity: "Email Nurture Sequence",
    action: "Updated subject lines",
    reason: "A/B test results showed 40% higher open rates",
    impact: ["Open rate projected to increase from 22% to 31%"],
    diff: {
      before: "Old: 'Updates from our team'",
      after: "New: 'The workflow mistake costing you 10hrs/week'",
    },
  },
  {
    id: "entry-5",
    type: "decision",
    timestamp: new Date("2024-01-11T10:00:00"),
    user: "Jordan Lee",
    module: "Moves",
    entity: "Q1 Content Strategy",
    action: "Added new pillar: 'AI Integration'",
    reason: "Market research showed high demand for AI content",
    impact: [
      "3 new blog posts added to calendar",
      "1 webinar rescheduled",
    ],
  },
  {
    id: "entry-6",
    type: "unlock",
    timestamp: new Date("2024-01-10T14:30:00"),
    user: "Taylor Swift",
    module: "Foundation",
    entity: "Messaging Framework",
    action: "Unlocked for editing",
    reason: "New product features require messaging updates",
    impact: ["Campaign generation paused until re-lock"],
  },
];

// Type configuration
const typeConfig: Record<EntryType | "unlock", { icon: React.ElementType; label: string; color: string; bg: string }> = {
  decision: {
    icon: GitCommit,
    label: "Decision",
    color: "text-[var(--status-info)]",
    bg: "bg-[var(--status-info-bg)]",
  },
  change: {
    icon: Edit3,
    label: "Change",
    color: "text-[var(--status-warning)]",
    bg: "bg-[var(--status-warning-bg)]",
  },
  assumption: {
    icon: Lightbulb,
    label: "Assumption",
    color: "text-[var(--status-success)]",
    bg: "bg-[var(--status-success-bg)]",
  },
  lock: {
    icon: Lock,
    label: "Lock",
    color: "text-[var(--ink-1)]",
    bg: "bg-[var(--bg-canvas)]",
  },
  unlock: {
    icon: Unlock,
    label: "Unlock",
    color: "text-[var(--status-error)]",
    bg: "bg-[var(--status-error-bg)]",
  },
};

// Format date
function formatDate(date: Date): string {
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
  });
}

// Entry Card Component
function EntryCard({
  entry,
  isExpanded,
  onToggle,
}: {
  entry: BlackboxEntry;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  
  const config = typeConfig[entry.type];
  const TypeIcon = config.icon;

  return (
    <Card
      className={`timeline-entry relative overflow-visible ${isExpanded ? "ring-1 ring-[var(--border-2)]" : ""}`}
    >
      {/* Timeline connector */}
      <div className="absolute -left-8 top-6 w-6 h-px bg-[var(--border-1)] hidden lg:block" />
      <div className="absolute -left-[39px] top-4 w-5 h-5 rounded-full bg-[var(--bg-surface)] border-2 border-[var(--border-1)] hidden lg:flex items-center justify-center">
        <div className={`w-2 h-2 rounded-full ${config.bg.replace("bg-", "bg-")}`} />
      </div>

      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 rounded-[var(--radius-sm)] ${config.bg} flex items-center justify-center`}>
            <TypeIcon size={16} className={config.color} />
          </div>
          <div>
            <span className={`rf-mono-xs font-semibold uppercase ${config.color}`}>
              {config.label}
            </span>
            <div className="flex items-center gap-2 text-[var(--ink-3)] rf-body-sm mt-0.5">
              <Calendar size={12} />
              <span>{formatDate(entry.timestamp)} at {formatTime(entry.timestamp)}</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="rf-tag">
            <Layers size={12} />
            {entry.module}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="space-y-3">
        <div>
          <h3 className="rf-h4">{entry.action}</h3>
          <p className="rf-body-sm text-[var(--ink-2)] mt-1">{entry.entity}</p>
        </div>

        {/* Reason */}
        <div className="flex items-start gap-2 p-3 bg-[var(--bg-canvas)] rounded-[var(--radius-sm)]">
          <span className="rf-mono-xs text-[var(--ink-3)] uppercase">Why:</span>
          <p className="rf-body-sm text-[var(--ink-2)] italic">&ldquo;{entry.reason}&rdquo;</p>
        </div>

        {/* Impact */}
        {entry.impact.length > 0 && (
          <div className="space-y-2">
            <span className="rf-mono-xs text-[var(--ink-3)] uppercase">Impact:</span>
            <ul className="space-y-1">
              {entry.impact.map((item, i) => (
                <li key={i} className="flex items-start gap-2 rf-body-sm text-[var(--ink-2)]">
                  <span className="text-[var(--ink-3)] mt-1">•</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Diff Viewer */}
        {entry.diff && (
          <div className="mt-4">
            <button
              onClick={onToggle}
              className="flex items-center gap-2 text-[var(--ink-2)] hover:text-[var(--ink-1)] transition-colors"
            >
              <span className="rf-mono-xs uppercase">View Diff</span>
              {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>

            {isExpanded && (
              <div className="mt-3 p-4 bg-[var(--bg-canvas)] rounded-[var(--radius-sm)] space-y-3">
                <div className="flex items-start gap-3">
                  <span className="rf-mono-xs text-[var(--status-error)] uppercase w-12 flex-shrink-0">Before</span>
                  <p className="rf-body-sm text-[var(--ink-2)] line-through">{entry.diff.before}</p>
                </div>
                <div className="flex items-start gap-3">
                  <span className="rf-mono-xs text-[var(--status-success)] uppercase w-12 flex-shrink-0">After</span>
                  <p className="rf-body-sm text-[var(--ink-1)]">{entry.diff.after}</p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="mt-4 pt-3 border-t border-[var(--border-1)] flex items-center justify-between">
        <div className="flex items-center gap-2 text-[var(--ink-3)] rf-body-sm">
          <User size={14} />
          <span>by {entry.user}</span>
        </div>
        <Button variant="tertiary" size="sm">
          Details
          <ArrowRight size={14} />
        </Button>
      </div>
    </Card>
  );
}

// Main Blackbox Page
export default function BlackboxPage() {
  const pageRef = useRef<HTMLDivElement>(null);
  const [expandedEntry, setExpandedEntry] = useState<string | null>(null);
  const [typeFilter, setTypeFilter] = useState<EntryType | "all">("all");
  const [moduleFilter, setModuleFilter] = useState<string>("all");
  const [showFilters, setShowFilters] = useState(false);

  // Filter entries
  const filteredEntries = mockBlackbox.filter((entry) => {
    const typeMatch = typeFilter === "all" || entry.type === typeFilter;
    const moduleMatch = moduleFilter === "all" || entry.module === moduleFilter;
    return typeMatch && moduleMatch;
  });

  // GSAP Entrance Animation
  useEffect(() => {
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: "power2.out" } });

      // Header entrance
      tl.fromTo(
        ".blackbox-header",
        { y: -20, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.5 }
      );

      // Filter bar
      tl.fromTo(
        ".filter-bar",
        { y: -10, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.3 },
        "-=0.2"
      );

      // Timeline entries stagger
      tl.fromTo(
        ".timeline-entry",
        { y: 30, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.4, stagger: 0.1 },
        "-=0.1"
      );
    }, pageRef);

    return () => ctx.revert();
  }, [typeFilter, moduleFilter]);

  const modules = ["all", ...Array.from(new Set(mockBlackbox.map((e) => e.module)))];
  const entryTypes: (EntryType | "all")[] = ["all", "decision", "change", "assumption", "lock"];

  return (
    <Layout mode="live" activeNavItem="blackbox">
      <div ref={pageRef} className="h-full overflow-y-auto">
        <div className="max-w-[900px] mx-auto p-6 pb-12">
          {/* Header */}
          <header className="blackbox-header mb-6">
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
              <div>
                <h1 className="rf-h2 mb-1">Blackbox</h1>
                <p className="rf-body text-[var(--ink-2)]">
                  Decision log and change history
                </p>
              </div>
              <div className="flex items-center gap-3">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setShowFilters(!showFilters)}
                >
                  <Filter size={14} />
                  Filters
                </Button>
                <Button variant="primary" size="sm">Export Log</Button>
              </div>
            </div>
          </header>

          {/* Filters */}
          {showFilters && (
            <div className="filter-bar mb-6 p-4 bg-[var(--bg-surface)] border border-[var(--border-1)] rounded-[var(--radius-md)]">
              <div className="flex flex-wrap items-center gap-6">
                {/* Type Filter */}
                <div className="flex items-center gap-3">
                  <span className="rf-label text-[var(--ink-3)]">Type:</span>
                  <div className="flex items-center gap-2">
                    {entryTypes.map((type) => (
                      <button
                        key={type}
                        onClick={() => setTypeFilter(type)}
                        className={`px-3 py-1.5 rounded-[var(--radius-sm)] text-[12px] font-medium transition-colors ${
                          typeFilter === type
                            ? "bg-[var(--ink-1)] text-[var(--ink-inverse)]"
                            : "bg-[var(--bg-canvas)] text-[var(--ink-2)] hover:bg-[var(--state-hover)]"
                        }`}
                      >
                        {type === "all" ? "All" : type.charAt(0).toUpperCase() + type.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Module Filter */}
                <div className="flex items-center gap-3">
                  <span className="rf-label text-[var(--ink-3)]">Module:</span>
                  <select
                    value={moduleFilter}
                    onChange={(e) => setModuleFilter(e.target.value)}
                    className="h-8 px-3 bg-[var(--bg-canvas)] border border-[var(--border-1)] rounded-[var(--radius-sm)] text-[14px] text-[var(--ink-1)]"
                  >
                    {modules.map((m) => (
                      <option key={m} value={m}>
                        {m === "all" ? "All Modules" : m}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Timeline */}
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-4 top-0 bottom-0 w-px bg-[var(--border-1)] hidden lg:block" />

            {/* Entries */}
            <div className="space-y-6 pl-0 lg:pl-12">
              {filteredEntries.map((entry) => (
                <EntryCard
                  key={entry.id}
                  entry={entry}
                  isExpanded={expandedEntry === entry.id}
                  onToggle={() =>
                    setExpandedEntry(expandedEntry === entry.id ? null : entry.id)
                  }
                />
              ))}
            </div>
          </div>

          {/* Empty State */}
          {filteredEntries.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <div className="w-16 h-16 rounded-full bg-[var(--bg-surface)] flex items-center justify-center mb-4">
                <Clock size={32} className="text-[var(--ink-3)]" />
              </div>
              <h3 className="rf-h4 mb-2">No entries found</h3>
              <p className="rf-body-sm text-[var(--ink-2)]">
                Try adjusting your filters to see more results.
              </p>
            </div>
          )}

          {/* Load More */}
          {filteredEntries.length > 0 && (
            <div className="mt-8 text-center">
              <Button variant="secondary">Load More History</Button>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
