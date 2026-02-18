"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { Layout } from "@/components/raptor/shell/Layout";
import { Card, CardHeader, CardFooter } from "@/components/raptor/ui/Card";
import { Button } from "@/components/raptor/ui/Button";
import { Badge } from "@/components/raptor/ui/Badge";
import { Input } from "@/components/raptor/ui/Input";
import { Modal, ConfirmDialog } from "@/components/raptor/ui/Modal";
import { EmptyStateOrigami, LockSeal } from "@/components/raptor/animations/LottieOrigami";
import { useWorkspace } from "@/components/workspace/WorkspaceProvider";
import { useBCMStore } from "@/stores/bcmStore";
import { notify } from "@/lib/notifications";
import {
  Save,
  Upload,
  Trash2,
  AlertTriangle,
  Check,
  Sparkles,
  Building2,
  ShoppingBag,
  Briefcase,
} from "lucide-react";

// ═══════════════════════════════════════════════════════════════════════════════
// SETTINGS PAGE — Workspace Configuration
// No login, no paywalls. Settings scoped to current workspace.
// ═══════════════════════════════════════════════════════════════════════════════

// Fixture data for dev harness
const FIXTURES = [
  {
    id: "saas",
    name: "FlowBoard",
    industry: "SaaS / Productivity",
    stage: "Series A",
    oneLiner: "AI-powered project management that auto-prioritizes work and surfaces blockers before standup.",
    color: "#3D5A6B",
    icon: Building2,
  },
  {
    id: "ecommerce",
    name: "EcoThread",
    industry: "E-commerce / Fashion",
    stage: "Seed",
    oneLiner: "Sustainable fashion marketplace connecting conscious consumers with verified ethical brands.",
    color: "#3D5A42",
    icon: ShoppingBag,
  },
  {
    id: "agency",
    name: "GrowthForge",
    industry: "Marketing / Agency",
    stage: "Bootstrapped",
    oneLiner: "B2B SaaS marketing agency that builds predictable growth engines for technical founders.",
    color: "#8B6914",
    icon: Briefcase,
  },
];

interface Asset {
  id: string;
  original_name: string;
  size_bytes: number;
  asset_type: string;
  public_url?: string;
}

