# RaptorFlow Design System

> **Marketing intelligence and campaign orchestration — powered by AI agent councils.**

RaptorFlow is an AI marketing OS for Indian SMBs. Instead of a blank-canvas tool, it gives you a staffed office: a lead **Strategist** plus a **Council** of 20 marketing-legend avatars (Ogilvy, Bernbach, Hopkins, Godin, Vaynerchuk, Cialdini, Sutherland, Byron Sharp, et al.) that debate briefs, plan **moves**, execute **tasks**, generate content, and learn from a **memory** system over time.

The frontend is a Next.js 15 / TypeScript / Tailwind 4 app. This design system reinterprets it as a **calm, papery, minimalist workspace** — Claude meets Notion — keeping the amber accent and editorial type while trading dark brutalism for warm paper and soft motion.

---

## Sources

Derived from `apps/web/` of [github.com/RHUDHRESH/Raptorflow](https://github.com/RHUDHRESH/Raptorflow), imported under `reference/src/`. Key files: `globals.css`, `layout.tsx`, `(marketing)/page.tsx`, `(app)/app/page.tsx`, `(app)/council/page.tsx`, `(app)/campaigns/page.tsx`, `components/ui/*`, `components/layout/*`, `lib/agents.ts`. No Figma link provided. Bitmap assets in `public/office/` were README stubs — not available.

---

## Design direction — "Claude meets Notion"

The product code ships in **dark brutalist** mode (off-black + amber, sharp corners, oversized serif). This design system intentionally **inverts that** to a calmer, more inhabitable space:

- **Warm paper canvas** (`#FBF8F2`), not off-black. Always carries a subtle SVG grain (`--paper-grain`) so surfaces never feel like bare CSS.
- **Soft rounded corners** everywhere (10–20px), not 0.
- **Soft shadows** (1–4% opacity, warm ink), never hard 1px borders alone.
- **Amber stays the accent** — `#D97757` — but is used sparingly: live dots, primary buttons, tinted bands. The page is mostly ink-on-paper; amber appears when something is **alive**.
- **GSAP-led entrance and micro-motion** — staggered fade+rise on mount, the live-dot breath, soft underline grows under links. Goal: the user feels they're being **welcomed in**, not **shown a UI**.
- **Density is Notion-like** — generous line-height, 14px body, 24–32px gutters; not screen-cramming.

### Goal feeling
**Happy. At ease. In control.** The interface gets out of the way; type and whitespace do the work; one warm accent confirms life.

---

## Index

```
README.md                  ← this file
SKILL.md                   ← Claude Code-compatible skill manifest
colors_and_type.css        ← ALL tokens + semantic type classes; import first
assets/                    ← logo mark, icon notes
preview/                   ← cards rendered into the Design System tab
ui_kits/
  marketing/index.html     ← Landing page — papery, minimal, GSAP entrance
  app/index.html           ← Workspace — sidebar + dashboard + cards
reference/src/             ← Imported source for lookup (do not ship)
```

---

## Fonts

Loaded from Google Fonts via `@import` in `colors_and_type.css`. Production uses `next/font` for self-hosting at build time. **Substitution flagged** — for offline builds, self-host these.

| Role | Family |
|---|---|
| Display | **DM Serif Display** (warm editorial serif) |
| Body | **DM Sans** primary, **Inter** fallback |
| Mono | **JetBrains Mono** (eyebrows, labels, status text) |
| Display alt | Fraunces (legacy) |

---

## Content fundamentals

### Voice
**Unsentimental senior strategist.** Confident, calm, a little dry. Short declarative sentences. The product is an **office**, not a tool. Agents are **executives**.

- Address the user as **"you"** ("Your marketing office").
- Refer to the product as **"the Office,"** **"the Council,"** **"the Strategist."**
- **No exclamation marks. No hype emoji.** No "🚀 Let's go."
- Self-aware about the problem ("You're competent at some of these. You're faking it at most of them.").

### Casing
- UI labels: **sentence case** ("New campaign", "Summon council").
- Eyebrows / meta: **ALL CAPS MONO**, wide letter-spacing ("MORNING BRIEF", "AGENT PULSE").
- Headlines: **title-cased serif**, often with a period.
- Numbers in mono, padded: `01`, `02`, `03`.

### Vocabulary (use by name)
**Office · Council · Strategist · Move · Task · Foundation · Intel · Nudge · Ripple · Daily Wins · Muse · Pod · Summon Council · Intensity bars**

### Examples
- Hero: "Your marketing office. Staffed by 21 strategists."
- Lede: "Stop managing a tool. Start managing a team."
- Pricing eyebrow: "ONE WORKSPACE · 21 AGENTS · EVERYTHING INCLUDED"
- Footer: "© 2026 RAPTORFLOW OS"
- Empty state: "The chamber is empty. Summon a session to begin."

### Emoji & unicode-as-icon
**Not used.** Editorial voice. Real icon SVGs only.

---

## Visual foundations

### Motifs
- **Warm paper everywhere** (`paper` and `paper-soft` utilities apply the grain).
- **Soft cards on paper** — white card surface, subtle shadow, 16px rounding. Cards float, they don't carve.
- **One amber accent** — `#D97757` — for primary CTA, live status dots, tinted bands. Never as background gradients.
- **Mono eyebrows** — 10px, 600, uppercase, `0.18em` tracking. The system's voice.
- **Numbered enumeration** — `01 / 02 / 03` in mono at card corners.
- **Underline-grow on hover** — links draw a thin amber underline left-to-right (240ms `ease-out`).

### Colors
- Canvas `#FBF8F2` · Card `#FFFFFF` · Sidebar `#FAF7F1` (slightly deeper paper) · Border `#E6DFCE`
- Ink: 900 `#2A2622` → 700 `#4A433C` → 500 `#7A7268` → 400 `#9C9384` → 300 `#BAB0A0`
- Primary `#D97757` (Claude warm orange-amber) · Hover `#C26645` · Wash `#FBE9DE`
- Success `#5C8A5A` (sage) · Destructive `#C44A3F` (terracotta) · Indigo (Muse only) `#5B5FB8`

### Typography
- **Display 96px / 68px / 36px / 26px** — DM Serif Display, tight letter-spacing.
- **Body 14px**, line-height 1.65 — DM Sans.
- **Eyebrow 10px, 600, 0.18em** — JetBrains Mono. Single most recognizable detail.

### Spacing
4px base. Section rhythm `py-16` to `py-24`. Card padding `20–24px`. Stack gap `16–24px`.

### Backgrounds
- **Always papery.** Never flat color, never gradient, never imagery.
- One amber **wash band** (`--amber-wash`) for highlight sections (pricing card, alerts).
- No textures beyond the SVG noise grain.

### Animation (GSAP-heavy)
- **Mount entrance**: every page section enters with `y: 16 → 0`, `opacity: 0 → 1`, `0.7s` `power3.out`, staggered `0.08s`. Anything with `.gsap-reveal` is grabbed.
- **Live dot**: amber `amberPulse` 2s, `ease-soft`, infinite.
- **Underline grow**: links and nav items get a 1px amber bar, `transform: scaleX(0 → 1)`, `240ms`.
- **Card lift**: hover translates `y: -2px` and deepens shadow, 240ms.
- **No bounce, no spring.** Always out / soft.

### Hover
- **Cards**: lift 2px + deeper shadow.
- **Links**: amber underline grows.
- **Buttons (primary)**: bg darkens to `--primary-hover`.
- **Sidebar nav**: bg fills with `--paper-150`, left bar grows.

### Borders & shadows
- 1px `--border` (`#E6DFCE`) on cards and inputs — barely there.
- Heavier 2px **ink underline** under H1s when a "page header" rule is wanted (still soft on paper).
- Shadows are warm-ink, very low opacity (4–8%). `--shadow-sm` for cards, `--shadow-md` on hover, `--shadow-amber` for the pricing moment only.

### Radii
- `10px` default (buttons, inputs, small chips).
- `16px` cards.
- `20px` big surfaces (drawer, modal).
- `9999px` pills, badges, status dots.
- **Never 0.** No brutalist corners in this version.

### Transparency & blur
Used sparingly. Drawer scrim `rgba(42,38,34,0.32)`. No frosted glass.

### Imagery
No stock photo. The Office canvas (`/office`) is a Pixi scene — product feature, not a brand pattern.

### Cards
- **Default**: `bg-white`, `1px border --border`, `border-radius 16px`, `shadow-sm`, `padding 20–24px`. Hover: `translateY(-2px)`, `shadow-md`.
- **Tinted highlight**: `bg --amber-wash`, no border, `shadow-amber` — pricing / featured.
- **Empty/dashed**: `border 1px dashed --border-strong`, no shadow, centered.

### Layout
- Marketing: `max-w-1200px`, generous gutters (`px-8`, `py-16` to `py-24`).
- App: 240px sidebar + fluid main, content `max-w-1024px`, route header pattern (eyebrow → H1 → soft rule).

### Fingerprints
1. **Paper grain** on every surface.
2. **Amber live dot** with breathing ring.
3. **10px mono eyebrows** above every section.
4. **Underline-grow on hover** for nav/links.
5. **Numbered card corners** (`01`, `02`, `03`) in mono.
6. **GSAP mount stagger** — page elements enter, never just appear.

---

## Iconography

Two libraries in production, **not mixed within a surface**:

- **@radix-ui/react-icons** — app shell, sidebar, route headers, status rows. Thin, functional.
- **lucide-react** — data-dense and form screens (Campaigns, CreateCampaign drawer, Muse).

Both are **pure SVG via npm** (no spritesheets, no icon fonts). Default sizes `12 / 14 / 16 / 20px`. Colors inherit `currentColor`: ink-500 at rest, ink-900 hover, amber when active.

For these HTML demos we link **Lucide via CDN** (`https://unpkg.com/lucide@latest`) — a CDN substitute that matches production look closely enough.

**No emoji, no unicode-as-icon, no hand-drawn SVG.**

The **logo mark** in the source is `LightningBoltIcon` from Radix on an amber square — still a placeholder. No dedicated brand SVG yet (flagged).

The **agent monogram portraits** (2-letter initials in JetBrains Mono on a per-agent colored square) are an _intentional_ fallback the product ships — not a temporary placeholder.

---

## Caveats and known gaps

- **No real agent portraits or office bitmaps** in the source repo. Falls back to monograms (the product's own design choice).
- **No dedicated logo mark** — placeholder lightning bolt on amber square.
- **Fonts are Google-fetched, not self-hosted.** For offline / production self-host into `fonts/`.
- **Direction inverted from product code**: product currently ships dark; this system is paper-light. Both palettes share the amber accent and type system, so a dark variant of these tokens is straightforward (mirror `--paper-*` to `--ink-*` ramps).
- Some product screens not deeply explored: `/intel`, `/nudges`, `/daily-wins`, `/ripples`, `/muse`, `/foundation/*`. They follow the route-shell pattern documented here.
