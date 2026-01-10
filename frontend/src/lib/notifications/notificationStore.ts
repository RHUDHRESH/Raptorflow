/**
 * Real-time Notification Management System
 * Handles in-app notifications with persistence and real-time updates
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
  metadata?: Record<string, unknown>;
}

interface NotificationStore {
  notifications: Notification[];
  unreadCount: number;
  maxNotifications: number;

  // Actions
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  removeNotification: (id: string) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  clearAll: () => void;

  // Getters
  getUnreadNotifications: () => Notification[];
  getRecentNotifications: (limit?: number) => Notification[];

  // Settings
  setMaxNotifications: (max: number) => void;
}

export const useNotificationStore = create<NotificationStore>()(
  persist(
    (set, get) => ({
      notifications: [],
      unreadCount: 0,
      maxNotifications: 50,

      addNotification: (notification) => {
        const newNotification: Notification = {
          ...notification,
          id: `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          timestamp: new Date(),
          read: false,
        };

        set((state) => {
          const updatedNotifications = [newNotification, ...state.notifications];

          // Keep only the most recent notifications
          const trimmedNotifications = updatedNotifications.slice(0, state.maxNotifications);

          return {
            notifications: trimmedNotifications,
            unreadCount: trimmedNotifications.filter(n => !n.read).length,
          };
        });

        // Auto-remove success notifications after 5 seconds
        if (notification.type === 'success') {
          setTimeout(() => {
            get().removeNotification(newNotification.id);
          }, 5000);
        }
      },

      removeNotification: (id) => {
        set((state) => {
          const updatedNotifications = state.notifications.filter(n => n.id !== id);
          return {
            notifications: updatedNotifications,
            unreadCount: updatedNotifications.filter(n => !n.read).length,
          };
        });
      },

      markAsRead: (id) => {
        set((state) => {
          const updatedNotifications = state.notifications.map(n =>
            n.id === id ? { ...n, read: true } : n
          );
          return {
            notifications: updatedNotifications,
            unreadCount: updatedNotifications.filter(n => !n.read).length,
          };
        });
      },

      markAllAsRead: () => {
        set((state) => ({
          notifications: state.notifications.map(n => ({ ...n, read: true })),
          unreadCount: 0,
        }));
      },

      clearAll: () => {
        set({
          notifications: [],
          unreadCount: 0,
        });
      },

      getUnreadNotifications: () => {
        return get().notifications.filter(n => !n.read);
      },

      getRecentNotifications: (limit = 10) => {
        return get().notifications.slice(0, limit);
      },

      setMaxNotifications: (max) => {
        set((state) => {
          const trimmedNotifications = state.notifications.slice(0, max);
          return {
            maxNotifications: max,
            notifications: trimmedNotifications,
            unreadCount: trimmedNotifications.filter(n => !n.read).length,
          };
        });
      },
    }),
    {
      name: 'notification-store',
      partialize: (state) => ({
        notifications: state.notifications.slice(0, 20), // Only persist recent 20
        maxNotifications: state.maxNotifications,
      }),
    }
  )
);

// Convenience functions for common notification types
export const notify = {
  success: (title: string, message: string, options?: Partial<Omit<Notification, 'id' | 'timestamp' | 'read' | 'type'>>) => {
    useNotificationStore.getState().addNotification({
      type: 'success',
      title,
      message,
      ...options,
    });
  },

  error: (title: string, message: string, options?: Partial<Omit<Notification, 'id' | 'timestamp' | 'read' | 'type'>>) => {
    useNotificationStore.getState().addNotification({
      type: 'error',
      title,
      message,
      ...options,
    });
  },

  warning: (title: string, message: string, options?: Partial<Omit<Notification, 'id' | 'timestamp' | 'read' | 'type'>>) => {
    useNotificationStore.getState().addNotification({
      type: 'warning',
      title,
      message,
      ...options,
    });
  },

  info: (title: string, message: string, options?: Partial<Omit<Notification, 'id' | 'timestamp' | 'read' | 'type'>>) => {
    useNotificationStore.getState().addNotification({
      type: 'info',
      title,
      message,
      ...options,
    });
  },
};

// Real-time notification hooks
export const useNotifications = () => {
  const store = useNotificationStore();

  return {
    notifications: store.notifications,
    unreadCount: store.unreadCount,
    addNotification: store.addNotification,
    removeNotification: store.removeNotification,
    markAsRead: store.markAsRead,
    markAllAsRead: store.markAllAsRead,
    clearAll: store.clearAll,
    getUnreadNotifications: store.getUnreadNotifications,
    getRecentNotifications: store.getRecentNotifications,
  };
};

export const useUnreadCount = () => {
  return useNotificationStore(state => state.unreadCount);
};

// Auto-generate sample notifications for demo
export const generateSampleNotifications = () => {
  const samples = [
    {
      type: 'success' as const,
      title: 'Campaign Launched',
      message: 'Your Q1 Founder Marketing campaign is now live',
    },
    {
      type: 'info' as const,
      title: 'New Feature Available',
      message: 'AI Content Generator is now ready to use',
    },
    {
      type: 'warning' as const,
      title: 'Budget Alert',
      message: 'You\'ve used 80% of your monthly budget',
    },
    {
      type: 'success' as const,
      title: 'Move Completed',
      message: 'LinkedIn thought leadership series finished',
    },
    {
      type: 'success' as const,
      title: 'Weekly Report Ready',
      message: 'Your weekly marketing report is available',
    },
  ];

  // Add a random sample notification every 30 seconds for demo
  const addRandomNotification = () => {
    const randomSample = samples[Math.floor(Math.random() * samples.length)];
    notify[randomSample.type](randomSample.title, randomSample.message);
  };

  // Start the interval
  setInterval(addRandomNotification, 30000);

  // Add initial notification
  setTimeout(() => {
    notify.success('Welcome Back!', 'Your marketing dashboard is ready');
  }, 1000);
};
