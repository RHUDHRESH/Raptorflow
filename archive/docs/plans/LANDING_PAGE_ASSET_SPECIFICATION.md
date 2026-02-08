# RAPTORFLOW LANDING PAGE — VISUAL ASSET SPECIFICATION
## Award-Winning GSAP-Heavy Website — Complete Image Asset Guide

---

# TABLE OF CONTENTS
1. [Asset Folder Structure](#asset-folder-structure)
2. [Brand Assets](#brand-assets)
3. [Hero Section Assets](#hero-section-assets)
4. [Product Demo Assets](#product-demo-assets)
5. [Feature Section Assets](#feature-section-assets)
6. [Social Proof Assets](#social-proof-assets)
7. [Background & Ambient Assets](#background--ambient-assets)
8. [Icon System Assets](#icon-system-assets)
9. [Export Specifications](#export-specifications)

---

# ASSET FOLDER STRUCTURE

```
public/
├── images/
│   ├── brand/                 # Logo, wordmark, favicon assets
│   ├── hero/                  # Hero section visuals
│   ├── product/               # Product screenshots & UI mocks
│   ├── features/              # Feature illustration icons
│   ├── testimonials/          # Founder/user photos
│   ├── backgrounds/           # Abstract backgrounds & gradients
│   ├── icons/                 # Custom icon system
│   └── textures/              # Noise, grain, paper textures
├── videos/                    # Lottie JSONs, MP4 backgrounds
└── fonts/                     # Custom editorial fonts
```

---

# BRAND ASSETS

## BA-01: Primary Logo Mark
**File:** `public/images/brand/logo-mark.svg`
**Format:** SVG (vector)
**Size:** 512×512px viewBox
**Transparent:** Yes

**PROMPT:**
```
Minimalist geometric raptor/bird of prey logo mark, side profile silhouette,
aggressive stance, sharp angular beak pointing right, sleek aerodynamic form,
single continuous line weight, architectural precision, monochrome black #1A1A1A,
vector art style, flat design, no gradients, inspired by Swiss design and
Bauhaus geometry, suitable for 16px favicon to billboard scale
```

---

## BA-02: Wordmark Logo
**File:** `public/images/brand/wordmark.svg`
**Format:** SVG (vector)
**Size:** 800×200px viewBox
**Transparent:** Yes

**PROMPT:**
```
Typography logo "RaptorFlow" in custom editorial serif font, sharp contrast
between thick and thin strokes, high x-height, geometric precision,
letter-spacing optimized for readability, black #1A1A1A on transparent,
combination of serif "Raptor" and sans-serif "Flow" with subtle weight
difference, architectural blueprint aesthetic, premium SaaS brand identity
```

---

## BA-03: Logo Symbol Animated (for preloader)
**File:** `public/images/brand/logo-animated.json`
**Format:** Lottie JSON
**Size:** 200×200px

**PROMPT (for reference frame):**
```
Animated raptor mark transforming from geometric outline to filled shape,
line drawing animation effect, stroke morphing, minimalist black lines on
warm cream background #F5F3EE, frame-by-frame construction sequence,
architectural drafting aesthetic, precision mechanical motion
```

---

# HERO SECTION ASSETS

## HE-01: Hero Dashboard Mockup (Primary)
**File:** `public/images/hero/dashboard-hero.webp`
**Format:** WebP
**Size:** 2400×1600px (2x for retina)
**Transparent:** No (has subtle shadow)

**PROMPT:**
```
Premium SaaS dashboard interface mockup, floating at 15-degree angle,
warm cream paper background #F5F3EE, sophisticated UI with:
- Left sidebar navigation with icons
- Central canvas showing marketing strategy board
- Right panel with AI insights and analytics
- Color palette: cream whites, charcoal blacks, blueprint blue accents #3A5A7C
- Subtle drop shadow creating depth
- Clean sans-serif typography
- Card-based layout with 12px rounded corners
- "Stop posting. Start building." headline visible on screen
- 3D perspective view, isometric angle from top-right
- Soft ambient lighting from top-left
- Photorealistic render, Octane quality
- Apple-style product photography aesthetic
```

---

## HE-02: Hero Background Abstract
**File:** `public/images/hero/hero-bg-abstract.webp`
**Format:** WebP
**Size:** 3840×2160px (4K)
**Transparent:** No

**PROMPT:**
```
Abstract architectural blueprint background, warm cream paper texture #F5F3EE,
faint technical grid lines in blueprint blue #3A5A7C at 10% opacity,
subtle geometric construction lines, compass and ruler motifs ghosted,
architectural drafting aesthetic, minimal noise texture overlay,
gradient from light center to slightly darker edges,
no focal point, designed for text overlay,
high resolution, print quality texture
```

---

## HE-03: Floating UI Element 1 - Strategy Card
**File:** `public/images/hero/float-strategy.webp`
**Format:** WebP
**Size:** 600×400px
**Transparent:** Yes (PNG-style alpha)

**PROMPT:**
```
Floating UI card component, glass morphism effect, strategy canvas interface,
showing marketing funnel diagram with 4 stages: Attract, Engage, Convert, Retain,
warm cream background with subtle transparency, charcoal text #1A1A1A,
blueprint blue accent lines #3A5A7C connecting nodes,
soft drop shadow, 16px rounded corners,
slight 3D tilt perspective, floating in space,
isolated on transparent background for overlay
```

---

## HE-04: Floating UI Element 2 - Analytics Widget
**File:** `public/images/hero/float-analytics.webp`
**Format:** WebP
**Size:** 500×350px
**Transparent:** Yes

**PROMPT:**
```
Floating analytics dashboard widget, glass morphism, showing growth chart
with upward trend line in blueprint blue #3A5A7C, metric cards showing
"+147% Engagement" and "2.3x ROI", warm cream semi-transparent background,
charcoal typography #1A1A1A, minimal grid lines, data visualization aesthetic,
soft ambient glow, 12px rounded corners, slight rotation for depth,
isolated on transparent background
```

---

## HE-05: Floating UI Element 3 - AI Assistant
**File:** `public/images/hero/float-ai.webp`
**Format:** WebP
**Size:** 450×500px
**Transparent:** Yes

**PROMPT:**
```
Floating AI chat interface, glass morphism, conversation bubbles showing
founder asking "What's my next move?" and AI responding with strategic
recommendations, warm cream background, blueprint blue accents #3A5A7C
for AI avatar indicator, charcoal text #1A1A1A, typing indicator animation
frame, soft glow effect, 16px rounded corners, slight left tilt,
isolated on transparent background for parallax layering
```

---

# PRODUCT DEMO ASSETS

## PD-01: Dashboard Full View
**File:** `public/images/product/dashboard-full.webp`
**Format:** WebP
**Size:** 2880×1800px
**Transparent:** No

**PROMPT:**
```
Full-screen SaaS dashboard screenshot, RaptorFlow marketing operating system,
dark mode interface option with warm cream light mode shown,
central command center with:
- Top navigation with workspace selector
- Left sidebar: Strategy, Content, Campaigns, Analytics, Moves
- Main area: Visual workflow builder with connected nodes
- Node types: Triggers, Actions, Decisions, Delays
- Blueprint blue #3A5A7C connection lines
- Charcoal #1A1A1A text on cream #F5F3EE background
- Card components with 12px radius
- Subtle depth shadows
- Premium productivity app aesthetic, Notion meets Linear
- Clean, organized, powerful appearance
```

---

## PD-02: Mobile App View
**File:** `public/images/product/mobile-app.webp`
**Format:** WebP
**Size:** 1200×2400px
**Transparent:** No

**PROMPT:**
```
Mobile app interface for iPhone 15 Pro, RaptorFlow companion app,
showing push notification "Your Move for today" and quick-action dashboard,
warm cream background #F5F3EE, charcoal text #1A1A1A,
blueprint blue #3A5A7C accent buttons, card-based layout,
swipe gestures implied, bottom tab navigation,
minimalist mobile UI, Apple Design Award quality,
device frame optional, clean screenshot style
```

---

## PD-03: Feature Screenshot - Strategy Builder
**File:** `public/images/product/feature-strategy.webp`
**Format:** WebP
**Size:** 1600×1000px
**Transparent:** No

**PROMPT:**
```
Strategy builder interface screenshot, visual canvas with sticky notes
and connection lines, founder's marketing strategy mapped out,
ICP definition cards, positioning statement generator visible,
warm cream canvas #F5F3EE, blueprint blue grid lines #3A5A7C,
charcoal text #1A1A1A, interactive node elements,
zoom controls visible, premium Miro/FigJam alternative aesthetic
```

---

## PD-04: Feature Screenshot - Content Calendar
**File:** `public/images/product/feature-calendar.webp`
**Format:** WebP
**Size:** 1600×1000px
**Transparent:** No

**PROMPT:**
```
Content calendar interface, month view with scheduled posts,
color-coded content pillars, drag-and-drop cards,
AI-generated content suggestions sidebar,
warm cream background #F5F3EE, charcoal #1A1A1A text,
blueprint blue #3A5A7C for scheduled items,
today highlighted, clean grid layout,
premium editorial calendar aesthetic
```

---

## PD-05: Feature Screenshot - Analytics Dashboard
**File:** `public/images/product/feature-analytics.webp`
**Format:** WebP
**Size:** 1600×1000px
**Transparent:** No

**PROMPT:**
```
Analytics dashboard interface, clean data visualization,
line charts showing growth trends, bar charts for engagement,
metric cards with percentage changes,
warm cream background #F5F3EE, charcoal #1A1A1A text,
blueprint blue #3A5A7C chart lines, subtle grid,
date range selector, export options,
professional business intelligence aesthetic
```

---

# FEATURE SECTION ASSETS

## FE-01: Feature Icon - Strategy OS
**File:** `public/images/features/icon-strategy.svg`
**Format:** SVG
**Size:** 120×120px viewBox
**Transparent:** Yes

**PROMPT:**
```
Geometric icon representing strategy operating system,
compass overlaid with circuit board patterns,
architectural blueprint aesthetic, line art style,
blueprint blue #3A5A7C stroke, 2px line weight,
clean geometric construction, no fill,
minimalist technical drawing style
```

---

## FE-02: Feature Icon - AI Co-Pilot
**File:** `public/images/features/icon-ai.svg`
**Format:** SVG
**Size:** 120×120px viewBox
**Transparent:** Yes

**PROMPT:**
```
Geometric icon representing AI co-pilot,
brain silhouette combined with airplane wing motifs,
neural network node patterns, line art style,
blueprint blue #3A5A7C stroke, 2px line weight,
clean vector paths, symmetrical design,
minimalist technical illustration
```

---

## FE-03: Feature Icon - Content Engine
**File:** `public/images/features/icon-content.svg`
**Format:** SVG
**Size:** 120×120px viewBox
**Transparent:** Yes

**PROMPT:**
```
Geometric icon representing content generation engine,
generative burst pattern with document/page motifs,
particles emanating from central source, line art style,
blueprint blue #3A5A7C stroke, 2px line weight,
dynamic motion implied in static form,
minimalist technical drawing
```

---

## FE-04: Feature Icon - Campaign Builder
**File:** `public/images/features/icon-campaign.svg`
**Format:** SVG
**Size:** 120×120px viewBox
**Transparent:** Yes

**PROMPT:**
```
Geometric icon representing campaign orchestration,
interconnected nodes forming campaign flow,
megaphone silhouette integrated with network topology,
blueprint blue #3A5A7C stroke, 2px line weight,
clean vector paths, architectural precision
```

---

## FE-05: Feature Icon - Analytics Intelligence
**File:** `public/images/features/icon-analytics.svg`
**Format:** SVG
**Size:** 120×120px viewBox
**Transparent:** Yes

**PROMPT:**
```
Geometric icon representing analytics intelligence,
eye motif combined with bar chart and trend line,
360-degree vision metaphor, line art style,
blueprint blue #3A5A7C stroke, 2px line weight,
symmetrical design, technical drawing aesthetic
```

---

## FE-06: Feature Illustration - Workflow Visualization
**File:** `public/images/features/workflow-illustration.webp`
**Format:** WebP
**Size:** 1200×800px
**Transparent:** Yes

**PROMPT:**
```
Isometric workflow visualization, marketing automation flowchart,
connected nodes showing: Trigger → Analysis → Decision → Action → Measure,
3D isometric perspective, warm cream #F5F3EE and blueprint blue #3A5A7C color scheme,
charcoal #1A1A1A connecting lines, floating elements with subtle shadows,
clean technical illustration style, isometric grid alignment,
isolated on transparent background for overlay flexibility
```

---

## FE-07: Feature Illustration - AI Brain
**File:** `public/images/features/ai-brain.webp`
**Format:** WebP
**Size:** 800×800px
**Transparent:** Yes

**PROMPT:**
```
Abstract AI brain visualization, geometric neural network,
interconnected nodes and pathways, glowing blueprint blue #3A5A7C connections,
warm cream #F5F3EE node centers, charcoal #1A1A1A pathways,
floating 3D geometric shapes representing data processing,
soft ambient glow, technical yet organic,
isolated on transparent background
```

---

# SOCIAL PROOF ASSETS

## SP-01: Founder Photo - Tech Startup
**File:** `public/images/testimonials/founder-01.webp`
**Format:** WebP
**Size:** 400×400px
**Transparent:** No

**PROMPT:**
```
Professional headshot, tech startup founder, 30s, confident expression,
neutral background, warm natural lighting, business casual attire,
high-quality portrait photography, shallow depth of field,
color grading matches warm cream aesthetic,
square crop, suitable for circular avatar display
```

---

## SP-02: Founder Photo - E-commerce
**File:** `public/images/testimonials/founder-02.webp`
**Format:** WebP
**Size:** 400×400px
**Transparent:** No

**PROMPT:**
```
Professional headshot, e-commerce brand founder, 40s, approachable smile,
clean studio background, soft professional lighting,
smart casual blazer, high-quality portrait,
warm color tones, square crop for avatar
```

---

## SP-03: Founder Photo - SaaS
**File:** `public/images/testimonials/founder-03.webp`
**Format:** WebP
**Size:** 400×400px
**Transparent:** No

**PROMPT:**
```
Professional headshot, B2B SaaS founder, 35, thoughtful expression,
minimalist background, editorial lighting style,
dark turtleneck, premium portrait aesthetic,
consistent warm color grading, square format
```

---

## SP-04: Company Logos - Logo Bar
**Files:**
- `public/images/testimonials/logo-company-01.svg`
- `public/images/testimonials/logo-company-02.svg`
- `public/images/testimonials/logo-company-03.svg`
- `public/images/testimonials/logo-company-04.svg`
- `public/images/testimonials/logo-company-05.svg`
**Format:** SVG
**Size:** 200×60px viewBox each
**Transparent:** Yes
**Color:** Grayscale/muted

**PROMPT (for each):**
```
Minimalist company wordmark, fictional tech/SaaS company,
clean sans-serif typography, grayscale #7A7A7A,
designed for logo bar display, horizontal layout,
professional B2B brand aesthetic, simple geometric mark optional
```

---

# BACKGROUND & AMBIENT ASSETS

## BG-01: Paper Texture Overlay
**File:** `public/images/textures/paper-grain.webp`
**Format:** WebP
**Size:** 1024×1024px (tileable)
**Transparent:** No

**PROMPT:**
```
Subtle paper texture, warm cream tone #F5F3EE,
fine grain noise, slightly aged premium paper look,
minimal fiber visibility, seamless tileable pattern,
very subtle, designed for opacity overlay at 5-10%,
high resolution, print quality
```

---

## BG-02: Blueprint Grid Pattern
**File:** `public/images/textures/blueprint-grid.svg`
**Format:** SVG (pattern)
**Size:** 100×100px viewBox
**Transparent:** Yes

**PROMPT:**
```
Technical grid pattern, blueprint drafting style,
light lines #3A5A7C at 5% opacity on transparent,
1px stroke weight, 20px grid spacing,
subtle cross markers at intersections,
seamless repeating pattern for CSS background
```

---

## BG-03: Gradient Orb - Coral
**File:** `public/images/backgrounds/orb-coral.webp`
**Format:** WebP
**Size:** 800×800px
**Transparent:** Yes

**PROMPT:**
```
Soft gradient orb, warm coral to peach tones,
radial gradient, feathered edges for blending,
etherial glow effect, no hard edges,
suitable for background decoration layer,
isolated on transparent for overlay
```

---

## BG-04: Gradient Orb - Ocean
**File:** `public/images/backgrounds/orb-ocean.webp`
**Format:** WebP
**Size:** 800×800px
**Transparent:** Yes

**PROMPT:**
```
Soft gradient orb, blueprint blue #3A5A7C to soft teal,
radial gradient, feathered edges,
calm professional aesthetic,
background decoration element,
isolated on transparent
```

---

## BG-05: Noise Texture Overlay
**File:** `public/images/textures/noise-overlay.webp`
**Format:** WebP
**Size:** 512×512px (tileable)
**Transparent:** No

**PROMPT:**
```
Film grain noise texture, monochrome,
fine ISO 400 style grain,
seamless tileable pattern,
designed for overlay at 3-5% opacity,
adds subtle texture to flat colors
```

---

# ICON SYSTEM ASSETS

## IC-01: Icon Set - Navigation
**Files:**
- `public/images/icons/nav-dashboard.svg`
- `public/images/icons/nav-strategy.svg`
- `public/images/icons/nav-content.svg`
- `public/images/icons/nav-campaigns.svg`
- `public/images/icons/nav-analytics.svg`
**Format:** SVG
**Size:** 24×24px viewBox
**Transparent:** Yes
**Stroke:** 1.5px
**Color:** CurrentColor (CSS controllable)

**PROMPT (consistent for all):**
```
Minimalist line icon, 24x24px grid, 1.5px stroke weight,
geometric construction, no fills, no rounded caps,
sharp precise corners, technical drawing aesthetic,
consistent visual weight across icon set
```

---

## IC-02: Icon Set - Actions
**Files:**
- `public/images/icons/action-create.svg`
- `public/images/icons/action-edit.svg`
- `public/images/icons/action-delete.svg`
- `public/images/icons/action-duplicate.svg`
- `public/images/icons/action-share.svg`
**Format:** SVG
**Size:** 20×20px viewBox
**Transparent:** Yes
**Stroke:** 1.5px

---

## IC-03: Icon Set - Status
**Files:**
- `public/images/icons/status-success.svg`
- `public/images/icons/status-warning.svg`
- `public/images/icons/status-error.svg`
- `public/images/icons/status-pending.svg`
- `public/images/icons/status-draft.svg`
**Format:** SVG
**Size:** 16×16px viewBox
**Transparent:** Yes

---

# EXPORT SPECIFICATIONS

## Image Format Priority
1. **SVG** - For all icons, logos, illustrations (scalable, small file size)
2. **WebP** - For photographs, complex images (best compression/quality)
3. **PNG** - Fallback for WebP where needed (transparency support)
4. **JSON** - Lottie animations

## Resolution Standards
| Usage | Resolution | DPI | Format |
|-------|-----------|-----|--------|
| Icons | 24×24 to 120×120 | - | SVG |
| UI Mockups | 1600×1000 to 2880×1800 | 144 | WebP |
| Hero Images | 2400×1600 to 3840×2160 | 144 | WebP |
| Photos | 400×400 to 800×800 | 72 | WebP |
| Backgrounds | 1024×1024 to 3840×2160 | 72 | WebP |
| Textures | 512×512 to 1024×1024 | - | WebP |

## Color Profile
- **Primary:** sRGB
- **Acceptable:** Display P3 for hero images
- **Consistency:** All assets should match brand color temperature

## Optimization Requirements
- SVG: Run through SVGO (minification)
- WebP: Quality 85-90 for photos, 95 for UI mockups
- Max file size targets:
  - Icons: < 5KB
  - Photos: < 50KB
  - UI Mockups: < 200KB
  - Hero images: < 500KB

---

# ANIMATION ASSET NOTES

## Lottie Animations Needed
1. **Logo reveal** (preloader): 2 seconds, line drawing effect
2. **Success checkmark**: 1 second, morphing animation
3. **Loading states**: Various, subtle motion
4. **Feature icons**: Subtle hover animations

## GSAP-Ready Image Guidelines
- All floating elements should have transparent backgrounds for layering
- Shadows should be baked into images (not CSS) for parallax consistency
- Export at 2x resolution for smooth scaling animations
- Avoid complex gradients that might band during animation

---

# IMPLEMENTATION CHECKLIST

- [ ] BA-01: Primary Logo Mark (SVG)
- [ ] BA-02: Wordmark Logo (SVG)
- [ ] BA-03: Logo Animated (Lottie)
- [ ] HE-01: Hero Dashboard Mockup (WebP)
- [ ] HE-02: Hero Background Abstract (WebP)
- [ ] HE-03: Float Strategy Card (WebP, transparent)
- [ ] HE-04: Float Analytics Widget (WebP, transparent)
- [ ] HE-05: Float AI Assistant (WebP, transparent)
- [ ] PD-01 to PD-05: Product Screenshots (WebP)
- [ ] FE-01 to FE-05: Feature Icons (SVG)
- [ ] FE-06: Workflow Illustration (WebP, transparent)
- [ ] FE-07: AI Brain Illustration (WebP, transparent)
- [ ] SP-01 to SP-03: Founder Photos (WebP)
- [ ] SP-04: Company Logos (SVG)
- [ ] BG-01 to BG-05: Backgrounds & Textures
- [ ] IC-01 to IC-03: Icon Systems (SVG)

---

*Document Version: 1.0*
*Created for: RaptorFlow Landing Page Redesign*
*Style: Warm Architectural Paper + Mechanical Motion*
*Target: Award-winning GSAP-heavy experience*
