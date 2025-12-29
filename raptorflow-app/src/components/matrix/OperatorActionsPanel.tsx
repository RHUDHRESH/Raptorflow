'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import {
  Zap,
  RotateCcw,
  Trash2,
  BarChart,
  RefreshCw,
  Loader2,
} from 'lucide-react';
import { toast } from 'sonner';
import { Badge } from '@/components/ui/badge';

export function OperatorActionsPanel() {
  const [throttling, setThrottling] = useState([1000]);
  const [replicas, setReplicas] = useState([1]);
  const [loading, setLoading] = useState<string | null>(null);

  const executeSkill = async (skillName: string, params: any) => {
    setLoading(skillName);
    try {
      const res = await fetch(`/api/v1/matrix/skills/${skillName}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to execute skill.');
      }

      toast.success('Action Successful', {
        description: `Successfully executed ${skillName.replace('_', ' ')}.`,
      });
    } catch (err: any) {
      toast.error('Action Failed', {
        description: err.message,
      });
    } finally {
      setLoading(null);
    }
  };

  return (
    <Card className="rounded-2xl border-stone-200 bg-white/50 backdrop-blur-sm shadow-sm overflow-hidden">
      <CardHeader className="border-b border-stone-100 bg-stone-50/50 py-4">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-xl font-serif text-stone-800">
              Operator Actions
            </CardTitle>
            <CardDescription className="text-stone-500 text-xs">
              Direct system manipulation tools
            </CardDescription>
          </div>
          <Badge
            variant="outline"
            className="font-mono text-[10px] uppercase tracking-wider border-stone-200 text-stone-400"
          >
            Secure Access
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="p-6 space-y-8">
        {/* Inference Throttling */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Zap className="h-4 w-4 text-stone-400" />
              <label className="text-sm font-medium text-stone-700">
                Inference Throttling
              </label>
            </div>
            <span className="text-xs font-mono text-stone-500 bg-stone-100 px-2 py-0.5 rounded">
              {throttling[0]} TPM
            </span>
          </div>
          <Slider
            defaultValue={throttling}
            max={5000}
            step={100}
            onValueChange={setThrottling}
            className="py-4"
            aria-label="token cap"
          />
          <Button
            variant="outline"
            className="w-full rounded-xl h-10 border-stone-200 hover:bg-stone-50 text-stone-600 transition-all duration-300"
            onClick={() =>
              executeSkill('inference_throttling', {
                agent_id: 'global',
                tpm_limit: throttling[0],
              })
            }
            disabled={loading === 'inference_throttling'}
          >
            {loading === 'inference_throttling' ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <RotateCcw className="mr-2 h-4 w-4" />
            )}
            Apply Throttle
          </Button>
        </div>

        {/* Resource Scaling */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <BarChart className="h-4 w-4 text-stone-400" />
              <label className="text-sm font-medium text-stone-700">
                Resource Scaling
              </label>
            </div>
            <span className="text-xs font-mono text-stone-500 bg-stone-100 px-2 py-0.5 rounded">
              {replicas[0]} Replicas
            </span>
          </div>
          <Slider
            defaultValue={replicas}
            min={1}
            max={10}
            step={1}
            onValueChange={setReplicas}
            className="py-4"
          />
          <Button
            variant="outline"
            className="w-full rounded-xl h-10 border-stone-200 hover:bg-stone-50 text-stone-600 transition-all duration-300"
            onClick={() =>
              executeSkill('resource_scaling', {
                service: 'raptor-engine',
                replicas: replicas[0],
              })
            }
            disabled={loading === 'resource_scaling'}
          >
            {loading === 'resource_scaling' ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="mr-2 h-4 w-4" />
            )}
            Scale Service
          </Button>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 gap-3 pt-2">
          <Button
            variant="outline"
            className="rounded-xl h-12 border-stone-200 hover:bg-red-50 hover:text-red-600 hover:border-red-100 transition-all duration-300 group"
            onClick={() => executeSkill('cache_purge', { pattern: '*' })}
            disabled={loading === 'cache_purge'}
          >
            {loading === 'cache_purge' ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Trash2 className="mr-2 h-4 w-4 group-hover:scale-110 transition-transform" />
            )}
            Purge Caches
          </Button>
          <Button
            variant="outline"
            className="rounded-xl h-12 border-stone-200 hover:bg-stone-800 hover:text-white hover:border-stone-800 transition-all duration-300 group"
            onClick={() =>
              executeSkill('retrain_trigger', { model_id: 'raptor-spine-v3' })
            }
            disabled={loading === 'retrain_trigger'}
          >
            {loading === 'retrain_trigger' ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="mr-2 h-4 w-4 group-hover:rotate-180 transition-transform duration-500" />
            )}
            Trigger Retraining
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
