# Implementation Plan: Onboarding Master System (25-Phase Architecture)

## Phase 1: Project Setup & BCM Foundation [checkpoint: 47c09ec]
- [x] Task: Initialize backend repository and LangGraph structure.
- [x] Task: Define the `business_context.json` schema for universal state.
- [x] Task: Implement the BCM (Business Context Map) base model and sync logic.
- [x] Task: Configure Supabase checkpointer for LangGraph state persistence.
- [x] Task: Implement UCID (Unique Customer ID) generation and mapping.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Project Setup & BCM Foundation' (Protocol in workflow.md)

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

## Phase 4: Data Purge Protocol & Real-time BCM Recalculation [checkpoint: bee1a1d]
- [x] Task: Implement 'handle_data_purge' node to delete GCS blobs after extraction.
- [x] Task: Implement BCM recalculation trigger on every state update.
- [x] Task: Ensure BCM nodes/edges update in real-time based on extracted facts.
- [x] Task: Conductor - User Manual Verification 'Phase 4: Data Purge Protocol & Real-time BCM Recalculation' (Protocol in workflow.md)

## Phase 5: Adversarial Red Team - Contradiction Detector (Step 3) [checkpoint: 987a68c]
- [x] Task: Implement Step 3 'handle_contradiction_check' node.
- [x] Task: Integrate RedTeam agent to find logical inconsistencies in extracted data.
- [x] Task: Build the UI data structure for the "Adversarial Logic Audit" view.
- [x] Task: Conductor - User Manual Verification 'Phase 5: Adversarial Red Team - Contradiction Detector (Step 3)' (Protocol in workflow.md)

## Phase 6: Step 4 Backend - TruthSheetGenerator & Verified Facts [checkpoint: 987a68c]
- [x] Task: Implement Step 4 'handle_truth_sheet' logic.
- [x] Task: Consolidate all extracted and non-contradictory facts into a Truth Sheet.
- [x] Task: Add verification flags to state (User must confirm truths in UI).
- [x] Task: Conductor - User Manual Verification 'Phase 6: Step 4 Backend - TruthSheetGenerator & Verified Facts' (Protocol in workflow.md)

## Phase 7: Step 5 Backend - BrandAuditEngine (Adversarial Brand Audit) [checkpoint: bee1a1d]
- [x] Task: Create 'BrandAuditEngine' agent to look for gaps between evidence and truth.
- [x] Task: Implement Step 5 'handle_brand_audit' node logic.
- [x] Task: Store "Brand Gap Report" in state for UI rendering.
- [x] Task: Conductor - User Manual Verification 'Phase 7: Step 5 Backend - BrandAuditEngine (Adversarial Brand Audit)' (Protocol in workflow.md)

## Phase 8: Offer Architecture & Model Logic (Step 6)
- [x] Task: Implement OfferArchitect agent for revenue model definition.
- [x] Task: Build Step 6 backend endpoint for pricing and outcome logic.
- [x] Task: Implement "Risk Reversal" validator for guarantee strength.
- [x] Task: Build outcome-to-deliverable mapping in the BCM.
- [x] Task: Write TDD tests for financial model calculations (Recurring vs One-time).
- [x] Task: Conductor - User Manual Verification 'Phase 8: Offer Architecture & Model Logic (Step 6)' (Protocol in workflow.md)

## Phase 9: Market Intelligence - Reddit Scraper (Step 7)
- [x] Task: Implement RedditScraper tool using Titan Sorter multiplexer.
- [x] Task: Build subreddit discovery logic based on ICP keywords.
- [x] Task: Implement high-speed parallel scraping for verbatims.
- [x] Task: Build the "Stealth Scraper" pool rotation for Reddit.
- [x] Task: Write TDD tests for Reddit data retrieval and rate-limiting.
- [x] Task: Conductor - User Manual Verification 'Phase 9: Market Intelligence - Reddit Scraper (Step 7)' (Protocol in workflow.md)

## Phase 10: Market Intelligence - Insight Extraction (Step 7)
- [x] Task: Implement InsightExtractor agent for Pain/Desire/Objection mapping.
- [x] Task: Build Step 7 backend endpoint for market intelligence dossier.
- [x] Task: Implement sentiment scoring for customer verbatims.
- [x] Task: Build the auto-discovery logic for competitors from research data.
- [x] Task: Write TDD tests for pain point categorization accuracy.
- [x] Task: Conductor - User Manual Verification 'Phase 10: Market Intelligence - Insight Extraction (Step 7)' (Protocol in workflow.md)

