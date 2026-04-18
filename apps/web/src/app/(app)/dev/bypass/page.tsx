// ⚠️ DEV BYPASS — DELETE THIS ENTIRE /dev/ FOLDER BEFORE PRODUCTION
"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { Card, CardHeader, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AlertTriangle, Loader2, Database, Rocket } from "lucide-react";

/**
 * Foundation Dev Bypass Page
 * 
 * Allows developers to skip the onboarding flow by seeding a high-fidelity 
 * test organization dataset (Verdant Naturals).
 */
export default function DevBypassPage() {
  const router = useRouter();
  const { getToken } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSeed = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/dev/seed-foundation`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      if (!res.ok) {
        throw new Error(await res.text() || "Failed to seed foundation data.");
      }

      // Success - redirect to dashboard
      router.push("/daily-wins");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#121212] flex items-center justify-center p-6 font-sans">
      <div className="max-w-md w-full space-y-4">
        {/* Warning Banner */}
        <div className="bg-red-500/10 border border-red-500/30 p-3 rounded-lg flex items-center gap-3">
          <AlertTriangle className="text-red-500 w-5 h-5 shrink-0" />
          <p className="text-[10px] text-red-500 uppercase font-bold tracking-widest leading-relaxed">
            ⚠️ DEV ONLY: Delete apps/web/src/app/(app)/dev and crates/foundation/src/dev_seed.rs before production.
          </p>
        </div>

        <Card className="bg-[#1a1a1a] border-zinc-800 shadow-2xl relative overflow-hidden">
          {/* Subtle Grid Overlay */}
          <div className="absolute inset-0 pointer-events-none opacity-[0.03]" style={{ backgroundImage: 'radial-gradient(#ffffff 1px, transparent 1px)', backgroundSize: '24px 24px' }} />
          
          <CardHeader className="text-center pt-8">
            <div className="w-12 h-12 bg-amber-500/20 border border-amber-500/30 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Database className="text-amber-500 w-6 h-6" />
            </div>
            <h1 className="text-xl font-bold text-white tracking-tight">
              Dev Bypass: Seed Foundation
            </h1>
            <p className="text-sm text-zinc-500 font-light">
              Skip the 21-screen onboarding and populate your workspace with "Verdant Naturals" demo data.
            </p>
          </CardHeader>

          <CardContent className="space-y-4">
            <div className="bg-[#121212] border border-zinc-800 p-4 rounded-lg space-y-2">
              <div className="flex items-center justify-between text-[10px] font-mono uppercase font-bold text-zinc-600">
                <span>Dataset Profile</span>
                <span className="text-green-500 text-[8px]">Ready</span>
              </div>
              <p className="text-xs text-zinc-400 leading-none">Business: <span className="text-white">Verdant Naturals</span></p>
              <p className="text-xs text-zinc-400 leading-none">Strategist: <span className="text-amber-500">ARIA</span></p>
            </div>

            {error && (
              <div className="text-xs bg-red-500/10 border border-red-500/20 p-2 text-red-400 text-center font-mono">
                {error}
              </div>
            )}
          </CardContent>

          <CardFooter className="pb-8">
            <Button 
              onClick={handleSeed} 
              disabled={loading}
              className="w-full bg-amber-500 hover:bg-amber-400 text-black font-bold uppercase tracking-widest h-12 flex items-center justify-center gap-2"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Rocket className="w-4 h-4" />
              )}
              {loading ? "Seeding Account..." : "Seed & Enter RaptorFlow"}
            </Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}
