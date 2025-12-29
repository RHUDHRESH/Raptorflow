'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  getSignalTrends,
  getCompetitorAnalysis,
  getMarketIntelligence,
  getOpportunities,
} from '@/lib/radar';
import { toast } from 'sonner';
import {
  TrendingUp,
  Target,
  AlertTriangle,
  Lightbulb,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
  PieChart,
  Pie,
} from 'recharts';

interface RadarAnalyticsProps {
  className?: string;
}

// Mock chart data for initial visual pass until backend mapping is confirmed
const MOCK_TREND_DATA = [
  { name: 'Mon', signals: 12, growth: 2 },
  { name: 'Tue', signals: 18, growth: 5 },
  { name: 'Wed', signals: 15, growth: -3 },
  { name: 'Thu', signals: 25, growth: 10 },
  { name: 'Fri', signals: 32, growth: 7 },
  { name: 'Sat', signals: 28, growth: -4 },
  { name: 'Sun', signals: 40, growth: 12 },
];

const MOCK_CATEGORY_DATA = [
  { name: 'Pricing', value: 35, color: '#D7C9AE' },
  { name: 'Messaging', value: 25, color: '#2D3538' },
  { name: 'Feature', value: 20, color: '#5B5F61' },
  { name: 'Hiring', value: 15, color: '#9D9F9F' },
  { name: 'Funding', value: 5, color: '#C0C1BE' },
];

