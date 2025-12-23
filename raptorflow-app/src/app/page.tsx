'use client';

import { AppLayout } from '@/components/layout/AppLayout';
import { FadeIn, Stagger } from '@/components/ui/motion';
import {
  ArrowRightIcon,
  FoundationIcon,
  CohortsIcon,
  CampaignsIcon,
  MuseIcon,
  AlertCircleIcon,
  CheckCircleIcon
} from '@/components/ui/icons';
import Link from 'next/link';
import { toast } from 'sonner';
import { StrategicPivotList } from '@/components/matrix/StrategicPivotList';

/**
 * Dashboard — Operator View (Polished)
 *
 * DESIGN PRINCIPLES (Onboarding Standard):
 * 1. Typography: Playfair >40px, Tracking Tight.
 * 2. Spacing: Grand Rhythm (gap-20+).
 * 3. Cards: rounded-2xl, subtle shadows.
 */
export default function Dashboard() {
  const handleStartExecution = () => {
    toast.success('Opening Mission Control', {
      description: 'Loading context for next move...',
    });
  };

  const currentDate = new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });

  return (
    <AppLayout>
      <Stagger className="flex flex-col gap-20 md:gap-24 pb-32">

        {/* Header Section */}
        <section className="flex flex-col gap-4 max-w-3xl pt-8">
          <FadeIn>
            <h1 className="font-display text-5xl md:text-7xl font-semibold tracking-tight text-foreground leading-[1] -ml-0.5">
              Good morning, Founder.
            </h1>
          </FadeIn>
          <FadeIn delay={1}>
            <p className="text-xl md:text-2xl text-muted-foreground/80 font-light tracking-wide">
              {currentDate}
            </p>
          </FadeIn>
        </section>

        {/* PRIMARY ACTION: The "Next Move" */}
        <FadeIn delay={2}>
          {/* ... existing primary action code ... */}
          <div className="group relative overflow-hidden rounded-2xl bg-card border border-border p-1 shadow-sm transition-all duration-500 hover:shadow-xl hover:border-border/80">
            <div className="relative z-10 p-10 md:p-14 flex flex-col md:flex-row items-start md:items-center justify-between gap-10">
              <div className="space-y-6 max-w-3xl">
                <div className="flex items-center gap-3">
                  <span className="inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.4)]" />
                  <p className="font-sans text-xs font-semibold tracking-widest uppercase text-muted-foreground">Highest Priority Move</p>
                </div>
                <h2 className="font-display text-4xl md:text-5xl font-medium tracking-tight text-foreground leading-[1.1]">
                  Review & Approve Q1 Campaign Strategy
                </h2>
                <p className="text-lg text-muted-foreground max-w-2xl leading-relaxed">
                  Your "Q1 Growth" campaign needs a final review before assets are generated.
                </p>
              </div>

              <div className="shrink-0">
                <Link href="/moves" onClick={handleStartExecution}>
                  <button className="h-16 px-10 rounded-xl text-lg font-medium shadow-md shadow-foreground/5 group-hover:scale-[1.02] active:scale-[0.98] transition-all duration-300 flex items-center gap-3 bg-primary text-primary-foreground hover:bg-primary/90">
                    Execute Move <ArrowRightIcon size={20} />
                  </button>
                </Link>
              </div>
            </div>

            {/* Abstract background - very subtle */}
            <div className="absolute top-0 right-0 h-full w-2/3 bg-gradient-to-l from-muted/50 via-muted/10 to-transparent pointer-events-none" />
            <div className="absolute -bottom-24 -right-24 h-64 w-64 bg-foreground/5 rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-1000" />
          </div>
        </FadeIn>

        {/* STRATEGIC INTELLIGENCE (Task 21) */}
        <StrategicPivotList />

        {/* SYSTEM STATUS GRID */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">

          {/* Foundation Status */}
          <StatusCard
            href="/foundation"
            icon={FoundationIcon}
            label="Foundation"
            status="Healthy"
            statusColor="emerald"
            description="Brand positioning is calibrated and locked."
            action="View details"
            delay={3}
          />

          {/* Cohorts Status */}
          <StatusCard
            href="/cohorts"
            icon={CohortsIcon}
            label="Cohorts"
            status="2 Active"
            statusColor="neutral"
            description="Segments A & B are performing well."
            action="Manage segments"
            delay={4}
          />

          {/* Campaigns Status */}
          <StatusCard
            href="/campaigns"
            icon={CampaignsIcon}
            label="Campaigns"
            status="Attention"
            statusColor="amber"
            description="Q1 Growth needs approval."
            action="View timeline"
            delay={5}
          />

          {/* Muse Status */}
          <StatusCard
            href="/muse"
            icon={MuseIcon}
            label="Muse"
            status="Ready"
            statusColor="neutral"
            description="Create new asset from scratch."
            action="Open studio"
            delay={6}
          />

        </div>

        {/* RECENT ACTIVITY / CONTEXT - "The Situation" continued */}
        <section className="border-t border-border pt-16">
          <FadeIn delay={7}>
            <div className="flex items-end justify-between mb-10">
              <div>
                <h2 className="text-2xl font-display font-medium tracking-tight">Recent Intelligence</h2>
                <p className="text-muted-foreground mt-1">Updates across your marketing engine.</p>
              </div>
              <button className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors border-b border-transparent hover:border-foreground pb-0.5">View all updates</button>
            </div>

            <div className="space-y-6">
              <ActivityItem
                icon={CheckCircleIcon}
                iconColor="text-emerald-500"
                title="Positioning Updated"
                description="Core value prop refreshed based on new customer interviews."
                time="2h ago"
                module="Foundation"
              />
              <ActivityItem
                icon={AlertCircleIcon}
                iconColor="text-amber-500"
                title="Competitor Price Drop"
                description="Competitor X lowered pricing by 15%. Recommend reviewing 'Offer' module."
                time="5h ago"
                module="Radar"
              />
              <ActivityItem
                icon={CampaignsIcon}
                iconColor="text-muted-foreground"
                title="Campaign Drafted"
                description="'Founder-Led Sales' campaign drafted by Muse."
                time="1d ago"
                module="Muse"
              />
            </div>
          </FadeIn>
        </section>

      </Stagger>
    </AppLayout>
  );
}

