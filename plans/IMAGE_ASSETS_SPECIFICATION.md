# RaptorFlow Landing Page — Image Asset Specification

## Overview

This document specifies all custom vector images and illustrations needed for the award-winning landing page. All images should be generated as **SVG vector files** or **high-resolution PNGs with transparency** (minimum 2x retina).

**Color Palette Reference**: Use the RaptorFlow brand colors
- Canvas: #F5F3EE
- Ink: #1A1A1A
- Blueprint: #3A5A7C
- Coral: #E08D79
- Sage: #9CAF98
- Ocean: #8CA9B3
- Lavender: #B3A5B8

---

## Folder Structure

```
public/
├── images/
│   ├── landing/
│   │   ├── hero/
│   │   ├── problem/
│   │   ├── solution/
│   │   ├── product-demo/
│   │   ├── features/
│   │   ├── how-it-works/
│   │   ├── testimonials/
│   │   ├── pricing/
│   │   ├── faq/
│   │   └── cta/
│   ├── textures/
│   │   ├── paper-grain.png
│   │   ├── noise-overlay.png
│   │   └── blueprint-grid.svg
│   └── icons/
│       └── landing-icons/
└── videos/
    └── landing/
```

---

## HERO SECTION IMAGES

### 1. Dashboard Preview — Main Hero Visual
**File**: [`hero-dashboard-preview.webp`](public/images/landing/hero/dashboard-preview.webp)
**Dimensions**: 1440x900px (16:10)
**Format**: WebP with transparency support
**Transparent Background**: No (has subtle shadow)

**Generation Prompt**:
```
Clean, minimal SaaS dashboard interface mockup floating at 15-degree angle,
warm paper-white background #F5F3EE. Dashboard shows:
- Left sidebar navigation with icons for Positioning, Strategy, Content, Analytics
- Main area displays "Weekly Moves" content calendar with coral #E08D79 accent cards
- Top bar shows "Marketing OS" branding in editorial typography
- Subtle blueprint grid pattern #3A5A7C at 5% opacity in background
- Soft diffused shadow beneath dashboard
- Rounded corners 16px, no harsh borders
- Isometric 3D perspective view
- Professional, architectural aesthetic
- No text labels, use abstract content blocks
- High-end product photography lighting
```

---

### 2. Hero Gradient Orb — Coral
**File**: [`hero-orb-coral.svg`](public/images/landing/hero/orb-coral.svg)
**Dimensions**: 600x600px
**Format**: SVG Vector
**Transparent Background**: Yes

**Generation Prompt**:
```
Abstract gradient orb, perfectly circular, soft ethereal glow,
gradient from coral #E08D79 center to transparent edges,
feathery edges with 40% opacity fade,
subtle inner glow effect,
vector format with radial gradient,
no hard edges, cloud-like softness,
architectural lighting quality
```

---

### 3. Hero Gradient Orb — Ocean
**File**: [`hero-orb-ocean.svg`](public/images/landing/hero/orb-ocean.svg)
**Dimensions**: 500x500px
**Format**: SVG Vector
**Transparent Background**: Yes

**Generation Prompt**:
```
Abstract gradient orb, perfectly circular, soft ethereal glow,
gradient from ocean blue #8CA9B3 center to transparent edges,
feathery edges with 35% opacity fade,
subtle inner glow effect,
vector format with radial gradient,
no hard edges, mist-like softness,
calm atmospheric quality
```

---

### 4. Hero Gradient Orb — Sage
**File**: [`hero-orb-sage.svg`](public/images/landing/hero/orb-sage.svg)
**Dimensions**: 400x400px
**Format**: SVG Vector
**Transparent Background**: Yes

**Generation Prompt**:
```
Abstract gradient orb, perfectly circular, soft ethereal glow,
gradient from sage green #9CAF98 center to transparent edges,
feathery edges with 30% opacity fade,
subtle inner glow effect,
vector format with radial gradient,
organic natural softness,
growth and vitality feeling
```

---

### 5. Grid Pattern Overlay
**File**: [`hero-grid-pattern.svg`](public/images/landing/hero/grid-pattern.svg)
**Dimensions**: 100x100px (tileable)
**Format**: SVG Pattern
**Transparent Background**: Yes

