"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { MobileSheet } from "./MobileSheet";

export function TopNav() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-rf-mineshaft/50 bg-rf-bg/80 backdrop-blur-sm">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Left: Wordmark */}
          <Link href="/" className="flex items-center space-x-2">
            <span className="text-xl font-bold text-rf-ink">RaptorFlow</span>
          </Link>

          {/* Center: Links (hidden on mobile) */}
          <div className="hidden md:flex items-center space-x-8">
            <Link
              href="#features"
              className="text-sm text-rf-subtle hover:text-rf-ink transition-colors"
            >
              Features
            </Link>
            <Link
              href="#how-it-works"
              className="text-sm text-rf-subtle hover:text-rf-ink transition-colors"
            >
              How It Works
            </Link>
            <Link
              href="#pricing"
              className="text-sm text-rf-subtle hover:text-rf-ink transition-colors"
            >
              Pricing
            </Link>
            <Link
              href="/docs"
              className="text-sm text-rf-subtle hover:text-rf-ink transition-colors"
            >
              Docs
            </Link>
          </div>

          {/* Right: Buttons */}
          <div className="hidden md:flex items-center space-x-4">
            <Button variant="ghost" className="text-rf-subtle hover:text-rf-ink">
              Login
            </Button>
            <Button className="bg-rf-accent hover:bg-rf-accent/90 text-white">
              Sign Up
            </Button>
          </div>

          {/* Mobile Menu */}
          <div className="md:hidden">
            <MobileSheet />
          </div>
        </div>
      </div>
    </nav>
  );
}
