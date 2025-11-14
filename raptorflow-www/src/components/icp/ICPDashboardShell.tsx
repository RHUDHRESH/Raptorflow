"use client";

import { DarkBackground } from "./DarkBackground";
import { ICPGrid, ICPGridItem } from "./ICPGrid";

/**
 * Main shell component for the ICP Maker / ICP Reveal screen.
 * Provides the dark, premium background and flexible layout structure
 * where ICP cards (left) and detail panels (right) will be plugged in.
 */
export function ICPDashboardShell() {
  return (
    <div className="relative min-h-screen w-full overflow-hidden">
      <DarkBackground />

      {/* Main content area */}
      <div className="relative z-10">
        <ICPGrid>
          {/* Left column: ICP Cards placeholder */}
          <ICPGridItem colSpan={3} className="min-h-[600px]">
            <div className="h-full flex flex-col items-center justify-center">
              <h3 className="text-2xl font-semibold text-white mb-2 tracking-tight">
                ICP Cards
              </h3>
              <p className="text-slate-400 text-sm">
                ICP cards will appear here
              </p>
            </div>
          </ICPGridItem>

          {/* Right column: ICP Details placeholder */}
          <ICPGridItem colSpan={3} className="min-h-[600px]">
            <div className="h-full flex flex-col items-center justify-center">
              <h3 className="text-2xl font-semibold text-white mb-2 tracking-tight">
                ICP Details
              </h3>
              <p className="text-slate-400 text-sm">
                ICP details will appear here
              </p>
            </div>
          </ICPGridItem>
        </ICPGrid>
      </div>
    </div>
  );
}

