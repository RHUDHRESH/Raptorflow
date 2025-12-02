# Raptorflow Editorial Style Guide

## Brand Voice

- **Perspective**: high-fashion strategist; confident, minimal, decisive.
- **Vocabulary Staples**: atelier, runway, edit, ritual, brief, capsule, curation, dispatch.
- **Tone Rules**:
  - Headlines = evocative statements (“Runway Dispatch”, “Studio Controls”).
  - Buttons = action phrased as a ritual (“Begin Ritual”, “Log Recap”, “Archive Move”).
  - Helper text = lowercase, calm, precise (“Describe the scene in 2 lines.”).

## Typographic System

| Role            | Font                | Usage                              |
|-----------------|---------------------|------------------------------------|
| Display         | `Playfair Display`  | Heros, section titles, stat values |
| Editorial Sans  | `Inter`             | Paragraphs, body copy              |
| Micro Labels    | `JetBrains Mono`    | Uppercase tags, nav microcopy      |

Sizing guidance:
- Display hero: 48–56px with 1.1 line-height.
- Section headers: 32–36px.
- Micro labels: 10px uppercase letter spacing 0.35em.

## Color Palette

| Token            | Hex      | Usage                                 |
|------------------|----------|---------------------------------------|
| `--ink`          | #0C0C0C  | Primary text, borders                  |
| `--porcelain`    | #F8F5F1  | Page background                        |
| `--champagne`    | #E9DCC7  | Accents, buttons hover                |
| `--oxblood`      | #6B2B2D  | Highlight CTA, warning                 |
| `--sable`        | #332E2A  | Surfaces (runway cards)                |
| `--veil`         | rgba(12,12,12,0.04) | Shadows & overlays           |

## Layout Principles

1. **Runway Card**: rounded 40px, soft border, inner shadow. Used for every hero/section container.
2. **Hero Composition**: micro label → headline → supporting copy → CTAs inline. Optional imagery aligned right with mask gradient.
3. **Grid**: 12-column responsive with 40px gutter on desktop, 24px on tablet, 16px on mobile.
4. **Whitespace**: large top/bottom padding (80px hero, 48px sections).
5. **Imagery**: editorial photography (black/white, muted). Use CSS backgrounds or dedicated components with overlay gradient.

## Component Lexicon

| Old Label       | New Editorial Label  |
|-----------------|----------------------|
| Dashboard       | Runway Dispatch      |
| Moves           | Runway Plays         |
| Weekly Review   | Editorial Recap      |
| Strategy        | Strategy Atelier     |
| Analytics       | Insights Studio      |
| ICP Manager     | Audience Archive     |
| Support         | Concierge Desk       |
| History         | Archive Ledger       |
| Account         | Portrait             |
| Settings        | Studio Controls      |

Button microcopy:
- Primary CTA: “Begin Ritual”, “Review Spread”, “Archive Runway”.
- Secondary: “Preview Edit”, “Save Capsule”, “Backstage”.

## Interaction Guidelines

- **Hover**: lighten background, increase letter spacing slightly.
- **Transitions**: 250ms ease, slide/fade for sections entering viewport.
- **Controls**: toggles styled as pill switches with micro labels left/right (“OFF / ON” replaced with “Muted / Live”).
- **Progress**: horizontal bar with micro labels and dot markers.

## Content Modules

- **Spotlight**: hero card featuring “Editor’s Note” (text + optional image).
- **Curator’s Picks**: 3-card grid featuring featured moves/strategies.
- **Recap Column**: vertical timeline with serif timestamp and italic summary.
- **Metrics Spread**: stats with sub-label microcopy (uppercase) and supporting description.

Use this document as the source of truth when renaming navigation, crafting microcopy, and styling new components. Update as new modules or vocabulary are introduced. 
