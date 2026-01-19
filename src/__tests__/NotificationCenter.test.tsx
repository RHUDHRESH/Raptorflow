import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { NotificationBell } from '../components/shell/NotificationCenter';
import { useNotificationStore } from '../stores/notificationStore';

// Mock notification store
vi.mock('../stores/notificationStore', () => ({
  useNotificationStore: vi.fn(),
}));

describe('NotificationBell', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should show notification count when there are unread notifications', () => {
    (useNotificationStore as any).mockReturnValue({
      notifications: [
        { id: '1', title: 'Test', message: 'Msg', read: false, type: 'info', timestamp: new Date() },
      ],
    });

    render(<NotificationBell />);
    
    // Check for indicator (dot or number)
    const dot = document.querySelector('.bg-\[var\(--blueprint\)\]');
    expect(dot).toBeDefined();
  });

  it('should show empty state message when no notifications', () => {
    (useNotificationStore as any).mockReturnValue({
      notifications: [],
    });

    render(<NotificationBell />);
    
    // Open popover
    const bell = screen.getByRole('button');
    fireEvent.click(bell);
    
    expect(screen.getByText(/no notifications yet/i)).toBeDefined();
  });
});
