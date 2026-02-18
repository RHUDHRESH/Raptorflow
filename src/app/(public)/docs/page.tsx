"use client";

import { useEffect, useRef, useState, useMemo } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
// Public docs page - no workspace required
import { Card } from "@/components/raptor/ui/Card";
import { Button } from "@/components/raptor/ui/Button";
import { 
  Search, 
  BookOpen, 
  Zap, 
  Shield, 
  FileText,
  Code,
  ArrowRight,
  ChevronRight,
  Copy,
  Check,
  Terminal,
  Layers,
  Sparkles,
  ExternalLink
} from "lucide-react";

gsap.registerPlugin(ScrollTrigger);

// ═══════════════════════════════════════════════════════════════════════════════
// DOCUMENTATION — Comprehensive Guide with Radical Animations
// Search, code blocks, interactive examples
// ═══════════════════════════════════════════════════════════════════════════════

const DOC_SECTIONS = [
  {
    id: "getting-started",
    icon: Zap,
    title: "Getting Started",
    description: "Quickstart, installation, and core concepts",
    color: "#3D5A42",
    articles: ["Quickstart", "Installation", "Core Concepts", "First Steps"],
  },
  {
    id: "foundation",
    icon: Shield,
    title: "Foundation",
    description: "Positioning, ICPs, messaging, and BCM",
    color: "#3D5A6B",
    articles: ["Positioning Statement", "Rich ICPs", "Core Messaging", "BCM Guide"],
  },
  {
    id: "moves",
    icon: FileText,
    title: "Strategic Moves",
    description: "Creating and executing marketing sprints",
    color: "#8B6914",
    articles: ["Move Categories", "14-Day Sprints", "Execution", "Tracking"],
  },
  {
    id: "muse",
    icon: Sparkles,
    title: "Muse AI",
    description: "AI assistant and content generation",
    color: "#6B3D5A",
    articles: ["Context Awareness", "Prompts", "Proposals", "Best Practices"],
  },
  {
    id: "api",
    icon: Code,
    title: "API Reference",
    description: "REST API endpoints and authentication",
    color: "#2A2529",
    articles: ["Authentication", "Endpoints", "Webhooks", "Rate Limits"],
  },
  {
    id: "advanced",
    icon: Layers,
    title: "Advanced",
    description: "Integrations, webhooks, and customization",
    color: "#5A4A3A",
    articles: ["Integrations", "Webhooks", "Custom Fields", "Export"],
  },
];

const CODE_EXAMPLES = [
  {
    id: "auth",
    title: "Authentication",
    language: "bash",
    code: `curl -X POST https://api.raptorflow.ai/v1/auth/token \\
  -H "Content-Type: application/json" \\
  -d '{
    "api_key": "your_api_key_here"
  }'`,
  },
  {
    id: "create-move",
    title: "Create a Move",
    language: "javascript",
    code: `const move = await raptorflow.moves.create({
  workspaceId: "ws_123",
  category: "ignite",
  name: "Product Launch Sprint",
  goal: "Generate 1000 signups",
  duration: 14,
  context: {
    product: "SaaS Analytics Platform",
    target: "Data-driven marketers"
  }
});`,
  },
  {
    id: "foundation-query",
    title: "Query Foundation",
    language: "javascript",
    code: `const foundation = await raptorflow.foundation.get({
  workspaceId: "ws_123"
});

console.log(foundation.positioning);
console.log(foundation.icps);
console.log(foundation.messaging);`,
  },
];

const QUICK_START_STEPS = [
  {
    number: "01",
    title: "Create Workspace",
    description: "Set up your first workspace and invite your team",
    action: "Get Started",
    href: "/onboarding",
  },
  {
    number: "02",
    title: "Build Foundation",
    description: "Define your positioning, ICPs, and messaging",
    action: "Open Foundation",
    href: "/foundation",
  },
  {
    number: "03",
    title: "Create First Move",
    description: "Launch a 14-day strategic marketing sprint",
    action: "Create Move",
    href: "/moves",
  },
  {
    number: "04",
    title: "Ask Muse",
    description: "Get AI-powered suggestions based on your context",
    action: "Open Muse",
    href: "/muse",
  },
];

