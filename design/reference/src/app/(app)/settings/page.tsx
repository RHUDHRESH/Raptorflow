"use client";

import type * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { useUser, useOrganization } from "@clerk/nextjs";
import { GsapBridge } from "@/components/ui/gsap-bridge";
import { GearIcon, IdCardIcon, AvatarIcon, Link1Icon } from "@radix-ui/react-icons";

export default function SettingsPage(): React.ReactElement {
  const { user, isLoaded: userLoaded } = useUser();
  const { organization, isLoaded: orgLoaded } = useOrganization();

  return (
    <div className="min-h-[calc(100vh-theme(spacing.16))] bg-[var(--background)] px-6 py-12 md:px-12 font-body">
      <GsapBridge stagger={true} className="mx-auto max-w-[1200px] flex flex-col md:flex-row gap-12">
        
        {/* Left Nav */}
        <aside className="gsap-reveal w-full md:w-64 shrink-0">
          <h1 className="font-[family-name:var(--font-display)] text-5xl mb-8">Settings</h1>
          <nav className="flex flex-col space-y-2 font-mono text-xs uppercase tracking-widest">
            <Link href={"/settings" as Route} className="flex items-center gap-3 bg-[var(--primary)] text-[var(--primary-foreground)] px-4 py-3">
              <GearIcon className="h-4 w-4" /> Workspace
            </Link>
            <Link href={"/billing" as Route} className="flex items-center gap-3 hover:bg-[var(--accent)] text-[var(--foreground)] px-4 py-3 transition-colors">
              <IdCardIcon className="h-4 w-4" /> Billing & Plan
            </Link>
            <button className="flex items-center gap-3 hover:bg-[var(--accent)] text-[var(--foreground)] px-4 py-3 transition-colors text-left">
              <AvatarIcon className="h-4 w-4" /> Team Access
            </button>
            <button className="flex items-center gap-3 hover:bg-[var(--accent)] text-[var(--foreground)] px-4 py-3 transition-colors text-left">
              <Link1Icon className="h-4 w-4" /> Integrations
            </button>
          </nav>
        </aside>

        {/* Main Content */}
        <div className="flex-1 space-y-16">
          
          <section className="gsap-reveal border-t-2 border-[var(--foreground)] pt-6">
            <h2 className="font-mono text-xs uppercase tracking-widest text-[var(--muted-foreground)] mb-8">Organization Profile</h2>
            
            <div className="grid md:grid-cols-2 gap-12">
              <div className="space-y-4">
                <label className="font-mono text-[10px] uppercase tracking-widest block text-[var(--muted-foreground)]">Workspace Name</label>
                <input 
                  type="text" 
                  defaultValue={organization?.name || "RaptorFlow Workspace"} 
                  className="w-full bg-transparent border-b border-[var(--border)] focus:border-[var(--primary)] outline-none py-2 font-[family-name:var(--font-display)] text-2xl transition-colors"
                />
              </div>
              <div className="space-y-4">
                <label className="font-mono text-[10px] uppercase tracking-widest block text-[var(--muted-foreground)]">Workspace ID</label>
                <div className="py-2 text-sm font-mono text-[var(--muted-foreground)]">{organization?.id || "org_pending"}</div>
              </div>
            </div>
            
            <button className="mt-8 bg-[var(--primary)] text-[var(--primary-foreground)] px-8 h-12 font-mono text-xs uppercase tracking-widest hover:opacity-90 transition-opacity">
              Save Changes
            </button>
          </section>

          <section className="gsap-reveal border-t border-[var(--border)] pt-6">
            <h2 className="font-mono text-xs uppercase tracking-widest text-[var(--muted-foreground)] mb-8">Personal Account</h2>
            
            <div className="bg-[var(--card)] border border-[var(--border)] p-6 flex flex-col md:flex-row items-center gap-8">
               {userLoaded && user ? (
                  <>
                     {user.imageUrl ? (
                       // eslint-disable-next-line @next/next/no-img-element
                       <img src={user.imageUrl} alt={user.fullName ?? "User"} className="h-20 w-20 grayscale border border-[var(--border)]" />
                     ) : (
                       <div className="h-20 w-20 bg-[var(--accent)] border border-[var(--border)] flex items-center justify-center font-[family-name:var(--font-display)] text-2xl text-[var(--muted-foreground)]">
                         {user.fullName?.charAt(0) || "U"}
                       </div>
                     )}
                     <div className="flex-1 text-center md:text-left">
                       <h3 className="font-[family-name:var(--font-display)] text-2xl mb-1">{user.fullName ?? "Unknown"}</h3>
                       <p className="font-mono text-xs text-[var(--muted-foreground)]">{user.primaryEmailAddress?.emailAddress}</p>
                     </div>
                  </>
               ) : (
                 <div className="h-20 w-full animate-pulse bg-[var(--muted)]" />
               )}
               
               <button className="border border-[var(--border)] bg-transparent hover:bg-[var(--accent)] px-6 h-10 font-mono text-[10px] uppercase tracking-widest transition-colors">
                 Manage Auth
               </button>
            </div>
          </section>

          <section className="gsap-reveal border-t border-[var(--border)] pt-6">
            <h2 className="font-mono text-xs uppercase tracking-widest text-[var(--destructive)] mb-8">Danger Zone</h2>
            
            <div className="border border-[var(--destructive)] bg-[var(--destructive)]/5 p-6 md:p-8">
              <h3 className="font-[family-name:var(--font-display)] text-2xl mb-2 text-[var(--destructive)]">Erase Workspace</h3>
              <p className="text-[var(--muted-foreground)] text-sm mb-6 max-w-xl">
                This will permanently destroy the foundation, council logs, active campaigns, and intelligence streams. This action cannot be undone.
              </p>
              <button className="bg-[var(--destructive)] text-[var(--destructive-foreground)] px-8 h-12 font-mono text-[10px] uppercase tracking-widest hover:bg-[var(--destructive)]/90 transition-opacity">
                Acknowledge and Delete
              </button>
            </div>
          </section>

        </div>
      </GsapBridge>
    </div>
  );
}

