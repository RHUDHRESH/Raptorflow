import { describe, it, expect, beforeEach } from 'vitest';
import { useNotificationStore } from '../stores/notificationStore';

describe('useNotificationStore', () => {
  beforeEach(() => {
    // Reset store before each test
    useNotificationStore.getState().clearNotifications();
  });

  it('should start with an empty notifications array', () => {
    const state = useNotificationStore.getState();
    expect(state.notifications).toEqual([]);
  });

  it('should add a notification', () => {
    const { addNotification } = useNotificationStore.getState();

    addNotification({
      type: 'success',
      title: 'Test Notification',
      message: 'This is a test message',
    });

    const state = useNotificationStore.getState();
    expect(state.notifications).toHaveLength(1);
    expect(state.notifications[0]).toMatchObject({
      type: 'success',
      title: 'Test Notification',
      message: 'This is a test message',
      read: false,
    });
    expect(state.notifications[0].id).toBeDefined();
    expect(state.notifications[0].timestamp).toBeDefined();
  });

  it('should remove a notification by id', () => {
    const { addNotification, removeNotification } = useNotificationStore.getState();

    addNotification({
      type: 'info',
      title: 'To be removed',
      message: 'Goodbye',
    });

    const id = useNotificationStore.getState().notifications[0].id;
    removeNotification(id);

    const state = useNotificationStore.getState();
    expect(state.notifications).toHaveLength(0);
  });

  it('should mark a notification as read', () => {
    const { addNotification, markAsRead } = useNotificationStore.getState();

    addNotification({
      type: 'warning',
      title: 'Unread',
      message: 'Read me',
    });

    const id = useNotificationStore.getState().notifications[0].id;
    markAsRead(id);

    const state = useNotificationStore.getState();
    expect(state.notifications[0].read).toBe(true);
  });

  it('should clear all notifications', () => {
    const { addNotification, clearNotifications } = useNotificationStore.getState();

    addNotification({ type: 'info', title: '1', message: '1' });
    addNotification({ type: 'info', title: '2', message: '2' });

    clearNotifications();

    const state = useNotificationStore.getState();
    expect(state.notifications).toHaveLength(0);
  });
});
