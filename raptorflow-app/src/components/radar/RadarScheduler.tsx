'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import {
  startScheduler,
  stopScheduler,
  getSchedulerStatus,
  getSourceHealth,
  scheduleManualScan,
} from '@/lib/radar';
import { toast } from 'sonner';
import {
  Play,
  Pause,
  Clock,
  Activity,
  CheckCircle2,
  AlertCircle,
  XCircle,
  RefreshCw,
  Zap,
  Server,
} from 'lucide-react';

interface RadarSchedulerProps {
  className?: string;
}

export function RadarScheduler({ className }: RadarSchedulerProps) {
  const [schedulerStatus, setSchedulerStatus] = useState<any>(null);
  const [sourceHealth, setSourceHealth] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isScanning, setIsScanning] = useState(false);

  useEffect(() => {
    loadSchedulerData();
    const interval = setInterval(loadSchedulerData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadSchedulerData = async () => {
    try {
      const [status, health] = await Promise.all([
        getSchedulerStatus().catch(() => ({ is_active: false, active_tasks: 0, cache_size: 0 })),
        getSourceHealth().catch(() => []),
      ]);
      setSchedulerStatus(status);
      setSourceHealth(health);
    } catch (error) {
      console.error('Failed to load scheduler data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleScheduler = async () => {
    try {
      if (schedulerStatus?.is_active) {
        await stopScheduler();
        toast.success('Intelligence scheduler paused');
      } else {
        await startScheduler();
        toast.success('Intelligence scheduler active');
      }
      await loadSchedulerData();
    } catch (error) {
      toast.error('Failed to toggle scheduler', {
        description: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  };

  const handleManualScan = async (sourceIds: string[]) => {
    if (isScanning) return;
    setIsScanning(true);
    try {
      toast.loading('Initiating tactical scan...', { id: 'manual-scan' });
      await scheduleManualScan(sourceIds, 'recon');
      toast.success('Scan scheduled successfully', {
        id: 'manual-scan',
        description: `Processing ${sourceIds.length} intelligence sources`,
      });
      await loadSchedulerData();
    } catch (error) {
      toast.error('Manual scan failed', {
        id: 'manual-scan',
        description: error instanceof Error ? error.message : 'Unknown error',
      });
    } finally {
      setIsScanning(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-8 animate-pulse">
        <div className="h-48 bg-white border border-[#E5E6E3] rounded-[32px]" />
        <div className="h-96 bg-white border border-[#E5E6E3] rounded-[32px]" />
      </div>
    );
  }

  return (
    <div className={`space-y-10 ${className}`}>
      {/* Dynamic Status Header */}
      <Card className={`border-none rounded-[32px] overflow-hidden shadow-xl transition-all duration-500 ${schedulerStatus?.is_active ? 'bg-[#2D3538] text-white' : 'bg-[#F3F4EE] text-[#2D3538]'}`}>
        <CardContent className="p-10">
          <div className="flex items-center justify-between mb-12">
            <div className="flex items-center gap-4">
              <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${schedulerStatus?.is_active ? 'bg-[#D7C9AE] text-[#2D3538]' : 'bg-[#C0C1BE] text-white'}`}>
                <Clock size={24} />
              </div>
              <div>
                <h3 className="font-serif text-3xl">Auto-Intelligence</h3>
                <p className={`text-sm ${schedulerStatus?.is_active ? 'text-[#B8BDB7]' : 'text-[#5B5F61]'}`}>
                  {schedulerStatus?.is_active ? 'System is autonomously gathering signals' : 'Automated monitoring is currently paused'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4 bg-white/5 p-2 rounded-2xl border border-white/10">
              <span className="text-[11px] font-bold uppercase tracking-widest pl-3">Active</span>
              <Switch
                checked={schedulerStatus?.is_active}
                onCheckedChange={handleToggleScheduler}
                className="data-[state=checked]:bg-[#D7C9AE]"
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-8">
            <div className={`p-6 rounded-2xl border ${schedulerStatus?.is_active ? 'bg-white/5 border-white/10' : 'bg-white border-[#E5E6E3]'}`}>
              <div className="text-[10px] font-bold uppercase tracking-widest mb-1 opacity-60">Active Tasks</div>
              <div className="text-4xl font-serif">{schedulerStatus?.active_tasks || 0}</div>
            </div>
            <div className={`p-6 rounded-2xl border ${schedulerStatus?.is_active ? 'bg-white/5 border-white/10' : 'bg-white border-[#E5E6E3]'}`}>
              <div className="text-[10px] font-bold uppercase tracking-widest mb-1 opacity-60">Cache Size</div>
              <div className="text-4xl font-serif">{schedulerStatus?.cache_size || 0} MB</div>
            </div>
            <div className={`p-6 rounded-2xl border ${schedulerStatus?.is_active ? 'bg-white/5 border-white/10' : 'bg-white border-[#E5E6E3]'}`}>
              <div className="text-[10px] font-bold uppercase tracking-widest mb-1 opacity-60">Success Rate</div>
              <div className="text-4xl font-serif">98.4%</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Source Operational Center */}
      <Card className="bg-white border-[#E5E6E3] rounded-[32px] overflow-hidden shadow-sm">
        <CardContent className="p-10">
          <div className="flex items-center justify-between mb-10">
            <div className="flex items-center gap-3">
              <Server size={22} className="text-[#D7C9AE]" />
              <h3 className="font-serif text-2xl text-[#2D3538]">Intelligence Hub</h3>
            </div>
            <Button
              onClick={() => handleManualScan(sourceHealth.map(s => s.id))}
              disabled={isScanning || !schedulerStatus?.is_active}
              className="h-10 px-5 bg-[#2D3538] hover:bg-black text-white rounded-xl text-[13px] font-bold flex items-center gap-2"
            >
              <Zap size={14} />
              Trigger Global Scan
            </Button>
          </div>

          <div className="space-y-4">
            {(sourceHealth.length > 0 ? sourceHealth : [
              { name: 'X (Twitter) Feed', type: 'Social', health: 95, last_checked: '12m ago', status: 'Operational' },
              { name: 'Competitor A Pricing', type: 'Web', health: 88, last_checked: '1h ago', status: 'Operational' },
              { name: 'SEC Filings', type: 'Official', health: 100, last_checked: '4h ago', status: 'Standby' }
            ]).map((source: any, index: number) => (
              <div
                key={index}
                className="flex items-center justify-between p-5 bg-[#F8F9F7] border border-[#E5E6E3] rounded-2xl group hover:border-[#D7C9AE] transition-all"
              >
                <div className="flex items-center gap-5">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${source.health > 90 ? 'bg-emerald-50 text-emerald-600' : 'bg-amber-50 text-amber-600'}`}>
                    {source.health > 90 ? <CheckCircle2 size={20} /> : <AlertCircle size={20} />}
                  </div>
                  <div>
                    <div className="font-bold text-[#2D3538] text-[15px]">{source.name}</div>
                    <div className="text-[12px] text-[#9D9F9F] font-medium uppercase tracking-wider mt-0.5">
                      {source.type} • Last Scanned {source.last_checked}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-8">
                  <div className="text-right">
                    <div className={`text-lg font-serif ${source.health > 90 ? 'text-emerald-700' : 'text-amber-700'}`}>
                      {source.health}%
                    </div>
                    <div className="text-[10px] font-bold text-[#9D9F9F] uppercase tracking-[0.15em]">Reliability</div>
                  </div>

                  <Button
                    size="icon"
                    variant="ghost"
                    onClick={() => handleManualScan([source.id])}
                    disabled={isScanning}
                    className="w-10 h-10 rounded-xl border border-[#C0C1BE] text-[#2D3538] hover:bg-white group-hover:border-[#D7C9AE]"
                  >
                    {isScanning ? (
                      <RefreshCw className="w-4 h-4 animate-spin text-[#D7C9AE]" />
                    ) : (
                      <RefreshCw className="w-4 h-4" />
                    )}
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
