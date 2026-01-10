"use client";

import { useState, useEffect, useRef } from "react";
import gsap from "gsap";
import { Bell, CheckCircle, AlertTriangle, Info, X, ChevronDown, Settings } from "lucide-react";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — NotificationCenter
   Dropdown notification panel with blueprint styling
   ══════════════════════════════════════════════════════════════════════════════ */

interface NotificationItem {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  code?: string;
}

export function NotificationCenter() {
  const [notifications, setNotifications] = useState<NotificationItem[]>([
    { id: '1', type: 'success', title: 'Campaign Launched', message: 'Q1 Founder Marketing campaign is now live', timestamp: new Date('2024-01-03T20:00:00Z'), read: false, code: 'N-001' },
    { id: '2', type: 'info', title: 'New Feature Available', message: 'AI Content Generator is now ready', timestamp: new Date('2024-01-03T19:50:00Z'), read: false, code: 'N-002' },
    { id: '3', type: 'warning', title: 'Budget Alert', message: "You've used 80% of monthly budget", timestamp: new Date('2024-01-03T19:35:00Z'), read: false, code: 'N-003' },
    { id: '4', type: 'success', title: 'Move Completed', message: 'LinkedIn thought leadership finished', timestamp: new Date('2024-01-03T19:00:00Z'), read: true, code: 'N-004' },
  ]);
  const [isOpen, setIsOpen] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);

  const unreadCount = notifications.filter(n => !n.read).length;

  useEffect(() => {
    if (isOpen && panelRef.current) {
      gsap.fromTo(panelRef.current, { opacity: 0, y: -8, scale: 0.97 }, { opacity: 1, y: 0, scale: 1, duration: 0.25, ease: "power2.out" });
    }
  }, [isOpen]);

  const getIcon = (type: NotificationItem['type']) => {
    const iconProps = { size: 12, strokeWidth: 1.5 };
    if (type === 'success') return <CheckCircle {...iconProps} className="text-[var(--success)]" />;
    if (type === 'error') return <AlertTriangle {...iconProps} className="text-[var(--error)]" />;
    if (type === 'warning') return <AlertTriangle {...iconProps} className="text-[var(--warning)]" />;
    return <Info {...iconProps} className="text-[var(--blueprint)]" />;
  };

  const markAsRead = (id: string) => setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
  const markAllAsRead = () => setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  const removeNotification = (id: string) => setNotifications(prev => prev.filter(n => n.id !== id));

  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    if (days > 0) return `${days}D`;
    if (hours > 0) return `${hours}H`;
    if (minutes > 0) return `${minutes}M`;
    return 'NOW';
  };

  return (
    <div className="relative">
      {/* Bell Button */}
      <button onClick={() => setIsOpen(!isOpen)} className="relative p-2 rounded-[var(--radius-sm)] text-[var(--muted)] hover:text-[var(--ink)] hover:bg-[var(--canvas)] transition-all">
        <Bell size={16} strokeWidth={1.5} />
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 h-4 min-w-4 px-1 flex items-center justify-center rounded-full bg-[var(--blueprint)] font-technical text-[var(--paper)]">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <div ref={panelRef} className="absolute right-0 top-full mt-2 w-80 z-50" style={{ opacity: 0 }}>
          <BlueprintCard code="NOTIF" showCorners padding="none" className="overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between p-3 border-b border-[var(--border)]">
              <span className="font-technical text-[var(--blueprint)]">NOTIFICATIONS</span>
              <div className="flex items-center gap-2">
                {unreadCount > 0 && <button onClick={markAllAsRead} className="font-technical text-[var(--muted)] hover:text-[var(--blueprint)] transition-colors">MARK ALL</button>}
                <button onClick={() => setIsOpen(false)} className="p-1 text-[var(--muted)] hover:text-[var(--ink)] transition-colors"><X size={12} strokeWidth={1.5} /></button>
              </div>
            </div>

            {/* List */}
            <div className="max-h-80 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-6 text-center">
                  <Bell size={24} strokeWidth={1} className="text-[var(--muted)] mx-auto mb-2" />
                  <p className="font-technical text-[var(--muted)]">NO NOTIFICATIONS</p>
                </div>
              ) : (
                <div>
                  {notifications.map((n, i) => (
                    <div key={n.id} onClick={() => markAsRead(n.id)} className={cn("p-3 border-b border-[var(--border-subtle)] cursor-pointer transition-colors hover:bg-[var(--canvas)]", !n.read && "bg-[var(--blueprint-light)]")}>
                      <div className="flex items-start gap-3">
                        <div className="pt-0.5">{getIcon(n.type)}</div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between gap-2 mb-1">
                            <p className={cn("text-sm font-medium truncate", !n.read ? "text-[var(--ink)]" : "text-[var(--secondary)]")}>{n.title}</p>
                            <button onClick={(e) => { e.stopPropagation(); removeNotification(n.id); }} className="p-1 text-[var(--muted)] hover:text-[var(--error)] transition-colors opacity-0 group-hover:opacity-100"><X size={10} strokeWidth={1.5} /></button>
                          </div>
                          <p className="text-xs text-[var(--secondary)] line-clamp-2">{n.message}</p>
                          <div className="flex items-center justify-between mt-1">
                            <span className="font-technical text-[var(--muted)]">{formatTime(n.timestamp)}</span>
                            {n.code && <span className="font-technical text-[var(--blueprint)]">{n.code}</span>}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Footer */}
            {notifications.length > 0 && (
              <div className="p-2 border-t border-[var(--border)]">
                <button className="w-full flex items-center justify-center gap-2 py-2 font-technical text-[var(--muted)] hover:text-[var(--blueprint)] transition-colors">
                  <Settings size={10} strokeWidth={1.5} />SETTINGS
                </button>
              </div>
            )}
          </BlueprintCard>
        </div>
      )}
    </div>
  );
}
