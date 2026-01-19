"use client";

import React from "react";
import { BlueprintSkeleton } from "./BlueprintSkeleton";
import { cn } from "@/lib/utils";

/**
 * Skeleton for the Foundation Dashboard
 */
export function FoundationSkeleton() {
  return (
    <div className="relative max-w-7xl mx-auto pb-12 space-y-10 animate-in fade-in duration-500">
      {/* Header Skeleton */}
      <div className="space-y-4">
        <div className="flex items-center gap-4">
          <BlueprintSkeleton variant="text" className="w-24 h-3" />
          <div className="h-px w-12 bg-[var(--structure-subtle)]" />
          <BlueprintSkeleton variant="text" className="w-16 h-3" />
        </div>
        <BlueprintSkeleton variant="text" className="w-64 h-10" />
        <BlueprintSkeleton variant="text" className="w-96 h-4" />
      </div>

      {/* Positioning Card Skeleton */}
      <section className="space-y-6">
        <div className="flex items-center gap-3">
          <BlueprintSkeleton variant="text" className="w-32 h-3" />
          <div className="h-px w-12 bg-[var(--structure-subtle)]" />
          <div className="h-px flex-1 bg-[var(--structure-subtle)]" />
        </div>
        <BlueprintSkeleton variant="card" className="h-40" />
      </section>

      {/* ICPs Grid Skeleton */}
      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <BlueprintSkeleton variant="text" className="w-24 h-3" />
            <div className="h-px w-12 bg-[var(--structure-subtle)]" />
          </div>
          <BlueprintSkeleton variant="text" className="w-24 h-9 rounded-[var(--radius)]" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <BlueprintSkeleton variant="card" className="h-64" />
          <BlueprintSkeleton variant="card" className="h-64" />
          <BlueprintSkeleton variant="card" className="h-64" />
        </div>
      </section>

      {/* Messaging Skeleton */}
      <section className="space-y-6">
        <div className="flex items-center gap-3">
          <BlueprintSkeleton variant="text" className="w-32 h-3" />
          <div className="h-px w-12 bg-[var(--structure-subtle)]" />
          <div className="h-px flex-1 bg-[var(--structure-subtle)]" />
        </div>
        <BlueprintSkeleton variant="card" className="h-48" />
      </section>
    </div>
  );
}

/**
 * Skeleton for the Moves Dashboard
 */
export function MovesSkeleton() {
  return (
    <div className="min-h-screen animate-in fade-in duration-500">
      {/* Header Skeleton */}
      <div className="border-b border-[var(--border)] bg-[var(--paper)]">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-start justify-between">
            <div className="space-y-3">
              <BlueprintSkeleton variant="text" className="w-48 h-8" />
              <BlueprintSkeleton variant="text" className="w-96 h-4" />
            </div>
            <div className="flex gap-3">
              <BlueprintSkeleton variant="text" className="w-40 h-10" />
              <BlueprintSkeleton variant="text" className="w-32 h-10" />
            </div>
          </div>
          {/* Tabs Skeleton */}
          <div className="flex items-center gap-8 mt-6">
            <BlueprintSkeleton variant="text" className="w-24 h-8" />
            <BlueprintSkeleton variant="text" className="w-24 h-8" />
            <BlueprintSkeleton variant="text" className="w-24 h-8" />
          </div>
        </div>
      </div>

      {/* Content Skeleton */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="max-w-3xl space-y-6">
          <BlueprintSkeleton variant="card" className="h-32" />
          <BlueprintSkeleton variant="card" className="h-32" />
          <BlueprintSkeleton variant="card" className="h-32" />
        </div>
      </div>
    </div>
  );
}
