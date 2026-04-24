"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { billingApi } from "@/lib/api";
import type { CreateOrderRequest } from "@/lib/api";

export function useBillingStatus() {
  return useQuery({
    queryKey: ["billing"],
    queryFn: () => billingApi.getStatus(),
  });
}

export function useCreateOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: CreateOrderRequest) => billingApi.createOrder(body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["billing"] });
    },
  });
}

export function useSubscription(id: string) {
  return useQuery({
    queryKey: ["billing", "subscriptions", id],
    queryFn: () => billingApi.getSubscription(id),
    enabled: !!id,
  });
}

export function useCancelSubscription() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => billingApi.cancelSubscription(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["billing"] });
    },
  });
}