**Generation Prompt**:
```
Minimal architectural grid pattern,
1px lines in ink color #1A1A1A at 3% opacity,
64px grid spacing,
intersection dots at 5% opacity,
seamless tileable pattern,
blueprint aesthetic,
precise technical drawing feel
```

---

## PROBLEM SECTION IMAGES

### 6. Tool Sprawl Illustration
**File**: [`problem-tool-sprawl.svg`](public/images/landing/problem/tool-sprawl.svg)
**Dimensions**: 800x600px
**Format**: SVG Vector
**Transparent Background**: Yes

**Generation Prompt**:
```
Abstract illustration of fragmented marketing tools,
six disconnected geometric shapes floating chaotically,
each shape represents a different tool:
- Calendar (coral tint)
- Chart (blueprint tint)
- Document (sage tint)
- Robot head (lavender tint)
- Social icons (ocean tint)
- Spreadsheet (muted gray)
Shapes are breaking apart, arrows pointing in different directions,
dotted connection lines that are broken/cut,
warm paper background #F5F3EE,
minimalist flat vector style,
editorial illustration aesthetic,
conveying chaos and disconnection
```

---

### 7. Time Drain Visualization
**File**: [`problem-time-drain.svg`](public/images/landing/problem/time-drain.svg)
**Dimensions**: 600x400px
**Format**: SVG Vector
**Transparent Background**: Yes

**Generation Prompt**:
```
Abstract hourglass with sand transforming into notifications,
pixelated sand particles becoming email/message icons,
coral #E08D79 accent on falling sand,
upper chamber nearly empty,
lower chamber overflowing with icons,
ink #1A1A1A outline strokes,
warm paper background,
editorial illustration style,
conveying time being consumed by busywork
```

---

## SOLUTION SECTION IMAGES

### 8. Marketing OS Core — Central Hub
**File**: [`solution-os-hub.svg`](public/images/landing/solution/os-hub.svg)
**Dimensions**: 700x700px
**Format**: SVG Vector
**Transparent Background**: Yes

**Generation Prompt**:
```
Central hub and spoke diagram representing unified marketing OS,
center: circular node with compass icon in coral #E08D79,
three main spokes connecting to satellite nodes:
- Positioning spoke: target icon, blueprint #3A5A7C
- Strategy spoke: chess piece icon, sage #9CAF98
- Execution spoke: lightning bolt, coral #E08D79
orbital rings around center showing integration flow,
connecting lines pulse with energy,
clean geometric vector style,
warm paper background,
conveying unity and system architecture
```

---

### 9. Integration Flow Visualization
**File**: [`solution-integration-flow.svg`](public/images/landing/solution/integration-flow.svg)
**Dimensions**: 900x400px
**Format**: SVG Vector
**Transparent Background**: Yes

**Generation Prompt**:
```
Data flow visualization showing seamless integration,
three horizontal layers connected by flowing lines:
Top layer: Input sources (social icons, document icons) in muted colors
Middle layer: RaptorFlow processing hub in coral #E08D79
Bottom layer: Output destinations (analytics, published content) in blueprint #3A5A7C
flowing curved connection lines with animated dash pattern feel,
particles moving along paths,
clean modern diagram style,
warm paper background,
conveying smooth data transformation
```

---

## PRODUCT DEMO SECTION IMAGES

### 10. Positioning Screen Mockup
**File**: [`demo-positioning.webp`](public/images/landing/product-demo/positioning.webp)
**Dimensions**: 1200x750px
**Format**: WebP
**Transparent Background**: No

**Generation Prompt**:
```
ICP Canvas interface mockup,
clean minimal UI on warm paper background,
left panel: "Ideal Customer Profile" with attribute cards,
center: Venn diagram showing overlapping circles for demographics, psychographics, behavior,
right panel: "Value Proposition Matrix" grid,
accent color: blueprint #3A5A7C,
rounded corners 12px,
subtle shadows,
editorial typography,
professional SaaS interface design,
no actual text, use placeholder blocks
```

---

