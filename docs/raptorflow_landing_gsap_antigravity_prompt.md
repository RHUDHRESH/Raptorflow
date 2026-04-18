# RaptorFlow Landing Page Build Prompt - Exhaustive GSAP Spec

Give this entire markdown file to Antigravity.

This is not a planning note.
This is the build instruction.

The task is to build a serious, premium, dark, story-driven RaptorFlow landing page using GSAP.

No generated image assets.
No external assets.
No hidden product reveal.
No workplace metaphors.
No generic SaaS hero.
No backend work.
No authenticated app work.

The page must sell RaptorFlow through:

- Indian SMB pain
- story-brand clarity
- disciplined marketing execution
- Foundation
- Campaigns
- Muse
- Intel
- Daily Wins
- Council
- compounding memory
- pricing: Ascend, Glide, Soar

---

## 001. Role

You are Antigravity acting as a senior frontend engineer, GSAP motion designer, and conversion-focused landing page builder.

Your job is to build the public landing page only.

You must ship a page that feels like a premium dark operating system for marketing execution.

You must not build a cute marketing site.

You must not build a generic AI landing page.

You must not build an image-heavy landing page.

You must use CSS, SVG, HTML, Tailwind, and GSAP to create the visual system.

---

## 002. Repo Context

Repository:

```txt
Raptorflow
```

Frontend app:

```txt
apps/web
```

Likely public marketing route:

```txt
apps/web/src/app/(marketing)/page.tsx
```

Possible component folder:

```txt
apps/web/src/components/landing
```

The project already uses:

- Next.js 15
- React 19
- TypeScript
- Tailwind CSS 4
- GSAP
- @gsap/react
- lucide-react
- Clerk auth routes

Use what exists.

Do not install new packages unless absolutely unavoidable.

---

## 003. Absolute Scope

Allowed:

- Public landing route
- Landing components
- Landing copy constants
- Landing motion helpers
- Tiny globals.css utilities if needed
- Route helper updates for `/sign-in` and `/sign-up` only if needed

Forbidden:

- Backend Rust files
- Database files
- Schemas
- OpenAPI
- Foundation onboarding
- App dashboard pages
- Campaign app pages
- Muse app pages
- Intel app pages
- Daily Wins app pages
- Council app pages
- Auth pages unless only linking to them
- Any surprise visual layer
- Any public mention of hidden internal visual surprises

---

## 004. Product Positioning

RaptorFlow is an AI-native marketing execution system for Indian SMBs.

It is not a chatbot.

It is not a caption generator.

It is not an agency marketplace.

It is not dashboard decoration.

It is a system that turns business context into campaign plans, competitor awareness, daily action, and compounding memory.

Core message:

```txt
Stop guessing what to do next in marketing.
```

Supporting message:

```txt
RaptorFlow understands your business, plans campaigns, watches competitor signals, and turns every day into one clear marketing action.
```

Founder-level promise:

```txt
Marketing stops being a scattered weekly panic and becomes a disciplined operating rhythm.
```

---

## 005. StoryBrand Logic

The customer is the hero.

RaptorFlow is the guide.

The villain is marketing chaos.

The external problem:

- Too many tools
- Too many tabs
- Too many disconnected decisions
- Too many people losing context

The internal problem:

- The founder feels alone
- The founder feels behind
- The founder feels like marketing should be obvious but never is
- The founder does not know which action matters today

The philosophical problem:

- A serious business should not have to restart its marketing brain every week

The plan:

1. Build Foundation
2. Run campaigns as systems
3. Ask Muse with full context
4. Watch competitor signals
5. Wake up to Daily Wins
6. Let memory compound over time

The call to action:

```txt
Start now
```

The success ending:

```txt
Every day, the founder knows the next serious marketing move.
```

The failure avoided:

```txt
Random content, wasted ad spend, expensive retainers, forgotten context, and generic AI output.
```

---

## 006. Tribe

The RaptorFlow tribe is Indian SMB operators who are done with random marketing.

They are not trying to look cool.

They are trying to make growth less chaotic.

They are serious.

They are resource-constrained but ambitious.

They do not want to be sold fluff.

They want execution.

They want clarity.

They want a memory layer.

They want to know what to do today.

Use copy like:

- You are not lazy. Your marketing system is leaking context.
- You do not need another caption generator.
- You do not need more tabs.
- You need one clear move today.
- Your business deserves marketing memory.
- Stop rebuilding context every Monday.

---

## 007. Visual Style

Use classic RaptorFlow visual language:

- deep charcoal backgrounds
- near-black surfaces
- zinc borders
- amber intelligence highlights
- fine-line diagrams
- floating dark cards
- subtle grid overlays
- subtle noise texture
- radial amber glow
- campaign maps
- memory lattices
- competitor radar arcs
- daily briefing cards
- serious editorial typography

Never use:

- bright pastel SaaS gradients
- big happy stock illustrations
- robots
- humanoid AI faces
- blue/purple primary CTAs
- generic 3D blobs
- childish icons
- confetti
- white backgrounds
- fake unreadable text baked into images
- any room/workplace imagery

---

## 008. Color System

Use these colors:

```txt
Page background: #0f0f0f
Main background: #121212
Section surface: #1a1a1a
Elevated card: #262626
Input/card inset: #1f1f1f
Subtle border: border-zinc-800
Strong border: border-zinc-700
Primary text: text-white
Secondary text: text-zinc-400
Muted text: text-zinc-500
Accent: amber-500
CTA: bg-amber-500 text-black hover:bg-amber-400
```

Amber means intelligence or action.

Gray means context.

White means primary reading.

Never use blue/purple as the main action color.

---

## 009. Typography

Use the existing app font stack.

Hero headline:

```txt
text-5xl md:text-7xl lg:text-8xl tracking-tight font-semibold
```

Section headlines:

```txt
text-4xl md:text-6xl tracking-tight font-semibold
```

Eyebrow labels:

```txt
text-xs uppercase tracking-[0.28em] text-amber-500
```

Body:

```txt
text-base md:text-lg text-zinc-400 leading-7
```

Card title:

```txt
text-lg md:text-xl text-white font-medium
```

Fine labels:

```txt
text-xs uppercase tracking-widest text-zinc-500
```

Make the site skimmable.

No wall-of-text sections.

---

## 010. GSAP Principles

Use GSAP for cinematic polish, not gimmicks.

Required animation primitives:

