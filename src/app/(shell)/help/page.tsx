"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import {
  Search,
  Book,
  MessageCircle,
  ArrowRight,
  Zap,
  Target,
  Users,
  BarChart3,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Mail,
  Link as LinkIcon
} from "lucide-react";

import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { PageHeader } from "@/components/ui/PageHeader";
import { notify } from "@/lib/notifications";
import { useWorkspace } from "@/components/workspace/WorkspaceProvider";
import { searchService, type SearchResponse } from "@/services/search.service";
import { scraperService, type ScrapeResult } from "@/services/scraper.service";
import { readRuntimeProfile, writeRuntimeProfile } from "@/lib/aiRuntimeProfile";

/* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
   HELP CENTER â€” Documentation & Support
   Clean blueprint style, no emojis, Lucide icons only
   â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */

const QUICK_LINKS = [
  { title: "Dashboard", desc: "Workspace overview and status.", icon: Book, href: "/dashboard" },
  { title: "Campaigns", desc: "90-day arcs that hold your moves.", icon: BarChart3, href: "/campaigns" },
  { title: "Moves", desc: "Create tactical plans and execute.", icon: Zap, href: "/moves" },
  { title: "Foundation", desc: "Positioning, ICPs, messaging, channels.", icon: Target, href: "/foundation" },
  { title: "Muse", desc: "AI content assistant (optional).", icon: MessageCircle, href: "/muse" },
  { title: "Settings", desc: "Workspace settings and tenant id.", icon: Users, href: "/settings" },
];

const FAQS = [
  {
    q: "What is RaptorFlow?",
    a: "RaptorFlow is a marketing operating system for founders. In reconstruction mode there is no login or paywall; everything is scoped to your current workspace."
  },
  {
    q: "What is a Workspace?",
    a: "A Workspace is the tenant boundary. The UI stores a workspace id in localStorage and sends it as the x-workspace-id header on API calls."
  },
  {
    q: "How do Campaigns work?",
    a: "Campaigns are 90-day strategic arcs that contain multiple Moves. Campaign CRUD is persisted per workspace."
  },
  {
    q: "How do Moves work?",
    a: "A Move is a tactical plan (usually 3-14 days). You can create a move, track execution tasks, and persist updates to the database."
  },
  {
    q: "What is Foundation?",
    a: "Foundation stores positioning inputs: ICPs (RICPs), messaging, and channels. It is saved per workspace."
  },
  {
    q: "Why does Muse say unavailable?",
    a: "Muse requires a working Vertex AI configuration. If it is not configured, the API returns an explicit 503 instead of silently falling back."
  },
];

