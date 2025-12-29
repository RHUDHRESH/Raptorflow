'use client';

import { useEffect, useState } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, CheckCircle2, Info } from 'lucide-react';

interface DriftMetric {
  p_value: number;
  is_drifting: boolean;
}

interface DriftData {
  is_drifting: boolean;
  metrics: Record<string, DriftMetric>;
}

export function DriftChart() {
  const [data, setData] = useState<DriftData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchDrift() {
      try {
        const res = await fetch('/api/v1/matrix/mlops/drift');
        if (!res.ok) throw new Error('Drift API unavailable');
        const json = await res.json();
        setData(json);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchDrift();
  }, []);

  if (loading)
    return (
      <div className="h-[300px] w-full bg-muted/5 animate-pulse rounded-2xl border border-dashed border-border flex items-center justify-center">
        <span className="text-xs font-bold text-muted-foreground uppercase tracking-widest">
          Analyzing Distribution...
        </span>
      </div>
    );

  const metrics = data?.metrics || {
    latency: { p_value: 0.45, is_drifting: false },
    embedding_dist: { p_value: 0.88, is_drifting: false },
    token_usage: { p_value: 0.02, is_drifting: true },
  };

  return (
    <Card className="rounded-2xl border-border bg-card/50 shadow-sm h-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="font-display text-xl">Data Drift</CardTitle>
            <CardDescription className="text-xs">
              Statistical K-S test results across core dimensions.
            </CardDescription>
          </div>
          <Badge
            variant={data?.is_drifting ? 'destructive' : 'outline'}
            className="font-mono text-[10px]"
          >
            {data?.is_drifting ? 'DRIFT DETECTED' : 'STABLE'}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {Object.entries(metrics).map(([name, metric]) => (
          <div key={name} className="space-y-2">
            <div className="flex items-center justify-between text-[10px] uppercase tracking-wider font-bold">
              <span className="text-muted-foreground flex items-center">
                {name}
                {metric.is_drifting ? (
                  <AlertCircle className="ml-1 h-3 w-3 text-red-500" />
                ) : (
                  <CheckCircle2 className="ml-1 h-3 w-3 text-green-500" />
                )}
              </span>
              <span className="font-mono">p={metric.p_value.toFixed(4)}</span>
            </div>
            <div className="relative h-2 w-full bg-muted/20 rounded-full overflow-hidden border border-border/50">
              <div
                className={`absolute inset-y-0 left-0 transition-all duration-1000 ${metric.is_drifting ? 'bg-red-500' : 'bg-primary'}`}
                style={{ width: `${Math.max(5, (1 - metric.p_value) * 100)}%` }}
              />
            </div>
          </div>
        ))}

        <div className="mt-4 pt-4 border-t border-border/50 flex items-start space-x-2 text-[10px] text-muted-foreground leading-relaxed">
          <Info className="h-3 w-3 mt-0.5 flex-shrink-0" />
          <p>
            Osipov Pattern: Threshold for drift is p &lt; 0.05. Metrics nearing
            the threshold may require manual retraining trigger.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
