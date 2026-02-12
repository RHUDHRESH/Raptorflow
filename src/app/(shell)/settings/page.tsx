"use client";

import { type ChangeEvent, useEffect, useMemo, useState } from "react";
import { notify } from "@/lib/notifications";
import { useWorkspace } from "@/components/workspace/WorkspaceProvider";
import { workspacesService } from "@/services/workspaces.service";
import { assetsService, type AssetRecord } from "@/services/assets.service";
import { useBCMStore } from "@/stores/bcmStore";
import { Check, AlertTriangle, Sparkles, Upload, Trash2 } from "lucide-react";

// Fixture data embedded for dev harness
const FIXTURES = [
  {
    id: "saas",
    name: "FlowBoard",
    industry: "SaaS / Productivity",
    stage: "Series A",
    oneLiner: "AI-powered project management that auto-prioritizes work and surfaces blockers before standup.",
    color: "#3b82f6",
  },
  {
    id: "ecommerce",
    name: "EcoThread",
    industry: "E-commerce / Fashion",
    stage: "Seed",
    oneLiner: "Sustainable fashion marketplace connecting conscious consumers with verified ethical brands.",
    color: "#22c55e",
  },
  {
    id: "agency",
    name: "GrowthForge",
    industry: "Marketing / Agency",
    stage: "Bootstrapped",
    oneLiner: "B2B SaaS marketing agency that builds predictable growth engines for technical founders.",
    color: "#f59e0b",
  },
];