export default function HelpPage() {
  const { workspaceId } = useWorkspace();
  const pageRef = useRef<HTMLDivElement>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const [runtimeIntensity, setRuntimeIntensity] = useState<"low" | "medium" | "high">("medium");
  const [runtimeMode, setRuntimeMode] = useState<"single" | "council" | "swarm">("council");

  const [labSearchQuery, setLabSearchQuery] = useState("");
  const [labSearchResult, setLabSearchResult] = useState<SearchResponse | null>(null);
  const [isSearching, setIsSearching] = useState(false);

  const [labScrapeUrl, setLabScrapeUrl] = useState("");
  const [labScrapeResult, setLabScrapeResult] = useState<ScrapeResult | null>(null);
  const [isScraping, setIsScraping] = useState(false);

  useEffect(() => {
    if (!pageRef.current) return;
    gsap.fromTo(pageRef.current, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.4, ease: "power2.out" });
  }, []);

  useEffect(() => {
    const runtime = readRuntimeProfile();
    setRuntimeIntensity(runtime.intensity);
    setRuntimeMode(runtime.executionMode);
  }, []);

  useEffect(() => {
    writeRuntimeProfile({
      intensity: runtimeIntensity,
      executionMode: runtimeMode,
    });
  }, [runtimeIntensity, runtimeMode]);

  const filteredFaqs = searchQuery
    ? FAQS.filter(f =>
      f.q.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.a.toLowerCase().includes(searchQuery.toLowerCase())
    )
    : FAQS;

  async function runSearchLab() {
    if (!workspaceId) {
      notify.error("Workspace not ready");
      return;
    }
    if (!labSearchQuery.trim()) {
      notify.error("Enter a search query");
      return;
    }

    setIsSearching(true);
    try {
      const response = await searchService.search(
        workspaceId,
        labSearchQuery.trim(),
        undefined,
        undefined,
        {
          intensity: runtimeIntensity,
          executionMode: runtimeMode,
          summarize: true,
        }
      );
      setLabSearchResult(response);
      notify.success("Search completed");
    } catch (error: any) {
      notify.error(error?.message || "Search failed");
    } finally {
      setIsSearching(false);
    }
  }

  async function runScraperLab() {
    if (!workspaceId) {
      notify.error("Workspace not ready");
      return;
    }
    if (!labScrapeUrl.trim()) {
      notify.error("Enter a URL to scrape");
      return;
    }

    setIsScraping(true);
    try {
      const response = await scraperService.scrape(workspaceId, {
        url: labScrapeUrl.trim(),
        user_id: workspaceId,
        intensity: runtimeIntensity,
        execution_mode: runtimeMode,
      });
      setLabScrapeResult(response);
      notify.success("Scrape completed");
    } catch (error: any) {
      notify.error(error?.message || "Scrape failed");
    } finally {
      setIsScraping(false);
    }
  }

  return (
    <div ref={pageRef} className="max-w-5xl mx-auto pb-12" style={{ opacity: 0 }}>
      {/* Header */}
      <PageHeader
        moduleCode="HELP"
        descriptor="SUPPORT"
        title="Help Center"
        subtitle="Everything you need to master RaptorFlow and dominate your market."
      />

      {/* Search */}
      <div className="relative max-w-xl mb-12">
        <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--ink-muted)]" />
        <input
          type="text"
          placeholder="Search documentation, FAQs, tutorials..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full h-12 pl-12 pr-5 text-base bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] text-[var(--ink)] placeholder:text-[var(--ink-muted)] focus:outline-none focus:border-[var(--blueprint)] transition-colors"
        />
      </div>

      {/* Quick Links Grid */}
      <div className="mb-12">
        <h2 className="text-2xl font-semibold text-[var(--ink)] mb-6">Quick Links</h2>
        <div className="grid grid-cols-3 gap-4">
          {QUICK_LINKS.map((link, i) => {
            const Icon = link.icon;
            return (
              <div
                key={i}
                onClick={() => {
                  window.location.href = link.href;
                }}
                className="group p-6 bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] hover:border-[var(--blueprint)] hover:shadow-md transition-all cursor-pointer"
              >
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-[var(--surface)] rounded-[var(--radius)] text-[var(--ink-muted)] group-hover:bg-[var(--blueprint-light)] group-hover:text-[var(--blueprint)] transition-colors">
                    <Icon size={24} strokeWidth={1.5} />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-[var(--ink)] mb-1 group-hover:text-[var(--blueprint)] transition-colors">
                      {link.title}
                    </h3>
                    <p className="text-sm text-[var(--ink-secondary)]">{link.desc}</p>
                  </div>
                  <ArrowRight size={16} className="text-[var(--ink-muted)] opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all mt-1" />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* FAQ Section */}
      <div className="mb-12">
        <h2 className="text-2xl font-semibold text-[var(--ink)] mb-6">
          Frequently Asked Questions
          {searchQuery && <span className="text-base text-[var(--ink-muted)] font-normal ml-2">({filteredFaqs.length} results)</span>}
        </h2>
        <div className="space-y-3">
          {filteredFaqs.map((faq, i) => (
            <div
              key={i}
              className="bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] overflow-hidden"
            >
              <button
                onClick={() => setOpenFaq(openFaq === i ? null : i)}
                className="w-full flex items-center justify-between p-5 text-left hover:bg-[var(--surface)] transition-colors"
              >
                <span className="font-medium text-[var(--ink)]">{faq.q}</span>
                {openFaq === i ? (
                  <ChevronUp size={18} className="text-[var(--ink-muted)]" />
                ) : (
                  <ChevronDown size={18} className="text-[var(--ink-muted)]" />
                )}
              </button>
              {openFaq === i && (
                <div className="px-5 pb-5 text-[var(--ink-secondary)] leading-relaxed animate-in slide-in-from-top-2 duration-200">
                  {faq.a}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* AI Runtime Lab */}
      <div className="mb-12 space-y-5">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-semibold text-[var(--ink)]">AI Runtime Lab</h2>
            <p className="text-sm text-[var(--ink-secondary)]">
              Validate `single/council/swarm` and low/medium/high behavior for search and scraper.
            </p>
          </div>
          <div className="text-xs text-[var(--ink-muted)] font-mono">
            Workspace: {workspaceId || "uninitialized"}
          </div>
        </div>

        <BlueprintCard showCorners padding="lg" className="space-y-6">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-1 rounded-[var(--radius)] border border-[var(--border)] p-1">
              {(["low", "medium", "high"] as const).map((level) => (
                <button
                  key={level}
                  onClick={() => setRuntimeIntensity(level)}
                  className={`px-2 py-1 text-xs rounded-[var(--radius)] uppercase tracking-wide ${
                    runtimeIntensity === level
                      ? "bg-[var(--blueprint)] text-[var(--paper)]"
                      : "text-[var(--muted)] hover:text-[var(--ink)]"
                  }`}
                >
                  {level}
                </button>
              ))}
            </div>
            <div className="flex items-center gap-1 rounded-[var(--radius)] border border-[var(--border)] p-1">
              {(["single", "council", "swarm"] as const).map((mode) => (
                <button
                  key={mode}
                  onClick={() => setRuntimeMode(mode)}
                  className={`px-2 py-1 text-xs rounded-[var(--radius)] uppercase tracking-wide ${
                    runtimeMode === mode
                      ? "bg-[var(--ink)] text-[var(--paper)]"
                      : "text-[var(--muted)] hover:text-[var(--ink)]"
                  }`}
                >
                  {mode}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h3 className="font-semibold text-[var(--ink)]">Web Search (Vertex summary)</h3>
              <div className="flex gap-2">
                <input
                  value={labSearchQuery}
                  onChange={(event) => setLabSearchQuery(event.target.value)}
                  placeholder="e.g. vertex ai model pricing 2026"
                  className="flex-1 h-10 px-3 bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] text-sm"
                />
                <BlueprintButton
                  className="h-10 px-4"
                  onClick={() => void runSearchLab()}
                  disabled={isSearching}
                >
                  {isSearching ? "Running..." : "Run"}
                </BlueprintButton>
              </div>
              {labSearchResult ? (
                <div className="text-xs text-[var(--ink-muted)] space-y-2 border border-[var(--structure-subtle)] rounded-[var(--radius)] p-3 bg-[var(--surface)]">
                  <div>
                    Results: <span className="text-[var(--ink)]">{labSearchResult.total_results}</span> |
                    Engines: <span className="text-[var(--ink)]"> {labSearchResult.engines_used.join(", ")}</span>
                  </div>
                  {labSearchResult.summary?.text ? (
                    <p className="text-[var(--ink-secondary)] whitespace-pre-wrap">{labSearchResult.summary.text}</p>
                  ) : (
                    <p>No summary returned.</p>
                  )}
                </div>
              ) : null}
            </div>

            <div className="space-y-3">
              <h3 className="font-semibold text-[var(--ink)]">Scraper (profile-driven)</h3>
              <div className="flex gap-2">
                <input
                  value={labScrapeUrl}
                  onChange={(event) => setLabScrapeUrl(event.target.value)}
                  placeholder="https://example.com"
                  className="flex-1 h-10 px-3 bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] text-sm"
                />
                <BlueprintButton
                  className="h-10 px-4"
                  onClick={() => void runScraperLab()}
                  disabled={isScraping}
                >
                  {isScraping ? "Running..." : "Run"}
                </BlueprintButton>
              </div>
              {labScrapeResult ? (
                <div className="text-xs text-[var(--ink-muted)] space-y-2 border border-[var(--structure-subtle)] rounded-[var(--radius)] p-3 bg-[var(--surface)]">
                  <div>
                    Status: <span className="text-[var(--ink)]">{labScrapeResult.status}</span> |
                    Strategy: <span className="text-[var(--ink)]"> {labScrapeResult.strategy}</span>
                  </div>
                  {labScrapeResult.title ? (
                    <p className="text-[var(--ink-secondary)]">
                      <span className="font-medium">Title:</span> {labScrapeResult.title}
                    </p>
                  ) : null}
                </div>
              ) : null}
            </div>
          </div>
        </BlueprintCard>
      </div>

      {/* Contact Section */}
      <BlueprintCard showCorners padding="lg" className="bg-gradient-to-br from-[var(--surface)] to-[var(--paper)]">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-2xl font-semibold text-[var(--ink)] mb-2">Still need help?</h3>
            <p className="text-[var(--ink-secondary)]">Our team typically responds within 2 hours during business hours.</p>
          </div>
          <div className="flex gap-4">
            <SecondaryButton className="h-12 px-6" onClick={() => notify.info("Connecting to live chat...", "Support agents are currently busy.")}>
              <MessageCircle size={18} />
              Live Chat
            </SecondaryButton>
            <BlueprintButton className="h-12 px-6" onClick={() => {
              window.open("mailto:support@raptorflow.ai");
              notify.success("Email client opened");
            }}>
              <Mail size={18} />
              Email Support
              <ArrowRight size={16} />
            </BlueprintButton>
          </div>
        </div>
      </BlueprintCard>

      {/* Footer */}
      <div className="mt-16 pt-8 border-t border-[var(--structure-subtle)] flex items-center justify-between text-sm text-[var(--ink-muted)]">
        <span>RaptorFlow v2.0 Documentation</span>
        <div className="flex items-center gap-4">
          <a href="#" className="hover:text-[var(--ink)] transition-colors flex items-center gap-1.5">
            <ExternalLink size={14} />
            API Reference
          </a>
          <a href="#" className="hover:text-[var(--ink)] transition-colors flex items-center gap-1.5">
            <LinkIcon size={14} />
            Status Page
          </a>
          <a href="#" className="hover:text-[var(--ink)] transition-colors flex items-center gap-1.5">
            <Users size={14} />
            Community
          </a>
        </div>
      </div>
    </div>
  );
}

