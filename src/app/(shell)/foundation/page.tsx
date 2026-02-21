"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { Layout } from "@/components/raptor/shell/Layout";
import { Card, CardHeader, CardFooter } from "@/components/raptor/ui/Card";
import { Button } from "@/components/raptor/ui/Button";
import { Badge } from "@/components/raptor/ui/Badge";
import { Input } from "@/components/raptor/ui/Input";
import { Tag } from "@/components/raptor/ui/Tag";
import { Progress } from "@/components/raptor/ui/Progress";
import { Tabs } from "@/components/raptor/ui/Tabs";
import { Modal } from "@/components/raptor/ui/Modal";
import {
  Building2,
  Users,
  MessageSquare,
  Lock,
  Unlock,
  Sparkles,
  Edit3,
  Plus,
  Trash2,
  Check,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { useWorkspace } from "@/components/workspace/WorkspaceProvider";
import {
  foundationService,
  EMPTY_FOUNDATION,
  type FoundationData,
} from "@/services/foundation.service";
import type { RICP, CoreMessaging } from "@/types/foundation";



// Helper function to calculate field completion
function calculatePositioningProgress(positioning: FoundationData["positioning"]): number {
  const fields = [
    positioning.companyName,
    positioning.tagline,
    positioning.valueProp,
    positioning.problem,
    positioning.solution,
  ];
  const completed = fields.filter((f) => f.trim().length > 0).length;
  return completed;
}

function calculateMessagingProgress(messaging: FoundationData["messaging"]): number {
  if (!messaging) return 0;
  const fields = [
    messaging.oneLiner,
    messaging.positioningStatement?.situation || "",
    ...(messaging.valueProps?.map(v => v.title) || []),
  ];
  const completed = fields.filter((f) => f && f.trim().length > 0).length;
  return Math.min(completed, 6);
}

// Editable Field Component
interface EditableFieldProps {
  label: string;
  value: string;
  type?: "text" | "textarea";
  placeholder?: string;
  isLocked: boolean;
  onChange: (value: string) => void;
  onGenerate?: () => void;
}

function EditableField({
  label,
  value,
  type = "text",
  placeholder,
  isLocked,
  onChange,
  onGenerate,
}: EditableFieldProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [localValue, setLocalValue] = useState(value);
  const [showCheck, setShowCheck] = useState(false);
  const inputRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  const handleSave = () => {
    onChange(localValue);
    setIsEditing(false);
    setShowCheck(true);
    setTimeout(() => setShowCheck(false), 1500);

    // Animate checkmark
    if (inputRef.current) {
      gsap.fromTo(
        ".check-icon",
        { scale: 0, opacity: 0 },
        { scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2)" }
      );
    }
  };

  const handleCancel = () => {
    setLocalValue(value);
    setIsEditing(false);
  };

  return (
    <div ref={inputRef} className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-[14px] font-medium text-[var(--ink-1)]">{label}</label>
        {!isLocked && (
          <div className="flex items-center gap-2">
            {!isEditing ? (
              <>
                {onGenerate && (
                  <Button
                    variant="tertiary"
                    size="sm"
                    leftIcon={<Sparkles size={14} />}
                    onClick={onGenerate}
                  >
                    Generate
                  </Button>
                )}
                <Button
                  variant="ghost"
                  onClick={() => setIsEditing(true)}
                  className="w-[32px] h-[32px]"
                >
                  <Edit3 size={16} />
                </Button>
              </>
            ) : (
              <div className="flex items-center gap-1">
                <Button variant="ghost" onClick={handleSave} className="w-[32px] h-[32px]">
                  <Check size={16} className="text-[var(--status-success)]" />
                </Button>
                <Button variant="ghost" onClick={handleCancel} className="w-[32px] h-[32px]">
                  <span className="text-[14px] text-[var(--ink-3)]">×</span>
                </Button>
              </div>
            )}
          </div>
        )}
      </div>

      {isEditing ? (
        <div className="animate-in fade-in slide-in-from-top-1 duration-200">
          <Input
            type={type}
            value={localValue}
            onChange={setLocalValue}
            placeholder={placeholder}
          />
        </div>
      ) : (
        <div className="group relative">
          <div
            className={`
              min-h-[44px] px-3 py-2.5 rounded-[10px] border transition-colors
              ${value.trim() ? "border-[var(--border-1)] bg-[var(--bg-surface)]" : "border-dashed border-[var(--border-2)] bg-[var(--bg-canvas)]"}
              ${isLocked ? "" : "group-hover:border-[var(--border-2)] cursor-pointer"}
            `}
            onClick={() => !isLocked && setIsEditing(true)}
          >
            <p className={`text-[14px] ${value.trim() ? "text-[var(--ink-1)]" : "text-[var(--ink-3)]"}`}>
              {value.trim() || placeholder || `Add ${label.toLowerCase()}...`}
            </p>
          </div>
          {showCheck && (
            <span className="check-icon absolute right-3 top-1/2 -translate-y-1/2 text-[var(--status-success)]">
              <Check size={16} />
            </span>
          )}
        </div>
      )}
    </div>
  );
}

// Positioning Card Component
interface PositioningCardProps {
  data: FoundationData["positioning"];
  onUpdate: (data: FoundationData["positioning"]) => void;
}

function PositioningCard({ data, onUpdate }: PositioningCardProps) {
  const [showLockModal, setShowLockModal] = useState(false);
  const lockIconRef = useRef<HTMLDivElement>(null);

  const isLocked = data.status === "locked";
  const completedFields = calculatePositioningProgress(data);
  const totalFields = 5;

  const handleLock = () => {
    if (lockIconRef.current) {
      gsap.to(lockIconRef.current, {
        rotation: 90,
        scale: 0.8,
        duration: 0.15,
        ease: "power2.in",
        onComplete: () => {
          gsap.to(lockIconRef.current, {
            rotation: 0,
            scale: 1,
            duration: 0.3,
            ease: "back.out(2)",
          });
        },
      });
    }
    onUpdate({
      ...data,
      status: "locked",
      version: data.version + 1,
      lockedAt: new Date(),
    });
    setShowLockModal(false);
  };

  const handleUnlock = () => {
    onUpdate({
      ...data,
      status: "draft",
    });
  };

  return (
    <Card className="foundation-card" isLocked={isLocked}>
      <CardHeader
        title="Positioning"
        subtitle={`${completedFields} of ${totalFields} fields complete`}
        badge={
          isLocked
            ? { text: "v" + data.version, variant: "success" }
            : { text: "Draft", variant: "warning" }
        }
      />

      <div className="flex items-center gap-2 mb-4">
        <div className="p-2 bg-[var(--bg-canvas)] rounded-[10px]">
          <Building2 size={20} className="text-[var(--ink-1)]" />
        </div>
        <span className="text-[12px] text-[var(--ink-3)] font-medium uppercase tracking-wide">
          Company & Value Proposition
        </span>
      </div>

      <div className="space-y-4">
        <EditableField
          label="Company Name"
          value={data.companyName}
          placeholder="Your company name"
          isLocked={isLocked}
          onChange={(v) => onUpdate({ ...data, companyName: v })}
        />
        <EditableField
          label="Tagline"
          value={data.tagline}
          placeholder="A short, memorable tagline"
          isLocked={isLocked}
          onChange={(v) => onUpdate({ ...data, tagline: v })}
          onGenerate={() => onUpdate({ ...data, tagline: "AI-powered automation for every team" })}
        />
        <EditableField
          label="Value Proposition"
          type="textarea"
          value={data.valueProp}
          placeholder="What value do you provide to customers?"
          isLocked={isLocked}
          onChange={(v) => onUpdate({ ...data, valueProp: v })}
          onGenerate={() =>
            onUpdate({
              ...data,
              valueProp:
                "We help teams eliminate repetitive work through intelligent automation that learns and adapts to their unique workflows.",
            })
          }
        />
        <EditableField
          label="Problem Statement"
          type="textarea"
          value={data.problem}
          placeholder="What problem are you solving?"
          isLocked={isLocked}
          onChange={(v) => onUpdate({ ...data, problem: v })}
        />
        <EditableField
          label="Solution Statement"
          type="textarea"
          value={data.solution}
          placeholder="How do you solve this problem?"
          isLocked={isLocked}
          onChange={(v) => onUpdate({ ...data, solution: v })}
        />
      </div>

      <CardFooter align="right">
        {isLocked ? (
          <Button
            variant="secondary"
            leftIcon={<Unlock size={16} />}
            onClick={handleUnlock}
          >
            Unlock to Edit
          </Button>
        ) : (
          <Button
            variant="primary"
            leftIcon={
              <div ref={lockIconRef}>
                <Lock size={16} />
              </div>
            }
            onClick={() => setShowLockModal(true)}
            disabled={completedFields < totalFields}
          >
            Lock Positioning
          </Button>
        )}
      </CardFooter>

      <Modal
        isOpen={showLockModal}
        onClose={() => setShowLockModal(false)}
        title="Lock Positioning?"
        subtitle="Locking makes this read-only. To change later, you'll create a new draft."
        footer={
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setShowLockModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" leftIcon={<Lock size={16} />} onClick={handleLock}>
              Lock Positioning
            </Button>
          </div>
        }
      >
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-[var(--bg-surface)] rounded-[10px]">
            <Check size={16} className="text-[var(--status-success)]" />
            <span className="text-[14px] text-[var(--ink-1)]">
              {completedFields} fields completed
            </span>
          </div>
          <p className="text-[14px] text-[var(--ink-3)]">
            Once locked, this positioning will be used across all your campaigns
            and content.
          </p>
        </div>
      </Modal>
    </Card>
  );
}

// ICP Card Component
interface RICPCardProps {
  icp: RICP;
  isLocked: boolean;
  onUpdate: (icp: RICP) => void;
  onDelete: () => void;
}

function ICPCardItem({ icp, isLocked, onUpdate, onDelete }: RICPCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!cardRef.current) return;

    const handleMouseEnter = () => {
      gsap.to(cardRef.current, {
        y: -4,
        boxShadow: "0 8px 24px rgba(42, 37, 41, 0.08)",
        duration: 0.2,
        ease: "power2.out",
      });
    };

    const handleMouseLeave = () => {
      gsap.to(cardRef.current, {
        y: 0,
        boxShadow: "0 0 0 rgba(42, 37, 41, 0)",
        duration: 0.2,
        ease: "power2.out",
      });
    };

    const card = cardRef.current;
    card.addEventListener("mouseenter", handleMouseEnter);
    card.addEventListener("mouseleave", handleMouseLeave);

    return () => {
      card.removeEventListener("mouseenter", handleMouseEnter);
      card.removeEventListener("mouseleave", handleMouseLeave);
    };
  }, []);

  if (isEditing) {
    return (
      <Card className="p-4 space-y-3">
        <Input
          label="Name"
          value={icp.name}
          onChange={(v) => onUpdate({ ...icp, name: v })}
        />
        <Input
          type="textarea"
          label="Role"
          value={icp.demographics?.role || ""}
          onChange={(v) => onUpdate({ ...icp, demographics: { ...icp.demographics, role: v } })}
        />
        <Input
          label="Income"
          value={icp.demographics?.income || ""}
          onChange={(v) => onUpdate({ ...icp, demographics: { ...icp.demographics, income: v } })}
        />
        <div className="flex justify-end gap-2 pt-2">
          <Button variant="secondary" size="sm" onClick={() => setIsEditing(false)}>
            Done
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <div ref={cardRef} className="bg-[var(--bg-surface)] border border-[var(--border-1)] rounded-[14px] p-4">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h4 className="text-[16px] font-semibold text-[var(--ink-1)]">{icp.name}</h4>
          <p className="text-[13px] text-[var(--ink-3)] mt-0.5">{icp.demographics?.role || ""}</p>
        </div>
        {!isLocked && (
          <div className="flex gap-1">
            <Button variant="ghost" onClick={() => setIsEditing(true)} className="w-[32px] h-[32px]">
              <Edit3 size={14} />
            </Button>
            <Button variant="ghost" onClick={onDelete} className="w-[32px] h-[32px]">
              <Trash2 size={14} className="text-[var(--status-error)]" />
            </Button>
          </div>
        )}
      </div>

      <div className="space-y-3">
        <div>
          <span className="text-[11px] font-semibold uppercase tracking-wide text-[var(--ink-3)]">
            Income/Role
          </span>
          <p className="text-[13px] text-[var(--ink-1)] mt-1">{icp.demographics?.income || ""}</p>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <span className="text-[11px] font-semibold uppercase tracking-wide text-[var(--ink-3)]">
              Pain Points
            </span>
            <div className="flex flex-wrap gap-1 mt-1.5">
              {icp.painPoints.map((point, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 text-[11px] bg-[#F5E6E6] text-[var(--status-error)] rounded-[6px]"
                >
                  {point}
                </span>
              ))}
            </div>
          </div>
          <div>
            <span className="text-[11px] font-semibold uppercase tracking-wide text-[var(--ink-3)]">
              Goals
            </span>
            <div className="flex flex-wrap gap-1 mt-1.5">
              {icp.goals.map((goal, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 text-[11px] bg-[#E8F0E9] text-[var(--status-success)] rounded-[6px]"
                >
                  {goal}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ICPs Section Component
interface ICPSectionProps {
  icps: RICP[];
  isLocked: boolean;
  onUpdate: (icps: RICP[]) => void;
}

function ICPSection({ icps, isLocked, onUpdate }: ICPSectionProps) {
  const handleAddICP = () => {
    const newICP: RICP = {
      id: `icp-${Date.now()}`,
      name: "New ICP",
      demographics: { ageRange: "", income: "", location: "", role: "Describe their role", stage: "" },
      psychographics: { beliefs: "", identity: "", becoming: "", fears: "", values: [], hangouts: [], contentConsumed: [], whoTheyFollow: [], language: [], timing: [], triggers: [] },
      marketSophistication: 1,
      painPoints: ["Pain point 1"],
      goals: ["Goal 1"],
      objections: [],
    };
    onUpdate([...icps, newICP]);
  };

  const handleUpdateICP = (updated: RICP) => {
    onUpdate(icps.map((icp) => (icp.id === updated.id ? updated : icp)));
  };

  const handleDeleteICP = (id: string) => {
    onUpdate(icps.filter((icp) => icp.id !== id));
  };

  return (
    <Card className="foundation-card">
      <CardHeader
        title="Ideal Customer Profiles"
        subtitle={`${icps.length} profile${icps.length !== 1 ? "s" : ""} defined`}
      />

      <div className="flex items-center gap-2 mb-4">
        <div className="p-2 bg-[var(--bg-canvas)] rounded-[10px]">
          <Users size={20} className="text-[var(--ink-1)]" />
        </div>
        <span className="text-[12px] text-[var(--ink-3)] font-medium uppercase tracking-wide">
          Target Audiences
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {icps.map((icp) => (
          <ICPCardItem
            key={icp.id}
            icp={icp}
            isLocked={isLocked}
            onUpdate={handleUpdateICP}
            onDelete={() => handleDeleteICP(icp.id)}
          />
        ))}

        {!isLocked && (
          <button
            onClick={handleAddICP}
            className="group flex flex-col items-center justify-center gap-3 p-6 border-2 border-dashed border-[var(--border-2)] rounded-[14px] hover:border-[var(--rf-charcoal)] hover:bg-[var(--state-hover)] transition-colors min-h-[200px]"
          >
            <div className="w-12 h-12 rounded-full bg-[var(--bg-canvas)] group-hover:bg-[var(--bg-surface)] flex items-center justify-center transition-colors">
              <Plus size={24} className="text-[var(--ink-3)] group-hover:text-[var(--ink-1)]" />
            </div>
            <span className="text-[14px] font-medium text-[var(--ink-3)] group-hover:text-[var(--ink-1)]">
              Add ICP
            </span>
          </button>
        )}
      </div>
    </Card>
  );
}

// Messaging Card Component
interface MessagingCardProps {
  data: FoundationData["messaging"];
  onUpdate: (data: FoundationData["messaging"]) => void;
}

function MessagingCard({ data, onUpdate }: MessagingCardProps) {
  const [activeTab, setActiveTab] = useState("core");
  const [showLockModal, setShowLockModal] = useState(false);
  const lockIconRef = useRef<HTMLDivElement>(null);


  if (!data) return <Card className="foundation-card"><CardHeader title="Messaging" subtitle="Start by setting up core messaging" /><div className="p-4"><Button onClick={() => onUpdate({ oneLiner: "", positioningStatement: {} as any, valueProps: [], brandVoice: {} as any, storyBrand: {} as any, confidence: 0 })}>Initialize Messaging</Button></div></Card>;
  const isLocked = (data?.confidence === 100);
  const completedItems = calculateMessagingProgress(data);
  const totalItems = 6;

  const tabs = [
    { id: "core", label: "Core", badge: completedItems },
    { id: "proof", label: "Proof Points", badge: (data?.storyBrand?.plan?.length || 0) },
  ];

  const handleLock = () => {
    if (lockIconRef.current) {
      gsap.to(lockIconRef.current, {
        rotation: 90,
        scale: 0.8,
        duration: 0.15,
        ease: "power2.in",
        onComplete: () => {
          gsap.to(lockIconRef.current, {
            rotation: 0,
            scale: 1,
            duration: 0.3,
            ease: "back.out(2)",
          });
        },
      });
    }
    onUpdate({
      ...data,
      confidence: 100,
    });
    setShowLockModal(false);
  };

  const handleUnlock = () => {
    onUpdate({
      ...data,
      confidence: 0,
    });
  };

  return (
    <Card className="foundation-card" isLocked={isLocked}>
      <CardHeader
        title="Messaging"
        subtitle={`${completedItems} of ${totalItems} items complete`}
        badge={
          isLocked
            ? { text: "v" + (data?.confidence || 1), variant: "success" }
            : { text: "Draft", variant: "warning" }
        }
      />

      <div className="flex items-center gap-2 mb-4">
        <div className="p-2 bg-[var(--bg-canvas)] rounded-[10px]">
          <MessageSquare size={20} className="text-[var(--ink-1)]" />
        </div>
        <span className="text-[12px] text-[var(--ink-3)] font-medium uppercase tracking-wide">
          Core Messaging & Proof
        </span>
      </div>

      <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />

      <div className="pt-4">
        {activeTab === "core" && (
          <div className="space-y-4">
            <EditableField
              label="One-liner"
              value={(data?.oneLiner || "")}
              placeholder="The one-sentence pitch"
              isLocked={isLocked}
              onChange={(v) => onUpdate({ ...data, oneLiner: v })}
              onGenerate={() => onUpdate({ ...data, oneLiner: "AI workflow automation that actually works" })}
            />
            <EditableField
              label="Elevator Pitch"
              type="textarea"
              value={(data?.positioningStatement?.situation || "")}
              placeholder="Short paragraph explaining what you do"
              isLocked={isLocked}
              onChange={(v) => onUpdate({ ...data, positioningStatement: { ...data?.positioningStatement, situation: v } as any })}
            />
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-[14px] font-medium text-[var(--ink-1)]">Key Messages</label>
                {!isLocked && (
                  <Button
                    variant="tertiary"
                    size="sm"
                    leftIcon={<Plus size={14} />}
                    onClick={() =>
                      onUpdate({
                        ...data,
                        valueProps: [...(data?.valueProps || []), { title: "New value prop", description: "" }],
                      })
                    }
                  >
                    Add
                  </Button>
                )}
              </div>
              <div className="space-y-2">
                {(data?.valueProps || []).map((msg, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] text-[11px] font-semibold flex items-center justify-center flex-shrink-0">
                      {i + 1}
                    </span>
                    {isLocked ? (
                      <span className="text-[14px] text-[var(--ink-1)]">{msg.title || ""}</span>
                    ) : (
                      <Input
                        value={msg.title || ""}
                        onChange={(v) => {
                          const newMessages = [...(data?.valueProps || [])];
                          newMessages[i] = { ...newMessages[i], title: v, description: newMessages[i]?.description || "" };
                          onUpdate({ ...data, valueProps: newMessages } as any);
                        }}
                      />
                    )}
                    {!isLocked && (
                      <Button
                        variant="ghost"
                        onClick={() => {
                          const newMessages = (data?.valueProps || []).filter((_, idx) => idx !== i);
                          onUpdate({ ...data, valueProps: newMessages });
                        }}
                        className="w-[32px] h-[32px] flex-shrink-0"
                      >
                        <Trash2 size={14} className="text-[var(--status-error)]" />
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === "proof" && (
          <div className="space-y-3">
            {(data?.storyBrand?.plan || []).map((point, i) => (
              <div
                key={i}
                className="flex items-center justify-between p-3 bg-[var(--bg-surface)] rounded-[10px] border border-[var(--border-1)]"
              >
                <div className="flex items-center gap-3">
                  <span
                    className={`w-2 h-2 rounded-full ${point.trim().length > 0 ? "bg-[var(--status-success)]" : "bg-[var(--status-warning)]"
                      }`}
                  />
                  <div>
                    <p className="text-[14px] font-medium text-[var(--ink-1)]">{point}</p>
                    <p className="text-[12px] text-[var(--ink-3)] capitalize">
                      {"Plan Step"} • {"Active"}
                    </p>
                  </div>
                </div>
                <Tag active={point.trim().length > 0}>
                  {point.trim().length > 0 ? "Validated" : "Pending"}
                </Tag>
              </div>
            ))}
            {!isLocked && (
              <Button
                variant="tertiary"
                leftIcon={<Plus size={16} />}
                onClick={() =>
                  onUpdate({
                    ...data,
                    storyBrand: {
                      ...data?.storyBrand, plan: [
                        ...(data?.storyBrand?.plan || []),
                        "New Plan Step",
                      ]
                    } as any,
                  })
                }
              >
                Add Proof Point
              </Button>
            )}
          </div>
        )}
      </div>

      <CardFooter align="right">
        {isLocked ? (
          <Button
            variant="secondary"
            leftIcon={<Unlock size={16} />}
            onClick={handleUnlock}
          >
            Unlock to Edit
          </Button>
        ) : (
          <Button
            variant="primary"
            leftIcon={
              <div ref={lockIconRef}>
                <Lock size={16} />
              </div>
            }
            onClick={() => setShowLockModal(true)}
            disabled={completedItems < 3}
          >
            Lock Messaging
          </Button>
        )}
      </CardFooter>

      <Modal
        isOpen={showLockModal}
        onClose={() => setShowLockModal(false)}
        title="Lock Messaging?"
        subtitle="Locking makes this read-only. To change later, you'll create a new draft."
        footer={
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setShowLockModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" leftIcon={<Lock size={16} />} onClick={handleLock}>
              Lock Messaging
            </Button>
          </div>
        }
      >
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-[var(--bg-surface)] rounded-[10px]">
            <Check size={16} className="text-[var(--status-success)]" />
            <span className="text-[14px] text-[var(--ink-1)]">{completedItems} items completed</span>
          </div>
          <p className="text-[14px] text-[var(--ink-3)]">
            Once locked, this messaging will be used across all your campaigns
            and content.
          </p>
        </div>
      </Modal>
    </Card>
  );
}

// Main Page Component
export default function FoundationPage() {
  const { workspaceId } = useWorkspace();
  const [foundation, setFoundation] = useState<FoundationData>(EMPTY_FOUNDATION);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const cardsRef = useRef<HTMLDivElement>(null);
  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Fetch foundation data from the backend
  useEffect(() => {
    if (!workspaceId) return;
    let cancelled = false;
    setLoading(true);
    setError(null);

    foundationService
      .get(workspaceId)
      .then((data) => {
        if (!cancelled) setFoundation(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err?.message ?? "Failed to load foundation");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => { cancelled = true; };
  }, [workspaceId]);

  // Debounced auto-save whenever foundation state changes (skip initial load)
  const isFirstRender = useRef(true);
  const handleUpdate = useCallback(
    (next: FoundationData) => {
      setFoundation(next);

      if (!workspaceId) return;
      if (saveTimerRef.current) clearTimeout(saveTimerRef.current);

      saveTimerRef.current = setTimeout(() => {
        setSaving(true);
        foundationService
          .save(workspaceId, next)
          .catch(() => { /* silently retry on next change */ })
          .finally(() => setSaving(false));
      }, 800);
    },
    [workspaceId]
  );

  // Calculate overall progress
  const positioningProgress = calculatePositioningProgress(foundation.positioning);
  const messagingProgress = calculateMessagingProgress(foundation.messaging);
  const totalProgress = Math.round(
    ((positioningProgress + (foundation.ricps?.length || 0) + messagingProgress) / 13) * 100
  );

  const completedSections = [
    positioningProgress === 5,
    (foundation.ricps?.length || 0) > 0,
    messagingProgress >= 4,
  ].filter(Boolean).length;
  const totalSections = 3;

  // GSAP Page Entrance Animation
  useEffect(() => {
    if (loading) return;
    const ctx = gsap.context(() => {
      const tl = gsap.timeline();

      tl.fromTo(
        ".page-header",
        { y: -20, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.5 }
      )
        .fromTo(
          ".progress-card",
          { y: 20, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.4 },
          "-=0.3"
        )
        .fromTo(
          ".foundation-card",
          { y: 30, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.5, stagger: 0.15 },
          "-=0.2"
        );
    });

    return () => ctx.revert();
  }, [loading]);

  // ── Loading State ──
  if (loading) {
    return (
      <Layout mode="draft" showDrawer>
        <div className="max-w-4xl mx-auto p-6 flex flex-col items-center justify-center min-h-[60vh] gap-4">
          <Loader2 size={32} className="animate-spin text-[var(--ink-3)]" />
          <p className="text-[14px] text-[var(--ink-3)]">Loading foundation…</p>
        </div>
      </Layout>
    );
  }

  // ── Error State ──
  if (error) {
    return (
      <Layout mode="draft" showDrawer>
        <div className="max-w-4xl mx-auto p-6 flex flex-col items-center justify-center min-h-[60vh] gap-4">
          <AlertCircle size={32} className="text-[var(--status-error)]" />
          <p className="text-[14px] text-[var(--status-error)]">{error}</p>
          <Button variant="secondary" onClick={() => window.location.reload()}>Retry</Button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout mode="draft" showDrawer>
      <div className="max-w-4xl mx-auto p-6 space-y-8">
        {/* Header with overall progress */}
        <header className="page-header">
          <div className="flex items-start justify-between">
            <div>
              <h1
                className="text-[32px] font-bold text-[var(--ink-1)]"
                style={{ fontFamily: "'DM Sans', system-ui, sans-serif", lineHeight: "40px" }}
              >
                Foundation
              </h1>
              <p
                className="text-[16px] text-[var(--ink-2)] mt-2"
                style={{ fontFamily: "'DM_Sans', system-ui, sans-serif", lineHeight: "26px" }}
              >
                Define your core positioning, ideal customers, and messaging.
              </p>
            </div>
            <div className="flex items-center gap-2">
              {saving && (
                <span className="text-[12px] text-[var(--ink-3)] flex items-center gap-1">
                  <Loader2 size={12} className="animate-spin" /> Saving…
                </span>
              )}
              <Badge variant={foundation.status === "locked" ? "success" : "warning"}>
                {foundation.status === "locked" ? "Locked" : "Draft"}
              </Badge>
            </div>
          </div>
        </header>

        {/* Progress Card */}
        <Card className="progress-card" padding="lg">
          <div className="flex items-center justify-between">
            <div>
              <h3
                className="text-[20px] font-semibold text-[var(--ink-1)]"
                style={{ fontFamily: "'DM Sans', system-ui, sans-serif", lineHeight: "28px" }}
              >
                Foundation Progress
              </h3>
              <p
                className="text-[14px] text-[var(--ink-2)] mt-1"
                style={{ fontFamily: "'DM Sans', system-ui, sans-serif" }}
              >
                {completedSections} of {totalSections} sections complete
              </p>
            </div>
            <div className="text-right">
              <span
                className="text-[32px] font-bold text-[var(--ink-1)]"
                style={{ fontFamily: "'DM Sans', system-ui, sans-serif", lineHeight: "40px" }}
              >
                {totalProgress}%
              </span>
            </div>
          </div>
          <Progress value={totalProgress} className="mt-4" />
          <div className="flex items-center gap-4 mt-3">
            <span className="text-[12px] text-[var(--ink-3)]">
              Positioning: {positioningProgress}/5
            </span>
            <span className="text-[12px] text-[var(--ink-3)]">ICPs: {(foundation.ricps?.length || 0)}</span>
            <span className="text-[12px] text-[var(--ink-3)]">Messaging: {messagingProgress}/6</span>
          </div>
        </Card>

        {/* Three Foundation Cards */}
        <div ref={cardsRef} className="space-y-6">
          <PositioningCard
            data={foundation.positioning}
            onUpdate={(positioning) => handleUpdate({ ...foundation, positioning })}
          />
          <ICPSection
            icps={foundation.ricps || []}
            isLocked={foundation.positioning.status === "locked"}
            onUpdate={(ricps) => handleUpdate({ ...foundation, ricps })}
          />
          <MessagingCard
            data={foundation.messaging}
            onUpdate={(messaging) => handleUpdate({ ...foundation, messaging })}
          />
        </div>
      </div>
    </Layout>
  );
}
