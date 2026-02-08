import type { Move } from "@/components/moves/types";
import { apiRequest } from "./http";

type MoveListResponse = { moves: Move[] };

export type MovePatch = Partial<
  Pick<
    Move,
    | "name"
    | "category"
    | "status"
    | "duration"
    | "goal"
    | "tone"
    | "context"
    | "attachments"
    | "startDate"
    | "endDate"
    | "execution"
    | "progress"
    | "icp"
    | "campaignId"
    | "metrics"
  >
>;

export const movesService = {
  async list(workspaceId: string): Promise<Move[]> {
    const data = await apiRequest<MoveListResponse>("/moves", {
      method: "GET",
      workspaceId,
    });
    return data.moves ?? [];
  },

  async create(workspaceId: string, move: Move): Promise<Move> {
    return apiRequest<Move>("/moves", {
      method: "POST",
      workspaceId,
      body: JSON.stringify(move),
    });
  },

  async update(workspaceId: string, moveId: string, patch: MovePatch): Promise<Move> {
    return apiRequest<Move>(`/moves/${encodeURIComponent(moveId)}`, {
      method: "PATCH",
      workspaceId,
      body: JSON.stringify(patch),
    });
  },

  async delete(workspaceId: string, moveId: string): Promise<void> {
    await apiRequest<void>(`/moves/${encodeURIComponent(moveId)}`, {
      method: "DELETE",
      workspaceId,
    });
  },
};

