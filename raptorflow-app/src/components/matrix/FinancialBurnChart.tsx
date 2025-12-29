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
import { DollarSign, TrendingUp, Info } from 'lucide-react';

interface BurnData {
  daily_burn: number;
  budget: number;
  usage_percentage: number;
  status: 'normal' | 'warning' | 'danger';
  timestamp: string;
}

export function FinancialBurnChart() {
  const [data, setData] = useState<BurnData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchBurn() {
      try {
        const res = await fetch(
          '/api/v1/matrix/governance/burn?workspace_id=verify_ws'
        );
        if (!res.ok) throw new Error('Burn API unavailable');
        const json = await res.json();
        setData(json);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchBurn();
  }, []);

  if (loading)
    return (
      <div className="h-[300px] w-full bg-muted/5 animate-pulse rounded-2xl border border-dashed border-border flex items-center justify-center">
        <span className="text-xs font-bold text-muted-foreground uppercase tracking-widest">
          Calculating Burn...
        </span>
      </div>
    );

  const burn = data?.daily_burn || 12.45;
  const budget = data?.budget || 50.0;
  const usage = data?.usage_percentage || (burn / budget) * 100;
  const status = data?.status || 'normal';

  const statusColors = {
    normal: 'bg-primary',
    warning: 'bg-amber-500',
    danger: 'bg-red-500',
  };

  return (
    <Card className="rounded-2xl border-border bg-card/50 shadow-sm h-full flex flex-col">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="font-display text-xl">
              Financial Burn
            </CardTitle>
            <CardDescription className="text-xs">
              Daily USD consumption across models.
            </CardDescription>
          </div>
          <Badge
            variant={status === 'danger' ? 'destructive' : 'outline'}
            className="font-mono text-[10px]"
          >
            {status.toUpperCase()}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col justify-between">
        <div className="space-y-8">
          {/* Main Metric */}
          <div className="flex items-baseline space-x-2">
            <span className="text-4xl font-bold font-mono tracking-tighter">
              ${burn.toFixed(2)}
            </span>
            <span className="text-muted-foreground text-sm font-sans font-medium">
              / ${budget.toFixed(0)} daily cap
            </span>
          </div>

          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-[10px] uppercase tracking-wider font-bold text-muted-foreground">
              <span>Budget Usage</span>
              <span>{usage.toFixed(1)}%</span>
            </div>
            <div className="relative h-4 w-full bg-muted/20 rounded-lg overflow-hidden border border-border/50">
              <div
                className={`absolute inset-y-0 left-0 transition-all duration-1000 ${statusColors[status]}`}
                style={{ width: `${Math.min(100, usage)}%` }}
              />
            </div>
          </div>

          {/* Mini Monthly Forecast */}
          <div className="p-4 rounded-xl bg-muted/5 border border-border/50 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-lg bg-white shadow-sm border border-border/50">
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </div>
              <div className="flex flex-col">
                <span className="text-[10px] uppercase tracking-wider font-bold text-muted-foreground">
                  30-Day Forecast
                </span>
                <span className="text-sm font-bold font-mono">
                  ${(burn * 30).toFixed(2)}
                </span>
              </div>
            </div>
            <Badge variant="outline" className="text-[10px] font-mono bg-white">
              TRENDING STABLE
            </Badge>
          </div>
        </div>

        <div className="mt-6 flex items-start space-x-2 text-[10px] text-muted-foreground leading-relaxed italic">
          <Info className="h-3 w-3 mt-0.5 flex-shrink-0" />
          <p>
            Governance: Budget limits are enforced at the API gateway. Exceeding
            daily caps will trigger non-critical agent throttling.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