## Phase 11: Competitive Landscape Mapping (Step 8)
- [x] Task: Implement CompetitorAnalyzer agent for deep rival research.
- [x] Task: Build Step 8 backend endpoint for comparative angle results.
- [x] Task: Implement "Vantage Point" logic to identify leverage (Your Leverage).
- [x] Task: Build the rival hook vs your gap mapping.
- [x] Task: Write TDD tests for competitor weakness detection.
- [x] Task: Conductor - User Manual Verification 'Phase 11: Competitive Landscape Mapping (Step 8)' (Protocol in workflow.md)

## Phase 12: Market Category Selection Logic (Step 9)
- [x] Task: Implement CategoryAdvisor agent for Safe/Clever/Bold pathing.
- [x] Task: Build Step 9 backend endpoint for category path selection.
- [x] Task: Implement pros/cons generation for each strategic path.
- [x] Task: Build pricing and effort implication logic for selected paths.
- [x] Task: Write TDD tests for strategic path recommendation logic.
- [x] Task: Conductor - User Manual Verification 'Phase 12: Market Category Selection Logic (Step 9)' (Protocol in workflow.md)

## Phase 13: Capability Uniqueness Engine (Step 10)
- [x] Task: Implement CapabilityAuditor agent for 4-tier rating.
- [x] Task: Build Step 10 backend endpoint for capability ratings.
- [x] Task: Implement "Verification" tool to audit "Only You" claims via Titan Sorter.
- [x] Task: Build the capability-to-competitor gap analysis logic.
- [x] Task: Write TDD tests for uniqueness verification accuracy.
- [x] Task: Conductor - User Manual Verification 'Phase 13: Capability Uniqueness Engine (Step 10)' (Protocol in workflow.md)

## Phase 14: Perceptual Map Generation (Step 11)
- [x] Task: Implement PerceptualMapGenerator for quadrant analysis.
- [x] Task: Build Step 11 backend endpoint for 3 positioning options.
- [x] Task: Implement competitor placement logic based on scraped data.
- [x] Task: Build "Only You" quadrant validation in 2D space.
- [x] Task: Write TDD tests for quadrant positioning logic.
- [x] Task: Conductor - User Manual Verification 'Phase 14: Perceptual Map Generation (Step 11)' (Protocol in workflow.md)

## Phase 15: Strategic Grid & Milestone Sync (Step 12)
- [x] Task: Implement StrategicGrid orchestrator for position selection.
- [x] Task: Build Step 12 backend endpoint for strategic grid summary.
- [x] Task: Implement the "Milestone Synthesis" to update BCM after Step 12.
- [x] Task: Build gap analysis cards for threats/opportunities.
- [x] Task: Write TDD tests for BCM sync after grid lock.
- [x] Task: Conductor - User Manual Verification 'Phase 15: Strategic Grid & Milestone Sync (Step 12)' (Protocol in workflow.md)

## Phase 16: Neuroscience Copywriting Engine (Step 13)
- [x] Task: Implement NeuroscienceCopywriter agent for manifesto drafting.
- [x] Task: Build Step 13 backend endpoint for positioning statements.
- [x] Task: Implement "Limbic Activation" scoring for brand copy.
- [x] Task: Build the 6-principle compliance auditor for every draft.
- [x] Task: Write TDD tests for copy score accuracy.
- [x] Task: Conductor - User Manual Verification 'Phase 16: Neuroscience Copywriting Engine (Step 13)' (Protocol in workflow.md)

## Phase 17: Focus & Sacrifice Constraint Engine (Step 14)
- [x] Task: Implement ConstraintEngine to enforce strategic trade-offs.
- [x] Task: Build Step 14 backend endpoint for focus/sacrifice decisions.
- [x] Task: Implement "Lightbulb" explanation logic for forced sacrifices.
- [x] Task: Build the David vs Goliath logic (e.g., Sacrificing Enterprise).
- [x] Task: Write TDD tests for constraint enforcement logic.
- [x] Task: Conductor - User Manual Verification 'Phase 17: Focus & Sacrifice Constraint Engine (Step 14)' (Protocol in workflow.md)