export default function SettingsPage() {
  const { workspaceId, workspace, refresh } = useWorkspace();
  const { manifest: bcm, seedBCM, isSeeding } = useBCMStore();
  const [name, setName] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [assets, setAssets] = useState<AssetRecord[]>([]);
  const [isLoadingAssets, setIsLoadingAssets] = useState(false);
  const [isUploadingAsset, setIsUploadingAsset] = useState(false);

  useEffect(() => {
    if (workspace?.name) setName(workspace.name);
  }, [workspace?.name]);

  useEffect(() => {
    if (!workspaceId) return;
    void loadAssets(workspaceId);
  }, [workspaceId]);

  const hasChanges = useMemo(() => {
    if (!workspace) return false;
    return name.trim() !== "" && name.trim() !== workspace.name;
  }, [name, workspace]);

  async function saveWorkspace() {
    if (!workspaceId) return;
    if (!hasChanges) return;

    setIsSaving(true);
    setError(null);
    try {
      await workspacesService.update(workspaceId, { name: name.trim() });
      await refresh();
      notify.success("Workspace updated");
    } catch (e: any) {
      const message = e?.message || "Failed to save workspace";
      setError(message);
      notify.error(message);
    } finally {
      setIsSaving(false);
    }
  }

  // Determine which fixture is active by checking company name in BCM
  const activeFixtureId = useMemo(() => {
    if (!bcm?.foundation?.company) return null;
    const company = bcm.foundation.company;
    if (company === "FlowBoard") return "saas";
    if (company === "EcoThread") return "ecommerce";
    if (company === "GrowthForge") return "agency";
    return null;
  }, [bcm]);

  async function activateFixture(fixtureId: string) {
    if (!workspaceId) return;

    try {
      // Dynamically import the fixture JSON
      let fixtureData;
      switch (fixtureId) {
        case "saas":
          fixtureData = await import("@/../backend/fixtures/business_context_saas.json");
          break;
        case "ecommerce":
          fixtureData = await import("@/../backend/fixtures/business_context_ecommerce.json");
          break;
        case "agency":
          fixtureData = await import("@/../backend/fixtures/business_context_agency.json");
          break;
        default:
          throw new Error("Unknown fixture");
      }

      await seedBCM(workspaceId, fixtureData.default || fixtureData);
      notify.success(`Activated ${FIXTURES.find((f) => f.id === fixtureId)?.name}`);
    } catch (e: any) {
      notify.error(e?.message || "Failed to activate fixture");
    }
  }

  async function loadAssets(currentWorkspaceId: string) {
    setIsLoadingAssets(true);
    try {
      const result = await assetsService.list(currentWorkspaceId, { limit: 50, offset: 0 });
      setAssets(result.assets || []);
    } catch (e: any) {
      notify.error(e?.message || "Failed to load assets");
    } finally {
      setIsLoadingAssets(false);
    }
  }

  async function onAssetSelected(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!workspaceId || !file) return;

    setIsUploadingAsset(true);
    try {
      await assetsService.upload(workspaceId, file, { source: "settings" });
      notify.success(`Uploaded ${file.name}`);
      await loadAssets(workspaceId);
    } catch (e: any) {
      notify.error(e?.message || "Asset upload failed");
    } finally {
      setIsUploadingAsset(false);
      event.target.value = "";
    }
  }

  async function deleteAsset(assetId: string) {
    if (!workspaceId) return;
    try {
      await assetsService.remove(workspaceId, assetId);
      setAssets((prev) => prev.filter((asset) => asset.id !== assetId));
      notify.success("Asset deleted");
    } catch (e: any) {
      notify.error(e?.message || "Failed to delete asset");
    }
  }

  return (
    <div className="min-h-[calc(100vh-80px)] bg-[var(--canvas)]">
      <div className="max-w-3xl mx-auto px-8 py-10 space-y-8">
        <header className="space-y-1">
          <h1 className="font-serif text-3xl text-[var(--ink)]">Settings</h1>
          <p className="text-sm text-[var(--ink-muted)]">
            No login, no paywalls. Settings are scoped to your current workspace.
          </p>
        </header>

        <section className="bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-lg)] p-6 space-y-4">
          <div className="space-y-1">
            <h2 className="font-serif text-lg text-[var(--ink)]">Workspace</h2>
            <p className="text-sm text-[var(--ink-muted)]">
              Workspace id is the tenant boundary. It is sent as{" "}
              <span className="font-mono text-[var(--ink)]">x-workspace-id</span>{" "}
              on API calls.
            </p>
          </div>

          <div className="grid gap-4">
            <label className="grid gap-2">
              <span className="text-sm font-medium text-[var(--ink)]">Name</span>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3 py-2 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--surface)] text-[var(--ink)]"
                placeholder="Workspace name"
              />
            </label>

            <div className="grid gap-2">
              <span className="text-sm font-medium text-[var(--ink)]">ID</span>
              <div className="px-3 py-2 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--surface)] font-mono text-xs text-[var(--ink)]">
                {workspaceId}
              </div>
            </div>

            {workspace?.slug ? (
              <div className="grid gap-2">
                <span className="text-sm font-medium text-[var(--ink)]">Slug</span>
                <div className="px-3 py-2 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--surface)] font-mono text-xs text-[var(--ink)]">
                  {workspace.slug}
                </div>
              </div>
            ) : null}
          </div>

          {error ? (
            <div className="text-sm text-[var(--error)]">{error}</div>
          ) : null}

          <div className="flex items-center gap-3">
            <button
              onClick={() => void saveWorkspace()}
              disabled={!hasChanges || isSaving}
              className="px-4 py-2 rounded-[var(--radius)] bg-[var(--ink)] text-white text-sm font-medium disabled:opacity-50"
            >
              {isSaving ? "Saving..." : "Save"}
            </button>
            {!hasChanges ? (
              <span className="text-xs text-[var(--ink-muted)]">No changes</span>
            ) : null}
          </div>
        </section>

        {/* BCM Fixture Switcher - Dev Harness */}
        <section className="bg-[var(--paper)] border-2 border-amber-500/30 rounded-[var(--radius-lg)] p-6 space-y-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
            <div className="space-y-1">
              <h2 className="font-serif text-lg text-[var(--ink)] flex items-center gap-2">
                Business Context (Dev)
                <span className="text-[10px] px-2 py-0.5 bg-amber-500/10 text-amber-600 rounded-full uppercase tracking-wider font-sans">
                  Temporary
                </span>
              </h2>
              <p className="text-sm text-[var(--ink-muted)]">
                Test the BCM pipeline by activating different business personalities.
                This transforms the entire app — Muse context, ICPs, company name, etc.
              </p>
            </div>
          </div>

          {/* Current Status */}
          {bcm?.foundation?.company && (
            <div className="p-3 rounded-lg bg-[var(--surface)] border border-[var(--border)]">
              <div className="flex items-center gap-2 text-sm">
                <Sparkles className="w-4 h-4 text-[var(--blueprint)]" />
                <span className="text-[var(--ink-muted)]">Currently active:</span>
                <span className="font-medium text-[var(--ink)]">{bcm.foundation.company}</span>
                <span className="text-xs text-[var(--muted)]">· v{bcm.version} · {bcm.meta?.icps_count} ICPs</span>
              </div>
            </div>
          )}

          {/* Fixture Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {FIXTURES.map((fixture) => {
              const isActive = activeFixtureId === fixture.id;
              return (
                <div
                  key={fixture.id}
                  className={`relative p-4 rounded-[var(--radius)] border-2 transition-all ${
                    isActive
                      ? "border-[var(--blueprint)] bg-[var(--blueprint)]/5"
                      : "border-[var(--border)] hover:border-[var(--blueprint)]/50"
                  }`}
                >
                  {isActive && (
                    <div className="absolute top-3 right-3">
                      <Check className="w-5 h-5 text-[var(--blueprint)]" />
                    </div>
                  )}

                  {/* Icon */}
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-lg mb-3"
                    style={{ backgroundColor: fixture.color }}
                  >
                    {fixture.name[0]}
                  </div>

                  {/* Content */}
                  <h3 className="font-serif text-lg text-[var(--ink)] mb-1">{fixture.name}</h3>
                  <div className="flex flex-wrap gap-2 mb-3">
                    <span className="text-[10px] px-2 py-0.5 bg-[var(--surface)] border border-[var(--border)] rounded-full text-[var(--muted)]">
                      {fixture.industry}
                    </span>
                    <span className="text-[10px] px-2 py-0.5 bg-[var(--surface)] border border-[var(--border)] rounded-full text-[var(--muted)]">
                      {fixture.stage}
                    </span>
                  </div>
                  <p className="text-xs text-[var(--ink-muted)] italic mb-4 line-clamp-3">
                    "{fixture.oneLiner}"
                  </p>

                  {/* Action */}
                  <button
                    onClick={() => activateFixture(fixture.id)}
                    disabled={isSeeding || isActive}
                    className={`w-full px-3 py-2 rounded-[var(--radius)] text-sm font-medium transition-all ${
                      isActive
                        ? "bg-[var(--blueprint)]/10 text-[var(--blueprint)] cursor-default"
                        : "bg-[var(--surface)] border border-[var(--border)] text-[var(--ink)] hover:bg-[var(--blueprint)] hover:text-white hover:border-[var(--blueprint)]"
                    }`}
                  >
                    {isSeeding ? "Activating..." : isActive ? "Active" : "Activate"}
                  </button>
                </div>
              );
            })}
          </div>

          <p className="text-xs text-[var(--muted)]">
            Tip: After activating, check the Dashboard BCM panel, try Muse with "What's my value prop?",
            or view Moves to see ICP badges update instantly.
          </p>
        </section>

        <section className="bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-lg)] p-6 space-y-4">
          <div className="space-y-1">
            <h2 className="font-serif text-lg text-[var(--ink)]">Assets</h2>
            <p className="text-sm text-[var(--ink-muted)]">
              Upload images and files for this workspace. Files are stored under the workspace path in Supabase Storage.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <label className="inline-flex items-center gap-2 px-4 py-2 rounded-[var(--radius)] bg-[var(--ink)] text-white text-sm font-medium cursor-pointer disabled:opacity-50">
              <Upload className="w-4 h-4" />
              <span>{isUploadingAsset ? "Uploading..." : "Upload File"}</span>
              <input
                type="file"
                className="hidden"
                onChange={onAssetSelected}
                disabled={isUploadingAsset || !workspaceId}
              />
            </label>
            {isLoadingAssets ? (
              <span className="text-xs text-[var(--ink-muted)]">Loading assets...</span>
            ) : (
              <span className="text-xs text-[var(--ink-muted)]">{assets.length} file(s)</span>
            )}
          </div>

          {assets.length === 0 ? (
            <div className="text-sm text-[var(--ink-muted)] border border-dashed border-[var(--border)] rounded-[var(--radius)] p-4">
              No assets uploaded yet.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {assets.map((asset) => (
                <div
                  key={asset.id}
                  className="border border-[var(--border)] rounded-[var(--radius)] p-3 bg-[var(--surface)] space-y-2"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <div className="text-sm font-medium text-[var(--ink)] truncate">{asset.original_name}</div>
                      <div className="text-xs text-[var(--ink-muted)]">
                        {(asset.size_bytes / 1024).toFixed(1)} KB · {asset.asset_type}
                      </div>
                    </div>
                    <button
                      className="p-1.5 rounded-[var(--radius)] border border-[var(--border)] text-[var(--ink-muted)] hover:text-[var(--ink)]"
                      onClick={() => void deleteAsset(asset.id)}
                      title="Delete asset"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  {asset.asset_type === "image" && asset.public_url ? (
                    <img
                      src={asset.public_url}
                      alt={asset.original_name}
                      className="w-full h-32 object-cover rounded-[var(--radius)] border border-[var(--border)]"
                    />
                  ) : null}
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
