"use client";

import { useEffect, useRef, useState, useMemo } from "react";
import gsap from "gsap";
import { Card } from "@/components/raptor/ui/Card";
import { Button } from "@/components/raptor/ui/Button";
import { 
  Search, 
  MessageCircle, 
  BookOpen, 
  Zap, 
  Shield, 
  CreditCard,
  ChevronDown,
  ArrowRight,
  Mail,
  Clock,
  Sparkles,
  LifeBuoy
} from "lucide-react";

const HELP_CATEGORIES = [
  { id: "getting-started", icon: Zap, title: "Getting Started", description: "Onboarding, workspace setup, first moves", color: "#3D5A42", articles: 12 },
  { id: "foundation", icon: Shield, title: "Foundation", description: "Positioning, ICPs, messaging, BCM", color: "#3D5A6B", articles: 8 },
  { id: "moves", icon: BookOpen, title: "Strategic Moves", description: "Creating, executing, and tracking moves", color: "#8B6914", articles: 15 },
  { id: "billing", icon: CreditCard, title: "Billing & Plans", description: "Subscriptions, invoices, upgrades", color: "#6B3D5A", articles: 6 },
];

const FAQS = [
  { id: "what-is", category: "getting-started", question: "What is RaptorFlow?", answer: "RaptorFlow is a Marketing OS for operators. It combines a strategic Foundation with an execution engine (Moves) and an AI assistant (Muse).", popular: true },
  { id: "foundation-required", category: "getting-started", question: "Do I need to complete my Foundation first?", answer: "No, but it's recommended. The Foundation provides context that makes Moves and Muse significantly more effective.", popular: true },
  { id: "what-are-moves", category: "moves", question: "What are Strategic Moves?", answer: "Moves are 14-day marketing sprints with a specific goal. Each Move has a category (Ignite, Capture, Authority, Repair, Rally).", popular: true },
  { id: "muse-ai", category: "foundation", question: "How does Muse AI work?", answer: "Muse is context-aware. It reads your Foundation and active Moves to provide relevant suggestions. It's pull-based—you ask, it answers.", popular: true },
];