### 11. Strategy Screen Mockup
**File**: [`demo-strategy.webp`](public/images/landing/product-demo/strategy.webp)
**Dimensions**: 1200x750px
**Format**: WebP
**Transparent Background**: No

**Generation Prompt**:
```
90-Day War Plan interface mockup,
clean minimal UI on warm paper background,
horizontal timeline showing 12 weeks,
weekly "Move" cards with coral #E08D79 accent,
content themes row with color-coded tags,
experiment tracker with hypothesis cards,
left sidebar: strategy pillars with progress indicators,
rounded corners 12px,
editorial typography,
professional SaaS interface,
no actual text content
```

---

### 12. Content Screen Mockup
**File**: [`demo-content.webp`](public/images/landing/product-demo/content.webp)
**Dimensions**: 1200x750px
**Format**: WebP
**Transparent Background**: No

**Generation Prompt**:
```
AI Content Generator interface mockup,
clean minimal UI on warm paper background,
left panel: Brand Voice settings with voice sliders,
center: Content editor with AI suggestions highlighted in coral #E08D79,
right panel: Preview cards for different platforms,
top: Content type selector with icons,
bottom: Generate button with sparkle icon,
rounded corners 12px,
professional SaaS interface,
no actual text content
```

---

### 13. Analytics Screen Mockup
**File**: [`demo-analytics.webp`](public/images/landing/product-demo/analytics.webp)
**Dimensions**: 1200x750px
**Format**: WebP
**Transparent Background**: No

**Generation Prompt**:
```
Pipeline Analytics Dashboard mockup,
clean minimal UI on warm paper background,
top row: KPI cards showing pipeline metrics in coral #E08D79,
main area: Revenue attribution chart with gradient area fill in blueprint #3A5A7C,
right panel: Top performing content list,
bottom: Funnel visualization with conversion rates,
data visualization in brand colors,
rounded corners 12px,
professional SaaS interface,
no actual numbers
```

---

## FEATURES SECTION IMAGES

### 14. AI Strategy Engine Icon
**File**: [`feature-ai-strategy.svg`](public/images/landing/features/ai-strategy.svg)
**Dimensions**: 200x200px
**Format**: SVG Vector
**Transparent Background**: Yes

**Generation Prompt**:
```
Abstract AI brain with strategy elements,
geometric brain shape with circuit patterns,
compass rose integrated into neural pathways,
coral #E08D79 primary with ink #1A1A1A outlines,
orbiting particles representing data points,
vector flat illustration style,
clean minimal design,
symbolizing intelligent planning
```

---

### 15. Pipeline Analytics Icon
**File**: [`feature-analytics.svg`](public/images/landing/features/analytics.svg)
**Dimensions**: 200x200px
**Format**: SVG Vector
**Transparent Background**: Yes

**Generation Prompt**:
```
Abstract analytics visualization,
ascending bar chart transforming into pipeline funnel,
geometric bars in blueprint #3A5A7C gradient,
connecting lines showing attribution flow,
circular nodes representing touchpoints,
upward trajectory arrow,
vector flat illustration,
clean data visualization aesthetic,
symbolizing revenue tracking
```

---

### 16. Content Generator Icon
**File**: [`feature-content.svg`](public/images/landing/features/content.svg)
**Dimensions**: 200x200px
**Format**: SVG Vector
**Transparent Background**: Yes

**Generation Prompt**:
```
Abstract content creation visualization,
document page with magic sparkle elements,
quill pen morphing into digital cursor,
flowing lines representing text generation,
sage #9CAF98 primary with coral #E08D79 sparkles,
particles emanating from page,
vector flat illustration style,
clean modern design,
symbolizing AI-powered writing
```

---

### 17. ICP Profiler Icon
**File**: [`feature-icp.svg`](public/images/landing/features/icp.svg)
**Dimensions**: 200x200px
**Format**: SVG Vector
**Transparent Background**: Yes

**Generation Prompt**:
```
Abstract ideal customer profile visualization,
target bullseye with person silhouette center,
concentric rings showing profile dimensions,
attribute tags orbiting target,
lavender #B3A5B8 primary with ink outlines,
geometric precision,
vector flat illustration,
clean iconographic style,
symbolizing precise targeting
```

---

