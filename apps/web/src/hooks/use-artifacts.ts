"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { capabilitiesApi, CreateArtifactVersionRequest } from "@/lib/api";

export function useArtifacts(params?: { artifact_type?: string; status?: string; limit?: number }) {
  return useQuery({
    queryKey: ["artifacts", params],
    queryFn: () => capabilitiesApi.listArtifacts(params),
  });
}

export function useArtifact(id: string) {
  return useQuery({
    queryKey: ["artifacts", id],
    queryFn: () => capabilitiesApi.getArtifact(id),
    enabled: !!id,
  });
}

export function useCreateArtifactVersion() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      artifactId,
      body,
    }: {
      artifactId: string;
      body: CreateArtifactVersionRequest;
    }) => capabilitiesApi.createArtifactVersion(artifactId, body),
    onSuccess: (_, { artifactId }) => {
      queryClient.invalidateQueries({ queryKey: ["artifacts", artifactId] });
    },
  });
}
