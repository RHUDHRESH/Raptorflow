import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, apiFetch, dailyWinsApi, getApiBaseUrl, getWsBaseUrl } from "./api";

const originalFetch = global.fetch;

describe("api client", () => {
  afterEach(() => {
    global.fetch = originalFetch;
    vi.restoreAllMocks();
  });

  it("uses the normalized API base URL", () => {
    expect(getApiBaseUrl()).toBe("http://localhost:8080");
    expect(getWsBaseUrl()).toBe("ws://localhost:8080");
  });

  it("throws ApiError on non-ok responses", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 503,
      text: async () => "dependency unavailable",
    } as Response);

    await expect(apiFetch("/health/ready")).rejects.toEqual(
      expect.objectContaining({
        status: 503,
        name: "ApiError",
        message: "dependency unavailable",
      }),
    );
  });

  it("normalizes today's daily win from the mounted backend contract", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        daily_win: {
          briefing_id: "brief-1",
          briefing_date: "2026-04-16",
          generated_at: "2026-04-16T07:30:00.000Z",
          lead_summary: "Pipeline quality improved after yesterday's campaign review.",
          full_briefing: "Campaign review and follow-up task completion pushed qualified demand.",
          recommended_action: "Review campaign progress",
          recommended_action_type: "review_campaign",
          recommended_action_data: { campaign_id: "campaign-1" },
          viewed_at: null,
        },
        status: "ok",
      }),
    } as Response);

    await expect(dailyWinsApi.getToday()).resolves.toEqual(
      expect.objectContaining({
        win_id: "brief-1",
        strategist_name: "Strategist",
        todays_focus: expect.objectContaining({
          action: "Review campaign progress",
          action_type: "review_campaign",
          action_data: { campaign_id: "campaign-1" },
        }),
      }),
    );
  });
});
