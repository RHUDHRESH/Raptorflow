"use client";

import React from "react";
import { MoveRight, Play, TrendingUp, Target, Zap, Compass, ArrowUpRight } from "lucide-react";
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { BlueprintCard, CardFooter } from "@/components/ui/BlueprintCard";
import { useAuth } from "@/components/auth/AuthProvider";

/* ══════════════════════════════════════════════════════════════════════════════
   INTERACTIVE HERO SECTION - Client Component
   Handles all interactive elements to avoid prerendering issues
   ═════════════════════════════════════════════════════════════════════════════ */

export function InteractiveHero() {
  const { user } = useAuth();
  const router = useRouter();

  const handleGetStarted = () => {
    if (user) {
      router.push('/dashboard');
    } else {
      router.push('/signup');
    }
  };

  const handleSignIn = () => {
    router.push('/signin');
  };

  return (
    <>
      {/* Navigation */}
      <nav className="hidden md:flex items-center gap-8">
        <Link href="#features" className="font-technical text-[var(--muted)] hover:text-[var(--ink)] transition-colors">
          FEATURES
        </Link>
        <Link href="#pricing" className="font-technical text-[var(--muted)] hover:text-[var(--ink)] transition-colors">
          PRICING
        </Link>
        <Link href="#docs" className="font-technical text-[var(--muted)] hover:text-[var(--ink)] transition-colors">
          DOCS
        </Link>
        <div className="w-px h-4 bg-[var(--border)]" />
        <button onClick={handleSignIn} className="font-technical text-[var(--secondary)] hover:text-[var(--ink)] transition-colors cursor-pointer">
          SIGN IN
        </button>
        <BlueprintButton size="sm" label="BTN-01" onClick={handleGetStarted}>
          Get Started
        </BlueprintButton>
      </nav>

      {/* Footer Links */}
      <div className="flex items-center gap-10">
        {["Privacy", "Terms", "Documentation", "GitHub"].map((link) => (
          <Link
            key={link}
            href={`#${link.toLowerCase()}`}
            className="font-technical text-[var(--muted)] hover:text-[var(--ink)] transition-colors"
          >
            {link.toUpperCase()}
          </Link>
        ))}
      </div>
    </>
  );
}
