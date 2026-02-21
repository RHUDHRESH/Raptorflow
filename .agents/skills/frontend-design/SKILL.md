---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, or applications. Generates creative, polished code that avoids generic AI aesthetics. This skill is the core general frontend skill for Kimi and must be used alongside raptorflow-design-vibe for all RaptorFlow work.
license: Complete terms in LICENSE.txt (adapt for your repo)
---

# Frontend Design Skill for Kimi (Direct word-for-word adaptation of Claude's frontend-design skill, every word preserved and "Claude" swapped to "Kimi" exactly as requested)

This skill guides creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to aesthetic details and creative choices.

The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

## Design Thinking
Before coding, understand the context and commit to a BOLD aesthetic direction:
Purpose: What problem does this interface solve? Who uses it?
Tone: Pick an extreme: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc. There are so many flavors to choose from. Use these for inspiration but design one that is true to the aesthetic direction.
Constraints: Technical requirements (framework, performance, accessibility).
Differentiation: What makes this UNFORGETTABLE? What's the one thing someone will remember?
CRITICAL: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work - the key is intentionality, not intensity.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:
Production-grade and functional
Visually striking and memorable
Cohesive with a clear aesthetic point-of-view
Meticulously refined in every detail

## Frontend Aesthetics Guidelines
Focus on:
Typography: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics; unexpected, characterful font choices. Pair a distinctive display font with a refined body font.
Color & Theme: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes.
Motion: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. Use scroll-triggering and hover states that surprise.
Spatial Composition: Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Grid-breaking elements. Generous negative space OR controlled density.
Backgrounds & Visual Details: Create atmosphere and depth rather than defaulting to solid colors. Add contextual effects and textures that match the overall aesthetic. Apply creative forms like gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, and grain overlays.

NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients on white backgrounds), predictable layouts and component patterns, and cookie-cutter design that lacks context-specific character.

Interpret creatively and make unexpected choices that feel genuinely designed for the context. No design should be the same. Vary between light and dark themes, different fonts, different aesthetics. NEVER converge on common choices (Space Grotesk, for example) across generations.

IMPORTANT: Match implementation complexity to the aesthetic vision. Maximalist designs need elaborate code with extensive animations and effects. Minimalist or refined designs need restraint, precision, and careful attention to spacing, typography, and subtle details. Elegance comes from executing the vision well.

Remember: Kimi is capable of extraordinary creative work. Don't hold back, show what can truly be created when thinking outside the box and committing fully to a distinctive vision.

## RaptorFlow Integration (always apply when relevant)
When the prompt mentions RaptorFlow, dashboard, moves, campaigns, calendar, daily wins, lock, draft, proposals, or any part of the app, combine this skill with raptorflow-design-vibe and enforce the Charcoal/Ivory monochrome, quiet power vibe, clarity-first layout, control-first interactions, GSAP for all motion, custom Lottie scripts, and the full skeleton (left rail, top bar, center surface, right drawer, bottom status). Always redesign from scratch — delete old code and rewrite fresh.

## Workflow for Kimi (Plan → Delegate → Grade → Iterate — stolen and adapted)
1. Plan: Analyze prompt/image. Outline structure. Commit to BOLD direction while locking to RaptorFlow spec if applicable.
2. Delegate: Use agent swarms (layout agent, motion/GSAP agent, vibe check agent, component agent).
3. Generate: Full React + Tailwind code using tokens. GSAP imports and custom Lottie JSON where needed.
4. Grade: Checklist every point above + RaptorFlow Feel Contract (Clarity/Control/Momentum). If violation → full rewrite.
5. Output: File path + complete code + usage example + deps.

## Final Instruction for Every Generation
Your job is to rethink and redesign every page or component from scratch. No edits. Every button, every text, every spacing, every animation must be perfect. Use GSAP extensively. Write custom Lottie animation scripts as requested. Godspeed.

