"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Edit3, Plus, Trash2 } from "lucide-react";

import { cn } from "@/lib/utils";
import { notify } from "@/lib/notifications";
import { useWorkspace } from "@/components/workspace/WorkspaceProvider";
import { useCampaignStore, type Campaign } from "@/stores/campaignStore";
import { useMovesStore } from "@/stores/movesStore";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintModal } from "@/components/ui/BlueprintModal";

const OBJECTIVES = [
  { value: "acquire", label: "Acquire" },
  { value: "convert", label: "Convert" },
  { value: "launch", label: "Launch" },
  { value: "proof", label: "Proof" },
  { value: "retain", label: "Retain" },
  { value: "reposition", label: "Reposition" },
];

const STATUSES = [
  { value: "planned", label: "Planned" },
  { value: "active", label: "Active" },
  { value: "paused", label: "Paused" },
  { value: "wrapup", label: "Wrap-up" },
  { value: "archived", label: "Archived" },
];

function statusVariant(status: string): "default" | "success" | "warning" | "info" {
  switch ((status || "").toLowerCase()) {
    case "active":
      return "success";
    case "paused":
    case "wrapup":
      return "warning";
    case "planned":
      return "info";
    case "archived":
    default:
      return "default";
  }
}

export default function CampaignDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const { workspaceId } = useWorkspace();

  const {
    campaigns,
    isLoading: campaignsLoading,
    fetchCampaigns,
    updateCampaign,
    deleteCampaign,
    error: campaignsError,
  } = useCampaignStore();

  const { moves, isLoading: movesLoading, fetchMoves } = useMovesStore();

  const campaign = useMemo(
    () => campaigns.find((c) => c.id === params.id),
    [campaigns, params.id]
  );

  const campaignMoves = useMemo(() => {
    return moves.filter((m) => m.campaignId === params.id);
  }, [moves, params.id]);

  const [isEditOpen, setIsEditOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [objective, setObjective] = useState("acquire");
  const [status, setStatus] = useState("active");
  const [description, setDescription] = useState("");

  useEffect(() => {
    if (!workspaceId) return;
    if (!campaign) fetchCampaigns(workspaceId);
    fetchMoves(workspaceId);
  }, [workspaceId, campaign, fetchCampaigns, fetchMoves]);

  useEffect(() => {
    if (!campaign) return;
    setTitle(campaign.title);
    setObjective((campaign.objective || "acquire").toLowerCase());
    setStatus((campaign.status || "active").toLowerCase());
    setDescription(campaign.description || "");
  }, [campaign?.id]);

  async function save() {
    if (!workspaceId || !campaign) return;
    const name = title.trim();
    if (!name) {
      notify.error("Campaign name is required");
      return;
    }

    try {
      await updateCampaign(workspaceId, campaign.id, {
        name,
        objective,
        status,
        description: description.trim() || undefined,
      });
      notify.success("Campaign updated");
      setIsEditOpen(false);
    } catch (e: any) {
      notify.error(e?.message || "Update failed");
    }
  }

  async function remove() {
    if (!workspaceId || !campaign) return;
    if (!window.confirm(`Delete campaign "${campaign.title}"? This cannot be undone.`)) return;
    try {
      await deleteCampaign(workspaceId, campaign.id);
      notify.success("Campaign deleted");
      router.push("/campaigns");
    } catch (e: any) {
      notify.error(e?.message || "Delete failed");
    }
  }

  const isLoading = campaignsLoading || movesLoading;

  if (!workspaceId) {
    return (
      <div className="p-10 text-sm text-[var(--muted)]">Initializing workspace...</div>
    );
  }

  if (isLoading && !campaign) {
    return (
      <div className="p-10 text-sm text-[var(--muted)]">Loading campaign...</div>
    );
  }

  if (!campaign) {
    return (
      <div className="p-10 space-y-4">
        <button
          onClick={() => router.push("/campaigns")}
          className="inline-flex items-center gap-2 text-sm text-[var(--muted)] hover:text-[var(--ink)]"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to campaigns
        </button>
        <div className="p-4 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--paper)]">
          <h1 className="font-serif text-2xl text-[var(--ink)]">Campaign not found</h1>
          <p className="text-sm text-[var(--muted)] mt-1">
            {campaignsError || "This campaign id does not exist in the current workspace."}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--canvas)]">
      <div className="max-w-6xl mx-auto px-6 py-8 space-y-6">
        <button
          onClick={() => router.push("/campaigns")}
          className="inline-flex items-center gap-2 text-sm text-[var(--muted)] hover:text-[var(--ink)]"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to campaigns
        </button>

        <header className="flex items-start justify-between gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <BlueprintBadge variant={statusVariant(campaign.status)} dot>
                {campaign.status}
              </BlueprintBadge>
              <span className="font-mono text-[10px] text-[var(--muted)]">
                objective: {campaign.objective}
              </span>
            </div>
            <h1 className="font-serif text-4xl text-[var(--ink)]">{campaign.title}</h1>
            {campaign.description ? (
              <p className="text-[var(--secondary)]">{campaign.description}</p>
            ) : (
              <p className="text-[var(--muted)] italic">No description</p>
            )}
            <div className="font-mono text-[10px] text-[var(--muted)]">ID: {campaign.id}</div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsEditOpen(true)}
              className="inline-flex items-center gap-2 h-10 px-3 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--paper)] text-sm text-[var(--ink)] hover:bg-[var(--surface-hover)]"
            >
              <Edit3 className="w-4 h-4" />
              Edit
            </button>
            <button
              onClick={() => router.push(`/moves?campaignId=${encodeURIComponent(campaign.id)}&new=1`)}
              className="inline-flex items-center gap-2 h-10 px-3 rounded-[var(--radius)] bg-[var(--ink)] text-white text-sm font-medium hover:bg-[var(--ink)]/90"
            >
              <Plus className="w-4 h-4" />
              New Move
            </button>
            <button
              onClick={() => void remove()}
              className="inline-flex items-center gap-2 h-10 px-3 rounded-[var(--radius)] border border-[var(--error)]/30 bg-[var(--error-bg)] text-[var(--error)] text-sm hover:opacity-90"
            >
              <Trash2 className="w-4 h-4" />
              Delete
            </button>
          </div>
        </header>

        <BlueprintCard title="Moves In This Campaign" code="MOVES" showCorners padding="md">
          {campaignMoves.length === 0 ? (
            <div className="space-y-2">
              <p className="text-sm text-[var(--muted)]">
                No moves are linked to this campaign yet.
              </p>
              <button
                onClick={() => router.push(`/moves?campaignId=${encodeURIComponent(campaign.id)}&new=1`)}
                className="inline-flex items-center gap-2 h-9 px-3 rounded-[var(--radius)] bg-[var(--ink)] text-white text-sm font-medium"
              >
                <Plus className="w-4 h-4" />
                Create a move
              </button>
            </div>
          ) : (
            <div className="divide-y divide-[var(--border-subtle)]">
              {campaignMoves.map((m) => (
                <div
                  key={m.id}
                  className="py-3 flex items-center justify-between gap-3"
                >
                  <div className="min-w-0">
                    <div className="font-medium text-[var(--ink)] truncate">{m.name}</div>
                    <div className="text-xs text-[var(--muted)]">
                      {m.category} | {m.status}
                    </div>
                  </div>
                  <button
                    onClick={() => router.push("/moves")}
                    className={cn(
                      "text-xs font-mono px-2 py-1 rounded-[var(--radius-sm)] border border-[var(--border)]",
                      "hover:bg-[var(--surface-hover)]"
                    )}
                  >
                    View in Moves
                  </button>
                </div>
              ))}
            </div>
          )}
        </BlueprintCard>

        {campaignsError ? (
          <div className="text-sm text-[var(--error)]">{campaignsError}</div>
        ) : null}
      </div>

      <BlueprintModal
        isOpen={isEditOpen}
        onClose={() => setIsEditOpen(false)}
        title="Edit Campaign"
        size="md"
        footer={
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsEditOpen(false)}
              className="h-9 px-3 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--paper)] text-sm text-[var(--ink)]"
            >
              Cancel
            </button>
            <button
              onClick={() => void save()}
              disabled={campaignsLoading}
              className="h-9 px-3 rounded-[var(--radius)] bg-[var(--ink)] text-white text-sm font-medium disabled:opacity-50"
            >
              {campaignsLoading ? "Saving..." : "Save"}
            </button>
          </div>
        }
      >
        <div className="space-y-4">
          <label className="grid gap-2">
            <span className="text-sm font-medium text-[var(--ink)]">Name</span>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full h-10 px-3 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--surface)] text-[var(--ink)]"
            />
          </label>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <label className="grid gap-2">
              <span className="text-sm font-medium text-[var(--ink)]">Objective</span>
              <select
                value={objective}
                onChange={(e) => setObjective(e.target.value)}
                className="w-full h-10 px-3 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--surface)] text-[var(--ink)]"
              >
                {OBJECTIVES.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </label>

            <label className="grid gap-2">
              <span className="text-sm font-medium text-[var(--ink)]">Status</span>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                className="w-full h-10 px-3 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--surface)] text-[var(--ink)]"
              >
                {STATUSES.map((s) => (
                  <option key={s.value} value={s.value}>
                    {s.label}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <label className="grid gap-2">
            <span className="text-sm font-medium text-[var(--ink)]">Description</span>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full min-h-24 px-3 py-2 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--surface)] text-[var(--ink)]"
            />
          </label>
        </div>
      </BlueprintModal>
    </div>
  );
}
