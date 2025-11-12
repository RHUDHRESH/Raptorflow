# RaptorFlow Website

Next.js (App Router) + TypeScript + Tailwind CSS + shadcn/ui + Lucide icons

## Local Setup

**Requirements:**
- Node.js v20.x LTS
- pnpm

**Installation:**

```bash
# Install dependencies
pnpm install

# Run development server
pnpm dev
```

Visit [http://localhost:3000](http://localhost:3000)

## Project Structure

```
raptorflow-www/
├─ src/
│  ├─ app/              # Next.js App Router pages
│  ├─ components/       # React components
│  │  ├─ system/        # Low-level primitives (TextRotate, SpotLight, Section)
│  │  ├─ nav/           # Navigation components
│  │  ├─ hero/          # Hero section
│  │  ├─ trio/          # Value proposition cards
│  │  ├─ icp/           # Persona grid with spotlight
│  │  ├─ plan/          # Short/Long Move tiles
│  │  ├─ ideas/         # Idea engine section
│  │  ├─ assets/        # Asset factory section
│  │  ├─ pricing/       # Pricing table
│  │  └─ cta/           # Bottom CTA
│  ├─ lib/              # Utilities (copy, images, tokens, utils)
│  └─ styles/           # Global styles and tokens
└─ public/              # Static assets
   └─ assets/           # Section-specific images
```

## Stack

- **Next.js 15** (App Router) - Server components, layouts, image optimization
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling with custom tokens
- **shadcn/ui** - Production-grade component library
- **Lucide React** - Icon library

## Brand Tokens

All brand colors and design tokens are defined in `src/styles/tokens.css` and extended in Tailwind config. The palette uses:

- **Core:** Deep noir background (#0B0B0E), card surfaces (#121217)
- **Accents:** Mineshaft (#2D2D2D), Akaroa (#D7C9AE), Purple accent (#8B7CF9)
- **Effects:** Glass morphism, custom shadows, ring effects

## Assets

Place your Sora-generated images in `public/assets/<section>/` and register them in `src/lib/images.ts` for centralized asset management.

## Development

```bash
# Type checking
pnpm typecheck

# Linting
pnpm lint

# Build for production
pnpm build
```

## Deploy

This project is configured for Vercel deployment. Push to your repository and connect it to Vercel for automatic deployments.

