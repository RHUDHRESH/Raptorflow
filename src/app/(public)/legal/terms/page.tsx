"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
// Public terms page - no workspace required
import { Card } from "@/components/raptor/ui/Card";
import { Button } from "@/components/raptor/ui/Button";
import { Badge } from "@/components/raptor/ui/Badge";
import { 
  FileText, 
  Scale, 
  Users, 
  Shield,
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  Download,
  Clock,
  Globe,
  Mail,
  ExternalLink
} from "lucide-react";

gsap.registerPlugin(ScrollTrigger);

// ═══════════════════════════════════════════════════════════════════════════════
// TERMS OF SERVICE — Interactive Legal Document
// Progress tracking, section navigation, acceptance flow
// ═══════════════════════════════════════════════════════════════════════════════

const TOS_SECTIONS = [
  {
    id: "acceptance",
    icon: CheckCircle2,
    title: "Acceptance of Terms",
    shortTitle: "Acceptance",
    content: `By accessing or using RaptorFlow, you agree to be bound by these Terms of Service. If you disagree with any part of the terms, you may not access the service.

These terms constitute a legally binding agreement between you and RaptorFlow, Inc. regarding your use of our marketing platform and associated services.`,
    important: true,
  },
  {
    id: "account",
    icon: Users,
    title: "Account Terms",
    shortTitle: "Account",
    content: `You are responsible for maintaining the security of your account and password. RaptorFlow cannot and will not be liable for any loss or damage from your failure to comply with this security obligation.

**You may not:**
- Use the service for any illegal or unauthorized purpose
- Violate any laws in your jurisdiction
- Upload malicious code or interfere with the service
- Attempt to access restricted areas of the platform
- Share account credentials with unauthorized users

We reserve the right to terminate accounts that violate these terms.`,
    important: false,
  },
  {
    id: "payment",
    icon: Scale,
    title: "Payment Terms",
    shortTitle: "Payment",
    content: `All fees are exclusive of taxes, levies, or duties imposed by taxing authorities. You are responsible for all such charges.

**Subscriptions:**
- Monthly and annual billing options available
- Fees are charged in advance on a recurring basis
- No refunds for partial months or unused time
- You may cancel at any time; access continues until period end

**Free Trials:**
- 14-day free trial for new accounts
- Credit card required but not charged during trial
- Automatic conversion to paid plan unless cancelled`,
    important: true,
  },
  {
    id: "content",
    icon: FileText,
    title: "Content & Data",
    shortTitle: "Content",
    content: `You retain all rights to the content you upload to RaptorFlow. By uploading content, you grant us a license to use, store, and process that content solely to provide the service.

**Your Responsibilities:**
- Ensure you have rights to all uploaded content
- Don't upload infringing, defamatory, or unlawful content
- Maintain backups of your important data
- Comply with applicable data protection laws

We may remove content that violates these terms or applicable laws.`,
    important: false,
  },
  {
    id: "intellectual",
    icon: Shield,
    title: "Intellectual Property",
    shortTitle: "IP Rights",
    content: `RaptorFlow and its original content, features, and functionality are owned by RaptorFlow, Inc. and are protected by international copyright, trademark, and other intellectual property laws.

**Our Rights:**
- All rights to the RaptorFlow platform and brand
- Trademarks, logos, and service marks
- Patents and patent applications
- Trade secrets and proprietary technology

**Your Rights:**
- Limited, non-exclusive license to use the service
- No right to modify, reverse engineer, or create derivative works`,
    important: false,
  },
  {
    id: "termination",
    icon: AlertTriangle,
    title: "Termination",
    shortTitle: "Termination",
    content: `We may terminate or suspend your account immediately, without prior notice or liability, for any reason, including breach of these Terms.

**Upon Termination:**
- Your right to use the service immediately ceases
- Your data may be deleted after a 30-day grace period
- Outstanding fees remain due and payable
- Provisions that by nature should survive termination shall survive

**Effect of Termination:**
All data associated with your account may be permanently deleted. We are not liable for any loss resulting from termination.`,
    important: true,
  },
  {
    id: "liability",
    icon: Scale,
    title: "Limitation of Liability",
    shortTitle: "Liability",
    content: `In no event shall RaptorFlow, its directors, employees, partners, agents, suppliers, or affiliates be liable for any indirect, incidental, special, consequential, or punitive damages.

**Our Liability is Limited To:**
- The amount you paid to us in the 12 months prior to the claim
- Or $100 if you have not paid for the service

**We Are Not Liable For:**
- Loss of profits, revenue, data, or goodwill
- Service interruptions or data loss
- Third-party conduct or content
- Unauthorized access to your account

This limitation applies regardless of the theory of liability.`,
    important: true,
  },
  {
    id: "governing",
    icon: Globe,
    title: "Governing Law",
    shortTitle: "Governing Law",
    content: `These Terms shall be governed by and construed in accordance with the laws of the State of Delaware, United States, without regard to its conflict of law provisions.

**Dispute Resolution:**
- Any dispute shall first be attempted to be resolved through good faith negotiation
- If negotiation fails, disputes shall be resolved through binding arbitration
- Arbitration shall be conducted in Delaware under AAA rules
- Class action waivers apply

You agree to submit to the personal jurisdiction of courts located in Delaware for any actions not subject to arbitration.`,
    important: false,
  },
];

