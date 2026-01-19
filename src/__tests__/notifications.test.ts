import { describe, it, expect, vi, beforeEach } from 'vitest';
import { notify } from '../lib/notifications';
import { toast } from 'sonner';
import { useNotificationStore } from '../stores/notificationStore';

// Mock sonner
vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
    warning: vi.fn(),
  },
}));

describe('notify utility', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useNotificationStore.getState().clearNotifications();
  });

  it('should call toast.success and add to store', () => {
    notify.success('Success Title', 'Success Message');

    expect(toast.success).toHaveBeenCalledWith('Success Title', expect.objectContaining({
      description: 'Success Message',
    }));

    const notifications = useNotificationStore.getState().notifications;
    expect(notifications).toHaveLength(1);
    expect(notifications[0]).toMatchObject({
      type: 'success',
      title: 'Success Title',
      message: 'Success Message',
    });
  });

  it('should call toast.error and add to store', () => {
    notify.error('Error Title', 'Error Message');

    expect(toast.error).toHaveBeenCalledWith('Error Title', expect.objectContaining({
      description: 'Error Message',
    }));

    const notifications = useNotificationStore.getState().notifications;
    expect(notifications).toHaveLength(1);
    expect(notifications[0].type).toBe('error');
  });

  it('should not add to store if persistent is false', () => {
    notify.info('Info Title', 'Info Message', { persistent: false });

    expect(toast.info).toHaveBeenCalled();
    const notifications = useNotificationStore.getState().notifications;
    expect(notifications).toHaveLength(0);
  });
});
