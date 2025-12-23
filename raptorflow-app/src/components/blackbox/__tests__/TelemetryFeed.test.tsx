import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { TelemetryFeed } from "../TelemetryFeed";
import React from 'react';

// Mock the lib/blackbox module
vi.mock("@/lib/blackbox", () => ({
  getTelemetryByMove: vi.fn(() => Promise.resolve([]))
}));

describe("TelemetryFeed Component", () => {
  it("should render traces correctly", () => {
    const mockTraces: any[] = [
      { id: '1', agent_id: 'TestAgent', trace: { status: 'success' }, latency: 100, timestamp: new Date().toISOString() }
    ];
    
    render(<TelemetryFeed traces={mockTraces} />);
    expect(screen.getByText(/TestAgent/i)).toBeDefined();
  });
});