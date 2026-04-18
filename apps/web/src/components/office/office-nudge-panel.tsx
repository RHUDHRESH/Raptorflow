"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bell, X, ChevronRight, User } from "lucide-react";
import { useOfficeStore } from "@/state/office-store";
import { useFoundationStore } from "@/state/foundation-store";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ANIMATION_DURATIONS } from "@/lib/office-constants";
import { cn } from "@/lib/cn";

/**
 * RaptorFlow Nudge Panel
 * 
 * Logic: Slides in from the right edge. Displays actionable directives 
 * and intel alerts in an Obsidian-minimalist aesthetic.
 */
export function OfficeNudgePanel() {
  const { nudgePanelOpen, toggleNudgePanel, snarkFeed } = useOfficeStore();
  const { sectionData } = useFoundationStore();
  
  const strategistName = sectionData.primary_goal?.strategistName || "Strategist";

  return (
    <AnimatePresence>
      {nudgePanelOpen && (
        <motion.aside
          initial={{ x: 320 }}
          animate={{ x: 0 }}
          exit={{ x: 320 }}
          transition={{ 
            duration: ANIMATION_DURATIONS.NUDGE_PANEL_SLIDE, 
            ease: [0.4, 0, 0.2, 1] 
          }}
          className="fixed right-0 top-0 bottom-0 w-80 bg-card border-l border-border z-50 flex flex-col"
        >
          {/* Header */}
          <div className="h-14 px-4 flex items-center justify-between border-b border-border">
            <div className="flex items-center gap-2">
              <Bell className="w-4 h-4 text-amber-500" />
              <span className="text-xs font-bold uppercase tracking-widest text-zinc-500">
                Operations Feed
              </span>
            </div>
            <button 
              onClick={() => toggleNudgePanel(false)}
              className="flex items-center justify-center rounded-md h-8 w-8 text-zinc-500 hover:text-white hover:bg-zinc-800 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {/* Strategist Welcome Directive (Hardcoded first ripple) */}
              <div className="bg-secondary rounded-lg p-3 border border-zinc-800 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <User className="w-3 h-3 text-amber-500" />
                    <span className="text-[10px] font-bold uppercase tracking-wider text-amber-500">
                      {strategistName}
                    </span>
                  </div>
                  <span className="text-[9px] text-zinc-600 font-mono italic">JUST NOW</span>
                </div>
                <p className="text-sm text-zinc-300 leading-relaxed italic">
                  "I've analyzed your positioning. We're optimized for the 90-day growth target. 
                  The Council is already reviewing the first campaign draft."
                </p>
                <Button 
                  variant="default" 
                  size="sm" 
                  className="w-full h-8 text-[10px] font-bold uppercase tracking-widest"
                >
                  Acknowledge Directive <ChevronRight className="ml-1 w-3 h-3" />
                </Button>
              </div>

              {/* Feed Items */}
              {snarkFeed.map((message) => (
                <div key={message.id} className="bg-zinc-900/40 rounded-lg p-3 border border-zinc-800/50 space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-zinc-500">
                      {message.agentKey}
                    </span>
                  </div>
                  <p className="text-sm text-zinc-400">
                    {message.text}
                  </p>
                </div>
              ))}
            </div>

          {/* Footer Telemetry */}
          <div className="px-4 h-10 border-t border-border bg-background flex items-center justify-between">
            <span className="text-[9px] text-zinc-600 font-mono tracking-tighter uppercase font-bold">
              SYS: ENCRYPTED_UPLINK
            </span>
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
              <span className="text-[9px] text-green-500/70 font-bold uppercase">Active</span>
            </div>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
}
