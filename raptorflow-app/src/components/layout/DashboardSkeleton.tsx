'use client';

import { Skeleton } from "@/components/ui/skeleton";

/**
 * Dashboard Skeleton - Loading state for the Dashboard
 * Philosophy: "The structure is already there, content is arriving"
 */
export function DashboardSkeleton() {
    return (
        <div className="flex flex-col gap-16 md:gap-24 pb-24 animate-pulse">
            {/* Header Skeleton */}
            <section className="flex flex-col gap-6 max-w-2xl">
                <Skeleton className="h-14 w-72" />
                <Skeleton className="h-6 w-96" />
            </section>

            {/* Hero Card Skeleton */}
            <div className="rounded-xl bg-card p-8 md:p-10 space-y-6 shadow-sm">
                <div className="space-y-4">
                    <Skeleton className="h-3 w-32" />
                    <Skeleton className="h-12 w-3/4" />
                    <Skeleton className="h-5 w-1/2" />
                </div>
                <div className="flex justify-between items-center pt-4">
                    <Skeleton className="h-4 w-40" />
                    <Skeleton className="h-12 w-40 rounded-lg" />
                </div>
            </div>

            {/* Focus List Skeleton */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-16 lg:gap-12">
                <div className="lg:col-span-7 space-y-4">
                    <Skeleton className="h-3 w-24" />
                    <div className="space-y-2 border-t border-b border-border/40 py-4">
                        {[...Array(5)].map((_, i) => (
                            <div key={i} className="flex justify-between items-center py-4">
                                <div className="flex items-center gap-4">
                                    <Skeleton className="h-5 w-5 rounded-full" />
                                    <Skeleton className="h-5 w-28" />
                                </div>
                                <Skeleton className="h-4 w-32" />
                            </div>
                        ))}
                    </div>
                </div>

                <div className="lg:col-span-5 space-y-4">
                    <Skeleton className="h-3 w-28" />
                    <div className="p-8 rounded-lg border border-border/60 space-y-6">
                        <div className="flex justify-between">
                            <Skeleton className="h-6 w-24" />
                            <Skeleton className="h-4 w-16" />
                        </div>
                        <Skeleton className="h-1 w-full" />
                        <div className="space-y-3">
                            <Skeleton className="h-4 w-full" />
                            <Skeleton className="h-4 w-3/4" />
                        </div>
                    </div>
                </div>
            </div>

            {/* Metrics Skeleton */}
            <section className="border-t border-border/40 pt-16">
                <div className="flex flex-wrap gap-x-24 gap-y-12">
                    {[...Array(4)].map((_, i) => (
                        <div key={i} className="space-y-3">
                            <Skeleton className="h-3 w-20" />
                            <Skeleton className="h-10 w-24" />
                        </div>
                    ))}
                </div>
            </section>
        </div>
    );
}
