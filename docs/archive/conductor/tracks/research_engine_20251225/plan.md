# Plan: Industrial Research Engine (SOTA)

## Phase 1: Self-Hosted Search & GCS Foundation
- [ ] Task: Write Unit Tests: Google Custom Search Service (CSE) multi-key rotation
- [ ] Task: Implement `backend/services/search_service.py` (Cloud Run shell)
- [ ] Task: Write Unit Tests: GCS Artifact Storage & Retention
- [ ] Task: Implement `backend/utils/storage_research.py` for raw artifact vaulting
- [ ] Task: Conductor - User Manual Verification 'Search Foundation' (Protocol in workflow.md)

## Phase 2: Domain Discovery & Sitemap Intelligence
- [ ] Task: Write Unit Tests: Sitemap recursive parser & URL scoring heuristics
- [ ] Task: Implement `backend/core/discovery_engine.py` (Robots.txt + XML Sitemaps)
- [ ] Task: Write Integration Test: Discovery logic path prioritization (Pricing/Docs)
- [ ] Task: Conductor - User Manual Verification 'Discovery Engine' (Protocol in workflow.md)

## Phase 3: SOTA Cloud Crawler (Playwright Stealth)
- [ ] Task: Write Unit Tests: Playwright Stealth fingerprinter & Jitter logic
- [ ] Task: Implement `backend/services/crawler_service.py` (Headless Chromium on Cloud Run)
- [ ] Task: Implement BeautifulSoup cleanup pipeline (Markdown conversion)
- [ ] Task: Write Integration Test: Recursive Crawling (Level 2) with 150-page cap
- [ ] Task: Conductor - User Manual Verification 'Cloud Crawler' (Protocol in workflow.md)

## Phase 4: Industrial Asset Parsing (PDF/PPTX)
- [ ] Task: Write Unit Tests: PyMuPDF table extraction & metadata recovery
- [ ] Task: Implement `backend/tools/asset_parser.py` (PDF & PPTX support)
- [ ] Task: Write Unit Tests: python-pptx slide-to-text conversion
- [ ] Task: Conductor - User Manual Verification 'Asset Parsing' (Protocol in workflow.md)

## Phase 5: Gap-Driven Intelligence Planner
- [ ] Task: Write Unit Tests: Dossier Schema validation & Gap Identification logic
- [ ] Task: Implement `backend/agents/research_planner.py` (LangGraph Node)
- [ ] Task: Implement "Phase 2" loop logic: Trigger follow-up crawl on missing fields
- [ ] Task: Conductor - User Manual Verification 'Intelligence Planner' (Protocol in workflow.md)

## Phase 6: RAG Integration & Content Cache
- [ ] Task: Write Unit Tests: Upstash Redis Content-Hash Caching
- [ ] Task: Implement RAG Sync: Push processed Markdown to `pgvector`
- [ ] Task: Final System Hardening: Decommission Firecrawl/Jina stubs
- [ ] Task: Conductor - User Manual Verification 'Full Pipeline Integration' (Protocol in workflow.md)
