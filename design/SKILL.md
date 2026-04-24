# RaptorFlow Design System — Skill Manifest

A condensed manifest for Claude Code or other automated agents.

## Identity
- **Name**: RaptorFlow
- **Tagline**: "Your marketing office. Staffed by 21 strategists."
- **Category**: AI marketing OS for Indian SMBs (B2B SaaS).
- **Voice**: unsentimental senior strategist — calm, dry, declarative. No hype, no exclamation marks, no emoji.
- **Vocabulary**: Office · Council · Strategist · Move · Task · Foundation · Intel · Nudge · Ripple · Daily Wins · Muse · Pod · Summon Council.

## Direction in one line
Claude meets Notion: warm paper canvas, soft rounded cards, amber accent reserved for what is alive, GSAP entrance choreography.

## Tokens (load `colors_and_type.css` first)
- **Canvas**: `--paper-100 #FBF8F2` (always with `paper` or `paper-soft` class for grain).
- **Card surface**: `#FFFFFF` on `--paper-100`. 1px `--border #E6DFCE`, `border-radius: 16px`, `--shadow-sm`.
- **Ink ramp**: 900 `#2A2622` → 700 `#4A433C` → 500 `#7A7268` → 400 `#9C9384` → 300 `#BAB0A0`.
- **Primary**: `--primary #D97757` (amber). Hover `#C26645`. Wash `#FBE9DE`.
- **Status**: success `#5C8A5A` (sage), destructive `#C44A3F` (terracotta), indigo Muse `#5B5FB8`.
- **Pods**: creative `#8B6FC2`, digital `#4F87B8`, strategy `#B8556B`, support `#C26F4A`, strategist `#4A433C`.

## Type
- **Display**: DM Serif Display (96 / 68 / 36 / 26 px). Italic for the lyrical second clause.
- **Body**: DM Sans 14px, line-height 1.65. Inter as system fallback.
- **Mono**: JetBrains Mono 10px, weight 600, `letter-spacing: 0.18em`, uppercase — eyebrows, status labels, numbered enumerators.

## Layout & rhythm
- Marketing: max-width 1180–1200px, gutters 32px, vertical rhythm 80–96px.
- App: 240px sidebar + fluid main, route header pattern (eyebrow → H1 → soft rule).
- Spacing base 4px. Card padding 20–24px. Stack gap 16–24px.

## Always-on motifs (the "fingerprints")
1. **Paper grain** on every canvas (`paper` / `paper-soft` utility).
2. **Amber live dot** with breathing ring (`amberPulse` 2s, `--ease-soft`).
3. **10px mono eyebrow** above every section.
4. **Underline-grow** on links/nav (`scaleX 0 → 1`, 240ms `ease-out`).
5. **Numbered card corners** `01 / 02 / 03` in mono.
6. **GSAP mount stagger** — `.gsap-reveal` elements enter `y: 16 → 0`, `opacity: 0 → 1`, 0.7s `power3.out`, 0.06s stagger.

## Hard rules
- **No emoji.** No unicode-as-icon.
- **No gradients** as backgrounds. One amber wash band is the only tinted surface.
- **No hard 1px-only borders** without a soft shadow companion.
- **No 0px corners.** Everything is 10–20px or 9999px (pills).
- **No stock photography.** Agent portraits are intentional 2-letter monograms.
- **No exclamation marks** in product copy.
- **Numbers in mono**, padded (`01`, not `1`).

## Iconography
- **@radix-ui/react-icons** for app shell (sidebar, route headers, status). Thin and functional.
- **lucide-react** for data-dense surfaces (Campaigns table, CreateCampaign drawer, Muse).
- Default sizes 12 / 14 / 16 / 20 px. Color via `currentColor`: ink-500 rest, ink-900 hover, amber active.
- For HTML demos: `https://unpkg.com/lucide@latest` is the CDN substitute.

## Components — minimum spec
- **Button (primary)**: `bg --primary`, `color #fff`, `padding 10px 16px`, `radius 10px`, hover → `--primary-hover` + `--shadow-amber`.
- **Button (secondary)**: `bg #fff`, `border 1px --border`, `--shadow-xs`. Hover lift 1px.
- **Button (mono)**: `bg --ink-900`, `color #fff`, `font-mono`, uppercase, `0.14em tracking`.
- **Card**: `bg #fff`, `border 1px --border`, `radius 16px`, `--shadow-sm`. Hover translate `-2px` + `--shadow-md`.
- **Card (highlight)**: `bg --amber-wash`, no border, `--shadow-amber`. For pricing / featured moments only.
- **Eyebrow**: `font-mono`, `10px`, weight 600, `0.18em` tracking, uppercase. Color `--ink-500` default, `--primary-hover` for accented eyebrows.
- **Live dot**: 6px amber circle, 6px amber-wash halo, `amberPulse 2.4s` infinite.
- **Status pill**: `padding 5px 10px`, `radius 9999px`, mono 10px caps, soft tinted bg matching semantic color.

## Files
```
README.md                  ← full system documentation
SKILL.md                   ← this file
colors_and_type.css        ← all CSS tokens + semantic type/utility classes
preview/                   ← design-system review cards
ui_kits/marketing/         ← marketing landing page
ui_kits/app/               ← workspace dashboard
reference/src/             ← imported source from RaptorFlow repo
```

## When generating new screens
1. Start by importing `colors_and_type.css`.
2. Apply `class="paper-soft"` (or `paper`) to `<body>`.
3. Open with a route header: mono eyebrow → display H1 → 1px `--border` rule.
4. Use white cards on paper, never paper on paper.
5. Add `.gsap-reveal` to top-level sections and run the stagger on load.
6. Reserve amber for: primary CTA, live status, pricing/featured highlight, active nav rail. Nothing else.
7. Mono labels for any meta-info (timestamps, IDs, status, counters).
8. Sentence case for UI; ALL CAPS MONO for eyebrows; title case with periods for headlines.
9. Refuse the urge to add gradients, emojis, or unnecessary iconography.