export default function SettingsPage() {
  const pageRef = useRef<HTMLDivElement>(null);
  const { workspaceId, workspace, refresh } = useWorkspace();
  const { manifest: bcm, seedBCM, isSeeding } = useBCMStore();

  const [workspaceName, setWorkspaceName] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [isLoadingAssets, setIsLoadingAssets] = useState(false);

  // Entrance animation
  useEffect(() => {
    if (!pageRef.current) return;

    const tl = gsap.timeline({ defaults: { ease: "power2.out" } });

    tl.fromTo(
      ".settings-section",
      { y: 20, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.4, stagger: 0.1 }
    );

    return () => {
      tl.kill();
    };
  }, []);

  // Sync workspace name
  useEffect(() => {
    if (workspace?.name) {
      setWorkspaceName(workspace.name);
    }
  }, [workspace?.name]);

  const handleSave = async () => {
    if (!workspaceId || workspaceName === workspace?.name) return;

    setIsSaving(true);
    try {
      // API call would go here
      await new Promise((resolve) => setTimeout(resolve, 500));
      await refresh();
      notify.success("Workspace updated");
    } catch (e: any) {
      notify.error(e?.message || "Failed to save");
    } finally {
      setIsSaving(false);
    }
  };

  const hasChanges = workspaceName !== workspace?.name && workspaceName.trim() !== "";

  const activeFixtureId = (() => {
    if (!bcm?.foundation?.company) return null;
    const company = bcm.foundation.company;
    if (company === "FlowBoard") return "saas";
    if (company === "EcoThread") return "ecommerce";
    if (company === "GrowthForge") return "agency";
    return null;
  })();

  const handleActivateFixture = async (fixtureId: string) => {
    if (!workspaceId) return;

    try {
      // In a real app, this would load and seed fixture data
      notify.success(`Activated ${FIXTURES.find((f) => f.id === fixtureId)?.name}`);
    } catch (e: any) {
      notify.error(e?.message || "Failed to activate fixture");
    }
  };

  return (
    <Layout mode="draft">
      <div ref={pageRef} className="space-y-8 max-w-3xl">
        {/* Header */}
        <header className="settings-section">
          <div className="flex items-center gap-3 mb-2">
            <span className="rf-mono-xs text-[var(--ink-3)] uppercase">
              Configuration
            </span>
          </div>
          <h1 className="rf-h2">Settings</h1>
          <p className="rf-body text-[var(--ink-2)] mt-2">
            No login, no paywalls. Settings are scoped to your current workspace.
          </p>
        </header>

        {/* Workspace Settings */}
        <section className="settings-section">
          <Card>
            <CardHeader
              title="Workspace"
              subtitle="Workspace ID is the tenant boundary. Sent as x-workspace-id on API calls."
            />

            <div className="space-y-4">
              <Input
                label="Name"
                value={workspaceName}
                onChange={setWorkspaceName}
                placeholder="Workspace name"
              />

              <div>
                <label className="rf-label text-[var(--ink-2)] mb-2 block">
                  ID
                </label>
                <div className="p-3 bg-[var(--bg-canvas)] border border-[var(--border-1)] rounded-[var(--radius-sm)] rf-mono-sm">
                  {workspaceId || "Not initialized"}
                </div>
              </div>

              {workspace?.slug && (
                <div>
                  <label className="rf-label text-[var(--ink-2)] mb-2 block">
                    Slug
                  </label>
                  <div className="p-3 bg-[var(--bg-canvas)] border border-[var(--border-1)] rounded-[var(--radius-sm)] rf-mono-sm">
                    {workspace.slug}
                  </div>
                </div>
              )}
            </div>

            <CardFooter>
              <Button
                variant="primary"
                onClick={handleSave}
                loading={isSaving}
                disabled={!hasChanges}
                leftIcon={<Save size={16} />}
              >
                Save Changes
              </Button>
              {!hasChanges && (
                <span className="rf-body-sm text-[var(--ink-3)]">No changes</span>
              )}
            </CardFooter>
          </Card>
        </section>

        {/* BCM Fixture Switcher (Dev Mode) */}
        <section className="settings-section">
          <Card className="border-2 border-amber-500/20">
            <CardHeader
              title={
                <span className="flex items-center gap-2">
                  Business Context
                  <Badge variant="warning" size="sm">
                    Dev Mode
                  </Badge>
                </span>
              }
              subtitle="Test the BCM pipeline by activating different business personalities. This transforms the entire app — Muse context, ICPs, company name, etc."
            />

            {/* Current Status */}
            {bcm?.foundation?.company && (
              <div className="mb-6 p-3 bg-[var(--bg-canvas)] rounded-[var(--radius-sm)] border border-[var(--border-1)]">
                <div className="flex items-center gap-2">
                  <Sparkles size={16} className="text-[var(--status-warning)]" />
                  <span className="rf-body-sm text-[var(--ink-2)]">
                    Currently active:
                  </span>
                  <span className="rf-body-sm font-medium">
                    {bcm.foundation.company}
                  </span>
                  <span className="rf-mono-xs text-[var(--ink-3)]">
                    v{bcm.version} · {bcm.meta?.icps_count} ICPs
                  </span>
                </div>
              </div>
            )}

            {/* Fixture Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {FIXTURES.map((fixture) => {
                const isActive = activeFixtureId === fixture.id;
                const Icon = fixture.icon;

                return (
                  <div
                    key={fixture.id}
                    className={`p-4 rounded-[var(--radius-md)] border-2 transition-all ${
                      isActive
                        ? "border-[var(--ink-1)] bg-[var(--state-selected)]"
                        : "border-[var(--border-1)] hover:border-[var(--border-2)]"
                    }`}
                  >
                    {isActive && (
                      <div className="absolute top-3 right-3">
                        <Check size={16} className="text-[var(--ink-1)]" />
                      </div>
                    )}

                    <div
                      className="w-10 h-10 rounded-full flex items-center justify-center mb-3"
                      style={{ backgroundColor: `${fixture.color}20` }}
                    >
                      <Icon size={20} style={{ color: fixture.color }} />
                    </div>

                    <h3 className="rf-h4 mb-1">{fixture.name}</h3>
                    <div className="flex flex-wrap gap-2 mb-3">
                      <span className="rf-tag">{fixture.industry}</span>
                      <span className="rf-tag">{fixture.stage}</span>
                    </div>
                    <p className="rf-body-sm text-[var(--ink-2)] italic line-clamp-3">
                      &ldquo;{fixture.oneLiner}&rdquo;
                    </p>

                    <Button
                      variant={isActive ? "tertiary" : "secondary"}
                      className="w-full mt-4"
                      onClick={() => handleActivateFixture(fixture.id)}
                      disabled={isSeeding || isActive}
                    >
                      {isActive ? "Active" : isSeeding ? "Activating..." : "Activate"}
                    </Button>
                  </div>
                );
              })}
            </div>

            <p className="rf-body-sm text-[var(--ink-3)] mt-4">
              Tip: After activating, check the Dashboard BCM panel, try Muse with
              &ldquo;What&apos;s my value prop?&rdquo;, or view Moves to see ICP badges
              update instantly.
            </p>
          </Card>
        </section>

        {/* Assets */}
        <section className="settings-section">
          <Card>
            <CardHeader
              title="Assets"
              subtitle="Upload images and files for this workspace. Files are stored under the workspace path in Supabase Storage."
            />

            <div className="flex items-center gap-3 mb-4">
              <label className="rf-btn rf-btn-primary cursor-pointer">
                <Upload size={16} />
                <span>Upload File</span>
                <input type="file" className="hidden" />
              </label>
              {isLoadingAssets ? (
                <span className="rf-body-sm text-[var(--ink-3)]">
                  Loading assets...
                </span>
              ) : (
                <span className="rf-body-sm text-[var(--ink-3)]">
                  {assets.length} file(s)
                </span>
              )}
            </div>

            {assets.length === 0 ? (
              <div className="p-8 border border-dashed border-[var(--border-2)] rounded-[var(--radius-md)] text-center">
                <p className="rf-body text-[var(--ink-3)]">
                  No assets uploaded yet.
                </p>
                <p className="rf-body-sm text-[var(--ink-3)] mt-1">
                  Upload images and documents to use in your moves and campaigns.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-3">
                {assets.map((asset) => (
                  <div
                    key={asset.id}
                    className="p-3 bg-[var(--bg-canvas)] border border-[var(--border-1)] rounded-[var(--radius-sm)]"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0">
                        <p className="rf-body-sm font-medium truncate">
                          {asset.original_name}
                        </p>
                        <p className="rf-mono-xs text-[var(--ink-3)]">
                          {(asset.size_bytes / 1024).toFixed(1)} KB ·{" "}
                          {asset.asset_type}
                        </p>
                      </div>
                      <button className="p-1.5 rounded-[var(--radius-sm)] hover:bg-[var(--status-error-bg)] text-[var(--ink-3)] hover:text-[var(--status-error)] transition-colors">
                        <Trash2 size={14} />
                      </button>
                    </div>
                    {asset.public_url && asset.asset_type === "image" && (
                      <img
                        src={asset.public_url}
                        alt={asset.original_name}
                        className="w-full h-24 object-cover rounded-[var(--radius-sm)] mt-2"
                      />
                    )}
                  </div>
                ))}
              </div>
            )}
          </Card>
        </section>

        {/* Danger Zone */}
        <section className="settings-section">
          <Card className="border-[var(--status-error)]/30">
            <CardHeader
              title={
                <span className="flex items-center gap-2 text-[var(--status-error)]">
                  <AlertTriangle size={18} />
                  Danger Zone
                </span>
              }
              subtitle="Irreversible actions. Proceed with caution."
            />

            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-[var(--status-error-bg)]/50 rounded-[var(--radius-md)]">
                <div>
                  <p className="rf-body font-medium text-[var(--status-error)]">
                    Reset Workspace
                  </p>
                  <p className="rf-body-sm text-[var(--ink-2)]">
                    Clear all data and start fresh. This cannot be undone.
                  </p>
                </div>
                <Button
                  variant="secondary"
                  className="border-[var(--status-error)] text-[var(--status-error)] hover:bg-[var(--status-error-bg)]"
                  onClick={() => setIsDeleteModalOpen(true)}
                >
                  Reset
                </Button>
              </div>
            </div>
          </Card>
        </section>
      </div>

      {/* Confirm Reset Modal */}
      <ConfirmDialog
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        onConfirm={() => {
          // Handle reset
          notify.success("Workspace reset");
        }}
        title="Reset Workspace?"
        description="This will permanently delete all data in this workspace including moves, campaigns, and foundation settings. This action cannot be undone."
        confirmText="Reset Workspace"
        cancelText="Cancel"
        variant="danger"
      />
    </Layout>
  );
}