- `gsap.timeline()` for hero load sequencing
- `gsap.from()` for reveal animations
- `gsap.fromTo()` for nav background and SVG line drawing
- `ScrollTrigger` for scroll-based reveals
- `stagger` for cards and nodes
- parallax transforms for layered visual panels
- SVG path/line drawing with `scaleX`, `scaleY`, or stroke dash animation
- subtle amber node pulses

Use `useGSAP` from `@gsap/react`.

Scope animations to refs.

Respect reduced motion.

Do not scroll-hijack.

Do not pin every section.

Do not animate layout-heavy properties.

Animate mostly transform and opacity.

---

## 011. Required File Structure

Create or update:

```txt
apps/web/src/app/(marketing)/page.tsx
apps/web/src/components/landing/landing-page.tsx
apps/web/src/components/landing/landing-nav.tsx
apps/web/src/components/landing/landing-hero.tsx
apps/web/src/components/landing/landing-command-visual.tsx
apps/web/src/components/landing/landing-problem.tsx
apps/web/src/components/landing/landing-system.tsx
apps/web/src/components/landing/landing-foundation.tsx
apps/web/src/components/landing/landing-campaigns.tsx
apps/web/src/components/landing/landing-muse.tsx
apps/web/src/components/landing/landing-intel.tsx
apps/web/src/components/landing/landing-daily-wins.tsx
apps/web/src/components/landing/landing-council.tsx
apps/web/src/components/landing/landing-memory.tsx
apps/web/src/components/landing/landing-pricing.tsx
apps/web/src/components/landing/landing-final-cta.tsx
apps/web/src/components/landing/landing-section.tsx
apps/web/src/components/landing/landing-ui-primitives.tsx
apps/web/src/components/landing/landing-gsap-provider.tsx
apps/web/src/lib/landing-copy.ts
apps/web/src/lib/landing-motion.ts
```

Optional only if necessary:

```txt
apps/web/src/lib/routes.ts
apps/web/src/app/globals.css
```

Do not create asset folders.

Do not add images.

---

## 012. page.tsx

File:

```txt
apps/web/src/app/(marketing)/page.tsx
```

Purpose:

- Keep as server component if possible
- Export metadata
- Render `<LandingPage />`

Required metadata:

```ts
export const metadata = {
  title: "RaptorFlow - AI-native marketing execution for Indian SMBs",
  description:
    "RaptorFlow turns business context into campaigns, competitor intelligence, daily action, and compounding marketing memory.",
};
```

Do not place GSAP logic here.

---

## 013. landing-page.tsx

File:

```txt
apps/web/src/components/landing/landing-page.tsx
```

This is the main composer.

It should render:

1. LandingNav
2. LandingHero
3. LandingProblem
4. LandingSystem
5. LandingFoundation
6. LandingCampaigns
7. LandingMuse
8. LandingIntel
9. LandingDailyWins
10. LandingCouncil
11. LandingMemory
12. LandingPricing
13. LandingFinalCTA

Wrapper:

```tsx
<main className="min-h-screen overflow-x-hidden bg-[#0f0f0f] text-white">
```

Add subtle background noise/grid with CSS utility or inline backgrounds.

---

## 014. landing-copy.ts

File:

```txt
apps/web/src/lib/landing-copy.ts
```

Put all copy constants here.

Required exports:

- navLinks
- problemCards
- systemPillars
- campaignSteps
- pricingPlans
- memorySignals
- councilPerspectives

Exact nav links:

```ts
export const navLinks = [
  { label: "Problem", href: "#problem" },
  { label: "System", href: "#system" },
  { label: "Campaigns", href: "#campaigns" },
  { label: "Pricing", href: "#pricing" },
] as const;
```

Exact problem cards:

```ts
export const problemCards = [
  {
    title: "Agencies are expensive",
    body: "Good strategy often starts at retainers most SMBs cannot justify.",
  },
  {
    title: "Freelancers lose context",
    body: "When people change, your marketing memory disappears with them.",
  },
  {
    title: "DIY marketing is scattered",
    body: "Content, ads, competitors, analytics, and positioning live in different tabs.",
  },
  {
    title: "Generic AI is not enough",
    body: "A chatbot can write a caption. It cannot run a campaign system.",
  },
] as const;
```

Exact system pillars:

```ts
export const systemPillars = [
  {
    title: "Foundation",
    body: "RaptorFlow learns your ICP, positioning, competitors, goals, voice, and constraints before it gives advice.",
  },
  {
    title: "Campaigns",
    body: "Goals become moves, tasks, content actions, performance checks, and replanning signals.",
  },
  {
    title: "Muse",
    body: "Ask strategic or tactical questions with full business context already attached.",
  },
  {
    title: "Intel",
    body: "Competitor signals turn into usable response paths instead of vague alerts.",
  },
  {
    title: "Daily Wins",
    body: "Every morning, one clear action tells you what matters today.",
  },
] as const;
```

Exact pricing:

```ts
export const pricingPlans = [
  {
    name: "Ascend",
    price: "₹5,000",
    cadence: "/month",
    line: "For founders and small teams starting disciplined marketing execution.",
    features: [
      "Foundation",
      "Daily Wins",
      "Muse",
      "Campaign planning basics",
      "Core task management",
      "Basic Intel",
    ],
    cta: "Start with Ascend",
  },
  {
    name: "Glide",
    price: "₹7,000",
    cadence: "/month",
    line: "For growing SMBs that need stronger campaign rhythm and deeper visibility.",
    features: [
      "Everything in Ascend",
      "Deeper campaign planning",
      "Stronger Intel",
      "More active execution support",
      "Better performance review flow",
    ],
    cta: "Choose Glide",
    featured: true,
  },
  {
    name: "Soar",
    price: "₹10,000",
    cadence: "/month",
    line: "For serious operators who want a full marketing operating rhythm.",
    features: [
      "Everything in Glide",
      "Advanced campaigns",
      "More strategic reviews",
      "Priority intelligence",
      "Deeper memory and execution loops",
    ],
    cta: "Go with Soar",
  },
] as const;
```

Use INR only.

---

## 015. landing-motion.ts

File:

```txt
apps/web/src/lib/landing-motion.ts
```

Export:

```ts
export const landingMotion = {
  ease: "power3.out",
  softEase: "power2.out",
  duration: 0.8,
  fast: 0.45,
  stagger: 0.08,
  scrollStart: "top 75%",
  scrollOnce: true,
} as const;
```

Add helpers if useful:

```ts
export const revealFromBottom = {
  y: 36,
  opacity: 0,
  duration: 0.8,
  ease: "power3.out",
};
```