## Phase 18: ICP Deep Research & Psychographics (Step 15)
- [x] Task: Implement ICPArchitect agent for deep persona building.
- [x] Task: Build Step 15 backend endpoint for rich ICP profiles.
- [x] Task: Implement "Who They Want To Become" psychographic mapping.
- [x] Task: Build sophistication level (1-5) logic for target segments.
- [x] Task: Write TDD tests for behavioral trigger extraction.
- [x] Task: Conductor - User Manual Verification 'Phase 18: ICP Deep Research & Psychographics (Step 15)' (Protocol in workflow.md)

## Phase 19: Buying Process Logic (Step 16)
- [x] Task: Implement BuyerJourney agent to map educational steps.
- [x] Task: Build Step 16 backend endpoint for journey mapping data.
- [x] Task: Implement "Cognitive Shift" detection for awareness stages.
- [x] Task: Build the "Problem Aware to Product Aware" chasm logic.
- [x] Task: Write TDD tests for journey stage transitions.
- [x] Task: Conductor - User Manual Verification 'Phase 19: Buying Process Logic (Step 16)' (Protocol in workflow.md)

## Phase 20: Messaging Guardrails & Enforcement (Step 17)
- [x] Task: Implement GuardrailEnforcer agent for tone/voice rules.
- [x] Task: Build Step 17 backend endpoint for Do's and Don'ts rules.
- [x] Task: Implement real-time "Forbidden Word" detection (e.g., Jargon).
- [x] Task: Build anti-pattern alerts based on strategic position.
- [x] Task: Write TDD tests for rule enforcement accuracy.
- [x] Task: Conductor - User Manual Verification 'Phase 20: Messaging Guardrails & Enforcement (Step 17)' (Protocol in workflow.md)

## Phase 21: Soundbites Library & Copy Blocks (Step 18)
- [x] Task: Implement SoundbiteManager for copy block assembly.
- [x] Task: Build Step 18 backend endpoint for the soundbites library.
- [x] Task: Implement "Approve/Improve" AI loops for copy blocks.
- [x] Task: Build the problem-agitation-mechanism (PAM) block generator.
- [x] Task: Write TDD tests for copy block consistency.
- [x] Task: Conductor - User Manual Verification 'Phase 21: Soundbites Library & Copy Blocks (Step 18)' (Protocol in workflow.md)

## Phase 22: Message Hierarchy & Content Assembly (Step 19)
- [x] Task: Implement HierarchyOrchestrator for headline-to-body mapping.
- [x] Task: Build Step 19 backend endpoint for the message hierarchy.
- [x] Task: Implement "Level 1-3" structural validation.
- [x] Task: Build the "Manifesto Assembly" logic for final review.
- [x] Task: Write TDD tests for hierarchy structural integrity.
- [x] Task: Conductor - User Manual Verification 'Phase 22: Message Hierarchy & Content Assembly (Step 19)' (Protocol in workflow.md)

## Phase 23: Channel Architecture & TAM/SAM/SOM (Step 20/21)
- [x] Task: Implement ChannelRecommender based on ICP behavior.
- [x] Task: Build Step 20 backend endpoint for channel mix mapping.
- [x] Task: Implement MarketSizer for TAM/SAM/SOM calculations.
- [x] Task: Build Step 21 backend endpoint for market reality data.
- [x] Task: Write TDD tests for market size calculation accuracy.
- [x] Task: Conductor - User Manual Verification 'Phase 23: Channel Architecture & TAM/SAM/SOM (Step 20/21)' (Protocol in workflow.md)

## Phase 24: Reality Check & Validation Protocol (Step 22)
- [x] Task: Implement ValidationTracker for non-content tasks.
- [x] Task: Build Step 22 backend endpoint for reality check tasks.
- [x] Task: Implement "Launch Readiness" auditor (AI score 0-100).
- [x] Task: Build the "Skip/Commit" verification logic.
- [x] Task: Write TDD tests for readiness score logic.
- [x] Task: Conductor - User Manual Verification 'Phase 24: Reality Check & Validation Protocol (Step 22)' (Protocol in workflow.md)

## Phase 25: Final Synthesis & BCM Transition (Step 23)
- [x] Task: Implement FinalSynthesis agent for "Systems Online" state.
- [x] Task: Build Step 23 backend endpoint for onboarding finalization.
- [x] Task: Implement the "BCM Conversion" from `business_context.json`.
- [x] Task: Build the Global Dashboard redirect and data handover.
- [x] Task: Task: Conductor - User Manual Verification 'Phase 25: Final Synthesis & BCM Transition' (Protocol in workflow.md)