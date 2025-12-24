import { describe, it, expect, vi } from "vitest";

// Mock supabase module
vi.mock("../supabase", () => ({
  supabase: {
    from: vi.fn(() => ({
      select: vi.fn(() => ({
        eq: vi.fn(() => ({
          order: vi.fn(() => Promise.resolve({ data: [], error: null })),
          single: vi.fn(() => Promise.resolve({ data: { source_ids: [] }, error: null })),
        })),
        in: vi.fn(() => Promise.resolve({ data: [], error: null })),
        contains: vi.fn(() => Promise.resolve({ data: [], error: null })),
      })),
      insert: vi.fn(() => Promise.resolve({ error: null })),
    }))
  }
}));

import {
  getOutcomesByCampaign,
  getEvidencePackage,
  getLearningsByMove,
  triggerLearningCycle,
  runSpecialistAgent
} from "../blackbox";

describe("Blackbox API Integration", () => {

  it("should fetch outcomes for a campaign from supabase", async () => {
    const outcomes = await getOutcomesByCampaign("test-campaign-id");
    expect(Array.isArray(outcomes)).toBe(true);
  });

  it("should fetch evidence package for a learning", async () => {
    const evidence = await getEvidencePackage("test-learning-id");
    expect(Array.isArray(evidence)).toBe(true);
  });

  it("should fetch learnings for a move", async () => {
    const learnings = await getLearningsByMove("test-move-id");
    expect(Array.isArray(learnings)).toBe(true);
  });

  it("should trigger learning cycle via fetch", async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve({ status: 'success' })
      })
    ) as unknown as typeof fetch;

    const result = await triggerLearningCycle("test-move-id");
    expect(result.status).toBe('success');
    expect(global.fetch).toHaveBeenCalled();
  });

  it("should run specialist agent via fetch", async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve({ status: 'success' })
      })
    ) as unknown as typeof fetch;

    const result = await runSpecialistAgent("roi_analyst", "test-move-id");
    expect(result.status).toBe('success');
    expect(global.fetch).toHaveBeenCalled();
  });
});
