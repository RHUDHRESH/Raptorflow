"use client";

import { useState, useRef, useEffect } from "react";
import gsap from "gsap";
import {
  Search,
  Book,
  MessageCircle,
  Video,
  ArrowRight,
  HelpCircle,
  Zap,
  Target,
  Users,
  BarChart3,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Mail
} from "lucide-react";

import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { PageHeader, PageFooter } from "@/components/ui/PageHeader";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

/* ══════════════════════════════════════════════════════════════════════════════
   HELP CENTER — Comprehensive Documentation & Support
   Full-page layout with search, quick links, FAQs, and contact
   ══════════════════════════════════════════════════════════════════════════════ */

const QUICK_LINKS = [
  { title: "Getting Started", desc: "New to RaptorFlow? Start here.", icon: Book, href: "/welcome" },
  { title: "Moves & Campaigns", desc: "Learn tactical execution", icon: Zap, href: "/moves" },
  { title: "Foundation Setup", desc: "Define your brand positioning", icon: Target, href: "/foundation" },
  { title: "Analytics & Tracking", desc: "Measure what matters", icon: BarChart3, href: "/analytics" },
  { title: "Cohorts & ICPs", desc: "Segment your audience", icon: Users, href: "/foundation#icp" },
  { title: "Video Tutorials", desc: "Watch step-by-step guides", icon: Video, href: "#", action: "coming_soon" },
];

const FAQS = [
  {
    q: "What is RaptorFlow?",
    a: "RaptorFlow is a Marketing Operating System (MOS) designed for founders. It helps you define positioning, create tactical marketing moves, track campaigns, and measure results — all in one place."
  },
  {
    q: "How do Moves work?",
    a: "A Move is a tactical marketing action lasting 3-14 days. You select a category (like Ignite for launches or Defend for retention), set your objective, and RaptorFlow generates a day-by-day execution plan with specific tasks."
  },
  {
    q: "What's the difference between Moves and Campaigns?",
    a: "Campaigns are 90-day strategic arcs that contain multiple Moves. Think of a Campaign as your quarterly strategy, and Moves as the weekly/bi-weekly tactics that execute that strategy."
  },
  {
    q: "Can I track results from external platforms?",
    a: "RaptorFlow tracks channel mix, clicks, CTR, and cost data that flows through our system. For impression-level metrics, you'll need to reference your native platform analytics and manually input key numbers."
  },
  {
    q: "What is the Black Box?",
    a: "Black Box is an experimental move generator. Set your focus area, desired outcome, and volatility level, and it creates high-risk/high-reward tactical suggestions. Great for breaking out of marketing ruts."
  },
  {
    q: "How do Daily Wins work?",
    a: "Daily Wins is a lottery-style content opportunity generator. Spin the wheel to get a trending topic paired with a content template. Execute it immediately for timely, relevant content that rides current waves."
  },
  {
    q: "What is Foundation?",
    a: "Foundation is where you define your marketing fundamentals: positioning statement, ideal customer profiles (ICPs), core messaging, and channel strategy. Everything else in RaptorFlow builds on these foundations."
  },
  {
    q: "Can I export my data?",
    a: "Yes! You can export campaign reports, move execution data, and analytics from their respective sections. Look for the Export button in the header of each module."
  },
];

export default function HelpPage() {
  const pageRef = useRef<HTMLDivElement>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  useEffect(() => {
    if (!pageRef.current) return;
    gsap.fromTo(pageRef.current, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.4, ease: "power2.out" });
  }, []);

  const filteredFaqs = searchQuery
    ? FAQS.filter(f =>
      f.q.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.a.toLowerCase().includes(searchQuery.toLowerCase())
    )
    : FAQS;

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
        <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--ink-muted)]" />
        <input
          type="text"
          placeholder="Search documentation, FAQs, tutorials..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="rf-input w-full h-12 pl-12 pr-5 text-base"
        />
      </div>

      {/* Quick Links Grid */}
      <div className="mb-12">
        <h2 className="font-serif text-2xl text-[var(--ink)] mb-6">Quick Links</h2>
        <div className="grid grid-cols-3 gap-4">
          <div className="grid grid-cols-3 gap-4">
            {QUICK_LINKS.map((link, i) => {
              const Icon = link.icon;
              return (
                <div
                  key={i}
                  onClick={() => {
                    if (link.action === "coming_soon") {
                      toast.info("Video tutorials coming soon!", { description: "Check back later for step-by-step guides." });
                    } else {
                      window.location.href = link.href;
                    }
                  }}
                  className="group p-6 bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] hover:border-[var(--blueprint)] hover:shadow-md transition-all cursor-pointer"
                >
                  <div className="flex items-start gap-4">
                    <div className="p-3 bg-[var(--surface)] rounded-xl text-[var(--ink-muted)] group-hover:bg-[var(--blueprint-light)] group-hover:text-[var(--blueprint)] transition-colors">
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
      </div>

      {/* FAQ Section */}
      <div className="mb-12">
          <h2 className="font-serif text-2xl text-[var(--ink)] mb-6">
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

        {/* Contact Section */}
        <BlueprintCard showCorners padding="lg" className="bg-gradient-to-br from-[var(--surface)] to-[var(--paper)]">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-serif text-2xl text-[var(--ink)] mb-2">Still need help?</h3>
              <p className="text-[var(--ink-secondary)]">Our team typically responds within 2 hours during business hours.</p>
            </div>
            <div className="flex gap-4">
              <SecondaryButton className="h-12 px-6" onClick={() => toast.info("Connecting to live chat...", { description: "Support agents are currently busy." })}>
                <MessageCircle size={18} />
                Live Chat
              </SecondaryButton>
              <BlueprintButton className="h-12 px-6" onClick={() => {
                window.open("mailto:support@raptorflow.ai");
                toast.success("Email client opened");
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
            <a href="#" className="hover:text-[var(--ink)] transition-colors flex items-center gap-1">
              <ExternalLink size={12} />
              API Reference
            </a>
            <a href="#" className="hover:text-[var(--ink)] transition-colors flex items-center gap-1">
              <ExternalLink size={12} />
              Status Page
            </a>
            <a href="#" className="hover:text-[var(--ink)] transition-colors flex items-center gap-1">
              <ExternalLink size={12} />
              Community
            </a>
          </div>
        </div>
      </div>
    );
  }
