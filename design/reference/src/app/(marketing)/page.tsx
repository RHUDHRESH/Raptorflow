import type * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { ArrowRightIcon, CheckIcon, PlayIcon } from "@radix-ui/react-icons";
import { Button } from "@/components/ui/button";
import { GsapBridge } from "@/components/ui/gsap-bridge";

const AGENTS = [
  { name: "David Ogilvy", role: "Ad Copy Strategy", desc: "Crafts copy that persuades through precision and proof." },
  { name: "Gary Vaynerchuk", role: "Growth & Viral", desc: "Attention arbitrage and raw distribution tactics." },
  { name: "Seth Godin", role: "Positioning & Tribes", desc: "Finds the permission asset and the remarkable angle." },
  { name: "Claude Hopkins", role: "Scientific Advertising", desc: "Reason-why copy and measurable outcomes." },
  { name: "Al Ries", role: "Positioning Strategy", desc: "Owning a word in the prospect's mind." },
  { name: "Lester Wunderman", role: "Direct Marketing", desc: "Action-oriented accountability and response loops." },
];

export default function MarketingHome(): React.ReactElement {
  return (
    <main className="min-h-screen bg-[var(--background)] text-[var(--foreground)] selection:bg-[var(--foreground)] selection:text-[var(--background)] pb-24">
      
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 mix-blend-difference text-white">
        <div className="mx-auto flex max-w-[1400px] items-center justify-between p-6">
          <div className="font-[family-name:var(--font-display)] text-2xl font-bold tracking-tight">RAPTORFLOW</div>
          <div className="flex items-center gap-6 text-sm uppercase tracking-widest font-mono">
            <Link href={"/sign-in" as Route} className="hover:opacity-70 transition-opacity">Sign in</Link>
            <Link href={"/sign-up" as Route} className="border border-white px-5 py-2 hover:bg-white hover:text-black transition-colors rounded-none">Get Access</Link>
          </div>
        </div>
      </nav>

      <GsapBridge stagger={true}>
        
        {/* Section 1: Hero */}
        <section className="relative flex min-h-[95vh] flex-col items-center justify-center px-6 pt-24 text-center">
          <div className="absolute inset-0 bg-gradient-to-b from-transparent to-[var(--background)] z-0" />
          <div className="relative z-10 max-w-5xl space-y-10">
            <h1 className="gsap-reveal font-[family-name:var(--font-display)] text-6xl md:text-8xl lg:text-[7rem] leading-[0.9] tracking-tighter text-[var(--primary)]">
              Your Marketing Office.
              <br />
              <span className="italic text-[var(--muted-foreground)]">Staffed by 21 AI Strategists.</span>
            </h1>
            
            <p className="gsap-reveal mx-auto max-w-2xl text-xl md:text-2xl font-light leading-relaxed text-[var(--muted-foreground)]">
              Stop managing a tool. Start managing a team. A sophisticated OS that drives strategy, debates campaigns, and generates assets.
            </p>
            
            <div className="gsap-reveal flex flex-col sm:flex-row items-center justify-center gap-6 pt-8">
              <Button asChild size="lg" className="rounded-none bg-[var(--primary)] text-[var(--primary-foreground)] hover:bg-[var(--primary)] hover:opacity-90 h-14 px-10 text-lg font-medium border border-[var(--primary)]">
                <Link href={"/sign-up" as Route}>Start Free Trial <ArrowRightIcon className="ml-2 h-5 w-5" /></Link>
              </Button>
              <Button asChild size="lg" variant="outline" className="rounded-none border-[var(--border)] text-[var(--primary)] hover:bg-[var(--accent)] h-14 px-8 text-lg bg-transparent">
                <Link href="#demo"><PlayIcon className="mr-2 h-5 w-5" /> Watch Demo</Link>
              </Button>
            </div>
            
            <div className="gsap-reveal flex items-center justify-center gap-4 pt-12 text-sm font-mono uppercase tracking-widest text-[var(--muted-foreground)] opacity-70">
              <span>Built for Indian SMBs</span>
              <span className="h-1 w-1 bg-[var(--muted-foreground)] rounded-full" />
              <span>₹5,000/month</span>
              <span className="h-1 w-1 bg-[var(--muted-foreground)] rounded-full" />
              <span>No setup fees</span>
            </div>
          </div>
        </section>

        {/* Section 2: Problem / Solution */}
        <section className="mx-auto max-w-[1400px] px-6 py-32 space-y-24 border-t border-[var(--border)]">
          <div className="max-w-4xl">
            <h2 className="gsap-reveal font-[family-name:var(--font-display)] text-5xl tracking-tight">Solving the Real Problem of Marketing Intelligence.</h2>
            <p className="gsap-reveal mt-6 text-xl text-[var(--muted-foreground)] leading-relaxed">
              You're wearing 21 hats. Sales hat. Copywriting hat. Analytics hat. Competitive strategy hat. You're competent at some of these. You're faking it at most of them.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-12 border border-[var(--border)] relative bg-[var(--card)] p-12">
            <div className="gsap-reveal space-y-6">
              <div className="h-12 w-12 border border-[var(--primary)] flex items-center justify-center text-xl font-mono">01</div>
              <h3 className="text-2xl font-bold font-[family-name:var(--font-display)]">Doing it alone</h3>
              <ul className="space-y-3 text-[var(--muted-foreground)] font-mono text-sm">
                <li className="flex items-start gap-2">- Limited time to execute</li>
                <li className="flex items-start gap-2">- Massive gaps in expertise</li>
                <li className="flex items-start gap-2">- No competitive monitoring</li>
              </ul>
            </div>
            
            <div className="gsap-reveal space-y-6 relative">
              <div className="absolute top-0 bottom-0 left-[-24px] w-[1px] bg-[var(--border)] hidden md:block" />
              <div className="h-12 w-12 border border-[var(--primary)] flex items-center justify-center text-xl font-mono">02</div>
              <h3 className="text-2xl font-bold font-[family-name:var(--font-display)]">The structural gap</h3>
              <p className="text-[var(--muted-foreground)] font-mono text-sm leading-relaxed">
                Traditional tools require you to know what to ask. They give you a blank canvas. You need a team that brings proactive intelligence to the table.
              </p>
            </div>

            <div className="gsap-reveal space-y-6 relative">
              <div className="absolute top-0 bottom-0 left-[-24px] w-[1px] bg-[var(--border)] hidden md:block" />
              <div className="h-12 w-12 bg-[var(--primary)] text-[var(--primary-foreground)] flex items-center justify-center text-xl font-mono">03</div>
              <h3 className="text-2xl font-bold font-[family-name:var(--font-display)]">21 Full-time experts</h3>
              <ul className="space-y-3 text-[var(--muted-foreground)] font-mono text-sm">
                <li className="flex items-start gap-2">- Works on your business</li>
                <li className="flex items-start gap-2">- Learns from your data</li>
                <li className="flex items-start gap-2">- Never sleeps, never stops</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Section 3: Agents Gallery */}
        <section className="bg-[var(--primary)] text-[var(--primary-foreground)] py-32 px-6">
          <div className="mx-auto max-w-[1400px]">
            <div className="max-w-3xl mb-24">
              <h2 className="gsap-reveal font-[family-name:var(--font-display)] text-5xl lg:text-7xl">Meet Your Executives</h2>
              <p className="gsap-reveal mt-6 text-xl text-[var(--accent)]/70 font-light">All 21 agents. All at your desk. They argue, they debate, they refine your vision until it's sharp.</p>
            </div>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-[1px] bg-white/10 border border-white/10 p-[1px]">
              {AGENTS.map((agent, i) => (
                <div key={i} className="gsap-reveal bg-[var(--primary)] hover:bg-[#1A1619] transition-colors p-10 group relative border border-transparent">
                  <div className="absolute top-4 right-4 text-white/20 font-mono text-xs">{String(i + 1).padStart(2, '0')}</div>
                  <h3 className="text-2xl font-[family-name:var(--font-display)] mb-2">{agent.name}</h3>
                  <div className="text-xs uppercase tracking-widest text-[#DBCDB6] font-mono mb-6">{agent.role}</div>
                  <p className="text-[#EAE6DB]/70">{agent.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Section 4: Workflow */}
        <section className="mx-auto max-w-[1400px] px-6 py-32 border-b border-[var(--border)]">
          <h2 className="gsap-reveal font-[family-name:var(--font-display)] text-5xl tracking-tight mb-20">The RaptorFlow Method</h2>
          
          <div className="space-y-16 lg:space-y-0 lg:grid lg:grid-cols-5 lg:gap-8">
            {[
              { title: "Build Foundation", desc: "21 strategic questions. 20 minutes of thinking. Your unique blueprint." },
              { title: "Agents Trained", desc: "They read your Foundation. They learn your ICP and competitive landscape." },
              { title: "Daily Briefings", desc: "Every morning: what changed overnight, what competitors did." },
              { title: "Campaign Planning", desc: "Write a brief. The Council debates it. 3+ distinct perspectives." },
              { title: "Continuous Learning", desc: "Each campaign teaches the system. Month 6 is smarter than Month 1." }
            ].map((step, i) => (
              <div key={i} className="gsap-reveal border-t-2 border-[var(--primary)] pt-6">
                <div className="text-4xl font-[family-name:var(--font-display)] text-[var(--muted-foreground)]/40 mb-4">{String(i + 1).padStart(2, '0')}</div>
                <h3 className="text-xl font-bold mb-3">{step.title}</h3>
                <p className="text-[var(--muted-foreground)] text-sm leading-relaxed">{step.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Section 6: Pricing & Footer CTA */}
        <section className="mx-auto max-w-[1400px] px-6 py-32 text-center">
          <div className="gsap-reveal inline-block border border-[var(--border)] bg-[var(--card)] p-12 lg:p-24 w-full max-w-4xl shadow-xl shadow-[var(--primary)]/5">
            <h2 className="font-[family-name:var(--font-display)] text-7xl mb-4">₹5,000<span className="text-2xl text-[var(--muted-foreground)]">/mo</span></h2>
            <p className="font-mono text-[var(--muted-foreground)] uppercase tracking-widest text-sm mb-12">One workspace. 21 agents. Everything included.</p>
            
            <div className="flex flex-col md:flex-row justify-center gap-8 mb-16 text-sm text-[var(--foreground)] text-left">
              <div className="flex items-center gap-3"><CheckIcon className="h-4 w-4" /> Unlimited campaigns</div>
              <div className="flex items-center gap-3"><CheckIcon className="h-4 w-4" /> Daily intelligence briefings</div>
              <div className="flex items-center gap-3"><CheckIcon className="h-4 w-4" /> Council debate sessions</div>
            </div>

            <Button asChild size="lg" className="rounded-none bg-[var(--primary)] text-[var(--primary-foreground)] h-16 px-16 text-xl">
              <Link href={"/sign-up" as Route}>Build Your Office</Link>
            </Button>
            <p className="mt-6 text-sm text-[var(--muted-foreground)]">14-day free trial. No credit card required.</p>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-[var(--border)] bg-[#100E0F] text-[#EAE6DB] py-12 px-6">
          <div className="mx-auto max-w-[1400px] flex flex-col md:flex-row items-center justify-between font-mono text-xs uppercase tracking-widest opacity-60">
            <div className="mb-4 md:mb-0">© 2026 RAPTORFLOW OS</div>
            <div className="flex gap-8">
              <Link href="#" className="hover:text-white transition-colors">Privacy</Link>
              <Link href="#" className="hover:text-white transition-colors">Terms</Link>
              <Link href="#" className="hover:text-white transition-colors">Docs</Link>
            </div>
          </div>
        </footer>

      </GsapBridge>
    </main>
  );
}
