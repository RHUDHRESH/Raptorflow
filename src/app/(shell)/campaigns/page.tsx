"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Edit3, Plus, Search, Trash2 } from "lucide-react";

import { cn } from "@/lib/utils";
import { notify } from "@/lib/notifications";
import { useWorkspace } from "@/components/workspace/WorkspaceProvider";
import { useCampaignStore, type Campaign } from "@/stores/campaignStore";
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

function statusLabel(status: string): string {
  const found = STATUSES.find((s) => s.value === (status || "").toLowerCase());
  return found?.label || (status || "unknown");
}

export default function CampaignsPage() {
  const router = useRouter();
  const { workspaceId } = useWorkspace();
  const {
    campaigns,
    isLoading,
    error,
    clearError,
    fetchCampaigns,
    createCampaign,
    updateCampaign,
    deleteCampaign,
  } = useCampaignStore();

  const [searchQuery, setSearchQuery] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editing, setEditing] = useState<Campaign | null>(null);

  const [title, setTitle] = useState("");
  const [objective, setObjective] = useState("acquire");
  const [status, setStatus] = useState("active");
  const [description, setDescription] = useState("");

  useEffect(() => {
    if (!workspaceId) return;
    fetchCampaigns(workspaceId);
  }, [workspaceId, fetchCampaigns]);

  const filtered = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return campaigns;
    return campaigns.filter((c) => {
      return (
        c.title.toLowerCase().includes(q) ||
        (c.description || "").toLowerCase().includes(q) ||
        (c.objective || "").toLowerCase().includes(q)
      );
    });
  }, [campaigns, searchQuery]);

  function openCreate() {
    clearError();
    setEditing(null);
    setTitle("");
    setObjective("acquire");
    setStatus("active");
    setDescription("");
    setIsModalOpen(true);
  }

  function openEdit(campaign: Campaign) {
    clearError();
    setEditing(campaign);
    setTitle(campaign.title);
    setObjective((campaign.objective || "acquire").toLowerCase());
    setStatus((campaign.status || "active").toLowerCase());
    setDescription(campaign.description || "");
    setIsModalOpen(true);
  }

  async function submit() {
    if (!workspaceId) {
      notify.error("Workspace not initialized yet");
      return;
    }

    const name = title.trim();
    if (!name) {
      notify.error("Campaign name is required");
      return;
    }

    try {
      if (editing) {
        await updateCampaign(workspaceId, editing.id, {
          name,
          objective,
          status,
          description: description.trim() || undefined,
        });
        notify.success("Campaign updated");
        setIsModalOpen(false);
        return;
      }

      const created = await createCampaign(workspaceId, {
        name,
        objective,
        status,
        description: description.trim() || undefined,
      });
      notify.success("Campaign created");
      setIsModalOpen(false);
      router.push(`/campaigns/${created.id}`);
    } catch (e: any) {
      notify.error(e?.message || "Request failed");
    }
  }

  async function removeCampaign(campaign: Campaign) {
    if (!workspaceId) return;
    if (!window.confirm(`Delete campaign "${campaign.title}"? This cannot be undone.`)) return;
    try {
      await deleteCampaign(workspaceId, campaign.id);
      notify.success("Campaign deleted");
    } catch (e: any) {
      notify.error(e?.message || "Delete failed");
    }
  }

  return (
    <div className="min-h-screen bg-[var(--canvas)]">
      <div className="max-w-6xl mx-auto px-6 py-8 space-y-6">
        <header className="flex items-start justify-between gap-4">
          <div className="space-y-1">
            <h1 className="font-serif text-3xl text-[var(--ink)]">Campaigns</h1>
            <p className="text-sm text-[var(--muted)]">
              Real campaigns, persisted to the database. No paywalls.
            </p>
          </div>
          <button
            onClick={openCreate}
            className="flex items-center gap-2 px-4 py-2 rounded-[var(--radius)] bg-[var(--ink)] text-white text-sm font-medium hover:bg-[var(--ink)]/90"
          >
            <Plus className="w-4 h-4" />
            New Campaign
          </button>
        </header>

        <div className="flex items-center gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[var(--muted)]" />
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search campaigns..."
              className="w-full h-10 pl-9 pr-3 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--paper)] text-sm text-[var(--ink)]"
            />
          </div>
          <button
            onClick={() => workspaceId && fetchCampaigns(workspaceId)}
            disabled={!workspaceId || isLoading}
            className="h-10 px-3 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--paper)] text-sm text-[var(--ink)] disabled:opacity-50"
          >
            {isLoading ? "Loading..." : "Refresh"}
          </button>
        </div>

        {error ? (
          <div className="p-3 rounded-[var(--radius)] border border-[var(--error)]/30 bg-[var(--error-bg)] text-[var(--error)] text-sm">
            {error}
          </div>
        ) : null}

        {filtered.length === 0 && !isLoading ? (
          <BlueprintCard showCorners padding="lg">
            <div className="space-y-2">
              <h2 className="font-serif text-xl text-[var(--ink)]">No campaigns yet</h2>
              <p className="text-sm text-[var(--muted)]">
                Create your first campaign. It will be saved to the database and visible across reloads.
              </p>
              <div>
                <button
                  onClick={openCreate}
                  className="mt-2 inline-flex items-center gap-2 px-4 py-2 rounded-[var(--radius)] bg-[var(--ink)] text-white text-sm font-medium"
                >
                  <Plus className="w-4 h-4" />
                  Create Campaign
                </button>
              </div>
            </div>
          </BlueprintCard>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filtered.map((campaign) => (
              <BlueprintCard
                key={campaign.id}
                showCorners
                padding="md"
                className="group cursor-pointer hover:border-[var(--blueprint)] transition-colors"
                onClick={() => router.push(`/campaigns/${campaign.id}`)}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <BlueprintBadge variant={statusVariant(campaign.status)} dot>
                        {statusLabel(campaign.status)}
                      </BlueprintBadge>
                      <span className="font-mono text-[10px] text-[var(--muted)]">
                        {campaign.objective}
                      </span>
                    </div>
                    <h3 className="font-serif text-xl text-[var(--ink)]">{campaign.title}</h3>
                    {campaign.description ? (
                      <p className="text-sm text-[var(--secondary)] line-clamp-2">
                        {campaign.description}
                      </p>
                    ) : (
                      <p className="text-sm text-[var(--muted)] italic">No description</p>
                    )}
                  </div>

                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        openEdit(campaign);
                      }}
                      className="p-2 rounded-[var(--radius-sm)] hover:bg-[var(--surface-hover)]"
                      aria-label="Edit campaign"
                    >
                      <Edit3 className="w-4 h-4 text-[var(--muted)]" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        void removeCampaign(campaign);
                      }}
                      className="p-2 rounded-[var(--radius-sm)] hover:bg-[var(--error-bg)]"
                      aria-label="Delete campaign"
                    >
                      <Trash2 className="w-4 h-4 text-[var(--error)]" />
                    </button>
                  </div>
                </div>

                <div className="mt-4 flex items-center justify-between text-[10px] font-mono text-[var(--muted)]">
                  <span>ID</span>
                  <span className={cn("truncate max-w-[70%]")}>{campaign.id}</span>
                </div>
              </BlueprintCard>
            ))}
          </div>
        )}
      </div>

      <BlueprintModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editing ? "Edit Campaign" : "New Campaign"}
        size="md"
        footer={
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsModalOpen(false)}
              className="h-9 px-3 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--paper)] text-sm text-[var(--ink)]"
            >
              Cancel
            </button>
            <button
              onClick={() => void submit()}
              disabled={isLoading}
              className="h-9 px-3 rounded-[var(--radius)] bg-[var(--ink)] text-white text-sm font-medium disabled:opacity-50"
            >
              {isLoading ? "Saving..." : editing ? "Save" : "Create"}
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
              placeholder="Campaign name"
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
              placeholder="What is this campaign doing?"
            />
          </label>

          {error ? (
            <div className="text-sm text-[var(--error)]">{error}</div>
          ) : null}
        </div>
      </BlueprintModal>
    </div>
  );
}
