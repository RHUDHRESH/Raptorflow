"use client";

import React from "react";
import { Bell, Check, Trash2, Info, AlertTriangle, XCircle, CheckCircle2 } from "lucide-react";
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuTrigger, 
  DropdownMenuLabel, 
  DropdownMenuSeparator 
} from "@/components/ui/dropdown-menu";
import { useNotificationStore, Notification } from "@/stores/notificationStore";
import { cn } from "@/lib/utils";
import { formatDistanceToNow } from "date-fns";
import { motion, AnimatePresence } from "framer-motion";

const ICONS = {
  success: <CheckCircle2 className="text-green-500" size={16} />,
  error: <XCircle className="text-red-500" size={16} />,
  warning: <AlertTriangle className="text-amber-500" size={16} />,
  info: <Info className="text-[var(--blueprint)]" size={16} />,
};

export function NotificationBell() {
  const { notifications, markAsRead, removeNotification, clearNotifications } = useNotificationStore();
  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button className="relative p-2 rounded-[var(--radius-sm)] hover:bg-[var(--canvas)] transition-colors group focus:outline-none">
          <Bell
            size={16}
            strokeWidth={1.5}
            className="text-[var(--muted)] group-hover:text-[var(--ink)] transition-colors"
          />
          {unreadCount > 0 && (
            <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-[var(--blueprint)] rounded-full border-2 border-[var(--paper)] animate-in zoom-in duration-300" />
          )}
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80 p-0 overflow-hidden bg-[var(--paper)] border border-[var(--border)] shadow-xl rounded-[var(--radius)]">
        <div className="flex items-center justify-between p-4 border-b border-[var(--structure-subtle)] bg-[var(--surface-elevated)]">
          <div className="flex items-center gap-2">
            <span className="font-technical text-[10px] text-[var(--blueprint)] uppercase tracking-wider">Alerts</span>
            <span className="text-[10px] font-bold text-[var(--ink-muted)]">•</span>
            <span className="text-[10px] font-bold text-[var(--ink)] uppercase">{unreadCount} New</span>
          </div>
          {notifications.length > 0 && (
            <button 
              onClick={(e) => { e.preventDefault(); clearNotifications(); }}
              className="text-[10px] font-bold text-[var(--ink-muted)] hover:text-red-500 transition-colors uppercase"
            >
              Clear All
            </button>
          )}
        </div>

        <div className="max-h-[400px] overflow-y-auto custom-scrollbar">
          <AnimatePresence initial={false}>
            {notifications.length === 0 ? (
              <div className="py-12 px-4 text-center">
                <Bell size={32} className="mx-auto text-[var(--structure)] mb-3 opacity-20" />
                <p className="text-sm text-[var(--ink-muted)]">No notifications yet</p>
              </div>
            ) : (
              notifications.map((notification) => (
                <NotificationItem 
                  key={notification.id} 
                  notification={notification} 
                  onRead={() => markAsRead(notification.id)}
                  onRemove={() => removeNotification(notification.id)}
                />
              ))
            )}
          </AnimatePresence>
        </div>

        <div className="p-2 bg-[var(--canvas)] border-t border-[var(--structure-subtle)] text-center">
          <span className="font-technical text-[9px] text-[var(--ink-muted)] uppercase tracking-widest">
            System OS v0.1.0
          </span>
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

function NotificationItem({ 
  notification, 
  onRead, 
  onRemove 
}: { 
  notification: Notification; 
  onRead: () => void;
  onRemove: () => void;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className={cn(
        "group p-4 border-b border-[var(--structure-subtle)] last:border-none transition-colors relative",
        !notification.read ? "bg-[var(--blueprint-light)]/5" : "bg-transparent"
      )}
    >
      <div className="flex gap-3">
        <div className="mt-0.5 shrink-0">
          {ICONS[notification.type]}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex justify-between items-start mb-1">
            <h4 className={cn(
              "text-xs font-bold truncate leading-none",
              !notification.read ? "text-[var(--ink)]" : "text-[var(--ink-muted)]"
            )}>
              {notification.title}
            </h4>
            <span className="text-[9px] font-technical text-[var(--ink-muted)] shrink-0 ml-2">
              {formatDistanceToNow(notification.timestamp, { addSuffix: true })}
            </span>
          </div>
          <p className="text-[11px] text-[var(--ink-secondary)] leading-normal line-clamp-2">
            {notification.message}
          </p>
          
          <div className="flex gap-4 mt-3">
            {!notification.read && (
              <button 
                onClick={(e) => { e.preventDefault(); onRead(); }}
                className="text-[10px] font-bold text-[var(--blueprint)] hover:text-[var(--blueprint)]/80 uppercase tracking-wider py-2 -my-2"
              >
                Mark as read
              </button>
            )}
            <button 
              onClick={(e) => { e.preventDefault(); onRemove(); }}
              className="text-[10px] font-bold text-red-500 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-opacity uppercase tracking-wider py-2 -my-2"
            >
              Remove
            </button>
          </div>
        </div>
      </div>
      
      {!notification.read && (
        <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-[var(--blueprint)]" />
      )}
    </motion.div>
  );
}
