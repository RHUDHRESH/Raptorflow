"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  AppPageFrame,
  AppEmptyState,
  AppErrorState,
  AppLoadingState,
} from "@/components/layout";
import {
  RfWindow,
  RfWindowGrid,
  RfWindowRail,
  StatusPill,
  SignalDot,
} from "@/components/windows";
import {
  useOfficeState,
  useOfficeCampaignFronts,
  useOfficeCouncilActivity,
  useOfficeRecentArtifacts,
  CANONICAL_AVATARS,
} from "@/features/office";
import { copy } from "@/brand/copy";
import { routes } from "@/brand/routes";

function MorningBriefingWindow() {
  const { data, isLoading, error } = useOfficeState();

  if (isLoading) return <AppLoadingState label="Loading briefing..." />;
  if (error)
    return (
      <AppErrorState
        title="Briefing unavailable"
        description="Could not load office state. The backend may be unreachable."
      />
    );
  if (!data) return null;

  const items = [
    { label: "Active Campaigns", value: data.activeCampaigns },
    { label: "Active Council Sessions", value: data.activeCouncilSessions },
    { label: "Open Nudges", value: data.openNudges },
    { label: "Muse Conversations (7d)", value: data.recentMuseConversations },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      {items.map((item) => (
        <div
          key={item.label}
          className="paper-card p-4 flex flex-col gap-1"
        >
          <span className="mono-label text-[var(--ink-500)]">
            {item.label}
          </span>
          <span className="h2">{item.value}</span>
        </div>
      ))}
    </div>
  );
}

