# Implementation Plan: Onboarding Master System (25-Phase Architecture)

## Phase 1: Project Setup & BCM Foundation [checkpoint: 47c09ec]
- [x] Task: Initialize backend repository and LangGraph structure.
- [x] Task: Define the `business_context.json` schema for universal state.
- [x] Task: Implement the BCM (Business Context Map) base model and sync logic.
- [x] Task: Configure Supabase checkpointer for LangGraph state persistence.
- [x] Task: Implement UCID (Unique Customer ID) generation and mapping.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Project Setup & BCM Foundation' (Protocol in workflow.md)

## Phase 2: Evidence Vault - Upload & AI Classification (Step 1) [checkpoint: 987a68c]
- [x] Task: Implement GCS upload logic with temporary storage lifecycle.
- [x] Task: Create EvidenceClassifier agent to auto-identify document types (Screenshots, Decks, URLs).
- [x] Task: Implement Step 1 backend endpoint for vault submission.
- [x] Task: Build the "Recommended Evidence" logic that updates based on uploads.
- [x] Task: Write TDD tests for auto-classification accuracy.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Evidence Vault - Upload & AI Classification (Step 1)' (Protocol in workflow.md)

## Phase 3: Extraction Engine & Intelligence (Step 2) [checkpoint: 987a68c]
- [x] Task: Implement ExtractionOrchestrator to process multi-format evidence.
- [x] Task: Integrate OCR service for document-to-text conversion.
- [x] Task: Implement Step 2 backend endpoint for fact extraction summary.
- [x] Task: Build citation logic to map every fact back to its source (file/URL).
- [x] Task: Write TDD tests for fact extraction from PDFs and images.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Extraction Engine & Intelligence (Step 2)' (Protocol in workflow.md)

## Phase 4: Data Purge Protocol & Real-time Sync (Step 1/2)
- [ ] Task: Implement the "Post-Extraction Purge" to delete GCS blobs after Step 2 verification.
- [ ] Task: Build the real-time trigger for partial `business_context.json` updates.
- [ ] Task: Implement BCM state recalculation hook for every context change.
- [ ] Task: Build validation for context integrity after file deletion.
- [ ] Task: Write TDD tests for file deletion success and context persistence.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Data Purge Protocol & Real-time Sync (Step 1/2)' (Protocol in workflow.md)

## Phase 5: Red Team Contradiction Detector (Step 3) [checkpoint: 987a68c]
- [x] Task: Implement ContradictionDetector agent for logical audit.
- [x] Task: Build Step 3 backend endpoint for inconsistency reporting.
- [x] Task: Implement "Red Team" audit layer to catch hallucinations or weak claims.
- [x] Task: Build the clarification/resolution loop for identified contradictions.
- [x] Task: Write TDD tests for detecting price-vs-positioning mismatches.
- [x] Task: Conductor - User Manual Verification 'Phase 5: Red Team Contradiction Detector (Step 3)' (Protocol in workflow.md)

## Phase 6: Truth Sheet & Versioning (Step 4) [checkpoint: 987a68c]
- [x] Task: Implement TruthSheet manager for ratifying and locking facts.
- [x] Task: Build versioning system for `business_context.json` snapshots.
- [x] Task: Implement Step 4 backend endpoint for truth confirmation.
- [x] Task: Build the "Digital Signature" logic for strategic ratification.
- [x] Task: Write TDD tests for version rollback and locking.
- [x] Task: Conductor - User Manual Verification 'Phase 6: Truth Sheet & Versioning (Step 4)' (Protocol in workflow.md)

## Phase 7: Brand Audit & Web Discovery (Step 5)
- [ ] Task: Implement BrandAudit agent to assess visual/messaging coherence.
- [ ] Task: Build Step 5 backend endpoint for brand diagnostic results.
- [ ] Task: Integrate Titan Sorter for external brand footprint discovery.
- [ ] Task: Build the "Anchor vs Accelerator" assessment logic.
- [ ] Task: Write TDD tests for brand health scoring accuracy.
- [ ] Task: Conductor - User Manual Verification 'Phase 7: Brand Audit & Web Discovery (Step 5)' (Protocol in workflow.md)

## Phase 8: Offer Architecture & Model Logic (Step 6)
- [ ] Task: Implement OfferArchitect agent for revenue model definition.
- [ ] Task: Build Step 6 backend endpoint for pricing and outcome logic.
- [ ] Task: Implement "Risk Reversal" validator for guarantee strength.
- [ ] Task: Build outcome-to-deliverable mapping in the BCM.
- [ ] Task: Write TDD tests for financial model calculations (Recurring vs One-time).
- [ ] Task: Conductor - User Manual Verification 'Phase 8: Offer Architecture & Model Logic (Step 6)' (Protocol in workflow.md)

