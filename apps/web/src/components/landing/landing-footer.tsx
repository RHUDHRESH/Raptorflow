"use client";

import * as React from "react";
import { useState } from "react";
import {
  MessageCircle,
  ArrowUpRight,
  Mail,
  MapPin,
  Phone,
  ExternalLink,
  Users,
  Zap,
} from "lucide-react";
import { GsapBridge } from "@/components/ui/gsap-bridge";

const footerLinks = {
  product: [
    { label: "Features", href: "#features" },
    { label: "How it works", href: "#how-it-works" },
    { label: "Access", href: "#access" },
    { label: "Sign in", href: "/sign-in" },
  ],
  company: [
    { label: "About", href: "/about" },
    { label: "Blog", href: "/blog" },
    { label: "Careers", href: "/careers" },
    { label: "Contact", href: "#contact" },
  ],
  legal: [
    { label: "Privacy Policy", href: "/privacy" },
    { label: "Terms of Service", href: "/terms" },
  ],
};

const stats = [
  { icon: Zap, label: "500+", desc: "Companies served" },
  { icon: MapPin, label: "40+", desc: "Cities in India" },
  { icon: Users, label: "Live", desc: "No paywall" },
];

export function LandingFooter() {
  const [hoveredLink, setHoveredLink] = useState<string | null>(null);

  const handleWhatsApp = () => {
    window.open(
      "https://wa.me/919600570299?text=Hi%2C+I%27d+like+to+know+more+about+RaptorFlow",
      "_blank",
      "noopener,noreferrer",
    );
  };

  return (
    <footer className="relative bg-[var(--ink-900)] text-white overflow-hidden paper-soft">
      <div className="absolute top-0 left-0 right-0 h-px bg-[var(--primary)]/30" />

      <GsapBridge stagger className="mx-auto max-w-7xl px-6 lg:px-8 pt-20 pb-12">
        <div className="gsap-reveal grid lg:grid-cols-12 gap-12 lg:gap-8">
          <div className="lg:col-span-4">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-[var(--radius)] bg-[var(--primary)] flex items-center justify-center text-white font-bold text-lg">
                R
              </div>
              <span className="text-2xl font-bold font-display">RaptorFlow</span>
            </div>

            <p className="text-[var(--ink-400)] leading-relaxed mb-8 max-w-sm">
              The marketing intelligence platform for Indian B2B SaaS founders. Sign in once and use the full product immediately.
            </p>

            <div className="flex flex-col gap-3">
              <button
                onClick={handleWhatsApp}
                className="group flex items-center gap-3 px-5 py-3 bg-[var(--primary)] text-white rounded-[var(--radius)] hover:bg-[var(--primary-hover)] transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]"
              >
                <MessageCircle className="w-5 h-5" />
                <span className="font-medium">Chat on WhatsApp</span>
                <ArrowUpRight className="w-4 h-4 ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
              </button>

              <a
                href="mailto:hello@raptorflow.in"
                className="group flex items-center gap-3 px-5 py-3 bg-[var(--ink-700)]/50 text-[var(--ink-300)] rounded-[var(--radius)] hover:bg-[var(--ink-700)] transition-all duration-200"
              >
                <Mail className="w-5 h-5" />
                <span>hello@raptorflow.in</span>
                <ExternalLink className="w-4 h-4 ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
              </a>
            </div>
          </div>

          <div className="lg:col-span-5 grid grid-cols-3 gap-8">
            <div>
              <h4 className="eyebrow text-[var(--ink-400)] mb-4">Product</h4>
              <ul className="space-y-3">
                {footerLinks.product.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="group flex items-center gap-1 text-[var(--ink-400)] hover:text-white transition-colors"
                      onMouseEnter={() => setHoveredLink(link.label)}
                      onMouseLeave={() => setHoveredLink(null)}
                    >
                      <span className="relative">
                        {link.label}
                        <span
                          className={`absolute -bottom-0.5 left-0 h-px bg-[var(--primary)] transition-all duration-300 ${
                            hoveredLink === link.label ? "w-full" : "w-0"
                          }`}
                        />
                      </span>
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="eyebrow text-[var(--ink-400)] mb-4">Company</h4>
              <ul className="space-y-3">
                {footerLinks.company.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="group flex items-center gap-1 text-[var(--ink-400)] hover:text-white transition-colors"
                      onMouseEnter={() => setHoveredLink(link.label)}
                      onMouseLeave={() => setHoveredLink(null)}
                    >
                      <span className="relative">
                        {link.label}
                        <span
                          className={`absolute -bottom-0.5 left-0 h-px bg-[var(--primary)] transition-all duration-300 ${
                            hoveredLink === link.label ? "w-full" : "w-0"
                          }`}
                        />
                      </span>
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="eyebrow text-[var(--ink-400)] mb-4">Legal</h4>
              <ul className="space-y-3">
                {footerLinks.legal.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="group flex items-center gap-1 text-[var(--ink-400)] hover:text-white transition-colors"
                      onMouseEnter={() => setHoveredLink(link.label)}
                      onMouseLeave={() => setHoveredLink(null)}
                    >
                      <span className="relative">
                        {link.label}
                        <span
                          className={`absolute -bottom-0.5 left-0 h-px bg-[var(--primary)] transition-all duration-300 ${
                            hoveredLink === link.label ? "w-full" : "w-0"
                          }`}
                        />
                      </span>
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="lg:col-span-3">
            <h4 className="eyebrow text-[var(--ink-400)] mb-4">By the numbers</h4>
            <div className="space-y-4">
              {stats.map((stat, i) => (
                <div
                  key={i}
                  className="group flex items-center gap-4 p-4 bg-[var(--ink-700)]/30 rounded-[var(--radius-lg)] hover:bg-[var(--ink-700)]/50 transition-all duration-200 cursor-default"
                >
                  <div className="w-10 h-10 rounded-[var(--radius)] bg-[var(--primary)]/10 flex items-center justify-center group-hover:bg-[var(--primary)]/20 transition-colors">
                    <stat.icon className="w-5 h-5 text-[var(--primary)]" />
                  </div>
                  <div>
                    <div className="text-xl font-bold text-white font-display">{stat.label}</div>
                    <div className="text-sm text-[var(--ink-400)]">{stat.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="gsap-reveal mt-16 pt-8 border-t border-[var(--ink-700)]/50">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-6 text-sm text-[var(--ink-400)]">
              <span>© 2026 RaptorFlow</span>
              <span className="hidden md:inline">·</span>
              <span>Made in Bangalore</span>
              <span className="hidden md:inline">·</span>
              <span>No plans required</span>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-sm text-[var(--ink-400)]">
                <Phone className="w-4 h-4" />
                <span>+91 96005 70299</span>
              </div>
            </div>
          </div>
        </div>
      </GsapBridge>
    </footer>
  );
}
