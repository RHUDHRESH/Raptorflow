'use client';

import React from 'react';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';

interface BulletTextProps {
  value:
    | {
        main: string;
        bullets: string[];
      }
    | string;
  onChange: (value: { main: string; bullets: string[] }) => void;
  mainPlaceholder?: string;
  bulletCount?: number;
  bulletLabels?: string[];
}

export function BulletText({
  value,
  onChange,
  mainPlaceholder = 'Enter your answer...',
  bulletCount = 3,
  bulletLabels = [],
}: BulletTextProps) {
  // Handle both object and string values for backward compat
  const safeValue =
    typeof value === 'object' && value
      ? value
      : { main: typeof value === 'string' ? value : '', bullets: [] };

  const bullets =
    safeValue.bullets.length >= bulletCount
      ? safeValue.bullets
      : [
          ...safeValue.bullets,
          ...Array(bulletCount - safeValue.bullets.length).fill(''),
        ];

  const updateMain = (text: string) => {
    onChange({ ...safeValue, main: text });
  };

  const updateBullet = (index: number, text: string) => {
    const newBullets = [...bullets];
    newBullets[index] = text;
    onChange({ ...safeValue, bullets: newBullets });
  };

  return (
    <div className="space-y-4">
      <Input
        placeholder={mainPlaceholder}
        value={safeValue.main}
        onChange={(e) => updateMain(e.target.value)}
        className="h-14 text-lg bg-background border-2 focus-visible:ring-0 focus-visible:border-primary shadow-sm"
      />
      <div className="space-y-3 pl-4 border-l-2 border-muted">
        {bullets.slice(0, bulletCount).map((bullet, i) => (
          <div key={i} className="relative">
            <Input
              placeholder={bulletLabels[i] || `Point ${i + 1}`}
              value={bullet}
              onChange={(e) => updateBullet(i, e.target.value)}
              className="h-11 text-base bg-background border-2 focus-visible:ring-0 focus-visible:border-primary"
            />
          </div>
        ))}
      </div>
    </div>
  );
}
