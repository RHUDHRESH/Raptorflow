"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { Card } from "@/components/raptor/ui/Card";
import { Button } from "@/components/raptor/ui/Button";
import { Shield, Lock, Eye, Database, UserCheck, Globe, Mail } from "lucide-react";

const PRIVACY_SECTIONS = [
  {
    id: "overview",
    icon: Shield,
    title: "Overview",
    content: `At RaptorFlow, we believe privacy is a fundamental right. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our marketing platform.`,
  },
  {
    id: "collection",
    icon: Database,
    title: "Information We Collect",
    content: `We collect information that you provide directly to us, information we collect automatically, and information from third parties. This includes account information, foundation data, move configurations, and usage analytics.`,
  },
  {
    id: "usage",
    icon: Eye,
    title: "How We Use Your Information",
    content: `We use the information we collect to provide, maintain, and improve our services. Your Foundation data is used exclusively to personalize your experience and is never used to train general AI models.`,
  },
  {
    id: "rights",
    icon: UserCheck,
    title: "Your Rights",
    content: `Depending on your location, you may have rights including: access to your data, rectification, erasure, data portability, and the right to object to processing. Contact us to exercise these rights.`,
  },
];

export default function PrivacyPolicyPage() {
  const pageRef = useRef<HTMLDivElement>(null);
  const [readingProgress, setReadingProgress] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = (window.scrollY / totalHeight) * 100;
      setReadingProgress(Math.min(progress, 100));
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    if (!pageRef.current) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        ".privacy-header",
        { y: 40, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.8, ease: "power3.out" }
      );
    }, pageRef);

    return () => ctx.revert();
  }, []);

  return (
    <div ref={pageRef} className="max-w-4xl mx-auto px-6 pb-24 pt-8">
      {/* Reading Progress */}
      <div className="fixed top-16 left-0 right-0 h-1 bg-[var(--border-1)] z-40">
        <div className="h-full bg-[var(--ink-1)] transition-all duration-150" style={{ width: `${readingProgress}%` }} />
      </div>

      {/* Header */}
      <div className="privacy-header text-center mb-12">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-[var(--bg-canvas)] rounded-full mb-6">
          <Shield size={16} className="text-[var(--ink-2)]" />
          <span className="rf-mono-xs text-[var(--ink-2)] uppercase tracking-wider">Legal</span>
        </div>
        <h1 className="rf-display mb-4">Privacy Policy</h1>
        <p className="rf-body text-[var(--ink-2)] mb-4">Last updated: February 13, 2025</p>
        <div className="flex items-center justify-center gap-4">
          <span className="rf-mono-xs px-3 py-1 bg-green-100 text-green-700 rounded-full">GDPR Compliant</span>
          <span className="rf-mono-xs px-3 py-1 bg-blue-100 text-blue-700 rounded-full">CCPA Ready</span>
        </div>
      </div>

      {/* Content */}
      <div className="space-y-6">
        {PRIVACY_SECTIONS.map((section) => {
          const Icon = section.icon;
          return (
            <Card key={section.id} padding="lg">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-lg bg-[var(--bg-canvas)] flex items-center justify-center">
                  <Icon size={24} className="text-[var(--ink-2)]" />
                </div>
                <div className="flex-1">
                  <h2 className="rf-h3 mb-4">{section.title}</h2>
                  <p className="rf-body text-[var(--ink-2)] leading-relaxed">{section.content}</p>
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Contact */}
      <Card padding="lg" className="mt-8">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-lg bg-[var(--ink-1)] flex items-center justify-center">
            <Mail size={24} className="text-[var(--ink-inverse)]" />
          </div>
          <div className="flex-1">
            <h3 className="rf-h4 mb-2">Questions about privacy?</h3>
            <p className="rf-body-sm text-[var(--ink-2)]">
              Contact our Data Protection Officer at{" "}
              <a href="mailto:privacy@raptorflow.ai" className="text-[var(--ink-1)] underline">
                privacy@raptorflow.ai
              </a>
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
