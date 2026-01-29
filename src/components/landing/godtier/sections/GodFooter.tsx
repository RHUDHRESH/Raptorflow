"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { RaptorLogo } from "@/components/ui/CompassLogo";
import { Twitter, Linkedin, Github, Mail } from "lucide-react";

// ═══════════════════════════════════════════════════════════════
// God Footer - Comprehensive footer with links
// ═══════════════════════════════════════════════════════════════

const footerLinks = {
  Product: [
    { label: "Features", href: "#features" },
    { label: "Pricing", href: "#pricing" },
    { label: "Integrations", href: "#" },
    { label: "Changelog", href: "#" },
  ],
  Company: [
    { label: "About", href: "#" },
    { label: "Blog", href: "#" },
    { label: "Careers", href: "#" },
    { label: "Contact", href: "#" },
  ],
  Resources: [
    { label: "Documentation", href: "#" },
    { label: "Help Center", href: "#" },
    { label: "Community", href: "#" },
    { label: "Templates", href: "#" },
  ],
  Legal: [
    { label: "Privacy", href: "#" },
    { label: "Terms", href: "#" },
    { label: "Security", href: "#" },
    { label: "Cookies", href: "#" },
  ],
};

const socialLinks = [
  { icon: Twitter, href: "#", label: "Twitter" },
  { icon: Linkedin, href: "#", label: "LinkedIn" },
  { icon: Github, href: "#", label: "GitHub" },
  { icon: Mail, href: "#", label: "Email" },
];

export function GodFooter() {
  return (
    <footer className="bg-[var(--ink)] text-[var(--canvas)] py-16 md:py-20">
      <div className="max-w-7xl mx-auto px-6">
        {/* Main Footer Content */}
        <div className="grid grid-cols-2 md:grid-cols-6 gap-8 mb-16">
          {/* Brand */}
          <div className="col-span-2">
            <Link href="/" className="flex items-center gap-3 mb-4">
              <RaptorLogo size={32} className="text-[var(--canvas)]" />
              <span className="font-editorial text-xl font-semibold">RaptorFlow</span>
            </Link>
            <p className="text-[var(--muted)] mb-6 max-w-xs">
              The marketing operating system for founders who want results, not more tools.
            </p>
            {/* Social Links */}
            <div className="flex gap-4">
              {socialLinks.map((social, i) => (
                <a
                  key={i}
                  href={social.href}
                  aria-label={social.label}
                  className="w-10 h-10 rounded-full border border-[var(--muted)]/30 flex items-center justify-center hover:border-[var(--canvas)] transition-colors"
                >
                  <social.icon className="w-4 h-4" />
                </a>
              ))}
            </div>
          </div>

          {/* Links */}
          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <h4 className="font-semibold mb-4">{category}</h4>
              <ul className="space-y-3">
                {links.map((link, i) => (
                  <li key={i}>
                    <Link
                      href={link.href}
                      className="text-[var(--muted)] hover:text-[var(--canvas)] transition-colors text-sm"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-[var(--muted)]/20 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-sm text-[var(--muted)]">
            © {new Date().getFullYear()} RaptorFlow. All rights reserved.
          </p>
          <p className="text-sm text-[var(--muted)]">
            Made with care for founders everywhere.
          </p>
        </div>
      </div>
    </footer>
  );
}
