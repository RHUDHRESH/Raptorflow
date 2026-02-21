"use client";

import React, { useRef, useEffect, useState } from "react";
import gsap from "gsap";
import { FileText, HelpCircle, Variable, History, Lightbulb, X, ChevronRight } from "lucide-react";

type TabId = "evidence" | "assumptions" | "variables" | "versions" | "why";

interface Tab {
  id: TabId;
  label: string;
  icon: React.ElementType;
}

const tabs: Tab[] = [
  { id: "evidence", label: "Evidence", icon: FileText },
  { id: "assumptions", label: "Assumptions", icon: HelpCircle },
  { id: "variables", label: "Variables", icon: Variable },
  { id: "versions", label: "Versions", icon: History },
  { id: "why", label: "Why this?", icon: Lightbulb },
];

interface RightDrawerProps {
  defaultTab?: TabId;
  onClose?: () => void;
  resizable?: boolean;
}

export function RightDrawer({
  defaultTab = "evidence",
  onClose,
  resizable = false,
}: RightDrawerProps) {
  const [activeTab, setActiveTab] = useState<TabId>(defaultTab);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [width, setWidth] = useState(400);
  const drawerRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const tabsRef = useRef<HTMLDivElement>(null);
  const resizeRef = useRef<HTMLDivElement>(null);
  const isDragging = useRef(false);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Initial state
      gsap.set(drawerRef.current, {
        x: 50,
        opacity: 0,
      });

      gsap.set(contentRef.current?.children || [], {
        y: 20,
        opacity: 0,
      });

      // Entrance animation
      gsap.to(drawerRef.current, {
        x: 0,
        opacity: 1,
        duration: 0.4,
        ease: "power2.out",
      });

      gsap.to(contentRef.current?.children || [], {
        y: 0,
        opacity: 1,
        duration: 0.3,
        ease: "power2.out",
        stagger: 0.05,
        delay: 0.2,
      });
    }, drawerRef);

    return () => ctx.revert();
  }, []);

  // Tab change animation
  useEffect(() => {
    if (contentRef.current) {
      gsap.fromTo(
        contentRef.current,
        { opacity: 0.7, y: 5 },
        {
          opacity: 1,
          y: 0,
          duration: 0.2,
          ease: "power2.out",
        }
      );
    }
  }, [activeTab]);

  // Resize handlers
  useEffect(() => {
    if (!resizable) return;

    const handleMouseDown = (e: MouseEvent) => {
      isDragging.current = true;
      document.body.style.cursor = "ew-resize";
      document.body.style.userSelect = "none";
    };

    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging.current) return;
      const newWidth = Math.max(300, Math.min(600, window.innerWidth - e.clientX));
      setWidth(newWidth);
    };

    const handleMouseUp = () => {
      isDragging.current = false;
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };

    const resizeHandle = resizeRef.current;
    if (resizeHandle) {
      resizeHandle.addEventListener("mousedown", handleMouseDown);
    }

    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);

    return () => {
      if (resizeHandle) {
        resizeHandle.removeEventListener("mousedown", handleMouseDown);
      }
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };
  }, [resizable]);

  const handleCollapse = () => {
    if (isCollapsed) {
      gsap.to(drawerRef.current, {
        width: width,
        duration: 0.3,
        ease: "power2.out",
        onComplete: () => setIsCollapsed(false),
      });
    } else {
      gsap.to(drawerRef.current, {
        width: 48,
        duration: 0.3,
        ease: "power2.out",
        onComplete: () => setIsCollapsed(true),
      });
    }
  };

  const handleTabClick = (tabId: TabId) => {
    if (isCollapsed) {
      setIsCollapsed(false);
      gsap.to(drawerRef.current, {
        width: width,
        duration: 0.3,
        ease: "power2.out",
      });
    }
    setActiveTab(tabId);
  };

  return (
    <aside
      ref={drawerRef}
      className="relative flex flex-col flex-shrink-0 h-full"
      style={{
        width: isCollapsed ? 48 : width,
        backgroundColor: "var(--bg-surface)",
        borderLeft: "1px solid var(--border-1)",
      }}
    >
      {/* Resize Handle */}
      {resizable && !isCollapsed && (
        <div
          ref={resizeRef}
          className="absolute left-0 top-0 bottom-0 w-1 cursor-ew-resize hover:bg-charcoal/10 z-10"
          style={{ transform: "translateX(-50%)" }}
        />
      )}

      {/* Collapse Toggle */}
      <button
        onClick={handleCollapse}
        className="absolute left-0 top-4 -translate-x-full flex items-center justify-center w-6 h-10 rounded-l-md border border-r-0 transition-colors hover:bg-surface"
        style={{
          backgroundColor: "var(--bg-surface)",
          borderColor: "var(--border-1)",
        }}
      >
        <ChevronRight
          size={14}
          style={{
            color: "var(--ink-2)",
            transform: isCollapsed ? "rotate(0deg)" : "rotate(180deg)",
            transition: "transform 0.2s ease",
          }}
        />
      </button>

      {/* Close Button */}
      {onClose && !isCollapsed && (
        <button
          onClick={onClose}
          className="absolute top-3 right-3 p-1 rounded-md transition-colors hover:bg-black/5"
        >
          <X size={16} className="text-[var(--ink-3)]" />
        </button>
      )}

      {/* Tabs */}
      <div
        ref={tabsRef}
        className={`flex ${isCollapsed ? "flex-col items-center py-4" : "px-4 pt-3 pb-2 gap-1"} border-b border-[var(--border-1)]`}
      >
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          const Icon = tab.icon;

          return (
            <button
              key={tab.id}
              onClick={() => handleTabClick(tab.id)}
              className={`flex items-center transition-all duration-200 ${isCollapsed
                  ? "justify-center w-9 h-9 mb-2 rounded-lg"
                  : "px-3 py-2 rounded-md text-xs font-medium"
                }`}
              style={{
                backgroundColor: isActive
                  ? isCollapsed
                    ? "var(--bg-canvas)"
                    : "var(--rf-charcoal)"
                  : "transparent",
                color: isActive
                  ? isCollapsed
                    ? "var(--rf-charcoal)"
                    : "var(--rf-ivory)"
                  : "var(--ink-2)",
                fontFamily: "'DM Sans', system-ui, sans-serif",
              }}
            >
              <Icon size={isCollapsed ? 18 : 14} className={isCollapsed ? "" : "mr-2"} />
              {!isCollapsed && <span>{tab.label}</span>}
            </button>
          );
        })}
      </div>

      {/* Content */}
      {!isCollapsed && (
        <div
          ref={contentRef}
          className="flex-1 overflow-y-auto p-4"
        >
          {activeTab === "evidence" && <EvidenceContent />}
          {activeTab === "assumptions" && <AssumptionsContent />}
          {activeTab === "variables" && <VariablesContent />}
          {activeTab === "versions" && <VersionsContent />}
          {activeTab === "why" && <WhyContent />}
        </div>
      )}
    </aside>
  );
}

