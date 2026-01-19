import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BlueprintCommandPrompt } from '../components/ui/BlueprintCommandPrompt';
import { useRouter } from 'next/navigation';
import { useSettingsStore } from '../stores/settingsStore';

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(),
}));

// Mock settings store
vi.mock('../stores/settingsStore', () => ({
  useSettingsStore: vi.fn(),
}));

describe('BlueprintCommandPrompt', () => {
  const mockPush = vi.fn();
  
  beforeEach(() => {
    vi.clearAllMocks();
    (useRouter as any).mockReturnValue({ push: mockPush });
    (useSettingsStore as any).mockReturnValue({
      preferences: { commandPalette: true }
    });
  });

  it('should not be visible by default', () => {
    render(<BlueprintCommandPrompt />);
    expect(screen.queryByPlaceholderText(/Type a command/i)).toBeNull();
  });

  it('should open when Ctrl+K is pressed', () => {
    render(<BlueprintCommandPrompt />);
    fireEvent.keyDown(document, { key: 'k', ctrlKey: true });
    expect(screen.getByPlaceholderText(/Type a command/i)).toBeDefined();
  });

  it('should filter commands based on search query', () => {
    render(<BlueprintCommandPrompt />);
    fireEvent.keyDown(document, { key: 'k', ctrlKey: true });
    
    const input = screen.getByPlaceholderText(/Type a command/i);
    fireEvent.change(input, { target: { value: 'Moves' } });
    
    expect(screen.getByText('Go to Moves')).toBeDefined();
    expect(screen.queryByText('Go to Dashboard')).toBeNull();
  });

  it('should navigate when a command is selected', () => {
    render(<BlueprintCommandPrompt />);
    fireEvent.keyDown(document, { key: 'k', ctrlKey: true });
    
    const movesButton = screen.getByText('Go to Moves').closest('button');
    fireEvent.click(movesButton!);
    
    expect(mockPush).toHaveBeenCalledWith('/moves');
  });

  it('should handle keyboard navigation (ArrowDown/Enter)', () => {
    render(<BlueprintCommandPrompt />);
    fireEvent.keyDown(document, { key: 'k', ctrlKey: true });
    
    const input = screen.getByPlaceholderText(/Type a command/i);
    
    // Press ArrowDown to select second item (Campaigns)
    fireEvent.keyDown(input, { key: 'ArrowDown' });
    fireEvent.keyDown(input, { key: 'Enter' });
    
    expect(mockPush).toHaveBeenCalledWith('/campaigns');
  });
});
