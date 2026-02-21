# RaptorFlow

RaptorFlow is a large-scale, production-ready application. This repository is structured to separate concerns clearly, ensuring rapid development and stable deployments.

## Directory Structure Overview
- `src/` - The core Next.js frontend application.
- `backend/` - The core backend application logic.
- `supabase/` - Database structure, migrations, and Edge Functions.
- `infrastructure/` - Deployment configurations and services (Nginx, Redis, Prometheus).
- `scripts/` - Utility scripts for deployment and local setup.
- `tests/` - The end-to-end and integration testing suite.

## Documentation Index
For detailed guides on specific components, refer to our `docs/` folder:
- [Architecture Guide](docs/ARCHITECTURE.md): System design, data flow, and tech stack details.
- [Development Workflow](docs/DEVELOPMENT.md): How to setup, run, and test the app locally.
- [Deployment Guide](docs/DEPLOYMENT.md): Instructions for production deployments, Docker setup, and CI/CD.

## Quick Start
1. **Clone the repository.**
2. **Install dependencies:** `npm install`
3. **Set up `.env`:** Copy `.env.example` to `.env` and fill in necessary keys.
4. **Run frontend:** `npm run dev`
5. **Run backend (if applicable):** Follow backend-specific instructions in `backend/`.

> [!NOTE]
> Ensure you have Docker running locally if you need to test the full infrastructure stack via `docker-compose`.
