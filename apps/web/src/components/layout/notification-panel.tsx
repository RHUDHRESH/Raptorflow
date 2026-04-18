"use client";

import * as React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Cross2Icon, BellIcon, LightningBoltIcon, InfoCircledIcon, ExclamationTriangleIcon } from "@radix-ui/react-icons";
import { useOfficeStore } from "@/state/office-store";

interface NotificationPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export function NotificationPanel({ isOpen, onClose }: NotificationPanelProps) {
  const eventLog = useOfficeStore((s) => s.eventLog);

  // Filter for alerts/significant events
  const notifications = eventLog.slice(-20).reverse();

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-[100] bg-black/40 backdrop-blur-sm"
          />

          {/* Drawer */}
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 bottom-0 z-[101] w-full max-w-sm bg-[#0a0a0a] border-l-2 border-[var(--foreground)] flex flex-col shadow-2xl"
          >
            {/* Header */}
            <div className="p-6 border-b-2 border-[var(--foreground)] flex items-center justify-between">
              <div>
                <p className="font-mono text-[9px] font-bold text-zinc-600 uppercase tracking-[0.2em] mb-1">
                  Alerts // Session_Buffer
                </p>
                <h2 className="font-[family-name:var(--font-display)] text-2xl text-white">System Notifications</h2>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-zinc-900 transition-colors rounded-none"
              >
                <Cross2Icon className="w-5 h-5 text-white" />
              </button>
            </div>

            {/* List */}
            <div className="flex-1 overflow-y-auto overflow-x-hidden scrollbar-hide divide-y divide-zinc-900">
              {notifications.length === 0 ? (
                <div className="p-12 text-center">
                  <BellIcon className="w-8 h-8 text-zinc-800 mx-auto mb-4" />
                  <p className="text-[10px] font-mono text-zinc-600 uppercase tracking-widest leading-relaxed">
                    Uplink Quiet. <br/>
                    No active ripples in buffer.
                  </p>
                </div>
              ) : (
                notifications.map((msg, i) => {
                  const type = (msg.type || msg.eventType || "system").toLowerCase();
                  const isCritical = type.includes("missed") || type.includes("alert") || type.includes("urg");
                  
                  return (
                    <div 
                      key={i} 
                      className="p-5 hover:bg-white/[0.02] transition-colors relative group"
                    >
                      {isCritical && (
                        <div className="absolute left-0 top-0 bottom-0 w-1 bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]" />
                      )}
                      
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {isCritical ? (
                            <LightningBoltIcon className="w-3 h-3 text-amber-500" />
                          ) : (
                            <InfoCircledIcon className="w-3 h-3 text-zinc-600" />
                          )}
                          <span className="font-mono text-[8px] font-bold text-zinc-500 uppercase tracking-widest">
                            {type}
                          </span>
                        </div>
                        <span className="font-mono text-[8px] text-zinc-700">
                          {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                        </span>
                      </div>
                      
                      <p className="text-zinc-400 text-xs font-light leading-relaxed mb-3">
                        {typeof msg.payload === 'string' ? msg.payload : JSON.stringify(msg.payload || {}).slice(0, 120)}
                      </p>
                      
                      <div className="flex items-center gap-4 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button className="text-[8px] font-mono font-bold text-amber-500 uppercase tracking-widest hover:underline">
                          View Intel
                        </button>
                        <button className="text-[8px] font-mono font-bold text-zinc-600 uppercase tracking-widest hover:underline">
                          Dismiss
                        </button>
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-zinc-900 bg-black/40">
              <button className="w-full h-10 border border-zinc-800 text-[9px] font-mono text-zinc-500 uppercase tracking-widest hover:border-zinc-400 hover:text-zinc-300 transition-all">
                Clear All Signals
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
