'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Zap, AlertTriangle, Check } from 'lucide-react';
import { toast } from 'sonner';

export function GlobalKillSwitch() {
  const [isConfirming, setIsConfirming] = useState(false);
  const [isHalted, setIsHalted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleHalt = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/matrix/kill-switch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason: 'Manual UI Trigger' }),
      });

      if (!res.ok) throw new Error('Failed to engage kill-switch.');

      setIsHalted(true);
      toast.error('SYSTEM HALTED', {
        description: 'All agentic activity has been stopped immediately.',
      });
    } catch (err: any) {
      toast.error('Action Failed', {
        description: err.message,
      });
    } finally {
      setLoading(false);
      setIsConfirming(false);
    }
  };

  if (isHalted) {
    return (
      <Button
        disabled
        variant="outline"
        className="h-11 rounded-xl px-6 border-red-200 text-red-600 bg-red-50"
      >
        <Check className="mr-2 h-4 w-4" />
        SYSTEM OFFLINE
      </Button>
    );
  }

  if (isConfirming) {
    return (
      <div className="flex items-center space-x-2 animate-in fade-in zoom-in duration-200">
        <Button
          variant="destructive"
          className="h-11 rounded-xl px-6 font-bold"
          onClick={handleHalt}
          disabled={loading}
        >
          {loading ? 'Engaging...' : 'CONFIRM HALT'}
        </Button>
        <Button
          variant="ghost"
          className="h-11 rounded-xl px-4"
          onClick={() => setIsConfirming(false)}
          disabled={loading}
        >
          Cancel
        </Button>
      </div>
    );
  }

  return (
    <Button
      variant="destructive"
      className="h-11 rounded-xl px-6 font-medium group relative overflow-hidden"
      onClick={() => setIsConfirming(true)}
    >
      <div className="absolute inset-0 bg-white/10 translate-y-full group-hover:translate-y-0 transition-transform duration-300" />
      <Zap className="mr-2 h-4 w-4" />
      Global Kill-Switch
    </Button>
  );
}