export default function SupportPage() {
  const pageRef = useRef<HTMLDivElement>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [openFaqId, setOpenFaqId] = useState<string | null>(null);

  const filteredFaqs = useMemo(() => {
    let faqs = FAQS;
    if (selectedCategory) faqs = faqs.filter((f) => f.category === selectedCategory);
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      faqs = faqs.filter((f) => f.question.toLowerCase().includes(q) || f.answer.toLowerCase().includes(q));
    }
    return faqs;
  }, [searchQuery, selectedCategory]);

  useEffect(() => {
    if (!pageRef.current) return;
    const ctx = gsap.context(() => {
      gsap.fromTo(".support-hero", { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.8, ease: "power3.out" });
    }, pageRef);
    return () => ctx.revert();
  }, []);

  return (
    <div ref={pageRef} className="max-w-5xl mx-auto px-6 pb-24 pt-8">
      {/* Hero */}
      <div className="support-hero text-center mb-12">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-[var(--bg-canvas)] rounded-full mb-6">
          <LifeBuoy size={16} className="text-[var(--ink-2)]" />
          <span className="rf-mono-xs text-[var(--ink-2)] uppercase tracking-wider">Support Center</span>
        </div>
        <h1 className="rf-h1 mb-4">How can we help?</h1>
        <p className="rf-body text-[var(--ink-2)] max-w-xl mx-auto">Search our knowledge base, browse FAQs, or reach out to our team directly.</p>
      </div>

      {/* Search */}
      <div className="max-w-2xl mx-auto mb-12">
        <div className="relative flex items-center bg-[var(--bg-surface)] border border-[var(--border-1)] rounded-lg shadow-sm">
          <Search size={20} className="ml-4 text-[var(--ink-3)]" />
          <input
            type="text"
            placeholder="Search for answers..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1 px-4 py-4 bg-transparent rf-body outline-none"
          />
        </div>
      </div>

      {/* Categories */}
      {!searchQuery && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-16">
          {HELP_CATEGORIES.map((cat) => {
            const Icon = cat.icon;
            const isSelected = selectedCategory === cat.id;
            return (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(isSelected ? null : cat.id)}
                className={`text-left p-6 rounded-lg border transition-all ${
                  isSelected ? "border-[var(--ink-1)] bg-[var(--ink-1)] text-white" : "border-[var(--border-1)] bg-[var(--bg-surface)] hover:border-[var(--border-2)]"
                }`}
              >
                <div className="w-12 h-12 rounded-lg flex items-center justify-center mb-4" style={{ backgroundColor: isSelected ? "rgba(255,255,255,0.2)" : `${cat.color}20` }}>
                  <Icon size={24} style={{ color: isSelected ? "white" : cat.color }} />
                </div>
                <h3 className="rf-h4 mb-1">{cat.title}</h3>
                <p className={`rf-body-sm mb-3 ${isSelected ? "text-white/70" : "text-[var(--ink-2)]"}`}>{cat.description}</p>
                <span className={`rf-mono-xs ${isSelected ? "text-white/50" : "text-[var(--ink-3)]"}`}>{cat.articles} articles</span>
              </button>
            );
          })}
        </div>
      )}

      {/* FAQs */}
      <div>
        <h2 className="rf-h3 mb-6">{searchQuery ? "Search Results" : "Frequently Asked Questions"}</h2>
        <div className="space-y-3">
          {filteredFaqs.map((faq) => (
            <div key={faq.id} className="bg-[var(--bg-surface)] border border-[var(--border-1)] rounded-lg overflow-hidden">
              <button
                onClick={() => setOpenFaqId(openFaqId === faq.id ? null : faq.id)}
                className="w-full flex items-center justify-between p-5 text-left"
              >
                <div className="flex items-center gap-3">
                  {faq.popular && <Sparkles size={16} className="text-amber-500" />}
                  <span className="rf-body font-medium">{faq.question}</span>
                </div>
                <ChevronDown size={20} className={`text-[var(--ink-3)] transition-transform ${openFaqId === faq.id ? "rotate-180" : ""}`} />
              </button>
              {openFaqId === faq.id && (
                <div className="px-5 pb-5">
                  <div className="h-px bg-[var(--border-1)] mb-4" />
                  <p className="rf-body text-[var(--ink-2)]">{faq.answer}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Contact */}
      <div className="mt-16 grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card padding="lg">
          <div className="w-12 h-12 rounded-lg bg-[var(--bg-canvas)] flex items-center justify-center mb-4">
            <MessageCircle size={24} className="text-[var(--ink-1)]" />
          </div>
          <h3 className="rf-h4 mb-2">Still need help?</h3>
          <p className="rf-body-sm text-[var(--ink-2)] mb-4">Our team typically responds within 24 hours.</p>
          <Button variant="primary" leftIcon={<Mail size={16} />}>
            Contact Support
          </Button>
        </Card>

        <Card padding="lg">
          <div className="w-12 h-12 rounded-lg bg-[#3D5A42]/10 flex items-center justify-center mb-4">
            <BookOpen size={24} className="text-[#3D5A42]" />
          </div>
          <h3 className="rf-h4 mb-2">Documentation</h3>
          <p className="rf-body-sm text-[var(--ink-2)] mb-4">Comprehensive guides and API references.</p>
          <Button variant="secondary" rightIcon={<ArrowRight size={16} />} onClick={() => window.location.href = "/docs"}>
            Browse Docs
          </Button>
        </Card>
      </div>

      {/* Footer Note */}
      <div className="mt-12 text-center">
        <div className="inline-flex items-center gap-2 text-[var(--ink-3)]">
          <Clock size={14} />
          <span className="rf-mono-xs uppercase">Support Hours: Mon-Fri, 9AM-6PM EST</span>
        </div>
      </div>
    </div>
  );
}
