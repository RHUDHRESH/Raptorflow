"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { MobileSheet } from "@/components/nav/MobileSheet";
import { cn } from "@/lib/utils";

export function FloatingNavbar() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <nav
      className={cn(
        "fixed top-4 left-1/2 -translate-x-1/2 z-50 transition-all duration-300",
        "rounded-full border backdrop-blur-xl",
        scrolled
          ? "bg-rf-card/80 border-rf-mineshaft/50 shadow-lg"
          : "bg-rf-card/40 border-rf-mineshaft/30"
      )}
    >
      <div className="flex h-14 items-center gap-1 px-4">
        {/* Logo */}
        <Link
          href="/"
          className="flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-rf-mineshaft/30 transition-colors"
        >
          <span className="text-lg font-bold text-rf-ink">RaptorFlow</span>
        </Link>

        {/* Desktop Links */}
        <div className="hidden md:flex items-center gap-1">
          <Link
            href="#features"
            className="px-4 py-2 text-sm text-rf-subtle hover:text-rf-ink hover:bg-rf-mineshaft/30 rounded-lg transition-colors"
          >
            Features
          </Link>
          <Link
            href="#how-it-works"
            className="px-4 py-2 text-sm text-rf-subtle hover:text-rf-ink hover:bg-rf-mineshaft/30 rounded-lg transition-colors"
          >
            How It Works
          </Link>
          <Link
            href="#pricing"
            className="px-4 py-2 text-sm text-rf-subtle hover:text-rf-ink hover:bg-rf-mineshaft/30 rounded-lg transition-colors"
          >
            Pricing
          </Link>
          <Link
            href="/docs"
            className="px-4 py-2 text-sm text-rf-subtle hover:text-rf-ink hover:bg-rf-mineshaft/30 rounded-lg transition-colors"
          >
            Docs
          </Link>
        </div>

        {/* Desktop Buttons */}
        <div className="hidden md:flex items-center gap-2 ml-2 pl-2 border-l border-rf-mineshaft/30">
          <Button
            variant="ghost"
            className="text-rf-subtle hover:text-rf-ink hover:bg-rf-mineshaft/30"
          >
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
    </nav>
  );
}

