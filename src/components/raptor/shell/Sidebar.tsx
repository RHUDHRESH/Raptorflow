"use client";

import React, { useRef, useEffect } from "react";
import gsap from "gsap";
import {
  Building2,
  Users,
  Target,
  Megaphone,
  Sparkles,
  Grid3X3,
  Box,
} from "lucide-react";
import { CompassLogo, CompassLogoRef } from "@/components/brand/CompassLogo";

interface NavItem {
  id: string;
  label: string;
  icon: React.ElementType;
  href: string;
}

const navItems: NavItem[] = [
  { id: "foundation", label: "Foundation", icon: Building2, href: "/foundation" },
  { id: "cohorts", label: "Cohorts", icon: Users, href: "/cohorts" },
  { id: "moves", label: "Moves", icon: Target, href: "/moves" },
  { id: "campaigns", label: "Campaigns", icon: Megaphone, href: "/campaigns" },
  { id: "muse", label: "Muse", icon: Sparkles, href: "/muse" },
  { id: "matrix", label: "Matrix", icon: Grid3X3, href: "/matrix" },
  { id: "blackbox", label: "Blackbox", icon: Box, href: "/blackbox" },
];

interface SidebarProps {
  activeItem?: string;
}

export function Sidebar({ activeItem = "foundation" }: SidebarProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const itemsRef = useRef<(HTMLAnchorElement | null)[]>([]);
  const dailyWinRef = useRef<HTMLDivElement>(null);
  const logoRef = useRef<CompassLogoRef>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Initial state
      gsap.set(itemsRef.current, {
        opacity: 0,
        x: -20,
      });

      gsap.set(dailyWinRef.current, {
        opacity: 0,
        y: 10,
      });

      // Stagger entrance animation
      gsap.to(itemsRef.current, {
        opacity: 1,
        x: 0,
        duration: 0.4,
        ease: "power2.out",
        stagger: 0.05,
        delay: 0.1,
      });

      // Daily win entrance
      gsap.to(dailyWinRef.current, {
        opacity: 1,
        y: 0,
        duration: 0.5,
        ease: "power2.out",
        delay: 0.6,
      });
    }, containerRef);

    return () => ctx.revert();
  }, []);

  const handleMouseEnter = (index: number) => {
    gsap.to(itemsRef.current[index], {
      x: 2,
      duration: 0.2,
      ease: "power2.out",
    });
  };

  const handleMouseLeave = (index: number) => {
    gsap.to(itemsRef.current[index], {
      x: 0,
      duration: 0.2,
      ease: "power2.out",
    });
  };

  return (
    <aside
      ref={containerRef}
      className="flex flex-col h-full"
      style={{
        width: "var(--shell-rail, 280px)",
        backgroundColor: "var(--bg-surface, #F7F5EF)",
        borderRight: "1px solid var(--border-1, #E3DED3)",
      }}
    >
      {/* Logo Section */}
      <div
        className="flex items-center px-4"
        style={{
          height: "var(--shell-topbar, 56px)",
          borderBottom: "1px solid var(--border-1, #E3DED3)",
        }}
      >
        <a 
          href="/dashboard" 
          className="hover:opacity-80 transition-opacity"
          onMouseEnter={() => logoRef.current?.pulse()}
        >
          <CompassLogo 
            ref={logoRef}
            size="md" 
            showText 
            animate 
          />
        </a>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 overflow-y-auto">
        <div className="flex flex-col" style={{ gap: "4px" }}>
          {navItems.map((item, index) => {
            const isActive = activeItem === item.id;
            const Icon = item.icon;

            return (
              <a
                key={item.id}
                ref={(el) => {
                  itemsRef.current[index] = el;
                }}
                href={item.href}
                onMouseEnter={() => handleMouseEnter(index)}
                onMouseLeave={() => handleMouseLeave(index)}
                className="flex items-center rounded-md transition-colors"
                style={{
                  height: "40px",
                  padding: "0 16px",
                  backgroundColor: isActive
                    ? "var(--rf-charcoal, #2A2529)"
                    : "transparent",
                  color: isActive
                    ? "var(--rf-ivory, #F3F0E7)"
                    : "var(--rf-muted-ink, #5C565B)",
                  fontFamily: "'DM Sans', system-ui, sans-serif",
                  fontSize: "14px",
                  fontWeight: 500,
                }}
              >
                <Icon
                  size={18}
                  className="mr-3"
                  style={{
                    color: isActive
                      ? "var(--rf-ivory, #F3F0E7)"
                      : "var(--rf-muted-ink, #5C565B)",
                  }}
                />
                <span>{item.label}</span>
                {item.id === "muse" && (
                  <span
                    className="ml-auto text-xs px-1.5 py-0.5 rounded"
                    style={{
                      backgroundColor: isActive
                        ? "rgba(243, 240, 231, 0.2)"
                        : "var(--rf-fog, #EFEDE6)",
                      color: isActive
                        ? "var(--rf-ivory, #F3F0E7)"
                        : "var(--rf-muted-ink, #5C565B)",
                    }}
                  >
                    AI
                  </span>
                )}
              </a>
            );
          })}
        </div>
      </nav>

      {/* Daily Win Indicator */}
      <div
        ref={dailyWinRef}
        className="mx-3 mb-4 p-3 rounded-lg"
        style={{
          backgroundColor: "var(--rf-fog, #EFEDE6)",
          border: "1px solid var(--border-1, #E3DED3)",
        }}
      >
        <div
          className="flex items-center justify-between mb-2"
          style={{
            fontFamily: "'DM Sans', system-ui, sans-serif",
          }}
        >
          <span
            className="text-xs font-medium uppercase tracking-wider"
            style={{ color: "var(--rf-muted-ink, #5C565B)" }}
          >
            Daily Win
          </span>
          <span
            className="text-xs"
            style={{ color: "var(--ink-3, #847C82)" }}
          >
            3/5
          </span>
        </div>
        <div
          className="h-1.5 rounded-full overflow-hidden"
          style={{ backgroundColor: "var(--border-1, #E3DED3)" }}
        >
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: "60%",
              backgroundColor: "var(--rf-charcoal, #2A2529)",
            }}
          />
        </div>
        <p
          className="mt-2 text-xs"
          style={{
            color: "var(--rf-muted-ink, #5C565B)",
            fontFamily: "'DM Sans', system-ui, sans-serif",
          }}
        >
          Validate 2 more assumptions
        </p>
      </div>
    </aside>
  );
}