export default function TermsPage() {
  const pageRef = useRef<HTMLDivElement>(null);
  const [readingProgress, setReadingProgress] = useState(0);
  const [acceptedSections, setAcceptedSections] = useState<string[]>([]);
  const [showAcceptanceModal, setShowAcceptanceModal] = useState(false);
  const [hasReadAll, setHasReadAll] = useState(false);

  // Reading progress and section tracking
  useEffect(() => {
    const handleScroll = () => {
      const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = (window.scrollY / totalHeight) * 100;
      setReadingProgress(Math.min(progress, 100));

      // Check if user has scrolled through all sections
      if (progress > 90) {
        setHasReadAll(true);
      }

      // Track which sections have been viewed
      TOS_SECTIONS.forEach((section) => {
        const element = document.getElementById(section.id);
        if (element) {
          const rect = element.getBoundingClientRect();
          if (rect.top < window.innerHeight && rect.bottom > 0) {
            setAcceptedSections((prev) =>
              prev.includes(section.id) ? prev : [...prev, section.id]
            );
          }
        }
      });
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Entrance animations
  useEffect(() => {
    if (!pageRef.current) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        ".terms-header",
        { y: 40, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.8, ease: "power3.out" }
      );

      gsap.fromTo(
        ".terms-section",
        { y: 30, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.5,
          stagger: 0.1,
          delay: 0.3,
          ease: "power2.out",
          scrollTrigger: {
            trigger: ".terms-content",
            start: "top 80%",
          },
        }
      );
    }, pageRef);

    return () => ctx.revert();
  }, []);

  const scrollToSection = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
  };

  const acceptanceRate = Math.round((acceptedSections.length / TOS_SECTIONS.length) * 100);

  return (
    <>
      {/* Reading Progress */}
      <div className="fixed top-16 left-0 right-0 h-1 bg-[var(--border-1)] z-40">
        <div
          className="h-full bg-[var(--ink-1)] transition-all duration-150"
          style={{ width: `${readingProgress}%` }}
        />
      </div>

      <div ref={pageRef} className="max-w-4xl mx-auto px-6 pb-24 pt-8">
        {/* Header */}
        <div className="terms-header text-center mb-12 pt-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-[var(--bg-canvas)] rounded-full mb-6">
            <Scale size={16} className="text-[var(--ink-2)]" />
            <span className="rf-mono-xs text-[var(--ink-2)] uppercase tracking-wider">
              Legal
            </span>
          </div>
          <h1 className="rf-display mb-4">Terms of Service</h1>
          <p className="rf-body text-[var(--ink-2)] mb-4">
            Last updated: February 13, 2025
          </p>
          <div className="flex items-center justify-center gap-4">
            <span className="rf-mono-xs px-3 py-1 bg-[var(--bg-canvas)] text-[var(--ink-2)] rounded-full">
              Version 1.0
            </span>
          </div>
        </div>

        {/* Progress Overview */}
        <Card padding="md" className="mb-8 sticky top-4 z-40 bg-white/95 backdrop-blur">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="relative w-12 h-12">
                <svg className="w-12 h-12 -rotate-90" viewBox="0 0 36 36">
                  <path
                    className="text-[var(--border-1)]"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="3"
                  />
                  <path
                    className="text-[var(--ink-1)]"
                    strokeDasharray={`${acceptanceRate}, 100`}
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="3"
                  />
                </svg>
                <span className="absolute inset-0 flex items-center justify-center rf-mono-xs">
                  {acceptanceRate}%
                </span>
              </div>
              <div>
                <p className="rf-body-sm font-medium">Reading Progress</p>
                <p className="rf-mono-xs text-[var(--ink-3)]">
                  {acceptedSections.length} of {TOS_SECTIONS.length} sections viewed
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="tertiary"
                size="sm"
                leftIcon={<Download size={14} />}
              >
                PDF
              </Button>
              {hasReadAll && (
                <Button
                  variant="primary"
                  size="sm"
                  leftIcon={<CheckCircle2 size={14} />}
                  onClick={() => setShowAcceptanceModal(true)}
                >
                  I Accept
                </Button>
              )}
            </div>
          </div>
        </Card>

        {/* Table of Contents */}
        <Card padding="md" className="mb-8">
          <h3 className="rf-h4 mb-4">Table of Contents</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {TOS_SECTIONS.map((section) => {
              const isViewed = acceptedSections.includes(section.id);
              return (
                <button
                  key={section.id}
                  onClick={() => scrollToSection(section.id)}
                  className="flex items-center gap-2 p-2 rounded-[var(--radius-sm)] hover:bg-[var(--bg-canvas)] transition-colors text-left"
                >
                  <div
                    className={`w-5 h-5 rounded-full flex items-center justify-center ${
                      isViewed ? "bg-green-100" : "bg-[var(--border-1)]"
                    }`}
                  >
                    {isViewed ? (
                      <CheckCircle2 size={12} className="text-green-600" />
                    ) : (
                      <div className="w-2 h-2 rounded-full bg-[var(--border-2)]" />
                    )}
                  </div>
                  <span className="rf-body-sm flex-1">{section.shortTitle}</span>
                  {section.important && (
                    <span className="rf-mono-xs px-1.5 py-0.5 bg-amber-100 text-amber-700 rounded">
                      Important
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </Card>

        {/* Content */}
        <div className="terms-content space-y-6">
          {TOS_SECTIONS.map((section) => {
            const Icon = section.icon;
            const isViewed = acceptedSections.includes(section.id);

            return (
              <div
                key={section.id}
                id={section.id}
                className="terms-section scroll-mt-32"
              >
                <Card
                  padding="lg"
                  className={`transition-all duration-300 ${
                    isViewed ? "border-green-200" : ""
                  }`}
                >
                  <div className="flex items-start gap-4">
                    <div
                      className={`w-12 h-12 rounded-[var(--radius-sm)] flex items-center justify-center flex-shrink-0 transition-colors ${
                        isViewed ? "bg-green-100" : "bg-[var(--bg-canvas)]"
                      }`}
                    >
                      <Icon
                        size={24}
                        className={isViewed ? "text-green-600" : "text-[var(--ink-2)]"}
                      />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-4">
                        <h2 className="rf-h3">{section.title}</h2>
                        {section.important && (
                          <Badge variant="warning" size="sm">
                            Important
                          </Badge>
                        )}
                        {isViewed && (
                          <Badge variant="success" size="sm">
                            Viewed
                          </Badge>
                        )}
                      </div>

                      <div className="prose prose-sm max-w-none">
                        {section.content.split("\n\n").map((paragraph, idx) => {
                          if (paragraph.startsWith("**") && paragraph.endsWith("**")) {
                            return (
                              <h3 key={idx} className="rf-h4 mt-6 mb-3 text-[var(--ink-1)]">
                                {paragraph.replace(/\*\*/g, "")}
                              </h3>
                            );
                          }
                          if (paragraph.startsWith("- ")) {
                            return (
                              <ul key={idx} className="list-disc list-inside space-y-1 mb-4">
                                {paragraph.split("\n").map((item, i) => (
                                  <li key={i} className="rf-body text-[var(--ink-2)]">
                                    {item.replace("- ", "")}
                                  </li>
                                ))}
                              </ul>
                            );
                          }
                          return (
                            <p key={idx} className="rf-body text-[var(--ink-2)] mb-4 whitespace-pre-line">
                              {paragraph.replace(/\*\*/g, "")}
                            </p>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                </Card>
              </div>
            );
          })}
        </div>

        {/* Contact Section */}
        <Card padding="lg" className="mt-8 bg-gradient-to-br from-[var(--bg-canvas)] to-transparent">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-[var(--radius-sm)] bg-[var(--ink-1)] flex items-center justify-center flex-shrink-0">
              <Mail size={24} className="text-[var(--ink-inverse)]" />
            </div>
            <div className="flex-1">
              <h3 className="rf-h4 mb-2">Questions about our terms?</h3>
              <p className="rf-body-sm text-[var(--ink-2)] mb-4">
                Contact our legal team at{" "}
                <a href="mailto:legal@raptorflow.ai" className="text-[var(--ink-1)] underline">
                  legal@raptorflow.ai
                </a>
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Acceptance Modal */}
      {showAcceptanceModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card padding="lg" className="max-w-md w-full">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[var(--ink-1)] flex items-center justify-center">
                <Scale size={32} className="text-[var(--ink-inverse)]" />
              </div>
              <h3 className="rf-h4 mb-2">Accept Terms of Service</h3>
              <p className="rf-body-sm text-[var(--ink-2)] mb-6">
                By clicking &quot;I Accept&quot;, you acknowledge that you have read, understood, and agree to be bound by these Terms of Service.
              </p>
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  onClick={() => setShowAcceptanceModal(false)}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  onClick={() => {
                    setShowAcceptanceModal(false);
                    // Handle acceptance
                  }}
                  className="flex-1"
                >
                  I Accept
                </Button>
              </div>
              <p className="rf-mono-xs text-[var(--ink-3)] mt-4">
                Last accepted: {new Date().toLocaleDateString()}
              </p>
            </div>
          </Card>
        </div>
      )}
    </>
  );
}