// Content Components
function EvidenceContent() {
  const sources = [
    { id: 1, title: "Customer Interview #42", type: "Interview", date: "2h ago" },
    { id: 2, title: "Q4 Analytics Report", type: "Data", date: "1d ago" },
    { id: 3, title: "Competitor Analysis", type: "Research", date: "3d ago" },
  ];

  return (
    <div className="space-y-3">
      <h3
        className="text-sm font-medium mb-4 text-[var(--ink-1)]"
      >
        Linked Sources
      </h3>
      {sources.map((source) => (
        <div
          key={source.id}
          className="p-3 rounded-lg border cursor-pointer transition-colors hover:border-[var(--rf-charcoal)] border-[var(--border-1)] bg-[var(--bg-canvas)]"
        >
          <div
            className="text-sm font-medium mb-1 text-[var(--ink-1)]"
          >
            {source.title}
          </div>
          <div className="flex items-center justify-between">
            <span
              className="text-xs px-2 py-0.5 rounded"
              style={{
                backgroundColor: "var(--bg-surface, #F7F5EF)",
                color: "var(--rf-muted-ink, #5C565B)",
              }}
            >
              {source.type}
            </span>
            <span
              className="text-xs"
              style={{ color: "var(--ink-3, #847C82)" }}
            >
              {source.date}
            </span>
          </div>
        </div>
      ))}
      <button
        className="w-full py-2 text-xs font-medium rounded-md border border-dashed transition-colors hover:border-[var(--border-1)] text-[var(--ink-2)] border-[var(--border-2)] font-['DM_Sans',system-ui,sans-serif]"
      >
        + Add Source
      </button>
    </div>
  );
}

