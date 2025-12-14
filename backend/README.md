# RaptorFlow Backend

Backend API server for RaptorFlow - handles onboarding, agent orchestration, and payments.

## Quick Start

```bash
# Install dependencies
cd backend
npm install

# Start development server
npm run dev
```

The server runs on `http://localhost:3001` by default.

## Environment Variables

Create a `.env` file in the project root with:

```env
# Backend
PORT=3001
NODE_ENV=development
FRONTEND_PUBLIC_URL=http://localhost:5173

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Google Cloud / Vertex AI
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# PhonePe (Optional - mock mode if not set)
PHONEPE_MERCHANT_ID=your-merchant-id
PHONEPE_SALT_KEY=your-salt-key
PHONEPE_SALT_INDEX=1
PHONEPE_ENV=UAT
```

## Architecture

### Native Tools (No External APIs)

The backend uses **native tools** that don't require external API keys:

1. **Website Scraper** - Fetches and parses websites to extract company info
2. **Company Analyzer** - Uses Vertex AI to analyze scraped content
3. **Competitor Research** - AI-powered competitor identification
4. **Tech Stack Detector** - Detects technologies from HTML signatures
5. **ICP Generator** - AI-powered ICP generation
6. **War Plan Generator** - Creates 90-day marketing plans

### Agents

- **PositioningParseAgent** - Analyzes Dan Kennedy/Dunford positioning answers
- **CompanyEnrichAgent** - Enriches company data using web scraping
- **ICPBuildAgent** - Generates 3 distinct ICPs using the 6D framework
- **MoveAssemblyAgent** - Creates war plans and campaign strategies

### API Endpoints

#### Onboarding
- `GET /api/onboarding/intake` - Get user's intake data
- `POST /api/onboarding/intake` - Save step data
- `GET /api/onboarding/status` - Get onboarding status
- `POST /api/onboarding/generate-icps` - Generate ICPs
- `POST /api/onboarding/generate-warplan` - Generate war plan
- `POST /api/onboarding/complete` - Mark onboarding complete
- `POST /api/onboarding/reset` - Reset onboarding

#### Payments
- `GET /api/payments/plans` - Get available plans
- `POST /api/payments/initiate` - Initiate payment
- `GET /api/payments/status/:txnId` - Check payment status
- `POST /api/payments/verify` - Verify payment
- `POST /api/payments/webhook` - PhonePe webhook

#### Shared Links (Sales-Assisted)
- `POST /api/shared/create` - Create shareable link
- `GET /api/shared/:token` - Get shared intake data
- `POST /api/shared/:token/payment` - Initiate payment from shared link

## PhonePe Integration

The payment integration supports both **real** and **mock** modes:

- **Real Mode**: Set `PHONEPE_MERCHANT_ID` and `PHONEPE_SALT_KEY`
- **Mock Mode**: Leave credentials empty for testing

### PhonePe Flow
1. Frontend calls `POST /api/payments/initiate`
2. Backend creates payment record and calls PhonePe API
3. User is redirected to PhonePe checkout
4. After payment, PhonePe redirects to callback URL
5. Backend webhook receives confirmation
6. Plan is activated for user

## Vertex AI Setup

1. Enable Vertex AI API in Google Cloud Console
2. Set up Application Default Credentials:
   ```bash
   gcloud auth application-default login
   ```
3. Or set `GOOGLE_APPLICATION_CREDENTIALS` to your service account key

## Database

Run the Supabase migration to create required tables:

```sql
-- See: supabase/migrations/003_onboarding_tables.sql
```

## Development

```bash
# Run in development with hot reload
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