function CampaignFrontsWindow() {
  const { data, isLoading, error } = useOfficeCampaignFronts();

  if (isLoading) return <AppLoadingState label="Loading campaigns..." />;
  if (error)
    return (
      <AppErrorState
        title="Campaigns unavailable"
        description="Could not load campaign data."
      />
    );
  if (!data || data.length === 0) {
    return (
      <AppEmptyState
        title="No active campaigns"
        description="Campaign fronts will appear once campaigns are created."
        action={
          <Link
            href={routes.campaigns.href}
            className="inline-flex items-center px-3 py-1.5 rounded-md bg-[var(--primary)] text-white text-sm font-medium hover:opacity-90 transition-opacity"
          >
            Go to Campaigns
          </Link>
        }
      />
    );
  }

  return (
    <div className="space-y-3">
      {data.slice(0, 5).map((campaign: any) => (
        <div
          key={campaign.id ?? campaign.campaign_id}
          className="flex items-center justify-between p-3 rounded-lg border border-[var(--border)] bg-[var(--paper-100)] hover:bg-[var(--paper-150)] transition-colors"
        >
          <div className="min-w-0">
            <p className="font-medium text-[var(--ink-900)] truncate">
              {campaign.name ?? campaign.title ?? "Untitled Campaign"}
            </p>
            {campaign.goal && (
              <p className="text-sm text-[var(--ink-500)] truncate">
                {campaign.goal}
              </p>
            )}
          </div>
          <div className="flex items-center gap-3 shrink-0 ml-4">
            <StatusPill
              status={campaign.status ?? "unknown"}
              tone={
                campaign.status === "active"
                  ? "success"
                  : campaign.status === "paused"
                    ? "warning"
                    : "neutral"
              }
            />
            {(campaign.move_count ?? campaign.moveCount) != null && (
              <span className="mono-label text-[var(--ink-500)]">
                {campaign.move_count ?? campaign.moveCount} moves
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

function MoveLadderWindow() {
  return (
    <AppEmptyState
      title="Move ladder unavailable"
      description="Move ladder will appear after campaign contract repair."
    />
  );
}

function CouncilActivityWindow() {
  const { data, isLoading, error } = useOfficeCouncilActivity();

  if (isLoading) return <AppLoadingState label="Loading council..." />;
  if (error)
    return (
      <AppErrorState
        title="Council data unavailable"
        description="Could not load council activity."
      />
    );
  if (!data || data.length === 0) {
    return (
      <AppEmptyState
        title="No recent council sessions"
        description="Council activity will appear after war room sessions are run."
        action={
          <Link
            href="/council/war-room"
            className="inline-flex items-center px-3 py-1.5 rounded-md bg-[var(--primary)] text-white text-sm font-medium hover:opacity-90 transition-opacity"
          >
            Open War Room
          </Link>
        }
      />
    );
  }

  const latest = data[0];

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between p-3 rounded-lg border border-[var(--border)] bg-[var(--paper-100)]">
        <div>
          <p className="font-medium text-[var(--ink-900)]">
            {latest.mode ?? "Council Session"}
          </p>
          <p className="text-sm text-[var(--ink-500)]">
            {latest.status ?? "unknown status"}
          </p>
        </div>
        <StatusPill
          status={latest.status ?? "unknown"}
          tone={latest.status === "completed" ? "success" : "amber"}
        />
      </div>
      <Link
        href="/council/war-room"
        className="inline-flex items-center text-sm text-[var(--primary)] hover:underline"
      >
        Open War Room →
      </Link>
    </div>
  );
}

function ArtifactLedgerWindow() {
  const { data, isLoading, error } = useOfficeRecentArtifacts();

  if (isLoading) return <AppLoadingState label="Loading artifacts..." />;
  if (error)
    return (
      <AppErrorState
        title="Artifacts unavailable"
        description="Could not load content artifacts."
      />
    );
  if (!data || data.length === 0) {
    return (
      <AppEmptyState
        title="No recent artifacts"
        description="Generated content will appear here after creation."
        action={
          <Link
            href={routes.content.href}
            className="inline-flex items-center px-3 py-1.5 rounded-md bg-[var(--primary)] text-white text-sm font-medium hover:opacity-90 transition-opacity"
          >
            Go to Content Ledger
          </Link>
        }
      />
    );
  }

  return (
    <div className="space-y-3">
      {data.map((artifact: any) => (
        <div
          key={artifact.id}
          className="flex items-center justify-between p-3 rounded-lg border border-[var(--border)] bg-[var(--paper-100)]"
        >
          <div className="min-w-0">
            <p className="font-medium text-[var(--ink-900)] truncate">
              {artifact.title ?? artifact.name ?? "Untitled"}
            </p>
            <p className="text-sm text-[var(--ink-500)]">
              {artifact.content_type ?? artifact.type ?? "content"}
            </p>
          </div>
          {artifact.created_at && (
            <span className="mono-label text-[var(--ink-500)] shrink-0 ml-4">
              {new Date(artifact.created_at).toLocaleDateString()}
            </span>
          )}
        </div>
      ))}
    </div>
  );
}

function MuseCommandWindow() {
  const router = useRouter();
  const [prompt, setPrompt] = React.useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = prompt.trim();
    if (!trimmed) return;
    router.push(`/muse?prompt=${encodeURIComponent(trimmed)}`);
    setPrompt("");
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-3">
      <input
        type="text"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Ask Muse..."
        className="flex-1 min-w-0 rounded-lg border border-[var(--border)] bg-[var(--paper-100)] px-4 py-2.5 text-sm text-[var(--ink-900)] placeholder:text-[var(--ink-400)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]/20 focus:border-[var(--primary)]"
      />
      <button
        type="submit"
        disabled={!prompt.trim()}
        className="shrink-0 inline-flex items-center px-4 py-2.5 rounded-lg bg-[var(--primary)] text-white text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
      >
        Send
      </button>
    </form>
  );
}

function AvatarRoster() {
  return (
    <div className="space-y-3">
      {CANONICAL_AVATARS.map((avatar) => (
        <div
          key={avatar.key}
          className="flex items-center gap-3"
        >
          <SignalDot tone="neutral" />
          <div className="min-w-0">
            <p className="text-sm font-medium text-[var(--ink-900)]">
              {avatar.label}
            </p>
            <p className="text-xs text-[var(--ink-500)]">{avatar.role}</p>
          </div>
          <span className="ml-auto mono-label text-[var(--ink-400)] capitalize">
            {avatar.status}
          </span>
        </div>
      ))}
    </div>
  );
}

function SystemSignals() {
  const { data } = useOfficeState();
  const isOnline = !data || data.activeCampaigns >= 0;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-sm text-[var(--ink-600)]">Office API</span>
        <SignalDot
          tone={isOnline ? "success" : "danger"}
          pulse={isOnline}
          label={isOnline ? "Online" : "Offline"}
        />
      </div>
      <div className="flex items-center justify-between">
        <span className="text-sm text-[var(--ink-600)]">Council</span>
        <SignalDot
          tone={data && data.activeCouncilSessions > 0 ? "amber" : "neutral"}
          label={
            data && data.activeCouncilSessions > 0
              ? `${data.activeCouncilSessions} active`
              : "Idle"
          }
        />
      </div>
    </div>
  );
}

function QuickLinks() {
  const links = [
    routes.campaigns,
    { ...routes.council, href: "/council/war-room", label: "Council War Room" },
    routes.content,
    routes.muse,
    routes.foundation,
    routes.ripples,
  ];

  return (
    <div className="space-y-2">
      {links.map((link) => (
        <Link
          key={link.href}
          href={link.href}
          className="block text-sm text-[var(--ink-600)] hover:text-[var(--primary)] transition-colors"
        >
          {link.label}
        </Link>
      ))}
    </div>
  );
}

function OfficeRail() {
  return (
    <RfWindowRail>
      <div className="space-y-6">
        <div>
          <h4 className="eyebrow mb-3">{copy.officeAvatarRosterTitle}</h4>
          <AvatarRoster />
        </div>
        <div className="h-px bg-[var(--border)]" />
        <div>
          <h4 className="eyebrow mb-3">System Signals</h4>
          <SystemSignals />
        </div>
        <div className="h-px bg-[var(--border)]" />
        <div>
          <h4 className="eyebrow mb-3">Quick Links</h4>
          <QuickLinks />
        </div>
      </div>
    </RfWindowRail>
  );
}

export default function OfficePage(): React.ReactElement {
  const { data: officeState, isLoading, error } = useOfficeState();

  const statusNode = React.useMemo(() => {
    if (isLoading)
      return <StatusPill status="Loading..." tone="neutral" />;
    if (error)
      return <StatusPill status="Unavailable" tone="danger" />;
    return <StatusPill status="Office online" tone="success" />;
  }, [isLoading, error]);

  const actions = (
    <>
      <Link
        href="/council/war-room"
        className="inline-flex items-center px-3 py-1.5 rounded-md border border-[var(--border)] text-sm font-medium text-[var(--ink-700)] hover:bg-[var(--paper-150)] transition-colors"
      >
        Open Council War Room
      </Link>
      <Link
        href={routes.campaigns.href}
        className="inline-flex items-center px-3 py-1.5 rounded-md bg-[var(--primary)] text-white text-sm font-medium hover:opacity-90 transition-opacity"
      >
        New Campaign
      </Link>
    </>
  );

  return (
    <AppPageFrame
      eyebrow="WORKSPACE"
      title={copy.officeTitle}
      description={copy.officeTagline}
      status={statusNode}
      actions={actions}
      rail={<OfficeRail />}
      maxWidth="wide"
    >
      <div className="space-y-6">
        <RfWindow
          title={copy.officeBriefingTitle}
          eyebrow="OVERVIEW"
          description="Current operational status across all systems."
        >
          <MorningBriefingWindow />
        </RfWindow>

        <RfWindowGrid columns={2}>
          <RfWindow
            title={copy.officeCampaignFrontsTitle}
            eyebrow="STRATEGY"
            description="Active and recent campaigns."
          >
            <CampaignFrontsWindow />
          </RfWindow>

          <RfWindow
            title={copy.officeCouncilActivityTitle}
            eyebrow="OPERATIONS"
            description="Latest council war room sessions."
          >
            <CouncilActivityWindow />
          </RfWindow>
        </RfWindowGrid>

        <RfWindow
          title={copy.officeMoveLadderTitle}
          eyebrow="EXECUTION"
          description="Campaign moves and execution pipeline."
        >
          <MoveLadderWindow />
        </RfWindow>

        <RfWindowGrid columns={2}>
          <RfWindow
            title={copy.officeArtifactLedgerTitle}
            eyebrow="OUTPUT"
            description="Recently generated content artifacts."
          >
            <ArtifactLedgerWindow />
          </RfWindow>

          <RfWindow
            title={copy.officeMuseCommandTitle}
            eyebrow="INPUT"
            description="Direct command to Muse."
          >
            <MuseCommandWindow />
          </RfWindow>
        </RfWindowGrid>
      </div>
    </AppPageFrame>
  );
}