export default function DocsPage() {
  const pageRef = useRef<HTMLDivElement>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  const [activeCodeTab, setActiveCodeTab] = useState("auth");
  const [readingProgress, setReadingProgress] = useState(0);

  // Reading progress
  useEffect(() => {
    const handleScroll = () => {
      const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = (window.scrollY / totalHeight) * 100;
      setReadingProgress(Math.min(progress, 100));
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Filter sections based on search
  const filteredSections = useMemo(() => {
    if (!searchQuery.trim()) return DOC_SECTIONS;
    const q = searchQuery.toLowerCase();
    return DOC_SECTIONS.filter(
      (s) =>
        s.title.toLowerCase().includes(q) ||
        s.description.toLowerCase().includes(q) ||
        s.articles.some((a) => a.toLowerCase().includes(q))
    );
  }, [searchQuery]);

  // Entrance animations
  useEffect(() => {
    if (!pageRef.current) return;

    const ctx = gsap.context(() => {
      // Hero
      gsap.fromTo(
        ".docs-hero",
        { y: 40, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.8, ease: "power3.out" }
      );

      // Search
      gsap.fromTo(
        ".docs-search",
        { scale: 0.95, opacity: 0 },
        { scale: 1, opacity: 1, duration: 0.6, delay: 0.2, ease: "back.out(1.5)" }
      );

      // Quick start steps
      gsap.fromTo(
        ".quick-step",
        { x: -30, opacity: 0 },
        {
          x: 0,
          opacity: 1,
          duration: 0.5,
          stagger: 0.1,
          delay: 0.3,
          ease: "power2.out",
        }
      );

      // Code example
      gsap.fromTo(
        ".code-example",
        { y: 30, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.6,
          delay: 0.5,
          ease: "power2.out",
        }
      );

      // Category cards
      gsap.fromTo(
        ".doc-card",
        { y: 40, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.5,
          stagger: 0.08,
          delay: 0.6,
          ease: "power2.out",
          scrollTrigger: {
            trigger: ".doc-cards-grid",
            start: "top 80%",
          },
        }
      );
    }, pageRef);

    return () => ctx.revert();
  }, []);

  const copyCode = (id: string, code: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(id);
    gsap.fromTo(
      `[data-copy-icon="${id}"]`,
      { scale: 0.8 },
      { scale: 1, duration: 0.3, ease: "back.out(2)" }
    );
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const activeCodeExample = CODE_EXAMPLES.find((c) => c.id === activeCodeTab);

  return (
    <>
      {/* Reading Progress Bar */}
      <div className="fixed top-16 left-0 right-0 h-1 bg-[var(--border-1)] z-40">
        <div
          className="h-full bg-[var(--ink-1)] transition-all duration-150"
          style={{ width: `${readingProgress}%` }}
        />
      </div>

      <div ref={pageRef} className="max-w-6xl mx-auto pb-24">
        {/* Hero Section */}
        <div className="docs-hero text-center mb-12 pt-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-[var(--bg-canvas)] rounded-full mb-6">
            <BookOpen size={16} className="text-[var(--ink-2)]" />
            <span className="rf-mono-xs text-[var(--ink-2)] uppercase tracking-wider">
              Documentation
            </span>
          </div>
          <h1 className="rf-display mb-4">RaptorFlow Docs</h1>
          <p className="rf-body-lg text-[var(--ink-2)] max-w-2xl mx-auto">
            Everything you need to build, execute, and scale your marketing with confidence.
          </p>
        </div>

        {/* Search Bar */}
        <div className="docs-search max-w-2xl mx-auto mb-16">
          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-[var(--ink-1)]/5 to-transparent rounded-[var(--radius-lg)] opacity-0 group-focus-within:opacity-100 transition-opacity duration-300" />
            <div className="relative flex items-center bg-[var(--bg-surface)] border border-[var(--border-1)] rounded-[var(--radius-lg)] shadow-sm focus-within:shadow-md focus-within:border-[var(--ink-1)] transition-all duration-300">
              <Search 
                size={20} 
                className="ml-4 text-[var(--ink-3)] group-focus-within:text-[var(--ink-1)] transition-colors" 
              />
              <input
                type="text"
                placeholder="Search documentation..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 px-4 py-4 bg-transparent rf-body outline-none placeholder:text-[var(--ink-3)]"
              />
              <div className="mr-4 px-2 py-1 bg-[var(--bg-canvas)] rounded-[var(--radius-sm)]">
                <span className="rf-mono-xs text-[var(--ink-3)]">⌘K</span>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Start Section */}
        {!searchQuery && (
          <div className="mb-16">
            <div className="flex items-center gap-3 mb-8">
              <Terminal size={20} className="text-[var(--ink-2)]" />
              <h2 className="rf-h3">Quick Start</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {QUICK_START_STEPS.map((step, idx) => (
                <div
                  key={step.number}
                  className="quick-step group relative p-6 bg-[var(--bg-surface)] border border-[var(--border-1)] rounded-[var(--radius-md)] hover:border-[var(--ink-1)] transition-all duration-300 hover:-translate-y-1"
                >
                  <span className="absolute top-4 right-4 rf-mono-xs text-[var(--border-2)] group-hover:text-[var(--ink-1)] transition-colors">
                    {step.number}
                  </span>
                  <h3 className="rf-h4 mb-2 group-hover:text-[var(--ink-1)] transition-colors">
                    {step.title}
                  </h3>
                  <p className="rf-body-sm text-[var(--ink-2)] mb-4">
                    {step.description}
                  </p>
                  <a
                    href={step.href}
                    className="inline-flex items-center gap-2 rf-body-sm font-medium text-[var(--ink-1)] hover:gap-3 transition-all"
                  >
                    {step.action}
                    <ArrowRight size={14} />
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Code Example Section */}
        {!searchQuery && (
          <div className="code-example mb-16">
            <div className="flex items-center gap-3 mb-6">
              <Code size={20} className="text-[var(--ink-2)]" />
              <h2 className="rf-h3">API Quick Reference</h2>
            </div>

            <Card padding="none" className="overflow-hidden">
              {/* Tabs */}
              <div className="flex items-center gap-1 p-2 bg-[var(--bg-canvas)] border-b border-[var(--border-1)]">
                {CODE_EXAMPLES.map((example) => (
                  <button
                    key={example.id}
                    onClick={() => setActiveCodeTab(example.id)}
                    className={`px-4 py-2 rf-body-sm rounded-[var(--radius-sm)] transition-all ${
                      activeCodeTab === example.id
                        ? "bg-[var(--bg-surface)] text-[var(--ink-1)] shadow-sm"
                        : "text-[var(--ink-3)] hover:text-[var(--ink-1)]"
                    }`}
                  >
                    {example.title}
                  </button>
                ))}
              </div>

              {/* Code Block */}
              <div className="relative bg-[#1a1a1a] p-6 overflow-x-auto">
                <button
                  onClick={() => activeCodeExample && copyCode(activeCodeExample.id, activeCodeExample.code)}
                  className="absolute top-4 right-4 p-2 rounded-[var(--radius-sm)] bg-white/10 hover:bg-white/20 transition-colors group"
                >
                  {copiedCode === activeCodeExample?.id ? (
                    <Check size={16} className="text-green-400" data-copy-icon={activeCodeExample?.id} />
                  ) : (
                    <Copy size={16} className="text-white/60 group-hover:text-white" />
                  )}
                </button>
                <pre className="font-mono text-sm text-white/90 leading-relaxed">
                  <code>{activeCodeExample?.code}</code>
                </pre>
              </div>
            </Card>
          </div>
        )}

        {/* Documentation Categories */}
        <div className="doc-cards-grid">
          <div className="flex items-center justify-between mb-6">
            <h2 className="rf-h3">
              {searchQuery ? "Search Results" : "Browse by Topic"}
            </h2>
            {searchQuery && (
              <span className="rf-body-sm text-[var(--ink-3)]">
                {filteredSections.length} result{filteredSections.length !== 1 ? "s" : ""}
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredSections.map((section) => {
              const Icon = section.icon;
              const isSelected = selectedSection === section.id;

              return (
                <div
                  key={section.id}
                  className={`doc-card group relative p-6 rounded-[var(--radius-md)] border transition-all duration-300 cursor-pointer ${
                    isSelected
                      ? "border-[var(--ink-1)] bg-[var(--ink-1)] text-white"
                      : "border-[var(--border-1)] bg-[var(--bg-surface)] hover:border-[var(--border-2)] hover:-translate-y-1"
                  }`}
                  onClick={() => setSelectedSection(isSelected ? null : section.id)}
                >
                  <div
                    className="w-12 h-12 rounded-[var(--radius-sm)] flex items-center justify-center mb-4 transition-all duration-300 group-hover:scale-110"
                    style={{
                      backgroundColor: isSelected
                        ? "rgba(255,255,255,0.2)"
                        : `${section.color}20`,
                    }}
                  >
                    <Icon
                      size={24}
                      style={{ color: isSelected ? "white" : section.color }}
                    />
                  </div>

                  <h3
                    className={`rf-h4 mb-2 flex items-center gap-2 ${
                      isSelected ? "text-white" : ""
                    }`}
                  >
                    {section.title}
                    <ChevronRight
                      size={16}
                      className={`transition-transform duration-300 ${
                        isSelected ? "rotate-90" : "opacity-0 group-hover:opacity-100"
                      }`}
                    />
                  </h3>

                  <p
                    className={`rf-body-sm mb-4 ${
                      isSelected ? "text-white/70" : "text-[var(--ink-2)]"
                    }`}
                  >
                    {section.description}
                  </p>

                  {/* Articles list */}
                  <ul className="space-y-2">
                    {section.articles.map((article) => (
                      <li
                        key={article}
                        className={`rf-body-sm flex items-center gap-2 ${
                          isSelected
                            ? "text-white/60 hover:text-white"
                            : "text-[var(--ink-3)] hover:text-[var(--ink-1)]"
                        } transition-colors`}
                      >
                        <span
                          className={`w-1 h-1 rounded-full ${
                            isSelected ? "bg-white/40" : "bg-[var(--border-2)]"
                          }`}
                        />
                        {article}
                      </li>
                    ))}
                  </ul>

                  {/* Expand indicator */}
                  <div
                    className={`mt-4 pt-4 border-t ${
                      isSelected ? "border-white/20" : "border-[var(--border-1)]"
                    }`}
                  >
                    <span
                      className={`rf-body-sm font-medium flex items-center gap-2 ${
                        isSelected ? "text-white" : "text-[var(--ink-1)]"
                      }`}
                    >
                      View Documentation
                      <ExternalLink size={14} />
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* CTA Section */}
        {!searchQuery && (
          <div className="mt-16 p-8 bg-gradient-to-br from-[var(--ink-1)] to-[var(--ink-2)] rounded-[var(--radius-lg)] text-white text-center">
            <h2 className="rf-h3 mb-3">Need more help?</h2>
            <p className="rf-body text-white/70 mb-6 max-w-md mx-auto">
              Can&apos;t find what you&apos;re looking for? Our support team is here to help.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button
                variant="primary"
                className="bg-white text-[var(--ink-1)] hover:bg-white/90"
                onClick={() => (window.location.href = "/support")}
              >
                Visit Support Center
              </Button>
              <a
                href="mailto:support@raptorflow.ai"
                className="rf-body-sm text-white/70 hover:text-white transition-colors"
              >
                support@raptorflow.ai
              </a>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
