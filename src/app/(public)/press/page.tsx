"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Link from "next/link";
import { Logo } from "@/components/brand";
import { Card } from "@/components/raptor/ui/Card";
import { Button } from "@/components/raptor/ui/Button";
import {
  Download,
  Newspaper,
  Image as ImageIcon,
  FileText,
  Mail,
  Calendar,
  MapPin,
  Users,
  Target,
  Sparkles,
  ArrowRight,
  ExternalLink,
  Quote,
  Camera,
  Check,
  ChevronDown,
  Twitter,
  Linkedin,
  Copy
} from "lucide-react";

gsap.registerPlugin(ScrollTrigger);

// ═══════════════════════════════════════════════════════════════════════════════
// PRESS KIT — RaptorFlow Media Center
// Comprehensive press release with artwork, animations, and downloadable assets
// ═══════════════════════════════════════════════════════════════════════════════

const COMPANY_STATS = [
  { label: "Founded", value: "2024", icon: Calendar },
  { label: "HQ", value: "Delaware, USA", icon: MapPin },
  { label: "Team", value: "12", icon: Users },
  { label: "Beta Users", value: "500+", icon: Target },
];

const MILESTONES = [
  { date: "Nov 2024", event: "Company Founded", highlight: false },
  { date: "Jan 2025", event: "Private Beta Launch", highlight: false },
  { date: "Feb 2025", event: "Public Beta Release", highlight: true },
  { date: "Q2 2025", event: "Series A & V1.0", highlight: false },
];

const PRESS_COVERAGE = [
  { outlet: "TechCrunch", title: "RaptorFlow wants to be the OS for marketing teams", date: "Feb 2025", link: "#" },
  { outlet: "Product Hunt", title: "#1 Product of the Day — RaptorFlow Beta", date: "Feb 2025", link: "#" },
  { outlet: "SaaStr", title: "Why Modern Marketing Needs an Operating System", date: "Jan 2025", link: "#" },
];

const DOWNLOAD_ASSETS = [
  {
    id: "logo-pack",
    title: "Logo Package",
    description: "SVG, PNG, and EPS formats in all color variations",
    size: "12 MB",
    format: "ZIP",
    icon: ImageIcon,
    items: ["Horizontal Logo", "Stacked Logo", "Icon Only", "Monochrome", "Reversed"]
  },
  {
    id: "brand-guidelines",
    title: "Brand Guidelines",
    description: "Complete brand book with usage rules, colors, and typography",
    size: "8 MB",
    format: "PDF",
    icon: FileText,
    items: ["Color System", "Typography", "Spacing Rules", "Do's & Don'ts", "Applications"]
  },
  {
    id: "press-photos",
    title: "Press Photography",
    description: "High-resolution team photos, office shots, and product screens",
    size: "45 MB",
    format: "ZIP",
    icon: Camera,
    items: ["Founder Portraits", "Team Photos", "Office Shots", "Product UI", "Lifestyle"]
  },
  {
    id: "media-kit",
    title: "Media Kit",
    description: "One-page fact sheet, boilerplate, and founder bios",
    size: "3 MB",
    format: "PDF",
    icon: Newspaper,
    items: ["Fact Sheet", "Boilerplate", "Founder Bio", "Quick Facts", "Quotes"]
  },
];

const FOUNDER_QUOTES = [
  {
    quote: "Marketing isn't a funnel. It's navigation. Every decision is a course correction. RaptorFlow is the compass that keeps you pointed toward truth.",
    author: "Alex Chen",
    role: "Co-founder & CEO"
  },
  {
    quote: "We built RaptorFlow because we were tired of marketing tools that treated strategy like an afterthought. Your foundation should be locked, not lost in a Google Doc.",
    author: "Sarah Kim",
    role: "Co-founder & CTO"
  }
];

