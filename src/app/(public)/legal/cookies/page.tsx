"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { Card } from "@/components/raptor/ui/Card";
import { Cookie, Mail } from "lucide-react";

const LAST_UPDATED = "February 13, 2025";

export default function CookiePolicyPage() {
  const pageRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!pageRef.current) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        ".legal-content",
        { y: 30, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.6, ease: "power2.out" }
      );
    }, pageRef);

    return () => ctx.revert();
  }, []);

  return (
    <div ref={pageRef} className="max-w-3xl mx-auto px-6 pb-24 pt-8">
      {/* Header */}
      <div className="text-center mb-12">
        <div className="flex items-center justify-center gap-2 mb-4">
          <Cookie size={20} className="text-[var(--ink-3)]" />
          <span className="rf-mono-xs text-[var(--ink-3)] uppercase tracking-wider">Legal</span>
        </div>
        <h1 className="rf-h1 mb-4">Cookie Policy</h1>
        <p className="rf-body-sm text-[var(--ink-3)]">Last updated: {LAST_UPDATED}</p>
      </div>

      {/* Content */}
      <div className="legal-content space-y-8">
        <Card>
          <section className="mb-8">
            <h2 className="rf-h4 mb-4">1. What Are Cookies</h2>
            <p className="rf-body text-[var(--ink-2)] mb-4">
              Cookies are small text files that are placed on your computer or mobile device when you 
              visit a website. They are widely used to make websites work more efficiently and provide 
              information to the owners of the site.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="rf-h4 mb-4">2. How We Use Cookies</h2>
            <p className="rf-body text-[var(--ink-2)] mb-4">RaptorFlow uses cookies for the following purposes:</p>
            
            <h3 className="rf-body font-semibold text-[var(--ink-1)] mb-3">Essential Cookies</h3>
            <p className="rf-body text-[var(--ink-2)] mb-4">
              These cookies are necessary for the website to function properly. They enable core 
              functionality such as security, network management, and account access.
            </p>
            
            <h3 className="rf-body font-semibold text-[var(--ink-1)] mb-3">Analytics Cookies</h3>
            <p className="rf-body text-[var(--ink-2)] mb-4">
              These cookies help us understand how visitors interact with our website by collecting 
              and reporting information anonymously.
            </p>
          </section>

          <section>
            <h2 className="rf-h4 mb-4">3. Contact Us</h2>
            <div className="flex items-center gap-2 mt-6">
              <Mail size={16} className="text-[var(--ink-3)]" />
              <a href="mailto:privacy@raptorflow.io" className="rf-body text-[var(--ink-1)] hover:underline">
                privacy@raptorflow.io
              </a>
            </div>
          </section>
        </Card>

        {/* Related Links */}
        <div className="flex flex-wrap gap-4 justify-center">
          <a href="/legal/privacy" className="rf-body-sm text-[var(--ink-2)] hover:text-[var(--ink-1)]">
            Privacy Policy
          </a>
          <span className="text-[var(--border-2)]">·</span>
          <a href="/legal/terms" className="rf-body-sm text-[var(--ink-2)] hover:text-[var(--ink-1)]">
            Terms of Service
          </a>
        </div>
      </div>
    </div>
  );
}
