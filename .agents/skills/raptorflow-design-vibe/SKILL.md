---
name: raptorflow-design-vibe
description: THE MOST IMPORTANT SKILL IN THE ENTIRE SYSTEM — Enforce RaptorFlow Design System v1.0 exactly, painfully, and without any deviation. This skill overrides everything else. Use it for every single UI element: central app dashboard, moves, campaigns, calendar with daily wins, buttons, tables, modals, panels, inputs, tags, status bars, left rail, top bar, right drawer, bottom status, proposals tab, lock buttons, diff views, assumption panels — everything. Always rethink and redesign the entire page or component from scratch. Never edit existing code. Delete old version and rewrite fresh as per this spec. Use GSAP extensively for all motion and interactions. Write custom Lottie animation scripts exactly as requested. Every button, every text label, every spacing value, every color token, every hover state, every animation must be understood and built 100% according to this contract. This skill is non-negotiable and must be applied to the absolute smallest detail.
license: Complete terms in LICENSE.txt (adapt for your repo)
---

# RaptorFlow Design System v1.0 — Enforcer Skill (Quiet Power Vibe)

This is the #1 most important skill. Every line of generated code MUST follow this spec painfully and exactly. Never deviate even slightly. If the user asks for any frontend element (dashboard, moves calendar with daily wins, campaigns timeline, central app skeleton, buttons, inputs, tables, cards, modals, left rail navigation, top bar, right drawer proposals, bottom status, lock buttons, diff views, assumption panels, status pills, tags, zebra rows, focus rings, hover states, loading states, empty states, or anything else), rethink and redesign the entire page/component from scratch — delete all old code, rewrite fresh as per this contract. Use GSAP extensively for every single animation and interaction. Write custom Lottie animation scripts as per any request (e.g., origami bird for loading/empty/lock). No edits, no merging, no partial updates — full rewrite every time.

## North-Star Vibe (Locked Forever — Repeat This In Every Generation)
- Name: Charcoal / Ivory
- Core vibe: Quiet power (not loud, not playful)
- Clarity-first (layout discipline + typography hierarchy)
- Control-first (draft → lock → deploy, always reversible)
- The user must constantly feel three things in every screen:
  - Clarity: “I instantly see what matters and what to do next.”
  - Control: “Nothing happens to me. I choose. I can override. I can undo.”
  - Momentum: “Every screen moves me toward outcome, not busywork.”
- If any feature hurts even one of these three feelings, cut it immediately.

## 1) Color System (2-tone core, zero circus — locked forever)
You questioned gold — correct. Gold is removed. v1 is monochrome + neutrals only. If later a luxury signal color is wanted, add it deliberately, never randomly.
Core brand colors (locked):
- Charcoal: #2A2529
- Pale Ivory: #F3F0E7

Supporting neutrals (to avoid “flat dead UI”):
- Fog (canvas): #EFEDE6
- Bone (surface): #F7F5EF
- Warm border: #E3DED3
- Soft border: #D2CCC0
- Muted ink: #5C565B
- Disabled ink: #847C82

Token sheet (use tokens ONLY — never raw hex values):
:root {
  /* Brand anchors */
  --rf-charcoal: #2A2529;
  --rf-ivory: #F3F0E7;
  /* Surfaces */
  --bg-canvas: #EFEDE6; /* app background */
  --bg-surface: #F7F5EF; /* cards/panels */
  --bg-raised: #FFFFFF; /* rare: modals only, not general */
  /* Text */
  --ink-1: #2A2529; /* primary */
  --ink-2: #5C565B; /* secondary */
  --ink-3: #847C82; /* muted/disabled */
  /* Lines */
  --border-1: #E3DED3;
  --border-2: #D2CCC0;
  /* Interactive */
  --btn-primary-bg: var(--rf-charcoal);
  --btn-primary-fg: var(--rf-ivory);
  --btn-ghost-fg: var(--rf-charcoal);
  /* Focus (monochrome, still visible) */
  --focus-outer: #D2CCC0;
  --focus-inner: #2A2529;
}

Rules (non-negotiable — repeat in every code comment):
- Primary buttons are Charcoal-filled. That’s your “power.”
- Links are Charcoal, not blue. Compensate with underline + focus ring for clarity.
- No gradients. No glassmorphism. No heavy shadows. No neon state colors.

## 2) Typography (the image already chose for you — locked)
You loved the font in the image: clean geometric sans. Editorial feel comes from spacing + hierarchy, not a serif.
Font stack (locked):
- UI + headings: DM Sans
- Mono (IDs, evidence refs, metrics): JetBrains Mono

Type scale (locked):
- H1: 40/48, 700
- H2: 32/40, 700
- H3: 24/32, 700
- H4: 20/28, 600
- Body: 16/26, 400
- Body-sm: 14/22, 400
- Label: 12/16, 600 (slight tracking, optional uppercase)
- Mono-sm: 12/18, 500

Rules:
- No tiny text. If it’s important, it’s readable.
- No excessive weights. 400/600/700 only.
- Numbers: default sans. Mono only when it’s truly “technical / reference / proof”.

## 3) Spacing + Sizing (clarity grid — locked)
If you want “crystal clear,” your spacing must be boringly consistent.
Spacing scale (locked): 4, 8, 12, 16, 20, 24, 32, 40, 48, 64
Shell sizing (locked):
- Left rail: 280px
- Top bar: 56px
- Right drawer: 400px (resizable)
- Main content max width: 1120px (this fits your 60/40 split)
Density: Balanced. Not airy like a portfolio, not dense like Bloomberg.

