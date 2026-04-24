"use client";

import * as React from "react";

interface Notification {
  id: number;
  message: string;
  href: string;
  createdAt: Date;
}

function timeAgo(date: Date): string {
  const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
  if (seconds < 60) return `${seconds}s ago`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export function NotificationBell({ userId }: { userId: string }): React.ReactElement {
  const [notifications, setNotifications] = React.useState<Notification[]>([]);
  const [unread, setUnread] = React.useState(0);
  const [open, setOpen] = React.useState(false);

  const addNotification = (message: string, href: string) => {
    setNotifications((prev) =>
      [{ id: Date.now(), message, href, createdAt: new Date() }, ...prev].slice(0, 20),
    );
    setUnread((prev) => prev + 1);
  };

  return (
    <div className="relative">
      <button
        onClick={() => {
          setOpen((o) => !o);
          if (!open) setUnread(0);
        }}
        className="relative rounded-lg p-2 transition-colors hover:bg-[var(--border)]"
        style={{ color: "var(--foreground)" }}
      >
        <span style={{ fontSize: 18 }}>🔔</span>
        {unread > 0 && (
          <span
            className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full text-xs font-bold"
            style={{ background: "var(--destructive)", color: "white" }}
          >
            {unread > 9 ? "9+" : unread}
          </span>
        )}
      </button>

      {open && (
        <div
          className="absolute right-0 top-full z-50 mt-1 w-80 overflow-y-auto rounded-xl border shadow-lg"
          style={{ background: "var(--card)", borderColor: "var(--border)", maxHeight: 384 }}
        >
          {notifications.length === 0 ? (
            <div
              className="px-4 py-6 text-center text-sm"
              style={{ color: "var(--muted-foreground)" }}
            >
              No notifications yet
            </div>
          ) : (
            notifications.map((n) => (
              <a
                key={n.id}
                href={n.href}
                className="flex flex-col border-b px-4 py-3 transition-colors hover:bg-[var(--muted)] last:border-0"
                style={{ borderColor: "var(--border)" }}
                onClick={() => setOpen(false)}
              >
                <span className="text-sm" style={{ color: "var(--foreground)" }}>
                  {n.message}
                </span>
                <span className="mt-0.5 text-xs" style={{ color: "var(--muted-foreground)" }}>
                  {timeAgo(n.createdAt)}
                </span>
              </a>
            ))
          )}
        </div>
      )}
    </div>
  );
}
