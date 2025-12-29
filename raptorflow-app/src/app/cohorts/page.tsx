'use client';

import { AppLayout } from '@/components/layout/AppLayout';
import { useState, useEffect } from 'react';
import {
  Users,
  ArrowRight,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Target,
  Brain,
  MessageSquare,
} from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { useFoundation } from '@/context/FoundationProvider';
import { IcpProfile } from '@/lib/foundation-types';
import { cn } from '@/lib/utils';

export default function CohortsPage() {
  const { getIcps, isLoading } = useFoundation();
  const icps = getIcps();
  const [selectedIcp, setSelectedIcp] = useState<IcpProfile | null>(null);

  // Select first ICP by default when loaded
  useEffect(() => {
    if (icps.length > 0 && !selectedIcp) {
      setSelectedIcp(icps[0]);
    }
  }, [icps, selectedIcp]);

  if (isLoading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </AppLayout>
    );
  }

  if (icps.length === 0) {
    return (
      <AppLayout>
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-8">
          <div className="w-20 h-20 rounded-full bg-muted flex items-center justify-center mb-6">
            <Users className="w-10 h-10 text-muted-foreground" />
          </div>
          <h1 className="font-serif text-4xl mb-4">No ICPs Generated Yet</h1>
          <p className="text-muted-foreground max-w-md mb-8">
            Complete your Foundation to generate AI-derived Ideal Customer
            Profiles.
          </p>
          <Link
            href="/foundation"
            className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:bg-primary/90 transition-colors"
          >
            Complete Foundation <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="flex flex-col gap-12 pb-24">
        {/* Header */}
        <section className="pt-8">
          <span className="text-xs font-semibold tracking-widest uppercase text-muted-foreground mb-3 block">
            Cohorts
          </span>
          <h1 className="font-serif text-5xl tracking-tight text-foreground mb-4">
            Your Ideal Customers
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl">
            AI-derived customer profiles based on your Foundation data. Each ICP
            includes firmographics, pain points, and engagement patterns.
          </p>
        </section>

        <div className="grid grid-cols-12 gap-8">
          {/* Left Sidebar: ICP List */}
          <div className="col-span-12 lg:col-span-4 space-y-4">
            <h3 className="font-medium text-sm text-muted-foreground uppercase tracking-wide mb-4">
              Active Cohorts
            </h3>
            {icps.map((icp) => (
              <button
                key={icp.icp_id}
                onClick={() => setSelectedIcp(icp)}
                className={cn(
                  'w-full text-left p-5 rounded-xl border transition-all duration-200 group',
                  selectedIcp?.icp_id === icp.icp_id
                    ? 'border-primary bg-primary/5 shadow-sm'
                    : 'border-border bg-card hover:border-primary/50'
                )}
              >
                <div className="flex items-start justify-between mb-2">
                  <span
                    className={cn(
                      'text-[10px] font-mono px-2 py-0.5 rounded-full uppercase',
                      'bg-blue-100 text-blue-700'
                    )}
                  >
                    {icp.b2b_or_b2c}
                  </span>
                </div>
                <h3 className="font-display text-lg font-medium mb-1 group-hover:text-primary transition-colors">
                  {icp.name}
                </h3>
                <p className="text-xs text-muted-foreground line-clamp-2">
                  {icp.firmographics.industry.join(', ')} •{' '}
                  {icp.firmographics.employee_range}
                </p>
              </button>
            ))}
          </div>

          {/* Right Panel: Detailed View */}
          <div className="col-span-12 lg:col-span-8">
            {selectedIcp && (
              <div className="bg-card border border-border rounded-2xl overflow-hidden shadow-sm">
                {/* Detail Header */}
                <div className="p-8 border-b border-border bg-muted/20">
                  <div className="flex items-start gap-5">
                    <div className="w-16 h-16 rounded-2xl bg-white border border-border shadow-sm flex items-center justify-center shrink-0">
                      <Users className="w-8 h-8 text-primary/80" />
                    </div>
                    <div>
                      <h2 className="font-serif text-3xl mb-2">
                        {selectedIcp.name}
                      </h2>
                      <div className="flex flex-wrap gap-3">
                        {selectedIcp.roles.buyer.map((role) => (
                          <span
                            key={role}
                            className="text-xs font-medium px-2.5 py-1 rounded-md bg-white border border-border text-foreground/80"
                          >
                            🎯 {role}
                          </span>
                        ))}
                        <span className="text-xs font-medium px-2.5 py-1 rounded-md bg-white border border-border text-foreground/80">
                          🏢 {selectedIcp.firmographics.revenue_range}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="p-8 space-y-10">
                  {/* Pains & Triggers */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div>
                      <div className="flex items-center gap-2 mb-4 text-primary">
                        <AlertCircle className="w-5 h-5" />
                        <h3 className="font-semibold">Pain Points</h3>
                      </div>
                      <div className="space-y-3">
                        <div className="p-4 bg-red-50/50 border border-red-100 rounded-lg">
                          <span className="text-xs font-bold text-red-600 uppercase mb-1 block">
                            Primary Pain
                          </span>
                          <p className="text-sm font-medium text-red-900">
                            {selectedIcp.pains.primary}
                          </p>
                        </div>
                        <ul className="space-y-2">
                          {selectedIcp.pains.secondary.map((pain, i) => (
                            <li
                              key={i}
                              className="text-sm text-muted-foreground flex items-start gap-2"
                            >
                              <span className="text-red-400 mt-1">•</span>
                              {pain}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    <div>
                      <div className="flex items-center gap-2 mb-4 text-primary">
                        <TrendingUp className="w-5 h-5" />
                        <h3 className="font-semibold">Buying Triggers</h3>
                      </div>
                      <div className="space-y-3">
                        {selectedIcp.triggers.map((trigger, i) => (
                          <div
                            key={i}
                            className="flex items-start gap-3 p-3 rounded-lg bg-muted/30 border border-transparent hover:border-border transition-colors"
                          >
                            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold">
                              {i + 1}
                            </span>
                            <p className="text-sm">{trigger}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="h-px bg-border/50" />

                  {/* Psychographics & Messaging */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div>
                      <div className="flex items-center gap-2 mb-4 text-primary">
                        <Brain className="w-5 h-5" />
                        <h3 className="font-semibold">Psychographics</h3>
                      </div>
                      <div className="space-y-4">
                        <div>
                          <h4 className="text-xs font-semibold uppercase text-muted-foreground mb-2">
                            Primary Fear
                          </h4>
                          <p className="text-sm italic pl-3 border-l-2 border-primary/20">
                            "{selectedIcp.psychographics.fears[0]}"
                          </p>
                        </div>
                        <div>
                          <h4 className="text-xs font-semibold uppercase text-muted-foreground mb-2">
                            Core Values
                          </h4>
                          <div className="flex flex-wrap gap-2">
                            {selectedIcp.psychographics.values.map((val) => (
                              <span
                                key={val}
                                className="text-xs px-2 py-1 bg-muted rounded-md border border-border/50"
                              >
                                {val}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>

                    <div>
                      <div className="flex items-center gap-2 mb-4 text-primary">
                        <Target className="w-5 h-5" />
                        <h3 className="font-semibold">Messaging Angles</h3>
                      </div>
                      <div className="space-y-3">
                        {selectedIcp.message_angles.hooks.map((hook, i) => (
                          <div
                            key={i}
                            className="text-sm p-3 bg-emerald-50/50 border border-emerald-100 rounded-lg text-emerald-900"
                          >
                            <span className="font-semibold mr-1">Hook:</span>{' '}
                            {hook}
                          </div>
                        ))}
                        <div className="mt-4">
                          <h4 className="text-xs font-semibold uppercase text-muted-foreground mb-2">
                            Winning Promise
                          </h4>
                          <p className="text-sm font-medium">
                            {selectedIcp.message_angles.promises[0]}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="h-px bg-border/50" />

                  {/* Objections */}
                  <div>
                    <div className="flex items-center gap-2 mb-4 text-primary">
                      <MessageSquare className="w-5 h-5" />
                      <h3 className="font-semibold">Key Objections</h3>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {selectedIcp.objections.map((obj, i) => (
                        <div
                          key={i}
                          className="p-3 bg-muted/20 border border-border/50 rounded-lg text-sm"
                        >
                          "{obj}"
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
