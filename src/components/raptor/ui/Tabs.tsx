"use client";

import React, { useRef, useEffect } from "react";
import { gsap } from "gsap";

interface Tab {
  id: string;
  label: string;
  badge?: number;
}

interface TabsProps {
  tabs: Tab[];
  activeTab: string;
  onChange: (id: string) => void;
}

export function Tabs({ tabs, activeTab, onChange }: TabsProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const indicatorRef = useRef<HTMLDivElement>(null);
  const tabRefs = useRef<(HTMLButtonElement | null)[]>([]);

  useEffect(() => {
    const activeIndex = tabs.findIndex((tab) => tab.id === activeTab);
    const activeTabEl = tabRefs.current[activeIndex];

    if (!activeTabEl || !indicatorRef.current) return;

    const containerRect = containerRef.current?.getBoundingClientRect();
    const tabRect = activeTabEl.getBoundingClientRect();

    if (containerRect) {
      gsap.to(indicatorRef.current, {
        x: tabRect.left - containerRect.left,
        width: tabRect.width,
        duration: 0.3,
        ease: "power2.out",
      });
    }
  }, [activeTab, tabs]);

  return (
    <div
      ref={containerRef}
      className="relative flex items-center border-b border-[#E3DED3]"
    >
      {/* Animated indicator */}
      <div
        ref={indicatorRef}
        className="absolute bottom-0 h-[2px] bg-[#2A2529]"
        style={{ width: 0 }}
      />

      {tabs.map((tab, index) => {
        const isActive = tab.id === activeTab;

        return (
          <button
            key={tab.id}
            ref={(el) => {
              tabRefs.current[index] = el;
            }}
            onClick={() => onChange(tab.id)}
            className={`
              relative flex items-center gap-2 px-4 py-3 text-[14px] font-medium
              font-['DM_Sans',system-ui,sans-serif]
              transition-colors duration-200
              ${isActive ? "text-[#2A2529]" : "text-[#847C82] hover:text-[#5C565B] hover:bg-[#F3F0E7]"}
            `}
          >
            <span>{tab.label}</span>
            {typeof tab.badge === "number" && (
              <span
                className={`
                  inline-flex items-center justify-center min-w-[18px] h-[18px] px-1
                  text-[10px] font-semibold rounded-[6px]
                  ${isActive ? "bg-[#2A2529] text-[#F3F0E7]" : "bg-[#E3DED3] text-[#5C565B]"}
                `}
              >
                {tab.badge}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
