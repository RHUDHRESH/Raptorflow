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

## Phase 11: Competitive Landscape Mapping (Step 8) [checkpoint: 53f106c]
- [x] Task: Implement CompetitorAnalyzer agent for deep rival research.
- [x] Task: Build Step 8 backend endpoint for comparative angle results.
- [x] Task: Implement "Vantage Point" logic to identify leverage (Your Leverage).
- [x] Task: Build the rival hook vs your gap mapping.
- [x] Task: Write TDD tests for competitor weakness detection.
- [x] Task: Conductor - User Manual Verification 'Phase 11: Competitive Landscape Mapping (Step 8)' (Protocol in workflow.md)

## Phase 12: Market Category Selection Logic (Step 9) [checkpoint: 53f106c]
- [x] Task: Implement CategoryAdvisor agent for Safe/Clever/Bold pathing.
- [x] Task: Build Step 9 backend endpoint for category path selection.
- [x] Task: Implement pros/cons generation for each strategic path.
- [x] Task: Build pricing and effort implication logic for selected paths.
- [x] Task: Write TDD tests for strategic path recommendation logic.
- [x] Task: Conductor - User Manual Verification 'Phase 12: Market Category Selection Logic (Step 9)' (Protocol in workflow.md)

## Phase 13: Capability Uniqueness Engine (Step 10) [checkpoint: 53f106c]
- [x] Task: Implement CapabilityAuditor agent for 4-tier rating.
- [x] Task: Build Step 10 backend endpoint for capability ratings.
- [x] Task: Implement "Verification" tool to audit "Only You" claims via Titan Sorter.
- [x] Task: Build the capability-to-competitor gap analysis logic.
- [x] Task: Write TDD tests for uniqueness verification accuracy.
- [x] Task: Conductor - User Manual Verification 'Phase 13: Capability Uniqueness Engine (Step 10)' (Protocol in workflow.md)

## Phase 14: Step 12 Backend - StrategicGridGenerator (Strategic Grid) [checkpoint: f753b03]
- [x] Task: Implement Step 12 'handle_strategic_grid' node.
- [x] Task: Create StrategicGridGenerator to populate the 2x2 grid (Value vs Rarity).
- [x] Task: Automate asset categorization based on capability ratings from Step 10.
- [x] Task: Conductor - User Manual Verification 'Phase 14: Step 12 Backend - StrategicGridGenerator (Strategic Grid)' (Protocol in workflow.md)

## Phase 15: Step 13 Backend - PositioningStatementGenerator (Final Positioning) [checkpoint: f753b03]
- [x] Task: Implement Step 13 'handle_positioning_statements' logic.
- [x] Task: Generate statements across multiple frameworks (Classic, Challenger, Benefit-Focused).
- [x] Task: Synthesize all research and truths into a definitive "Master Positioning" object.
- [x] Task: Conductor - User Manual Verification 'Phase 15: Step 13 Backend - PositioningStatementGenerator (Final Positioning)' (Protocol in workflow.md)

## Phase 16: Neuroscience Copywriting Engine (Step 13) [checkpoint: f85fe1e]
- [x] Task: Implement NeuroscienceCopywriter agent for manifesto drafting.
- [x] Task: Build Step 13 backend endpoint for positioning statements.
- [x] Task: Implement "Limbic Activation" scoring for brand copy.
- [x] Task: Build the 6-principle compliance auditor for every draft.
- [x] Task: Write TDD tests for copy score accuracy.
- [x] Task: Conductor - User Manual Verification 'Phase 16: Neuroscience Copywriting Engine (Step 13)' (Protocol in workflow.md)

## Phase 17: Focus & Sacrifice Constraint Engine (Step 14) [checkpoint: f85fe1e]
- [x] Task: Implement ConstraintEngine to enforce strategic trade-offs.
- [x] Task: Build Step 14 backend endpoint for focus/sacrifice decisions.
- [x] Task: Implement "Lightbulb" explanation logic for forced sacrifices.
- [x] Task: Build the David vs Goliath logic (e.g., Sacrificing Enterprise).
- [x] Task: Write TDD tests for constraint enforcement logic.
- [x] Task: Conductor - User Manual Verification 'Phase 17: Focus & Sacrifice Constraint Engine (Step 14)' (Protocol in workflow.md)

## Phase 18: Step 16 Backend - BuyingProcessArchitect (Sales Cycle) [checkpoint: afad9e1]
- [x] Task: Implement Step 16 'handle_buying_process' node.
- [x] Task: Create BuyingProcessArchitect to map the sales cycle and buyer journey.
- [x] Task: Define "Trust Milestones" for each stage based on ICP psychographics.
- [x] Task: Conductor - User Manual Verification 'Phase 18: Step 16 Backend - BuyingProcessArchitect (Sales Cycle)' (Protocol in workflow.md)

## Phase 19: Step 17 Backend - MessagingRulesEngine (Messaging Guardrails) [checkpoint: afad9e1]
- [x] Task: Implement Step 17 'handle_messaging_guardrails' node.
- [x] Task: Create MessagingRulesEngine to define what we say, how we say it, and what we NEVER say.
- [x] Task: Automate voice/tone rules based on the Category Path (Safe vs Bold).
- [x] Task: Conductor - User Manual Verification 'Phase 19: Step 17 Backend - MessagingRulesEngine (Messaging Guardrails)' (Protocol in workflow.md)

## Phase 20: Messaging Guardrails & Enforcement (Step 17) [checkpoint: 9fe65cc]
- [x] Task: Implement MessagingRulesEngine to define voice/tone guardrails.
- [x] Task: Build Step 17 node 'handle_messaging_guardrails'.
- [x] Task: Implement real-time "Forbidden Word" detection logic.
- [x] Task: Conductor - User Manual Verification 'Phase 20: Messaging Guardrails & Enforcement (Step 17)' (Protocol in workflow.md)

## Phase 21: Soundbites Library & Copy Blocks (Step 18) [checkpoint: 9fe65cc]
- [x] Task: Implement SoundbitesGenerator for messaging library assembly.
- [x] Task: Build Step 18 node 'handle_soundbites_library'.
- [x] Task: Generate taglines, value props, and elevator pitches.
- [x] Task: Conductor - User Manual Verification 'Phase 21: Soundbites Library & Copy Blocks (Step 18)' (Protocol in workflow.md)

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
