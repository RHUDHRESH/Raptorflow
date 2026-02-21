---
name: form-handling
description: THE COMPLETE FORM HANDLING SKILL FOR RAPTORFLOW — Build every form (Brief editor, Assumptions panel, Proposals tab, Lock/Create Draft, Move selector, Campaign checklist, daily wins input, etc.) with React Hook Form + Zod validation, Tailwind tokens, GSAP micro-interactions, and full RaptorFlow v1.0 enforcement. Always redesign the entire form/page from scratch — delete old code, rewrite fresh. Invoke all relevant MCP servers (shadcn, context7, playwright, lighthouse, chrome-devtools, magicui, github). Combine with raptorflow-design-vibe, frontend-design, vision-to-frontend, mcp-frontend-tools, and frontend-animations. Never use uncontrolled inputs or basic state. Every field must feel empowering (Clarity + Control + Momentum).
license: Complete terms in LICENSE.txt (adapt for your repo)
---

# Form Handling Skill for Kimi (React Hook Form + Zod + RaptorFlow Edition)

This skill is mandatory for any form, input group, editor, or data entry UI in RaptorFlow. Briefs, Assumptions, Proposals, Lock forms, Move selection, Campaign tasks, daily wins metrics — everything. Always redesign the entire form component or page from scratch. Delete old code completely. Use React Hook Form + Zod for validation, shadcn primitives adapted to Charcoal/Ivory tokens, GSAP for every interaction, and custom Lottie for success states (rare bird). Enforce the full non-negotiable RaptorFlow skeleton and Feel Contract.

## Locked Form Rules (Painfully Enforced From RaptorFlow v1.0)
- Use only RaptorFlow tokens: --bg-surface, --border-2, --ink-1, etc.
- Labels: 12/16 600 DM Sans, slight tracking, optional uppercase
- Inputs: Surface bg, Border-2, monochrome focus ring (outer/inner)
- Errors: Small muted red dot + label (never screaming)
- Buttons: Primary Charcoal-filled, Ghost Charcoal text
- Progressive disclosure: Advanced fields hidden behind toggle (off by default)
- AI suggestions: Pull-only in right drawer Proposals tab
- Locking: Every form has explicit “Lock” / “Create Draft” with diff preview
- Copy: Operator labels (“Proposed”, “Lock”, “Deploy”), Advisor tooltips (1 sentence, reason + tradeoff)

## Tech Stack (Mandatory)
- React Hook Form + Zod resolver
- shadcn/ui components (Button, Input, Textarea, Select, Checkbox, etc.) — pulled via MCP
- Tailwind + CSS variables only
- GSAP for all feedback (field focus scale, submit success timeline, error shake)
- Custom Lottie bird for successful Lock (tiny, once)
- TypeScript interfaces for every field

## MCP Server Invocation (Always List These)
Activating MCP servers for this form:
- shadcn → pull latest Input, FormField, etc. and adapt to RaptorFlow tokens
- context7 → retrieve exact RaptorFlow field definitions and validation rules
- magicui → micro-interactions for fields
- playwright + browserbase → live form testing & accessibility validation
- lighthouse → audit form performance and accessibility (>95)
- chrome-devtools → debug form state and GSAP timelines
- github → commit form changes with diff for Lock/Draft

## Workflow (Integrate With All Previous Skills)
1. Plan: Redesign entire form from scratch per raptorflow-design-vibe
2. Activate MCPs: List which servers are used
3. Schema: Define Zod schema for every field (required, minLength, custom rules)
4. UI: Build with React Hook Form, shadcn, RaptorFlow tokens
5. Motion: Add GSAP onFocus, onSubmit success, error shake (frontend-animations)
6. Validation: Real-time + submit, show editable assumptions
7. Test: playwright visual + lighthouse audit
8. Lock Integration: On “Lock” button → show diff vs baseline + github commit
9. Grade: Must pass Clarity/Control/Momentum + reduced-motion
10. Output: Full component code + usage + MCP summary + test command

## Example Forms to Generate Perfectly
- Brief editor (rich text with inline toggle for suggestions)
- Assumptions global panel (editable table with Lock)
- Proposals drawer (ranked cards with Apply/Edit/Dismiss)
- Daily wins input in calendar (numeric + metric selector)
- Campaign task checklist (timeline hybrid)

## Final Instruction for Every Generation
Your job is to rethink and redesign every form in RaptorFlow from scratch. Pay attention to every field, every validation message, every button, every GSAP interaction, every daily wins entry. Build with React Hook Form + Zod + shadcn + GSAP + custom Lottie when bird appears. Invoke all MCP servers. Enforce quiet power vibe, clarity-first layout, control-first locking. Delete old code. No edits. Make the user feel total control.

Godspeed.
