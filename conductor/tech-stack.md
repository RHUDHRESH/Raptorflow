# Technology Stack — RaptorFlow

## Frontend Core
- **Framework:** [Next.js](https://nextjs.org/) (App Router)
- **Language:** [TypeScript](https://www.typescriptlang.org/)
- **UI Library:** [React 19](https://react.dev/)
- **Deployment:** [Vercel](https://vercel.com/)

## AI & LLM
- **Platform:** [Google Vertex AI](https://cloud.google.com/vertex-ai) (Gemini models)
- **Search & Intelligence:** [Native Zero-Cost Engine](./backend/core/search_native.py) (Brave/DDG), replaces Tavily/Perplexity
- **Orchestration:** [LangGraph](https://langchain-ai.github.io/langgraph/)

## Backend & Infrastructure
- **Cloud Provider:** [Google Cloud Platform (GCP)](https://cloud.google.com/)
- **Compute:** [Cloud Run](https://cloud.google.com/run)
- **Database & Auth:** [Supabase](https://supabase.com/) (PostgreSQL + pgvector)
- **Caching & Messaging:** [Upstash](https://upstash.com/) (Redis)
- **Secrets Management:** [GCP Secret Manager](https://cloud.google.com/secret-manager)
- **Data Warehouse & Analytics:** [BigQuery](https://cloud.google.com/bigquery) (Longitudinal Analysis)
- **Blob Storage:** [Google Cloud Storage (GCS)](https://cloud.google.com/storage)

## Payments
- **Gateway:** [PhonePe](https://www.phonepe.com/business-solutions/payment-gateway/)

## Styling & Motion
- **Styling:** [Tailwind CSS](https://tailwindcss.com/)
- **Components:** [Shadcn UI](https://ui.shadcn.com/) (Radix UI primitives)
- **Animations:** [Framer Motion](https://www.framer.com/motion/)

## Utilities
- **Icons:** [Lucide React](https://lucide.dev/)
- **Forms/Validation:** [React Hook Form](https://react-hook-form.com/)
- **Toast/Notifications:** [Sonner](https://sonner.stevenly.me/)

## Development Tools
- **Linter:** ESLint
- **Package Manager:** npm
