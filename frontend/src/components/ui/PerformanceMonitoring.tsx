'use client';

import React, { useState, useEffect } from 'react';
import { BlueprintCard, BlueprintKPI, BlueprintProgress } from '@/components/ui';
import { Cpu, MemoryStick, HardDrive, Activity, AlertTriangle } from 'lucide-react';

interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network_io: number;
  response_time: number;
  error_rate: number;
  uptime: number;
}

interface MetricCard {
  title: string;
  value: string;
  change: number;
  icon: React.ComponentType<{ size?: number; strokeWidth?: number; className?: string }>;
  trend: 'up' | 'down' | 'neutral';
}

export default function PerformanceMonitoring() {
  const [metrics, setMetrics] = useState<SystemMetrics>({
    cpu_usage: 45,
    memory_usage: 62,
    disk_usage: 78,
    network_io: 23,
    response_time: 120,
    error_rate: 0.2,
    uptime: 99.9
  });

  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      setIsLoading(true);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setMetrics({
        cpu_usage: Math.random() * 100,
        memory_usage: Math.random() * 100,
        disk_usage: Math.random() * 100,
        network_io: Math.random() * 100,
        response_time: Math.random() * 500,
        error_rate: Math.random() * 5,
        uptime: 99.9
      });
      
      setIsLoading(false);
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  const metricCards: MetricCard[] = [
    {
      title: 'CPU Usage',
      value: `${metrics.cpu_usage.toFixed(1)}%`,
      change: metrics.cpu_usage > 80 ? -5 : 2,
      icon: Cpu,
      trend: metrics.cpu_usage > 80 ? 'down' : 'up'
    },
    {
      title: 'Memory Usage',
      value: `${metrics.memory_usage.toFixed(1)}%`,
      change: metrics.memory_usage > 80 ? -3 : 1,
      icon: MemoryStick,
      trend: metrics.memory_usage > 80 ? 'down' : 'up'
    },
    {
      title: 'Disk Usage',
      value: `${metrics.disk_usage.toFixed(1)}%`,
      change: metrics.disk_usage > 90 ? -2 : 0.5,
      icon: HardDrive,
      trend: metrics.disk_usage > 90 ? 'down' : 'neutral'
    },
    {
      title: 'Network I/O',
      value: `${metrics.network_io.toFixed(1)} MB/s`,
      change: 8,
      icon: Activity,
      trend: 'up'
    }
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-[var(--ink)]">System Performance</h1>
        <div className="flex items-center gap-2 text-sm text-[var(--muted)]">
          <Activity size={16} />
          <span>Live</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metricCards.map((card, index) => (
          <BlueprintCard key={index}>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <card.icon 
                    size={20} 
                    className="text-[var(--muted)]"
                  />
                  <span className="font-medium text-[var(--ink)]">{card.title}</span>
                </div>
                <BlueprintKPI
                  label={card.title}
                  value={card.value}
                  trend={card.trend}
                />
              </div>
              <BlueprintProgress 
                value={parseFloat(card.value)}
                max={100}
                className="mt-4"
              />
            </div>
          </BlueprintCard>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <BlueprintCard>
          <div className="p-6">
            <h3 className="text-lg font-semibold mb-4 text-[var(--ink)]">Response Time</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-[var(--muted)]">Average</span>
                <span className="font-mono text-lg">{metrics.response_time.toFixed(0)}ms</span>
              </div>
              <BlueprintProgress 
                value={metrics.response_time}
                max={500}
              />
            </div>
          </div>
        </BlueprintCard>

        <BlueprintCard>
          <div className="p-6">
            <h3 className="text-lg font-semibold mb-4 text-[var(--ink)]">System Health</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-[var(--muted)]">Error Rate</span>
                <div className="flex items-center gap-2">
                  <AlertTriangle size={16} className="text-yellow-500" />
                  <span className="font-mono text-lg">{metrics.error_rate.toFixed(2)}%</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[var(--muted)]">Uptime</span>
                <span className="font-mono text-lg">{metrics.uptime}%</span>
              </div>
            </div>
          </div>
        </BlueprintCard>
      </div>
    </div>
  );
}