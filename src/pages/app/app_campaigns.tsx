import React, { useCallback, useState } from "react";
import { Layers, MoreHorizontal } from "lucide-react";
import { useLocation, useNavigate, useParams } from "react-router-dom";

import { useMe } from "../../hooks/useMe";
import { usePlans } from "../../hooks/usePlans";
import { entitlementsForPlanName } from "../../lib/entitlements";
import { cn } from "../../lib/utils";
import { useToast } from "../../providers/ToastProvider";
import { useLimitsModal } from "../../providers/LimitsModalProvider";
import { Button } from "../../components/ui/Button";
import { Pill } from "../../components/ui/Pill";

type CampaignStatus = "draft" | "active" | "paused" | "completed" | "archived";
type MoveStatus = "draft" | "active" | "paused" | "complete";

type Campaign = {
  id: string;
  status: CampaignStatus;
  name: string;
  objective: string;
  cohort: string;
  theme: string;
  northStar: { label: string; series6: number[] };
  kpis: Array<{ label: string; value: number }>;
};

type Move = {
  id: string;
  campaignId: string;
  status: MoveStatus;
  name: string;
  channel: string;
  kpi: string;
  targetValue: number;
  actualValue: number;
  startDate: string;
  endDate: string;
  assets: Array<{ id: string; name: string; type: string }>;
};

type DemoState = {
  onboardingComplete: boolean;
  campaigns: Campaign[];
  moves: Move[];
};

const STORAGE_KEY = "rf_demo_state";

function loadState(): DemoState {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored) {
    try {
      return JSON.parse(stored);
    } catch {
      // Fall through
    }
  }
  return {
    onboardingComplete: false,
    campaigns: [
      {
        id: "c1",
        status: "active",
        name: "Q1 Product Launch",
        objective: "Generate qualified leads for new feature",
        cohort: "SMB prospects",
        theme: "Innovation & Efficiency",
        northStar: { label: "Marketing Qualified Leads", series6: [12, 19, 28, 35, 42, 48] },
        kpis: [
          { label: "MQLs", value: 48 },
          { label: "Demo Requests", value: 23 },
          { label: "Conversion Rate", value: 12 },
        ],
      },
      {
        id: "c2",
        status: "draft",
        name: "Enterprise Expansion",
        objective: "Upsell existing enterprise customers",
        cohort: "Current enterprise clients",
        theme: "Growth & Partnership",
        northStar: { label: "Expansion Revenue", series6: [8, 15, 22, 31, 38, 45] },
        kpis: [
          { label: "Upsell Revenue", value: 45 },
          { label: "Accounts Targeted", value: 12 },
          { label: "Success Rate", value: 38 },
        ],
      },
    ],
    moves: [
      {
        id: "m1",
        campaignId: "c1",
        status: "active",
        name: "Cold Email Outreach",
        channel: "Email",
        kpi: "Reply Rate",
        targetValue: 15,
        actualValue: 12,
        startDate: "2024-01-15",
        endDate: "2024-02-15",
        assets: [
          { id: "a1", name: "Email Template", type: "template" },
          { id: "a2", name: "Prospect List", type: "list" },
        ],
      },
      {
        id: "m2",
        campaignId: "c1",
        status: "paused",
        name: "LinkedIn Content",
        channel: "LinkedIn",
        kpi: "Engagement Rate",
        targetValue: 8,
        actualValue: 5,
        startDate: "2024-01-20",
        endDate: "2024-02-20",
        assets: [
          { id: "a3", name: "Post Templates", type: "template" },
        ],
      },
    ],
  };
}

function saveState(state: DemoState) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

type MoveTemplate = {
  id: string;
  name: string;
  durationDays: 7 | 14 | 28;
  kpi: string;
  targetHint: string;
};