---

## 016. landing-gsap-provider.tsx

File:

```txt
apps/web/src/components/landing/landing-gsap-provider.tsx
```

Responsibilities:

- Register ScrollTrigger once
- Provide reduced motion hook
- Export utility hook if helpful

Implementation guidance:

```tsx
"use client";

import { useEffect, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

export function usePrefersReducedMotion() {
  const [reduced, setReduced] = useState(false);

  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduced(media.matches);
    const listener = () => setReduced(media.matches);
    media.addEventListener("change", listener);
    return () => media.removeEventListener("change", listener);
  }, []);

  return reduced;
}
```

If import path fails, adjust based on current GSAP package behavior.

---

## 017. landing-ui-primitives.tsx

File:

```txt
apps/web/src/components/landing/landing-ui-primitives.tsx
```

Create:

- SectionLabel
- AmberButton
- GhostButton
- DiagramCard
- MetricPill
- AmberLine

AmberButton:

- href prop
- children
- className optional
- uses `<a>` for marketing links
- bg-amber-500 text-black hover:bg-amber-400

GhostButton:

- border-zinc-700
- text-zinc-300
- hover:bg-zinc-900

SectionLabel:

- uppercase
- tracking wide
- amber text

DiagramCard:

- dark background
- border
- rounded-2xl
- subtle shadow

---

## 018. landing-section.tsx

File:

```txt
apps/web/src/components/landing/landing-section.tsx
```

Props:

```ts
type LandingSectionProps = {
  id?: string;
  eyebrow?: string;
  title?: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
  centered?: boolean;
};
```

Default layout:

```txt
relative mx-auto max-w-7xl px-6 py-24 lg:px-8 lg:py-32
```

Centered variant:

```txt
text-center max-w-4xl mx-auto
```

Do not overcomplicate.

---

## 019. Landing Nav

File:

```txt
apps/web/src/components/landing/landing-nav.tsx
```

Content:

- Left: RaptorFlow wordmark
- Center/right: Problem, System, Campaigns, Pricing
- Right: Sign in, Start now

Routes:

- Sign in: `/sign-in`
- Start now: `/sign-up`

Mobile:

- Hide center links
- Show wordmark + Start now

GSAP:

- Use fromTo on nav background when page scrolls
- transparent -> rgba(15,15,15,.86)
- backdropFilter blur(14px)
- borderBottomColor from transparent to rgba(63,63,70,.7)

Do not make nav huge.

---

## 020. Landing Hero

File:

```txt
apps/web/src/components/landing/landing-hero.tsx
```

Section id:

```txt
hero
```

Eyebrow:

```txt
AI-native marketing execution for Indian SMBs
```

Headline:

```txt
Stop guessing what to do next in marketing.
```

Body:

```txt
RaptorFlow understands your business, plans campaigns, watches competitor signals, and turns every day into one clear action.
```

Primary CTA:

```txt
Start now
```

Secondary CTA:

```txt
See how it works
```

Trust line:

```txt
Built for Indian SMBs that need strategy, execution, intelligence, and memory in one system.
```

Layout:

- full viewport or near-full viewport
- left: copy
- right: command visual
- background: dark grid/noise
- no images

GSAP:

- timeline entrance
- split headline into words manually
- stagger words
- reveal body
- reveal CTAs
- reveal command cards
- draw connector lines

---

## 021. Command Visual

File:

```txt
apps/web/src/components/landing/landing-command-visual.tsx
```

This is the hero visual.

No images.

Build with:

- div cards
- SVG paths
- CSS gradients
- amber glows
- grid background

Cards:

1. Foundation
2. Campaign
3. Intel
4. Daily Action
5. Memory

Central node:

```txt
Decision
```

It is okay for HTML text labels to be readable because they are real frontend text.

Do not put text into images.

Animation:

- cards stagger in
- lines draw
- amber node pulses subtly
- small dots travel along lines if simple

---

## 022. Problem Section

File:

```txt
apps/web/src/components/landing/landing-problem.tsx
```

Section id:

```txt
problem
```

Eyebrow:

```txt
The real problem
```

Title:

```txt
Marketing breaks when the owner has to remember everything.
```

Description:

```txt
RaptorFlow is built for operators who are tired of restarting strategy every week.
```

Cards:

Use `problemCards`.

Bottom thesis:

```txt
The issue is not effort. The issue is missing memory.
```

GSAP:

- card stagger reveal
- amber underline scaleX
- thesis fades in after cards

---

## 023. System Section

File:

```txt
apps/web/src/components/landing/landing-system.tsx
```

Section id:

```txt
system
```

Eyebrow:

```txt
The operating loop
```

Title:

```txt
One loop for strategy, campaigns, intelligence, and action.
```

Description:

```txt
RaptorFlow connects the parts of marketing that usually live in separate tabs.
```

Show five pillars:

- Foundation
- Campaigns
- Muse
- Intel
- Daily Wins

Each pillar card:

- number
- title
- one-line body
- small abstract glyph

Visual:

- horizontal or grid flow
- amber connector line

GSAP:

- ScrollTrigger reveal
- connector line draw
- active glow moves through cards

---

## 024. Foundation Section

File:

```txt
apps/web/src/components/landing/landing-foundation.tsx
```

Section id:

```txt
foundation
```

Eyebrow:

```txt
Foundation
```

Title:

```txt
The system starts with your business, not a blank prompt.
```

Body:

```txt
Foundation captures your ICP, positioning, competitors, pricing, channels, goals, voice, budget, assets, frustrations, and strategist style. That context powers every campaign and recommendation after it.
```

Visual:

- 21 tiny cards
- arranged as blueprint grid
- amber lines flow into one context core

Card labels can be:

- ICP
- Pricing
- Competitors
- Goals
- Voice
- Channels
- Budget
- Assets
- Positioning
- Frustrations
- Product
- Stage
- Tracking
- References
- Transformation
- Keywords
- History
- Customer
- Problem
- Strategy
- Constraints

GSAP:

- tiny cards stagger from opacity 0
- lines draw toward core
- core subtle pulse

---

## 025. Campaigns Section

File:

```txt
apps/web/src/components/landing/landing-campaigns.tsx
```

Section id:

```txt
campaigns
```

Eyebrow:

```txt
Campaign execution
```

Title:

```txt
Campaigns become living systems, not forgotten plans.
```

Body:

```txt
RaptorFlow turns a goal into moves, tasks, content actions, performance checks, and response loops.
```

