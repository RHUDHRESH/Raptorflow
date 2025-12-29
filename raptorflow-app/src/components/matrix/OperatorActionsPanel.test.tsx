import { render, screen } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { OperatorActionsPanel } from './OperatorActionsPanel';
import React from 'react';

describe('OperatorActionsPanel', () => {
  beforeEach(() => {
    // Mock ResizeObserver which is used by Radix UI Slider
    global.ResizeObserver = class ResizeObserver {
      observe = vi.fn();
      unobserve = vi.fn();
      disconnect = vi.fn();
    };
  });

  it('renders the operator actions heading', () => {
    render(<OperatorActionsPanel />);
    expect(screen.getByText(/Operator Actions/i)).toBeDefined();
  });

  it('renders the Inference Throttling section', () => {
    render(<OperatorActionsPanel />);
    expect(screen.getByText(/Inference Throttling/i)).toBeDefined();
    expect(screen.getAllByRole('slider')[0]).toBeDefined();
  });

  it('renders the Cache Purge button', () => {
    render(<OperatorActionsPanel />);
    expect(screen.getByRole('button', { name: /purge caches/i })).toBeDefined();
  });

  it('renders the Resource Scaling section', () => {
    render(<OperatorActionsPanel />);
    expect(screen.getByText(/Resource Scaling/i)).toBeDefined();
  });

  it('renders the Retrain Trigger button', () => {
    render(<OperatorActionsPanel />);
    expect(
      screen.getByRole('button', { name: /trigger retraining/i })
    ).toBeDefined();
  });
});