### 18. Brand Voice Icon
**File**: [`feature-voice.svg`](public/images/landing/features/voice.svg)
**Dimensions**: 200x200px
**Format**: SVG Vector
**Transparent Background**: Yes

**Generation Prompt**:
```
Abstract brand voice visualization,
sound waves forming unique fingerprint pattern,
microphone icon with neural network overlay,
waveform visualization in coral #E08D79,
unique pattern showing voice distinctiveness,
vector flat illustration,
clean modern design,
symbolizing voice training and consistency
```

---

### 19. Smart Scheduling Icon
**File**: [`feature-scheduling.svg`](public/images/landing/features/scheduling.svg)
**Dimensions**: 200x200px
**Format**: SVG Vector
**Transparent Background**: Yes

**Generation Prompt**:
```
Abstract smart scheduling visualization,
calendar grid with optimal time slots highlighted,
clock hands merging with analytics graph,
ocean #8CA9B3 primary color,
orbiting dots representing audience activity,
vector flat illustration,
clean minimal design,
symbolizing intelligent timing
```

---

### 20. Data Privacy Icon
**File**: [`feature-privacy.svg`](public/images/landing/features/privacy.svg)
**Dimensions**: 200x200px
**Format**: SVG Vector
**Transparent Background**: Yes

**Generation Prompt**:
```
Abstract data security visualization,
shield with lock mechanism,
data packets protected within shield boundary,
sage #9CAF98 primary with ink outlines,
encryption pattern overlay,
secure vault symbolism,
vector flat illustration,
clean trustworthy design,
symbolizing enterprise security
```

---

### 21. Integrations Icon
**File**: [`feature-integrations.svg`](public/images/landing/features/integrations.svg)
**Dimensions**: 200x200px
**Format**: SVG Vector
**Transparent Background**: Yes

**Generation Prompt**:
```
Abstract integrations hub visualization,
central connector node with multiple platform icons,
flowing connection lines to surrounding tools,
blueprint #3A5A7C primary color,
synchronized flow pattern,
seamless connection symbolism,
vector flat illustration,
clean technical design,
symbolizing tool connectivity
```

---

## HOW IT WORKS SECTION IMAGES

### 22. Step 1 — Position Path Node
**File**: [`how-position-node.svg`](public/images/landing/how-it-works/position-node.svg)
**Dimensions**: 300x300px
**Format**: SVG Vector
**Transparent Background**: Yes

**Generation Prompt**:
```
Journey path node for "Position" step,
compass icon centered in circular node,
orbital ring with waypoint marker,
blueprint #3A5A7C primary,
activated state glow effect,
connecting path entry and exit points,
vector flat illustration,
clean navigation aesthetic,
step 1 of 4 in journey
```

---

### 23. Step 2 — Strategy Path Node
**File**: [`how-strategy-node.svg`](public/images/landing/how-it-works/strategy-node.svg)
**Dimensions**: 300x300px
**Format**: SVG Vector
**Transparent Background**: Yes

**Generation Prompt**:
```
Journey path node for "Strategy" step,
chess knight icon centered in circular node,
orbital ring with waypoint marker,
sage #9CAF98 primary,
activated state glow effect,
connecting path entry and exit points,
vector flat illustration,
clean navigation aesthetic,
step 2 of 4 in journey
```

---

### 24. Step 3 — Execute Path Node
**File**: [`how-execute-node.svg`](public/images/landing/how-it-works/execute-node.svg)
**Dimensions**: 300x300px
**Format**: SVG Vector
**Transparent Background**: Yes

**Generation Prompt**:
```
Journey path node for "Execute" step,
lightning bolt icon centered in circular node,
orbital ring with waypoint marker,
coral #E08D79 primary,
activated state glow effect,
connecting path entry and exit points,
vector flat illustration,
clean navigation aesthetic,
step 3 of 4 in journey
```

---

### 25. Step 4 — Measure Path Node
**File**: [`how-measure-node.svg`](public/images/landing/how-it-works/measure-node.svg)
**Dimensions**: 300x300px
**Format**: SVG Vector
**Transparent Background**: Yes

