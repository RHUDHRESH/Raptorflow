# RaptorFlow — Muse + Shared Agent Platform (DEV.md)
**This doc tells the team what to build (requirements + contracts). Not code.**
Muse already exists visually (command box, suggestion cards, editor modal). This spec locks the **agent platform**, **skills**, **memory**, **RAG**, **storage**, and **UX contracts** that make it real.

---

## 0) Non‑Negotiables (product rules)
1. **Muse is “input → output”.** Not a dashboard.
2. **Minimal, monochrome, expensive.** Zero rainbow UI. Zero junk tiles.
3. **First draft fast enough, but premium > speed.** You said “slow but premium” is acceptable.
4. **Ambiguity policy:** never interrogate. If unclear, use **chips/cards**; max **3 questions** before a draft.
5. **Ratings teach the system.** Strong feedback becomes memory and shifts future generations.
6. **Skills are the engine.** Especially for **emails**. Users can create, tweak, and reuse Skills.

---

## 1) Current Muse UI (baseline to preserve)
### 1.1 Home / Empty state (shown in screenshot)
- Centered header: “What shall we create?”
- 3×2 suggestion cards (e.g., Cold Sales Email, LinkedIn Announcement, Industry Meme)
- Bottom command bar: `Describe what you want to create… (use / or @)`
- Helper text: `/` for asset types; ` @` to mention cohorts/competitors/campaigns

### 1.2 Conversation strip (optional)
- Small assistant bubble + minimal message stream (do not become “chat app”)
- Command bar stays anchored at bottom

### 1.3 Editor modal (text)
- Title: asset name (e.g., “Welcome Email Sequence”)
- Metadata: words, read time, save status
- Tone slider (e.g., “Professional”)
- **Save** button (primary)
- Formatting toolbar (bold/italic/headers/lists/insert)
- Right rail icons (open panels): performance, suggestions, etc.
- Optional right panel: **Performance Predictions** with compact metrics + actionable suggestions

**Note:** Keep “performance predictions” *quiet*. It must never dominate the work surface.

---

## 2) System Architecture (what ships)
### 2.1 Components
- **Frontend:** Next.js + Tailwind + shadcn/ui
- **Orchestrator:** Python service using **LangGraph** for stateful workflows + interrupts (human-in-loop). LangGraph supports pausing/resuming with `interrupt` and requires checkpointing with a persistent checkpointer for production.
- **DB:** Supabase Postgres (multi-tenant)
- **Vector:** pgvector in Postgres (tenant-scoped embeddings)
- **Storage:** Supabase Storage (exports, images, meme renders, previews)
- **Canvas editor:** Konva or Fabric
- **Text editor:** TipTap (headless editor framework on ProseMirror).

### 2.2 The only “platform” decision that matters
Everything must be **resumable**:
- generation runs
- clarifications
- editor side actions (rewrite, score, export)
- skill creation

That implies: **state persistence + run logs + idempotent tools**.

---

## 3) UX Contracts (backend ↔ UI)
### 3.1 The Ambiguity Ladder (hard requirement)
MuseRouter must choose exactly one path:
1. **Confident → generate immediately**
2. **Semi-confident → show chips/cards (3–6 options)**
3. **Not confident → ask 1–3 questions (each with choices)**

**Rule:** after max 3 questions, generate a draft anyway.

### 3.2 UI “Card” payload schema
The orchestrator returns a list of renderable UI cards. The UI never invents logic.

**Card types**
- `suggestion_grid`: curated or personalized actions (like your 3×2 grid)
- `clarify_chips`: choose one of N directions
- `clarify_questions`: 1–3 question cards with choice sets
- `generation_card`: progress animation; no %; show phases (Drafting → Polishing → Packaging)
- `result_card`: preview + actions (Open / Duplicate / Export / Save as Skill / Rate)
- `error_card`: one line + retry + “add details”

### 3.3 Editor side-panel contract
Editor can request “side intelligence” via tool calls:
- `score_asset` (hook, clarity, brand fit)
- `suggest_edits` (3–7 suggestions)
- `rewrite_section` (selected text only)
- `predict_performance` (heuristic now, model later)

**Critical:** all side panels are collapsible and default to closed.

---

## 4) LangGraph Requirements (graphs to implement)
You are building **graphs**, not “one giant agent.”

### 4.1 Graph list
1. **MuseCreateGraph**
   `prompt → classify → (clarify?) → context → choose skill → generate → quality gate → store asset → return cards`
2. **MuseRefineGraph**
   `asset_id + edit_intent → choose tool/skill → apply → new version → return patch + suggestions`
