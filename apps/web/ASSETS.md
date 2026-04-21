# RaptorFlow Landing Page — Asset Specification

This document lists every visual asset needed for the landing page. All assets are referenced in code. Create them exactly as specified and place them in the exact paths shown.

---

## 1. Logo Assets

### 1.1 `/public/brand/logo-light.svg`

**Usage:** Navigation bar, footer (light backgrounds)
**Specs:**

- Format: SVG
- Width: 140px when rendered
- Content: "RaptorFlow" wordmark in dark ink (#13141A)
- Style: Clean geometric sans-serif, bold weight, tight tracking
- No icon — text only
- Transparent background

**How to create:**

1. Open Figma or Illustrator
2. Type "RaptorFlow" using a bold geometric sans (Inter Bold, Plus Jakarta Sans Bold, or similar)
3. Tracking: -0.02em
4. Color: #13141A
5. Export as SVG with text converted to outlines
6. Save to `/public/brand/logo-light.svg`

---

### 1.2 `/public/brand/logo-dark.svg`

**Usage:** Footer on dark background
**Specs:**

- Format: SVG
- Width: 120px when rendered
- Content: "RaptorFlow" wordmark in cream (#F7F4EE)
- Style: Same as logo-light but light colored
- Transparent background

**How to create:**

1. Duplicate logo-light.svg
2. Change color to #F7F4EE
3. Save to `/public/brand/logo-dark.svg`

---

### 1.3 `/public/brand/icon.svg`

**Usage:** Channel diagram center mark, favicon source
**Specs:**

- Format: SVG
- Size: 60px when rendered in channel diagram
- Content: "RF" monogram or a stylized raptor/bird mark
- Style: Bold, geometric, minimal
- Color: #E85A2C (orange) on transparent

**How to create:**

1. Create a simple geometric mark — either:
   - Option A: "RF" letters in a bold sans, tightly tracked, inside a circle
   - Option B: A stylized bird/raptor silhouette (think simple, like the Twitter bird but more angular/aggressive)
2. Color: #E85A2C
3. Export as SVG
4. Save to `/public/brand/icon.svg`

---

## 2. Favicon & Touch Icons

### 2.1 `/public/favicon.ico`

**Specs:**

- Format: ICO (multi-resolution)
- Sizes: 16x16, 32x32
- Source: Use icon.svg, render on #0E0F13 dark background

**How to create:**

1. Open icon.svg in Figma/Illustrator
2. Create a 32x32px artboard with #0E0F13 background
3. Place the icon centered, scaled to fit with 4px padding
4. Export as PNG 32x32
5. Use a favicon generator (favicon.io) to convert to .ico
6. Save to `/public/favicon.ico`

---

### 2.2 `/public/apple-touch-icon.png`

**Specs:**

- Format: PNG
- Size: 180x180
- Source: Use icon.svg on #0E0F13 background with rounded corners

**How to create:**

1. Create 180x180px artboard
2. Background: #0E0F13
3. Add 20px rounded corners mask
4. Place icon.svg centered, scaled to ~120px
5. Export as PNG
6. Save to `/public/apple-touch-icon.png`

---

## 3. Open Graph / Social Image

### 3.1 `/public/og-image.png`

**Usage:** Social sharing preview (Twitter, LinkedIn, WhatsApp)
**Specs:**

- Format: PNG
- Size: 1200x630
- Background: #0E0F13 (dark)
- Content layout:
  - Top-left: icon.svg at ~80px, color #E85A2C
  - Center: "RaptorFlow" in large bold white text (~72px)
  - Below: "AI Marketing for B2B SaaS Founders" in muted text (~28px, color rgba(255,255,255,0.5))
  - Bottom: "Your product deserves to be found." in orange (~24px, #E85A2C)
  - Subtle gradient mesh background (same colors as hero mesh)

**How to create:**

1. In Figma, create 1200x630 frame
2. Fill with #0E0F13
3. Add subtle gradient blob using colors #E85A2C, #1F3A5F at 10% opacity in background
4. Place icon.svg top-left with 60px margin
5. Add text layers as described
6. Font: Plus Jakarta Sans or similar geometric sans
7. Export as PNG at 2x (2400x1260) then scale down, or export 1x
8. Save to `/public/og-image.png`

---

## 4. Customer Logos (Social Proof Strip)

**Location:** `/public/logos/`
**Usage:** Section 2 social proof strip

**Note:** These should be REAL customer logos once you have them. For now, create placeholder silhouettes or skip this section in code.

If you want placeholders:

- Create 8-12 simple monogram/lettermark SVGs
- Names like: "Acme Corp", "BetaTech", "GammaSoft", etc.
- Color: grayscale, muted
- Height: 32px when rendered

**Files:**

- `/public/logos/customer-01.svg`
- `/public/logos/customer-02.svg`
- ... up to `/public/logos/customer-12.svg`

**How to create:**

1. For each customer, create a simple lettermark (first letter in a circle, or wordmark)
2. Color: #6B6D78 (muted gray)
3. Export as SVG
4. Save to respective paths

---

## 5. Testimonial Photos

**Location:** `/public/testimonials/`
**Usage:** Section 10 testimonial cards

**Specs for each:**

- Format: JPG or WebP
- Size: 200x200 (displayed at 64x64 or 80x80)
- Style: Professional headshot, neutral background
- Border-radius applied in CSS

**Files needed:**

- `/public/testimonials/raj-patel.jpg` — "Raj Patel, Founder, Bansi Jewellery, Surat"
- `/public/testimonials/priya-sharma.jpg` — "Priya Sharma, CEO, TechStart, Bangalore"
- `/public/testimonials/amit-kumar.jpg` — "Amit Kumar, CMO, CloudKitchen, Pune"
- `/public/testimonials/sneha-rao.jpg` — "Sneha Rao, Founder, D2C Brand, Mumbai"

**How to create:**

1. Use real customer photos if available
2. Or use AI image generators with prompts like:
   - "Professional headshot of Indian businessman in his 30s, neutral gray background, studio lighting, high quality"
3. Crop to square 400x400
4. Export as WebP (or JPG)
5. Save to respective paths

---

## 6. Dashboard Mockup (Optional Enhancement)

**Location:** `/public/images/dashboard-preview.png`
**Usage:** Could replace the code-built briefing card with a real screenshot

**Specs:**

- Format: PNG with transparency OR WebP
- Size: ~800x600
- Content: Screenshot of actual RaptorFlow dashboard showing:
  - Morning briefing
  - Competitor intel
  - Action items
  - Dark theme UI

**How to create:**

1. Take screenshot of actual RaptorFlow app
2. Or design in Figma based on the briefing card design in the code
3. Export as PNG
4. Save to `/public/images/dashboard-preview.png`

---

## 7. Complete Asset Checklist

| #   | File Path                               | Type | Priority | Status |
| --- | --------------------------------------- | ---- | -------- | ------ |
| 1   | `/public/brand/logo-light.svg`          | SVG  | Critical | ⬜     |
| 2   | `/public/brand/logo-dark.svg`           | SVG  | Critical | ⬜     |
| 3   | `/public/brand/icon.svg`                | SVG  | Critical | ⬜     |
| 4   | `/public/favicon.ico`                   | ICO  | Critical | ⬜     |
| 5   | `/public/apple-touch-icon.png`          | PNG  | High     | ⬜     |
| 6   | `/public/og-image.png`                  | PNG  | High     | ⬜     |
| 7   | `/public/logos/customer-01.svg`         | SVG  | Medium   | ⬜     |
| 8   | `/public/logos/customer-02.svg`         | SVG  | Medium   | ⬜     |
| 9   | `/public/logos/customer-03.svg`         | SVG  | Medium   | ⬜     |
| 10  | `/public/logos/customer-04.svg`         | SVG  | Medium   | ⬜     |
| 11  | `/public/testimonials/raj-patel.jpg`    | JPG  | Medium   | ⬜     |
| 12  | `/public/testimonials/priya-sharma.jpg` | JPG  | Medium   | ⬜     |
| 13  | `/public/testimonials/amit-kumar.jpg`   | JPG  | Medium   | ⬜     |
| 14  | `/public/testimonials/sneha-rao.jpg`    | JPG  | Medium   | ⬜     |
| 15  | `/public/images/dashboard-preview.png`  | PNG  | Low      | ⬜     |

---

## 8. Quick Start — Minimum Viable Assets

To launch the page, you ONLY need these 5 files:

1. `logo-light.svg` — For the nav
2. `logo-dark.svg` — For the footer
3. `icon.svg` — For the channel diagram
4. `favicon.ico` — Browser tab icon
5. `og-image.png` — Social sharing

All other assets can be added later without code changes.

---

## 9. Design References

### Color Palette

| Role             | Hex     |
| ---------------- | ------- |
| Background light | #F7F4EE |
| Background dark  | #0E0F13 |
| Primary text     | #13141A |
| Secondary text   | #6B6D78 |
| Accent orange    | #E85A2C |
| Accent indigo    | #1F3A5F |
| Success green    | #3FA66A |

### Typography

- Primary: Plus Jakarta Sans (weights 400, 500, 600, 700, 800)
- Mono: DM Mono (weights 400, 500)

### Logo Style Reference

Think: Linear.app, Vercel, Clerk.dev — clean geometric wordmarks, no serifs, no gradients on the logo itself. The logo should feel like it belongs on a YC company's landing page.

---

_Last updated: 2025-01-21_
_Create these assets and the landing page will look complete and professional._