**Generation Prompt**:
```
Journey path node for "Measure" step,
chart trending up icon centered in circular node,
orbital ring with waypoint marker,
lavender #B3A5B8 primary,
activated state glow effect,
connecting path entry and exit points,
vector flat illustration,
clean navigation aesthetic,
step 4 of 4 in journey
```

---

## TESTIMONIALS SECTION IMAGES

### 26. Founder Avatar 1
**File**: [`avatar-founder-1.webp`](public/images/landing/testimonials/founder-1.webp)
**Dimensions**: 200x200px
**Format**: WebP
**Transparent Background**: No (solid background)

**Generation Prompt**:
```
Professional headshot style avatar,
friendly tech founder appearance,
neutral warm background matching #F5F3EE,
confident expression,
modern casual business attire,
soft studio lighting,
high-quality portrait photography style,
diverse representation,
approachable and authentic
```

---

### 27. Founder Avatar 2
**File**: [`avatar-founder-2.webp`](public/images/landing/testimonials/founder-2.webp)
**Dimensions**: 200x200px
**Format**: WebP
**Transparent Background**: No (solid background)

**Generation Prompt**:
```
Professional headshot style avatar,
female tech founder appearance,
neutral warm background matching #F5F3EE,
warm confident smile,
modern professional attire,
soft studio lighting,
high-quality portrait photography style,
diverse representation,
approachable and authentic
```

---

### 28. Founder Avatar 3
**File**: [`avatar-founder-3.webp`](public/images/landing/testimonials/founder-3.webp)
**Dimensions**: 200x200px
**Format**: WebP
**Transparent Background**: No (solid background)

**Generation Prompt**:
```
Professional headshot style avatar,
mature experienced founder appearance,
neutral warm background matching #F5F3EE,
thoughtful confident expression,
business casual attire,
soft studio lighting,
high-quality portrait photography style,
diverse representation,
authoritative and trustworthy
```

---

## PRICING SECTION IMAGES

### 29. Ascent Plan Illustration
**File**: [`pricing-ascent.svg`](public/images/landing/pricing/ascent.svg)
**Dimensions**: 400x300px
**Format**: SVG Vector
**Transparent Background**: Yes

**Generation Prompt**:
```
Abstract mountain ascent illustration,
founder figure climbing first hill/mountain,
simple geometric mountain shapes,
starting journey symbolism,
sage #9CAF98 color palette,
progress path showing beginning of climb,
vector flat illustration,
clean minimal design,
representing starter plan
```

---

### 30. Glide Plan Illustration
**File**: [`pricing-glide.svg`](public/images/landing/pricing/glide.svg)
**Dimensions**: 400x300px
**Format**: SVG Vector
**Transparent Background**: Yes

**Generation Prompt**:
```
Abstract smooth flight illustration,
founder figure with wings gliding,
cloud formations below showing altitude,
smooth curved motion lines,
coral #E08D79 color palette with glow,
momentum and growth symbolism,
vector flat illustration,
dynamic flowing design,
representing growth plan
```

---

### 31. Soar Plan Illustration
**File**: [`pricing-soar.svg`](public/images/landing/pricing/soar.svg)
**Dimensions**: 400x300px
**Format**: SVG Vector
**Transparent Background**: Yes

**Generation Prompt**:
```
Abstract soaring flight illustration,
founder figure ascending toward stars,
cosmic background with constellation patterns,
reaching new heights symbolism,
blueprint #3A5A7C and gold accents,
team silhouettes in background,
vector flat illustration,
ambitious expansive design,
representing enterprise plan
```

---

## CTA SECTION IMAGES

### 32. Final CTA Background Burst
**File**: [`cta-burst.svg`](public/images/landing/cta/burst.svg)
**Dimensions**: 800x800px
**Format**: SVG Vector
**Transparent Background**: Yes

**Generation Prompt**:
```
Abstract energy burst visualization,
radiating lines and particles from center,
coral #E08D79 and blueprint #3A5A7C gradient blend,
explosion of possibility symbolism,
particles in orbital paths,
dynamic outward motion,
vector flat illustration,
energetic inspiring design,
background element for final call-to-action
```

---

## TEXTURE ASSETS

