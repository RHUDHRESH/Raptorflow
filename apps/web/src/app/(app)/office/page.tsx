import type * as React from "react";
import dynamic from "next/dynamic";
import { OfficeErrorBoundary } from "@/components/office/OfficeErrorBoundary";

const OfficeCanvas = dynamic(
  () => import("@/components/office/OfficeCanvas"),
  { ssr: false, loading: () => null }
);

export default function OfficePage(): React.ReactElement {
  return (
    <div
      className="relative w-[calc(100vw+16rem)] h-screen overflow-hidden -ml-64"
      style={{ background: "#08081a" }}
    >
      <OfficeErrorBoundary>
        <OfficeCanvas />
      </OfficeErrorBoundary>
      <div className="absolute top-6 left-[calc(16rem+1.5rem)] z-10 pointer-events-none">
        <p className="text-white/80 text-xl font-bold tracking-tight">
          The Office
        </p>
        <p className="text-slate-400 text-sm mt-0.5">
          6 council members present
        </p>
      </div>
      <div className="absolute bottom-0 left-64 right-0 z-10 px-6 pb-6">
        <div className="max-w-2xl mx-auto">
          <div
            className="w-full rounded-2xl border border-white/[0.08] px-4 py-3 text-slate-400 text-sm cursor-text"
            style={{ background: "rgba(255,255,255,0.04)", backdropFilter: "blur(24px)" }}
          >
            Ask your council anything...
          </div>
        </div>
      </div>
    </div>
  );
}
