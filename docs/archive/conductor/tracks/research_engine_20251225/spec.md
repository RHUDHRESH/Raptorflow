# Specification: Industrial Research Engine (SOTA)

## 1. Overview
RaptorFlow requires a production-grade, self-hosted research system to eliminate reliance on third-party APIs (Firecrawl, Jina, Brave). This track implements an end-to-end intelligence pipeline—from SERP discovery to Level-2 recursive crawling and gap-driven planning—hosted entirely within the GCP/Supabase ecosystem.

## 2. Functional Requirements

### 2.1 Self-Hosted Search & Discovery
- **Search Service:** Deploy a Cloud Run service wrapping Google Custom Search API (CSE) with multi-key rotation. Fall back to Playwright SERP scraping if keys are exhausted.
- **Domain Discovery:** Implement a module to parse `robots.txt` and sitemaps recursively. Score and prioritize URLs based on high-value keywords (e.g., "pricing", "case-studies").

### 2.2 Deep Extraction Engine
- **Cloud Crawler:** A Cloud Run service using Playwright Stealth to handle both static HTML and JS-heavy sites.
- **Recursive Depth:** Support Level-2 crawling with a cap of 150 pages per domain.
- **Asset Parsing:** Integrate native PDF (`PyMuPDF`) and PPTX (`python-pptx`) extraction into the extraction pipeline.

### 2.3 Gap-Driven Intelligence
- **Dossier Schema:** Implement a standard JSON schema covering:
    - Company Profile (Mission, Leadership)
    - Product & Pricing (Tiers, Feature Matrices)
    - Target Audience (ICPs, Testimonials)
    - Ecosystem (Integrations, Tech Stack)
    - Marketing Strategy (Messaging, Ad Channels)
- **Intelligence Planner:** A LangGraph node that evaluates scraped data against the schema, identifies "Gaps," and generates surgical follow-up crawl targets or search queries.

### 2.4 Industrial Persistence & Cache
- **Audit-Ready Storage:** Save raw artifacts (HTML/PDFs) to Google Cloud Storage (GCS).
- **RAG Sync:** Ingest cleaned Markdown into Supabase `pgvector` (768 dimensions).
- **Content Cache:** Use Upstash Redis to skip redundant fetches based on URL and content hash.

## 3. Non-Functional Requirements
- **100% GCP Native:** No external third-party scraping or search SaaS.
- **Stealth & Resilience:** Use Cloud Run dynamic egress, Playwright Stealth, and randomized industrial jitter (1-5s).
- **Security:** All API keys (Google CSE) stored in GCP Secret Manager.

## 4. Acceptance Criteria
- [ ] Research dossier can be generated for a competitor domain without calling Firecrawl or Jina.
- [ ] System successfully crawls 150 pages of a target domain and extracts structured pricing data.
- [ ] PDF whitepapers are parsed and their content is searchable via pgvector RAG.
- [ ] Gap-planner successfully triggers a "Phase 2" crawl when pricing info is missing.

## 5. Out of Scope
- Integration with paid proxy providers (e.g., Bright Data).
- Social media platform authenticated scraping (LinkedIn/X private profiles).
