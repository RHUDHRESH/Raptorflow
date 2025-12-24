import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { AgentAuditLog } from "../AgentAuditLog";
import React from 'react';

// Mock the lib/blackbox module
vi.mock("@/lib/blackbox", () => ({
  getTelemetryByMove: vi.fn(() => Promise.resolve([]))
}));

describe("AgentAuditLog Component", () => {
  it("should render entries correctly", () => {
    const mockEntries: any[] = [
      { id: '1', agent_id: 'AuditAgent', move_id: 'm1', trace: {}, tokens: 10, latency: 0.5, timestamp: new Date().toISOString() }
    ];

    render(<AgentAuditLog entries={mockEntries} />);
    expect(screen.getByText(/AuditAgent/i)).toBeDefined();
  });
});