Visual:

- goal node
- move nodes
- task nodes
- performance check
- next action

Cards:

1. Plan the move
2. Execute the task
3. Review the signal
4. Adjust the path

GSAP:

- horizontal timeline reveal
- nodes brighten as scroll progresses
- final action glows amber

---

## 026. Muse Section

File:

```txt
apps/web/src/components/landing/landing-muse.tsx
```

Section id:

```txt
muse
```

Eyebrow:

```txt
Muse
```

Title:

```txt
Ask with context already attached.
```

Body:

```txt
Muse is for tactical and strategic questions when you do not want to explain your business from scratch again.
```

Visual:

- question node
- passes through context layers
- returns recommendation card

Context layers:

- Foundation
- Active campaign
- Competitor signal
- Past result
- Daily priority

Avoid chatbot clichés.

No robot.

No face.

GSAP:

- node travels along SVG path
- layers reveal as node passes
- recommendation card appears last

---

## 027. Intel Section

File:

```txt
apps/web/src/components/landing/landing-intel.tsx
```

Section id:

```txt
intel
```

Eyebrow:

```txt
Intel
```

Title:

```txt
Competitor signals before they become surprises.
```

Body:

```txt
RaptorFlow watches market changes and turns useful signals into campaign response paths.
```

Visual:

- radar arcs
- competitor signal dots
- amber alert node
- response path card

Signals:

- Pricing shift
- Message change
- Ad movement
- SEO movement

GSAP:

- radar sweep rotates slowly
- signal dots reveal
- amber alert pulse

Keep it strategic, not cybersecurity.

---

## 028. Daily Wins Section

File:

```txt
apps/web/src/components/landing/landing-daily-wins.tsx
```

Section id:

```txt
daily-wins
```

Eyebrow:

```txt
Daily Wins
```

Title:

```txt
Wake up to one clear marketing move.
```

Body:

```txt
Every morning, RaptorFlow turns campaign status, competitor signals, and memory into one focused action.
```

Visual:

- dark briefing card
- one amber priority row
- three muted context rows

Rows:

- Campaign status
- Competitor signal
- Performance note

GSAP:

- card slides in
- priority row expands
- context rows stagger

---

## 029. Council Section

File:

```txt
apps/web/src/components/landing/landing-council.tsx
```

Section id:

```txt
council
```

Eyebrow:

```txt
Council
```

Title:

```txt
Better strategy comes from disagreement.
```

Body:

```txt
Multiple perspectives challenge a campaign decision, then RaptorFlow turns the tension into one practical plan.
```

Visual:

- 12 perspective nodes
- central synthesis path
- no people
- no table
- no room

GSAP:

- nodes light in sequence
- argument lines converge
- synthesis path draws in amber

---

## 030. Memory Section

File:

```txt
apps/web/src/components/landing/landing-memory.tsx
```

Section id:

```txt
memory
```

Eyebrow:

```txt
Compounding memory
```

Title:

```txt
Every campaign teaches the next one.
```

Body:

```txt
RaptorFlow remembers what worked, what failed, what was predicted, and what actually happened. The longer it works with you, the less generic it becomes.
```

Visual:

- memory lattice
- past outcome nodes
- prediction nodes
- future recommendation node
- thin amber links

GSAP:

- nodes reveal
- links draw
- future node brightens

This is one of the most important sections.

Make it feel novel.

---

## 031. Pricing Section

File:

```txt
apps/web/src/components/landing/landing-pricing.tsx
```

Section id:

```txt
pricing
```

Eyebrow:

```txt
Pricing
```

Title:

```txt
Pricing built for Indian SMBs.
```

Subtitle:

```txt
No fake free tier. No agency retainer shock. Choose the operating level your business needs.
```

Plans:

- Ascend - ₹5,000/month
- Glide - ₹7,000/month
- Soar - ₹10,000/month

Glide is featured.

Use amber border glow on Glide.

Do not add USD.

Do not add random enterprise card unless already present elsewhere.

GSAP:

- plan cards stagger upward
- Glide settles slightly later
- features reveal inside cards

---

## 032. Final CTA Section

File:

```txt
apps/web/src/components/landing/landing-final-cta.tsx
```

Section id:

```txt
final-cta
```

Title:

```txt
Stop restarting marketing from zero.
```

Body:

```txt
Start with Foundation. Build the memory layer. Turn strategy into daily execution.
```

Primary CTA:

```txt
Start now
```

Secondary CTA:

```txt
Sign in
```

Visual:

- scattered dark cards converge into one amber path
- no images

GSAP:

- scattered cards settle
- amber path draws
- CTA appears last

---

## 033. No-Asset Visual Techniques

Use these instead of images:

- CSS radial gradients
- CSS linear gradients
- SVG paths
- SVG circles
- div cards
- CSS grid backgrounds
- border glow
- pseudo-noise utility
- tiny animated amber dots
- mask gradients
- shadow layers
- blur only sparingly

Create diagrams from DOM elements.

Do not fetch images.

Do not link to remote assets.

Do not rely on public image files.

---

## 034. Minimal Globals CSS Additions

Only if needed, add:

```css
/* RaptorFlow landing utilities */
.landing-noise {
  background-image: radial-gradient(rgba(255,255,255,0.035) 1px, transparent 1px);
  background-size: 18px 18px;
}

.landing-grid {
  background-image:
    linear-gradient(rgba(245, 158, 11, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(245, 158, 11, 0.08) 1px, transparent 1px);
  background-size: 32px 32px;
}

.landing-amber-glow {
  box-shadow: 0 0 48px rgba(245, 158, 11, 0.18);
}
```

Do not rewrite existing globals.

---

## 035. Hero Animation Code Shape

Use this shape, adapted to the actual component:

```tsx
useGSAP(
  () => {
    if (reducedMotion) return;

    const tl = gsap.timeline({ defaults: { ease: "power3.out" } });

    tl.from(".hero-kicker", { y: 18, opacity: 0, duration: 0.5 })
      .from(".hero-word", { y: 54, opacity: 0, stagger: 0.045, duration: 0.8 }, "-=0.2")
      .from(".hero-copy", { y: 24, opacity: 0, duration: 0.65 }, "-=0.35")
      .from(".hero-cta", { y: 18, opacity: 0, stagger: 0.08, duration: 0.5 }, "-=0.25")
      .from(".command-card", { y: 24, opacity: 0, scale: 0.96, stagger: 0.08, duration: 0.7 }, "-=0.35")
      .from(".command-line", { scaleX: 0, transformOrigin: "left center", stagger: 0.05, duration: 0.6 }, "-=0.4");
  },
  { scope: rootRef }
);
```