const MOVE_LIBRARY: MoveTemplate[] = [
  { id: "lib_proof", name: "Proof Spike", durationDays: 7, kpi: "Demos", targetHint: "(+5)" },
  { id: "lib_outreach", name: "Outbound Sprint", durationDays: 14, kpi: "Replies", targetHint: "(100)" },
  { id: "lib_landing", name: "Landing Tightening", durationDays: 28, kpi: "CallsBooked", targetHint: "(20)" },
];

function ModalShell({
  title,
  description,
  children,
  onClose,
}: {
  title: string;
  description?: string;
  children: React.ReactNode;
  onClose: () => void;
}) {
  return (
    <div className="fixed inset-0 z-[999] flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-xl rounded-3xl border border-border bg-card p-5 shadow-soft">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="text-lg font-semibold text-fg">{title}</div>
            {description ? <div className="mt-1 text-sm text-muted">{description}</div> : null}
          </div>
          <Button variant="ghost" onClick={onClose}>
            Close
          </Button>
        </div>
        <div className="mt-4">{children}</div>
      </div>
    </div>
  );
}

export default function CampaignsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { campaignId } = useParams<{ campaignId: string }>();
  const { data: plans } = usePlans();
  const { data: me } = useMe();
  const { toast } = useToast();
  const { openLimitModal } = useLimitsModal();

  const [state, setState] = useState<DemoState>(loadState);
  const [createOpen, setCreateOpen] = useState(false);
  const [addMoveOpen, setAddMoveOpen] = useState(false);

  const selectedCampaign = state.campaigns.find((c) => c.id === campaignId);

  const plan = Array.isArray(plans) ? plans.find((p: any) => p.id === me?.subscription?.planId) : undefined;
  const ent = entitlementsForPlanName(plan?.name ?? null);
  const activeCap = ent.limits.activeCampaigns;

  const setAndPersist = useCallback(
    (updater: (prev: DemoState) => DemoState) => {
      setState((prev) => {
        const next = updater(prev);
        saveState(next);
        return next;
      });
    },
    []
  );

  const requestActivateCampaign = useCallback(
    (campaignId: string) => {
      const campaign = state.campaigns.find((c) => c.id === campaignId);
      if (!campaign) return;

      const wouldActivate = campaign.status !== "active";
      const nextActiveCount = wouldActivate
        ? state.campaigns.filter((c) => c.status === "active" || c.id === campaignId).length
        : state.campaigns.filter((c) => c.status === "active").length;

      if (wouldActivate && nextActiveCount >= activeCap) {
        toast({
          title: "Limit reached",
          description: `Your plan allows ${activeCap} active campaigns. Pause or complete one to activate another.`,
          tone: "warn",
        });
        openLimitModal({ kind: "active_campaigns", limit: activeCap });
        return;
      }

      setAndPersist((prev) => ({
        ...prev,
        campaigns: prev.campaigns.map((c) =>
          c.id === campaignId ? { ...c, status: wouldActivate ? "active" : "paused" } : c
        ),
      }));
    },
    [activeCap, openLimitModal, setAndPersist, state.campaigns, toast]
  );

  const requestDeleteCampaign = useCallback(
    (campaignId: string) => {
      if (!confirm("Delete this campaign and all its moves? This cannot be undone.")) return;

      setAndPersist((prev) => ({
        ...prev,
        campaigns: prev.campaigns.filter((c) => c.id !== campaignId),
        moves: prev.moves.filter((m) => m.campaignId !== campaignId),
      }));

      if (campaignId === campaignId) {
        navigate("/app/campaigns");
      }
    },
    [navigate, setAndPersist]
  );

  const activeCount = state.campaigns.filter((c) => c.status === "active").length;

  if (selectedCampaign) {
    const campaignMoves = state.moves.filter((m) => m.campaignId === selectedCampaign.id);
    
    return (
      <div className="mx-auto max-w-7xl space-y-8">
        {/* Campaign Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-4">
              <h1 className="text-3xl font-serif text-fg">{selectedCampaign.name}</h1>
              <Pill>{selectedCampaign.status}</Pill>
            </div>
            <p className="mt-2 text-lg text-muted">{selectedCampaign.objective}</p>
            <div className="mt-4 flex items-center gap-6 text-sm text-muted">
              <span>Cohort: {selectedCampaign.cohort}</span>
              <span>Theme: {selectedCampaign.theme}</span>
              <span>Duration: 90 days</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              onClick={() => requestActivateCampaign(selectedCampaign.id)}
            >
              {selectedCampaign.status === "active" ? "Pause" : "Activate"}
            </Button>
          </div>
        </div>

        {/* Overview Section */}
        <div className="grid gap-8 lg:grid-cols-2">
          <div>
            <h2 className="mb-4 text-xl font-serif text-fg">North Star Metric</h2>
            <div className="rounded-2xl border border-border bg-surface p-6">
              <div className="mb-4 flex items-center justify-between">
                <span className="text-sm font-medium text-fg">
                  {selectedCampaign.northStar.label}
                </span>
                <span className="text-2xl font-bold text-primary">
                  {(selectedCampaign.northStar?.series6 ?? [])[selectedCampaign.northStar?.series6?.length - 1] ?? 0}
                </span>
              </div>
              <div className="flex h-24 items-end justify-between gap-1">
                {(selectedCampaign.northStar?.series6 ?? []).map((val, i) => (
                  <div
                    key={i}
                    className="w-full bg-primary/20 rounded-t"
                    style={{ height: `${(val / Math.max(...(selectedCampaign.northStar?.series6 ?? [1]))) * 100}%` }}
                  />
                ))}
              </div>
            </div>
          </div>

          <div>
            <h2 className="mb-4 text-xl font-serif text-fg">Key Metrics</h2>
            <div className="grid gap-3">
              {(selectedCampaign.kpis ?? []).map((kpi, i) => (
                <div key={i} className="flex items-center justify-between rounded-xl border border-border bg-surface p-4">
                  <span className="text-sm font-medium text-fg">{kpi.label}</span>
                  <span className="text-lg font-semibold text-primary">{kpi.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Moves Roster */}
        <div>
          <div className="mb-6 flex items-center justify-between">
            <h2 className="text-xl font-serif text-fg">Moves Roster</h2>
            <Button variant="primary" onClick={() => setAddMoveOpen(true)}>
              <Layers className="mr-2 h-4 w-4" />
              Add Move
            </Button>
          </div>
          
          {campaignMoves.length === 0 ? (
            <div className="rounded-2xl border border-border bg-surface p-12 text-center">
              <h3 className="text-lg font-serif text-fg">No moves yet</h3>
              <p className="mt-2 text-sm text-muted">Add your first move to start executing this campaign</p>
              <Button variant="primary" className="mt-4" onClick={() => setAddMoveOpen(true)}>
                Add Move
              </Button>
            </div>
          ) : (
            <div className="grid gap-4">
              {campaignMoves.map((move) => (
                <div key={move.id} className="rounded-2xl border border-border bg-surface p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <h3 className="text-lg font-serif text-fg">{move.name}</h3>
                        <Pill>{move.status}</Pill>
                      </div>
                      <p className="mt-2 text-sm text-muted">
                        {move.channel} • {move.kpi}: {move.actualValue}/{move.targetValue}
                      </p>
                      <div className="mt-3 flex items-center gap-4 text-xs text-muted">
                        <span>Start: {move.startDate}</span>
                        <span>End: {move.endDate}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="ghost" size="sm">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Add Move Modal */}
        {addMoveOpen && (
          <ModalShell
            title="Add Move to Campaign"
            description="Choose a template from the Move Library"
            onClose={() => setAddMoveOpen(false)}
          >
            <div className="space-y-3">
              {MOVE_LIBRARY.map((template) => (
                <button
                  key={template.id}
                  className="w-full rounded-xl border border-border bg-surface p-4 text-left hover:bg-bg"
                  onClick={() => {
                    const newMove: Move = {
                      id: `m_${Date.now()}`,
                      campaignId: selectedCampaign.id,
                      status: "draft",
                      name: template.name,
                      channel: "Multi-channel",
                      kpi: template.kpi,
                      targetValue: parseInt(template.targetHint.replace(/[^\d]/g, "")),
                      actualValue: 0,
                      startDate: new Date().toISOString().split("T")[0],
                      endDate: new Date(Date.now() + template.durationDays * 24 * 60 * 60 * 1000)
                        .toISOString()
                        .split("T")[0],
                      assets: [],
                    };
                    setAndPersist((prev) => ({
                      ...prev,
                      moves: [...prev.moves, newMove],
                    }));
                    setAddMoveOpen(false);
                    toast({
                      title: "Move added",
                      description: `${template.name} has been added to this campaign`,
                    });
                  }}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-fg">{template.name}</h4>
                      <p className="text-sm text-muted">
                        {template.durationDays} days • Target: {template.targetHint} {template.kpi}
                      </p>
                    </div>
                    <Button variant="outline" size="sm">
                      Use Template
                    </Button>
                  </div>
                </button>
              ))}
            </div>
          </ModalShell>
        )}
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-serif text-fg">Campaigns</h1>
          <p className="mt-2 text-lg text-muted">90-day containers for your marketing objectives</p>
        </div>
        <div className="flex items-center gap-3">
          <Pill>
            Active: {activeCount}/{activeCap}
          </Pill>
          <Button variant="primary" onClick={() => setCreateOpen(true)}>
            <Layers className="mr-2 h-4 w-4" />
            New Campaign
          </Button>
        </div>
      </div>

      <div className="grid gap-6">
        {state.campaigns.map((campaign) => (
          <div
            key={campaign.id}
            className={cn(
              "rounded-2xl border bg-card p-8 transition-all hover:shadow-lg",
              campaign.status === "active"
                ? "border-primary/20 bg-primary/5"
                : "border-border bg-card",
              campaignId === campaign.id && "ring-2 ring-primary ring-offset-2"
            )}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-4">
                  <h2
                    className="text-2xl font-serif text-fg cursor-pointer hover:text-primary"
                    onClick={() => navigate(`/app/campaigns/${campaign.id}`)}
                  >
                    {campaign.name}
                  </h2>
                  <Pill>{campaign.status}</Pill>
                </div>
                <p className="mt-2 text-lg text-muted">{campaign.objective}</p>
                <div className="mt-4 flex items-center gap-6 text-sm text-muted">
                  <span>Cohort: {campaign.cohort}</span>
                  <span>Theme: {campaign.theme}</span>
                  <span>Moves: {state.moves.filter(m => m.campaignId === campaign.id).length}</span>
                </div>
                <div className="mt-6 grid grid-cols-3 gap-6">
                  {campaign.kpis.map((kpi, i) => (
                    <div key={i} className="text-center">
                      <div className="text-2xl font-bold text-primary">{kpi.value}</div>
                      <div className="text-sm text-muted">{kpi.label}</div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="flex items-center gap-3 ml-8">
                <Button
                  variant="outline"
                  onClick={() => requestActivateCampaign(campaign.id)}
                >
                  {campaign.status === "active" ? "Pause" : "Activate"}
                </Button>
                <Button
                  variant="ghost"
                  onClick={() => navigate(`/app/campaigns/${campaign.id}`)}
                >
                  View
                </Button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {state.campaigns.length === 0 && (
        <div className="rounded-2xl border border-border bg-surface p-16 text-center">
          <h3 className="text-2xl font-serif text-fg">No campaigns yet</h3>
          <p className="mt-4 text-lg text-muted">Create your first 90-day campaign to get started</p>
          <Button variant="primary" className="mt-6" onClick={() => setCreateOpen(true)}>
            Create Campaign
          </Button>
        </div>
      )}

      {createOpen && (
        <ModalShell
          title="Create Campaign"
          description="Set up a new 90-day marketing campaign"
          onClose={() => setCreateOpen(false)}
        >
          <CreateCampaignForm
            onSubmit={(data) => {
              const newCampaign: Campaign = {
                id: `c_${Date.now()}`,
                status: "draft",
                ...data,
                northStar: { label: data.kpi || "Leads", series6: [0, 0, 0, 0, 0, 0] },
                kpis: [],
              };
              setAndPersist((prev) => ({
                ...prev,
                campaigns: [...prev.campaigns, newCampaign],
              }));
              setCreateOpen(false);
              toast({
                title: "Campaign created",
                description: `${data.name} is ready to configure`,
              });

              // Check if activating would exceed limit
              const activeCount = state.campaigns.filter((c) => c.status === "active").length;
              if (activeCount >= activeCap) {
                toast({
                  title: "Limit reached",
                  description: `Your plan allows ${activeCap} active campaigns. Pause or complete one to activate another.`,
                  tone: "warn",
                });
                openLimitModal({ kind: "active_campaigns", limit: activeCap });
              }
            }}
          />
        </ModalShell>
      )}
    </div>
  );
}

function CreateCampaignForm({
  onSubmit,
}: {
  onSubmit: (data: any) => void;
}) {
  const [data, setData] = useState({
    name: "",
    objective: "",
    cohort: "",
    theme: "",
    kpi: "Leads",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!data.name || !data.objective) return;
    onSubmit(data);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="text-sm font-medium text-fg">Campaign Name</label>
        <input
          type="text"
          className="mt-2 w-full rounded-xl border border-border bg-surface px-4 py-3 text-fg"
          value={data.name}
          onChange={(e) => setData({ ...data, name: e.target.value })}
          placeholder="e.g., Q1 Product Launch"
          required
        />
      </div>
      <div>
        <label className="text-sm font-medium text-fg">Objective</label>
        <textarea
          className="mt-2 w-full rounded-xl border border-border bg-surface px-4 py-3 text-fg"
          rows={3}
          value={data.objective}
          onChange={(e) => setData({ ...data, objective: e.target.value })}
          placeholder="What do you want to achieve?"
          required
        />
      </div>
      <div>
        <label className="text-sm font-medium text-fg">Target Cohort</label>
        <input
          type="text"
          className="mt-2 w-full rounded-xl border border-border bg-surface px-4 py-3 text-fg"
          value={data.cohort}
          onChange={(e) => setData({ ...data, cohort: e.target.value })}
          placeholder="e.g., SMB prospects"
          required
        />
      </div>
      <div>
        <label className="text-sm font-medium text-fg">Theme</label>
        <input
          type="text"
          className="mt-2 w-full rounded-xl border border-border bg-surface px-4 py-3 text-fg"
          value={data.theme}
          onChange={(e) => setData({ ...data, theme: e.target.value })}
          placeholder="e.g., Innovation & Efficiency"
          required
        />
      </div>
      <div>
        <label className="text-sm font-medium text-fg">Primary KPI</label>
        <select
          className="mt-2 w-full rounded-xl border border-border bg-surface px-4 py-3 text-fg"
          value={data.kpi}
          onChange={(e) => setData({ ...data, kpi: e.target.value })}
        >
          <option value="Leads">Marketing Qualified Leads</option>
          <option value="Sales">Sales Revenue</option>
          <option value="Demo">Demo Requests</option>
        </select>
      </div>
      <div className="flex justify-end gap-3 pt-4">
        <Button type="button" variant="outline" onClick={() => window.history.back()}>
          Cancel
        </Button>
        <Button type="submit" variant="primary">
          Create Campaign
        </Button>
      </div>
    </form>
  );
}