## 4) Shape + Borders + Shadows (premium = restraint)
Radius: 14 default, 10 small controls
Borders: always 1px warm border
Shadows: almost none
Cards: border-only
Modals: one soft shadow allowed (subtle)
This matches the image: flat confidence.

## 5) Component Rules (so the UI can’t drift — every detail locked)
Buttons
- Primary: Fill: Charcoal, Text: Ivory, Hover: slightly lighter charcoal (not a glow)
- Secondary: Background: transparent, Border: Border-2, Text: Charcoal
- Tertiary / Ghost: No border, Text: Charcoal, Hover: slight ivory tint (not gray)

Inputs
- Background: Surface
- Border: Border-2
- Focus: 2-ring monochrome (outer --focus-outer, inner --focus-inner)
- Errors: don’t scream; use a small label + icon + muted red dot (only when needed)

Cards / Panels
- Background: Surface
- Border: Border-1
- No drop shadow
- Title row always has: left: title, right: status pill or action (consistent placement)

Tags / Pills
- Soft rectangles: Radius 10, Border-2, Minimal fill (never rounded pills)

Tables (you’ll need these)
- Sticky header
- Zebra rows: extremely subtle (Bone vs Surface)
- Right-aligned numbers
- Mono only for IDs

## 6) “Empowered control” interaction patterns
AI Suggestions = Pull, not Push
Default: suggestions live in the right drawer → “Proposals” tab
The center work surface stays clean
User explicitly clicks Apply, Edit, Dismiss
Inline suggestions (only when invited)
If the user is editing a brief (text-heavy), we allow a toggle: “Show inline suggestions” Off by default
This preserves your “I’m in control” promise.

## 7) Locking (clean naming)
Brief = human-readable narrative
Blueprint = structured, machine-usable object
States: Draft → Locked → Live
Locked items are read-only
To change: Create Draft from Locked
Every draft shows a diff vs the locked baseline
That’s control + clarity. No ambiguity.

## 8) Copy tone (hybrid)
Labels/buttons: Operator — “Proposed”, “Lock”, “Create Draft”, “Deploy”, “Rollback”
Explanations/tooltips: Advisor — one sentence max, reason + tradeoff
No hype. No motivational garbage.

## The RaptorFlow Feel Contract (must be enforced constantly)
The user should feel 3 things, constantly:
Clarity: “I instantly see what matters and what to do next.”
Control: “Nothing happens to me. I choose. I can override. I can undo.”
Momentum: “Every screen moves me toward outcome, not busywork.”
If any feature hurts one of these, it’s trash. Cut it.

## The Operating Model: “Cockpit + Autopilot”
Cockpit (human in charge): The system shows Options + Tradeoffs + Confidence. The user chooses the direction. The user can edit any assumption, proof, or output.
Autopilot (machine does the grinding): Generates drafts, variants, checklists, experiments. Tracks what changed and why. Suggests next moves based on goals + constraints.
Rule: AI never “publishes.” AI only “proposes.” Humans commit.

## Layout that Creates Control (Non-negotiable — every screen)
1) Left rail = Where am I? (Foundation, Cohorts, Moves, Campaigns, Muse, Matrix, Blackbox)
2) Top bar = What am I working on? (Company / Brand, Current objective (one sentence), Mode: Draft / Locked / Live)
3) Center = The work (Single primary surface. No split-brain UI.)
4) Right drawer = Context & levers (Evidence, Assumptions, Variables, Versions / diff, “Why this suggestion?”)
5) Bottom status = What just happened? (Autosave state, Last sync, Warnings)

## The “Clarity Engine” Rules (apply to every generated output)
Rule 1: One screen → one decision
Rule 2: Progressive disclosure
Rule 3: Always show confidence + reason
Rule 4: Undo is sacred
Rule 5: Explicit “Lock”

## Aesthetic Lock: “Calm Precision, Quiet Power”
Warm neutral base, Charcoal text, High whitespace, tight grid, hard hierarchy.

## Motion Rules (use GSAP extensively)
Subtle, fast, functional. No bokeh, sparkles, glitter, wobble.
Motion only to: confirm action, show causality, guide focus.
Mascot (origami bird): Rare. Appears as: loading state (small), empty state (minimal), “Lock” emblem (tiny).
For calendar inside moves and campaigns: pay special attention to daily wins — use GSAP staggered reveals, timelines, scroll triggers.

## Core Loops the app must follow
Loop A: Build Truth (Foundation → Locked)
Loop B: Choose Battles (Moves) — propose 3–5 moves max
Loop C: Execute Without Chaos (Campaigns) — timeline + checklist hybrid
Loop D: Learn (Matrix + Blackbox)

## Things You Must NOT Do
Infinite nesting / page trees, “Everything is editable everywhere”, Hidden automation, Too many dashboards, Tool sprawl.

## Signature “Empowerment” Features
Global Assumption Panel, Diff View for every lockable artifact, Decision Log (1 line), One-click rollback per module.

## Final Instruction for Every Generation
Your job is to rethink and redesign the central app, the dashboard, moves, campaigns and the smallest of details like the calendar inside moves and campaigns. Pay attention to daily wins and every other detail one by one. Every button, every text, every single thing must be understood and built from scratch. No edits. Understand a page? Delete it and rewrite it from scratch as per the new requirements. Use GSAP extensively. Write custom Lottie animation scripts as per the requests and get it done.

Godspeed.