### 33. Paper Grain Texture
**File**: [`paper-grain.png`](public/images/textures/paper-grain.png)
**Dimensions**: 512x512px (tileable)
**Format**: PNG
**Transparent**: No (multiply blend)

**Generation Prompt**:
```
Seamless paper grain texture,
subtle organic fiber pattern,
warm off-white base #F5F3EE,
very fine noise detail,
seamless tileable pattern,
5% opacity level when applied,
architectural drawing paper quality,
high resolution for retina displays
```

---

### 34. Noise Overlay
**File**: [`noise-overlay.png`](public/images/textures/noise-overlay.png)
**Dimensions**: 512x512px (tileable)
**Format**: PNG
**Transparent**: No (overlay blend)

**Generation Prompt**:
```
Film grain noise texture,
monochromatic subtle grain,
uniform noise distribution,
seamless tileable pattern,
fine granularity,
3% opacity when applied,
cinematic film quality,
high resolution
```

---

### 35. Blueprint Grid
**File**: [`blueprint-grid.svg`](public/images/textures/blueprint-grid.svg)
**Dimensions**: 100x100px (tileable)
**Format**: SVG
**Transparent**: Yes

**Generation Prompt**:
```
Technical blueprint grid pattern,
1px lines in blueprint #3A5A7C,
major lines every 100px,
minor grid lines every 20px,
cross markers at intersections,
seamless tileable pattern,
10% opacity,
architectural blueprint aesthetic
```

---

## LOGO CLOUD IMAGES

### 36-45. Company Logos (10 placeholder logos)
**Files**:
- [`logo-company-1.svg`](public/images/landing/logos/company-1.svg)
- [`logo-company-2.svg`](public/images/landing/logos/company-2.svg)
- [`logo-company-3.svg`](public/images/landing/logos/company-3.svg)
- ... through company-10.svg

**Dimensions**: 160x40px each
**Format**: SVG Vector
**Transparent Background**: Yes

**Generation Prompt**:
```
Minimalist tech company wordmark logo,
fictional company name,
clean sans-serif typography,
ink #1A1A1A color on transparent background,
modern startup aesthetic,
simple geometric icon optional,
professional trustworthy appearance,
horizontal layout,
scalable vector format
```

---

## VIDEO ASSETS

### 46. Product Demo Video (Poster Frame)
**File**: [`demo-video-poster.webp`](public/images/landing/hero/demo-video-poster.webp)
**Dimensions**: 1920x1080px
**Format**: WebP
**Transparent Background**: No

**Generation Prompt**:
```
Video poster frame showing RaptorFlow interface,
clean dashboard with content calendar visible,
play button overlay centered,
warm paper background,
professional product screenshot aesthetic,
inviting click to watch,
high-quality UI mockup,
1080p resolution quality
```

---

## GENERATION NOTES

### For AI Image Generation Tools

**Recommended Tools**:
1. **Midjourney** — Best for photorealistic mockups and avatars
2. **DALL-E 3** — Good for illustrations and icons
3. **Adobe Firefly** — Excellent for vector-style outputs
4. **Recraft** — Specialized for vector illustrations

### Vector Conversion
If generating as PNG/Raster:
1. Use **Vectorizer.AI** or **Adobe Illustrator Image Trace**
2. Convert to clean SVG with minimal paths
3. Optimize with **SVGOMG**

### Color Consistency
- Always reference the brand hex codes
- Test colors against the warm paper background #F5F3EE
- Ensure sufficient contrast for accessibility

### File Optimization
- **SVG**: Run through SVGO for minification
- **WebP**: Use 80% quality for photos, 90% for graphics
- **PNG**: Use TinyPNG for compression

---

## TOTAL ASSET COUNT

| Category | Count |
|----------|-------|
| Hero | 5 |
| Problem | 2 |
| Solution | 2 |
| Product Demo | 4 |
| Features | 8 |
| How It Works | 4 |
| Testimonials | 3 |
| Pricing | 3 |
| CTA | 1 |
| Textures | 3 |
| Logos | 10 |
| Video | 1 |
| **TOTAL** | **46 assets** |

---

*Generate these assets and place them in the specified folder structure. The landing page implementation will reference these paths directly.*
