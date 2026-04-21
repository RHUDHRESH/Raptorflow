"use client";

import * as React from "react";
import { MessageCircle } from "lucide-react";

export function LandingFooter() {
  return (
    <footer className="relative bg-[#0E0F13] border-t border-[rgba(255,255,255,0.07)] px-6 lg:px-12 py-12">
      <div className="mx-auto max-w-[1200px] grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
        {/* Left */}
        <div>
          <div className="text-white font-bold text-lg tracking-tight">RaptorFlow</div>
          <p className="font-[family-name:var(--font-mono)] text-[11px] text-[rgba(255,255,255,0.25)] mt-4">
            Built in Bangalore. Made for Indian B2B SaaS.
          </p>
        </div>

        {/* Center */}
        <div className="text-center">
          <div className="flex items-center justify-center gap-4 mb-3">
            <a
              href="/privacy"
              className="text-[13px] text-[rgba(255,255,255,0.35)] hover:text-white transition-colors"
            >
              Privacy
            </a>
            <span className="text-[rgba(255,255,255,0.20)]">·</span>
            <a
              href="/terms"
              className="text-[13px] text-[rgba(255,255,255,0.35)] hover:text-white transition-colors"
            >
              Terms
            </a>
          </div>
          <p className="font-[family-name:var(--font-mono)] text-[12px] text-[rgba(255,255,255,0.20)]">
            © 2025 RaptorFlow. GST invoices provided.
          </p>
        </div>

        {/* Right */}
        <div className="flex justify-start md:justify-end">
          <a
            href="https://wa.me/919600570299?text=Hi%2C+I%27d+like+to+know+more+about+RaptorFlow"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-[13px] text-[rgba(255,255,255,0.50)] hover:text-white transition-colors"
          >
            <MessageCircle className="w-4 h-4 text-[#3FA66A]" />
            <span>+91 96005 70299</span>
          </a>
        </div>
      </div>
    </footer>
  );
}
