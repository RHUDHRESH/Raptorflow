import { toast } from 'sonner';
import { useNotificationStore } from '../stores/notificationStore';

interface NotifyOptions {
  description?: string;
  persistent?: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

const defaultOptions: NotifyOptions = {
  persistent: true,
};

export const notify = {
  success: (title: string, message?: string, options: NotifyOptions = {}) => {
    const opts = { ...defaultOptions, ...options };
    toast.success(title, {
      description: message || opts.description,
      action: opts.action,
    });

    if (opts.persistent) {
      useNotificationStore.getState().addNotification({
        type: 'success',
        title,
        message: message || opts.description || '',
        action: opts.action,
      });
    }
  },

  error: (title: string, message?: string, options: NotifyOptions = {}) => {
    const opts = { ...defaultOptions, ...options };
    toast.error(title, {
      description: message || opts.description,
      action: opts.action,
    });

    if (opts.persistent) {
      useNotificationStore.getState().addNotification({
        type: 'error',
        title,
        message: message || opts.description || '',
        action: opts.action,
      });
    }
  },

  info: (title: string, message?: string, options: NotifyOptions = {}) => {
    const opts = { ...defaultOptions, ...options };
    toast.info(title, {
      description: message || opts.description,
      action: opts.action,
    });

    if (opts.persistent) {
      useNotificationStore.getState().addNotification({
        type: 'info',
        title,
        message: message || opts.description || '',
        action: opts.action,
      });
    }
  },

  warning: (title: string, message?: string, options: NotifyOptions = {}) => {
    const opts = { ...defaultOptions, ...options };
    toast.warning(title, {
      description: message || opts.description,
      action: opts.action,
    });

    if (opts.persistent) {
      useNotificationStore.getState().addNotification({
        type: 'warning',
        title,
        message: message || opts.description || '',
        action: opts.action,
      });
    }
  },
};
