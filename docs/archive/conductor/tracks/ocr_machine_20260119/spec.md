# Track Specification: Raptorflow SOTA OCR Machine

## 1. Overview
This track replaces the existing "brownfield" OCR implementation with an industrial-grade, Hybrid Cognitive OCR Machine. The goal is to move from a "shit" unreliable implementation to a robust system capable of handling messy, real-world marketing and business data (blurry images, huge multi-page PDFs, Excel tables) and mapping them into the Raptorflow intelligence engine.

## 2. Functional Requirements
### 2.1 Universal Input Handling
- Support for all common image formats (JPG, PNG, WebP).
- Support for complex documents (multi-page PDFs, raw scans).
- Support for structured data files (Excel/CSV) for data reconciliation.
- Resilience logic for low-quality inputs (blurred, skewed, or low-resolution images).

### 2.2 Hybrid Extraction Engine (The "Machine")
- **Primary Engine:** GCP Vision / Document AI for raw text and structure detection.
- **Cognitive Layer:** Gemini 2.0 Flash Vision for intelligent interpretation, "fixing" OCR typos, and semantic mapping.
- **Table Reconstruction:** Identification and extraction of tabular data into structured JSON objects.
- **PDF Stitching:** Coherent aggregation of results from massive, multi-page files into a singular context.

### 2.3 Asynchronous Processing
- Integration with an asynchronous queue system (Upstash Redis) to handle heavy batch processing.
- Status tracking for long-running OCR jobs (Pending, Processing, Completed, Failed).

## 3. Technical Constraints
- **Stack:** Python (Backend), GCP Cloud Vision API, Vertex AI (Gemini), Upstash (Redis).
- **Architecture:** Decoupled service architecture to ensure OCR failures do not crash the core application.

## 4. Acceptance Criteria
- [ ] 100% replacement of legacy OCR code.
- [ ] Successful extraction from a "messy" test suite (blurry photos, skewed docs).
- [ ] Accurate table reconstruction from Excel/PDF into JSON.
- [ ] Multi-page PDFs (>10 pages) processed and stitched without memory leaks.
- [ ] Cognitive cleanup proves higher accuracy than raw GCP Vision output alone.

## 5. Out of Scope
- Direct integration with physical scanners.
- Real-time video-stream OCR (static assets only).
