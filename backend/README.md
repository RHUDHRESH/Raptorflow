# RaptorFlow Agentic Spine

This is the Python-based creative engine for RaptorFlow, built with FastAPI and LangGraph.

## Tech Stack
- **Framework:** FastAPI
- **Orchestration:** LangGraph
- **Inference:** Vertex AI (Gemini)
- **Database:** Supabase (PostgreSQL + pgvector)

## Setup
1. Install dependencies:
   ```bash
   poetry install
   ```
2. Set environment variables:
   - `DATABASE_URL`: Supabase postgres connection string.
   - `SERPER_API_KEY`: Search API key.
   - `INFERENCE_PROVIDER`: "google" (default).
   - `RF_INTERNAL_KEY`: Secret key for API auth.

## Deployment
Deploy to Google Cloud Run:
```bash
gcloud run deploy raptorflow-spine --source .
```
