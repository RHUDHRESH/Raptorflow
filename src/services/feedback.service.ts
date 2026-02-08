import { apiRequest } from "./http";

export const feedbackService = {
  async submitFeedback(
    workspaceId: string,
    generationId: string,
    score: number,
    edits?: string
  ): Promise<{ success: boolean; memory_id: string }> {
    return apiRequest<{ success: boolean; memory_id: string }>(
      "/context/feedback/",
      {
        method: "POST",
        workspaceId,
        body: JSON.stringify({
          generation_id: generationId,
          score,
          edits,
        }),
      }
    );
  },
};
