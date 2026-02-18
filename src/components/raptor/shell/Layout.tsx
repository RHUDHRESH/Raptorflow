"use client";

import React, { useRef, useEffect, useState } from "react";
import gsap from "gsap";
import { Sidebar } from "./Sidebar";
import { TopBar, ModeType } from "./TopBar";
import { RightDrawer } from "./RightDrawer";
import { Footer } from "./Footer";

export interface LayoutProps {
  children: React.ReactNode;
  mode?: ModeType;
  showDrawer?: boolean;
  drawerContent?: React.ReactNode;
  drawerDefaultTab?: "evidence" | "assumptions" | "variables" | "versions" | "why";
  activeNavItem?: string;
  brandName?: string;
  objective?: string;
  autosaveState?: "saving" | "saved" | "error";
  lastSync?: string;
  warnings?: number;
  version?: string;
  onDrawerClose?: () => void;
  resizableDrawer?: boolean;
}

export function Layout({
  children,
  mode = "draft",
  showDrawer = false,
  drawerContent,
  drawerDefaultTab = "evidence",
  activeNavItem = "foundation",
  brandName,
  objective,
  autosaveState,
  lastSync,
  warnings,
  version,
  onDrawerClose,
  resizableDrawer = false,
}: LayoutProps) {
  const mainRef = useRef<HTMLElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const [isDrawerVisible, setIsDrawerVisible] = useState(showDrawer);

  // Sync local state with prop
  useEffect(() => {
    setIsDrawerVisible(showDrawer);
  }, [showDrawer]);

  // Main content entrance animation
  useEffect(() => {
    const ctx = gsap.context(() => {
      if (contentRef.current) {
        gsap.fromTo(
          contentRef.current,
          { opacity: 0.8, y: 8 },
          {
            opacity: 1,
            y: 0,
            duration: 0.4,
            ease: "power2.out",
            delay: 0.15,
          }
        );
      }
    }, mainRef);

    return () => ctx.revert();
  }, []);

  // Handle drawer close
  const handleDrawerClose = () => {
    setIsDrawerVisible(false);
    onDrawerClose?.();
  };

  return (
    <div
      className="flex h-screen w-screen overflow-hidden"
      style={{
        backgroundColor: "var(--bg-canvas, #EFEDE6)",
      }}
    >
      {/* Sidebar - Fixed Left Rail */}
      <Sidebar activeItem={activeNavItem} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Bar */}
        <TopBar
          brandName={brandName}
          objective={objective}
          mode={mode}
        />

        {/* Content + Optional Drawer */}
        <div className="flex flex-1 overflow-hidden">
          {/* Main Scrollable Area */}
          <main
            ref={mainRef}
            className="flex-1 overflow-y-auto overflow-x-hidden"
            style={{
              backgroundColor: "var(--bg-canvas, #EFEDE6)",
            }}
          >
            <div ref={contentRef} className="h-full">
              {children}
            </div>
          </main>

          {/* Right Drawer */}
          {isDrawerVisible && (
            drawerContent ? (
              <div
                className="flex-shrink-0 h-full"
                style={{
                  width: "var(--shell-drawer, 400px)",
                  backgroundColor: "var(--bg-surface, #F7F5EF)",
                  borderLeft: "1px solid var(--border-1, #E3DED3)",
                }}
              >
                {drawerContent}
              </div>
            ) : (
              <RightDrawer
                defaultTab={drawerDefaultTab}
                onClose={handleDrawerClose}
                resizable={resizableDrawer}
              />
            )
          )}
        </div>

        {/* Footer */}
        <Footer
          autosaveState={autosaveState}
          lastSync={lastSync}
          warnings={warnings}
          version={version}
        />
      </div>
    </div>
  );
}

// Re-export components for convenience
export { Sidebar } from "./Sidebar";
export { TopBar, type ModeType } from "./TopBar";
export { RightDrawer } from "./RightDrawer";
export { Footer } from "./Footer";
