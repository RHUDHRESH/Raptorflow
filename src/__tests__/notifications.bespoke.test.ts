import { describe, it, expect, vi, beforeEach } from 'vitest';
import { notify } from '../lib/notifications';
import { toast } from 'sonner';

// Mock sonner
vi.mock('sonner', () => ({
  toast: {
    error: vi.fn(),
  },
}));

describe('notify bespoke errors', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should map UNAUTHORIZED code to friendly message', () => {
    notify.error('Access Denied', { code: 'UNAUTHORIZED' });
    
    expect(toast.error).toHaveBeenCalledWith('Access Denied', expect.objectContaining({
      description: 'Your session has expired or you do not have permission. Please log in again.'
    }));
  });

  it('should map AI_ENGINE_ERROR code', () => {
    notify.error('Synthesis Failed', { code: 'AI_ENGINE_ERROR' });
    
    expect(toast.error).toHaveBeenCalledWith('Synthesis Failed', expect.objectContaining({
      description: 'The Intelligence Engine encountered an issue. Our team has been notified.'
    }));
  });
});
