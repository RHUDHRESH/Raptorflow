'use client';

import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

export function MatrixMetricSkeleton() {
  return (
    <Card className="rounded-2xl border-border bg-card/50 shadow-sm animate-pulse">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <Skeleton className="h-4 w-[100px]" />
        <Skeleton className="h-4 w-4 rounded-full" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-8 w-[60px] mb-2" />
        <Skeleton className="h-3 w-[120px]" />
      </CardContent>
    </Card>
  );
}

export function MatrixListSkeleton() {
  return (
    <Card className="rounded-2xl border-border bg-card/50 shadow-sm overflow-hidden h-full">
      <CardHeader className="border-b border-border/50 bg-muted/5">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <Skeleton className="h-5 w-[150px]" />
            <Skeleton className="h-3 w-[200px]" />
          </div>
          <Skeleton className="h-5 w-[60px] rounded-full" />
        </div>
      </CardHeader>
      <CardContent className="p-4 space-y-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="flex items-center space-x-4">
            <Skeleton className="h-10 w-10 rounded-lg" />
            <div className="space-y-2 flex-1">
              <Skeleton className="h-4 w-[140px]" />
              <Skeleton className="h-3 w-full" />
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
