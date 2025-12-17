import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { toast } from 'sonner'

const generateId = () => `${Date.now()}_${Math.random().toString(36).substring(2, 9)}`

const useNotificationsStore = create(
  persist(
    (set, get) => ({
      notifications: [],
      toastsEnabled: true,
      hasSeededDemo: false,

      addNotification: (notification, options = {}) => {
        const { toast: shouldToast = false } = options

        const newNotification = {
          id: generateId(),
          createdAt: new Date().toISOString(),
          unread: true,
          level: 'info',
          title: '',
          detail: '',
          href: null,
          ...notification,
        }

        set((state) => ({ notifications: [newNotification, ...state.notifications] }))

        if (shouldToast && get().toastsEnabled) {
          const message = newNotification.title || 'Notification'
          const description = newNotification.detail || undefined

          if (newNotification.level === 'success') toast.success(message, { description })
          else if (newNotification.level === 'error') toast.error(message, { description })
          else toast(message, { description })
        }

        return newNotification
      },

      setToastsEnabled: (enabled) => {
        set({ toastsEnabled: !!enabled })
      },

      seedDemoNotifications: () => {
        const { hasSeededDemo, notifications } = get()
        if (hasSeededDemo) return
        if (notifications.length > 0) {
          set({ hasSeededDemo: true })
          return
        }

        const now = Date.now()
        const iso = (msAgo) => new Date(now - msAgo).toISOString()

        const demo = [
          {
            id: generateId(),
            createdAt: iso(2 * 60 * 1000),
            unread: true,
            level: 'success',
            title: 'Move completed',
            detail: '“LinkedIn Thought Leadership Post” finished successfully.',
            href: '/app/moves',
          },
          {
            id: generateId(),
            createdAt: iso(18 * 60 * 1000),
            unread: true,
            level: 'info',
            title: 'New radar signal detected',
            detail: 'A competitor spike was flagged in your space.',
            href: '/app/radar',
          },
          {
            id: generateId(),
            createdAt: iso(55 * 60 * 1000),
            unread: true,
            level: 'success',
            title: 'Campaign activated',
            detail: '“Q1 Pipeline Blitz” is now live.',
            href: '/app/campaigns',
          },
          {
            id: generateId(),
            createdAt: iso(3 * 60 * 60 * 1000),
            unread: false,
            level: 'info',
            title: 'Draft saved',
            detail: 'Your edits were saved.',
            href: '/app/campaigns',
          },
          {
            id: generateId(),
            createdAt: iso(26 * 60 * 60 * 1000),
            unread: false,
            level: 'error',
            title: 'Action needed',
            detail: 'One integration needs attention.',
            href: '/app/settings',
          },
        ]

        set({ notifications: demo, hasSeededDemo: true })
      },

      markRead: (id) => {
        set((state) => ({
          notifications: state.notifications.map((n) => (n.id === id ? { ...n, unread: false } : n)),
        }))
      },

      markAllRead: () => {
        set((state) => ({
          notifications: state.notifications.map((n) => ({ ...n, unread: false })),
        }))
      },

      removeNotification: (id) => {
        set((state) => ({ notifications: state.notifications.filter((n) => n.id !== id) }))
      },

      clearNotifications: () => {
        set({ notifications: [], hasSeededDemo: true })
      },

      getUnreadCount: () => get().notifications.filter((n) => n.unread).length,
    }),
    {
      name: 'raptorflow_notifications_v1',
      version: 1,
    }
  )
)

export default useNotificationsStore