export default function PressKitPage() {
  const pageRef = useRef<HTMLDivElement>(null);
  const [copiedText, setCopiedText] = useState<string | null>(null);
  const [expandedAsset, setExpandedAsset] = useState<string | null>(null);

  // Copy to clipboard helper
  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedText(id);
    setTimeout(() => setCopiedText(null), 2000);
  };

  // Entrance animations
  useEffect(() => {
    if (!pageRef.current) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(".press-hero",
        { y: 60, opacity: 0 },
        { y: 0, opacity: 1, duration: 1, ease: "power3.out" }
      );

      gsap.fromTo(".press-section",
        { y: 40, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.8,
          stagger: 0.15,
          ease: "power2.out",
          scrollTrigger: {
            trigger: ".press-content",
            start: "top 80%",
          }
        }
      );

      gsap.fromTo(".timeline-item",
        { x: -30, opacity: 0 },
        {
          x: 0,
          opacity: 1,
          duration: 0.6,
          stagger: 0.1,
          ease: "power2.out",
          scrollTrigger: {
            trigger: ".timeline",
            start: "top 80%",
          }
        }
      );
    }, pageRef);

    return () => ctx.revert();
  }, []);

  const toggleAsset = (id: string) => {
    setExpandedAsset(expandedAsset === id ? null : id);
  };

  return (
    <div ref={pageRef} className="min-h-screen bg-[#F3F0E7]">
      {/* Reading Progress */}
      <div className="fixed top-16 left-0 right-0 h-1 bg-[#E3DED3] z-40">
        <div className="h-full bg-[#2A2529] transition-all duration-150" style={{ width: "0%" }} />
      </div>

      {/* Hero Section */}
      <section className="press-hero relative pt-32 pb-20 px-6 overflow-hidden">
        <div className="absolute top-20 left-10 w-64 h-64 bg-[#2A2529]/5 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-[#8B6914]/5 rounded-full blur-3xl" />
        
        <div className="max-w-5xl mx-auto relative">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-[#F7F5EF] border border-[#E3DED3] rounded-full mb-8">
            <Newspaper size={16} className="text-[#8B6914]" />
            <span className="rf-mono-xs text-[#5C565B] uppercase tracking-wider">Press Center</span>
          </div>

          <h1 className="rf-display text-5xl md:text-7xl mb-6 leading-tight">
            <span className="text-[#2A2529]">The Story of</span>
            <br />
            <span className="relative inline-block text-[#2A2529]">
              RaptorFlow
              <svg className="absolute -bottom-2 left-0 w-full" height="8" viewBox="0 0 200 8" preserveAspectRatio="none">
                <path d="M0,4 Q50,0 100,4 T200,4" fill="none" stroke="#8B6914" strokeWidth="3" />
              </svg>
            </span>
          </h1>

          <p className="rf-body text-[#5C565B] text-xl max-w-2xl mb-8 leading-relaxed">
            We&apos;re building the marketing operating system for operators who demand precision. 
            Here&apos;s everything you need to tell our story.
          </p>

          <div className="flex flex-wrap gap-4">
            <Button variant="primary" leftIcon={<Download size={18} />} className="bg-[#2A2529] text-[#F3F0E7]">
              Download Full Press Kit
            </Button>
            <Button variant="secondary" leftIcon={<Mail size={18} />}>
              Contact Press Team
            </Button>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <div className="press-content max-w-6xl mx-auto px-6 pb-24 space-y-24">
        
        {/* Company Stats */}
        <section className="press-section">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {COMPANY_STATS.map((stat, idx) => {
              const Icon = stat.icon;
              return (
                <Card key={idx} padding="lg" className="text-center group hover:border-[#8B6914] transition-colors">
                  <div className="w-12 h-12 mx-auto mb-4 rounded-lg bg-[#F7F5EF] flex items-center justify-center group-hover:bg-[#8B6914]/10 transition-colors">
                    <Icon size={24} className="text-[#8B6914]" />
                  </div>
                  <div className="rf-h2 text-[#2A2529] mb-1">{stat.value}</div>
                  <div className="rf-body-sm text-[#5C565B]">{stat.label}</div>
                </Card>
              );
            })}
          </div>
        </section>

        {/* Press Release */}
        <section className="press-section">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-lg bg-[#2A2529] flex items-center justify-center">
              <Newspaper size={20} className="text-[#F3F0E7]" />
            </div>
            <div>
              <h2 className="rf-h3 text-[#2A2529]">Press Release</h2>
              <p className="rf-mono-xs text-[#5C565B]">FOR IMMEDIATE RELEASE — February 13, 2025</p>
            </div>
          </div>

          <Card padding="lg" className="relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-[#8B6914]/10 to-transparent" />
            
            <article className="prose prose-lg max-w-none">
              <h3 className="rf-h2 text-[#2A2529] mb-6">
                RaptorFlow Launches Public Beta, Redefining How Marketing Teams Build and Execute Strategy
              </h3>

              <div className="rf-body text-[#5C565B] space-y-6">
                <p className="font-medium text-[#2A2529]">
                  <strong>WILMINGTON, Del.</strong> — RaptorFlow, the marketing operating system designed for precision-focused operators, today announced the launch of its public beta. The platform introduces a radical new approach to marketing management: treating strategy as immutable truth that guides every tactical decision.
                </p>

                <p>
                  Traditional marketing tools treat strategy as an afterthought—buried in slide decks, lost in shared drives, or forgotten after the kickoff meeting. RaptorFlow inverts this model. The Foundation module locks positioning, ideal customer profiles (ICPs), and messaging into a synthesized &ldquo;Business Context Manifest&rdquo; (BCM) that powers every subsequent action.
                </p>

                <blockquote className="border-l-4 border-[#8B6914] pl-6 py-2 my-8 bg-[#F7F5EF] rounded-r-lg">
                  <p className="rf-body text-[#2A2529] italic mb-4">
                    &ldquo;Marketing isn&apos;t a funnel. It&apos;s navigation through uncertain terrain. Every campaign is a course correction. RaptorFlow is the compass that keeps you pointed toward truth.&rdquo;
                  </p>
                  <footer className="rf-body-sm text-[#5C565B]">
                    — Alex Chen, Co-founder & CEO
                  </footer>
                </blockquote>

                <p>
                  The platform&apos;s core innovation is the relationship between three modules:
                </p>

                <ul className="space-y-3 my-6">
                  <li className="flex items-start gap-3">
                    <span className="w-2 h-2 rounded-full bg-[#8B6914] mt-2 flex-shrink-0" />
                    <span><strong>Foundation</strong> — Lock positioning, ICPs, and messaging. Version-controlled, always reversible, permanently referenceable.</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="w-2 h-2 rounded-full bg-[#8B6914] mt-2 flex-shrink-0" />
                    <span><strong>Moves</strong> — 14-day strategic sprints across five categories: Ignite (launches), Capture (acquisition), Authority (thought leadership), Repair (crisis), and Rally (community).</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="w-2 h-2 rounded-full bg-[#8B6914] mt-2 flex-shrink-0" />
                    <span><strong>Muse</strong> — Context-aware AI that reads your Foundation and suggests moves, never publishing without explicit approval.</span>
                  </li>
                </ul>

                <p>
                  Unlike generic AI marketing tools, Muse doesn&apos;t generate content in a vacuum. It understands your value proposition, your ICP&apos;s pain points, and your brand voice—because they&apos;re locked in your Foundation. Suggestions appear in a &ldquo;Proposal Drawer&rdquo; for review, editing, and one-click acceptance or dismissal.
                </p>

                <p>
                  RaptorFlow is built on the philosophy of &ldquo;Cockpit + Autopilot.&rdquo; The operator (you) sits in the cockpit, seeing options, tradeoffs, and confidence scores. The AI handles the grinding—execution checklists, content drafts, progress tracking. But you lock the strategy. You approve every publish. You maintain full reversibility.
                </p>

                <p>
                  The public beta follows a successful private beta with 500+ marketing operators from early-stage SaaS companies. Users report a 40% reduction in time spent on campaign planning and a 3x increase in strategic clarity.
                </p>

                <p>
                  &ldquo;Before RaptorFlow, our positioning lived in a Notion doc nobody read,&rdquo; said Sarah Miller, Head of Marketing at Vertex AI. &ldquo;Now it&apos;s locked, Muse knows it, and every campaign brief starts from that truth. It&apos;s like having a strategic compass that actually works.&rdquo;
                </p>

                <p>
                  RaptorFlow is available now in public beta at raptorflow.ai. Core features are free forever. Premium features, including advanced Muse capabilities and team collaboration tools, will be announced with the v1.0 release in Q2 2025.
                </p>

                <div className="border-t border-[#E3DED3] pt-6 mt-8">
                  <h4 className="rf-h4 text-[#2A2529] mb-4">About RaptorFlow</h4>
                  <p>
                    RaptorFlow is the marketing operating system for operators who demand precision. Founded in 2024 by Alex Chen and Sarah Kim, the company is headquartered in Delaware with a distributed team across North America.
                  </p>
                </div>

                <div className="border-t border-[#E3DED3] pt-6 mt-8">
                  <h4 className="rf-h4 text-[#2A2529] mb-4">Media Contact</h4>
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-lg bg-[#F7F5EF] flex items-center justify-center">
                      <Mail size={20} className="text-[#8B6914]" />
                    </div>
                    <div>
                      <p className="rf-body font-medium text-[#2A2529]">Press Team</p>
                      <a href="mailto:press@raptorflow.ai" className="rf-body text-[#8B6914] hover:underline">
                        press@raptorflow.ai
                      </a>
                    </div>
                    <button
                      onClick={() => copyToClipboard("press@raptorflow.ai", "press-email")}
                      className="ml-auto p-2 rounded-lg hover:bg-[#F7F5EF] transition-colors"
                    >
                      {copiedText === "press-email" ? (
                        <Check size={18} className="text-green-600" />
                      ) : (
                        <Copy size={18} className="text-[#5C565B]" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </article>
          </Card>
        </section>

        {/* Timeline */}
        <section className="press-section">
          <h2 className="rf-h3 text-[#2A2529] mb-8">Company Timeline</h2>
          <div className="timeline relative">
            <div className="absolute left-4 top-0 bottom-0 w-px bg-[#E3DED3]" />
            
            <div className="space-y-8">
              {MILESTONES.map((milestone, idx) => (
                <div key={idx} className="timeline-item relative pl-12">
                  <div className={`absolute left-2 top-1 w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                    milestone.highlight 
                      ? "bg-[#8B6914] border-[#8B6914]" 
                      : "bg-[#F3F0E7] border-[#D2CCC0]"
                  }`}>
                    {milestone.highlight && <Sparkles size={12} className="text-white" />}
                  </div>
                  <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-6">
                    <span className="rf-mono-sm text-[#8B6914] w-24 flex-shrink-0">{milestone.date}</span>
                    <span className={`rf-body ${milestone.highlight ? "font-semibold text-[#2A2529]" : "text-[#5C565B]"}`}>
                      {milestone.event}
                    </span>
                    {milestone.highlight && (
                      <span className="ml-auto px-3 py-1 bg-[#8B6914]/10 text-[#8B6914] text-xs rounded-full">
                        Latest
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Founder Quotes */}
        <section className="press-section">
          <h2 className="rf-h3 text-[#2A2529] mb-8">From the Founders</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {FOUNDER_QUOTES.map((quote, idx) => (
              <Card key={idx} padding="lg" className="relative overflow-hidden">
                <Quote size={32} className="absolute top-6 right-6 text-[#E3DED3]" />
                <blockquote className="relative">
                  <p className="rf-body text-[#2A2529] italic mb-6 leading-relaxed">
                    &ldquo;{quote.quote}&rdquo;
                  </p>
                  <footer className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-[#F7F5EF] flex items-center justify-center">
                      <span className="rf-mono-sm font-bold text-[#8B6914]">
                        {quote.author.split(" ").map(n => n[0]).join("")}
                      </span>
                    </div>
                    <div>
                      <p className="rf-body font-semibold text-[#2A2529]">{quote.author}</p>
                      <p className="rf-body-sm text-[#5C565B]">{quote.role}</p>
                    </div>
                  </footer>
                </blockquote>
              </Card>
            ))}
          </div>
        </section>

        {/* Press Coverage */}
        <section className="press-section">
          <h2 className="rf-h3 text-[#2A2529] mb-8">Press Coverage</h2>
          <div className="space-y-4">
            {PRESS_COVERAGE.map((article, idx) => (
              <a
                key={idx}
                href={article.link}
                className="flex items-center gap-6 p-6 bg-[#F7F5EF] rounded-xl hover:bg-[#EDE9E0] transition-colors group"
              >
                <div className="w-16 h-16 rounded-lg bg-[#2A2529] flex items-center justify-center flex-shrink-0">
                  <span className="rf-mono-xs font-bold text-[#F3F0E7]">
                    {article.outlet.substring(0, 2).toUpperCase()}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="rf-mono-xs text-[#8B6914] uppercase tracking-wider mb-1">{article.outlet}</p>
                  <h3 className="rf-body font-semibold text-[#2A2529] group-hover:text-[#8B6914] transition-colors truncate">
                    {article.title}
                  </h3>
                </div>
                <div className="flex items-center gap-4">
                  <span className="rf-mono-xs text-[#5C565B] hidden sm:block">{article.date}</span>
                  <ExternalLink size={18} className="text-[#5C565B] group-hover:text-[#8B6914] transition-colors" />
                </div>
              </a>
            ))}
          </div>
        </section>

        {/* Download Assets */}
        <section className="press-section">
          <div className="flex items-center justify-between mb-8">
            <h2 className="rf-h3 text-[#2A2529]">Download Assets</h2>
            <Button variant="secondary" leftIcon={<Download size={16} />}>
              Download All
            </Button>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {DOWNLOAD_ASSETS.map((asset) => {
              const Icon = asset.icon;
              const isExpanded = expandedAsset === asset.id;
              
              return (
                <Card key={asset.id} padding="none" className="overflow-hidden">
                  <button
                    onClick={() => toggleAsset(asset.id)}
                    className="w-full p-6 flex items-start gap-4 text-left"
                  >
                    <div className="w-14 h-14 rounded-xl bg-[#F7F5EF] flex items-center justify-center flex-shrink-0">
                      <Icon size={28} className="text-[#8B6914]" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <h3 className="rf-h4 text-[#2A2529] mb-1">{asset.title}</h3>
                          <p className="rf-body-sm text-[#5C565B] mb-2">{asset.description}</p>
                          <div className="flex items-center gap-3">
                            <span className="rf-mono-xs px-2 py-1 bg-[#E3DED3] rounded text-[#5C565B]">{asset.format}</span>
                            <span className="rf-mono-xs text-[#5C565B]">{asset.size}</span>
                          </div>
                        </div>
                        <ChevronDown 
                          size={20} 
                          className={`text-[#5C565B] flex-shrink-0 transition-transform ${isExpanded ? "rotate-180" : ""}`} 
                        />
                      </div>
                    </div>
                  </button>
                  
                  {isExpanded && (
                    <div className="px-6 pb-6">
                      <div className="h-px bg-[#E3DED3] mb-4" />
                      <p className="rf-label text-[#5C565B] mb-3">Includes:</p>
                      <ul className="space-y-2 mb-6">
                        {asset.items.map((item, idx) => (
                          <li key={idx} className="flex items-center gap-2 rf-body-sm text-[#2A2529]">
                            <Check size={14} className="text-[#8B6914]" />
                            {item}
                          </li>
                        ))}
                      </ul>
                      <Button variant="primary" leftIcon={<Download size={16} />} className="w-full bg-[#2A2529] text-[#F3F0E7]">
                        Download {asset.title}
                      </Button>
                    </div>
                  )}
                </Card>
              );
            })}
          </div>
        </section>

        {/* Social Links */}
        <section className="press-section">
          <h2 className="rf-h3 text-[#2A2529] mb-8">Follow Us</h2>
          <div className="flex flex-wrap gap-4">
            {[
              { name: "Twitter / X", icon: Twitter, href: "https://twitter.com/raptorflow", handle: "@raptorflow" },
              { name: "LinkedIn", icon: Linkedin, href: "https://linkedin.com/company/raptorflow", handle: "/company/raptorflow" },
            ].map((social, idx) => {
              const Icon = social.icon;
              return (
                <a
                  key={idx}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-4 px-6 py-4 bg-[#F7F5EF] rounded-xl hover:bg-[#EDE9E0] transition-colors group flex-1 min-w-[200px]"
                >
                  <div className="w-12 h-12 rounded-lg bg-[#2A2529] flex items-center justify-center group-hover:bg-[#8B6914] transition-colors">
                    <Icon size={24} className="text-[#F3F0E7]" />
                  </div>
                  <div>
                    <p className="rf-body font-semibold text-[#2A2529]">{social.name}</p>
                    <p className="rf-mono-xs text-[#5C565B]">{social.handle}</p>
                  </div>
                  <ArrowRight size={18} className="ml-auto text-[#5C565B] group-hover:text-[#8B6914] transition-colors" />
                </a>
              );
            })}
          </div>
        </section>

        {/* Final CTA */}
        <section className="press-section">
          <Card padding="lg" className="bg-gradient-to-br from-[#2A2529] to-[#3A3539] text-[#F3F0E7] text-center">
            <div className="max-w-2xl mx-auto">
              <h2 className="rf-h2 mb-4">Ready to cover RaptorFlow?</h2>
              <p className="rf-body text-[#D2CCC0] mb-8">
                We&apos;re always available for interviews, demos, and deep dives. 
                Reach out to our press team for exclusive access.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Button variant="primary" leftIcon={<Mail size={18} />} className="bg-[#F3F0E7] text-[#2A2529] hover:bg-[#E3DED3]">
                  Email Press Team
                </Button>
                <Button variant="secondary" className="border-[#F3F0E7] text-[#F3F0E7] hover:bg-[#F3F0E7]/10">
                  Schedule a Demo
                </Button>
              </div>
            </div>
          </Card>
        </section>
      </div>

      {/* Footer */}
      <footer className="border-t border-[#E3DED3] bg-[#F7F5EF] py-12 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <Link href="/" className="flex items-center gap-2">
            <Logo size={28} />
            <span className="font-semibold text-[#2A2529]">RaptorFlow</span>
          </Link>
          <p className="rf-mono-xs text-[#5C565B] text-center">
            © 2025 RaptorFlow, Inc. Press materials may be used with attribution.
          </p>
          <div className="flex items-center gap-6">
            <Link href="/legal/privacy" className="rf-mono-xs text-[#5C565B] hover:text-[#2A2529]">Privacy</Link>
            <Link href="/legal/terms" className="rf-mono-xs text-[#5C565B] hover:text-[#2A2529]">Terms</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