## Phase 9: Market Intelligence - Reddit Scraper (Step 7)
- [ ] Task: Implement RedditScraper tool using Titan Sorter multiplexer.
- [ ] Task: Build subreddit discovery logic based on ICP keywords.
- [ ] Task: Implement high-speed parallel scraping for verbatims.
- [ ] Task: Build the "Stealth Scraper" pool rotation for Reddit.
- [ ] Task: Write TDD tests for Reddit data retrieval and rate-limiting.
- [ ] Task: Conductor - User Manual Verification 'Phase 9: Market Intelligence - Reddit Scraper (Step 7)' (Protocol in workflow.md)

## Phase 10: Market Intelligence - Insight Extraction (Step 7)
- [ ] Task: Implement InsightExtractor agent for Pain/Desire/Objection mapping.
- [ ] Task: Build Step 7 backend endpoint for market intelligence dossier.
- [ ] Task: Implement sentiment scoring for customer verbatims.
- [ ] Task: Build the auto-discovery logic for competitors from research data.
- [ ] Task: Write TDD tests for pain point categorization accuracy.
- [ ] Task: Conductor - User Manual Verification 'Phase 10: Market Intelligence - Insight Extraction (Step 7)' (Protocol in workflow.md)

## Phase 11: Competitive Landscape Mapping (Step 8)
- [ ] Task: Implement CompetitorAnalyzer agent for deep rival research.
- [ ] Task: Build Step 8 backend endpoint for comparative angle results.
- [ ] Task: Implement "Vantage Point" logic to identify leverage (Your Leverage).
- [ ] Task: Build the rival hook vs your gap mapping.
- [ ] Task: Write TDD tests for competitor weakness detection.
- [ ] Task: Conductor - User Manual Verification 'Phase 11: Competitive Landscape Mapping (Step 8)' (Protocol in workflow.md)

## Phase 12: Market Category Selection Logic (Step 9)
- [ ] Task: Implement CategoryAdvisor agent for Safe/Clever/Bold pathing.
- [ ] Task: Build Step 9 backend endpoint for category path selection.
- [ ] Task: Implement pros/cons generation for each strategic path.
- [ ] Task: Build pricing and effort implication logic for selected paths.
- [ ] Task: Write TDD tests for strategic path recommendation logic.
- [ ] Task: Conductor - User Manual Verification 'Phase 12: Market Category Selection Logic (Step 9)' (Protocol in workflow.md)

## Phase 13: Capability Uniqueness Engine (Step 10)
- [ ] Task: Implement CapabilityAuditor agent for 4-tier rating.
- [ ] Task: Build Step 10 backend endpoint for capability ratings.
- [ ] Task: Implement "Verification" tool to audit "Only You" claims via Titan Sorter.
- [ ] Task: Build the capability-to-competitor gap analysis logic.
- [ ] Task: Write TDD tests for uniqueness verification accuracy.
- [ ] Task: Conductor - User Manual Verification 'Phase 13: Capability Uniqueness Engine (Step 10)' (Protocol in workflow.md)

## Phase 14: Perceptual Map Generation (Step 11)
- [ ] Task: Implement PerceptualMapGenerator for quadrant analysis.
- [ ] Task: Build Step 11 backend endpoint for 3 positioning options.
- [ ] Task: Implement competitor placement logic based on scraped data.
- [ ] Task: Build "Only You" quadrant validation in 2D space.
- [ ] Task: Write TDD tests for quadrant positioning logic.
- [ ] Task: Conductor - User Manual Verification 'Phase 14: Perceptual Map Generation (Step 11)' (Protocol in workflow.md)

## Phase 15: Strategic Grid & Milestone Sync (Step 12)
- [ ] Task: Implement StrategicGrid orchestrator for position selection.
- [ ] Task: Build Step 12 backend endpoint for strategic grid summary.
- [ ] Task: Implement the "Milestone Synthesis" to update BCM after Step 12.
- [ ] Task: Build gap analysis cards for threats/opportunities.
- [ ] Task: Write TDD tests for BCM sync after grid lock.
- [ ] Task: Conductor - User Manual Verification 'Phase 15: Strategic Grid & Milestone Sync (Step 12)' (Protocol in workflow.md)

## Phase 16: Neuroscience Copywriting Engine (Step 13)
- [ ] Task: Implement NeuroscienceCopywriter agent for manifesto drafting.
- [ ] Task: Build Step 13 backend endpoint for positioning statements.
- [ ] Task: Implement "Limbic Activation" scoring for brand copy.
- [ ] Task: Build the 6-principle compliance auditor for every draft.
- [ ] Task: Write TDD tests for copy score accuracy.
- [ ] Task: Conductor - User Manual Verification 'Phase 16: Neuroscience Copywriting Engine (Step 13)' (Protocol in workflow.md)

## Phase 17: Focus & Sacrifice Constraint Engine (Step 14)
- [ ] Task: Implement ConstraintEngine to enforce strategic trade-offs.
- [ ] Task: Build Step 14 backend endpoint for focus/sacrifice decisions.
- [ ] Task: Implement "Lightbulb" explanation logic for forced sacrifices.
- [ ] Task: Build the David vs Goliath logic (e.g., Sacrificing Enterprise).
- [ ] Task: Write TDD tests for constraint enforcement logic.
- [ ] Task: Conductor - User Manual Verification 'Phase 17: Focus & Sacrifice Constraint Engine (Step 14)' (Protocol in workflow.md)

