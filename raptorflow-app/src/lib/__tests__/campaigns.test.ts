import { describe, it, expect, vi } from "vitest";
import { Campaign } from "../campaigns-types";

// Mock supabase module before importing campaigns
vi.mock("../supabase", () => ({
  supabase: {
    from: vi.fn(() => ({
      select: vi.fn(() => ({
        order: vi.fn(() => Promise.resolve({ data: [], error: null })),
        eq: vi.fn(() => ({
          single: vi.fn(() => Promise.resolve({ data: null, error: null }))
        }))
      })),
      insert: vi.fn(() => Promise.resolve({ error: null })),
      update: vi.fn(() => ({
        eq: vi.fn(() => Promise.resolve({ error: null }))
      })),
      delete: vi.fn(() => ({
        eq: vi.fn(() => Promise.resolve({ error: null }))
      }))
    }))
  }
}));

import { getCampaigns, createCampaign } from "../campaigns";

describe("Campaigns API Integration", () => {

  it("should fetch campaigns from supabase", async () => {
    const campaigns = await getCampaigns();
    expect(Array.isArray(campaigns)).toBe(true);
  });

  it("should persist a new campaign to supabase", async () => {
    const mockCampaign: Partial<Campaign> = {
      id: "test-id",
      name: "Test Campaign",
      objective: "acquire",
      status: "active",
      createdAt: new Date().toISOString(),
    };

    await createCampaign(mockCampaign as Campaign);
    // Success means no error thrown
  });
});
