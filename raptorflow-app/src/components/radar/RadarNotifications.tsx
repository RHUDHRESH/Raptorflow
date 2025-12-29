'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { processNotifications, getDailyDigest } from '@/lib/radar';
import { toast } from 'sonner';
import {
  Bell,
  BellOff,
  Mail,
  TrendingUp,
  DollarSign,
  Calendar,
  Settings,
  RefreshCw,
  Zap,
  CheckCircle2,
  AlertCircle,
  Clock,
} from 'lucide-react';

interface RadarNotificationsProps {
  className?: string;
}

export function RadarNotifications({ className }: RadarNotificationsProps) {
  const [notifications, setNotifications] = useState<any[]>([]);
  const [dailyDigest, setDailyDigest] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [preferences, setPreferences] = useState({
    highStrengthSignals: true,
    competitorActivitySpikes: true,
    pricingChanges: true,
    dailyDigest: true,
  });

  useEffect(() => {
    loadNotificationData();
  }, []);

  const loadNotificationData = async () => {
    setLoading(true);
    try {
      const [digestData] = await Promise.all([getDailyDigest().catch(() => null)]);
      setDailyDigest(digestData);

      // Mock notifications for now
      const mockNotifications = [
        {
          id: '1',
          type: 'high_strength_signal',
          priority: 'high',
          title: 'High-Strength Signal',
          message: 'Competitor A launched new enterprise pricing tier ($499/mo)',
          created_at: new Date().toISOString(),
        },
        {
          id: '2',
          type: 'competitor_activity_spike',
          priority: 'medium',
          title: 'Activity Spike Detected',
          message: 'Unusual messaging activity detected from 3 direct competitors',
          created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        },
        {
          id: '3',
          type: 'pricing_change',
          priority: 'high',
          title: 'Pricing Strategy Update',
          message: 'Competitor B pivoted their landing page messaging to value-based pricing',
          created_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
        },
      ];
      setNotifications(mockNotifications);
    } catch (error) {
      toast.error('Failed to load notifications', {
        description: error instanceof Error ? error.message : 'Unknown error',
      });
    } finally {
      setLoading(false);
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'high_strength_signal':
        return <TrendingUp className="w-5 h-5 text-[#D7C9AE]" />;
      case 'competitor_activity_spike':
        return <Zap className="w-5 h-5 text-amber-500" />;
      case 'pricing_change':
        return <DollarSign className="w-5 h-5 text-emerald-500" />;
      default:
        return <Bell className="w-5 h-5 text-[#2D3538]" />;
    }
  };

  if (loading) {
    return (
      <div className="space-y-8 animate-pulse">
        <div className="h-64 bg-white border border-[#E5E6E3] rounded-[32px]" />
        <div className="h-96 bg-white border border-[#E5E6E3] rounded-[32px]" />
      </div>
    );
  }

  return (
    <div className={`space-y-10 ${className}`}>
      {/* Configuration Hub */}
      <Card className="bg-white border-[#E5E6E3] rounded-[32px] overflow-hidden shadow-sm">
        <CardContent className="p-10">
          <div className="flex items-center justify-between mb-10">
            <div className="flex items-center gap-3">
              <Settings size={22} className="text-[#D7C9AE]" />
              <h3 className="font-serif text-2xl text-[#2D3538]">Intelligence Alerts</h3>
            </div>
            <Button
              variant="ghost"
              onClick={loadNotificationData}
              className="text-[13px] font-bold text-[#5B5F61] hover:text-[#2D3538] flex items-center gap-2"
            >
              <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
              Refresh
            </Button>
          </div>

          <div className="grid grid-cols-2 gap-8">
            {[
              { key: 'highStrengthSignals', label: 'Strategic Signals', desc: 'High-confidence competitive pivots' },
              { key: 'competitorActivitySpikes', label: 'Activity Spikes', desc: 'Unusual patterns in market movement' },
              { key: 'pricingChanges', label: 'Pricing Events', desc: 'Real-time pricing and tier adjustments' },
              { key: 'dailyDigest', label: 'Daily Briefing', desc: 'Morning summary of all detected signals' }
            ].map((pref) => (
              <div key={pref.key} className="flex items-center justify-between p-6 rounded-2xl bg-[#F8F9F7] border border-[#E5E6E3]">
                <div>
                  <div className="font-bold text-[#2D3538] text-[15px]">{pref.label}</div>
                  <div className="text-[12px] text-[#9D9F9F] mt-1">{pref.desc}</div>
                </div>
                <Switch
                  checked={(preferences as any)[pref.key]}
                  onCheckedChange={(checked) => setPreferences(prev => ({ ...prev, [pref.key]: checked }))}
                  className="data-[state=checked]:bg-[#D7C9AE]"
                />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Daily Digest Spotlight */}
      {dailyDigest && preferences.dailyDigest && (
        <Card className="bg-[#2D3538] text-white rounded-[32px] overflow-hidden shadow-2xl relative">
          <div className="absolute top-0 right-0 p-10 opacity-[0.05]">
            <Calendar size={120} />
          </div>
          <CardContent className="p-10 relative">
            <div className="flex items-center gap-3 mb-8">
              <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center">
                <Clock size={20} className="text-[#D7C9AE]" />
              </div>
              <div>
                <h3 className="font-serif text-2xl">Today's Executive Brief</h3>
                <p className="text-[13px] text-[#B8BDB7]">Generated {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</p>
              </div>
            </div>

            <div className="grid grid-cols-4 gap-6 mb-10">
              <div className="p-6 rounded-2xl bg-white/5 border border-white/10 text-center">
                <div className="text-[10px] font-bold uppercase tracking-widest text-[#B8BDB7] mb-1">Signals</div>
                <div className="text-3xl font-serif text-[#D7C9AE]">{dailyDigest.signal_count || 12}</div>
              </div>
              <div className="p-6 rounded-2xl bg-white/5 border border-white/10 text-center">
                <div className="text-[10px] font-bold uppercase tracking-widest text-[#B8BDB7] mb-1">Critical</div>
                <div className="text-3xl font-serif text-amber-500">3</div>
              </div>
              <div className="p-6 rounded-2xl bg-white/5 border border-white/10 text-center">
                <div className="text-[10px] font-bold uppercase tracking-widest text-[#B8BDB7] mb-1">Competitors</div>
                <div className="text-3xl font-serif text-white">5</div>
              </div>
              <div className="p-6 rounded-2xl bg-white/5 border border-white/10 text-center">
                <div className="text-[10px] font-bold uppercase tracking-widest text-[#B8BDB7] mb-1">Outcomes</div>
                <div className="text-3xl font-serif text-emerald-500">2</div>
              </div>
            </div>

            <Button className="w-full h-14 bg-white text-[#2D3538] hover:bg-[#F3F4EE] rounded-2xl font-bold text-[15px] shadow-sm">
              Review Full Digest
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Recent Activity Flow */}
      <div className="space-y-6">
        <div className="flex items-center gap-3 pl-2">
          <Bell size={18} className="text-[#D7C9AE]" />
          <h3 className="font-serif text-2xl text-[#2D3538]">Recent Intelligence</h3>
        </div>

        <div className="space-y-4">
          {notifications.length > 0 ? notifications.map((notification) => (
            <div
              key={notification.id}
              className="flex items-start gap-6 p-6 bg-white border border-[#E5E6E3] rounded-[28px] hover:border-[#D7C9AE] transition-all group"
            >
              <div className="mt-1 w-12 h-12 rounded-2xl bg-[#F8F9F7] flex items-center justify-center shrink-0">
                {getNotificationIcon(notification.type)}
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-bold text-[#2D3538] text-[17px]">{notification.title}</h4>
                  <span className="text-[11px] font-bold text-[#9D9F9F] uppercase tracking-widest">
                    {new Date(notification.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <p className="text-[15px] text-[#5B5F61] leading-relaxed mb-6">
                  {notification.message}
                </p>
                <div className="flex items-center justify-between">
                  <div className="flex gap-2">
                    <Badge variant="outline" className={`text-[10px] uppercase tracking-widest border-[#C0C1BE] ${notification.priority === 'high' ? 'text-amber-700 bg-amber-50' : 'text-[#5B5F61]'}`}>
                      {notification.priority} priority
                    </Badge>
                  </div>
                  <Button variant="ghost" className="h-8 px-4 text-[#D7C9AE] font-bold text-[13px] hover:bg-[#F3F4EE] rounded-lg">
                    Details
                  </Button>
                </div>
              </div>
            </div>
          )) : (
            <div className="py-20 text-center bg-white border border-dashed border-[#C0C1BE] rounded-[32px]">
              <BellOff size={40} className="mx-auto text-[#C0C1BE] mb-4" />
              <h4 className="font-serif text-xl text-[#2D3538]">All clear for now</h4>
              <p className="text-[14px] text-[#5B5F61] mt-1">No new intelligence notifications to display.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