## Phase 18: ICP Deep Research & Psychographics (Step 15)
- [ ] Task: Implement ICPArchitect agent for deep persona building.
- [ ] Task: Build Step 15 backend endpoint for rich ICP profiles.
- [ ] Task: Implement "Who They Want To Become" psychographic mapping.
- [ ] Task: Build sophistication level (1-5) logic for target segments.
- [ ] Task: Write TDD tests for behavioral trigger extraction.
- [ ] Task: Conductor - User Manual Verification 'Phase 18: ICP Deep Research & Psychographics (Step 15)' (Protocol in workflow.md)

## Phase 19: Buying Process Logic (Step 16)
- [ ] Task: Implement BuyerJourney agent to map educational steps.
- [ ] Task: Build Step 16 backend endpoint for journey mapping data.
- [ ] Task: Implement "Cognitive Shift" detection for awareness stages.
- [ ] Task: Build the "Problem Aware to Product Aware" chasm logic.
- [ ] Task: Write TDD tests for journey stage transitions.
- [ ] Task: Conductor - User Manual Verification 'Phase 19: Buying Process Logic (Step 16)' (Protocol in workflow.md)

## Phase 20: Messaging Guardrails & Enforcement (Step 17)
- [ ] Task: Implement GuardrailEnforcer agent for tone/voice rules.
- [ ] Task: Build Step 17 backend endpoint for Do's and Don'ts rules.
- [ ] Task: Implement real-time "Forbidden Word" detection (e.g., Jargon).
- [ ] Task: Build anti-pattern alerts based on strategic position.
- [ ] Task: Write TDD tests for rule enforcement accuracy.
- [ ] Task: Conductor - User Manual Verification 'Phase 20: Messaging Guardrails & Enforcement (Step 17)' (Protocol in workflow.md)

## Phase 21: Soundbites Library & Copy Blocks (Step 18)
- [ ] Task: Implement SoundbiteManager for copy block assembly.
- [ ] Task: Build Step 18 backend endpoint for the soundbites library.
- [ ] Task: Implement "Approve/Improve" AI loops for copy blocks.
- [ ] Task: Build the problem-agitation-mechanism (PAM) block generator.
- [ ] Task: Write TDD tests for copy block consistency.
- [ ] Task: Conductor - User Manual Verification 'Phase 21: Soundbites Library & Copy Blocks (Step 18)' (Protocol in workflow.md)

## Phase 22: Message Hierarchy & Content Assembly (Step 19)
- [ ] Task: Implement HierarchyOrchestrator for headline-to-body mapping.
- [ ] Task: Build Step 19 backend endpoint for the message hierarchy.
- [ ] Task: Implement "Level 1-3" structural validation.
- [ ] Task: Build the "Manifesto Assembly" logic for final review.
- [ ] Task: Write TDD tests for hierarchy structural integrity.
- [ ] Task: Conductor - User Manual Verification 'Phase 22: Message Hierarchy & Content Assembly (Step 19)' (Protocol in workflow.md)

## Phase 23: Channel Architecture & TAM/SAM/SOM (Step 20/21)
- [ ] Task: Implement ChannelRecommender based on ICP behavior.
- [ ] Task: Build Step 20 backend endpoint for channel mix mapping.
- [ ] Task: Implement MarketSizer for TAM/SAM/SOM calculations.
- [ ] Task: Build Step 21 backend endpoint for market reality data.
- [ ] Task: Write TDD tests for market size calculation accuracy.
- [ ] Task: Conductor - User Manual Verification 'Phase 23: Channel Architecture & TAM/SAM/SOM (Step 20/21)' (Protocol in workflow.md)

## Phase 24: Reality Check & Validation Protocol (Step 22)
- [ ] Task: Implement ValidationTracker for non-content tasks.
- [ ] Task: Build Step 22 backend endpoint for reality check tasks.
- [ ] Task: Implement "Launch Readiness" auditor (AI score 0-100).
- [ ] Task: Build the "Skip/Commit" verification logic.
- [ ] Task: Write TDD tests for readiness score logic.
- [ ] Task: Conductor - User Manual Verification 'Phase 24: Reality Check & Validation Protocol (Step 22)' (Protocol in workflow.md)

## Phase 25: Final Synthesis & BCM Transition (Step 23)
- [ ] Task: Implement FinalSynthesis agent for "Systems Online" state.
- [ ] Task: Build Step 23 backend endpoint for onboarding finalization.
- [ ] Task: Implement the "BCM Conversion" from `business_context.json`.
- [ ] Task: Build the Global Dashboard redirect and data handover.
- [ ] Task: Task: Conductor - User Manual Verification 'Phase 25: Final Synthesis & BCM Transition' (Protocol in workflow.md)