Do not copy blindly if selectors differ.

Scope it properly.

---

## 036. Section Reveal Code Shape

Use this shape:

```tsx
useGSAP(
  () => {
    if (reducedMotion) return;

    gsap.from(".reveal-card", {
      y: 36,
      opacity: 0,
      duration: 0.8,
      stagger: 0.08,
      ease: "power3.out",
      scrollTrigger: {
        trigger: sectionRef.current,
        start: "top 75%",
        once: true,
      },
    });
  },
  { scope: sectionRef }
);
```

Use class names scoped inside each component.

---

## 037. SVG Line Drawing Code Shape

For simple lines:

```tsx
gsap.fromTo(
  ".diagram-line",
  { scaleX: 0 },
  {
    scaleX: 1,
    transformOrigin: "left center",
    ease: "none",
    scrollTrigger: {
      trigger: sectionRef.current,
      start: "top 70%",
      end: "bottom 45%",
      scrub: true,
    },
  }
);
```

For SVG paths using stroke dash:

```tsx
const paths = gsap.utils.toArray<SVGPathElement>(".draw-path");
paths.forEach((path) => {
  const length = path.getTotalLength();
  gsap.set(path, { strokeDasharray: length, strokeDashoffset: length });
  gsap.to(path, {
    strokeDashoffset: 0,
    ease: "none",
    scrollTrigger: {
      trigger: sectionRef.current,
      start: "top 75%",
      end: "bottom 50%",
      scrub: true,
    },
  });
});
```

Use whichever is simpler and build-safe.

---

## 038. Reduced Motion

If user prefers reduced motion:

- disable GSAP timelines
- show static cards
- no pulsing loops
- no moving dots
- no scrubbed diagrams

The page should still look premium.

---

## 039. Mobile Behavior

Mobile must be excellent.

Rules:

- Hero stacks vertically
- Command visual appears below copy
- Cards become one column
- Pricing becomes one column
- Nav links hidden
- CTA still visible
- No horizontal overflow
- Diagrams simplify
- Tiny labels can be hidden if cramped

Do not create tiny unreadable diagrams on mobile.

---

## 040. Build Commands

Run:

```bash
pnpm --filter @raptorflow/web typecheck
pnpm --filter @raptorflow/web build
```

If the filter is different, inspect package.json and use the correct command.

Fix all errors caused by this landing work.

---

## 041. Final Report Format

Return exactly:

1. Files changed
2. Landing route worked on
3. Sections built
4. GSAP animations implemented
5. CSS/SVG visuals created
6. CTA routes
7. Typecheck result
8. Build result
9. Anything unresolved

Do not suggest a roadmap.

Do not mention unrelated completed pages.

Do not say backend needs work.

Only report landing work.

---

## 042. Acceptance Standard

The landing is acceptable only if:

- It looks premium without external images
- It has a clear StoryBrand structure
- It speaks to Indian SMB founder pain
- It does not sound like generic AI SaaS
- It shows Foundation, Campaigns, Muse, Intel, Daily Wins, Council, and Memory
- It has three pricing tiers exactly
- It uses GSAP intentionally
- It is responsive
- It does not expose hidden internal visual surprises
- It does not touch backend
- It passes typecheck

---

## 043. Begin

Build the landing now.


## Micro QA Pass 1

- [01.01] Every section must earn its place.
- [01.02] Every visual must explain a system, not decorate the page.
- [01.03] Every animation must make the product easier to understand.
- [01.04] Every CTA must point to a real route.
- [01.05] Every pricing card must use INR.
- [01.06] Every public copy line must avoid hidden visual surprise references.
- [01.07] Every component must be build-safe.
- [01.08] Every imported file must exist.
- [01.09] Every GSAP selector must be scoped.
- [01.10] Every ScrollTrigger must avoid leaking on navigation.
- [01.11] Every mobile layout must avoid horizontal overflow.
- [01.12] Every hero line must speak to founder pain.
- [01.13] Every diagram must be CSS/SVG, not an image.
- [01.14] Every amber glow must represent action or intelligence.
- [01.15] Every dark card must have a clear hierarchy.
- [01.16] Every section headline must be understandable without body copy.
- [01.17] Every body paragraph must stay short.
- [01.18] Every grid must collapse cleanly on mobile.
- [01.19] Every repeated pattern must feel intentional.
- [01.20] Every final report line must include exact paths where relevant.

## Micro QA Pass 2

- [02.01] Every section must earn its place.
- [02.02] Every visual must explain a system, not decorate the page.
- [02.03] Every animation must make the product easier to understand.
- [02.04] Every CTA must point to a real route.
- [02.05] Every pricing card must use INR.
- [02.06] Every public copy line must avoid hidden visual surprise references.
- [02.07] Every component must be build-safe.
- [02.08] Every imported file must exist.
- [02.09] Every GSAP selector must be scoped.
- [02.10] Every ScrollTrigger must avoid leaking on navigation.
- [02.11] Every mobile layout must avoid horizontal overflow.
- [02.12] Every hero line must speak to founder pain.
- [02.13] Every diagram must be CSS/SVG, not an image.
- [02.14] Every amber glow must represent action or intelligence.
- [02.15] Every dark card must have a clear hierarchy.
- [02.16] Every section headline must be understandable without body copy.
- [02.17] Every body paragraph must stay short.
- [02.18] Every grid must collapse cleanly on mobile.
- [02.19] Every repeated pattern must feel intentional.
- [02.20] Every final report line must include exact paths where relevant.

## Micro QA Pass 3

- [03.01] Every section must earn its place.
- [03.02] Every visual must explain a system, not decorate the page.
- [03.03] Every animation must make the product easier to understand.
- [03.04] Every CTA must point to a real route.
- [03.05] Every pricing card must use INR.
- [03.06] Every public copy line must avoid hidden visual surprise references.
- [03.07] Every component must be build-safe.
- [03.08] Every imported file must exist.
- [03.09] Every GSAP selector must be scoped.
- [03.10] Every ScrollTrigger must avoid leaking on navigation.
- [03.11] Every mobile layout must avoid horizontal overflow.
- [03.12] Every hero line must speak to founder pain.
- [03.13] Every diagram must be CSS/SVG, not an image.
- [03.14] Every amber glow must represent action or intelligence.
- [03.15] Every dark card must have a clear hierarchy.
- [03.16] Every section headline must be understandable without body copy.
- [03.17] Every body paragraph must stay short.
- [03.18] Every grid must collapse cleanly on mobile.
- [03.19] Every repeated pattern must feel intentional.
- [03.20] Every final report line must include exact paths where relevant.

