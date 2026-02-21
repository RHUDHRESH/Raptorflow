# Local Development Guide

## Prerequisites
- Node.js (v18+)
- Docker Desktop (for Redis, PostgreSQL, etc., if running locally without Supabase cloud)
- A Supabase project (local or remote)

## Getting Started

1. **Install Dependencies**
   Run `npm install` from the root directory to grab all frontend dependencies.

2. **Environment Configuration**
   Copy `.env.example` to `.env.local` or `.env` and ensure `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` are populated.

3. **Running the Frontend**
   ```bash
   npm run dev
   ```
   The application will be available at `http://localhost:3000`.

## Testing & Linting

We maintain strict quality control. Before pushing code:
- Run the linter: `npm run lint`
- Run typecheck: `npm run typecheck` (if applicable)
- Run tests: Use `pytest` for backend, and Playwright for E2E tests in the `tests/` directory.

## Best Practices
- Keep components small and reusable in `src/components`.
- Write pure Functions and separate side-effects.
- Never commit secrets to the repository. Use `.env.local`.
