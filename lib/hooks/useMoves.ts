import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getMoves,
  getTodaysMoves,
  getMoveById,
  createMove,
  updateMove,
  shipMove,
  deleteMove,
} from "@/lib/api/moves";
import { Move } from "@/lib/types";

export function useMoves(campaignId?: string) {
  return useQuery({
    queryKey: ["moves", campaignId],
    queryFn: () => getMoves(campaignId),
    staleTime: 1000 * 60 * 5,
  });
}

export function useTodaysMoves() {
  return useQuery({
    queryKey: ["moves", "today"],
    queryFn: getTodaysMoves,
    staleTime: 1000 * 60 * 2,
  });
}

export function useMoveById(id: string) {
  return useQuery({
    queryKey: ["move", id],
    queryFn: () => getMoveById(id),
    staleTime: 1000 * 60 * 5,
  });
}

export function useCreateMove() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createMove,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["moves"] });
    },
  });
}

export function useUpdateMove() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: Partial<Move> }) =>
      updateMove(id, updates),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["moves"] });
      queryClient.setQueryData(["move", data.id], data);
    },
  });
}

export function useShipMove() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      proofUrl,
      proofScreenshot,
    }: {
      id: string;
      proofUrl: string;
      proofScreenshot?: string;
    }) => shipMove(id, proofUrl, proofScreenshot),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["moves"] });
      queryClient.setQueryData(["move", data.id], data);
    },
  });
}

export function useDeleteMove() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteMove,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["moves"] });
    },
  });
}