## Micro QA Pass 4

- [04.01] Every section must earn its place.
- [04.02] Every visual must explain a system, not decorate the page.
- [04.03] Every animation must make the product easier to understand.
- [04.04] Every CTA must point to a real route.
- [04.05] Every pricing card must use INR.
- [04.06] Every public copy line must avoid hidden visual surprise references.
- [04.07] Every component must be build-safe.
- [04.08] Every imported file must exist.
- [04.09] Every GSAP selector must be scoped.
- [04.10] Every ScrollTrigger must avoid leaking on navigation.
- [04.11] Every mobile layout must avoid horizontal overflow.
- [04.12] Every hero line must speak to founder pain.
- [04.13] Every diagram must be CSS/SVG, not an image.
- [04.14] Every amber glow must represent action or intelligence.
- [04.15] Every dark card must have a clear hierarchy.
- [04.16] Every section headline must be understandable without body copy.
- [04.17] Every body paragraph must stay short.
- [04.18] Every grid must collapse cleanly on mobile.
- [04.19] Every repeated pattern must feel intentional.
- [04.20] Every final report line must include exact paths where relevant.

## Micro QA Pass 5

- [05.01] Every section must earn its place.
- [05.02] Every visual must explain a system, not decorate the page.
- [05.03] Every animation must make the product easier to understand.
- [05.04] Every CTA must point to a real route.
- [05.05] Every pricing card must use INR.
- [05.06] Every public copy line must avoid hidden visual surprise references.
- [05.07] Every component must be build-safe.
- [05.08] Every imported file must exist.
- [05.09] Every GSAP selector must be scoped.
- [05.10] Every ScrollTrigger must avoid leaking on navigation.
- [05.11] Every mobile layout must avoid horizontal overflow.
- [05.12] Every hero line must speak to founder pain.
- [05.13] Every diagram must be CSS/SVG, not an image.
- [05.14] Every amber glow must represent action or intelligence.
- [05.15] Every dark card must have a clear hierarchy.
- [05.16] Every section headline must be understandable without body copy.
- [05.17] Every body paragraph must stay short.
- [05.18] Every grid must collapse cleanly on mobile.
- [05.19] Every repeated pattern must feel intentional.
- [05.20] Every final report line must include exact paths where relevant.

## Micro QA Pass 6

- [06.01] Every section must earn its place.
- [06.02] Every visual must explain a system, not decorate the page.
- [06.03] Every animation must make the product easier to understand.
- [06.04] Every CTA must point to a real route.
- [06.05] Every pricing card must use INR.
- [06.06] Every public copy line must avoid hidden visual surprise references.
- [06.07] Every component must be build-safe.
- [06.08] Every imported file must exist.
- [06.09] Every GSAP selector must be scoped.
- [06.10] Every ScrollTrigger must avoid leaking on navigation.
- [06.11] Every mobile layout must avoid horizontal overflow.
- [06.12] Every hero line must speak to founder pain.
- [06.13] Every diagram must be CSS/SVG, not an image.
- [06.14] Every amber glow must represent action or intelligence.
- [06.15] Every dark card must have a clear hierarchy.
- [06.16] Every section headline must be understandable without body copy.
- [06.17] Every body paragraph must stay short.
- [06.18] Every grid must collapse cleanly on mobile.
- [06.19] Every repeated pattern must feel intentional.
- [06.20] Every final report line must include exact paths where relevant.

## Micro QA Pass 7

- [07.01] Every section must earn its place.
- [07.02] Every visual must explain a system, not decorate the page.
- [07.03] Every animation must make the product easier to understand.
- [07.04] Every CTA must point to a real route.
- [07.05] Every pricing card must use INR.
- [07.06] Every public copy line must avoid hidden visual surprise references.
- [07.07] Every component must be build-safe.
- [07.08] Every imported file must exist.
- [07.09] Every GSAP selector must be scoped.
- [07.10] Every ScrollTrigger must avoid leaking on navigation.
- [07.11] Every mobile layout must avoid horizontal overflow.
- [07.12] Every hero line must speak to founder pain.
- [07.13] Every diagram must be CSS/SVG, not an image.
- [07.14] Every amber glow must represent action or intelligence.
- [07.15] Every dark card must have a clear hierarchy.
- [07.16] Every section headline must be understandable without body copy.
- [07.17] Every body paragraph must stay short.
- [07.18] Every grid must collapse cleanly on mobile.
- [07.19] Every repeated pattern must feel intentional.
- [07.20] Every final report line must include exact paths where relevant.

## Micro QA Pass 8

- [08.01] Every section must earn its place.
- [08.02] Every visual must explain a system, not decorate the page.
- [08.03] Every animation must make the product easier to understand.
- [08.04] Every CTA must point to a real route.
- [08.05] Every pricing card must use INR.
- [08.06] Every public copy line must avoid hidden visual surprise references.
- [08.07] Every component must be build-safe.
- [08.08] Every imported file must exist.
- [08.09] Every GSAP selector must be scoped.
- [08.10] Every ScrollTrigger must avoid leaking on navigation.
- [08.11] Every mobile layout must avoid horizontal overflow.
- [08.12] Every hero line must speak to founder pain.
- [08.13] Every diagram must be CSS/SVG, not an image.
- [08.14] Every amber glow must represent action or intelligence.
- [08.15] Every dark card must have a clear hierarchy.
- [08.16] Every section headline must be understandable without body copy.
- [08.17] Every body paragraph must stay short.
- [08.18] Every grid must collapse cleanly on mobile.
- [08.19] Every repeated pattern must feel intentional.
- [08.20] Every final report line must include exact paths where relevant.

## Micro QA Pass 9

