import { toast } from 'sonner';
import { useNotificationStore } from '../stores/notificationStore';

interface NotifyOptions {
  description?: string;
  persistent?: boolean;
  code?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

const defaultOptions: NotifyOptions = {
  persistent: true,
};

const ERROR_MAP: Record<string, string> = {
  'UNAUTHORIZED': 'Your session has expired or you do not have permission. Please log in again.',
  'FORBIDDEN': 'You do not have access to this resource.',
  'NOT_FOUND': 'The requested item was not found.',
  'VALIDATION_ERROR': 'Please check your input and try again.',
  'AI_ENGINE_ERROR': 'The Intelligence Engine encountered an issue. Our team has been notified.',
  'NETWORK_ERROR': 'Unable to connect to the server. Please check your internet connection.',
  'INTERNAL_SERVER_ERROR': 'A system error occurred. We are working on a fix.',
};

export const notify = {
  success: (title: string, message?: string | NotifyOptions, options: NotifyOptions = {}) => {
    const msg = typeof message === 'string' ? message : undefined;
    const opts = { ...defaultOptions, ...(typeof message === 'object' ? message : options) };
    
    toast.success(title, {
      description: msg || opts.description,
      action: opts.action,
    });

    if (opts.persistent) {
      useNotificationStore.getState().addNotification({
        type: 'success',
        title,
        message: msg || opts.description || '',
        action: opts.action,
      });
    }
  },

  error: (title: string, message?: string | NotifyOptions, options: NotifyOptions = {}) => {
    const msg = typeof message === 'string' ? message : undefined;
    const opts = { ...defaultOptions, ...(typeof message === 'object' ? message : options) };
    
    // Map error code to friendly description if provided
    const friendlyDescription = opts.code ? ERROR_MAP[opts.code] : (msg || opts.description);

    toast.error(title, {
      description: friendlyDescription,
      action: opts.action,
    });

    if (opts.persistent) {
      useNotificationStore.getState().addNotification({
        type: 'error',
        title,
        message: friendlyDescription || '',
        action: opts.action,
      });
    }
  },

  info: (title: string, message?: string | NotifyOptions, options: NotifyOptions = {}) => {
    const msg = typeof message === 'string' ? message : undefined;
    const opts = { ...defaultOptions, ...(typeof message === 'object' ? message : options) };
    
    toast.info(title, {
      description: msg || opts.description,
      action: opts.action,
    });

    if (opts.persistent) {
      useNotificationStore.getState().addNotification({
        type: 'info',
        title,
        message: msg || opts.description || '',
        action: opts.action,
      });
    }
  },

  warning: (title: string, message?: string | NotifyOptions, options: NotifyOptions = {}) => {
    const msg = typeof message === 'string' ? message : undefined;
    const opts = { ...defaultOptions, ...(typeof message === 'object' ? message : options) };
    
    toast.warning(title, {
      description: msg || opts.description,
      action: opts.action,
    });

    if (opts.persistent) {
      useNotificationStore.getState().addNotification({
        type: 'warning',
        title,
        message: msg || opts.description || '',
        action: opts.action,
      });
    }
  },
};