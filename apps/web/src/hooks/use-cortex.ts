"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { capabilitiesApi, CreateContextPackRequest } from "@/lib/api";

export function useContextPack(id: string) {
  return useQuery({
    queryKey: ["context-packs", id],
    queryFn: () => capabilitiesApi.getContextPack(id),
    enabled: !!id,
  });
}

export function useCreateContextPack() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: CreateContextPackRequest) => capabilitiesApi.createContextPack(body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["context-packs"] });
    },
  });
}