- [09.01] Every section must earn its place.
- [09.02] Every visual must explain a system, not decorate the page.
- [09.03] Every animation must make the product easier to understand.
- [09.04] Every CTA must point to a real route.
- [09.05] Every pricing card must use INR.
- [09.06] Every public copy line must avoid hidden visual surprise references.
- [09.07] Every component must be build-safe.
- [09.08] Every imported file must exist.
- [09.09] Every GSAP selector must be scoped.
- [09.10] Every ScrollTrigger must avoid leaking on navigation.
- [09.11] Every mobile layout must avoid horizontal overflow.
- [09.12] Every hero line must speak to founder pain.
- [09.13] Every diagram must be CSS/SVG, not an image.
- [09.14] Every amber glow must represent action or intelligence.
- [09.15] Every dark card must have a clear hierarchy.
- [09.16] Every section headline must be understandable without body copy.
- [09.17] Every body paragraph must stay short.
- [09.18] Every grid must collapse cleanly on mobile.
- [09.19] Every repeated pattern must feel intentional.
- [09.20] Every final report line must include exact paths where relevant.

## Micro QA Pass 10

- [10.01] Every section must earn its place.
- [10.02] Every visual must explain a system, not decorate the page.
- [10.03] Every animation must make the product easier to understand.
- [10.04] Every CTA must point to a real route.
- [10.05] Every pricing card must use INR.
- [10.06] Every public copy line must avoid hidden visual surprise references.
- [10.07] Every component must be build-safe.
- [10.08] Every imported file must exist.
- [10.09] Every GSAP selector must be scoped.
- [10.10] Every ScrollTrigger must avoid leaking on navigation.
- [10.11] Every mobile layout must avoid horizontal overflow.
- [10.12] Every hero line must speak to founder pain.
- [10.13] Every diagram must be CSS/SVG, not an image.
- [10.14] Every amber glow must represent action or intelligence.
- [10.15] Every dark card must have a clear hierarchy.
- [10.16] Every section headline must be understandable without body copy.
- [10.17] Every body paragraph must stay short.
- [10.18] Every grid must collapse cleanly on mobile.
- [10.19] Every repeated pattern must feel intentional.
- [10.20] Every final report line must include exact paths where relevant.

## Micro QA Pass 11

- [11.01] Every section must earn its place.
- [11.02] Every visual must explain a system, not decorate the page.
- [11.03] Every animation must make the product easier to understand.
- [11.04] Every CTA must point to a real route.
- [11.05] Every pricing card must use INR.
- [11.06] Every public copy line must avoid hidden visual surprise references.
- [11.07] Every component must be build-safe.
- [11.08] Every imported file must exist.
- [11.09] Every GSAP selector must be scoped.
- [11.10] Every ScrollTrigger must avoid leaking on navigation.
- [11.11] Every mobile layout must avoid horizontal overflow.
- [11.12] Every hero line must speak to founder pain.
- [11.13] Every diagram must be CSS/SVG, not an image.
- [11.14] Every amber glow must represent action or intelligence.
- [11.15] Every dark card must have a clear hierarchy.
- [11.16] Every section headline must be understandable without body copy.
- [11.17] Every body paragraph must stay short.
- [11.18] Every grid must collapse cleanly on mobile.
- [11.19] Every repeated pattern must feel intentional.
- [11.20] Every final report line must include exact paths where relevant.

## Micro QA Pass 12

- [12.01] Every section must earn its place.
- [12.02] Every visual must explain a system, not decorate the page.
- [12.03] Every animation must make the product easier to understand.
- [12.04] Every CTA must point to a real route.
- [12.05] Every pricing card must use INR.
- [12.06] Every public copy line must avoid hidden visual surprise references.
- [12.07] Every component must be build-safe.
- [12.08] Every imported file must exist.
- [12.09] Every GSAP selector must be scoped.
- [12.10] Every ScrollTrigger must avoid leaking on navigation.
- [12.11] Every mobile layout must avoid horizontal overflow.
- [12.12] Every hero line must speak to founder pain.
- [12.13] Every diagram must be CSS/SVG, not an image.
- [12.14] Every amber glow must represent action or intelligence.
- [12.15] Every dark card must have a clear hierarchy.
- [12.16] Every section headline must be understandable without body copy.
- [12.17] Every body paragraph must stay short.
- [12.18] Every grid must collapse cleanly on mobile.
- [12.19] Every repeated pattern must feel intentional.
- [12.20] Every final report line must include exact paths where relevant.

## Micro QA Pass 13

- [13.01] Every section must earn its place.
- [13.02] Every visual must explain a system, not decorate the page.
- [13.03] Every animation must make the product easier to understand.
- [13.04] Every CTA must point to a real route.
- [13.05] Every pricing card must use INR.
- [13.06] Every public copy line must avoid hidden visual surprise references.
- [13.07] Every component must be build-safe.
- [13.08] Every imported file must exist.
- [13.09] Every GSAP selector must be scoped.
- [13.10] Every ScrollTrigger must avoid leaking on navigation.
- [13.11] Every mobile layout must avoid horizontal overflow.
- [13.12] Every hero line must speak to founder pain.
- [13.13] Every diagram must be CSS/SVG, not an image.
- [13.14] Every amber glow must represent action or intelligence.
- [13.15] Every dark card must have a clear hierarchy.
- [13.16] Every section headline must be understandable without body copy.
- [13.17] Every body paragraph must stay short.
- [13.18] Every grid must collapse cleanly on mobile.
- [13.19] Every repeated pattern must feel intentional.
- [13.20] Every final report line must include exact paths where relevant.

## Micro QA Pass 14

- [14.01] Every section must earn its place.
- [14.02] Every visual must explain a system, not decorate the page.
- [14.03] Every animation must make the product easier to understand.
- [14.04] Every CTA must point to a real route.
- [14.05] Every pricing card must use INR.
- [14.06] Every public copy line must avoid hidden visual surprise references.
- [14.07] Every component must be build-safe.
- [14.08] Every imported file must exist.
- [14.09] Every GSAP selector must be scoped.
- [14.10] Every ScrollTrigger must avoid leaking on navigation.
- [14.11] Every mobile layout must avoid horizontal overflow.
- [14.12] Every hero line must speak to founder pain.
- [14.13] Every diagram must be CSS/SVG, not an image.
- [14.14] Every amber glow must represent action or intelligence.
- [14.15] Every dark card must have a clear hierarchy.
- [14.16] Every section headline must be understandable without body copy.
- [14.17] Every body paragraph must stay short.
- [14.18] Every grid must collapse cleanly on mobile.
- [14.19] Every repeated pattern must feel intentional.
- [14.20] Every final report line must include exact paths where relevant.

## Micro QA Pass 15