3. **SkillCreateGraph** (user creates a skill from a good output)
   `asset + edits + preferences → extract steps → generate SkillSpec → tests → publish (private/workspace/public)`
4. **SkillRunGraph**
   `skill_id + inputs → run steps → validate outputs → store run → return result_card`
5. **RAGIngestGraph**
   `source → normalize → chunk → embed → store vectors`
6. **MemoryUpdateGraph**
   `feedback events → decide write → update preference weights → store memory_event`
7. **MemeRenderGraph**
   `concept → layout plan → assets (images/fonts) → canvas JSON → raster export → store artifact`

### 4.2 Interrupt + resume rules
Use `interrupt()` when:
- you need the user to choose among options (chips/cards)
- you need approval to use an external source / organization knowledge
- you need confirmation before publishing a skill publicly

---

## 5) Agent Catalog (what “agents” exist)
### 5.1 Shared agents (used across Muse / Radar / Campaigns / Matrix / Onboarding)
**A1 — IntentRouterAgent**
- Output: `{asset_type, confidence, extracted_goal, extracted_entities}`
- Must recognize `/email`, `/meme`, `/post`, and ` @mentions`

**A2 — ClarifierAgent**
- Input: ambiguity reasons
- Output: `clarify_chips` or `clarify_questions` (max 3)
- Must prefer **choices**, not free-text

**A3 — ContextAssemblerAgent**
- Pulls: brand voice, product context, cohort context, past assets, current campaign, user skill prefs
- Output: compact context pack (<= 2k tokens equivalent)

**A4 — MemoryReaderAgent**
- Returns: top user prefs + workspace constraints (short list)
- Hard cap: 30 memories; ranked

**A5 — RAGRetrievalAgent**
- Query rewrite → retrieve → rerank → citations pack
- Store citations per output section
- Uses pgvector similarity search in Postgres.

**A6 — SkillSelectorAgent**
- Chooses the best skill (or skill pack) given intent + context
- If no match, chooses a “default skill” for that asset_type

**A7 — QualityGateAgent**
- Checks: clarity, tone, spamminess, factuality, brand fit
- Output: pass OR targeted fixes (not generic “improve”)

**A8 — CostGovernorAgent**
- Enforces per-workspace budgets (tokens, images, deep research)
- Downgrades model or reduces context as needed

**A9 — ExportAgent**
- Creates PDF/HTML/PNG/MD exports
- Heavy tasks go to queue

**A10 — TelemetryAgent**
- Emits run stats + quality metrics + latency breakdown
- Needed for iteration

### 5.2 Muse-specific agents
**M1 — EmailComposerAgent** (Skill-driven)
- Uses skill steps: Subject → Opener → Body → CTA → PS → Follow-ups
- Must support variants (`--variants 3`)
- Must support personalization placeholders (`{{name}}`, `{{company}}`)

**M2 — SocialPostAgent**
- Outputs: hook, body, CTA, hashtags (optional)
- “No cringe” filter

**M3 — MemeDirectorAgent**
- Outputs: meme concept + caption + layout plan + canvas JSON
- Delegates rendering to MemeRenderGraph

**M4 — TextPolishAgent**
- Editor command actions: shorten/expand/clarify/change tone

**M5 — PerformancePredictorAgent**
- Phase 1: heuristic scorer (not ML) with confidence tag
- Must explain suggestions in one line each

---

## 6) The Skills System (this is the moat)
### 6.1 What a Skill is
A Skill is a versioned, reusable **pipeline** that creates a typed asset.

### 6.2 SkillSpec (storage format)
Store as JSON + schema validated.
A Skill includes:
- metadata (name, category, visibility, version)
- `inputs_schema` (what it needs)
- `steps[]` (agent/prompt/tool blocks)
- `outputs_schema`
- `tests[]` (assertions)

---

## 7) Memory (preference learning)
### 7.1 Memory types
- `tone_preference`
- `structure_preference`
- `cta_preference`
- `brand_voice_rules`
- `taboo_phrases`
- `favorite_skills`

---

## 8) RAG (knowledge retrieval)
### 8.1 What gets indexed
- Onboarding answers
- Uploaded brand docs, product docs
- Past approved assets
- Dossiers (from Radar)

---

## 9) Storage (minimum schema — conceptual)
Detailed schema for Assets, Skills, Memory, RAG.

---

## 10) Meme Editor & Rendering
Konva/Fabric based canvas system.

---

## 11) Text Editor Intelligence
TipTap based.

---

## 13) Acceptance Criteria
- Ambiguity Ladder works (Confident/Semi/Not).
- Resumable graphs.
- Real-time RAG + Memory.
- Meme + Text editors functional.
