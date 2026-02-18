"use client";

import { useEffect, useRef, useState } from "react";
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
} from "lucide-react";

// Types

type LockStatus = "draft" | "locked";

interface LockableSection {
  status: LockStatus;
  lockedAt?: Date;
  lockedBy?: string;
  version: number;
}

interface ICP {
  id: string;
  name: string;
  description: string;
  firmographics: string;
  painPoints: string[];
  goals: string[];
}

interface ProofPoint {
  claim: string;
  evidence: string;
  status: "validated" | "pending";
}

interface FoundationData {
  status: LockStatus;
  progress: number;
  positioning: LockableSection & {
    companyName: string;
    tagline: string;
    valueProp: string;
    problem: string;
    solution: string;
  };
  icps: ICP[];
  messaging: LockableSection & {
    oneLiner: string;
    elevatorPitch: string;
    keyMessages: string[];
    proofPoints: ProofPoint[];
  };
}

// Mock Data
const mockFoundation: FoundationData = {
  status: "draft",
  progress: 65,
  positioning: {
    status: "draft",
    version: 1,
    companyName: "Acme AI",
    tagline: "Automation for modern teams",
    valueProp: "We help enterprise teams automate repetitive workflows using intelligent AI agents that integrate seamlessly with their existing tools.",
    problem: "Teams waste 40% of their time on manual processes, data entry, and repetitive tasks that could be automated.",
    solution: "AI-powered workflow automation that learns your processes and handles them autonomously, saving hours every week.",
  },
  icps: [
    {
      id: "icp-1",
      name: "Enterprise Operations",
      description: "Large teams struggling with process inefficiency",
      firmographics: "500+ employees, Tech/Finance",
      painPoints: ["Manual data entry", "Approval bottlenecks", "Tool sprawl"],
      goals: ["Reduce processing time", "Improve accuracy", "Scale operations"],
    },
    {
      id: "icp-2",
      name: "Growing Startups",
      description: "Scaling teams needing automation",
      firmographics: "50-200 employees, SaaS",
      painPoints: ["Tool sprawl", "Inconsistent processes", "Limited engineering resources"],
      goals: ["Scale operations", "Maintain quality", "Move fast"],
    },
  ],
  messaging: {
    status: "draft",
    version: 1,
    oneLiner: "AI workflow automation that actually works",
    elevatorPitch: "Acme AI replaces repetitive tasks with intelligent automation. Our agents learn your workflows and handle them autonomously—no coding required. Teams save 10+ hours per week.",
    keyMessages: [
      "Save 10+ hours per week",
      "Zero-code automation",
      "Enterprise security",
      "Seamless integrations",
    ],
    proofPoints: [
      { claim: "10x ROI in 90 days", evidence: "case-study", status: "validated" },
      { claim: "SOC 2 Type II certified", evidence: "certification", status: "validated" },
      { claim: "99.9% uptime SLA", evidence: "metric", status: "pending" },
    ],
  },
};

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
  const fields = [
    messaging.oneLiner,
    messaging.elevatorPitch,
    ...messaging.keyMessages,
  ];
  const completed = fields.filter((f) => f.trim().length > 0).length;
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
        <label className="text-[14px] font-medium text-[#2A2529]">{label}</label>
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
                  <Check size={16} className="text-[#3D5A42]" />
                </Button>
                <Button variant="ghost" onClick={handleCancel} className="w-[32px] h-[32px]">
                  <span className="text-[14px] text-[#847C82]">×</span>
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
              ${value.trim() ? "border-[#E3DED3] bg-[#F7F5EF]" : "border-dashed border-[#D2CCC0] bg-[#EFEDE6]"}
              ${isLocked ? "" : "group-hover:border-[#D2CCC0] cursor-pointer"}
            `}
            onClick={() => !isLocked && setIsEditing(true)}
          >
            <p className={`text-[14px] ${value.trim() ? "text-[#2A2529]" : "text-[#847C82]"}`}>
              {value.trim() || placeholder || `Add ${label.toLowerCase()}...`}
            </p>
          </div>
          {showCheck && (
            <span className="check-icon absolute right-3 top-1/2 -translate-y-1/2 text-[#3D5A42]">
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
        <div className="p-2 bg-[#EFEDE6] rounded-[10px]">
          <Building2 size={20} className="text-[#2A2529]" />
        </div>
        <span className="text-[12px] text-[#847C82] font-medium uppercase tracking-wide">
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
          <div className="flex items-center gap-3 p-3 bg-[#F7F5EF] rounded-[10px]">
            <Check size={16} className="text-[#3D5A42]" />
            <span className="text-[14px] text-[#2A2529]">
              {completedFields} fields completed
            </span>
          </div>
          <p className="text-[14px] text-[#847C82]">
            Once locked, this positioning will be used across all your campaigns
            and content.
          </p>
        </div>
      </Modal>
    </Card>
  );
}

// ICP Card Component
interface ICPCardProps {
  icp: ICP;
  isLocked: boolean;
  onUpdate: (icp: ICP) => void;
  onDelete: () => void;
}

function ICPCardItem({ icp, isLocked, onUpdate, onDelete }: ICPCardProps) {
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
          label="Description"
          value={icp.description}
          onChange={(v) => onUpdate({ ...icp, description: v })}
        />
        <Input
          label="Firmographics"
          value={icp.firmographics}
          onChange={(v) => onUpdate({ ...icp, firmographics: v })}
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
    <div ref={cardRef} className="bg-[#F7F5EF] border border-[#E3DED3] rounded-[14px] p-4">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h4 className="text-[16px] font-semibold text-[#2A2529]">{icp.name}</h4>
          <p className="text-[13px] text-[#847C82] mt-0.5">{icp.description}</p>
        </div>
        {!isLocked && (
          <div className="flex gap-1">
            <Button variant="ghost" onClick={() => setIsEditing(true)} className="w-[32px] h-[32px]">
              <Edit3 size={14} />
            </Button>
            <Button variant="ghost" onClick={onDelete} className="w-[32px] h-[32px]">
              <Trash2 size={14} className="text-[#8B3D3D]" />
            </Button>
          </div>
        )}
      </div>

      <div className="space-y-3">
        <div>
          <span className="text-[11px] font-semibold uppercase tracking-wide text-[#847C82]">
            Firmographics
          </span>
          <p className="text-[13px] text-[#2A2529] mt-1">{icp.firmographics}</p>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <span className="text-[11px] font-semibold uppercase tracking-wide text-[#847C82]">
              Pain Points
            </span>
            <div className="flex flex-wrap gap-1 mt-1.5">
              {icp.painPoints.map((point, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 text-[11px] bg-[#F5E6E6] text-[#8B3D3D] rounded-[6px]"
                >
                  {point}
                </span>
              ))}
            </div>
          </div>
          <div>
            <span className="text-[11px] font-semibold uppercase tracking-wide text-[#847C82]">
              Goals
            </span>
            <div className="flex flex-wrap gap-1 mt-1.5">
              {icp.goals.map((goal, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 text-[11px] bg-[#E8F0E9] text-[#3D5A42] rounded-[6px]"
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
  icps: ICP[];
  isLocked: boolean;
  onUpdate: (icps: ICP[]) => void;
}

function ICPSection({ icps, isLocked, onUpdate }: ICPSectionProps) {
  const handleAddICP = () => {
    const newICP: ICP = {
      id: `icp-${Date.now()}`,
      name: "New ICP",
      description: "Describe this customer profile",
      firmographics: "Company size, industry",
      painPoints: ["Pain point 1"],
      goals: ["Goal 1"],
    };
    onUpdate([...icps, newICP]);
  };

  const handleUpdateICP = (updated: ICP) => {
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
        <div className="p-2 bg-[#EFEDE6] rounded-[10px]">
          <Users size={20} className="text-[#2A2529]" />
        </div>
        <span className="text-[12px] text-[#847C82] font-medium uppercase tracking-wide">
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
            className="group flex flex-col items-center justify-center gap-3 p-6 border-2 border-dashed border-[#D2CCC0] rounded-[14px] hover:border-[#2A2529] hover:bg-[#F3F0E7] transition-colors min-h-[200px]"
          >
            <div className="w-12 h-12 rounded-full bg-[#EFEDE6] group-hover:bg-[#F7F5EF] flex items-center justify-center transition-colors">
              <Plus size={24} className="text-[#847C82] group-hover:text-[#2A2529]" />
            </div>
            <span className="text-[14px] font-medium text-[#847C82] group-hover:text-[#2A2529]">
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

  const isLocked = data.status === "locked";
  const completedItems = calculateMessagingProgress(data);
  const totalItems = 6;

  const tabs = [
    { id: "core", label: "Core", badge: completedItems },
    { id: "proof", label: "Proof Points", badge: data.proofPoints.length },
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
        title="Messaging"
        subtitle={`${completedItems} of ${totalItems} items complete`}
        badge={
          isLocked
            ? { text: "v" + data.version, variant: "success" }
            : { text: "Draft", variant: "warning" }
        }
      />

      <div className="flex items-center gap-2 mb-4">
        <div className="p-2 bg-[#EFEDE6] rounded-[10px]">
          <MessageSquare size={20} className="text-[#2A2529]" />
        </div>
        <span className="text-[12px] text-[#847C82] font-medium uppercase tracking-wide">
          Core Messaging & Proof
        </span>
      </div>

      <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />

      <div className="pt-4">
        {activeTab === "core" && (
          <div className="space-y-4">
            <EditableField
              label="One-liner"
              value={data.oneLiner}
              placeholder="The one-sentence pitch"
              isLocked={isLocked}
              onChange={(v) => onUpdate({ ...data, oneLiner: v })}
              onGenerate={() => onUpdate({ ...data, oneLiner: "AI workflow automation that actually works" })}
            />
            <EditableField
              label="Elevator Pitch"
              type="textarea"
              value={data.elevatorPitch}
              placeholder="Short paragraph explaining what you do"
              isLocked={isLocked}
              onChange={(v) => onUpdate({ ...data, elevatorPitch: v })}
            />
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-[14px] font-medium text-[#2A2529]">Key Messages</label>
                {!isLocked && (
                  <Button
                    variant="tertiary"
                    size="sm"
                    leftIcon={<Plus size={14} />}
                    onClick={() =>
                      onUpdate({
                        ...data,
                        keyMessages: [...data.keyMessages, "New key message"],
                      })
                    }
                  >
                    Add
                  </Button>
                )}
              </div>
              <div className="space-y-2">
                {data.keyMessages.map((msg, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-[#2A2529] text-[#F3F0E7] text-[11px] font-semibold flex items-center justify-center flex-shrink-0">
                      {i + 1}
                    </span>
                    {isLocked ? (
                      <span className="text-[14px] text-[#2A2529]">{msg}</span>
                    ) : (
                      <Input
                        value={msg}
                        onChange={(v) => {
                          const newMessages = [...data.keyMessages];
                          newMessages[i] = v;
                          onUpdate({ ...data, keyMessages: newMessages });
                        }}
                      />
                    )}
                    {!isLocked && (
                      <Button
                        variant="ghost"
                        onClick={() => {
                          const newMessages = data.keyMessages.filter((_, idx) => idx !== i);
                          onUpdate({ ...data, keyMessages: newMessages });
                        }}
                        className="w-[32px] h-[32px] flex-shrink-0"
                      >
                        <Trash2 size={14} className="text-[#8B3D3D]" />
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
            {data.proofPoints.map((point, i) => (
              <div
                key={i}
                className="flex items-center justify-between p-3 bg-[#F7F5EF] rounded-[10px] border border-[#E3DED3]"
              >
                <div className="flex items-center gap-3">
                  <span
                    className={`w-2 h-2 rounded-full ${
                      point.status === "validated" ? "bg-[#3D5A42]" : "bg-[#8B6B3D]"
                    }`}
                  />
                  <div>
                    <p className="text-[14px] font-medium text-[#2A2529]">{point.claim}</p>
                    <p className="text-[12px] text-[#847C82] capitalize">
                      {point.evidence} • {point.status}
                    </p>
                  </div>
                </div>
                <Tag active={point.status === "validated"}>
                  {point.status === "validated" ? "Validated" : "Pending"}
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
                    proofPoints: [
                      ...data.proofPoints,
                      { claim: "New proof point", evidence: "metric", status: "pending" },
                    ],
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
          <div className="flex items-center gap-3 p-3 bg-[#F7F5EF] rounded-[10px]">
            <Check size={16} className="text-[#3D5A42]" />
            <span className="text-[14px] text-[#2A2529]">{completedItems} items completed</span>
          </div>
          <p className="text-[14px] text-[#847C82]">
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
  const [foundation, setFoundation] = useState<FoundationData>(mockFoundation);
  const headerRef = useRef<HTMLElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);
  const cardsRef = useRef<HTMLDivElement>(null);

  // Calculate overall progress
  const positioningProgress = calculatePositioningProgress(foundation.positioning);
  const messagingProgress = calculateMessagingProgress(foundation.messaging);
  const totalProgress = Math.round(
    ((positioningProgress + foundation.icps.length + messagingProgress) / 13) * 100
  );

  const completedSections = [
    positioningProgress === 5,
    foundation.icps.length > 0,
    messagingProgress >= 4,
  ].filter(Boolean).length;
  const totalSections = 3;

  // GSAP Page Entrance Animation
  useEffect(() => {
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
  }, []);

  return (
    <Layout mode="draft" showDrawer>
      <div className="max-w-4xl mx-auto p-6 space-y-8">
        {/* Header with overall progress */}
        <header className="page-header">
          <div className="flex items-start justify-between">
            <div>
              <h1
                className="text-[32px] font-bold text-[#2A2529]"
                style={{ fontFamily: "'DM Sans', system-ui, sans-serif", lineHeight: "40px" }}
              >
                Foundation
              </h1>
              <p
                className="text-[16px] text-[#5C565B] mt-2"
                style={{ fontFamily: "'DM_Sans', system-ui, sans-serif", lineHeight: "26px" }}
              >
                Define your core positioning, ideal customers, and messaging.
              </p>
            </div>
            <Badge variant={foundation.status === "locked" ? "success" : "warning"}>
              {foundation.status === "locked" ? "Locked" : "Draft"}
            </Badge>
          </div>
        </header>

        {/* Progress Card */}
        <Card className="progress-card" padding="lg">
          <div className="flex items-center justify-between">
            <div>
              <h3
                className="text-[20px] font-semibold text-[#2A2529]"
                style={{ fontFamily: "'DM Sans', system-ui, sans-serif", lineHeight: "28px" }}
              >
                Foundation Progress
              </h3>
              <p
                className="text-[14px] text-[#5C565B] mt-1"
                style={{ fontFamily: "'DM Sans', system-ui, sans-serif" }}
              >
                {completedSections} of {totalSections} sections complete
              </p>
            </div>
            <div className="text-right">
              <span
                className="text-[32px] font-bold text-[#2A2529]"
                style={{ fontFamily: "'DM Sans', system-ui, sans-serif", lineHeight: "40px" }}
              >
                {totalProgress}%
              </span>
            </div>
          </div>
          <Progress value={totalProgress} className="mt-4" />
          <div className="flex items-center gap-4 mt-3">
            <span className="text-[12px] text-[#847C82]">
              Positioning: {positioningProgress}/5
            </span>
            <span className="text-[12px] text-[#847C82]">ICPs: {foundation.icps.length}</span>
            <span className="text-[12px] text-[#847C82]">Messaging: {messagingProgress}/6</span>
          </div>
        </Card>

        {/* Three Foundation Cards */}
        <div ref={cardsRef} className="space-y-6">
          <PositioningCard
            data={foundation.positioning}
            onUpdate={(positioning) => setFoundation({ ...foundation, positioning })}
          />
          <ICPSection
            icps={foundation.icps}
            isLocked={foundation.status === "locked"}
            onUpdate={(icps) => setFoundation({ ...foundation, icps })}
          />
          <MessagingCard
            data={foundation.messaging}
            onUpdate={(messaging) => setFoundation({ ...foundation, messaging })}
          />
        </div>
      </div>
    </Layout>
  );
}