function AssumptionsContent() {
  const assumptions = [
    { id: 1, text: "Users prefer email over SMS", status: "unvalidated", confidence: 30 },
    { id: 2, text: "Discount drives retention", status: "validated", confidence: 85 },
    { id: 3, text: "Mobile users convert higher", status: "testing", confidence: 60 },
  ];

  return (
    <div className="space-y-3">
      <h3
        className="text-sm font-medium mb-4"
        style={{
          color: "var(--ink-1, #2A2529)",
          fontFamily: "'DM Sans', system-ui, sans-serif",
        }}
      >
        Key Assumptions
      </h3>
      {assumptions.map((assumption) => (
        <div
          key={assumption.id}
          className="p-3 rounded-lg border"
          style={{
            backgroundColor: "var(--rf-fog, #EFEDE6)",
            borderColor: "var(--border-1, #E3DED3)",
          }}
        >
          <p
            className="text-sm mb-2"
            style={{ color: "var(--ink-1, #2A2529)" }}
          >
            {assumption.text}
          </p>
          <div className="flex items-center justify-between">
            <span
              className="text-xs capitalize"
              style={{
                color:
                  assumption.status === "validated"
                    ? "#3D5A42"
                    : assumption.status === "testing"
                      ? "#8B6B3D"
                      : "var(--rf-muted-ink, #5C565B)",
              }}
            >
              {assumption.status}
            </span>
            <span
              className="text-xs"
              style={{ color: "var(--ink-3, #847C82)" }}
            >
              {assumption.confidence}%
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}

function VariablesContent() {
  const variables = [
    { id: 1, name: "discount_rate", value: "15%", type: "number" },
    { id: 2, name: "email_subject", value: "\"Last chance\" offer", type: "string" },
    { id: 3, name: "cohort_size", value: "5,240", type: "number" },
  ];

  return (
    <div className="space-y-3">
      <h3
        className="text-sm font-medium mb-4"
        style={{
          color: "var(--ink-1, #2A2529)",
          fontFamily: "'DM Sans', system-ui, sans-serif",
        }}
      >
        Campaign Variables
      </h3>
      {variables.map((variable) => (
        <div
          key={variable.id}
          className="flex items-center justify-between p-3 rounded-lg border"
          style={{
            backgroundColor: "var(--rf-fog, #EFEDE6)",
            borderColor: "var(--border-1, #E3DED3)",
          }}
        >
          <div>
            <div
              className="text-xs font-mono mb-1"
              style={{ color: "var(--ink-3, #847C82)" }}
            >
              {variable.name}
            </div>
            <div
              className="text-sm"
              style={{ color: "var(--ink-1, #2A2529)" }}
            >
              {variable.value}
            </div>
          </div>
          <span
            className="text-xs px-2 py-0.5 rounded"
            style={{
              backgroundColor: "var(--bg-surface, #F7F5EF)",
              color: "var(--rf-muted-ink, #5C565B)",
            }}
          >
            {variable.type}
          </span>
        </div>
      ))}
    </div>
  );
}

function VersionsContent() {
  const versions = [
    { id: 1, version: "v2.3", author: "Sarah Chen", date: "2h ago", changes: "Updated cohort filter" },
    { id: 2, version: "v2.2", author: "Mike Ross", date: "Yesterday", changes: "Added A/B test variant" },
    { id: 3, version: "v2.1", author: "Sarah Chen", date: "3 days ago", changes: "Initial draft" },
  ];

  return (
    <div className="space-y-3">
      <h3
        className="text-sm font-medium mb-4"
        style={{
          color: "var(--ink-1, #2A2529)",
          fontFamily: "'DM Sans', system-ui, sans-serif",
        }}
      >
        Version History
      </h3>
      {versions.map((v, index) => (
        <div
          key={v.id}
          className="relative pl-4 pb-4 last:pb-0"
        >
          {index < versions.length - 1 && (
            <div
              className="absolute left-1.5 top-2 bottom-0 w-px"
              style={{ backgroundColor: "var(--border-1, #E3DED3)" }}
            />
          )}
          <div
            className="absolute left-0 top-2 w-3 h-3 rounded-full border-2"
            style={{
              backgroundColor: "var(--bg-surface, #F7F5EF)",
              borderColor: index === 0 ? "var(--rf-charcoal, #2A2529)" : "var(--border-2, #D2CCC0)",
            }}
          />
          <div
            className="text-xs font-medium mb-1"
            style={{ color: "var(--ink-1, #2A2529)" }}
          >
            {v.version} · {v.author}
          </div>
          <div
            className="text-xs mb-1"
            style={{ color: "var(--rf-muted-ink, #5C565B)" }}
          >
            {v.changes}
          </div>
          <div
            className="text-xs"
            style={{ color: "var(--ink-3, #847C82)" }}
          >
            {v.date}
          </div>
        </div>
      ))}
    </div>
  );
}

function WhyContent() {
  return (
    <div className="space-y-4">
      <h3
        className="text-sm font-medium mb-4"
        style={{
          color: "var(--ink-1, #2A2529)",
          fontFamily: "'DM Sans', system-ui, sans-serif",
        }}
      >
        Why This Suggestion?
      </h3>
      <div
        className="p-3 rounded-lg border"
        style={{
          backgroundColor: "var(--rf-fog, #EFEDE6)",
          borderColor: "var(--border-1, #E3DED3)",
        }}
      >
        <p
          className="text-sm leading-relaxed"
          style={{ color: "var(--ink-1, #2A2529)" }}
        >
          Based on your historical campaign data, discounts between 10-20% have
          shown the highest conversion rates for retention campaigns targeting
          users who haven&apos;t purchased in 30+ days.
        </p>
      </div>
      <div
        className="text-xs p-3 rounded-lg"
        style={{
          backgroundColor: "rgba(139, 107, 61, 0.1)",
          color: "var(--rf-muted-ink, #5C565B)",
        }}
      >
        <strong>Confidence:</strong> 78% based on 12 similar campaigns
      </div>
    </div>
  );
}
