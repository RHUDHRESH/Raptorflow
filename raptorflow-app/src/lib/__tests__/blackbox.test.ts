import { describe, it, expect, vi, beforeEach } from "vitest";

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
      })),
      insert: vi.fn(() => Promise.resolve({ error: null })),
    }))
  }
}));

import { getOutcomesByCampaign, getEvidencePackage } from "../blackbox";

describe("Blackbox API Integration", () => {

  it("should fetch outcomes for a campaign from supabase", async () => {
    const outcomes = await getOutcomesByCampaign("test-campaign-id");
    expect(Array.isArray(outcomes)).toBe(true);
  });

  it("should fetch evidence package for a learning", async () => {
    const evidence = await getEvidencePackage("test-learning-id");
    expect(Array.isArray(evidence)).toBe(true);
  });
});
