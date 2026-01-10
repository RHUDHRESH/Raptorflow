"use client";

import { useState, useRef, useEffect, useMemo } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import gsap from "gsap";
import "react-big-calendar/lib/css/react-big-calendar.css";
import {
  Send, Sparkles, Bot, User, FileText, Edit3, Download, X, Check, Zap, Terminal, ArrowRight,
  Command, Paperclip, Maximize2, History, ChevronRight, Mail, MessageSquare, Video, Image,
  PenTool, Trash2, Copy, ExternalLink, Clock, Folder, ChevronDown, Search, Filter, Plus
} from "lucide-react";

import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { useMuseStore, MuseAsset } from "@/stores/museStore";
import { useMuseVersionStore, AssetVersion } from "@/stores/museVersionStore";
import { usePersonaStore, PersonaBrief } from "@/stores/personaStore";
import PersonaBriefModal from "@/components/muse/PersonaBriefModal";
import { exportAssets, ExportFormat, copyToClipboard, openInNewTab, sendToEmail } from "@/lib/museExport";
import { Template } from "@/lib/museTemplates";
import { TemplateSelector } from "@/components/muse/TemplateSelector";
import { TemplateEditor } from "@/components/muse/TemplateEditor";
import { ContentCalendar } from "@/components/muse/ContentCalendar";
import { format } from "date-fns";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   MUSE // COMMAND INTERFACE — 2-Panel Layout
   Chat interface (left) + Asset library (right)
   ══════════════════════════════════════════════════════════════════════════════ */

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  asset?: MuseAsset;
  suggestions?: string[];
  timestamp: number;
}

const generateId = () => Math.random().toString(36).substr(2, 9);

// Quick action buttons
const QUICK_ACTIONS = [
  { id: "email", label: "Draft Email", icon: Mail, prompt: "Draft a cold email for" },
  { id: "post", label: "LinkedIn Post", icon: MessageSquare, prompt: "Create a LinkedIn post about" },
  { id: "script", label: "Video Script", icon: Video, prompt: "Write a video script for" },
  { id: "carousel", label: "Carousel", icon: Image, prompt: "Design a carousel on" },
];

const TOPICS = [
  { id: "product-launch", label: "Product launch" },
  { id: "competitor-takedown", label: "Competitor takedown" },
  { id: "feature-update", label: "Feature update" },
  { id: "thought-leadership", label: "Thought leadership" },
  { id: "event-promo", label: "Event promo" },
] as const;

