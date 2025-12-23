import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { TelemetryFeed } from "../TelemetryFeed";
import React from 'react';

describe("TelemetryFeed Component", () => {
  it("should render traces correctly", () => {
    const mockTraces: any[] = [
      { id: '1', agent_id: 'TestAgent', trace: { status: 'success' }, latency: 100, timestamp: new Date().toISOString() }
    ];
    
    render(<TelemetryFeed traces={mockTraces} />);
    expect(screen.getByText(/TestAgent/i)).toBeDefined();
  });
});