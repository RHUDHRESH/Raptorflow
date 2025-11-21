# Raptorflow Quick Start Guide

Get Raptorflow running locally in 5 minutes.

## Prerequisites

- Node.js 20+
- npm or yarn
- Git

## Step 1: Clone and Install

```bash
git clone https://github.com/your-org/raptorflow.git
cd raptorflow
npm install
```

## Step 2: Set Up Environment

```bash
# Copy environment template
cp .env.example .env.local

# Edit with your values
nano .env.local
```

Minimum required for local dev:
```bash
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_ENVIRONMENT=development
```

## Step 3: Start Development Server

```bash
npm run dev
```

Visit [http://localhost:5173](http://localhost:5173)

## Step 4: Set Up Supabase (First Time)

### Option A: Use Existing Supabase Project

1. Create account at [supabase.com](https://supabase.com)
2. Create new project
3. Go to SQL Editor
4. Copy and run schema from `database/schema.sql`
5. Get credentials from Settings > API
6. Update `.env.local`

### Option B: Run Supabase Locally

```bash
# Install Supabase CLI
npm install -g supabase

# Start local instance
supabase start

# Use local credentials in .env.local:
VITE_SUPABASE_URL=http://localhost:54321
VITE_SUPABASE_ANON_KEY=<from supabase start output>
```

## What's Next?

### For Development
- Read [INFRASTRUCTURE_SETUP.md](./INFRASTRUCTURE_SETUP.md) for full setup
- Check [ARCHITECTURE_DIAGRAM.txt](./ARCHITECTURE_DIAGRAM.txt) for system design
- Review [IMPLEMENTATION_BLUEPRINT.md](./IMPLEMENTATION_BLUEPRINT.md) for features

### For Deployment
- Set up [Vercel](https://vercel.com) for frontend
- Set up [GCP](https://cloud.google.com) for backend
- Set up [PostHog](https://posthog.com) for analytics
- Follow [DEPLOYMENT.md](./DEPLOYMENT.md) for instructions

## Project Structure

```
raptorflow/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/          # Route pages
│   ├── lib/            # Utilities and configs
│   │   ├── supabase.ts # Supabase client
│   │   └── posthog.ts  # PostHog analytics
│   └── services/       # Business logic (templates)
├── database/           # Database schema and migrations
├── public/             # Static assets
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose setup
├── vercel.json         # Vercel deployment config
├── app.yaml            # GCP App Engine config
└── cloudbuild.yaml     # GCP Cloud Build config
```

## Common Commands

```bash
# Development
npm run dev              # Start dev server
npm run build           # Build for production
npm run preview         # Preview production build
npm run lint            # Run linter

# Docker
docker-compose up -d    # Start all services
docker-compose down     # Stop all services
docker-compose logs -f  # View logs

# Deployment
vercel --prod          # Deploy to Vercel
gcloud app deploy      # Deploy to GCP
```

## Getting Help

- Documentation: [INFRASTRUCTURE_SETUP.md](./INFRASTRUCTURE_SETUP.md)
- Deployment: [DEPLOYMENT.md](./DEPLOYMENT.md)
- Issues: [GitHub Issues](https://github.com/your-org/raptorflow/issues)

## Default Login (Development)

After setting up Supabase with the seed data:
- Check Supabase Dashboard > Authentication for test users
- Or create your own via the signup flow

## Features Available

✅ **Fully Functional:**
- Dashboard with metrics
- Campaign management
- OODA loop workflow
- Technology tree
- Maneuver library
- ICP management
- Analytics dashboard

🔄 **Needs Backend Integration:**
- Data persistence (Supabase)
- User authentication
- Real-time updates
- API endpoints

## Troubleshooting

### Port already in use
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9

# Or use different port
npm run dev -- --port 3000
```

### Environment variables not loading
- Ensure file is named `.env.local` (not `.env.local.example`)
- Restart dev server after changing env variables
- Check variables start with `VITE_`

### Supabase connection errors
- Verify URL and anon key are correct
- Check project is not paused in Supabase Dashboard
- Test connection in browser console:
  ```javascript
  console.log(import.meta.env.VITE_SUPABASE_URL)
  ```

### Build errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf .vite
```

---

Happy coding! 🚀