function AssetEditorModal({ asset, onClose, onSave }: { asset: MuseAsset; onClose: () => void; onSave: (content: string, updates?: Partial<MuseAsset>) => void }) {
  const [content, setContent] = useState(asset.content);
  const [copied, setCopied] = useState(false);
  const [toneAction, setToneAction] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'edit' | 'history'>('edit');
  const [selectedVersions, setSelectedVersions] = useState<{ from: string | null; to: string | null }>({ from: null, to: null });
  const { addVersion, getVersions, getDiff } = useMuseVersionStore();
  const versions = getVersions(asset.id);

  const handleSave = () => {
    // Save a version before updating
    addVersion(asset.id, {
      content: asset.content,
      title: asset.title,
      tags: asset.tags,
      type: asset.type,
      metadata: asset.metadata,
      changeDescription: 'Saved before edit',
    });
    onSave(content);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 60) return `${mins}m ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${date.getMonth() + 1}/${date.getDate()}`;
  };

  const applyRefinement = (action: string) => {
    setToneAction(action);
    const refinements: Record<string, string> = {
      Expand: "Expand this draft with richer detail, vivid examples, and clear benefits.",
      Simplify: "Rewrite this draft in plain language, short sentences, and remove jargon.",
      "Fix Grammar": "Clean up grammar, spelling, and tighten the prose.",
      "Make Punchy": "Make this punchier: bold hooks, shorter lines, and high energy.",
      "Change Tone": "Rewrite with a confident, consultative tone for busy executives."
    };
    setContent((prev) => `${prev}\n\n[Refine]: ${refinements[action]}`);
    setTimeout(() => setToneAction(null), 800);
  };

  const diff = selectedVersions.from && selectedVersions.to ? getDiff(asset.id, selectedVersions.from, selectedVersions.to) : null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
      <div className="bg-[var(--paper)] w-full max-w-5xl h-[90vh] rounded-[var(--radius)] border border-[var(--ink)] shadow-2xl flex flex-col relative overflow-hidden">
        {/* Header */}
        <div className="h-14 flex items-center justify-between px-6 border-b border-[var(--border)] bg-[var(--surface-subtle)]/80 backdrop-blur sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <div className="flex flex-col">
              <span className="font-editorial text-lg text-[var(--ink)]">{asset.title}</span>
              <span className="text-[10px] uppercase tracking-widest text-[var(--muted)] font-mono">{asset.type} // {asset.id}</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <SecondaryButton size="sm" onClick={handleCopy}>
              {copied ? <Check size={14} className="text-[var(--success)]" /> : <Copy size={14} />}
              {copied ? "Copied" : "Copy"}
            </SecondaryButton>
            <BlueprintButton size="sm" onClick={() => { onSave(content); onClose(); }}>
              <Check size={14} /> Save
            </BlueprintButton>
            <button onClick={onClose} className="p-2 hover:bg-[var(--surface)] rounded text-[var(--muted)] hover:text-[var(--ink)] transition-colors">
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Editor Body */}
        <div className="flex-1 flex relative z-0">
          {/* Tabs */}
          <div className="flex border-b border-[var(--structure-subtle)]">
            <button
              onClick={() => setActiveTab('edit')}
              className={cn(
                "flex-1 py-2 text-xs font-medium transition-colors",
                activeTab === 'edit'
                  ? "text-[var(--ink)] border-b-2 border-[var(--ink)]"
                  : "text-[var(--ink-muted)] hover:text-[var(--ink)]"
              )}
            >
              Edit
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={cn(
                "flex-1 py-2 text-xs font-medium transition-colors",
                activeTab === 'history'
                  ? "text-[var(--ink)] border-b-2 border-[var(--ink)]"
                  : "text-[var(--ink-muted)] hover:text-[var(--ink)]"
              )}
            >
              History ({versions.length})
            </button>
          </div>

          {/* Tab Content */}
          {activeTab === 'edit' ? (
            <>
              {/* Editor */}
              <div className="flex-1 flex flex-col">
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  className="flex-1 p-4 text-sm font-mono bg-[var(--surface)] border-0 resize-none focus:outline-none"
                  placeholder="Start typing your content..."
                />
                {/* Stats Bar */}
                <div className="flex items-center justify-between px-4 py-2 bg-[var(--surface-subtle)] border-t border-[var(--structure-subtle)]">
                  <div className="flex items-center gap-4 text-[10px] font-technical text-[var(--ink-muted)]">
                    <span>{content.split(/\s+/).filter(Boolean).length} words</span>
                    <span>{content.length} characters</span>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={handleCopy}
                      className={cn(
                        "px-3 py-1 text-xs font-medium rounded transition-colors",
                        copied
                          ? "bg-[var(--success)]/10 text-[var(--success)] border border-[var(--success)]/30"
                          : "text-[var(--ink-muted)] border border-[var(--structure-subtle)] hover:border-[var(--ink)] hover:text-[var(--ink)]"
                      )}
                    >
                      {copied ? "Copied!" : "Copy"}
                    </button>
                  </div>
                </div>
              </div>
              {/* Tone/Length Sidebar */}
              <div className="w-64 bg-[var(--paper)] border-l border-[var(--structure-subtle)] p-4 overflow-y-auto">
                <div className="mb-6">
                  <span className="text-[10px] font-bold text-[var(--ink-muted)] uppercase mb-3 block">Tone</span>
                  <div className="space-y-1.5">
                    {[
                      { label: "Confident", prompt: "Rewrite with a confident, authoritative tone. Use strong statements and avoid hedging." },
                      { label: "Casual", prompt: "Rewrite in a casual, conversational tone. Use contractions and friendly language." },
                      { label: "Formal", prompt: "Rewrite in a formal, professional tone. Use proper grammar and avoid slang." },
                    ].map(({ label, prompt }) => (
                      <button
                        key={label}
                        onClick={() => {
                          setContent((prev) => `${prev}\n\n[Tone: ${label}] ${prompt}`);
                        }}
                        className="w-full text-left px-3 py-2 text-xs font-medium text-[var(--ink-secondary)] border border-[var(--structure-subtle)] rounded-[var(--radius)] hover:border-[var(--blueprint)] hover:text-[var(--blueprint)] transition-all flex items-center justify-between group"
                      >
                        {label}
                        <Sparkles size={10} className="opacity-0 group-hover:opacity-100 transition-opacity" />
                      </button>
                    ))}
                  </div>
                </div>
                <div className="mb-6">
                  <span className="text-[10px] font-bold text-[var(--ink-muted)] uppercase mb-3 block">Length</span>
                  <div className="space-y-1.5">
                    {[
                      { label: "Shorten", prompt: "Shorten this content while preserving the key message. Remove redundancy and be concise." },
                      { label: "Expand", prompt: "Expand this content with more detail, examples, and explanations. Add depth and clarity." },
                    ].map(({ label, prompt }) => (
                      <button
                        key={label}
                        onClick={() => {
                          setContent((prev) => `${prev}\n\n[Length: ${label}] ${prompt}`);
                        }}
                        className="w-full text-left px-3 py-2 text-xs font-medium text-[var(--ink-secondary)] border border-[var(--structure-subtle)] rounded-[var(--radius)] hover:border-[var(--blueprint)] hover:text-[var(--blueprint)] transition-all flex items-center justify-between group"
                      >
                        {label}
                        <Sparkles size={10} className="opacity-0 group-hover:opacity-100 transition-opacity" />
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <span className="text-[10px] font-bold text-[var(--ink-muted)] uppercase mb-3 block">Quick Refine</span>
                  <div className="space-y-1.5">
                    {["Fix Grammar", "Make Punchy", "Simplify"].map((action) => (
                      <button
                        key={action}
                        onClick={() => applyRefinement(action)}
                        className={cn(
                          "w-full text-left px-3 py-2 text-xs font-medium text-[var(--ink-secondary)] border border-[var(--structure-subtle)] rounded-[var(--radius)] hover:border-[var(--blueprint)] hover:text-[var(--blueprint)] transition-all flex items-center justify-between group",
                          toneAction === action && "border-[var(--blueprint)] text-[var(--blueprint)]"
                        )}
                      >
                        {action}
                        <Sparkles size={10} className="opacity-0 group-hover:opacity-100 transition-opacity" />
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </>
          ) : (
            /* History Tab */
            <div className="flex-1 flex">
              {/* Version List */}
              <div className="w-1/2 border-r border-[var(--structure-subtle)] overflow-y-auto">
                <div className="p-3 space-y-2">
                  {versions.length === 0 ? (
                    <p className="text-xs text-[var(--ink-muted)] text-center py-8">No versions yet</p>
                  ) : (
                    versions.map((version, idx) => (
                      <div
                        key={version.id}
                        className={cn(
                          "p-2 rounded border cursor-pointer transition-colors",
                          selectedVersions.from === version.id || selectedVersions.to === version.id
                            ? "border-[var(--blueprint)] bg-[var(--blueprint-light)]/10"
                            : "border-[var(--structure-subtle)] hover:border-[var(--ink)]"
                        )}
                        onClick={() => {
                          if (!selectedVersions.from) {
                            setSelectedVersions({ from: version.id, to: null });
                          } else if (!selectedVersions.to && version.id !== selectedVersions.from) {
                            setSelectedVersions({ ...selectedVersions, to: version.id });
                          } else {
                            setSelectedVersions({ from: version.id, to: null });
                          }
                        }}
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-medium text-[var(--ink)]">Version {versions.length - idx}</span>
                          <span className="text-[9px] text-[var(--ink-muted)]">{formatTime(version.createdAt)}</span>
                        </div>
                        {version.changeDescription && (
                          <p className="text-[9px] text-[var(--ink-muted)] mt-1">{version.changeDescription}</p>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </div>
              {/* Diff Viewer */}
              <div className="w-1/2 overflow-y-auto">
                {diff ? (
                  <div className="p-3 space-y-2">
                    <h4 className="text-xs font-medium text-[var(--ink)] mb-2">Diff</h4>
                    {diff.added.length > 0 && (
                      <div>
                        <p className="text-[9px] font-medium text-[var(--success)] mb-1">Added</p>
                        <pre className="text-[10px] font-mono bg-[var(--success)]/5 border border-[var(--success)]/20 rounded p-2 whitespace-pre-wrap">
                          {diff.added.join('\n')}
                        </pre>
                      </div>
                    )}
                    {diff.removed.length > 0 && (
                      <div>
                        <p className="text-[9px] font-medium text-[var(--destructive)] mb-1">Removed</p>
                        <pre className="text-[10px] font-mono bg-[var(--destructive)]/5 border border-[var(--destructive)]/20 rounded p-2 whitespace-pre-wrap">
                          {diff.removed.join('\n')}
                        </pre>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-full text-[var(--ink-muted)]">
                    <p className="text-xs text-center">Select two versions to compare</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Footer Actions */}
          {activeTab === 'edit' && (
            <div className="flex items-center justify-between p-4 border-t border-[var(--structure-subtle)]">
              <div className="flex gap-2">
                <button
                  onClick={() => onClose()}
                  className="px-3 py-1.5 text-xs text-[var(--ink-muted)] border border-[var(--structure-subtle)] rounded-[var(--radius)] hover:border-[var(--ink)] hover:text-[var(--ink)] transition-colors"
                >
                  Cancel
                </button>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleSave}
                  disabled={!content.trim() || content === asset.content}
                  className="px-3 py-1.5 text-xs bg-[var(--ink)] text-[var(--paper)] rounded-[var(--radius)] hover:opacity-90 disabled:opacity-40 transition-opacity"
                >
                  Save Changes
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function MessageBubble({ msg, onOpenAsset, onSuggestion }: { msg: Message; onOpenAsset: (asset: MuseAsset) => void; onSuggestion: (text: string) => void }) {
  const isBot = msg.type === 'bot';

  return (
    <div className={cn("flex w-full mb-6 animate-in fade-in slide-in-from-bottom-2 duration-300", isBot ? 'justify-start' : 'justify-end')}>
      {isBot && (
        <div className="w-7 h-7 rounded bg-[var(--ink)] text-[var(--paper)] flex items-center justify-center mr-3 shrink-0 mt-0.5">
          <Bot size={14} />
        </div>
      )}

      <div className={cn("max-w-[90%]", !isBot && "flex flex-col items-end")}>
        {msg.type === 'user' ? (
          <div className="bg-[var(--surface)] border border-[var(--structure)] px-4 py-2.5 rounded-[var(--radius)] text-[var(--ink)] text-sm">
            {msg.content}
          </div>
        ) : (
          <div className="space-y-3">
            <div className="text-sm text-[var(--ink)] leading-relaxed whitespace-pre-wrap">
              {msg.content}
            </div>
          </div>
        )}

        {msg.asset && (
          <div onClick={() => onOpenAsset(msg.asset!)} className="mt-3 w-full max-w-md cursor-pointer group">
            <div className="bg-[var(--paper)] border border-[var(--blueprint)] rounded-[var(--radius)] p-4 hover:border-[var(--ink)] transition-all">
              <div className="flex items-start gap-3">
                <div className="p-2.5 bg-[var(--blueprint-light)]/30 text-[var(--blueprint)] rounded">
                  <FileText size={20} strokeWidth={1.5} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <h4 className="font-medium text-sm text-[var(--ink)] truncate group-hover:text-[var(--blueprint)] transition-colors">{msg.asset.title}</h4>
                    <ArrowRight size={14} className="text-[var(--blueprint)] opacity-0 group-hover:opacity-100 transition-all" />
                  </div>
                  <BlueprintBadge variant="default" size="sm">{msg.asset.type}</BlueprintBadge>
                  <p className="text-xs text-[var(--ink-muted)] mt-2 line-clamp-2 italic">
                    "{msg.asset.content.substring(0, 100)}..."
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {msg.suggestions && (
          <div className="flex flex-wrap gap-1.5 mt-3">
            {msg.suggestions.map((s, i) => (
              <button
                key={i}
                onClick={() => onSuggestion(s)}
                className="text-[10px] font-medium text-[var(--ink-secondary)] px-2.5 py-1 rounded-full border border-[var(--structure-subtle)] hover:border-[var(--blueprint)] hover:text-[var(--blueprint)] transition-colors"
              >
                {s}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function MusePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { assets, addAsset, updateAsset, deleteAsset } = useMuseStore();
  const { brief } = usePersonaStore();

  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'init',
      type: 'bot',
      content: "Muse system online. Ready to generate high-converting content for your campaigns.",
      timestamp: Date.now(),
      suggestions: ["Draft a cold email", "Create a LinkedIn post", "Analyze a competitor"]
    }
  ]);
  const [input, setInput] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const [activeAsset, setActiveAsset] = useState<MuseAsset | null>(null);
  const [sidebarTab, setSidebarTab] = useState<"assets" | "history" | "calendar">("assets");
  const [selectedTopic, setSelectedTopic] = useState<(typeof TOPICS)[number]>(TOPICS[0]);
  const [isTopicDropdownOpen, setIsTopicDropdownOpen] = useState(false);
  const [filterType, setFilterType] = useState<string>("all");
  const [filterTag, setFilterTag] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState("");
  const [bulkMode, setBulkMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
  const [isPersonaModalOpen, setIsPersonaModalOpen] = useState(false);
  const [exportFormat, setExportFormat] = useState<ExportFormat>('markdown');
  const [isExportDropdownOpen, setIsExportDropdownOpen] = useState(false);
  const [isTemplateSelectorOpen, setIsTemplateSelectorOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const topicDropdownRef = useRef<HTMLDivElement>(null);
  const exportDropdownRef = useRef<HTMLDivElement>(null);

  // Auto-scroll
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, isThinking]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd+K focus input
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.querySelector<HTMLInputElement>('input[placeholder="Tell me what to create..."]')?.focus();
      }
      // Ctrl/Cmd+E export
      if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
        e.preventDefault();
        const payload = JSON.stringify(assets, null, 2);
        const blob = new Blob([payload], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "muse-assets.json";
        link.click();
        URL.revokeObjectURL(url);
      }
      // Escape close modals
      if (e.key === 'Escape') {
        if (activeAsset) setActiveAsset(null);
        if (deleteConfirm) setDeleteConfirm(null);
        if (isTopicDropdownOpen) setIsTopicDropdownOpen(false);
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [assets, activeAsset, deleteConfirm, isTopicDropdownOpen]);

  // Context loading
  useEffect(() => {
    const context = searchParams.get('context');
    if (searchParams.get('source') === 'blackbox' && context) {
      setTimeout(() => {
        setMessages(prev => [...prev, { id: generateId(), type: 'user', content: `Context: ${decodeURIComponent(context)}`, timestamp: Date.now() }]);
        handleCommand(decodeURIComponent(context), true);
      }, 500);
    }
  }, [searchParams]);

  const handleCommand = async (cmd: string, silent = false) => {
    setIsThinking(true);

    setTimeout(() => {
      setIsThinking(false);
      const lower = cmd.toLowerCase();
      let response: Message = { id: generateId(), type: 'bot', content: "I didn't quite catch that. Try asking me to draft, create, or write something.", timestamp: Date.now() };

      // Include persona brief context if available
      const contextPrefix = brief ? `\n\n[Persona Brief]\nAudience: ${brief.audience}\nVoice: ${brief.voice}\nGoals: ${brief.goals.join(', ')}\n` : '';

      if (lower.includes('draft') || lower.includes('create') || lower.includes('write')) {
        const assetType = lower.includes('email') ? 'Email' : lower.includes('linkedin') ? 'Social' : lower.includes('video') ? 'Script' : 'Blog';
        const asset: MuseAsset = {
          id: `GEN-${Date.now()}`,
          title: cmd.length > 30 ? `${cmd.slice(0, 30)}...` : cmd,
          type: assetType,
          content: `Here is a high-converting ${assetType.toLowerCase()} based on your strategy...${contextPrefix}\n\n[Subject Line]: Disruption requires precision.\n\nFollowing up on our previous discussion about scaling your...\n\nKey Points:\n• Point one with clear value proposition\n• Point two addressing pain points\n• Point three with social proof\n\nBest regards,\n[Your Name]`,
          tags: ["Draft"], createdAt: new Date().toISOString(), source: "Muse"
        };
        addAsset(asset);
        response = {
          id: generateId(), type: 'bot',
          content: `I've generated a ${assetType.toLowerCase()} draft${brief ? ' using your persona brief' : ''}. Click the card below to open the full editor.`,
          asset, timestamp: Date.now(),
          suggestions: ["Make it bolder", "Shorten it", "Add a CTA"]
        };
      } else if (lower.includes('analyze') || lower.includes('competitor')) {
        response = { id: generateId(), type: 'bot', content: "Competitor analysis initiated. I'll scan available market data and provide insights on positioning opportunities.", timestamp: Date.now(), suggestions: ["Generate attack angles", "Find gaps", "Track their content"] };
      } else {
        response = { id: generateId(), type: 'bot', content: "Command acknowledged. Try commands like:\n• \"Draft a cold email for enterprise CTOs\"\n• \"Create a LinkedIn post about AI\"\n• \"Write a video script for product demo\"", timestamp: Date.now() };
      }

      setMessages(prev => [...prev, response]);
    }, 1200);
  };

  // Close dropdowns on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (topicDropdownRef.current && !topicDropdownRef.current.contains(e.target as Node)) {
        setIsTopicDropdownOpen(false);
      }
      if (exportDropdownRef.current && !exportDropdownRef.current.contains(e.target as Node)) {
        setIsExportDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleQuickAction = (action: typeof QUICK_ACTIONS[0]) => {
    const prompt = `${action.prompt} ${selectedTopic.label}`;
    sendMessage(prompt);
  };

  const sendMessage = (text: string) => {
    if (!text.trim()) return;
    const msg: Message = { id: generateId(), type: 'user', content: text, timestamp: Date.now() };
    setMessages(prev => [...prev, msg]);
    handleCommand(text);
  };

  const handleSend = () => {
    if (!input.trim()) return;
    sendMessage(input);
    setInput("");
  };

  const handleSuggestion = (text: string) => {
    sendMessage(text);
  };

  const toggleSelect = (id: string) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const handleDelete = (id: string) => {
    setDeleteConfirm(id);
  };

  const confirmDelete = () => {
    if (deleteConfirm) {
      deleteAsset(deleteConfirm);
      setDeleteConfirm(null);
      if (activeAsset?.id === deleteConfirm) setActiveAsset(null);
    }
  };

  const handleBulkDelete = () => {
    selectedIds.forEach(id => deleteAsset(id));
    setSelectedIds(new Set());
    setBulkMode(false);
  };

  const handleExport = async (format: 'markdown' | 'pdf' | 'html' | 'csv') => {
    try {
      await exportAssets(filteredAssets, format, { includeMetadata: true, includeTimestamp: true });
      setIsExportDropdownOpen(false);
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const handleTemplateSelect = (template: Template) => {
    setSelectedTemplate(template);
  };

  const handleTemplateSubmit = (content: string) => {
    // Create a new asset from the template
    const newAsset: MuseAsset = {
      id: generateId(),
      title: selectedTemplate?.title || 'Untitled',
      content,
      type: selectedTemplate?.type || 'email',
      tags: selectedTemplate?.tags || [],
      source: 'Template',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    addAsset(newAsset);
    setSelectedTemplate(null);

    // Add to messages
    setMessages(prev => [...prev, {
      id: generateId(),
      type: 'bot',
      content: `I've created your ${selectedTemplate?.type} using the "${selectedTemplate?.title}" template. You can edit it further if needed.`,
      asset: newAsset,
      timestamp: Date.now()
    }]);
  };

  const formatTime = (timestamp: string) => {
    // Use a fixed format to avoid hydration mismatches
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 60) return `${mins}m ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h ago`;
    // Use a consistent date format to avoid hydration issues
    return `${date.getMonth() + 1}/${date.getDate()}`;
  };

  const allTags = useMemo(() => {
    const tags = new Set<string>();
    assets.forEach(a => a.tags.forEach(t => tags.add(t)));
    return Array.from(tags);
  }, [assets]);

  const filteredAssets = useMemo(() => {
    let filtered = assets;
    if (filterType !== "all") filtered = filtered.filter(a => a.type === filterType);
    if (filterTag) filtered = filtered.filter(a => a.tags.includes(filterTag));
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      filtered = filtered.filter(a => a.title.toLowerCase().includes(q) || a.content.toLowerCase().includes(q));
    }
    const sorted = [...filtered].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
    return sidebarTab === "assets" ? sorted.slice(0, 10) : sorted;
  }, [assets, filterType, filterTag, searchQuery, sidebarTab]);

  return (
    <div className="flex h-[calc(100vh-100px)] gap-6">
      {/* LEFT PANEL: Chat Interface */}
      <div className="flex-1 flex flex-col bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] overflow-hidden">
        {/* Header */}
        <div className="h-14 flex items-center justify-between px-5 border-b border-[var(--structure)] bg-[var(--surface)]">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-[var(--ink)] text-[var(--paper)] flex items-center justify-center">
              <Bot size={16} />
            </div>
            <div>
              <h1 className="font-editorial text-lg text-[var(--ink)] leading-none">Muse</h1>
              <div className="flex items-center gap-1.5 mt-0.5">
                <div className="w-1.5 h-1.5 bg-[var(--success)] rounded-full animate-pulse" />
                <span className="text-[10px] font-technical text-[var(--ink-muted)] uppercase">GENERATIVE ENGINE</span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2 text-[10px] font-technical text-[var(--ink-muted)]">
            <Zap size={10} className="text-[var(--warning)]" />
            <span>UNLIMITED</span>
          </div>
        </div>

        {/* Persona Brief Bar */}
        {brief && (
          <div className="px-5 py-2 border-b border-[var(--structure-subtle)] bg-[var(--blueprint-light)]/5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-[9px] font-bold text-[var(--blueprint)] uppercase">Persona Brief</span>
                <span className="text-[9px] text-[var(--ink-muted)]">{brief.audience} • {brief.voice}</span>
              </div>
              <button
                onClick={() => setIsPersonaModalOpen(true)}
                className="text-[9px] text-[var(--blueprint)] hover:underline"
              >
                Edit
              </button>
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="px-5 py-3 border-b border-[var(--structure-subtle)] bg-[var(--surface-subtle)]">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold text-[var(--ink-muted)] uppercase mr-2">QUICK:</span>
            {/* Topic Selector Dropdown */}
            <div ref={topicDropdownRef} className="relative">
              <button
                onClick={() => setIsTopicDropdownOpen(!isTopicDropdownOpen)}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-[var(--ink)] bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] hover:border-[var(--blueprint)] hover:text-[var(--blueprint)] transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--blueprint)]"
              >
                {selectedTopic.label}
                <ChevronDown size={12} className={cn("transition-transform", isTopicDropdownOpen && "rotate-180")} />
              </button>
              {isTopicDropdownOpen && (
                <div className="absolute top-full left-0 mt-1 bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] shadow-lg z-10 min-w-[140px] animate-in fade-in slide-in-from-top-1 duration-150">
                  {TOPICS.map((topic) => (
                    <button
                      key={topic.id}
                      onClick={() => {
                        setSelectedTopic(topic);
                        setIsTopicDropdownOpen(false);
                      }}
                      className={cn(
                        "w-full text-left px-3 py-2 text-xs font-medium transition-colors first:rounded-t-[var(--radius)] last:rounded-b-[var(--radius)]",
                        selectedTopic.id === topic.id
                          ? "bg-[var(--blueprint-light)]/30 text-[var(--blueprint)]"
                          : "text-[var(--ink)] hover:bg-[var(--surface)] hover:text-[var(--blueprint)]"
                      )}
                    >
                      {topic.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
            {/* Action Buttons */}
            {QUICK_ACTIONS.map((action) => (
              <button
                key={action.id}
                onClick={() => handleQuickAction(action)}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-[var(--ink-secondary)] border border-[var(--structure-subtle)] rounded-[var(--radius)] hover:border-[var(--blueprint)] hover:text-[var(--blueprint)] transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--blueprint)]"
              >
                <action.icon size={12} />
                {action.label}
              </button>
            ))}
            <button
              onClick={() => setIsTemplateSelectorOpen(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-[var(--ink-secondary)] border border-[var(--structure-subtle)] rounded-[var(--radius)] hover:border-[var(--blueprint)] hover:text-[var(--blueprint)] transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--blueprint)]"
            >
              <Folder size={12} />
              Use Template
            </button>
          </div>
        </div>

        {/* Chat Stream */}
        <div className="flex-1 overflow-y-auto p-5">
          {messages.map(m => <MessageBubble key={m.id} msg={m} onOpenAsset={setActiveAsset} onSuggestion={handleSuggestion} />)}

          {isThinking && (
            <div className="flex items-center gap-3 ml-10 animate-in fade-in duration-300">
              <div className="flex gap-1">
                <div className="w-1.5 h-1.5 bg-[var(--ink-muted)] rounded-full animate-bounce [animation-delay:-0.32s]" />
                <div className="w-1.5 h-1.5 bg-[var(--ink-muted)] rounded-full animate-bounce [animation-delay:-0.16s]" />
                <div className="w-1.5 h-1.5 bg-[var(--ink-muted)] rounded-full animate-bounce" />
              </div>
              <span className="text-xs font-technical text-[var(--ink-muted)]">GENERATING...</span>
            </div>
          )}
          <div ref={messagesEndRef} className="h-4" />
        </div>

        {/* Input - Floating */}
        <div className="p-5 pt-2">
          <div className="flex items-center gap-3 bg-[var(--surface)] border border-[var(--structure)] rounded-[var(--radius)] px-4 py-3 shadow-sm focus-within:border-[var(--blueprint)] focus-within:ring-1 focus-within:ring-[var(--blueprint)]/20 transition-all">
            <Terminal size={18} className="text-[var(--ink-muted)] shrink-0" />
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
                // Escape clears input
                if (e.key === 'Escape') setInput('');
              }}
              placeholder="Tell me what to create..."
              className="flex-1 bg-transparent text-sm text-[var(--ink)] placeholder:text-[var(--ink-muted)] focus:outline-none"
              autoFocus
            />
            <button
              onClick={handleSend}
              disabled={!input.trim()}
              className="p-2 bg-[var(--ink)] text-[var(--paper)] rounded-[var(--radius)] hover:opacity-90 disabled:opacity-40 transition-all shrink-0"
            >
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* RIGHT PANEL: Asset Library */}
      <div className="w-80 bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="h-14 flex items-center justify-between px-5 border-b border-[var(--structure)] bg-[var(--surface)]">
          <div className="flex items-center gap-3">
            <Folder size={16} className="text-[var(--ink-muted)]" />
            <span className="font-medium text-sm text-[var(--ink)]">Asset Library</span>
          </div>
          <div className="flex items-center gap-2">
            {filteredAssets.length > 0 && (
              <button
                onClick={() => { setBulkMode(!bulkMode); setSelectedIds(new Set()); }}
                className={cn(
                  "text-[10px] font-medium px-2 py-1 rounded border transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--blueprint)]",
                  bulkMode ? "bg-[var(--blueprint-light)]/30 text-[var(--blueprint)] border-[var(--blueprint)]" : "text-[var(--ink-muted)] border-[var(--structure-subtle)] hover:border-[var(--ink)] hover:text-[var(--ink)]"
                )}
              >
                {bulkMode ? `Cancel (${selectedIds.size})` : "Select"}
              </button>
            )}
            <span className="text-xs font-technical text-[var(--ink-muted)]">{filteredAssets.length}</span>
          </div>
        </div>

        {/* Filters */}
        <div className="px-3 py-2 border-b border-[var(--structure-subtle)] bg-[var(--surface-subtle)] space-y-2">
          {/* Search */}
          <div className="relative">
            <Search size={12} className="absolute left-2 top-1/2 -translate-y-1/2 text-[var(--ink-muted)]" />
            <input
              type="text"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Escape') setSearchQuery('');
              }}
              placeholder="Search assets..."
              className="w-full pl-7 pr-2 py-1.5 text-xs bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)] placeholder:text-[var(--ink-ghost)]"
            />
          </div>
          {/* Type + Tag filters */}
          <div className="flex gap-2">
            <select
              value={filterType}
              onChange={e => setFilterType(e.target.value)}
              className="flex-1 text-xs bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] px-2 py-1.5 focus:outline-none focus:border-[var(--blueprint)]"
            >
              <option value="all">All Types</option>
              <option value="Email">Email</option>
              <option value="Social">Social</option>
              <option value="Blog">Blog</option>
              <option value="Script">Script</option>
              <option value="Campaign">Campaign</option>
              <option value="Tweet">Tweet</option>
              <option value="Other">Other</option>
            </select>
            <select
              value={filterTag}
              onChange={e => setFilterTag(e.target.value)}
              className="flex-1 text-xs bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] px-2 py-1.5 focus:outline-none focus:border-[var(--blueprint)]"
            >
              <option value="">All Tags</option>
              {allTags.map(tag => (
                <option key={tag} value={tag}>{tag}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-[var(--structure-subtle)]">
          <button
            onClick={() => setSidebarTab("assets")}
            className={cn(
              "flex-1 py-2.5 text-xs font-medium transition-colors",
              sidebarTab === "assets"
                ? "text-[var(--ink)] border-b-2 border-[var(--ink)]"
                : "text-[var(--ink-muted)] hover:text-[var(--ink)]"
            )}
          >
            Recent
          </button>
          <button
            onClick={() => setSidebarTab("history")}
            className={cn(
              "flex-1 py-2.5 text-xs font-medium transition-colors",
              sidebarTab === "history"
                ? "text-[var(--ink)] border-b-2 border-[var(--ink)]"
                : "text-[var(--ink-muted)] hover:text-[var(--ink)]"
            )}
          >
            All Assets
          </button>
          <button
            onClick={() => setSidebarTab("calendar")}
            className={cn(
              "flex-1 py-2.5 text-xs font-medium transition-colors",
              sidebarTab === "calendar"
                ? "text-[var(--ink)] border-b-2 border-[var(--ink)]"
                : "text-[var(--ink-muted)] hover:text-[var(--ink)]"
            )}
          >
            Calendar
          </button>
        </div>

        {/* Asset List or Calendar */}
        {sidebarTab === "calendar" ? (
          <ContentCalendar
            assets={assets}
            onEventClick={(event) => {
              if (event.resource?.asset) {
                setActiveAsset(event.resource.asset);
              }
            }}
            onDateSelect={(date) => {
              setInput(`Schedule content for ${format(date, 'PPP')}`);
              document.querySelector<HTMLInputElement>('input[placeholder="Tell me what to create..."]')?.focus();
            }}
          />
        ) : (
          <div className="flex-1 overflow-y-auto p-3">
            {filteredAssets.length === 0 && (searchQuery || filterType !== "all" || filterTag) ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <Filter size={20} className="text-[var(--ink-ghost)] mb-2" />
                <p className="text-xs text-[var(--ink-muted)]">No assets match filters</p>
                <button onClick={() => { setFilterType("all"); setFilterTag(""); setSearchQuery(""); }} className="text-[10px] text-[var(--blueprint)] hover:underline mt-1">Clear filters</button>
              </div>
            ) : filteredAssets.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <div className="w-12 h-12 rounded-full border border-[var(--structure-subtle)] flex items-center justify-center mb-3">
                  <FileText size={20} className="text-[var(--ink-ghost)]" />
                </div>
                <p className="text-xs text-[var(--ink-muted)]">No assets yet</p>
                <button onClick={() => { setInput("Draft a cold email for product launch"); document.querySelector<HTMLInputElement>('input[placeholder="Tell me what to create..."]')?.focus(); }} className="text-[10px] text-[var(--blueprint)] hover:underline mt-1">Generate something now</button>
              </div>
            ) : (
              <div className="space-y-2">
                {filteredAssets.map((asset) => (
                  <div
                    key={asset.id}
                    className={cn(
                      "group p-3 bg-[var(--surface)] border rounded-[var(--radius)] transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--blueprint)]",
                      bulkMode ? "border-[var(--structure-subtle)]" : "border-[var(--structure-subtle)] cursor-pointer hover:border-[var(--structure)]"
                    )}
                    tabIndex={bulkMode ? undefined : 0}
                  >
                    <div className="flex items-start gap-3">
                      {bulkMode && (
                        <input
                          type="checkbox"
                          checked={selectedIds.has(asset.id)}
                          onChange={() => toggleSelect(asset.id)}
                          className="mt-1 rounded border-[var(--structure-subtle)] text-[var(--blueprint)] focus:ring-[var(--blueprint)]"
                        />
                      )}
                      <div
                        className={cn(
                          "p-2 bg-[var(--paper)] border rounded text-[var(--ink-muted)]",
                          bulkMode ? "border-[var(--structure-subtle)]" : "border-[var(--structure-subtle)]"
                        )}
                      >
                        <FileText size={14} />
                      </div>
                      <div className="flex-1 min-w-0" onClick={!bulkMode ? () => setActiveAsset(asset) : undefined}>
                        <div className="flex items-center justify-between">
                          <h4 className="text-xs font-medium text-[var(--ink)] truncate group-hover:text-[var(--blueprint)] transition-colors">
                            {asset.title}
                          </h4>
                          {!bulkMode && (
                            <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
                              <button
                                onClick={(e) => { e.stopPropagation(); copyToClipboard(asset.content); }}
                                className="p-0.5 hover:bg-[var(--surface)] rounded text-[var(--ink-muted)] hover:text-[var(--ink)]"
                                title="Copy to clipboard"
                              >
                                <Copy size={12} />
                              </button>
                              <button
                                onClick={(e) => { e.stopPropagation(); openInNewTab(asset.content, asset.title); }}
                                className="p-0.5 hover:bg-[var(--surface)] rounded text-[var(--ink-muted)] hover:text-[var(--ink)]"
                                title="Open in new tab"
                              >
                                <ExternalLink size={12} />
                              </button>
                              <button
                                onClick={(e) => { e.stopPropagation(); sendToEmail(asset.title, asset.content); }}
                                className="p-0.5 hover:bg-[var(--surface)] rounded text-[var(--ink-muted)] hover:text-[var(--ink)]"
                                title="Send via email"
                              >
                                <Mail size={12} />
                              </button>
                              <button
                                onClick={(e) => { e.stopPropagation(); handleDelete(asset.id); }}
                                className="p-0.5 hover:bg-[var(--surface)] rounded text-[var(--ink-muted)] hover:text-[var(--destructive)]"
                                title="Delete asset"
                              >
                                <Trash2 size={12} />
                              </button>
                            </div>
                          )}
                        </div>
                        <p className="text-[11px] text-[var(--ink-muted)] mt-1 line-clamp-2">{asset.content.slice(0, 110)}...</p>
                        <div className="flex items-center gap-2 mt-1">
                          <BlueprintBadge variant="default" size="sm">{asset.type}</BlueprintBadge>
                          {asset.tags.map(tag => (
                            <span key={tag} className="text-[9px] px-1.5 py-0.5 bg-[var(--blueprint-light)]/20 text-[var(--blueprint)] rounded">{tag}</span>
                          ))}
                          {asset.source && <span className="text-[9px] text-[var(--ink-muted)] uppercase">{asset.source}</span>}
                          <span className="text-[9px] text-[var(--ink-ghost)]">{formatTime(asset.createdAt)}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                {bulkMode && selectedIds.size > 0 && (
                  <div className="sticky bottom-0 p-2 bg-[var(--surface-subtle)] border-t border-[var(--structure-subtle)] flex items-center justify-between">
                    <span className="text-[10px] text-[var(--ink-muted)]">{selectedIds.size} selected</span>
                    <button
                      onClick={handleBulkDelete}
                      className="text-[10px] font-medium px-2 py-1 bg-[var(--destructive)]/10 text-[var(--destructive)] border border-[var(--destructive)]/30 rounded hover:bg-[var(--destructive)]/20 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--destructive)]"
                    >
                      Delete Selected
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="p-3 border-t border-[var(--structure-subtle)] bg-[var(--surface-subtle)]">
          <div ref={exportDropdownRef} className="relative">
            <button
              onClick={() => setIsExportDropdownOpen(!isExportDropdownOpen)}
              className="w-full py-2 text-xs font-medium text-[var(--ink-muted)] hover:text-[var(--ink)] border border-[var(--structure-subtle)] hover:border-[var(--structure)] rounded-[var(--radius)] transition-all flex items-center justify-center gap-2"
            >
              <ExternalLink size={12} />
              Export ({filteredAssets.length})
              <ChevronDown size={10} className={cn("transition-transform", isExportDropdownOpen && "rotate-180")} />
            </button>
            {isExportDropdownOpen && (
              <div className="absolute bottom-full left-0 mb-1 w-full bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] shadow-lg z-10 animate-in fade-in slide-in-from-bottom-1 duration-150">
                <div className="p-2">
                  <p className="text-[9px] text-[var(--ink-muted)] mb-2">Format:</p>
                  <div className="space-y-1">
                    {(['markdown', 'pdf', 'html', 'csv'] as ExportFormat[]).map((format) => (
                      <button
                        key={format}
                        onClick={() => handleExport(format)}
                        className={cn(
                          "w-full text-left px-3 py-2 text-xs font-medium transition-colors rounded",
                          exportFormat === format
                            ? "bg-[var(--blueprint-light)]/30 text-[var(--blueprint)]"
                            : "text-[var(--ink)] hover:bg-[var(--surface)]"
                        )}
                      >
                        {format.toUpperCase()}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
          <div className="bg-[var(--paper)] w-full max-w-sm rounded-[var(--radius)] border border-[var(--ink)] shadow-2xl p-5">
            <h3 className="font-medium text-sm text-[var(--ink)] mb-2">Delete asset?</h3>
            <p className="text-xs text-[var(--ink-muted)] mb-4">This cannot be undone.</p>
            <div className="flex gap-2 justify-end">
              <button onClick={() => setDeleteConfirm(null)} className="px-3 py-1.5 text-xs text-[var(--ink-muted)] border border-[var(--structure-subtle)] rounded-[var(--radius)] hover:border-[var(--ink)] hover:text-[var(--ink)] transition-colors">
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                className="px-3 py-1.5 text-xs bg-[var(--destructive)] text-[var(--paper)] rounded-[var(--radius)] hover:opacity-90 transition-opacity focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--destructive)]"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {activeAsset && (
        <AssetEditorModal
          asset={activeAsset}
          onClose={() => setActiveAsset(null)}
          onSave={(content) => {
            setActiveAsset(null);
            updateAsset(activeAsset.id, { content });
            setMessages(prev => [...prev, { id: generateId(), type: 'bot', content: "Asset updated and saved.", timestamp: Date.now() }]);
          }}
        />
      )}

      {/* Persona Brief Modal */}
      <PersonaBriefModal
        isOpen={isPersonaModalOpen}
        onClose={() => setIsPersonaModalOpen(false)}
      />

      {/* Template Modals */}
      {isTemplateSelectorOpen && (
        <TemplateSelector
          onSelect={handleTemplateSelect}
          onClose={() => setIsTemplateSelectorOpen(false)}
        />
      )}

      {selectedTemplate && (
        <TemplateEditor
          template={selectedTemplate}
          onSubmit={handleTemplateSubmit}
          onClose={() => setSelectedTemplate(null)}
        />
      )}
    </div>
  );
}