function StatusCard({ href, icon: Icon, label, status, statusColor, description, action, delay }: any) {
  const colorClasses = {
    emerald: "text-emerald-700 bg-emerald-100/50",
    amber: "text-amber-700 bg-amber-100/50",
    neutral: "text-muted-foreground bg-muted",
  }[statusColor as string] || "text-muted-foreground bg-muted";

  return (
    <FadeIn delay={delay}>
      <Link href={href} className="block h-full">
        <div className="h-full p-8 rounded-2xl border border-border bg-card hover:bg-card/80 hover:border-border transition-all duration-300 group flex flex-col justify-between hover:shadow-md">
          <div className="space-y-6">
            <div className="flex justify-between items-start">
              <div className="p-3 rounded-xl bg-secondary text-secondary-foreground group-hover:text-foreground group-hover:bg-muted transition-colors">
                <Icon size={24} />
              </div>
              <span className={`text-xs font-mono font-medium px-2.5 py-1 rounded-full ${colorClasses}`}>{status}</span>
            </div>
            <div>
              <h3 className="font-display text-xl font-medium text-foreground mb-2">{label}</h3>
              <p className="text-sm text-muted-foreground line-clamp-2 leading-relaxed">{description}</p>
            </div>
          </div>
          <div className="mt-8 pt-6 border-t border-border flex justify-between items-center text-sm">
            <span className="text-muted-foreground font-medium group-hover:text-foreground transition-colors">{action}</span>
            <ArrowRightIcon className="h-4 w-4 text-muted-foreground group-hover:translate-x-1 transition-transform group-hover:text-foreground" />
          </div>
        </div>
      </Link>
    </FadeIn>
  )
}

function ActivityItem({ icon: Icon, iconColor, title, description, time, module }: { icon: any, iconColor: string, title: string, description: string, time: string, module: string }) {
  return (
    <div className="group flex items-start gap-6 p-6 rounded-xl hover:bg-card border border-transparent hover:border-border transition-all duration-200 hover:shadow-sm">
      <div className={`mt-1 p-2 rounded-full bg-background border border-border shadow-sm shrink-0 group-hover:border-border group-hover:shadow-md transition-all`}>
        <Icon className={`h-4 w-4 ${iconColor}`} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-3 mb-2">
          <h4 className="text-base font-medium text-foreground">{title}</h4>
          <span className="text-[10px] uppercase tracking-wider text-muted-foreground border border-border px-2 py-0.5 rounded-full">{module}</span>
        </div>
        <p className="text-base text-muted-foreground leading-relaxed">{description}</p>
      </div>
      <span className="text-sm text-muted-foreground font-mono whitespace-nowrap pt-1">{time}</span>
    </div>
  )
}