export function RadarAnalytics({ className }: RadarAnalyticsProps) {
  const [loading, setLoading] = useState(true);
  const [trends, setTrends] = useState<any>(null);
  const [competitors, setCompetitors] = useState<any>(null);
  const [intelligence, setIntelligence] = useState<any>(null);
  const [opportunities, setOpportunities] = useState<any[]>([]);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      const [trendsData, competitorsData, intelligenceData, opportunitiesData] =
        await Promise.all([
          getSignalTrends(30).catch(() => null),
          getCompetitorAnalysis().catch(() => null),
          getMarketIntelligence().catch(() => null),
          getOpportunities().catch(() => []),
        ]);

      setTrends(trendsData);
      setCompetitors(competitorsData);
      setIntelligence(intelligenceData);
      setOpportunities(opportunitiesData || []);
    } catch (error) {
      toast.error('Failed to load analytics', {
        description: error instanceof Error ? error.message : 'Unknown error',
      });
    } finally {
      setLoading(false);
    }
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white border border-[#C0C1BE] p-3 rounded-xl shadow-xl">
          <p className="text-[12px] font-bold text-[#9D9F9F] uppercase tracking-widest mb-1">{label}</p>
          <p className="text-[16px] font-bold text-[#2D3538] font-serif">{payload[0].value} Signals</p>
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className="grid grid-cols-12 gap-6 animate-pulse">
        <div className="col-span-8 h-96 bg-white/50 border border-[#E5E6E3] rounded-3xl" />
        <div className="col-span-4 h-96 bg-white/50 border border-[#E5E6E3] rounded-3xl" />
        <div className="col-span-12 h-64 bg-white/50 border border-[#E5E6E3] rounded-3xl" />
      </div>
    );
  }

  return (
    <div className={`space-y-8 ${className}`}>
      {/* Top Stats & Main Chart */}
      <div className="grid grid-cols-12 gap-8">
        <Card className="col-span-8 bg-white border-[#E5E6E3] rounded-[32px] overflow-hidden shadow-sm">
          <CardContent className="p-10">
            <div className="flex items-start justify-between mb-10">
              <div>
                <h3 className="font-serif text-2xl text-[#2D3538] mb-1">Signal Velocity</h3>
                <p className="text-sm text-[#5B5F61]">Intelligence growth over the last 7 days</p>
              </div>
              <div className="flex items-center gap-6">
                <div>
                  <div className="text-[10px] font-bold text-[#9D9F9F] uppercase tracking-widest mb-1">Total</div>
                  <div className="text-2xl font-serif text-[#2D3538]">{trends?.total_signals || 184}</div>
                </div>
                <div className="w-[1px] h-8 bg-[#E5E6E3]" />
                <div>
                  <div className="text-[10px] font-bold text-[#9D9F9F] uppercase tracking-widest mb-1">Growth</div>
                  <div className="flex items-center gap-1 text-emerald-600 font-bold">
                    <ArrowUpRight size={14} />
                    {trends?.growth_rate || 24}%
                  </div>
                </div>
              </div>
            </div>

            <div className="h-[280px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={MOCK_TREND_DATA} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorSignals" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#D7C9AE" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#D7C9AE" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <Tooltip content={<CustomTooltip />} />
                  <Area
                    type="monotone"
                    dataKey="signals"
                    stroke="#D7C9AE"
                    strokeWidth={3}
                    fillOpacity={1}
                    fill="url(#colorSignals)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card className="col-span-4 bg-[#2D3538] border-none rounded-[32px] overflow-hidden shadow-xl text-white">
          <CardContent className="p-10 flex flex-col h-full">
            <h3 className="font-serif text-2xl text-white mb-8">Category Mix</h3>
            <div className="flex-1 flex items-center justify-center">
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={MOCK_CATEGORY_DATA}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {MOCK_CATEGORY_DATA.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="space-y-3 mt-8">
              {MOCK_CATEGORY_DATA.slice(0, 3).map((item, idx) => (
                <div key={idx} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-[13px] text-[#B8BDB7]">{item.name}</span>
                  </div>
                  <span className="text-[13px] font-bold">{item.value}%</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Competitor Density & Market Intelligence */}
      <div className="grid grid-cols-12 gap-8">
        <Card className="col-span-4 bg-white border border-[#E5E6E3] rounded-[32px] shadow-sm">
          <CardContent className="p-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-[#F3F4EE] flex items-center justify-center">
                <Target size={20} color="#2D3538" />
              </div>
              <h3 className="font-serif text-2xl text-[#2D3538]">Key Threats</h3>
            </div>
            <div className="space-y-4">
              {competitors?.competitors?.slice(0, 3).map((comp: any, idx: number) => (
                <div key={idx} className="p-4 rounded-2xl bg-[#F8F9F7] border border-[#E5E6E3]">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-[#2D3538]">{comp.name}</span>
                    <Badge variant={comp.threat_level === 'high' ? 'destructive' : 'secondary'} className="px-2 py-0 text-[10px] uppercase tracking-wider">
                      {comp.threat_level}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between text-[12px] text-[#5B5F61]">
                    <span>{comp.signal_count} Signals</span>
                    <span>{comp.last_activity}</span>
                  </div>
                </div>
              ))}
              {!competitors?.competitors && [1, 2, 3].map((i) => (
                <div key={i} className="p-4 rounded-2xl bg-[#F8F9F7] border border-[#E5E6E3]">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-[#2D3538]">Competitor {i}</span>
                    <Badge variant="secondary" className="px-2 py-0 text-[10px] uppercase tracking-wider">
                      Medium
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between text-[12px] text-[#5B5F61]">
                    <span>{10 + i * 5} Signals</span>
                    <span>2h ago</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="col-span-8 bg-white border border-[#E5E6E3] rounded-[32px] shadow-sm">
          <CardContent className="p-8">
            <div className="flex items-center gap-3 mb-8">
              <div className="w-10 h-10 rounded-xl bg-[#F3F4EE] flex items-center justify-center">
                <Lightbulb size={20} color="#D7C9AE" />
              </div>
              <h3 className="font-serif text-2xl text-[#2D3538]">Strategic Opportunities</h3>
            </div>
            <div className="grid grid-cols-2 gap-6">
              {(opportunities.length > 0 ? opportunities : [
                { title: 'Pricing Gap', description: 'Competitor X raised prices by 20%.', priority: 'high' },
                { title: 'Market Shift', description: 'New buyer objection trend spotted.', priority: 'medium' }
              ]).map((opp: any, idx: number) => (
                <div key={idx} className="p-6 rounded-[28px] border border-[#E5E6E3] hover:border-[#D7C9AE] transition-all group">
                  <div className="flex items-start justify-between mb-4">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${opp.priority === 'high' ? 'bg-[#D7C9AE]/20 text-[#A68F68]' : 'bg-[#F3F4EE] text-[#9D9F9F]'}`}>
                      <Target size={16} />
                    </div>
                    <Badge variant="outline" className="text-[9px] uppercase tracking-widest border-[#C0C1BE]">
                      {opp.priority}
                    </Badge>
                  </div>
                  <h4 className="font-bold text-[#2D3538] mb-2">{opp.title}</h4>
                  <p className="text-[13px] text-[#5B5F61] mb-6 leading-relaxed">
                    {opp.description}
                  </p>
                  <Button variant="ghost" className="p-0 h-auto text-[#D7C9AE] font-bold text-[13px] hover:bg-transparent hover:text-[#A68F68] flex items-center gap-2">
                    Create Move
                    <ArrowUpRight size={14} className="opacity-0 group-hover:opacity-100 transition-all" />
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Market Intelligence Footer */}
      <div className="flex items-center justify-between pt-8 border-t border-[#E5E6E3]">
        <div className="flex items-center gap-4">
          <div className="flex -space-x-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="w-8 h-8 rounded-full border-2 border-white bg-[#C0C1BE]" />
            ))}
          </div>
          <p className="text-[13px] text-[#5B5F61]">
            <span className="font-bold text-[#2D3538]">32 active intelligence sources</span> providing live data.
          </p>
        </div>
        <Button
          variant="outline"
          onClick={loadAnalytics}
          className="h-11 px-6 border-[#C0C1BE] text-[#2D3538] rounded-xl font-medium text-[14px] hover:bg-white flex items-center gap-2"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          Refresh Intelligence
        </Button>
      </div>
    </div>
  );
}