- [15.01] Every section must earn its place.
- [15.02] Every visual must explain a system, not decorate the page.
- [15.03] Every animation must make the product easier to understand.
- [15.04] Every CTA must point to a real route.
- [15.05] Every pricing card must use INR.
- [15.06] Every public copy line must avoid hidden visual surprise references.
- [15.07] Every component must be build-safe.
- [15.08] Every imported file must exist.
- [15.09] Every GSAP selector must be scoped.
- [15.10] Every ScrollTrigger must avoid leaking on navigation.
- [15.11] Every mobile layout must avoid horizontal overflow.
- [15.12] Every hero line must speak to founder pain.
- [15.13] Every diagram must be CSS/SVG, not an image.
- [15.14] Every amber glow must represent action or intelligence.
- [15.15] Every dark card must have a clear hierarchy.
- [15.16] Every section headline must be understandable without body copy.
- [15.17] Every body paragraph must stay short.
- [15.18] Every grid must collapse cleanly on mobile.
- [15.19] Every repeated pattern must feel intentional.
- [15.20] Every final report line must include exact paths where relevant.

## Micro QA Pass 16

- [16.01] Every section must earn its place.
- [16.02] Every visual must explain a system, not decorate the page.
- [16.03] Every animation must make the product easier to understand.
- [16.04] Every CTA must point to a real route.
- [16.05] Every pricing card must use INR.
- [16.06] Every public copy line must avoid hidden visual surprise references.
- [16.07] Every component must be build-safe.
- [16.08] Every imported file must exist.
- [16.09] Every GSAP selector must be scoped.
- [16.10] Every ScrollTrigger must avoid leaking on navigation.
- [16.11] Every mobile layout must avoid horizontal overflow.
- [16.12] Every hero line must speak to founder pain.
- [16.13] Every diagram must be CSS/SVG, not an image.
- [16.14] Every amber glow must represent action or intelligence.
- [16.15] Every dark card must have a clear hierarchy.
- [16.16] Every section headline must be understandable without body copy.
- [16.17] Every body paragraph must stay short.
- [16.18] Every grid must collapse cleanly on mobile.
- [16.19] Every repeated pattern must feel intentional.
- [16.20] Every final report line must include exact paths where relevant.

## Micro QA Pass 17

- [17.01] Every section must earn its place.
- [17.02] Every visual must explain a system, not decorate the page.
- [17.03] Every animation must make the product easier to understand.
- [17.04] Every CTA must point to a real route.
- [17.05] Every pricing card must use INR.
- [17.06] Every public copy line must avoid hidden visual surprise references.
- [17.07] Every component must be build-safe.
- [17.08] Every imported file must exist.
- [17.09] Every GSAP selector must be scoped.
- [17.10] Every ScrollTrigger must avoid leaking on navigation.
- [17.11] Every mobile layout must avoid horizontal overflow.
- [17.12] Every hero line must speak to founder pain.
- [17.13] Every diagram must be CSS/SVG, not an image.
- [17.14] Every amber glow must represent action or intelligence.
- [17.15] Every dark card must have a clear hierarchy.
- [17.16] Every section headline must be understandable without body copy.
- [17.17] Every body paragraph must stay short.
- [17.18] Every grid must collapse cleanly on mobile.
- [17.19] Every repeated pattern must feel intentional.
- [17.20] Every final report line must include exact paths where relevant.

## Micro QA Pass 18

- [18.01] Every section must earn its place.
- [18.02] Every visual must explain a system, not decorate the page.
- [18.03] Every animation must make the product easier to understand.
- [18.04] Every CTA must point to a real route.
- [18.05] Every pricing card must use INR.
- [18.06] Every public copy line must avoid hidden visual surprise references.
- [18.07] Every component must be build-safe.
- [18.08] Every imported file must exist.
- [18.09] Every GSAP selector must be scoped.
- [18.10] Every ScrollTrigger must avoid leaking on navigation.
- [18.11] Every mobile layout must avoid horizontal overflow.
- [18.12] Every hero line must speak to founder pain.
- [18.13] Every diagram must be CSS/SVG, not an image.
- [18.14] Every amber glow must represent action or intelligence.
- [18.15] Every dark card must have a clear hierarchy.
- [18.16] Every section headline must be understandable without body copy.
- [18.17] Every body paragraph must stay short.
- [18.18] Every grid must collapse cleanly on mobile.
- [18.19] Every repeated pattern must feel intentional.
- [18.20] Every final report line must include exact paths where relevant.

## Micro QA Pass 19

- [19.01] Every section must earn its place.
- [19.02] Every visual must explain a system, not decorate the page.
- [19.03] Every animation must make the product easier to understand.
- [19.04] Every CTA must point to a real route.
- [19.05] Every pricing card must use INR.
- [19.06] Every public copy line must avoid hidden visual surprise references.
- [19.07] Every component must be build-safe.
- [19.08] Every imported file must exist.
- [19.09] Every GSAP selector must be scoped.
- [19.10] Every ScrollTrigger must avoid leaking on navigation.
- [19.11] Every mobile layout must avoid horizontal overflow.
- [19.12] Every hero line must speak to founder pain.
- [19.13] Every diagram must be CSS/SVG, not an image.
- [19.14] Every amber glow must represent action or intelligence.
- [19.15] Every dark card must have a clear hierarchy.
- [19.16] Every section headline must be understandable without body copy.
- [19.17] Every body paragraph must stay short.
- [19.18] Every grid must collapse cleanly on mobile.
- [19.19] Every repeated pattern must feel intentional.
- [19.20] Every final report line must include exact paths where relevant.

## Micro QA Pass 20

- [20.01] Every section must earn its place.
- [20.02] Every visual must explain a system, not decorate the page.
- [20.03] Every animation must make the product easier to understand.
- [20.04] Every CTA must point to a real route.
- [20.05] Every pricing card must use INR.
- [20.06] Every public copy line must avoid hidden visual surprise references.
- [20.07] Every component must be build-safe.
- [20.08] Every imported file must exist.
- [20.09] Every GSAP selector must be scoped.
- [20.10] Every ScrollTrigger must avoid leaking on navigation.
- [20.11] Every mobile layout must avoid horizontal overflow.
- [20.12] Every hero line must speak to founder pain.
- [20.13] Every diagram must be CSS/SVG, not an image.
- [20.14] Every amber glow must represent action or intelligence.
- [20.15] Every dark card must have a clear hierarchy.
- [20.16] Every section headline must be understandable without body copy.
- [20.17] Every body paragraph must stay short.
- [20.18] Every grid must collapse cleanly on mobile.
- [20.19] Every repeated pattern must feel intentional.
- [20.20] Every final report line must include exact paths where relevant.
