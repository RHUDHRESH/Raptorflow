"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import gsap from "gsap";
import { Check, Compass, ArrowRight } from "lucide-react";
import dynamic from 'next/dynamic';
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { getEnvironmentSummary } from "@/lib/env-validation";
import { getSupabaseClient } from '@/lib/supabase-auth';

const BlueprintButton = dynamic(() => import("@/components/ui/BlueprintButton").then(mod => ({ default: mod.BlueprintButton })), { ssr: false });
const SecondaryButton = dynamic(() => import("@/components/ui/BlueprintButton").then(mod => ({ default: mod.SecondaryButton })), { ssr: false });

export const runtime = 'edge';

const PLANS = [
  {
    name: "Ascent",
    price: "₹5,000",
    desc: "For founders just getting started with systematic marketing.",
    features: ["Foundation setup (ICP + Positioning)", "Weekly Moves (3 per week)", "Basic Muse AI generation", "Matrix analytics dashboard", "3 Active Campaigns"],
    code: "PLN-ASCENT",
    popular: false
  },
  {
    name: "Glide",
    price: "₹7,000",
    desc: "For founders scaling their marketing engine.",
    features: ["Everything in Ascent", "Unlimited Moves", "Advanced Muse (voice training)", "Cohort segmentation", "Campaign planning tools", "Priority support"],
    code: "PLN-GLIDE",
    popular: true
  },
  {
    name: "Soar",
    price: "₹10,000",
    desc: "For teams running multi-channel campaigns.",
    features: ["Everything in Glide", "Unlimited Team seats", "White-label exports", "Custom AI training", "Full API access", "Dedicated success manager"],
    code: "PLN-SOAR",
    popular: false
  }
];

export default function PricingPage() {
  const router = useRouter();
  const pageRef = useRef<HTMLDivElement>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [userName, setUserName] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check authentication status and load user data
    const checkAuth = async () => {
      try {
        const supabase = getSupabaseClient();
        const { data: { session } } = await supabase.auth.getSession();

        if (session?.user) {
          setIsAuthenticated(true);
          setUserEmail(session.user.email || null);

          // Load user profile data
          const { data: profile } = await supabase
            .from('profiles')
            .select('full_name, onboarding_status')
            .eq('id', session.user.id)
            .single();

          if (profile) {
            setUserName(profile.full_name || session.user.email?.split('@')[0] || 'User');
          }
        }
      } catch (error) {
        console.log('Auth check failed:', error);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();

    // Debug environment
    console.log('🔍 Pricing Page Environment Debug:');
    console.log(getEnvironmentSummary());
    console.log('Current URL:', window.location.href);
    console.log('Hostname:', window.location.hostname);

    if (!pageRef.current) return;
    const tl = gsap.timeline({ defaults: { ease: "power2.out" } });
    tl.fromTo("[data-anim-hero]", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6 });
    tl.fromTo("[data-anim-card]", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.5, stagger: 0.1 }, "-=0.3");
  }, []);

  const handlePlanSelect = (planName: string) => {
    if (isAuthenticated) {
      // User is authenticated, go to dashboard
      router.push('/dashboard');
    } else {
      // User not authenticated, go to signup
      router.push('/signup');
    }
  };

  return (
    <div ref={pageRef} className="min-h-screen bg-[var(--canvas)] relative overflow-hidden">
      <div className="fixed inset-0 pointer-events-none z-0" style={{ backgroundImage: "url('/textures/paper-grain.png')", opacity: 0.05, mixBlendMode: "multiply" }} />
      <div className="fixed inset-0 blueprint-grid pointer-events-none z-0 opacity-30" />

      {/* Nav */}
      <div className="relative z-10 flex justify-between items-center px-8 py-6 max-w-7xl mx-auto">
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => router.push('/')}>
          <Compass size={24} /> <span className="font-serif font-bold text-lg">RaptorFlow</span>
        </div>
        <div className="flex gap-4">
          {isLoading ? (
            <span className="text-sm font-technical text-[var(--muted)]">Loading...</span>
          ) : isAuthenticated ? (
            <>
              <span className="text-sm font-technical text-[var(--muted)]">Welcome, {userName}</span>
              <BlueprintButton size="sm" onClick={() => router.push('/dashboard')}>DASHBOARD</BlueprintButton>
            </>
          ) : (
            <>
              <button onClick={() => router.push('/login')} className="text-sm font-technical text-[var(--muted)] hover:text-[var(--ink)]">LOG IN</button>
              <BlueprintButton size="sm" onClick={() => router.push('/signup')}>START NOW</BlueprintButton>
            </>
          )}
        </div>
      </div>

      <div className="relative z-10 py-20 px-4">
        <div className="text-center mb-20" data-anim-hero>
          <h1 className="font-serif text-6xl text-[var(--ink)] mb-4">Pricing that scales.</h1>
          <p className="text-xl text-[var(--secondary)] max-w-2xl mx-auto font-light">
            Simple, transparent pricing for serious founders. No hidden fees. Cancel anytime.
          </p>
          {isAuthenticated && (
            <p className="text-sm text-[var(--blueprint)] mt-4">
              ✅ You're authenticated! Choose a plan to get started.
            </p>
          )}
        </div>

        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
          {PLANS.map((plan, i) => (
            <div key={i} data-anim-card className={`relative ${plan.popular ? '-mt-4' : ''}`}>
              {plan.popular && (
                <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 z-20">
                  <BlueprintBadge variant="blueprint">MOST POPULAR</BlueprintBadge>
                </div>
              )}
              <BlueprintCard
                code={plan.code}
                showCorners
                padding="lg"
                variant={plan.popular ? "elevated" : "default"}
                className={`h-full ${plan.popular ? 'border-[var(--blueprint)] ring-1 ring-[var(--blueprint)]' : ''}`}
              >
                <h3 className="font-serif text-2xl text-[var(--ink)] mb-2">{plan.name}</h3>
                <div className="flex items-baseline gap-1 mb-2">
                  <span className="text-4xl font-bold text-[var(--ink)]">{plan.price}</span>
                  <span className="text-sm text-[var(--muted)]">/ month</span>
                </div>
                <p className="text-sm text-[var(--secondary)] mb-8 min-h-[40px]">{plan.desc}</p>

                <BlueprintButton
                  variant={plan.popular ? "blueprint" : "default"}
                  className="w-full mb-8"
                  onClick={() => handlePlanSelect(plan.name)}
                >
                  {isAuthenticated ? `Continue with ${plan.name}` : `Start Now with ${plan.name}`}
                </BlueprintButton>

                <div className="space-y-3">
                  {plan.features.map((feat, j) => (
                    <div key={j} className="flex items-start gap-3 text-sm text-[var(--ink)]">
                      <div className="mt-0.5 p-0.5 rounded-full bg-[var(--success-light)] text-[var(--success)]">
                        <Check size={10} strokeWidth={3} />
                      </div>
                      {feat}
                    </div>
                  ))}
                </div>
              </BlueprintCard>
            </div>
          ))}
        </div>

        <div className="max-w-3xl mx-auto mt-24 text-center border-t border-[var(--border)] pt-12">
          <h3 className="font-serif text-2xl mb-4">Enterprise Custom</h3>
          <p className="text-[var(--secondary)] mb-6">Need custom integrations, SLA, or on-premise deployment?</p>
          <SecondaryButton onClick={() => router.push('/help')}>Contact Sales <ArrowRight size={14} /></SecondaryButton>
        </div>
      </div>
    </div>
  );
}
