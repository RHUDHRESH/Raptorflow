"use client";

import * as React from "react";
import { useState, useEffect } from "react";
import { Menu, X } from "lucide-react";

const navLinks = [
  { label: "Features", href: "#features" },
  { label: "How it works", href: "#how-it-works" },
  { label: "Access", href: "#access" },
];

export function LandingNav() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? "bg-[var(--background)]/95 backdrop-blur-sm shadow-sm paper-soft"
          : "bg-transparent"
      }`}
    >
      <div className="mx-auto max-w-6xl px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 lg:h-20">
          <a href="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 rounded-[var(--radius)] bg-[var(--primary)] flex items-center justify-center text-white font-bold transition-transform duration-200 group-hover:scale-105">
              R
            </div>
            <span className="text-xl font-bold text-[var(--ink-900)] font-display">RaptorFlow</span>
          </a>

          <div className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => (
              <a
                key={link.label}
                href={link.href}
                className="text-sm font-medium text-[var(--ink-500)] hover:text-[var(--ink-900)] transition-colors link-underline"
              >
                {link.label}
              </a>
            ))}
          </div>

          <div className="hidden md:flex items-center gap-4">
            <a
              href="/sign-in"
              className="text-sm font-medium text-[var(--ink-500)] hover:text-[var(--ink-900)] transition-colors"
            >
              Sign in
            </a>
            <a href="/sign-up" className="btn-primary">
              Get started
            </a>
          </div>

          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2 text-[var(--ink-500)] hover:text-[var(--ink-900)] transition-colors"
          >
            {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {isMobileMenuOpen && (
        <div className="md:hidden bg-[var(--card)] border-t border-[var(--border)] shadow-lg">
          <div className="px-6 py-4 space-y-3">
            {navLinks.map((link) => (
              <a
                key={link.label}
                href={link.href}
                className="block py-2 text-[var(--ink-700)] font-medium"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                {link.label}
              </a>
            ))}
            <div className="pt-3 border-t border-[var(--border)] space-y-3">
              <a href="/sign-in" className="block py-2 text-[var(--ink-700)] font-medium">
                Sign in
              </a>
              <a href="/sign-up" className="block w-full py-3 text-center btn-primary">
                Get started
              </a>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}
